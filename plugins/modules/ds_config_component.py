#!/usr/bin/python

from ansible.module_utils.basic import *
import re
# from pprint import pprint
# import json


# Return ds config method e.g. set-connection-handler-prop
# TODO remove from filster
def ds_config_method(component):
    comp = component.split('_')[0]  # e.g. connection-handler
    # pprint({'component': component, 'config': config, 'get_set': get_set})
    if 'create' in component:
        return 'create-' + comp
    elif 'delete' in component:
        return 'delete-' + comp
    else:
        return 'set-{}-prop'.format(comp)


# Return string with quotes for values with whitespace
# TODO remove from filster
def format_ds_cmd_value(v):
    if isinstance(v, int):
        return str(v)
    elif '"' in v:
        return v
    elif ' ' in v:
        return '"' + v + '"'
    return v


def ds_cmd_ignore_keys():
    kys = ['when', 'get', 'step', 'method',
           'keys', 'cmd', 'get-cmd',
           'change', 'enabled', 'changed_when',
           'property-update', 'stdout']
    return kys


def ds_cmd_ignore_keys_get():
    kys = ds_cmd_ignore_keys()
    kys += ['add', 'remove', 'set', 'cmd']
    return kys


# Return command switches for ForgeRock CLI utilities
# TODO remove from filters
def ds_cmd(cmd_config, update_properties=[]):
    cmd_line = []
    for key in cmd_config:
        cck = cmd_config[key]
        if cck is None:
            cck = ''
        if key in ds_cmd_ignore_keys():
            continue
        if not isinstance(cck, list):
            cck = [cck]
        for v in cck:
            vf = format_ds_cmd_value(v)
            if key in ['add', 'remove', 'set']:
                if v in update_properties:
                    cmd_line.append('--{} {}'.format(key, vf))
            else:
                cmd_line.append('--{} {}'.format(key, vf))
    return " ".join(cmd_line)


def ds_config_result_of_step(results, step):
    if results:
        for r in results:
            # print('whatever')
            if r['item']['step'] == step:
                return r
    return 'n.a.'


# Create get dict based on set dict
def ds_cmd_get_keys(ci, data):
    gt = {}
    if ci['method'] in data['get_methods']:
        return gt
    for ky in ci:
        if ky in ds_cmd_ignore_keys_get():
            continue
        gt[ky] = ci[ky]
    return gt


# Return the method to get current state
def ds_cmd_get_method(ci, get_methods):
    mthd = ci['method'].replace('set-', 'get-')
    if ci['method'] in get_methods:
        mthd = get_methods[ci['method']]['method']
    return mthd


# Return the when to evaluate current state
def ds_cmd_get_method_when(ci, get_methods):
    whn = {}
    whn['match-expected'] = False  # default
    for ky in ['match-expected']:
        if ky in get_methods[ci['method']]:
            whn[ky] = get_methods[ci['method']][ky]
    if 'regex_key' in get_methods[ci['method']]:
        whn['regex'] = ci[get_methods[ci['method']]['regex_key']] + "\\n"
    return whn


# Build properties to get
def ds_config_get_properties(ci, data):
    prps = []
    if ci['method'] not in data['get_methods']:
        for ky in ['add', 'remove', 'set']:
            if ky in ci:
                ci_ky = ci[ky]
                if not isinstance(ci_ky, list):
                    ci_ky = [ci_ky]
                for p in ci_ky:
                    prp = p.split(':', 1)[0]
                    if prp not in prps:
                        prps.append(prp)
    ci['get']['property'] = prps
    return ci

# Return regex pattern to use
#def ds_config_regex_pattern(ci):
#    ptrn = '.*'
#    if 'stdout' in ci['get']:
#        if ci['get']['stdout'].count("\t") == 1:
#            ptrn = '\t'  # one tab
#    return ptrn


# Return regex or list of regex for set, add, remove
def ds_config_regex(ci, get_methods):
    if 'when' not in ci:
        ci['when'] = []
    if ci['method'] in get_methods:
        ci['when'] = [ds_cmd_get_method_when(ci, get_methods)]
    else:
        for ky in ['add', 'remove', 'set']:
            if ky in ci:
                ci_ky = ci[ky]
                if not isinstance(ci_ky, list):  # list
                    ci_ky = [ci[ky]]
                for kv in ci_ky:
                    whn = {}
                    whn['match-expected'] = False  # default
                    if ky == 'remove':
                        whn['match-expected'] = True
                    whn['prop'] = kv
                    whn['regex'] = '.*\t'.join(kv.split(':', 1)) + '[\t|\n]'
                    ci['when'].append(whn)
    return ci


# Return regex or list of regex for set, add, remove
def ds_config_regex_match(ci):
    whns = ci['when']
    whns2 = []
    ci['change'] = False
    if not isinstance(whns, list):
        whns = [whns]
    for whn in whns:
        whn['change'] = False
        rslt = False
        if 'match-expected' not in whn:
            whn['match-expected'] = False  # default
        if (re.search(whn['regex'], ci['get']['stdout'] + "\n")):
            rslt = True  # regex match
        if rslt == whn['match-expected']:
            ci['change'] = True
            whn['change'] = True
        whn['match-result'] = rslt
        whns2.append(whn)
    ci['when'] = whns2
    return ci


# Create set cmd
def ds_config_set_cmd(ci, data):
    ci = ds_config_update_properties(ci)
    cmd = "{} {}".format(ci['method'], ds_cmd(ci, ci['property-update']))
    ci['cmd'] = cmd
    return ci


# Create get cmd
def ds_config_get_cmd(ci, data):
    if 'get' not in ci:  # create get
        ci['get'] = {}
        ci['get'] = ds_cmd_get_keys(ci, data)
        ci['get']['method'] = ds_cmd_get_method(ci, data['get_methods'])
    else:  # no get
        ci = ds_config_get_cmd_explicit(ci, data)
    gt_mthd = ci['get']['method']
    # from pprint import pprint
    # pprint({"ci['get']": ci['get']})
    # with open('/vagrant/magweg2.txt', 'a') as f: f.write(ci['get'])
    gt_cmd = ds_cmd(ci['get'])
    ci['get']['cmd'] = \
        "{} {} -s".format(gt_mthd, gt_cmd)  # -s for script friendly
    return ci


# Create get cmd from configured get
def ds_config_get_cmd_explicit(ci, data):
    if 'method' not in ci['get']:
        ci['get']['method'] = ds_cmd_get_method(ci, data['get_methods'])
    if 'keys' in ci['get']:
        for ky in ci['get']['keys']:
            ci['get'][ky] = ci[ky]
    return ci


# Set properties that need to be updated
def ds_config_update_properties(ci):
    prps = []
    if 'when' in ci:
        for whn in ci['when']:
            if 'prop' not in whn:
                continue
            if 'change' in whn:
                if whn['change']:
                    prps.append(whn['prop'])
    ci['property-update'] = prps
    return ci


def ds_config(data):
    fcts = {}
    comp = data['component']
    fcts['ds_config'] = {}
    fcts['ds_config'][comp] = data['config']
    cis = []
    step = 0
    for ci in fcts['ds_config'][comp]:
        ci['step'] = step
        if 'enabled' not in ci:
            ci['enabled'] = True
        ci = ds_config_set_cmd(ci, data)
        ci = ds_config_get_cmd(ci, data)
        ci = ds_config_get_properties(ci, data)
        if 'config_current' in data:
            r = ds_config_result_of_step(data['config_current'], step)
            if 'stdout' in r:
                ci['get']['stdout'] = r['stdout']
            if 'when' not in ci:   # no when key
                ci = ds_config_regex(ci, data['get_methods'])
            if 'when' in ci:
                if 'stdout' in ci['get']:
                    ci = ds_config_regex_match(ci)
                if 'enabled' in ci:
                    if not ci['enabled']:
                        ci['change'] = False
            ci = ds_config_set_cmd(ci, data)  # update set cmd
        if 'config_changes' in data:
            r = ds_config_result_of_step(data['config_changes'], step)
            if 'stdout' in r:
                ci['stdout'] = r['stdout']
        cis.append(ci)
        step += 1
    fcts['ds_config'][comp] = cis
    return False, fcts['ds_config'], "DS config prepared"


def main():
    fields = {
        "component": {"required": True, "type": "str"},
        "get_methods": {"required": True, "type": "dict"},
        "config": {"required": True, "type": "list"},
        "config_current": {"required": False, "type": "list"},
        "config_changes": {"required": False, "type": "list"}}
    module = AnsibleModule(argument_spec=fields)
    has_changed, fcts, tr = ds_config(module.params)
    module.exit_json(changed=has_changed, msg=tr, config=fcts)


if __name__ == '__main__':
    main()
