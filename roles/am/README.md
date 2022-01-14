# Ansible Role ForgeRock Access Management (AM)

This Ansible role is used to setup and configure [AM](https://go.forgerock.com/Access-Management.html) using [Amster](https://backstage.forgerock.com/docs/amster/6.5/user-guide/) and other means. 

<!-- MarkdownTOC levels="2,3,4" autolink="true" -->

- [Requirements](#requirements)
- [Role Variables](#role-variables)
  - [Installation](#installation)
  - [Configure](#configure)
    - [108-set-sessionproperties](#108-set-sessionproperties)
    - [500-debug-logging](#500-debug-logging)
  - [Configure REST](#configure-rest)
  - [Configure JSON](#configure-json)
  - [Configure raw](#configure-raw)
  - [Files, directories and ACL](#files-directories-and-acl)
  - [Certificate](#certificate)
  - [Git](#git)
    - [Files](#files)
    - [Folders](#folders)
  - [Keystore](#keystore)
  - [Manual mode](#manual-mode)
- [Dependencies](#dependencies)
- [Notes](#notes)
  - [Amster](#amster)
- [Links](#links)

<!-- /MarkdownTOC -->

## Requirements

ForgeRock uses zip files mostly - not tarballs, so to use this role `unzip` is required on target nodes.

## Role Variables

|var                      |required|default|choices|comments                                                                                                                      |
|-------------------------|--------|-------|-------|------------------------------------------------------------------------------------------------------------------------------|
|am_amster_scripts_default|no      |yes    |       |List of Amster scripts that are always created and executed.                                                                  |
|am_amster_subscripts     |no      |yes    |       |List of Amster scripts that are called by other Amster scripts. These will always be created regardless of what you configure.|
|am_amster_templates      |no      |yes    |       |List of templates for creating Amster scripts. It also defines the scripts with required and optional variables.              |
|am_configure             |no      |no     |       |List of Amster scripts that defines the scripts to actually execute in order with the actual arguments values.                |
|amster_am_install        |no      |no     |       |This dict basically describes the install command to run using Ansible to install AM. See [Installation](#installation)       |
              |


### Installation

Use `amster_am_install` var to control installation

```yaml
amster_am_install:
  serverUrl: TODO
  adminPwd: "{{ am_amster_amadmin_pw }}"
  acceptLicense: ''
  pwdEncKey: "{{ am_amster_encryptpw }}"
  cfgStoreDirMgr: 'uid=am-config,ou=admins,ou=am-config'
  cfgStoreDirMgrPwd: '{{ am_amster_ds_rootpw }}'
  cfgStore: dirServer
  cfgStoreHost: "{{ am_amster_ds_hostname }}"
  cfgStoreAdminPort: 4444
  cfgStoreSsl: SSL
  cfgStorePort: 10636
  cfgStoreRootSuffix: ou=am-config
  cookieDomain: TODO
  cfgDir: /opt/tomcat/am # default $HOME/openam
  userStoreDirMgr: "cn=Directory Manager"
  userStoreDirMgrPwd: "{{ am_amster_ds_rootpw }}"
  userStoreHost: "{{ am_amster_ds_hostname  }}"
  userStoreType: LDAPv3ForOpenDS
  userStoreSsl: SSL
  userStorePort: 10636
  userStoreRootSuffix: dc=iwkb,dc=NL
```

`am_manage_parent_config_dir`

### Configure

Use `am_configure` to configure AM using Amster. There is an important note to be made about idempotancy with regards to the Amster scripts. 

A script will run when the script changes. The scripts 

`am_amster_force`


To create a realm `myapp` for domain `myapp.com`

```yaml
am_configure:
  - name: Create Siwunet realm
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

Scripts will only be executed if they change. This behaviour can be changed. For example if I want to a 500 script each time use `force` attribute as shown below.

```yaml
am_configure:
  - name: Debug level
    template: 500-debug-logging
    vars:
      debuglevel: "{{ siwunet_am_configure_500_debug_level }}"
    force: yes
```

You can also force all script to run each time

```yaml
am_amster_force: yes
```

Note: disabled scripts will never run. A `force` attribute or `am_amster_force` don't override attribute `enabled: no`

```yaml
am_configure:
  - name: siwunet-policy
    template: 106-create-policy
    enabled: no
    vars:
      policyName: siwunet-policy
      policySetName: siwunet-policy-set
      realmName: siwunet
      realms: ['siwunet']
      resources:
        - https://some.url/*
        - https://some.url/*?
        - https://some.url/*?*
      am.protected.uidIdentifier: whatever
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
      sharedSecret: l8wOCob/UBw26X62nS5xEawumOBP3GYo5WG7nJ2PSvU= # openssl rand -base64 32
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

### Configure REST

The REST interface of AM can also be used directly of course ( rather than indirectly via Amster ). To make this more convenient this role integrates the [c2platform.core.rest](https://github.com/c2platform/ansible-collection-core/tree/master/roles/rest) role. The configuration is an example of the use of this role. It defines two *groups* of REST requests `01_authenticate` and `02_amUserAdmin` that achieves the following:

1. The `id: Authenticate` request performs login and returns a token that is used in `02_amUserAdmin` group requests by setting in the default `samb` header.
2. `id: amUserAdmin` creates the user `amUserAdmin`.
3. `id: amDelegates` create the group `amDelegates`.
4. `id: amUserAdmin_amDelegates` add the user `amUserAdmin` to the group.
5. `id: amDelegates_privileges` updates the privileges of the group `amDelegates`.

```yaml
am_rest_headers:
  samb: "{{ rest_responses['01_authenticate'][0]['json']['tokenId']|default(omit) }}"
  Content-Type: application/json
  Accept-API-Version: resource=4.0, protocol=2.0
am_rest_base_url: "https://{{ ansible_fqdn }}:{{ tomcat_ssl_connector_port }}/{{ am_context }}/"
am_rest_resources:
  01_authenticate:
    headers: 
      X-OpenAM-Username: amadmin
      X-OpenAM-Password: "{{ am_amster_amadmin_pw }}"
      Content-Type: application/json
      Accept-API-Version: resource=2.0, protocol=1.0
    resources:
      - id: Authenticate
        url: json/realms/root/authenticate
  02_amUserAdmin:
    resources:
      - id: amUserAdmin # user
        url: json/realms/root/users/?_action=create
        body_format: json
        body:
          username: amUserAdmin
          userpassword: supersecret
        status_code: [201,409] # 409 is conflict / resource exists
      - id: amDelegates # group
        url: json/realms/root/groups?_action=create
        body_format: json
        body:
          username: amDelegates
        status_code: [201,409] # 409 idem, is conflict
      - id: amUserAdmin_amDelegates
        url: json/realms/root/groups/amDelegates
        method: PUT
        body_format: json
        body:
          uniquemember:
            - uid=amUserAdmin,ou=people,dc=bkwi,dc=nl
        status_code: [200] # always 200
      - id: amDelegates_privileges
        url: json/realms/root/groups/amDelegates
        method: PUT
        body_format: json
        body:
          _id: amDelegates
          username: amDelegates
          realm: "/"
          universalid:
          - id=amDelegates,ou=group,ou=am-config
          members:
            uniqueMember:
            - amUserAdmin
          cn:
          - amDelegates
          privileges:
            RealmAdmin: true
            LogAdmin: false
            LogRead: false
            LogWrite: true
            AgentAdmin: false
            FederationAdmin: false
            RealmReadAccess: false
            PolicyAdmin: true
            EntitlementRestAccess: false
            PrivilegeRestReadAccess: true
            PrivilegeRestAccess: true
            ApplicationReadAccess: false
            ApplicationModifyAccess: false
            ResourceTypeReadAccess: false
            ResourceTypeModifyAccess: false
            ApplicationTypesReadAccess: false
            ConditionTypesReadAccess: false
            SubjectTypesReadAccess: false
            DecisionCombinersReadAccess: false
            SubjectAttributesReadAccess: false
            SessionPropertyModifyAccess: false
        status_code: [200] # always 200
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

### Files, directories and ACL

Use dicts `am_files`, `am_directories`, `am_ac`l to create / manage any other files, directories and ACL. See [c2platform.core.files](https://github.com/c2platform/ansible-collection-core/tree/master/roles/files) for more information

### Certificate

It is recommended to replace the default secret stores that are created by AM during installation, see for example [Configuring Secrets, Certificates, and Keys](https://backstage.forgerock.com/docs/am/7/security-guide/keys-secrets.html#default-secret-stores).

am_shared_secrets

```yaml
am_certificate:
  dev:
    cert: "{{ am_dev_cert }}"
    key: "{{ am_dev_key }}"
    keystore_path: "{{ amster_am_install['cfgDir'] }}/{{ am_context }}/keystore.jceks"
    keystore_pass_file: "{{ amster_am_install['cfgDir'] }}/{{ am_context }}/.storepass"
    keytool: "{{ java_versions[siwunet_java_version|default(java_version)]['keytool'] }}"
    notify: restart tomcat instance
```

`am_certificate_force: no`

```yaml
am_certificate:
  dev:
    cert: "{{ am_dev_cert }}"
    key: "{{ am_dev_key }}"
    keystore_path: "{{ amster_am_install['cfgDir'] }}/{{ am_context }}/keystore.jceks"
    keystore_pass_file: "{{ amster_am_install['cfgDir'] }}/{{ am_context }}/.storepass"
    keytool: "{{ java_versions[siwunet_java_version|default(java_version)]['keytool'] }}"
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
  dest: "{{ am_amster_home_link }}/path/to/destfile"
```

| parameter | required | default | choices | comments                                           |
|-----------|----------|---------|---------|----------------------------------------------------|
| source    | yes      |      |         | Relative path of file in Git repository   |
| dest      | yes      |       |         | Absolute path of destination file 

Note: this uses the Ansible [copy](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html) module so you can also use `am_git_files` to copy directories for example as follows:

```yaml
am_git_files:
- source: siwunet_am/saml/bto/
  dest: "{{ am_amster_home_link }}/saml-config/"
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
- source: siwunet_am/saml/bto/
  dest: "{{ am_amster_home_link }}/saml-config/"
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
        "siwunet.nl"
    ],
    "_rev": "369290511",
    "_id": "L3N1d2luZXQ"
}
no delta, skipping realm creation/update
===> null
```

## Dependencies

## Notes

### Amster

This Ansible role relies on [Amster](https://backstage.forgerock.com/docs/amster/6.5/user-guide/) to do most of the configuration work.

> Amster is a command-line interface built upon the ForgeRock Access Management REST interface. Use Amster in DevOps processes, such as continuous integration, command-line installations, and scripted cloud deployments.

There are some issues with Amster when used from Ansible. There are some indications that Amster was designed with a _human_ operator in mind. And not a _non human_ operator like Ansible / AWX.  For example for some type of errors Amster will be put in *interactive* console mode. So your Ansible / AWX job will hang indefinitely waiting for user input. 

On the other hand other error conditions will be completely ignored. As a matter of fact the exit code of running an Amster script is always 0.  For example when you load another Amster script using `:load` that Amster cannot find this will be ignored. In this case Amster will *not* go in interactive console mode , it will instead just continue without reporting an error. The exit code will be 0 and you and Ansible won't know that something was wrong.

## Links

* [Amster 7.0.1 > User Guide > Install AM with Amster](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-install-am.html)
* [Amster 7.0.1 > User Guide > Connect to AM](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-connecting.html)
* [Using Variables in Amster Scripts](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-usage-scripts.html#amster-variables-scripts)
* [Amster 7.0.2 > Entity Reference > Realms](https://backstage.forgerock.com/docs/amster/7/entity-reference/sec-amster-entity-realms.html)
* [Amster 7.1 > Entity Reference > WebAgents]
https://backstage.forgerock.com/docs/amster/7.1/entity-reference/sec-amster-entity-webagents.html]
