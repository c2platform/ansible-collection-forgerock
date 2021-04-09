# Ansible Role ForgeRock Directory Services (DS)

This Ansible role is used to install and configure upgrade [ForgeRock Directory Services](https://backstage.forgerock.com/docs/ds/6.5/install-guide/) components using the [Cross-Platform Zip](https://backstage.forgerock.com/docs/ds/6.5/install-guide/#install-files-zip). The role will download and setup DS. Furthermore the role can be used to configure DS using `dsconfig`, create user stores, users and configure replication.

<!-- MarkdownTOC levels="2,3" autolink="true" -->

- [Requirements](#requirements)
  - [Java](#java)
- [Role Variables](#role-variables)
  - [Setup config](#setup-config)
  - [DB Schema ldifs](#db-schema-ldifs)
  - [Backends](#backends)
  - [Modify](#modify)
  - [Passwords](#passwords)
  - [Import](#import)
  - [Replication](#replication)
- [Dependencies](#dependencies)
- [Example Playbook](#example-playbook)
- [Links](#links)
- [Notes](#notes)
  - [Systemd services changed](#systemd-services-changed)
  - [Fingerprint](#fingerprint)
  - [DS service checks](#ds-service-checks)
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

ForgeRock DS requires Java to be installed. `java_home` directory, expose java_home set to Yes.

## Role Variables

<!--A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.-->

### Setup config

ds_setup_config

`ds_config`
Note that the configbase module (running dsconfig command) for some parts uses 'fingerprints': signatures of the last result stored on disk, to prevent unnecessary calls to dsconfig. This however assumes that Ansible is in full control of the file system.

TODO if needed
Note that the main dsconfig part(4.)  is highly parametrised, you could call it 'normalised' in SQL terms with no copypasting of elements. Parts 5 and 6 are not parametrised, except a small dsconfig part, and hence have quite some copypasting. For the code (nontrivial, but still a lot shorter than dsconfig used to be) parametrising is for sure doable but the return-on-investment is debatable. One reason is that we talk not about 1 'shelled' command but three different, each with slightly different syntax; ldapsearch, ldapmodify and ldappasswordmodify.

### DB Schema ldifs

Using `ds_db_schema_ldifs` ldifs files can be created in `db/schema`. For example configuration below will create file `/opt/ds/ds-6.5.4/db/schema/appPerson.ldif` to create a new __appPerson__ object class. 

```yaml
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

### Modify

Modify the directory using [LDIF](https://en.wikipedia.org/wiki/LDAP_Data_Interchange_Format) by using `ds_modify`. This holds an ordered list of ldif to be used to modify DS using `./ldapmodify`.

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

Note here the use of another variable `ds_modify_extra`. This variable works exactly the same as `ds_modify`. Anything you configure with this var will be applied to DS using `ldapmodify`.

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
```

### Replication

To create a two node cluster with [replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1) you can add `ds_replication` var similar to shown below:

```yaml
ds_replication_global_admin: admin
ds_replication_global_admin_password: supersecure
ds_replication_port: 8989

ds_replication: 
  replication-server:
    hostname: "1.1.1.51.nip.io"
    port: 4444
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
    - dc=bkwi,dc=nl
```

If one of the servers is unavailable, the setup will fail of course.

The possible settings under `replication-server`, `host1` and `host2` are mostly optional they will default to `ds_connect`. To setup replication at a minimum you need to configure:

```yaml
ds_replication: 
  replication-server:
    hostname: "1.1.1.51.nip.io"
  host2: 
    hostname: "1.1.1.58.nip.io"
  baseDNs:
    - ou=am-config
    - c=NL
    - dc=bkwi,dc=nl
```
Which implies that host 1 will also be the replication server with hostname `1.1.1.51.nip.io` etc.  

Configuration above will result in command being executed similar to 

```bash
./dsreplication configure  \
--host1 1.1.1.51.nip.io --port1 4444 --bindDn1 "cn=Directory Manager" \
--bindPassword1 supersecret --secureReplication1 --replicationPort1 8989 \
--host2 1.1.1.58.nip.io --port2 4444 --bindDn2 "cn=Directory Manager" \
--bindPassword2 supersecret --secureReplication2 --replicationPort2 8989 \
--baseDN dc=bkwi,dc=nl \
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

## Dependencies

<!--A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.-->

## Example Playbook

## Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)
* [DS 6 > Configuration Reference](https://backstage.forgerock.com/docs/ds/6/configref/index.html#preface) aka `dsconfig` command.
* Note that the -- commandline options given in the Forgerock website, as mentioned above, at times are buggy. The leading source for the proper ones is the help screen (dsconfig --help).
* [DS 6 > Reference | Replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1)
* [How do I verify that a DS 5.x, 6 or OpenDJ 3.x server is responding to LDAP requests without providing a password? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a54816700)


## Notes

### Systemd services changed
A service added: ds-config. It is a wrapper around /bin/start-ds and stop-ds scripts. See the URL given on why this is needed.

### Fingerprint

If in some testing situation it is needed to make changes in DS, e.g. using dsconfig but also commands like ldapmodify, manually (outside Ansible), beware that the next Ansible run could not work as intended due to it relying on now outdated fingerprints.
The solution if you really needed to make manual changes in DS: manually remove the related fingerprint file, or simply all fingerprints, in /opt/ds/.fingerprint/6.5.4 directory. It causes Ansible to run a bit slower than it should, but it guarantees that it works as intended even in this 'manual' scenario.

### DS service checks

There are limited checks in the role, e.g. to see whether the DS service was already installed and configured. However more checks could be helpful,
this also makes the chance less that in AM and IG rollout errors are found related to mistakes in the DS install/config.

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
