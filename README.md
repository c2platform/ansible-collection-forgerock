# Ansible Collection - c2platform.forgerock

[![Linters ( Ansible, YAML )](https://github.com/c2platform/ansible-collection-forgerock/actions/workflows/ci.yml/badge.svg)](https://github.com/c2platform/ansible-collection-forgerock/actions/workflows/ci.yml)

Roles for [ForgeRock](https://www.forgerock.com/) platform.

## Roles

* [ds](./roles/ds) ForgeRock Directory Services.
* [am](./roles/am) ForgeRock Access Management.
* [ig](./roles/ig) ForgeRock Identity Gateway.

## Plugins

Module plugins:

* [amster_scripts_prepare](./plugins/modules/amster_script_prepare.py) facts for Amster scripts to create
* [amster_scripts_prepare_execute](./plugins/modules/amster_script_prepare_execute.py) determine if scripts should run by setting `execute` fact

Filter plugins:

* [am_filters](./plugins/filter/am_filters.py)
* [ds_filters](./plugins/filter/ds_filters.py)
