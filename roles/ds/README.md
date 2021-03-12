# Ansible Role ForgeRock Directory Services (DS)

This Ansible role is used to install and configure upgrade [ForgeRock Directory Services](https://backstage.forgerock.com/docs/ds/6.5/install-guide/) components using the [Cross-Platform Zip](https://backstage.forgerock.com/docs/ds/6.5/install-guide/#install-files-zip). The role will download and setup DS. Furthermore the role can be used to configure DS using `dsconfig`, create user stores, users and configure replication.

<!-- MarkdownTOC levels="2,3" autolink="true" -->

- [Requirements](#requirements)
  - [Java](#java)
- [Role Variables](#role-variables)
  - [Setup config](#setup-config)
  - [Backends](#backends)
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
  - [Replication](#replication-1)
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
Note that the main dsconfig part(4.)  is highly parametrised, you could call it 'normalised' in SQL terms with no copypasting of elements. Parts 5 and 6 are not parametrised and hence have quite some copypasting. For the tiny bit of dsconfig usage there it would not be too hard to piggyback this on the parametrised framework. For the rest of the code (nontrivial, but still a lot shorter than dsconfig used to be) parametrising is for sure doable but the return-on-investment is debatable. One reason is that we talk not about 1 'shelled' command but three different, each with slightly different syntax; ldapsearch, ldapmodify and ldappasswordmodify.

The host_vars variable dsrepl_is_config_master defines whether this is a clustered environment and if so which is the 'master' (the machine where dsreplication command will be run). If that variable is set to NO on the sole node of a non-clustered environment, replication won't be installed.

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

### Replication

To create a two node cluster with [replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1) you can add `ds_replication` var similar to shown below:

```yaml
ds_replication: 
```
Note: default off course ds_replication 

For installing a cluster, mind the sequence:
1. First install the node which is NOT the config master. In DEV we call this DS2.
2. Then install the config master. It is this one that will have the step to configure the replication process, for both nodes. It also before configuring replication, does a check (ldapsearch) on whether the not-config-master node is up and running.


## Dependencies

<!--A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.-->

## Example Playbook

## Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)
* [DS 6 > Configuration Reference](https://backstage.forgerock.com/docs/ds/6/configref/index.html#preface) aka `dsconfig` command.
* Note that the -- commandline options given in the Forgerock website, as mentioned above, at times are buggy. The leading source for the proper ones is the help screen (dsconfig --help).
* [DS 6 > Reference | Replication](https://backstage.forgerock.com/docs/ds/6/reference/index.html#dsreplication-1)

## Notes

### Systemd services changed
A service added: ds-config. It is a 2-layer wrapper around /bin/start-ds and stop-ds scripts. See the URL given on why this is needed.

### Fingerprint

If in some testing situation it is needed to make changes in DS, e.g. using dsconfig but also commands like ldapmodify, manually (outside Ansible), beware that the next Ansible run could not work as intended due to it relying on now outdated fingerprints.
The solution if you really needed to make manual changes in DS: manually remove the related fingerprint file, or simply all fingerprints, in /opt/ds/.fingerprint/6.5.4 directory. It causes Ansible to run a bit slower than it should, but it guarantees that it works as intended even in this 'manual' scenario.

### DS service checks

There are limited checks in the role, e.g. to see whether the DS service was already installed and configured. However more checks could be helpful,
this also makes the chance less that in AM and IG rollout errors are found related to mistakes in the DS install/config.

### Upgrade

### Backup / restore

### Replication

```bash
./dsreplication status --adminUID admin --adminPassword --hostname 1.1.1.51.nip.io --port 4444 --trustAll --no-prompt
```

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
