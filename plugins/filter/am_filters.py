"""ansible filters."""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def amster_script_name(am_configure_item, am_configure):
    a = am_configure_item
    idx = amster_script_index(am_configure_item, am_configure)
    # a = 's' + idx + '-' + a['script'] + '.amster'
    a = "s{}-{}.amster".format(idx, a['script'])
    return a.lower().replace('_', '-').replace(' ', '-')


def amster_script_index(am_configure_item, am_configure):
    idx = am_configure.index(am_configure_item)
    return str(idx).zfill(2)


def amster_param_quotes(var):
    if 'string' in var:
        if var['string'] is False:
            return ''
    return '"'


class FilterModule(object):
    """ansible filters."""

    def filters(self):
        return {
            'amster_script_name': amster_script_name,
            'amster_param_quotes': amster_param_quotes,
            'amster_script_index': amster_script_index
        }
