# Ansible Role ForgeRock Internet Gateway ( IG )

This Ansible role is used to configure [ForgeRock Internet Gateway](https://www.forgerock.com/platform/identity-gateway).

<!-- MarkdownTOC levels="2,3" autolink="true" -->

- [Requirements](#requirements)
- [Role Variables](#role-variables)
    - [Rewrite paths](#rewrite-paths)
- [Dependencies](#dependencies)
- [Example Playbook](#example-playbook)
- [Links](#links)

<!-- /MarkdownTOC -->

## Requirements

<!-- Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required. -->

## Role Variables

<!--  A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well. -->

### Rewrite paths

Paths can be rewritten using `ig_rewrite_paths` for example 

```yaml
ig_rewrite_paths:
  - name: myAppRewritePath
    backend: https://myapplication.com
    target: html/something
    replacement: something/static
```

This will create file `myAppRewritePath.groovy` in `$HOME/.openig/scripts/groovy/`.

## Dependencies

<!--   A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles. -->

## Example Playbook

<!--   Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too: -->

```yaml
    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }
```

## Links

1. [IG 6 Release Notes](https://backstage.forgerock.com/docs/ig/6/release-notes/)
2. [ForgeRock Identity Gateway 7 > Configuration Reference > Configuration Settings|https://backstage.forgerock.com/docs/ig/7/reference/configuration.html)
3. [IG 6 > Configuration Reference](https://backstage.forgerock.com/docs/ig/6/reference/index.html)
4. [ForgeRock Identity Gateway 7 > Configuration Reference > ReverseProxyHandler](https://backstage.forgerock.com/docs/ig/7/reference/ReverseProxyHandler.html)