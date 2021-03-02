# Ansible Role ForgeRock Directory Services CLI

This role downloads and installs ForgeRock Directory Services CLI. ForgeRock does not provide a seperate install for CLI utilities.

> Server distributions include command-line tools for installing, configuring, and managing servers. The tools make it possible to script all operations.
> 
> By default, this file unpacks into an opendj/ directory. 
> [Directory Services 7 > Release Notes > Requirements](https://backstage.forgerock.com/docs/ds/7/release-notes/before-you-install.html)

<!-- MarkdownTOC levels="2,3" autolink="true" -->

- [Requirements](#requirements)
- [Role Variables](#role-variables)
- [Dependencies](#dependencies)
- [Example Playbook](#example-playbook)

<!-- /MarkdownTOC -->

## Requirements

This role is basically only an include of the [install](../ds/tasks/install.yml) tasks of the [ds](../ds) role.

```yaml
- include: ../../ds/tasks/install.yml
```

## Role Variables

See also [ds](../ds) role. 

## Dependencies

## Example Playbook
