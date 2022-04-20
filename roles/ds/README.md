# Ansible Role ForgeRock Directory Services (DS)

This Ansible role can be used to install and configure [ForgeRock Directory Services](https://backstage.forgerock.com/docs/ds/6.5/install-guide/) components using the [Cross-Platform Zip](https://backstage.forgerock.com/docs/ds/6.5/install-guide/#install-files-zip). The role can download and setup DS.

Note: on default - without additional configuration - this role will only install DS as CLI utilities. To perform actual setup of DS you will have to configure `ds_setup_config` var. 

> Server distributions include command-line tools for installing, configuring, and managing servers. The tools make it possible to script all operations.

<!-- MarkdownTOC levels="2,3,4" autolink="true" -->

- [Requirements](#requirements)
  - [Java](#java)
- [Role Variables](#role-variables)
  - [ds_setup_config](#ds_setup_config)
  - [ds_db_schema_ldifs](#ds_db_schema_ldifs)
  - [ds_config](#ds_config)
    - [LDAPS certificate alias](#ldaps-certificate-alias)
  - [Backends](#backends)
  - [Attribute Uniqueness](#attribute-uniqueness)
  - [Global ACI](#global-aci)
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
- [Links](#links)
- [Notes](#notes)
  - [Idempotancy](#idempotancy)
  - [Upgrade](#upgrade)
  - [Backup / restore](#backup--restore)
  - [dsconfig add](#dsconfig-add)
  - [Global configuration](#global-configuration)
  - [Password validators](#password-validators)

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

Dict `ds_config` is used to configure DS using [dsconfig](https://backstage.forgerock.com/docs/ds/6.5/configref/) command. The remainder of this section contains examples of the use of this dict starting with a simple example. In the remainder of this section whenever `dsconfig` is referenced we are using an alias defined as follows.

```bash
alias dsconfig="/opt/ds/ds/bin/dsconfig --hostname localhost --port 10636 --bindDN \"cn=Directory Manager\" --bindPasswordFile /root/.dspassword --trustAll --no-prompt"
```

#### LDAPS certificate alias

Default certificate alias is `server-cert`. To change it to for example `config-server-cert` using property `ssl-cert-nickname`. This is a simple example of adding an property with value.

```yaml
ds_config:
  ldaps:
    - method: set-connection-handler-prop
      handler-name: LDAPS
      add: ssl-cert-nickname:config-server-cert
ds_config_components:
  - ldaps
```

Notes:

1. `ldaps` is just group name, `ds_config` dict groups lists of config. You can use any group name or grouping you want. 
2. Groups you want to enable need to be added to `ds_config_components`. This is just a simple lists of group names.

Below is the Ansible logging for this configuration. It shows that the dict is processed using a number of Ansible tasks. The key tasks are: **Get current config** and **Change config**. The first task checks the current state of DS and the second task changes DS if necessary.

Note also a number of "ds_config" tasks: **ds_config prepared**, **ds_config current** and **ds_config changes**. This role changes the dict `ds_config` which can you help you understand what Ansible / this role is doing. For your convience this changed dict is written to disk in task **Log ds_config → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps.yml**. Note: if you configure `ds_debug: true` the other log files will also be written to disk e.g. `ds_config_0_ldaps_0.yml`.

```
TASK [c2platform.forgerock.ds : include_tasks] *********************************
included: /home/ostraaten/git/vips-gitlab/bkwi-dev/ansible_collections/c2platform/forgerock/roles/ds/tasks/config_component.yml for bkd-ds

TASK [c2platform.forgerock.ds : Log ds_config prepared / 0 → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps_0.yml] ***
skipping: [bkd-ds]

TASK [c2platform.forgerock.ds : Prepare config ldaps] **************************
ok: [bkd-ds]

TASK [c2platform.forgerock.ds : ds_config prepared] ****************************
ok: [bkd-ds]

TASK [c2platform.forgerock.ds : Log ds_config prepared / 1  → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps_1.yml] ***
skipping: [bkd-ds]

TASK [c2platform.forgerock.ds : Get current config] ****************************
ok: [bkd-ds] => (item=0-ldaps-0 set-connection-handler-prop enabled: True)

TASK [c2platform.forgerock.ds : Prepare config ( add current )] ****************
ok: [bkd-ds]

TASK [c2platform.forgerock.ds : ds_config current] *****************************
ok: [bkd-ds]

TASK [c2platform.forgerock.ds : Log ds_config prepared / 2 → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps_2.yml] ***
skipping: [bkd-ds]

TASK [c2platform.forgerock.ds : Change config] *********************************
changed: [bkd-ds] => (item=0-ldaps-0 set-connection-handler-prop enabled: True)

TASK [c2platform.forgerock.ds : Prepare config ( add results )] ****************
ok: [bkd-ds]

TASK [c2platform.forgerock.ds : ds_config changes] *****************************
ok: [bkd-ds]

TASK [c2platform.forgerock.ds : Log ds_config changed / 3 → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps_3.yml] ***
skipping: [bkd-ds]

TASK [c2platform.forgerock.ds : Log ds_config → /opt/ds/ds-6.5.5/logs/ds_config_0_ldaps.yml] ***
ok: [bkd-ds]

PLAY RECAP *********************************************************************
bkd-ds                     : ok=79   changed=1    unreachable=0    failed=0    skipped=69   rescued=0    ignored=0   
```

Log file `ds_config_0_ldaps.yml` is below. Note how the dict `ds_config` has expanded. The list item now has 7 extra keys.

1. Key `change` contains the resuls the *current* vs *desired state* analysis. It is true and so DS was changed, which we can see in logging show above in tasks **Change config**. If we run our play again, `change` would be `false`.
2. key `cmd` contains the `dsconfig` command line. 
3. Key `enabled` is `true`. This is the default. You can use this key to turn specific steps / list items off.
4. key `get` is a dict with with information created to get *current state* of DS with regards to this property.
5. Key `stdout` contains output return by `dsconfig` when changing DS. In this case nothing was returned.
6. Key `step` is just the index of the list item in the group. Which is used for processing results of `dsconfig` commands.
7. Key `when`

```yaml
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


The above configuration will evaluate to `dsconfig` command:

```bash
dsconfig set-connection-handler-prop --handler-name LDAPS --add ssl-cert-nickname:config-server-cert
````


```bash
dsconfig get-connection-handler-prop --handler-name LDAPS --property ssl-cert-nickname
```

The dicts also contains a `when` key that is used to check the current value of the property.



ssl-cert-nickname                  : server-cert

See [ssl-cert-nickname](https://backstage.forgerock.com/docs/opendj/2.6/configref/ldap-connection-handler.html#ssl-cert-nickname)


### Backends

[DS backends](https://backstage.forgerock.com/docs/ds/7/config-guide/import-export.html) can be created using config shown below. This config will use [dsconfig create-backend](https://backstage.forgerock.com/docs/ds/7/config-guide/import-export.html#create-database-backend) to create the backend.

```yaml
ds_config:
  backend_create:
    - set:
        - base-dn:c=NL
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: appRoot
    - set:
        - base-dn:dc=example,dc=com
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: userRoot
```

### Attribute Uniqueness

TODO

[Attribute Uniqueness](https://backstage.forgerock.com/docs/ds/7/config-guide/attribute-uniqueness.html)


### Global ACI

[Directory Services 7 > Security Guide > Access Control](https://backstage.forgerock.com/docs/ds/7/security-guide/access.html)


  access-control-handler:
    - add:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)" 
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2 || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18 || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\") (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetattr!=\"userPassword||authPassword||changes||changeNumber||changeType||changeTime||targetDN||newRDN||newSuperior||deleteOldRDN||targetEntryUUID||targetUniqueID||changeInitiatorsName||changeLogCookie\")(version 3.0; acl \"Anonymous read access\"; allow (read,search,compare) userdn=\"ldap:///dc=iwkb,dc=nl\";)"


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

```yaml
---
- name: myapp_ds
  hosts: myapp_ds
  become: yes

  roles:
    - { role: c2platform.core.common,  tags: ["common"] }
    - { role: c2platform.core.java,    tags: ["java"] }
    - { role: c2platform.forgerock.ds, tags: ["forgerock","ds"] }
```

Example configuration that includes `ds_setup_config` for your `group_vars` or `host_vars` configuration, that will perform and configure a DS server.

```yaml
---
java_version: jdk11_0411_oj9

ds_version: 6.5.4
ds_versions:
  6.5.4:
    url: file:///vagrant/downloads/DS-6.5.4.zip
    checksum: "sha256: 820a197f4ac11b020c653ef00c684e63034df1f9f591b826ee4735c4bde7b8f1"

common_pip_packages_extra: ['python-ldap']

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

ds_config_backend_index_templates:
  uid_etc:
    backend-name: myappRoot
    set:
      - index-type:equality
      - index-entry-limit:4000
  cn_etc:
    backend-name: myappRoot
    set:
      - index-type:equality
      - index-type:substring
      - index-entry-limit:4000

# Password policy settings
ds_config_pps:
  generic:
    - default-password-storage-scheme:Salted SHA-512
    - password-attribute:userPassword
    - deprecated-password-storage-scheme:Salted SHA-1
    - last-login-time-attribute:ds-pwp-last-login-time
    - last-login-time-format:yyyyMMddHHmmss
    - password-expiration-warning-interval:7 days
    - min-password-age:24 hours
    - password-change-requires-current-password:true
    - password-history-duration:0 seconds
    - skip-validation-for-administrators:true
    - require-secure-authentication:true
  default:
    - allow-user-password-changes:true
    - expire-passwords-without-warning:true
    - grace-login-count:2
    - lockout-duration:0 minutes
    - lockout-failure-expiration-interval:0 minutes
    - lockout-failure-count:5
    - max-password-reset-age:14 days
    - password-history-count:10
    - require-secure-password-changes:true
    - max-password-age:56 days
    - force-change-on-add:true
    - force-change-on-reset:true
    - idle-lockout-interval:45 days
  service-accounts:
    - expire-passwords-without-warning:false
    - force-change-on-add:false
    - force-change-on-reset:false
    - grace-login-count:10
    - idle-lockout-interval:2000 days
    - lockout-duration:1 s
    - lockout-failure-expiration-interval:1 s
    - lockout-failure-count:10000
    - max-password-age:2000 days
    - max-password-reset-age:8 hours
    - password-history-count:5
    - require-secure-password-changes:true
  jmx:
    - default-password-storage-scheme:Salted SHA-512
    - expire-passwords-without-warning:false
    - force-change-on-add:false
    - force-change-on-reset:false
    - grace-login-count:10
    - idle-lockout-interval:2000 days
    - lockout-duration:480 s
    - lockout-failure-expiration-interval:600 s
    - lockout-failure-count:5
    - max-password-age:2000 days
    - max-password-reset-age:8 hours
    - password-history-count:5
    - password-history-duration:0 seconds

ds_config:
  connection-handler_set_cert: # note underscore → connection-handler component
    - handler-name: LDAPS
      add: ssl-cert-nickname:config-server-cert
  connection-handler:
    - handler-name: LDAP
      set: enabled:false
    - handler-name: LDAPS
      set: allow-ldap-v2:true
  global-configuration:
    - set: lookthrough-limit:20000
    - set: smtp-server:127.0.0.1:25
  log-publisher:
    - publisher-name: File-Based Access Logger
      set: enabled:false
  password-policy_create:
    - policy-name: Default Password Policy
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
      when:
        regex: '^(Default Password Policy)\s+:'
        method: list-password-policies
        match: no
        #switches:
        #  property: password-attribute
  password-policy:
    - policy-name: Default Password Policy
      set: "{{ ds_config_pps['generic'] + ds_config_pps['default'] }}"
      add:
        - password-validator:Length-Based Password Validator
        - password-validator:Similarity-Based Password Validator
        - password-validator:Attribute Value
        - password-validator:Unique Characters
        - password-validator:Character Set
  password-policy_remove:
    - policy-name: Default Password Policy
      remove: password-validator:At least 8 characters
      when:
        regex: '^password-validator\s:[\S\s.]*(\sAt least 8 characters)[\s,].*$'
        method: get-password-policy-prop
        match: yes
        switches:
           policy-name: Default Password Policy
           property: password-validator
    - policy-name: Default Password Policy
      remove: password-validator:Common passwords
      when:
        regex: '^password-validator\s:[\S\s.]*(\sCommon passwords)[\s,].*$'
        method: get-password-policy-prop
        match: yes
        switches:
           policy-name: Default Password Policy
           property: password-validator
    - policy-name: Default Password Policy
      remove: password-validator:Dictionary
      when:
        regex: '^password-validator\s:[\S\s.]*(\sDictionary)[\s,].*$'
        method: get-password-policy-prop
        match: yes
        switches:
           policy-name: Default Password Policy
           property: password-validator
    - policy-name: Default Password Policy
      remove: password-validator:Repeated Characters
      when:
        regex: '^password-validator\s:[\S\s.]*(\sRepeated Characters)[\s,].*$'
        method: get-password-policy-prop
        match: yes
        switches:
           policy-name: Default Password Policy
           property: password-validator
  password-policy_service-accounts-create:
    - policy-name: Password Policy Service Accounts
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
  password-policy_service-accounts:
    - policy-name: Password Policy Service Accounts
      set: "{{ ds_config_pps['generic'] + ds_config_pps['service-accounts'] }}"
  password-policy_service-accounts-jmx-create:
    - policy-name: Password Policy JMX Service Accounts
      type: password-policy
      set:
        - default-password-storage-scheme:Salted SHA-512
        - password-attribute:userPassword
  password-policy_service-accounts-jmx:
    - policy-name: Password Policy JMX Service Accounts
      set: "{{ ds_config_pps['generic'] + ds_config_pps['jmx'] }}"
  password-validator:
    - validator-name: '"Length-Based Password Validator"'
      set:
        - enabled:true
        - min-password-length:8
        - max-password-length:0
    - validator-name: '"Similarity-Based Password Validator"'
      set:
        - enabled:true
        - min-password-difference:3
    - validator-name: '"Attribute Value"'
      set: enabled:true
      add:
        - match-attribute:cn
        - match-attribute:sn
        - match-attribute:givenName
        - match-attribute:uid
    - validator-name: '"Unique Characters"'
      set:
        - enabled:true
        - min-unique-characters:4
        - case-sensitive-validation:true
    - validator-name: '"Character Set"'
      set:
        - enabled:true
        - allow-unclassified-characters:true
  backend_create:
    - set:
        - base-dn:c=NL
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: myappRoot
    - set:
        - base-dn:dc=myapporg,dc=nl
        - enabled:true
        - db-cache-percent:5
      type: je
      backend-name: userRoot
  access-control-handler:
    - add:
        - global-aci:"(targetcontrol=\"2.16.840.1.113730.3.4.18\") (version 3.0; acl \"Authenticated users control access\"; allow(read) userdn=\"ldap:///all\";)" 
        - global-aci:"(targetcontrol=\"1.3.6.1.1.12 || 1.3.6.1.1.13.1 || 1.3.6.1.1.13.2 || 1.2.840.113556.1.4.319 || 1.2.826.0.1.3344810.2.3 || 2.16.840.1.113730.3.4.18 || 2.16.840.1.113730.3.4.9 || 1.2.840.113556.1.4.473 || 1.3.6.1.4.1.42.2.27.9.5.9\") (version 3.0; acl \"and the rest\"; allow(read) userdn=\"ldap:///all\";)"
        - global-aci:"(targetattr!=\"userPassword||authPassword||changes||changeNumber||changeType||changeTime||targetDN||newRDN||newSuperior||deleteOldRDN||targetEntryUUID||targetUniqueID||changeInitiatorsName||changeLogCookie\")(version 3.0; acl \"Anonymous read access\"; allow (read,search,compare) userdn=\"ldap:///dc=myapporg,dc=nl\";)"
  backend-index_create:
    - "{{ ds_config_backend_index_templates['uid_etc']|combine({ 'index-name': 'uid' }) }}"
    - "{{ ds_config_backend_index_templates['uid_etc']|combine({ 'index-name':'member' }) }}"
    - "{{ ds_config_backend_index_templates['uid_etc']|combine({ 'index-name':'uniqueMember' }) }}"
    - "{{ ds_config_backend_index_templates['uid_etc']|combine({ 'index-name':'ou' }) }}"
    - "{{ ds_config_backend_index_templates['cn_etc']|combine({ 'index-name':'cn' }) }}"
    - "{{ ds_config_backend_index_templates['cn_etc']|combine({ 'index-name':'givenName' }) }}"
    - "{{ ds_config_backend_index_templates['cn_etc']|combine({ 'index-name':'sn' }) }}"
    - "{{ ds_config_backend_index_templates['cn_etc']|combine({ 'index-name':'mail' }) }}"
    - set:
        - index-type:equality
        - index-type:substring
        - index-entry-limit:100000
      backend-name: myappRoot
      index-name: businessCategory
#  password-validator_add:
#    - validator-name: '"Attribute Value"'
#      set: enabled:true
#      add:
#        - match-attribute:cn
#        - match-attribute:sn
#        - match-attribute:givenName
#        - match-attribute:uid
#      #remove:
#      #  - match-attribute:sn

ds_config_components:
  - connection-handler
  - global-configuration
  - log-publisher
  - password-policy_create
  - password-policy
  - password-policy_service-accounts-create
  - password-policy_service-accounts
  - password-policy_service-accounts-jmx-create
  - password-policy_service-accounts-jmx
  - password-validator
  - password-policy_remove
  - backend_create
  - backend-index_create
  - access-control-handler
  #- password-validator_add

# Components that require use of a fingerpint to detect
# changes between current and desired state
ds_config_components_fingerprint:
  - connection-handler
  #- password-validator_add
  #- password-policy_create
  - password-policy
  - password-policy_service-accounts-create
  - password-policy_service-accounts
  - password-policy_service-accounts-jmx-create
  - password-policy_service-accounts-jmx
  - backend_create
  - backend-index_create
  - access-control-handler

ds_db_schema_ldifs: # default disabled via ds_db_schema_ldifs_enable: no
  myappPerson: | # db/schema/myappPerson.ldif to create myappPerson object class
    dn: cn=schema
    changetype: modify
    add: attributeTypes
    attributeTypes: ( myapp-account-expiration-time-oid NAME 'myapp-account-expiration-time' DESC 'The time the account becomes disabled' EQUALITY generalizedTimeMatch ORDERING generalizedTimeOrderingMatch SUBSTR caseIgnoreSubstringsMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.24 SINGLE-VALUE USAGE userApplications )
    dn: cn=schema
    changetype: modify
    add: objectClasses
    objectClasses: ( myappPerson-oid NAME 'myappPerson' DESC 'Extra properties for a myapp user' SUP top AUXILIARY MAY ( myapp-account-expiration-time ) )
ds_modify:
  - name: userstore.myappRoot
    ldif: |
      dn: c=NL
      objectClass: country
      objectClass: top
      c: NL
  - name: userstore.userRoot
    ldif: |
      dn: dc=myapporg,dc=nl
      objectClass: domain
      objectClass: top
      dc: myapporg
  - name: organization.special
    ldif: |
      dn: o=special,c=NL
      objectClass: organization
      objectClass: top
      o: special
  - name: organization.myapp
    ldif: |
      dn: o=myapp,c=NL
      objectClass: organization
      objectClass: top
      o: myapp
  - name: special.sa_reports
    ldif: |
      dn: cn=sa_reports,o=special,c=NL
      objectClass: person
      objectClass: inetOrgPerson
      objectClass: organizationalPerson
      objectClass: top
      sn: Reports
      cn: sa_reports
      givenName: Service Account
      uid: sa_reports
      ds-pwp-password-policy-dn: cn=Password Policy Service Accounts,cn=Password Policies,cn=config
      ds-rlim-lookthrough-limit: 100000
      ds-pwp-last-login-time: 20200903105229
      ds-privilege-name: unindexed-search
      ds-rlim-time-limit: 300
      ds-rlim-size-limit: 10000
  - name: special.sa_monitor
    ldif: |
      dn: cn=sa_monitor,o=special,c=NL
      objectClass: person
      objectClass: inetOrgPerson
      objectClass: organizationalPerson
      objectClass: top
      sn: Myapp JMX monitoring account
      cn: sa_monitor
      givenName: Service Account
      uid: sa_monitor
      ds-pwp-password-policy-dn: cn=Password Policy JMX Service Accounts,cn=Password Policies,cn=config
      ds-rlim-lookthrough-limit: 100000
      ds-pwp-last-login-time: 20200903105938
      ds-privilege-name: jmx-read
      ds-rlim-size-limit:  1000
  - name: special.sa_useradmin
    ldif: |
      dn: cn=sa_useradmin,o=special,c=NL
      objectClass: person
      objectClass: inetOrgPerson
      objectClass: organizationalPerson
      objectClass: top
      sn: Myapp User Administrator
      cn: sa_useradmin
      givenName: Service Account
      uid: sa_useradmin
      ds-pwp-password-policy-dn: cn=Password Policy Service Accounts,cn=Password Policies,cn=config
      ds-rlim-lookthrough-limit: 100000
      ds-pwp-last-login-time: 20200829000000
      ds-privilege-name: proxied-auth
      ds-privilege-name: subentry-write
      ds-privilege-name: password-reset
      ds-privilege-name: modify-acl
      ds-privilege-name: unindexed-search
      ds-rlim-size-limit: 100000
  - name: passwordpolicy.am_config
    ldif: |
      dn: uid=am-config,ou=admins,ou=am-config
      changetype: modify
      replace: ds-pwp-password-policy-dn
      ds-pwp-password-policy-dn: cn=Root Password Policy,cn=Password Policies,cn=config
    search: "&(objectclass=top)(uid=am-config)(ds-pwp-password-policy-dn=cn=Root Password Policy,cn=Password Policies,cn=config)"
  - name: add-ACI-to-cNL
    ldif: |
      dn: c=NL
      changetype: modify
      add: aci
      aci: (target="ldap:///o=myapp,c=nl")(targetattr ="*")(version 3.0; acl "Allow apps proxied auth"; allow(all, proxy)(userdn = "ldap:///cn=sa_useradmin,o=special,c=nl");)
      aci: (target="ldap:///o=myapp,c=nl")(targetcontrol = "1.3.6.1.4.1.42.2.27.9.5.8")(targetattr ="*")(version 3.0; acl "Allow apps proxy auth"; allow(all)(userdn =  "ldap:///cn=sa_useradmin,o=special,c=nl");)
      aci: (target="ldap:///o=myapp,c=nl")(version 3.0; acl "Delegated import and export rights"; allow (import,export) (userdn = "ldap:///cn=sa_useradmin,o=special,c=nl");)
      aci: (extop="1.3.6.1.4.1.4203.1.11.1 || 1.3.6.1.4.1.26027.1.6.1")(version 3.0; acl "Password modify and policy extended operation"; allow (read)(userdn = "ldap:///cn=sa_useradmin,o=special,c=nl");)
      aci: (target="ldap:///o=myappdesk,c=nl")(targetattr ="* || +")(version 3.0; acl "Allow auth"; allow(add,delete,write,read,search,compare)(userdn = "ldap:///o=myappdesk,c=nl??sub?(uid=a_*)");)
      aci: (target="ldap:///o=myapp,c=nl")(targetattr ="* || +")(version 3.0; acl "Allow auth"; allow(add,delete,write,read,search,compare)(userdn = "ldap:///o=myappdesk,c=nl??sub?(uid=a_*)");)
      aci: (target="ldap:///o=myapp,c=nl")(targetattr="aci||ds-pwp-account-disabled")(version 3.0; acl "Delegated write and delete rights"; allow (delete,write,read,search,compare)(userdn = "ldap:///cn=sa_useradmin,o=special,c=nl");)
      aci: (targetattr="objectclass||cn||sn||givenName||initials||mail||telephoneNumber||facsimileTelephoneNumber||businessCategory||myapp-account-expiration-time||userPassword||authPassword||isMemberOf")(version 3.0; acl "Self entry read"; allow (read,search,compare) userdn="ldap:///self";)
      aci: (targetattr="sn||givenName||initials||mail||telephoneNumber||facsimileTelephoneNumber")(version 3.0; acl "Self entry update"; allow (delete,write) userdn="ldap:///self";)
      aci: (targetattr="objectClass||businessCategory||myapp-account-expiration-time||ou||cn||employeeNumber||telephoneNumber||facsimileTelephoneNumber||givenName||initials||mail||sn||uid||isMemberOf||ds-pwp-account-disabled||ds-pwp-last-login-time||ds-pwp-password-expiration-time||ds-pwp-warned-time||pwdAccountLockedTime||pwdChangedTime||pwdFailureTime||pwdReset")(version 3.0; acl "Report user read rights"; allow (read,search,compare)(userdn = "ldap:///cn=sa_reports,o=special,c=nl");)
      aci: (target="ldap:///o=myapp,c=nl")(targetcontrol = "1.3.6.1.4.1.42.2.27.9.5.8")(targetattr ="*")(version 3.0; acl "Report user account status rights"; allow(all) userdn = "ldap:///cn=sa_reports,o=special,c=nl";)
      aci: (target="ldap:///o=myapp,c=nl")(targetcontrol = "1.3.6.1.4.1.42.2.27.9.5.8")(targetattr ="*")(version 3.0; acl "Self account status rights"; allow (read) userdn="ldap:///self";)
      aci: (target="ldap:///o=myapp,c=nl")(targetcontrol = "1.3.6.1.4.1.42.2.27.9.5.8")(targetattr ="*")(version 3.0; acl "Account usability"; allow(all)(userdn = "ldap:///all");)
    search: "&(objectclass=top)(c=NL)(aci=*)"
  - name: 11-add-self-manage-settings
    ldif: |
      dn: c=NL
      changetype: modify
      add: aci
      aci: (targetattr = "objectclass || inetuserstatus || iplanet-am-user-login-status || iplanet-am-user-account-life || iplanet-am-session-quota-limit || iplanet-am-user-alias-list ||  iplanet-am-session-max-session-time || iplanet-am-session-max-idle-time || iplanet-am-session-get-valid-sessions || iplanet-am-session-destroy-sessions || iplanet-am-user-admin-start-dn || iplanet-am-auth-post-login-process-class || iplanet-am-user-federation-info || iplanet-am-user-federation-info-key || ds-pwp-account-disabled || sun-fm-saml2-nameid-info || sun-fm-saml2-nameid-infokey || sunAMAuthInvalidAttemptsData || memberof || member || kbaInfoAttempts")(version 3.0; acl "OpenAM User self modification denied for these attributes"; deny (write) userdn ="ldap:///self";)
      aci: (targetcontrol="1.3.6.1.4.1.42.2.27.8.5.1 || 1.3.6.1.4.1.36733.2.1.5.1") (version 3.0; acl "Allow anonymous access to behera draft and transaction control"; allow(read) userdn="ldap:///anyone";)
      aci: (targetattr="userPassword") (version 3.0; acl "Allow password change"; allow (write) userdn="ldap:///self";)
    search: "&(objectclass=top)(c=NL)(aci=*Allow password change*)"
  - name: 15-add-aci-for-sa_useradmin
    ldif: |
      dn: cn=sa_useradmin,o=special,c=NL
      changetype: modify
      add: aci
      aci: (targetcontrol="2.16.840.1.113730.3.4.18")
        (version 3.0; acl "Apps can use the Proxy Authorization Control";
        allow(read) userdn="ldap:///cn=sa_useradmin,o=special,c=NL";)
    search: "&(objectclass=top)(uid=sa_useradmin)(aci=*)"
  - name: 16-delete-password-reset-from-sa_useradmin
    ldif: |
      dn: cn=sa_useradmin,o=special,c=NL
      changetype: modify
      delete: ds-privilege-name
      ds-privilege-name: password-reset
    search: "&(objectclass=top)(uid=sa_useradmin)(!(ds-privilege-name=password-reset))"

ds_import: # default disabled - ds_import_enable: no
  - name: export
    ldif-url: file:///vagrant/downloads/export.ldif
    properties:
      backendId: myappRoot
      skipFile: /tmp/export-skipped.ldif
      rejectFile: /tmp/export-reject.ldif
      no-prompt: ''
      offline: ''
      # excludeFilter
    sed:
      - 's/dn: c=nl/dn: c=NL/g'
      - 's/c: nl/c: NL/g'
# see secrets.yml for passwords - passwords are default 'secret'
#ds_passwords:
# see also secrets.yml
#    sa_reports:
#      authzId: cn=sa_reports,o=special,c=NL
#      newPassword: supersecure
#    sa_monitor:
#      authzId: cn=sa_monitor,o=special,c=NL
#      newPassword: supersecure
#    sa_useradmin:
#      authzId: cn=sa_useradmin,o=special,c=NL
#      newPassword: supersecure

ds_git_repos:
  scripts:
    repo: "{{ myapp_ds_scripts_repo }}" # vault
    dest: "{{ ds_home_link }}/scripts"

ds_scripts_connect:
  hostname: "{{ ds_connect['hostname'] }}"
  port: "{{ ds_connect['port'] }}"
  bindDN:  "{{ ds_connect['bindDN'] }}"
  bindPassword: "{{ ds_connect['bindPassword'] }}"
  baseDn: c=NL

ds_scripts:
  password-reset_subentry-write:
    # Note: this script does not filter currently on cn=Administrators
    # which is currently not a problem because there are not other groups
    # than groups with cn=Administrators
    shell: |
      # python3 -c 'import sys; print(sys.stdout.encoding)'
      python3 migrate-admin-aci.py {{ ds_scripts_connect|c2platform.forgerock.ds_cmd }}
    chdir: "{{ ds_home_version }}/scripts/ds"
  migrate-myapp-expiry:
    shell: |
      python3 migrate-myapp-expiry.py {{ ds_scripts_connect|c2platform.forgerock.ds_cmd }}
    chdir: "{{ ds_home_version }}/scripts/ds"

#  ds_attributes:
#  password-reset_subentry-write:
#    filter: (objectclass=groupOfUniqueNames)
#    attributes:
#      - name: aci
#        value: >
#          (target="ldap:///{dn-parent}")(targetattr="ds-pwp-account-expiration-time")
#          (version 3.0; acl "Delegated expiration rights"; allow (write,delete) groupdn="ldap:///dn"; )
#        target: parent # default self
#    members:
#      - name: uniqueMember
#        attributes:
#          - name: ds-privilege-name
#            values: ['password-reset', 'subentry-write']
#
```


## Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)
* [DS 6 > Configuration Reference](https://backstage.forgerock.com/docs/ds/6/configref/index.html#preface) aka `dsconfig` command.
* Note that the -- commandline options given in the Forgerock website, as mentioned above, at times are buggy. The leading source for the proper ones is the help screen (dsconfig --help).
* [DS 6 > Reference | Replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1)
* [How do I verify that a DS 5.x, 6 or OpenDJ 3.x server is responding to LDAP requests without providing a password? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a54816700)
* [How do I rebuild indexes in DS (All versions)? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a46097400)
* [How do I verify indexes in DS (All versions) are correct? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a59282000)
* [Directory Services 7 > Tools Reference > ldapsearch — perform LDAP search operations](https://backstage.forgerock.com/docs/ds/7/tools-reference/ldapsearch-1.html)

## Notes

### Idempotancy

The bulk of DS configuration is done using the `dsconfig` command which poses some challenges 
when it comes to implementing idempotancy. Currently only a few "components" support checking
"current" configuration. This can be seen in `ds_cmd_get` filter which shows that the following
components support a current check:

* global-configuration
* password-validator
* log-publisher
* plugin
* replication-server

Other components you configure using `ds_config` dict will fail with message like

> No get command defined for component <name>. Use a fingerprint!?

You can fix this by adding the component name to list `ds_config_components_fingerprint`. For this
component then a fingerprint file will be used that is stored in folder `/opt/ds/.fingerprint/6.5.4`.
The `dsconfig` command will then only run if the fingerprint file changes. See example below.

```bash
root:~# ls /opt/ds/.fingerprint/6.5.5/
access-control-handler         password-policy
backend_create                 password-policy_service-accounts
backend-index_suwiroot-create  password-policy_service-accounts-create
backend-index_userroot-create  password-policy_service-accounts-jmx
connection-handler             password-policy_service-accounts-jmx-create
ds_passwords                   plugin
root:~# 
```
If the fingerprint files are lost provision will fail for each component configured. Using `ds_config_ignore_errors`
you can temporarily ignore errors so that the fingerprint files are created. Of course, then you should review the
errors to make sure all are the result of this and not some other issue.

### Upgrade

### Backup / restore

### dsconfig add

`add` configuration is currently not checked for changes, only `set`. Combine with fingerprint for complete component configuration? I.e. run complete component configuration if 1) fingerprint changes or 2) property changes

```yaml
    - validator-name: '"Attribute Value"'
      set: enabled:true
      add:
        - match-attribute:cn
        - match-attribute:sn
        - match-attribute:givenName
        - match-attribute:uid
```

```bash
forgerock@bkd-ds:~/ds-6.5.4/bin$ ./dsconfig get-password-validator-prop --hostname 1.1.1.51.nip.io --port 4444 --bindDN "cn=Directory Manager" --bindPassword supersecret --trustAll --no-prompt --validator-name "Attribute Value"
Property               : Value(s)
-----------------------:--------------------------------------------------
check-substrings       : true
enabled                : true
match-attribute        : All attributes in the user entry will be checked.
min-substring-length   : 5
test-reversed-password : true
```

### Global configuration

Global configuration such as `lookthrough-limit`, `smtp-server` can be configured as shown below

```yaml
ds_config:
  set-global-configuration-prop:
    - set: lookthrough-limit:20000
    - set: smtp-server:127.0.0.1:25
```

This will execute commands similar to

```bash
./dsconfig set-global-configuration-prop  \
--hostname 1.1.1.51.nip.io --port 4444 --bindDN "cn=Directory Manager" \
--bindPassword supersecure   --trustAll  --no-prompt   \
--set lookthrough-limit:20000
```

Using `get-global-configuration-prop` we can check current value

```bash
./dsconfig get-global-configuration-prop  \
--hostname 1.1.1.51.nip.io --port 4444 --bindDN "cn=Directory Manager" \
--bindPassword supersecure   --trustAll  --no-prompt   \
--property lookthrough-limit
```

### Password validators

To configure password validators for example

```yaml
ds_config:
  set-password-validator-prop:
    - validator-name: '"Length-Based Password Validator"'
      set:
        - enabled:true
        - min-password-length:8
        - max-password-length:0
```

```bash
./dsconfig set-password-validator-prop  --hostname 1.1.1.51.nip.io --port 4444 --bindDN "cn=Directory Manager" --bindPassword supersecure   --trustAll  --no-prompt   --validator-name "Length-Based Password Validator" --set enabled:true --set min-password-length:8 --set max-password-length:0
```

```bash
./dsconfig get-password-validator-prop  --hostname 1.1.1.51.nip.io --port 4444 --bindDN "cn=Directory Manager" --bindPassword supersecure   --trustAll  --no-prompt   --validator-name "Length-Based Password Validator"
```

```bash
forgerock@bkd-ds:~/ds-6.5.4/bin$ ./dsconfig get-password-validator-prop  --hostname 1.1.1.51.nip.io --port 4444 --bindDN "cn=Directory Manager" --bindPassword supersecure   --trustAll  --no-prompt   --validator-name "Length-Based Password Validator"
Property            : Value(s)
--------------------:---------
enabled             : true
max-password-length : 0
min-password-length : 8
```
