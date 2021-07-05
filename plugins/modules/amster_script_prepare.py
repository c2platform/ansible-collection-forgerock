#!/usr/bin/python

from ansible.module_utils.basic import *
import glob
import os


def script(step, name, template):
    a = "s{}-{}-{}.amster".format(step, template.split('-')[0], name)
    return a.lower().replace('_', '-').replace(' ', '-')


# Return the old name of the script ( so it can be removed )
def obsolete_script_name(step, name, template, dest):
    current_script = script(step, name, template)
    for s in glob.glob("{}/s{}-*".format(dest, step)):
        if s != current_script:
            return s


# Set additional facts in am_configure: step, script, script-obsolete
def amster_script_prepare(data):
    fcts = {}
    fcts['am_configure'] = data['configure']
    i = 1
    for c in fcts['am_configure']:
        c['step'] = str(i).zfill(2)
        c['script'] = script(c['step'], c['name'], c['template'])
        osn = obsolete_script_name(
            c['step'], c['name'], c['template'], data['dest'])
        if osn is not None:
            bn = os.path.basename(osn)
            if bn != c['script']:
                c['script-obsolete'] = bn
        i += 1
    return True, fcts, str(i) + " Amster scripts prepared"


def main():
    fields = {
        "dest": {"required": True, "type": "str"},
        "configure": {"required": True, "type": "list"},
        "templates": {"required": True, "type": "dict"}}
    module = AnsibleModule(argument_spec=fields)
    has_changed, fcts, tr = amster_script_prepare(module.params)
    module.exit_json(changed=False, ansible_facts=fcts, msg=tr)


if __name__ == '__main__':
    main()
