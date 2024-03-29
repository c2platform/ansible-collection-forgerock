# Ansible Role ForgeRock Directory Services (DS)

This Ansible role can be used to install and configure [ForgeRock Directory Services](https://backstage.forgerock.com/docs/ds/6.5/install-guide/) components using the [Cross-Platform Zip](https://backstage.forgerock.com/docs/ds/6.5/install-guide/#install-files-zip). The role can download and setup DS. Note that default - without additional configuration - this role will only install DS as a command-line utility. To perform actual setup of DS you will have to configure [ds_setup_config](#ds_setup_config) dict at a minimum. 

> Server distributions include command-line tools for installing, configuring, and managing servers. The tools make it possible to script all operations.

<!-- MarkdownTOC levels="2,3,4" autolink="true" -->

- [Requirements](#requirements)
  - [Java](#java)
- [Role Variables](#role-variables)
  - [ds_setup_config](#ds_setup_config)
  - [ds_db_schema_ldifs](#ds_db_schema_ldifs)
  - [ds_config](#ds_config)
    - [LDAPS certificate alias](#ldaps-certificate-alias)
    - [LDAPS](#ldaps)
    - [Global configuration](#global-configuration)
    - [Password policies](#password-policies)
    - [Backends](#backends)
    - [Backend indexes](#backend-indexes)
    - [Attribute Uniqueness](#attribute-uniqueness)
    - [Access control](#access-control)
    - [Other](#other)
  - [ds_config_check_mode](#ds_config_check_mode)
  - [Modify](#modify)
    - [Simple](#simple)
    - [Download](#download)
    - [Existence checks](#existence-checks)
    - [Extra](#extra)
  - [Passwords](#passwords)
  - [Import](#import)
  - [Directories](#directories)
  - [Git](#git)
  - [Files, directories and ACL](#files-directories-and-acl)
  - [Cron](#cron)
  - [Scripts](#scripts)
  - [Replication](#replication)
  - [Backup](#backup)
- [Dependencies](#dependencies)
- [Example configuration](#example-configuration)
  - [Play](#play)
  - [Main](#main)
  - [Config](#config)
- [Links](#links)

<!-- /MarkdownTOC -->

## Requirements

<!--
Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required. -->

### Java

The default is to use the JDK configured in the **java** role in c2platform.core.

```yaml
ds_java_home: "{{ java['version']|c2platform.core.java_home }}"
```

## Role Variables

<!--A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.-->

### ds_setup_config

At a minimum you will require `ds_setup_config` for example as follows

```yaml
ds_setup_config:
  instancePath:  "{{ ds_home_version }}"
  rootUserDN: '"cn=Directory Manager"'
  rootUserPassword: "{{ ds_rootpw }}"
  hostname: "{{ ds_hostname }}"
  adminConnectorPort: "{{ ds_adminport }}"
  ldapPort: 10389
  enableStartTls: ""
  productionMode: ""
  ldapsPort: 10636
  profile: am-config:6.5
  set: "am-config/amConfigAdminPassword:{{ ds_rootpw }}"
  acceptLicense: ""
```


### ds_db_schema_ldifs

Using `ds_db_schema_ldifs` ldifs files can be created in `db/schema`. For example configuration below will create file `/opt/ds/ds-6.5.4/db/schema/appPerson.ldif` to create a new __appPerson__ object class. These files are automatically used upon restart of DS, but depending on a toggle mentioned below.

```yaml
ds_db_schema_ldifs_enable: yes
ds_db_schema_ldifs:
 appPerson: |
   dn: cn=schema
   changetype: modify
   add: attributeTypes
   attributeTypes: ( app-account-expiration-time-oid NAME 'app-account-expiration-time' DESC 'The time the account becomes disabled' EQUALITY generalizedTimeMatch ORDERING generalizedTimeOrderingMatch SUBSTR caseIgnoreSubstringsMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.24 SINGLE-VALUE USAGE userApplications )
   dn: cn=schema
   changetype: modify
   add: objectClasses
   objectClasses: ( AppPerson-oid NAME 'appPerson' DESC 'Extra properties for a app user' SUP top AUXILIARY MAY ( app-account-expiration-time ) )
```

Note: processing of schema LDIF is default disabled with `ds_db_schema_ldifs_enable: no`. This var `ds_db_schema_ldifs_enable` was added to allow you to toggle configuration on / off.

### ds_config

Dict `ds_config` is used to configure DS using [dsconfig](https://backstage.forgerock.com/docs/ds/6.5/configref/) command. The remainder of this section contains examples of the use of this dict starting with a simple example. The dict has groups of lists where each list item configures DS using [dsconfig](https://backstage.forgerock.com/docs/ds/6.5/configref/). 

```yaml
ds_config:
  ldaps:
    - method: set-connection-handler-prop
      handler-name: LDAPS
      add: ssl-cert-nickname:config-server-cert
ds_config_components: ['ldaps']
```

So `ldaps` is just group name, you can use any group name / grouping you want. Groups you want to enable need to be added to `ds_config_components`. This is just a simple lists of group names.

The above dict corresponds to the following command:
```bash
dsconfig set-connection-handler-prop --handler-name LDAPS --add ssl-cert-nickname:config-server-cert
```

In the remainder of this section whenever `dsconfig` is referenced we are using an alias for example defined as follows.

```bash
alias dsconfig="/opt/ds/ds/bin/dsconfig --hostname localhost --port 10636 --bindDN \"cn=Directory Manager\" --bindPasswordFile /root/.dspassword --trustAll --no-prompt"
```

The tasks for `ds_config` are in [tasks/config_component.yml](./tasks/config_component.yml). Note that in this tasks file the module [c2platform.forgerock.ds_config_component](../plugins/modules/ds_config_component.py) is used three times:

1. Dict `ds_config` is prepared for querying the current status of DS. Get commands are added for example `get-connection-handler-prop`.
2. Current vs desired status analysis is performed and this info is added to `ds_config`. Dict `ds_config` resources that require change / update get for example attribute / key `change: true`.
3. Output of change commands is added to `ds_config`.

The `ds_config` dict is written to a file `ds_config.yml` continuously. This file can help with troubleshooting issues and with gaining a better understanding of the way this Ansible role configures DS using `dsconfig` command.

#### LDAPS certificate alias

Default LDAPS certificate alias is `server-cert`. To change it to for example `config-server-cert` using property `ssl-cert-nickname`. This is a simple example of adding an property with value. See for more information [ssl-cert-nickname](https://backstage.forgerock.com/docs/opendj/2.6/configref/ldap-connection-handler.html#ssl-cert-nickname).

```yaml
ds_config:
  ldaps:
    - method: set-connection-handler-prop
      handler-name: LDAPS
      add: ssl-cert-nickname:config-server-cert
ds_config_components: ['ldaps']
```

Below is the Ansible logging for this configuration. It shows that the dict is processed using a number of Ansible tasks. The key tasks are: **Get current config** and **Change config**. The first task checks the current state of DS and the second task changes DS if necessary.

<details>
  <summary>Ansible logging</summary>

TODO 
```
```
</details>

Note also a number of "ds_config" tasks: **ds_config prepared**, **ds_config current** and **ds_config changes**. This role changes the dict `ds_config` which can you help you understand what Ansible / this role is doing. For your convience this changed dict is written to disk in task **Log ds_config → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps.yml**. Note: if you configure `ds_debug: true` the other log files will also be written to disk e.g. `ds_config_0_ldaps_0.yml`.

Log file `ds_config_0_ldaps.yml` is below. Note how the dict `ds_config` has expanded. The list item now has 7 extra keys.

1. Key `change` contains the resuls the *current* vs *desired state* analysis. It is true and so DS was changed, which we can see in logging show above in tasks **Change config**. If we run our play again, `change` would be `false`.
2. key `cmd` contains the `dsconfig` command line. 
3. Key `enabled` is `true`. This is the default. You can use this key to turn specific steps / list items off.
4. key `get` is a dict with with information created to get *current state* of DS with regards to this property.
5. Key `stdout` contains output return by `dsconfig` when changing DS. In this case nothing was returned.
6. Key `step` is just the index of the list item in the group. Which is used for processing results of `dsconfig` commands.
7. Key `when` shows info used to perform *current* vs *desired state* analysis. In this case regex is simple the property value `config-server-cert`. In this case the `match-result` is equal to `match` ( and `false` ) so *current state* is not the *desired state* and `dsconfig` should run.

```yaml
ds_config:
  ldaps:
    -   add: ssl-cert-nickname:config-server-cert
        change: true
        cmd: set-connection-handler-prop --handler-name LDAPS --add ssl-cert-nickname:config-server-cert
        enabled: true
        get:
            cmd: get-connection-handler-prop --handler-name LDAPS --property ssl-cert-nickname
            handler-name: LDAPS
            method: get-connection-handler-prop
            property: ssl-cert-nickname
            stdout: 'Property          : Value(s)
    
                ------------------:------------
    
                ssl-cert-nickname : server-cert'
        handler-name: LDAPS
        method: set-connection-handler-prop
        stdout: ''
        step: 0
        when:
            match: false
            match-result: false
            regex: config-server-cert
```

If we want to now remove this value we could configure for example

```yaml
ds_config:
  ldaps:
    - method: set-connection-handler-prop
      handler-name: LDAPS
      remove: ssl-cert-nickname:config-server-cert
```

The dict `ds_config` is expanded to:

<details>
  <summary>ds_config</summary>

```yaml
ds_config:
  ldaps:
  -   change: true
      cmd: set-connection-handler-prop --handler-name LDAPS --remove ssl-cert-nickname:config-server-cert
      enabled: true
      get:
          cmd: get-connection-handler-prop --handler-name LDAPS --property ssl-cert-nickname
          handler-name: LDAPS
          method: get-connection-handler-prop
          property: ssl-cert-nickname
          stdout: 'Property          : Value(s)
  
              ------------------:--------------------------------
  
              ssl-cert-nickname : config-server-cert, server-cert'
      handler-name: LDAPS
      method: set-connection-handler-prop
      remove: ssl-cert-nickname:config-server-cert
      stdout: ''
      step: 0
      when:
          match: true
          match-result: true
          regex: config-server-cert
```
</details>

#### LDAPS

In previous chapter we have seen example of `add` and `remove`. There is also `set` operation which we use to complete LDAPS configuration:

```yaml
ds_config:
  ldaps:
    - method: set-connection-handler-prop
      handler-name: LDAPS
      add: ssl-cert-nickname:config-server-cert
    - method: set-connection-handler-prop
      handler-name: LDAP
      set: enabled:false
    - method: set-connection-handler-prop
      handler-name: LDAPS
      set: allow-ldap-v2:true
```

The dict `ds_config` is expanded to:

<details>
  <summary>ds_config</summary>

```yaml
ldaps:
-   add: ssl-cert-nickname:config-server-cert
    change: false
    cmd: set-connection-handler-prop --handler-name LDAPS --add ssl-cert-nickname:config-server-cert
    enabled: true
    get:
        cmd: get-connection-handler-prop --handler-name LDAPS --property ssl-cert-nickname
        handler-name: LDAPS
        method: get-connection-handler-prop
        property: ssl-cert-nickname
        stdout: 'Property          : Value(s)

            ------------------:--------------------------------

            ssl-cert-nickname : config-server-cert, server-cert'
    handler-name: LDAPS
    method: set-connection-handler-prop
    step: 0
    when:
        match: false
        match-result: true
        regex: config-server-cert
-   change: false
    cmd: set-connection-handler-prop --handler-name LDAP --set enabled:true
    enabled: true
    get:
        cmd: get-connection-handler-prop --handler-name LDAP --property enabled
        handler-name: LDAP
        method: get-connection-handler-prop
        property: enabled
        stdout: 'Property : Value(s)

            ---------:---------

            enabled  : true'
    handler-name: LDAP
    method: set-connection-handler-prop
    set: enabled:true
    step: 1
    when:
        match: false
        match-result: true
        regex: enabled\s+:\s+true
-   change: false
    cmd: set-connection-handler-prop --handler-name LDAPS --set allow-ldap-v2:true
    enabled: true
    get:
        cmd: get-connection-handler-prop --handler-name LDAPS --property allow-ldap-v2
        handler-name: LDAPS
        method: get-connection-handler-prop
        property: allow-ldap-v2
        stdout: 'Property      : Value(s)

            --------------:---------

            allow-ldap-v2 : true'
    handler-name: LDAPS
    method: set-connection-handler-prop
    set: allow-ldap-v2:true
    step: 2
    when:
        match: false
        match-result: true
        regex: allow-ldap-v2\s+:\s+true
```
</details>

#### Global configuration

```yaml
ds_config:
  global:
    - method: set-global-configuration-prop
      set: lookthrough-limit:20000
    - method: set-global-configuration-prop
      set: smtp-server:127.0.0.1:25
    - method: set-global-configuration-prop
      set: size-limit:10000
ds_config_components: ['global']

```

#### Password policies

Config below shows how we can create password policy **Default Password Policy** using one `set` key with two property-value pairs. Note: these properties are required to be able to create a password policy.

```yaml
ds_config:
  default-password-policy:
    - method: create-password-policy
      policy-name: Default Password Policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
```

This is expanded to: 

<details>
  <summary>ds_config</summary>

```yaml
ds_config:
  password-policy:
  -   change: false
      cmd: set-password-policy-prop --policy-name "Default Password Policy" --set   "default-password-storage-scheme:Salted
          SHA-512" --set password-attribute:userPassword
      enabled: true
      get:
          cmd: get-password-policy-prop --policy-name "Default Password Policy" --property
              default-password-storage-scheme --property password-attribute
          method: get-password-policy-prop
          policy-name: Default Password Policy
          property:
          - default-password-storage-scheme
          - password-attribute
          stdout: 'Property                        : Value(s)
  
              --------------------------------:---------------
  
              default-password-storage-scheme : Salted SHA-512
  
              password-attribute              : userPassword'
      method: set-password-policy-prop
      policy-name: Default Password Policy
      set:
      - default-password-storage-scheme:Salted SHA-512
      - password-attribute:userPassword
      step: 0
      when:
      -   match: false
          match-result: true
          regex: default-password-storage-scheme\s+:\s+Salted SHA-512
      -   match: false
          match-result: true
          regex: password-attribute\s+:\s+userPassword
```
</details>

We can `set`, `add` and `remove` password policy properties.

```yaml
ds_config:
  password-policies:
    - method: set-password-policy-prop
      policy-name: "Default Password Policy"
      set: 
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
        - deprecated-password-storage-scheme:Salted SHA-1
        - last-login-time-attribute:ds-pwp-last-login-time
        - last-login-time-format:yyyyMMddHHmmss
        - password-expiration-warning-interval:604800 s # 7 days
        - min-password-age:86400 s # 24 hours
        - password-change-requires-current-password:true
        - password-history-duration:0 s # 0 seconds
      add:
        - password-validator:Length-Based Password Validator
        - password-validator:Similarity-Based Password Validator
        - password-validator:Attribute Value
        - password-validator:Unique Characters
        - password-validator:Character Set
      remove:
        - password-validator:At least 8 characters
        - password-validator:Common passwords
        - password-validator:Dictionary
        - password-validator:Repeated Characters
```

Note: use time in seconds as shown above. It is possible to configure `7 days` for `password-expiration-warning-interval` but this will cause this property to show up as changed on current vs desired state comparison because DS reports back this setting in seconds.

#### Backends

Backends can be created using config shown below. This config will use [dsconfig create-backend](https://backstage.forgerock.com/docs/ds/7/config-guide/import-export.html#create-database-backend) to create the backend.

```yaml
ds_config:
  backend-create:
    - method: create-backend
      set:
        - base-dn:c=NL
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: siwuRoot
    - method: create-backend
      set:
        - base-dn:dc=iwkb,dc=nl
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: userRoot
```

#### Backend indexes

Backend indexes are created using [dsconfig create-backend-indexes](https://backstage.forgerock.com/docs/ds/5/configref/create-backend-index.html)

```yaml
ds_config:
  backend-indexes-create:
    - method: create-backend-index
      backend-name: siwuRoot
      index-name: member
      set:
        - index-type:equality
        - index-entry-limit:4000
ds_config_components:
  - backend-indexes-create
```

This is expanded to: 

<details>
  <summary>ds_config</summary>

```yaml
ds_config:
    backend-index-create-userRoot:
    -   backend-name: userRoot
        change: true
        cmd: create-backend-index --backend-name userRoot --set index-type:equality
            --set index-entry-limit:4000 --index-name member
        enabled: true
        get:
            backend-name: userRoot
            cmd: list-backend-indexes --backend-name userRoot -s
            method: list-backend-indexes
            property: []
            stdout: 'aci

                ds-sync-conflict

                ds-sync-hist

                entryUUID

                objectClass'
        index-name: member
        method: create-backend-index
        property-update: []
        set:
        - index-type:equality
        - index-entry-limit:4000
        stdout: '

            The Backend Index was created successfully'
        step: 0
        when:
        -   change: true
            match-expected: false
            match-result: false
            regex: userRoot\n
```
</details>


#### Attribute Uniqueness

Make for example `uid` unique. See also [Attribute Uniqueness](https://backstage.forgerock.com/docs/ds/7/config-guide/attribute-uniqueness.html).

```yaml
ds_config:
  uid-unique:
    - method: set-plugin-prop
      plugin-name: UID Unique Attribute
      set:
        - enabled:true
ds_config_components:
  - uid-unique
```

#### Access control

Access control can be managed using [set-access-control-handler-prop](https://backstage.forgerock.com/docs/ds/7.1/configref/subcommands-set-access-control-handler-prop.html). Show below is example of add two global access control policies using `global-aci` key. See also [Access Control](https://backstage.forgerock.com/docs/ds/7/security-guide/access.html).

```yaml
ds_config:
  access-control-handler-properties:
    - method: set-access-control-handler-prop
      add:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2 || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18 || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\") (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
ds_config_components:
  - access-control-handler-properties
```

This is expanded to: 

<details>
  <summary>ds_config</summary>

```yaml
ds_config:
    access-control-handler-properties:
    -   add:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl
            \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2
            || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18
            || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\")
            (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
        change: true
        cmd: set-access-control-handler-prop --add global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\")
            (version 3.0; acl \"Authenticated users control access\"; allow(read)
            userdn=\"ldap:///all\";)" --add global-aci:"(targetcontrol=\"1.3.6.1.1.12
            || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2 || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3
            || 2.16.840.1.113730.3.4.18 || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473
            || 1.3.6.1.4.1.42.2.27.9.5.9\") (version 3.0; acl \"and the rest\"; allow(read)
            userdn=\"ldap:///all\";)"
        comment: global-aci
        enabled: true
        get:
            cmd: get-access-control-handler-prop --property global-aci -s
            method: get-access-control-handler-prop
            property:
            - global-aci
            stdout: "enabled\ttrue\nglobal-aci\t(extop=\"1.3.6.1.4.1.26027.1.6.3 ||\
                \ 1.3.6.1.4.1.1466.20037\") (version 3.0; acl \"Anonymous extended\
                \ operation access\"; allow(read) userdn=\"ldap:///anyone\";)\t(extop=\"\
                1.3.6.1.4.1.4203.1.11.1 || 1.3.6.1.4.1.4203.1.11.3 || 1.3.6.1.1.8\"\
                ) (version 3.0; acl \"Authenticated users extended operation access\"\
                ; allow(read) userdn=\"ldap:///all\";)\t(target = \"ldap:///cn=schema\"\
                )(targetattr = \"attributeTypes || objectClasses\")(version 3.0; acl\
                \ \"Modify schema\"; allow (write) (userdn = \"ldap:///uid=am-config,ou=admins,ou=am-config\"\
                );)\t(target=\"ldap:///\")(targetscope=\"base\") (targetattr=\"objectClass||namingContexts||supportedAuthPasswordSchemes||supportedControl||supportedExtension||supportedFeatures||supportedLDAPVersion||supportedSASLMechanisms||supportedTLSCiphers||supportedTLSProtocols||vendorName||vendorVersion||alive||healthy\"\
                )(version 3.0; acl \"User-Visible Root DSE Operational Attributes\"\
                ; allow (read,search,compare) userdn=\"ldap:///anyone\";)\t(target=\"\
                ldap:///cn=schema\")(targetscope=\"base\") (targetattr=\"objectClass||attributeTypes||dITContentRules||dITStructureRules\
                \ ||ldapSyntaxes||matchingRules||matchingRuleUse||nameForms||objectClasses\"\
                ) (version 3.0; acl \"User-Visible Schema Operational Attributes\"\
                ; allow (read,search,compare) userdn=\"ldap:///all\";)\t(targetcontrol=\"\
                1.3.6.1.1.13.1||1.3.6.1.1.13.2 ||1.2.840.113556.1.4.805||1.2.840.113556.1.4.1413\"\
                ) (version 3.0; acl \"REST to LDAP control access\"; allow(read) userdn=\"\
                ldap:///all\";)\t(targetcontrol=\"1.3.6.1.4.1.36733.2.1.5.1\") (version\
                \ 3.0; acl \"Transaction ID control access\"; allow(read) userdn=\"\
                ldap:///all\";)"
        method: set-access-control-handler-prop
        property-update:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl
            \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2
            || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18
            || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\")
            (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
        stdout: ''
        step: 0
        when:
        -   change: true
            match-expected: false
            match-result: false
            prop: global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version
                3.0; acl \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)"
            regex: "global-aci.*\t\\(targetcontrol\\=\\\"2\\.16\\.840\\.1\\.113730\\\
                .3\\.4\\.18\\\"\\)\\ \\(version\\ 3\\.0\\;\\ acl\\ \\\"Authenticated\\\
                \ users\\ control\\ access\\\"\\;\\ allow\\(read\\)\\ userdn\\=\\\"\
                ldap\\:\\/\\/\\/all\\\"\\;\\)[\t|\n]"
        -   change: true
            match-expected: false
            match-result: false
            prop: global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2
                || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18
                || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\")
                (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
            regex: "global-aci.*\t\\(targetcontrol\\=\\\"1\\.3\\.6\\.1\\.1\\.12\\\
                \ \\|\\|\\ 1\\.3\\.6\\.1\\.1\\.13\\.1\\ \\|\\|\\ 1\\.3\\.6\\.1\\.1\\\
                .13\\.2\\ \\|\\|\\ 1\\.2\\.840\\.113556\\.1\\.4\\.319\\ \\|\\|\\ 1\\\
                .2\\.826\\.0\\.1\\.3344810\\.2\\.3\\ \\|\\|\\ 2\\.16\\.840\\.1\\.113730\\\
                .3\\.4\\.18\\ \\|\\|\\ 2\\.16\\.840\\.1\\.113730\\.3\\.4\\.9\\ \\\
                |\\|\\ 1\\.2\\.840\\.113556\\.1\\.4\\.473\\ \\|\\|\\ 1\\.3\\.6\\.1\\\
                .4\\.1\\.42\\.2\\.27\\.9\\.5\\.9\\\"\\)\\ \\(version\\ 3\\.0\\;\\\
                \ acl\\ \\\"and\\ the\\ rest\\\"\\;\\ allow\\(read\\)\\ userdn\\=\\\
                \"ldap\\:\\/\\/\\/all\\\"\\;\\)[\t|\n]"

```
</details>

To remove those `global-aci` just replace `add` with `remove`

```yaml
ds_config:
  access-control-handler-properties:
    - method: set-access-control-handler-prop
      remove:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2 || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18 || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\") (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
ds_config_components:
  - access-control-handler-properties
```

#### Other

This DS role processes the `ds_config` in a structured and generic way and so will support other types of changes not described above. For example simple setting, adding, removing of properties will be supported. So if you want to use a method like `set-<component-name>-prop` not mentioned in this text, it will work.

For other methods for example `create-backend-index` this will require extra configuration, which you can provide, without the need to change this role.

```yaml
ds_config:
  backend-indexes-create:
    - method: create-backend-index
      backend-name: siwuRoot
      index-name: member
      set:
        - index-type:equality
        - index-entry-limit:4000
ds_config_components:
  - backend-indexes-create
```

For these type of methods there is an additional dict `ds_config_get_methods` which has default values see [defaults/main.yml](./defaults/main.yml).

```yaml
ds_config_get_methods:
  create-password-policy:
    method: list-password-policies
    regex_key: policy-name
  create-backend:
    method: list-backends
    regex_key: backend-name
  create-backend-index:
    method: list-backend-indexes
    regex_key: index-name
    keys:
      - backend-name
```

Note the key `create-backend-index`. So using `ds_config_get_methods` we configure the get method to use `list-backend-indexes`, the keys to add to the get command-line `backend-name` and we also configure which key to use for constructing a regular expression to check current status `index-name`. If you check `logs/ds_config.yml` you can see that from this configuration the get command is `dsconfig list-backend-indexes --backend-name siwuRoot -s` and the `regex` is simply `member\n`.

### ds_config_check_mode

The DS role has a check mode var `ds_config_check_mode` default `false` that you can use for `ds_config`. This [check mode](https://docs.ansible.com/ansible/latest/user_guide/playbooks_checkmode.html) focuses only on `ds_config` and it basically disabled to chance commands. 

### Modify

Modify the directory using [LDIF](https://en.wikipedia.org/wiki/LDAP_Data_Interchange_Format) by using `ds_modify`. This holds an ordered list of ldifs to be used to modify DS using `./ldapmodify`.

Use `ds_modify_enabled: false` to disable apply of LDIF. 

#### Simple

DS is checked for the existence of the DN as present on the first line of the LDIF. If the DN does not exist, the LDIF is applied.

```yaml
ds_modify:
  - name: userstore.orgRoot
    ldif: |
      dn: c=NL
      objectClass: country
      objectClass: top
      c: NL
  - name: userstore.userRoot
    ldif: |
      dn: dc=org,dc=nl
      objectClass: domain
      objectClass: top
      dc: org
```

#### Download

Optionally you can also configure the LDIF to be downloaded using `ldif-url`. Let's say we have an LDIF file `file:///vagrant/downloads/akaufman.ldif` with following contents

```yaml
dn: cn=akaufman,o=special,c=NL
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
cn: akaufman
sn: Andy's special account
givenName: Andy
uid: akaufman
userPassword: secret
```

The following configuration will create this entry
```yaml
ds_modify_extra:
  - name: akaufman
    ldif-url: file:///vagrant/downloads/akaufman.ldif
    dn: cn=akaufman,o=special,c=NL
```

Notice the extra `dn`. This is used for existence check.

#### Existence checks

The default is to perform existence check before applying LDIF by using the `dn` on first line of the LDIF. For example LDIF fragment below will be applied only if `c=NL` does not exists.

```yaml
ds_modify:
  - name: userstore.orgRoot
    ldif: |
      dn: c=NL
      objectClass: country
      objectClass: top
      c: NL
```

The `dn` can also explicitly be specified.
```yaml
ds_modify:
  - name: somename
    ldif: |
      someldif
    dn: cn=akaufman,o=special,c=NL
```

Other LDIF than simple adding require you to specifiy a `not_if` attribute to check for existence as shown below. Note the default DN check is an example of a `not_if` condition. 

```yaml
ds_modify:
      - name: add-ACI-to-cNL
        ldif: |
          dn: c=NL
          changetype: modify
          add: aci
          aci: (target="ldap:///o=myapp,c=nl")(targetattr ="*")(version 3.0; acl "Allow apps proxiedauth"; allow(all, proxy)(userdn = "ldap:///cn=sa_useradmin,o=special,c=nl");)
        not_if: "&(objectclass=top)(c=NL)(aci=*)"
```

You can also configure an `only_if` condition. The example below shows both `not_if` and `only_if` being used. The particular account `amUserAdmin` is not created using LDIF, it is created using ForgeRock AM. We only want to use LDIF to add an attribute to the user *if* the user exists.

```yaml
  - name: amUserAdmin
    base_dn: dc=iwkb,dc=nl
    ldif: |
      dn: uid=amUserAdmin,ou=people,dc=iwkb,dc=nl
      changetype: modify
      add: ds-pwp-password-policy-dn
      ds-pwp-password-policy-dn: cn=Password Policy Service Accounts,cn=Password Policies,cn=config
    not_if: "&(objectclass=top)(uid=amUserAdmin)(ds-pwp-password-policy-dn=*)"
    only_if: "uid=amUserAdmin"
```

#### Extra

Using `ds_modify_extra`. This variable works exactly the same as `ds_modify`. Anything you configure with this var will be applied to DS using `ldapmodify`.

### Passwords

To configure passwords use `ds_passwords`. 

```yaml
ds_passwords: # see also secrets.yml
    sa_reports:
      authzId: cn=sa_reports,o=special,c=NL
      newPassword: supersecure
    sa_monitor:
      authzId: cn=sa_monitor,o=special,c=NL
      newPassword: supersecure
    sa_useradmin:
      authzId: cn=sa_useradmin,o=special,c=NL
      newPassword: supersecure
```

This feature also a fingerprint file `ds_passwords` that will prevent Ansible resetting the password each run. You can force password reset using `ds_passwords_force`. This might be for example necessary when for example `ds_import` imports accounts with wrong / other passwords.

```yaml
ds_passwords_force: yes
```

### Import

To download and import LDIF files using [import-ldif](https://backstage.forgerock.com/docs/ds/7/tools-reference/import-ldif-1.html) use `ds_import` for example as follows:

```yaml
ds_import:
  - name: 03-onlUserAttrs
    ldif-url: file:///vagrant/downloads/03-onlUserAttrs.ldif
    properties:
      includeBranch: c=nl
      excludeAttribute:
        - ds-pwp-password-expiration-time
        - pwdHistory
      skipFile: /tmp/03-onlUserAttrs-skipped.ldif
      rejectFile: /tmp/03-onlUserAttrs-reject.ldif      
      skipSchemaValidation: '' # required with custom object classes
      no-prompt: ''
      offline: ''      
```

Note: option `skipSchemaValidation` is required when importing LDIF with custom / self defined object classes as `import-ldif` will fail on schema validation of those object classes. 

Imports using `ds_import` will be done offline / after stopping `ds-config` service.

It is possible to do some post-processing of the LDIF using `sed` as shown below.

```yaml
ds_import:
  - name: export
    ldif-url: file:///vagrant/downloads/export.ldif
    properties:
      backendId: myappRoot
      skipFile: /tmp/export-skipped.ldif
      rejectFile: /tmp/export-reject.ldif
      no-prompt: ''
      offline: ''
    sed:
      - 's/dn: c=nl/dn: c=NL/g'
      - 's/c: nl/c: NL/g'
```

Note: import is default disabled using `ds_import_enable: no`. This var can be used to toggle import on / off.

### Directories

Create additional directories using `ds_directories` for example to create a `scripts` directory

```yaml
ds_directories:
- "{{ ds_home_version }}/scripts"
```
### Git

Fetch arbitrary files from a Git repository and add them to DS filesystem. To configure the repo and the parent dir for this repository.

```yaml
ds_git_config:
  repo: https://myrepo
  proxy: http://localhost:8888
ds_git_config_parent_dir: /tmp
```
This will create a folder `/tmp/ds-git-config-<hash>`. You can also create this clone on the control for example if nodes don't have internet access. In this case we configure a custom checkout script using `ds_git_config_script` because the Ansible Git module does not allow any Git config.

```yaml
ds_git_config_control_node: yes
ds_git_config_script: |
  if [ ! -d "{{ ds_git_config['dir'] }}" ]; then
    git init {{ ds_git_config['dir'] }}
    cd {{ ds_git_config['dir'] }}
    git remote add origin {{ ds_git_config['repo'] }}
    git config http.proxy {{ ds_git_config['proxy'] }}
    git config pull.ff only
  fi
  cd {{ ds_git_config['dir'] }}
  git pull origin master
```

Configure where the files should be created using `ds_git_files`

```yaml
ds_git_files:
- source: ds/scripts/ldap_wrapper.py
  dest: "{{ ds_home_version }}/scripts/ldap_wrapper.py"
- source: ds/scripts/migrate-admin-aci.py
  dest: "{{ ds_home_version }}/scripts/migrate-admin-aci.py"
- source: ds/scripts/migrate-siwunet-expiry.py
  dest: "{{ ds_home_version }}/scripts/migrate-siwunet-expiry.py"
```

In the above example we are putting the files in a directory `scripts` that does not exist. To create it we can use `ds_directories`.

```yaml
ds_directories:
- "{{ ds_home_version }}/scripts"
```

Note: if we want to execute those scripts, see [Scripts](#scripts) 

### Files, directories and ACL

Use dicts `ds_files`, `ds_directories`, `ds_acl` to create / manage any other files, directories and ACL. See [c2platform.core.files](https://github.com/c2platform/ansible-collection-core/tree/master/roles/files) for more information For example see [Backup](#backup).

### Cron

Using `ds_cron` cron jobs in `/etc/cron.d` can be created / managed. For example see [Backup](#backup).

### Scripts

Use `ds_scripts` to configure execution of all kinds of scripts using Ansible [shell](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/shell_module.html) module.

```yaml
ds_scripts_connect:
  hostname: "{{ ds_connect['hostname'] }}"
  port: "{{ ds_connect['port'] }}"
  bindDN:  "{{ ds_connect['bindDN'] }}"
  bindPassword: "{{ ds_connect['bindPassword'] }}"
  baseDn: c=NL

ds_git_repos:
  scripts:
    repo: "{{ myapp_ds_scripts_repo }}" # vault
    dest: "{{ ds_home_version }}/scripts"

ds_scripts:
  password-reset_subentry-write:
    shell: |
      python3 migrate-admin-aci.py {{ ds_connect|c2platform.forgerock.ds_cmd }}
    chdir: "{{ ds_home_version }}/scripts/ds"
```

Typically DS scripts will require pip package [python-ldap](https://pypi.org/project/python-ldap/). This pip package typically requires OS packages to installed as well. When using [core](https://github.com/c2platform/ansible-collection-core) collection these can be configured as follows.

```yaml
common_pip_packages_extra: ['python-ldap']
common_packages_extra:
  Ubuntu 18:
    - build-essential
    - python3-dev
    - python3-wheel
    - libsasl2-dev
    - libldap2-dev
    - libssl-dev
```

### Replication

To create a two node cluster with [replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1) you can add `ds_replication` var similar to shown below:

```yaml
ds_replication_global_admin: admin
ds_replication_global_admin_password: supersecure
ds_replication_port: 8989

ds_replication: 
  replication-server:
    hostname: ""
    inventory_hostname: "{{ groups['myapp_ds'][0] }}"
    port: "{{ ds_adminport }}"
    bindDN:  cn=Directory Manager
    bindPassword: supersecret
    trustAll: ""
    no-prompt: ""
  host1:
    replication_port: 8990 # optional if != ds_replication_port  
    # same as replication-server
  host2: 
    replication_port: 8990 # optional if != ds_replication_port  
    # same as replication-server
  baseDNs:
    - ou=am-config
    - c=NL
    - dc=myapporg,dc=nl
```

If one of the servers is unavailable, the setup will fail. This is one reason that in the overall process flow we install replication in a separate Ansible run, as then it's guaranteed that AWX has completed the base install and both servers are available.

The possible settings under `replication-server`, `host1` and `host2` are mostly optional they will default to `ds_connect`. To setup replication at a minimum you need to configure:

```yaml
ds_replication_enable: yes
ds_replication:
 replication-server:
   hostname: "{{ groups['myapp_ds'][0] }}.iwkb.local"
   inventory_hostname: "{{ groups['myapp_ds'][0] }}"
 host2:
   hostname: "{{ groups['myapp_ds'][1] }}.iwkb.local"
 baseDNs:
   - ou=am-config
   - c=NL
   - dc=iwkb,dc=nl
```
Which implies that host 1 will also be the replication server with hostname `1.1.1.51.nip.io` etc. Note that `ds_replication_enable` is default `no`. You can use this variable as a toggle to provision with / without replication.

Configuration above will result in command being executed similar to 

```bash
./dsreplication configure  \
--host1 1.1.1.51.nip.io --port1 4444 --bindDn1 "cn=Directory Manager" \
--bindPassword1 supersecret --secureReplication1 --replicationPort1 8989 \
--host2 1.1.1.58.nip.io --port2 4444 --bindDn2 "cn=Directory Manager" \
--bindPassword2 supersecret --secureReplication2 --replicationPort2 8989 \
--baseDN dc=myapporg,dc=nl \
--adminUid admin --adminPassword Su12perSec34retIt5Is \
--trustAll  --no-prompt
```

To check the replication status

```bash
./dsreplication status --hostname 1.1.1.51.nip.io --port 4444 \
--adminUID admin --adminPassword Su12perSec34retIt5Is  \
--trustAll --no-prompt
```

The required arguments for the different dsreplication scenarios differ quite a bit, hence below the scenarios, where used
in the code (and the requirements in the XLS) and unique arguments. These also help explaining the refactoring/normalisation
of the dsreplication arguments.
* status: _used_  for initial check and for listing the configured dn's if already something is running. _arguments_ adminUID and adminPassword.
* configure: _used_ for creating (--baseDN is already an itemised list hence no loop needed), again for intial and for delta. _arguments_ basically all, notably bind and admin.
* initialize-all: _used_ as a follow-up of configure, it activates the replication config. _arguments_ adminUID and adminPassword, baseDN

To configure replication you can use `ds_config_components_replication` for example:

```yaml
ds_config:
  replication-server:
    - provider-name: Multimaster Synchronization
      set:
        - changelog-enabled:disabled

ds_config_components_replication:
  - replication-server
```

### Backup

There are no dedicated Ansible variables for creating a DS backup but it can be configured using `ds_files` and `ds_cron`. This section shows an actual example of how this was done on a project.

First, for our convience, we created some dictionaries. This is of course not required.
```yaml
siwunet_ds_backup_incremental0:
  port: "{{ ds_adminport }}"
  bindDN: 'cn=Directory Manager'
  bindPasswordFile: "{{ ds_password_file }}"
  incremental: ""
  backendID: siwuRoot
  incrementalBaseID: full_daily
  backupID: incremental0
  backupDirectory: /opt/ds/ds/bak/current/siwuRoot/
  recurringTask: "5,10,15,20,25,30,35,40,45,50,55 0 * * *"
  errorNotify: "{{ siwunet_support_mail_address }}"
  hostname: 127.0.0.1
  trustAll:

siwunet_ds_backup_incremental1:
  backupID: incremental1
  recurringTask: "0,5,10,15,20,25,30,35,40,45,50,55 1-23 * * *"

siwunet_ds_manage_tasks:
  port: "{{ ds_adminport }}"
  bindDN: cn=Directory Manager
  bindPasswordFile: "{{ ds_password_file }}"
  hostname: 127.0.0.1
  trustAll:

siwunet_ds_backup:
  port: "{{ ds_adminport }}"
  bindDN: cn=Directory Manager
  bindPasswordFile: "{{ ds_password_file }}"
  hostname: 127.0.0.1
  trustAll:
  start: 0
  backUpAll:
  backupID: full_daily
  backupDirectory: "{{ ds_home_link }}/bak/current"

siwunet_ds_backup_scripts:
  create_incr: /usr/local/bin/ds65-backup-incr.sh
  list_incr: /usr/local/bin/ds65-backup-incr-list.sh
  backup: /usr/local/bin/ds65-backup.sh
```

Now we us `ds_files` to configure some backup scripts.

```yaml
ds_files:
  incremental-backup-create-script:
    dest: "{{ siwunet_ds_backup_scripts['create_incr'] }}"
    content: |
      #!/bin/bash
      # Create DS scheduled tasks for incremental backups

      echo "## Create incremental0"
      sudo {{ ds_home_link }}/bin/backup \
      {{ siwunet_ds_backup_incremental0|c2platform.forgerock.ds_cmd_ml }}

      echo "## Create incremental1"
      sudo {{ ds_home_link }}/bin/backup \
      {{ siwunet_ds_backup_incremental0|combine(siwunet_ds_backup_incremental1)|c2platform.forgerock.ds_cmd_ml }}
    mode: '0755'
  increment-backup-list-script:
    dest: "{{ siwunet_ds_backup_scripts['list_incr'] }}"
    content: |
      #!/bin/bash
      # List DS scheduled tasks
      OUTPUTTMP=$(mktemp)

      # List the summary of all tasks
      echo "### show task summary"
      sudo {{ ds_home_link }}/bin/manage-tasks --summary \
      {{ siwunet_ds_manage_tasks|c2platform.forgerock.ds_cmd_ml }} > $OUTPUTTMP
      cat $OUTPUTTMP
      echo

      # List the details of recurring tasks
      RECURRING=$(awk '/Recurring/ {print $1}' ${OUTPUTTMP})
      if [ -z "${RECURRING}" ]; then
        echo "### no recurring tasks"
       else
        for TASK in $RECURRING; do
          echo "### task $TASK"
          sudo {{ ds_home_link }}/bin/manage-tasks --info $TASK \
      {{ siwunet_ds_manage_tasks|c2platform.forgerock.ds_cmd_ml(8) }}
        done
      fi
      # Cleanup
      rm $OUTPUTTMP
    mode: '0755'
  backup-script:
    dest: "{{ siwunet_ds_backup_scripts['backup'] }}"
    content: |
      #!/bin/bash

      DATE=$(date +%Y%m%d)
      DIR={{ ds_home_link }}/bak/
      LINK=current

      mkdir $DIR/$DATE
      chown -R {{ ds_owner }}.{{ ds_owner }} $DIR/$DATE
      rm -rf $DIR/$LINK
      ln -s $DIR/$DATE $DIR/$LINK

      {{ ds_home_link }}/bin/backup \
      {{ siwunet_ds_backup|c2platform.forgerock.ds_cmd_ml }}
    mode: '0755'
```

And some cron jobs using `ds_cron`

```yaml
ds_cron:
  daily:
    hour: "0"
    minute: "0"
    job: "{{ siwunet_ds_backup_scripts['backup'] }} >> /var/log/ds-daily-backup.log"
    cron_file: ds-backup-daily
  clean:
    hour: "23"
    minute: "0"
    job: "find {{ ds_home_link }}/bak -mmin +2800 -delete 2>/dev/null"
    cron_file: ds-backup-daily-cleanup
  clean-incremental:
    hour: "*"
    minute: "*/30"
    job: "find {{ ds_home_link }}/bak  -type f -mmin +60 -not -name *_daily -not -name backup.info -delete 2>/dev/null"
    cron_file: ds-backup-incr-cleanup
```

* [FAQ: Backup and restore in DS 5.x and 6.x - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a89103342)
* [DS 6.5 > Reference](https://backstage.forgerock.com/docs/ds/6.5/reference/index.html#backup-1)
* [DS 6.5 > Administration Guide - To Schedule Incremental Backup](https://backstage.forgerock.com/docs/ds/6.5/admin-guide/#schedule-incremental-backup)
* [Chapter 34. manage-tasks — manage server administration tasks](https://backstage.forgerock.com/docs/ds/6.5/reference/#manage-tasks-1)

## Dependencies

<!--A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.-->

## Example configuration

The example configuration in this section also shows vars prefixed with `siwunet_`. These are just "helper" variables. They only exist in `group_vars` to help set actual DS vars that are prefixed with `ds_`. 

There is a lot of configuration so typically you would split this up in seperate YAML files in a `group_vars` directory for your group. In this example we have for example `group_vars/my_ds/main.yml`, `group_vars/my_ds/config.yml` etc.

### Play

```yaml
- name: my_ds.yml
  hosts: my_ds
  become: yes

  roles:
    - { role: c2platform.core.common,  tags: ["common"] }
    - { role: c2platform.core.java,    tags: ["java"] }
    - { role: c2platform.forgerock.ds, tags: ["forgerock","ds"] }

  vars:
    ds_debug: false
    ds_passwords_force: false
```

### Main

For example in a `main.yml` we might have

```yaml
---
ds_version: 6.5.5
ds_versions:
  6.5.5:
    url: "{{ my_artefact_repo }}/software/forgerock/DS-6.5.5.zip"
    checksum: "sha256: 05865497d76e73a23894d4ce1ccd4478026f0eae8152b0934b266a85d00fe7bd"

common_pip_packages_extra: ['python-ldap']

ds_connect:
  hostname: "{{ ansible_fqdn }}"
  port: "{{ ds_adminport }}"

ds_hostname: "{{ inventory_hostname }}.bkd.local"

ds_setup_config:
  instancePath:  "{{ ds_home_version }}"
  rootUserDN: '"cn=Directory Manager"'
  rootUserPassword: "{{ ds_rootpw }}"
  hostname: "{{ ds_hostname }}"
  adminConnectorPort: "{{ ds_adminport }}"
  ldapPort: 10389
  enableStartTls: ""
  productionMode: ""
  ldapsPort: 10636
  profile: am-config:6.5
  set: "am-config/amConfigAdminPassword:{{ ds_rootpw }}"
  acceptLicense: ""

ds_replication_enable: true
```

### Config

In `config.yml`

```yaml
---
# ds_config, ds_config_components
siwunet_ds_config_backend_index_templates:
  index_type1:
    method: create-backend-index
    backend-name: siwuRoot
    set:
      - index-type:equality
      - index-entry-limit:4000
  index_type2:
    method: create-backend-index
    backend-name: siwuRoot
    set:
      - index-type:equality
      - index-type:substring
      - index-entry-limit:4000

siwunet_backend_index_create:
  - "{{ siwunet_ds_config_backend_index_templates['index_type1']|combine({ 'index-name':'member' }) }}"
  - "{{ siwunet_ds_config_backend_index_templates['index_type1']|combine({ 'index-name':'uniqueMember' }) }}"
  - "{{ siwunet_ds_config_backend_index_templates['index_type1']|combine({ 'index-name':'ou' }) }}"
  - "{{ siwunet_ds_config_backend_index_templates['index_type2']|combine({ 'index-name':'cn' }) }}"
  - "{{ siwunet_ds_config_backend_index_templates['index_type2']|combine({ 'index-name':'givenName' }) }}"
  - "{{ siwunet_ds_config_backend_index_templates['index_type2']|combine({ 'index-name':'sn' }) }}"
  - "{{ siwunet_ds_config_backend_index_templates['index_type2']|combine({ 'index-name':'mail' }) }}"
  - method: create-backend-index
    set:
      - index-type:equality
      - index-type:substring
      - index-entry-limit:100000
    backend-name: siwuRoot
    index-name: businessCategory
  - method: create-backend-index
    set:
      - index-type:equality
      - index-type:substring
      - index-entry-limit:100000
    backend-name: siwuRoot
    index-name: uid

# Password policy settings
siwunet_ds_config_pps:
  generic:
    - default-password-storage-scheme:Salted SHA-512
    - password-attribute:userPassword
    - deprecated-password-storage-scheme:Salted SHA-1
    - last-login-time-attribute:ds-pwp-last-login-time
    - last-login-time-format:yyyyMMddHHmmss
    - password-expiration-warning-interval:604800 s # 7 days
    - min-password-age:86400 s # 24 hours
    - password-change-requires-current-password:true
    - password-history-duration:0 s # 0 seconds
    # - skip-validation-for-administrators:true # seperate group
    - require-secure-authentication:true
  default:
    - allow-user-password-changes:true
    - expire-passwords-without-warning:true
    - grace-login-count:2
    - lockout-duration:0 s # 0 minutes
    - lockout-failure-expiration-interval:0 s # 0 minutes
    - lockout-failure-count:5
    - max-password-reset-age:1209600 s # 14 days
    - password-history-count:10
    - require-secure-password-changes:true
    - max-password-age:4838400 s # 56 days
    - force-change-on-add:true
    - force-change-on-reset:true
    - idle-lockout-interval:3888000 s # 45 days
  service-accounts:
    - expire-passwords-without-warning:false
    - force-change-on-add:false
    - force-change-on-reset:false
    - grace-login-count:10
    - idle-lockout-interval:172800000 s # 2000 days
    - lockout-duration:1 s
    - lockout-failure-expiration-interval:1 s
    - lockout-failure-count:10000
    - max-password-age:172800000 s # 2000 days
    - max-password-reset-age:28800 s # 8 hours
    - password-history-count:5
    - require-secure-password-changes:true
  jmx:
    - default-password-storage-scheme:Salted SHA-512
    - expire-passwords-without-warning:false
    - force-change-on-add:false
    - force-change-on-reset:false
    - grace-login-count:10
    - idle-lockout-interval:172800000 s # 2000 days
    - lockout-duration:480 s
    - lockout-failure-expiration-interval:600 s
    - lockout-failure-count:5
    - max-password-age:172800000 s # 2000 days
    - max-password-reset-age:28800 s # 8 hours
    - password-history-count:5
    - password-history-duration:0 s
  test-gebruikers:
    - default-password-storage-scheme:Salted SHA-512
    - allow-user-password-changes:true
    - expire-passwords-without-warning:false
    - password-expiration-warning-interval:432000 s # 5 days
    - force-change-on-add:false
    - force-change-on-reset:false
    - grace-login-count:0
    - idle-lockout-interval:0 s
    - lockout-duration:0 s
    - lockout-failure-expiration-interval:0 s
    - lockout-failure-count:0
    - max-password-age:0 s
    - max-password-reset-age:0 s
    - min-password-age:0 s
    - password-attribute:userPassword
    - password-change-requires-current-password:false
    - password-history-count:0
    - password-history-duration:0 s
    - require-secure-authentication:false
    - require-secure-password-changes:false

ds_config_enabled: true

ds_config:
  ldaps:
    - method: set-connection-handler-prop
      handler-name: LDAPS
      add: ssl-cert-nickname:config-server-cert
    - method: set-connection-handler-prop
      handler-name: LDAP
      set: enabled:true
    - method: set-connection-handler-prop
      handler-name: LDAPS
      set: allow-ldap-v2:true
  global:
    - method: set-global-configuration-prop
      set: lookthrough-limit:20000
    - method: set-global-configuration-prop
      set: smtp-server:127.0.0.1:25
    - method: set-global-configuration-prop
      set: size-limit:10000
  log-publisher:
    - method: set-log-publisher-prop
      publisher-name: File-Based Access Logger
      set: enabled:false
    - method: set-log-publisher-prop
      publisher-name: File-Based Audit Logger
      set: enabled:false
    - method: set-log-publisher-prop
      publisher-name: File-Based Debug Logger
      set: enabled:false
    - method: set-log-publisher-prop
      publisher-name: File-Based Error Logger
      set: enabled:true
    - method: set-log-publisher-prop
      publisher-name: File-Based HTTP Access Logger
      set: enabled:false
    - method: set-log-publisher-prop
      publisher-name: Filtered Json File-Based Access Logger
      set: enabled:false
    - method: set-log-publisher-prop
      publisher-name: Json File-Based Access Logger
      set: enabled:true
    - method: set-log-publisher-prop
      publisher-name: Json File-Based HTTP Access Logger
      set: enabled:false
    - method: set-log-publisher-prop
      publisher-name: Replication Repair Logger
      set: enabled:true
  password-policies-create:
    - method: create-password-policy # default created on setup!?
      policy-name: "Default Password Policy"
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
    - method: create-password-policy
      policy-name: "Password Policy Service Accounts"
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
    - method: create-password-policy
      policy-name: "Password Policy JMX Service Accounts"
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
    - method:  create-password-policy
      policy-name: "Test gebruikers Password Policy"
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
  password-policies:
    - method: set-password-policy-prop
      policy-name: "Default Password Policy"
      set: "{{ siwunet_ds_config_pps['generic'] + siwunet_ds_config_pps['default'] }}"
      add:
        - password-validator:Length-Based Password Validator
        - password-validator:Similarity-Based Password Validator
        - password-validator:Attribute Value
        - password-validator:Unique Characters
        - password-validator:Character Set
    - method: set-password-policy-prop
      policy-name: "Default Password Policy" # TODO add to previous
      remove:
        - password-validator:At least 8 characters
        - password-validator:Common passwords
        - password-validator:Dictionary
        - password-validator:Repeated Characters
    - method: set-password-policy-prop
      policy-name: "Password Policy Service Accounts"
      set: "{{ siwunet_ds_config_pps['generic'] + siwunet_ds_config_pps['service-accounts'] }}"
    - method: set-password-policy-prop
      policy-name: "Password Policy JMX Service Accounts"
      set: "{{ siwunet_ds_config_pps['generic'] + siwunet_ds_config_pps['jmx'] }}"
    - method: set-password-policy-prop
      policy-name: "Test gebruikers Password Policy"
      set: "{{ siwunet_ds_config_pps['test-gebruikers'] }}"
  password-policy-skip-admin-validation: # note: this resources are always "changed"
    # get-password-policy-prop does not work in 6.5
    - method: set-password-policy-prop
      policy-name: "Default Password Policy"
      set: skip-validation-for-administrators:true
      # changed_when: false # TODO
    - method: set-password-policy-prop
      policy-name: "Password Policy Service Accounts"
      set: skip-validation-for-administrators:true
    - method: set-password-policy-prop
      policy-name: "Password Policy JMX Service Accounts"
      set: skip-validation-for-administrators:true
    - method: set-password-policy-prop
      policy-name: "Test gebruikers Password Policy"
      set: skip-validation-for-administrators:true
  password-validator-props:
    - method: set-password-validator-prop
      validator-name: Length-Based Password Validator
      set:
        - enabled:true
        - min-password-length:8
        - max-password-length:0
    - method: set-password-validator-prop
      validator-name: Similarity-Based Password Validator
      set:
        - enabled:true
        - min-password-difference:3
    - method: set-password-validator-prop
      validator-name: Attribute Value
      set: enabled:true
      add:
        - match-attribute:cn
        - match-attribute:sn
        - match-attribute:givenName
        - match-attribute:uid
    - method: set-password-validator-prop
      validator-name: Unique Characters
      set:
        - enabled:true
        - min-unique-characters:4
        - case-sensitive-validation:true
    - method: set-password-validator-prop
      validator-name: Character Set
      set:
        - enabled:true
        - allow-unclassified-characters:true
  backend-create:
    - method: create-backend
      set:
        - base-dn:c=NL
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: siwuRoot
    - method: create-backend
      set:
        - base-dn:dc=iwkb,dc=nl
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: userRoot
  access-control-handler-properties:
    - method: set-access-control-handler-prop
      add:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2 || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18 || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\") (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
      comment: global-aci
  backend-index-create-siwuRoot: "{{ siwunet_backend_index_create }}"
  backend-index-create-userroot: "{{ siwunet_backend_index_create|c2platform.core.update_list_attibute('backend-name', 'userRoot')|list }}"
  uid-unique:
    - method: set-plugin-prop
      plugin-name: UID Unique Attribute
      set:
        - enabled:true
  replication-server:
    - method: set-replication-server-prop
      provider-name: Multimaster Synchronization
      set:
        - changelog-enabled:disabled

ds_config_components:
  - ldaps
  - global
  - log-publisher
  - password-policies-create
  - password-policies
  - password-policy-skip-admin-validation
  - password-validator-props
  - backend-create
  - access-control-handler-properties
  - backend-index-create-siwuRoot
  - backend-index-create-userroot
  - uid-unique

ds_config_components_replication:
  - replication-server
```


## Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)
* [DS 6 > Configuration Reference](https://backstage.forgerock.com/docs/ds/6/configref/index.html#preface) aka `dsconfig` command.
* [DS 6 > Reference | Replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1)
* [How do I verify that a DS 5.x, 6 or OpenDJ 3.x server is responding to LDAP requests without providing a password? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a54816700)
* [How do I rebuild indexes in DS (All versions)? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a46097400)
* [How do I verify indexes in DS (All versions) are correct? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a59282000)
* [Directory Services 7 > Tools Reference > ldapsearch — perform LDAP search operations](https://backstage.forgerock.com/docs/ds/7/tools-reference/ldapsearch-1.html)
