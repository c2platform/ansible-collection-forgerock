#!/usr/bin/python

from ansible.module_utils.basic import *
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


# Return command switches for ForgeRock CLI utilities
# TODO remove from filters
def ds_cmd(cmd_config):
    cmd_line = []
    for key in cmd_config:
        # print('key: ' + key)
        if cmd_config[key] is None:
            cmd_config[key] = ''
        if key in ['when', 'get', 'step', 'method']:
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
        if ci['method'] in data['get']:
            gt = data['get'][ci['method']]
            gt_mthd = data['get'][ci['method']]['method']
            gt_cmd = ds_cmd(gt)
            ci['get-cmd'] = "{} {}".format(gt_mthd, gt_cmd)
        if 'config_current' in data:
            r = ds_config_result_of_step(data['config_current'], step)
            if 'stdout' in r:
                ci['get-stdout'] = r['stdout']
        if 'config_changes' in data:
            r = ds_config_result_of_step(data['config_changes'], step)
            if 'stdout' in r:
                ci['stdout'] = r['stdout']
        cis.append(ci)
        step += 1
    return False, cis, "DS config prepared"


def main():
    fields = {
        "component": {"required": True, "type": "str"},
        "config": {"required": True, "type": "list"},
        "get": {"required": True, "type": "dict"},
        "config_current": {"required": False, "type": "list"},
        "config_changes": {"required": False, "type": "list"}}
    module = AnsibleModule(argument_spec=fields)
    has_changed, cis, tr = ds_config(module.params)
    module.exit_json(changed=has_changed, msg=tr, config=cis)


if __name__ == '__main__':
    main()
