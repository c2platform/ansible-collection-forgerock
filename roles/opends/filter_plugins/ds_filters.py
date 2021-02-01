"""ansible filters."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.errors import AnsibleFilterError

# Return command switches for OpenDS
def opends_cmd(cmd_config):
  cmd_line = ''
  for key in cmd_config:
    cmd_line += ' --{} {}'.format(key,cmd_config[key])
  return cmd_line

class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'opends_cmd': opends_cmd
        }
