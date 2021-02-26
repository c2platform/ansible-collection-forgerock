"""ansible filters."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
from pprint import pprint
import re, json, os
import hashlib

# Return command switches for ForgeRock CLI utilities
def ds_cmd(cmd_config):
  cmd_line = ''
  for key in cmd_config:
    if isinstance(cmd_config[key], list):
      for v in cmd_config[key]:
        cmd_line += ' --{} {}'.format(key,v)
    else:
      cmd_line += ' --{} {}'.format(key,cmd_config[key])
  return cmd_line

# Return the command switches to get current config
def ds_cmd_get(cmd_config, component):
  if component == 'global-configuration':
    return '--property ' + ds_config_property_name(cmd_config['set'])
  elif component == 'password-validator':
    return '--validator-name ' + cmd_config['validator-name']
  return False

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
        return v.split(':',1)[1]
    except:
      pprint(v)
      raise ValueError('Unable to get property value')

# Similar to ds_config_property_value
# Now return the property
def ds_config_property_name(v):
    try:
        return v.split(':')[0]
    except:
      pprint(v)
      raise ValueError('Unable to get property name')

# Determine if a current property is different from target
def ds_config_property_change(set_item, current_config, component_fingerprint, use_component_fingerprint, skip_state_check):
   #pprint( {'ds_config_property_change': set_item} )
   #pprint( {'component_fingerprint': component_fingerprint} )
   #pprint( {'current_config': current_config} )
   #pprint( {'component_fingerprint[changed]': component_fingerprint['changed']} )
   if skip_state_check:
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
          cv = ds_cmd_result_property_value(current_config['results'],set_item,prop)
          if tv != cv:
              # pprint( {'item': si, 'property': prop, 'current': cv, 'target': tv } )
              return True
      return False
   else:
      prop = ds_config_property_name(set_item['set'])
      tv = ds_config_property_value(set_item['set'])
      cv = ds_cmd_result_property_value(current_config['results'],set_item,prop)
      return tv != cv

# Return hash value for config
def ds_config_fingerprint(config):
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

class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'ds_cmd': ds_cmd,
            'ds_cmd_get': ds_cmd_get,
            'ds_cmd_result_property_value': ds_cmd_result_property_value,
            'ds_config_property_value': ds_config_property_value,
            'ds_config_property_name': ds_config_property_name,
            'ds_config_property_change': ds_config_property_change,
            'ds_config_fingerprint': ds_config_fingerprint,
            'ds_config_fingerprint_folder': ds_config_fingerprint_folder,
            'ds_config_fingerprint_component_path': ds_config_fingerprint_component_path
        }
