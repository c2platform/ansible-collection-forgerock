# Ansible Role ForgeRock Access Management (AM)

This Ansible role is used to setup and configure [AM](https://go.forgerock.com/Access-Management.html) usig [Amster](https://backstage.forgerock.com/docs/amster/6.5/user-guide/).

<!-- MarkdownTOC levels="2,3,4" autolink="true" -->

- [Requirements](#requirements)
- [Role description](#role-description)
- [Role Variables](#role-variables)
  - [Installation](#installation)
  - [Configure](#configure)
    - [108-set-sessionproperties](#108-set-sessionproperties)
    - [500-debug-logging](#500-debug-logging)
  - [Configure JSON](#configure-json)
  - [Configure raw](#configure-raw)
  - [Certificate](#certificate)
  - [Git](#git)
    - [Files](#files)
    - [Folders](#folders)
  - [Keystore](#keystore)
  - [Manual mode](#manual-mode)
- [Dependencies](#dependencies)
- [Links](#links)

<!-- /MarkdownTOC -->

## Requirements

ForgeRock uses zip files mostly - not tarballs, so to use this role `unzip` is required on target nodes.

Note that the 'Amster' utility part of the AM install connects with a ForgeRock DS server and expects a proxied AM adsress.
Hence requirement is that the configured DS server and IG proxy server already are up and running. In a 2-server setup as is now the standard, provisioning of the DS node goes first. The role does a check whether the DS instance is up and running, using the ldapsearch utility which checks on DS content level.

Designed 'patterns' are initial install (clean DS and clean AM) and running the play several times in case something changes, e.g. an Amster file other than 100-install. If however the 100-install changes, make sure both DS and AM get a full clean install; as otherwise the configuration in DS used by AM is not guaranteed as you want it to be. Note that there is no tight coupling between AM and Amster running on the same machine; though we never tested it a pattern with separate servers for AM and Amster could work. However as the usage scenarios are radically different, AM has the production load and Amster is solely for provisioning, the current co-hosting seems to work fine.

## Role description

1. Download and unpack Amster tool
2. Run the Amster tool, calling the associated DS server (which solely has the 'config' instance, used for configuration and users)

Note that due to the content of the (Groovy) .amster scripts, functional errors can appear during execution. Just like in the old Chef system these aren't trapped or analysed, it's up to the operators to watch these. In a user story for future extension trapping of functional errors is considered. Also for this reason debug statements (to give the outcome of all Amster commands on the screen and hence also in the AWX logfile) are kept in the Ansible code.

# Filesystem before and after situation
Before: no opt/amster and anything below it. No /opt/tomcat/am.

After situation for Amster:
/opt/amster/amster-[version] has the tool.
/opt/tomcat/am/openamcfg is created after a succesful run of Amster 
And amster tool makes a lot of changes in how AM works; probably most of them are stored in the associated DS server.


## Role Variables

### Installation

Use `amster_am_install` var to control installation

```yaml
amster_am_install:
  serverUrl: TODO
  adminPwd: "{{ amster_amadmin_pw }}"
  acceptLicense: ''
  pwdEncKey: "{{ amster_encryptpw }}"
  cfgStoreDirMgr: 'uid=am-config,ou=admins,ou=am-config'
  cfgStoreDirMgrPwd: '{{ amster_ds_rootpw }}'
  cfgStore: dirServer
  cfgStoreHost: "{{ amster_ds_hostname }}"
  cfgStoreAdminPort: 4444
  cfgStoreSsl: SSL
  cfgStorePort: 10636
  cfgStoreRootSuffix: ou=am-config
  cookieDomain: TODO
  cfgDir: /opt/tomcat/am # default $HOME/openam
  userStoreDirMgr: "cn=Directory Manager"
  userStoreDirMgrPwd: "{{ amster_ds_rootpw }}"
  userStoreHost: "{{ amster_ds_hostname  }}"
  userStoreType: LDAPv3ForOpenDS
  userStoreSsl: SSL
  userStorePort: 10636
  userStoreRootSuffix: dc=bkwi,dc=NL
```

### Configure

Use `am_configure` to configure AM using Amster. To create a realm `myapp` for domain `myapp.com`

```yaml
am_configure:
  - name: Create Suwinet realm
    template: 103-configure_realm
    vars:
      realmName: myapp
      realmAliases: '[\"myapp.nl\"]' # escape for json body
```

Each entry in the list `am_configured` will create an Amster script on the file system that will be executed by Ansible. These scripts are self-contained: each script can be run individually.

```bash
root@bkd-am:/opt/amster/amster# ls | grep s0
s01-103-configure-realm.amster
s02-104-create-j2ee-agent.amster
s03-105-create-policy-set.amster
s04-106-create-policy.amster
s05-107-update-identity-store.amster
s06-108-set-sessionproperties.amster
s07-103-configure-realm.amster
s08-107-update-identity-store.amster
s09-108-set-sessionproperties.amster
```

`template` is above item refers to items in list `am_amster_templates`. The dict `am_amster_templates` specifies the mandatory and / or optional variables the scripts has. It can also specify additional subscripts to call as is the case for `110-create-authentication-LdapTree`

```yaml
am_amster_templates:
  110-create-authentication-LdapTree:
    vars: ['realmName','defaultTreeName','defaultAuthenticationService', 'primaryLDAPServer','bindUserPassword']
    vars-optional:
      - name: startDN
        value: cn=Directory Manager
      - name: dnToStartUserSearch
        value: o=myapp,c=NL
      - name: bindUserDN
        value: cn=Directory Manager
      - name: attributeUsedtoRetrieveUserProfile
        value: uid
      - name: attributeUsedtoSearchForAUserToBeAuthenticated
        value: uid
      - name: secondaryLDAPServer
        value:
    scripts:
      - 110-function-delete-authentication-tree
      - 110-function-create-authentication-tree
      # - 110-function-load-authentication-service
      # Set tree as default service
      # TODO uncomment when password reset works
```

#### 108-set-sessionproperties

Using template `108-set-sessionproperties` authentication settings can be changed. Settings that you can find admin interface Via **<Realm>** → **AUthencation** → **Settings** 

|parameter|required                     |default|choices                                      |comments|
|---------|-----------------------------|-------|---------------------------------------------|--------|
|realmName|yes                          |       |                                             |        |
|SharedSecret|yes                          |       |                                             |        |
|loginSuccessUrl|yes                          |       |                                             |        |
|loginFailureUrl|no                          |       |                                             |        |
|KeyAlias |no                           |test   |                                             |        |


```yaml
am_configure:
  - name: MyRealm session properties
    template: 108-set-sessionproperties
    vars:
      realmName: myRealm
      sharedSecret: "{{ amster_realm_defaults['shared_secret'] }}"
      loginSuccessUrl: https://myapp.com/index.html
      keyAlias: dev
```
#### 500-debug-logging

Using template `500-debug-logging` debug level can be configured. This is done globally and for each server.

```yaml
  - name: Debug level
    template: 500-debug-logging
    vars:
      debuglevel: error # warning, message, off
```
### Configure JSON

TODO `am_config_files` 

### Configure raw

Via `am_config_files_raw` various raw config files can be configured.

```yaml
am_config_files_raw:
- dest: "{{ tomcat_home_link }}/webapps/{{ am_context }}/WEB-INF/classes/debugconfig.properties"
  content: |
    org.forgerock.openam.debug.prefix=
    org.forgerock.openam.debug.suffix=-MM.dd.yyyy-HH.mm
    org.forgerock.openam.debug.rotation=1440
  notify: restart tomcat instance
```

Other attributes are owner, group and mode which default respectively to `tomcat`, `tomcat` and `0644`. 

### Certificate

It is recommended to replace the default secret stores that are created by AM during installation, see for example [Configuring Secrets, Certificates, and Keys](https://backstage.forgerock.com/docs/am/7/security-guide/keys-secrets.html#default-secret-stores).


```yaml
am_certificate:
  dev:
    cert: "{{ am_dev_cert }}"
    key: "{{ am_dev_key }}"
    keystore_path: "{{ amster_am_install['cfgDir'] }}/{{ am_context }}/keystore.jceks"
    keystore_pass_file: "{{ amster_am_install['cfgDir'] }}/{{ am_context }}/.storepass"
    keytool: "{{ java_versions[suwinet_java_version|default(java_version)]['keytool'] }}"
    notify: restart tomcat instance
```

### Git

Fetch arbitrary files from a Git repository and add them to DS filesystem. To configure the repo and the parent dir for this repository.

```yaml
am_git_config:
  repo: https://myrepo
  proxy: http://localhost:8888
am_git_config_parent_dir: /tmp
```
This will create a folder `/tmp/ds-git-config-<hash>`. You can also create this clone on the control for example if nodes don't have internet access. In this case we configure a custom checkout script using `am_git_config_script` because the Ansible Git module does not allow any Git config.

```yaml
am_git_config_control_node: yes
am_git_config_script: |
  if [ ! -d "{{ am_git_config['dir'] }}" ]; then
    git init {{ am_git_config['dir'] }}
    cd {{ am_git_config['dir'] }}
    git remote add origin {{ am_git_config['repo'] }}
    git config http.proxy {{ am_git_config['proxy'] }}
    git config pull.ff only
  fi
  cd {{ am_git_config['dir'] }}
  git pull origin master
```
Configure where the files should be created using `am_git_files` or `am_git_folders`.

#### Files

You can use `am_git_files` to configure where files you should be copied to.

```yaml
am_git_files:
- source: path/to/file/in/repo
  dest: "{{ amster_home_link }}/path/to/destfile"
```

| parameter | required | default | choices | comments                                           |
|-----------|----------|---------|---------|----------------------------------------------------|
| source    | yes      |      |         | Relative path of file in Git repository   |
| dest      | yes      |       |         | Absolute path of destination file 

Note: this uses the Ansible [copy](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html) module so you can also use `am_git_files` to copy directories for example as follows:

```yaml
am_git_files:
- source: suwinet_am/saml/bto/
  dest: "{{ amster_home_link }}/saml-config/"
```

One drawback of [copy](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html) module is that it does not delete files. If you want that you can use `am_git_folders` which uses [synchronize](https://docs.ansible.com/ansible/2.3/synchronize_module.html) module.

#### Folders

You can use `am_git_folders` to configure where complete folders you should be copied to. This uses Ansible [synchronize](https://docs.ansible.com/ansible/2.3/synchronize_module.html) module.

| parameter | required | default | choices | comments                                           |
|-----------|----------|---------|---------|----------------------------------------------------|
| source    | yes      |      |         | Relative path of source folder in Git repository   |
| dest      | yes      |       |         | Absolute path of destination folder on file system |
| recursive  | no      | yes      |         |  |
| delete     | no      | yes      |         |  |

```yaml
am_git_folders:
- source: suwinet_am/saml/bto/
  dest: "{{ amster_home_link }}/saml-config/"
```

### Keystore

Using `am_keystore` it is possible to replace the AM generated keystore with your own keystore.

Only an URL is required for example as follows:

```yaml
am_keystore:
  url: file:///vagrant/keystore.jceks
```

This will create for example the file `/opt/tomcat/am/acs/keystore.jceks` and update the content of `/opt/tomcat/am/acs/.storepass` to `changeit`

There are optional attribute to customize this behaviour:

1. `basename` for example if the basename of the download URL is different from what you want on the file system. For example if the URL is file:///vagrant/stub-keystore.jceks but you want to create a file `keystore.jceks`.
2. `checksum`
3. `group` and `owner`. Default `tomcat`.
4. `backup` `yes` or `no` to save original backup / storepass files.
5. `notify` if you want to notify some resource for example `restart tomcat instance`

Note: for some reason the keystore is continually changing so a cache copy is used to detect changes. The file is named for example `keystore.jceks.cache`.

### Manual mode

Amster scripts can be used manually. To enter Amster manual mode

```yaml
am_configure_manual: yes
```
Note: when running in manual mode the Ansible will fail at the end.

For example to run the first step

```bash
root@bkd-am:/opt/amster/amster# ./amster 01-103-configure-realm.amster 
WARNING: An illegal reflective access operation has occurred
WARNING: Illegal reflective access by org.codehaus.groovy.reflection.CachedClass (file:/opt/amster/amster-6.5.3/amster-6.5.3.jar) to method java.lang.Object.clone()
WARNING: Please consider reporting this to the maintainers of org.codehaus.groovy.reflection.CachedClass
WARNING: Use --illegal-access=warn to enable warnings of further illegal reflective access operations
WARNING: All illegal access operations will be denied in a future release
Amster OpenAM Shell (6.5.3 build fd13bbcf96, JVM: 11.0.4)
Type ':help' or ':h' for help.
--------------------------------------------------------------------------------------------------------------------------------------
am> :load 01-103-configure-realm.amster
===> true
===> true
===> true
===> true
===> true
===> true
===> true
===> true
===> true
===> true
===> true
===> true
===> true
Parameters
=========================================================
Create realm
=========================================================
===> {
    "name": "myapp",
    "active": true,
    "parentPath": "/",
    "aliases": [
        "suwinet.nl"
    ],
    "_rev": "369290511",
    "_id": "L3N1d2luZXQ"
}
no delta, skipping realm creation/update
===> null
```

## Dependencies

## Links

* [Amster 7.0.1 > User Guide > Install AM with Amster](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-install-am.html)
* [Amster 7.0.1 > User Guide > Connect to AM](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-connecting.html)
* [Using Variables in Amster Scripts](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-usage-scripts.html#amster-variables-scripts)
* [Amster 7.0.2 > Entity Reference > Realms](https://backstage.forgerock.com/docs/amster/7/entity-reference/sec-amster-entity-realms.html)
* [Amster 7.1 > Entity Reference > WebAgents]
https://backstage.forgerock.com/docs/amster/7.1/entity-reference/sec-amster-entity-webagents.html]