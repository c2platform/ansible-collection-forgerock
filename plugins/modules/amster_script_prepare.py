#!/usr/bin/python

from ansible.module_utils.basic import *
# import glob, os, hashlib, uuid


def script(step, template):
    a = "s{}-{}.amster".format(step, template)
    return a.lower().replace('_', '-').replace(' ', '-')


def amster_script_prepare(data):
    fcts = {}
    fcts['am_configure'] = data['configure']
    i = 1
    for c in fcts['am_configure']:
        c['step'] = str(i).zfill(2)
        c['script'] = script(c['step'], c['template'])
        # c['script'] = amster_script_name() # TODO
        i += 1
    return True, fcts, str(i) + " Amster scripts prepared"


def main():
    fields = {
        "configure": {"required": True, "type": "list"},
        "templates": {"required": True, "type": "dict"}}
    module = AnsibleModule(argument_spec=fields)
    has_changed, fcts, tr = amster_script_prepare(module.params)
    module.exit_json(changed=False, ansible_facts=fcts, msg=tr)


if __name__ == '__main__':
    main()
