#!/usr/bin/python

from ansible.module_utils.basic import *


# Set additional facts in am_configure: step, script, script-obsolete
def amster_script_prepare_execution(data):
    fcts = {}
    fcts['am_configure'] = data['configure']
    i = 0
    for c in fcts['am_configure']:
        c['changed'] = data['scripts']['results'][i]['changed']
        c['execute'] = c['changed']
        if 'force' in c:
            if c['force']:
                c['execute'] = True
        if data['force']:
            c['execute'] = True
        if 'enabled' in c:  # disabled should never run
            if not c['enabled']:
                c['execute'] = False
        i += 1
    return True, fcts, str(i) + " Amster scripts prepared for execution"


def main():
    fields = {
        "dest": {"required": True, "type": "str"},
        "configure": {"required": True, "type": "list"},
        "templates": {"required": True, "type": "dict"},
        "scripts": {"required": True, "type": "dict"},
        "force": {"required": True, "type": "bool"}}
    module = AnsibleModule(argument_spec=fields)
    has_changed, fcts, tr = amster_script_prepare_execution(module.params)
    module.exit_json(changed=False, ansible_facts=fcts, msg=tr)


if __name__ == '__main__':
    main()
