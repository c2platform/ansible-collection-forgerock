"""ansible filters."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError

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

class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'ds_cmd': ds_cmd
        }
