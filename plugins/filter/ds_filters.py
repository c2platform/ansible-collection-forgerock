"""ansible filters."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from pprint import pprint
import re
import json
import os
import hashlib


# Return command switches for ForgeRock CLI utilities
def ds_cmd(cmd_config):
    cmd_line = ''
    for key in cmd_config:
        if cmd_config[key] is None:
            cmd_config[key] = ''
        if key == 'when':
            continue
        if isinstance(cmd_config[key], list):
            for v in cmd_config[key]:
                vf = format_ds_cmd_value(v)
                cmd_line += '  --{} {}'.format(key, vf)
        else:
            vf = format_ds_cmd_value(cmd_config[key])
            cmd_line += '  --{} {}'.format(key, vf)
    return cmd_line


def ds_cmd_ml(cmd_config, ident=4):
    itms = ds_cmd(cmd_config).split('--')
    itms.pop(0)
    cmd_line = ''
    for itm in itms:
        cmd_line += (' ' * ident) + '--{}'.format(itm.strip())
        if not itm == itms[-1]:
            cmd_line += " \\\n"
    return cmd_line


# Return string with quotes for values with whitespace
def format_ds_cmd_value(v):
    if isinstance(v, int):
        return str(v)
    elif '"' in v:
        return v
    elif ' ' in v:
        return '"' + v + '"'
    return v


# Return ds config method e.g. set-connection-handler-prop
def ds_config_method(component, config=None, get_set='set'):
    comp = component.split('_')[0]  # e.g. connection-handler
    # pprint({'component': component, 'config': config, 'get_set': get_set})
    if get_set == 'set':
        if 'create' in component:
            return 'create-' + comp
        elif 'delete' in component:
            return 'delete-' + comp
        else:
            return 'set-{}-prop'.format(comp)
    else:  # get
        if (config is not None) and 'when' in config:
            return config['when']['method']
        else:
            return 'get-{}-prop'.format(comp)

# Return the command switches to get current config
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


# Return value from property from get results
# returns None if property does not exist
def ds_cmd_result_property_value(results, set_item, prop):
    p = re.compile(prop + '\s+:\s(\S+)')
    for result in results:
        # pprint( {'set_item': set_item, 'result[item]': result['item']} )
        if set_item == result['item']:
            # pprint( {'result[stdout]': result['stdout'], 'p': p} )
            r = p.search(result['stdout'])
            if r is None:
                return ''
            else:
                return r.group(1).rstrip()
    return ''


# Return value part from set in ds_config var
# e.g. input 'set: lookthrough-limit:20000' will
# return 2000 - the value of the property
def ds_config_property_value(v):
    try:
        return v.split(':', 1)[1]
    except Exception:
        pprint(v)
        raise ValueError('Unable to get property value')


# Similar to ds_config_property_value
# Now return the property
def ds_config_property_name(v):
    try:
        return v.split(':')[0]
    except Exception:
        pprint(v)
        raise ValueError('Unable to get property name')


# Select in current_config the results of a specific item
def current_config_select(current_config, item):
    # pprint({'current_config_select': current_config, 'item': item})
    for rslt in current_config['results']:
        if rslt['item'] == item:
            return rslt
    raise ValueError('Unable to find the results for item')


# Determine desired state is different
def ds_config_state_diff(set_item, current_config, component_fingerprint,
                         use_component_fingerprint, skip_state_check):
    # pprint( {'ds_config_state_diff': set_item} )
    # pprint( {'component_fingerprint': component_fingerprint} )
    # pprint( {'current_config': current_config} )
    # pprint( {'component_fingerprint[changed]':
    # component_fingerprint['changed']} )
    if skip_state_check:
        return True
    elif 'when' in set_item:
        rslt = current_config_select(current_config, set_item)
        p = re.compile(set_item['when']['regex'], re.MULTILINE)
        r = p.search(rslt['stdout'])
        # pprint({'p': p, 'r': r, 'stdout': rslt['stdout'],
        #       'set_item': set_item})
        if r is None:
            return not set_item['when']['match']
        else:
            return set_item['when']['match']
        return True
    elif use_component_fingerprint:
        return component_fingerprint['changed']
    elif current_config is None:
        return True
    elif current_config['results'] == '':
        return True
    elif isinstance(set_item['set'], list):
        for si in set_item['set']:
            prop = ds_config_property_name(si)
            tv = ds_config_property_value(si)
            cv = ds_cmd_result_property_value(current_config['results'],
                                              set_item, prop)
            if tv != cv:
                return True
        return False
    else:
        prop = ds_config_property_name(set_item['set'])
        tv = ds_config_property_value(set_item['set'])
        cv = ds_cmd_result_property_value(current_config['results'],
                                          set_item, prop)
        return tv != cv


# Return hash value for config
def ds_config_fingerprint(config):
    if type(config).__name__ == 'AnsibleUndefined':
        print('fatal: component configuration is missing')
    json_config = json.dumps(config)
    str = hashlib.sha1(bytes(json_config, 'utf-8'))
    return str.hexdigest()


# Return path for fingerprint folder
def ds_config_fingerprint_folder(ds_home, ds_version):
    return os.path.join(os.path.sep, ds_home, '.fingerprint', ds_version)


# Return path for fingerprint for component
def ds_config_fingerprint_component_path(component, ds_home, ds_version):
    return os.path.join(os.path.sep,
                        ds_config_fingerprint_folder(ds_home, ds_version),
                        component)


# Return path for fingerprint for component
def ds_pop(settings, k):
    if k in settings:
        settings.pop(k)
    return settings


# Return dn from ldif string
def dn_from_modify_item(itm):
    if 'dn' in itm:
        return itm['dn']
    else:
        dn = itm['ldif'].split("\n")[0]
        dn = dn.split(':')[1]
        return dn.strip()


# Return search string for ds_modify config
def ds_modify_search(itm):
    dn = dn_from_modify_item(itm)
    base_dn = dn.rsplit(',', 1)[-1]  # e.g. c=NL
    if 'search' in itm:
        return '--baseDn ' + base_dn + ' "' + itm['search'] + '"'
    else:
        return '--baseDn "' + dn + '" --searchScope base objectclass=*  || true'


class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'ds_cmd': ds_cmd,
            'ds_cmd_ml': ds_cmd_ml,
            'ds_cmd_get': ds_cmd_get,
            'ds_config_method': ds_config_method,
            'ds_cmd_result_property_value': ds_cmd_result_property_value,
            'ds_config_property_value': ds_config_property_value,
            'ds_config_property_name': ds_config_property_name,
            'ds_config_state_diff': ds_config_state_diff,
            'ds_config_fingerprint': ds_config_fingerprint,
            'ds_config_fingerprint_folder': ds_config_fingerprint_folder,
            'ds_config_fingerprint_component_path':
            ds_config_fingerprint_component_path,
            'ds_pop': ds_pop,
            'dn_from_modify_item': dn_from_modify_item,
            'ds_modify_search': ds_modify_search
        }
