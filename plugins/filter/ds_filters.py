"""ansible filters."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError
import re

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

# Return value from property from get results
# returns None if property does not exist
def ds_cmd_result_property_value(results, prop):
    p = re.compile(prop + '.*?:.*?([\S.]*)$')
    for result in results:
        if result['item'] == prop:
            return p.search(result['stdout']).group(1).rstrip()
    return ''

# Return value part from set in ds_config var
# e.g. input 'set: lookthrough-limit:20000' will
# return 2000 - the value of the property
def ds_config_property_value(v):
    return v['set'].split(':',1)[1]

# Similar to ds_config_property_value
# Now return the property
def ds_config_property_name(v):
    return v['set'].split(':')[0]

# Determine if a current property is different from target
def ds_config_property_change(set_item,results):
   if results == '':
       return True
   else:
      prop = ds_config_property_name(set_item)
      tv = ds_config_property_value(set_item)
      cv = ds_cmd_result_property_value(results,prop)
      return tv != cv

class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'ds_cmd': ds_cmd,
            'ds_cmd_result_property_value': ds_cmd_result_property_value,
            'ds_config_property_value': ds_config_property_value,
            'ds_config_property_name': ds_config_property_name,
            'ds_config_property_change': ds_config_property_change
        }
