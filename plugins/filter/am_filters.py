"""ansible filters."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def amster_param_quotes(var):
    if 'string' in var:
        if var['string'] is False:
            return ''
    return '"'


def amster_script_header(item):
    if 'template' in item:
        return "Script: {}\nTemplate: {}".format(
            item['script'], item['template'])
    return "Subscript: {}".format(item)


# Return notify for script or None
def amster_script_notify(script, am_configure, am_amster_templates):
    for itm in am_configure:
        if itm['script'] == script:
            tpl = am_amster_templates[itm['template']]
            if 'notify' in tpl:
                return tpl['notify']
    return 'empty-am-hander'


class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'amster_script_header': amster_script_header,
            'amster_script_notify': amster_script_notify,
            'amster_param_quotes': amster_param_quotes
        }
