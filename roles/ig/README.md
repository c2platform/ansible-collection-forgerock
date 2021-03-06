# Ansible Role ForgeRock Internet Gateway ( IG )

This Ansible role is used to configure [ForgeRock Internet Gateway](https://www.forgerock.com/platform/identity-gateway).

<!-- MarkdownTOC levels="2,3" autolink="true" -->

- [Requirements](#requirements)
- [Role Variables](#role-variables)
  - [Config](#config)
  - [Config raw](#config-raw)
  - [Notify handlers for restart etc](#notify-handlers-for-restart-etc)
  - [Routes](#routes)
  - [Rewrite paths](#rewrite-paths)
  - [Alive check](#alive-check)
- [Dependencies](#dependencies)
- [Example Playbook](#example-playbook)
- [Links](#links)

<!-- /MarkdownTOC -->

## Requirements

<!-- Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required. -->

This role assumes that IG is installed using an Ansible role like `c2platform.tomcat`. It assumes that Tomcat is running under account `tomcat` and that the Tomcat home directory will be `/home/tomcat/`. IG creates it own home directory `/home/tomcat/.openig` as part of deployment.

## Role Variables

<!--  A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well. -->

### Config

Use `ig_config` to create [JSON](https://nl.wikipedia.org/wiki/JSON) config files in location `{{ ig_home }}/config`. For example the config 

```yaml
ig_config:
  admin.json:
    mode: DEVELOPMENT
```
will create a file `{{ ig_home }}/config/admin.json` with contents

```json
{
  "mode": "DEVELOPMENT"
}
```

### Config raw

Variable `ig_config_raw` is similar to `ig_config` but will create any type of file. 

```yaml
ig_config_raw:
  logback.xml:
    dest: "{{ ig_home }}/config/logback.xml"
    content: |
      <?xml version="1.0" encoding="UTF-8"?>
      <configuration>
      ...
      </configuration>

```

|parameter|required|default |choices|comments                     |
|---------|--------|--------|-------|-----------------------------|
|dest     |yes     |        |       |Absolute path to config file |
|content  |yes     |        |       |                             |
|owner    |no      |ig_owner|       |                             |
|group    |no      |ig_owner|       |                             |
|mode     |no      |640     |       |                             |

### Notify handlers for restart etc

Changes to `config.json` require restart of service for example Tomcat. For resources defined using `ig_config` you can configure restart using dict `ig_config_notify`. For example to trigger a Tomcat restart for `config.json`

```yaml
ig_config_notify:
  config.json: restart tomcat instance
```

For resources defined using `ig_config_raw` you can use `notify` attribute for example:

```yaml
ig_config_raw:
  logback.xml:
    dest: "{{ ig_home }}/config/logback.xml"
    content: |
      <?xml version="1.0" encoding="UTF-8"?>
      <configuration>
      ...
      </configuration>
    notify: restart tomcat instance
```

### Routes

`ig_routes` TODO

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

### Alive check

To check if ForgeRock IG is fine as part of provision you can configure an `ig_alive_check` for example as shown below. 

```yaml
ig_alive_check:
  url: "https://localhost:{{ tomcat_ssl_connector_port }}/alive/"
  content: "IG is alive!"
```

Next create a alive route using `ig_routes`

```yaml
ig_routes:
  000-alive.json:
    name: 000-alive
    capture: all
    condition: "${ request.uri.path == '/alive/' }"
    handler:
      type: StaticResponseHandler
      config:
        status: 200
        entity: |
          IG is alive!
          contexts.client.remoteAddress: ${contexts.client.remoteAddress}
          request.uri.host: ${request.uri.host}
          request.headers['X-Forwarded-For']:${request.headers['X-Forwarded-For']}
```

Note: IG might for example fail to start because it cannot reach AM or run around in circles because of a redirect loop and crash.

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

* [Identity Gateway 6.5 - Docs - BackStage](https://backstage.forgerock.com/docs/ig/6.5https://backstage.forgerock.com/docs/ig/6.5 )
* [IG 6 Release Notes](https://backstage.forgerock.com/docs/ig/6/release-notes/)
* [ForgeRock Identity Gateway 7 > Configuration Reference > Configuration Settings|https://backstage.forgerock.com/docs/ig/7/reference/configuration.html)
* [IG 6 > Configuration Reference](https://backstage.forgerock.com/docs/ig/6/reference/index.html)
* [ForgeRock Identity Gateway 7 > Configuration Reference > ReverseProxyHandler](https://backstage.forgerock.com/docs/ig/7/reference/ReverseProxyHandler.html)
