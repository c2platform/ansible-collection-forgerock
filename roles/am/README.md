# Ansible Role ForgeRock Access Management (AM)

This Ansible role is used to setup and configure [AM](https://go.forgerock.com/Access-Management.html) usig [Amster](https://backstage.forgerock.com/docs/amster/6.5/user-guide/).

<!-- MarkdownTOC levels="2,3" autolink="true" -->

- [Requirements](#requirements)
- [Role description](#role-description)
- [Role Variables](#role-variables)
  - [Installation](#installation)
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

## Dependencies

## Links

* [Amster 7.0.1 > User Guide > Install AM with Amster](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-install-am.html)
* [Amster 7.0.1 > User Guide > Connect to AM](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-connecting.html)
* [Using Variables in Amster Scripts](https://backstage.forgerock.com/docs/amster/7/user-guide/amster-usage-scripts.html#amster-variables-scripts)
