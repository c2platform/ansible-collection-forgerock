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
           'keys', 'cmd', 'get-cmd', 'get-stdout',
           'change', 'enabled']
    return kys


def ds_cmd_ignore_keys_get():
    kys = ds_cmd_ignore_keys()
    kys += ['add', 'remove', 'set']
    return kys


# Return command switches for ForgeRock CLI utilities
# TODO remove from filters
def ds_cmd(cmd_config):
    cmd_line = []
    for key in cmd_config:
        # print('key: ' + key)
        if cmd_config[key] is None:
            cmd_config[key] = ''
        if key in ds_cmd_ignore_keys():
            continue
        if isinstance(cmd_config[key], list):
            for v in cmd_config[key]:
                vf = format_ds_cmd_value(v)
                cmd_line.append('--{} {}'.format(key, vf))
        else:
            vf = format_ds_cmd_value(cmd_config[key])
            cmd_line.append('--{} {}'.format(key, vf))
    return " ".join(cmd_line)


# Return the command switches to get current config
# TODO remove from filters
def ds_cmd_get(cmd_config, component):
    # pprint({'component':component, 'cmd_config': cmd_config})
    comp = component.split('_')[0]  # e.g. connection-handler
    if 'when' in cmd_config:
        if 'switches' in cmd_config['when']:
            return ds_cmd(cmd_config['when']['switches'])
        return ''
    if comp == 'global-configuration':
        return '--property ' + ds_config_property_name(cmd_config['set'])
    elif comp == 'password-validator':
        return '--validator-name ' + \
            format_ds_cmd_value(cmd_config['validator-name'])
    elif comp == 'log-publisher':
        return '--publisher-name ' + \
            format_ds_cmd_value(cmd_config['publisher-name'])
    elif comp == 'plugin':
        return '--plugin-name ' + \
            format_ds_cmd_value(cmd_config['plugin-name'])
    elif comp == 'replication-server':
        return '--provider-name ' + \
            format_ds_cmd_value(cmd_config['provider-name'])
    else:
        msg = "No get command defined for component {}. Use a fingerprint!?"
        raise Exception(msg.format(comp))


def ds_config_result_of_step(results, step):
    if results:
        for r in results:
            # print('whatever')
            if r['item']['step'] == step:
                return r
    return 'n.a.'


# Create get dict based on set dict
def ds_cmd_get_keys(ci):
    gt = {}
    for ky in ci:
        if ky in ds_cmd_ignore_keys_get():
            continue
        gt[ky] = ci[ky]
    return gt


def ds_config(data):
    fcts = {}
    comp = data['component']
    fcts['ds_config'] = {}
    fcts['ds_config'][comp] = data['config']
    cis = []
    step = 0
    for ci in fcts['ds_config'][comp]:
        ci['step'] = step
        ci['cmd'] = "{} {}".format(ci['method'], ds_cmd(ci))
        gt = {}
        if 'enabled' not in ci:
            ci['enabled'] = True
        if 'get' in ci:  # build explicit get
            gt = ci['get']
            if 'method' in ci['get']:
                gt_mthd = ci['get']['method']
            else:
                gt_mthd = ci['method'].replace('set-', 'get-')
            if 'keys' in ci['get']:
                for ky in ci['get']['keys']:
                    gt[ky] = ci[ky]
        else:
            gt = ds_cmd_get_keys(ci)  # build implicit / default get
            gt_mthd = ci['method'].replace('set-', 'get-')
        if 'add' in ci:  # assume simple property
            gt['property'] = ci['add'].split(':')[0]
        if 'remove' in ci:  # assume simple property
            gt['property'] = ci['remove'].split(':')[0]
        if 'set' in ci:  # assume simple property
            gt['property'] = ci['set'].split(':')[0]
            # e.g. property: ssl-cert-nickname
        ci['get'] = gt
        ci['get']['method'] = gt_mthd
        gt_cmd = ds_cmd(gt)
        if 'cmd' not in ci['get']:
            ci['get']['cmd'] = "{} {}".format(gt_mthd, gt_cmd)
        if 'config_current' in data:
            r = ds_config_result_of_step(data['config_current'], step)
            if 'stdout' in r:
                ci['get']['stdout'] = r['stdout']
            if 'when' not in ci:   # no when key
                if 'add' in ci:  # assume simple property
                    ci['when'] = {}
                    ci['when']['regex'] = ci['add'].split(':')[1]
                if 'remove' in ci:  # assume simple property
                    ci['when'] = {}
                    ci['when']['regex'] = ci['remove'].split(':')[1]
                    ci['when']['match'] = False
                if 'set' in ci:  # assume simple property
                    ci['when'] = {}
                    ci['when']['regex'] = "\s+:\s+".join(ci['set'].split(':'))
            if 'when' in ci:
                if 'match' not in ci['when']:
                    ci['when']['match'] = False
                if 'stdout' in ci['get']:
                    x = re.search(ci['when']['regex'], ci['get']['stdout'])
                    ci['when']['match-result'] = False
                    ci['change'] = False
                    if (x):
                        ci['when']['match-result'] = True
                    if ci['when']['match-result'] == ci['when']['match']:
                        ci['change'] = True
                if 'enabled' in ci:
                    if not ci['enabled']:
                        ci['change'] = False
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
        "config": {"required": True, "type": "list"},
        "config_current": {"required": False, "type": "list"},
        "config_changes": {"required": False, "type": "list"}}
    module = AnsibleModule(argument_spec=fields)
    has_changed, fcts, tr = ds_config(module.params)
    module.exit_json(changed=has_changed, msg=tr, config=fcts)


if __name__ == '__main__':
    main()
