# Ansible Role ForgeRock Directory Services (DS)

This Ansible role is used to install, upgrade and remove [ForgeRock Directory Services](https://backstage.forgerock.com/docs/ds/6.5/install-guide/) components using the [Cross-Platform Zip](https://backstage.forgerock.com/docs/ds/6.5/install-guide/#install-files-zip).

[[_TOC_]]

# The main steps listed

1. Download and unpack
2. Run setup 
3. Create systemd service and enable it
4. Run a lot of extra configuration steps (Policies, Password validators, the combination of those)
5. Configure userstore
6. Configure off-the-shelf (technical) users. Not to be confused with 'real' users which come through a data load/migration process.
7. Configure replication


# Filesystem before and after situation
Before: no /opt/ds and anything below it
After: opt/ds/[ds-version]. Almost all relevant activity happens in the [ds-version]/bin directory.
Note that the configbase module (running dsconfig command) for some parts uses 'fingerprints': signatures of the last result stored on disk, to prevent unnecessary calls to dsconfig. This however assumes that Ansible is in full control of the file system.

If in some testing situation it is needed to make changes in DS, e.g. using dsconfig but also commands like ldapmodify, manually (outside Ansible), beware that the next Ansible run could not work as intended due to it relying on now outdated fingerprints.
The solution if you really needed to make manual changes in DS: manually remove the related fingerprint file, or simply all fingerprints, in /opt/ds/.fingerprint/6.5.4 directory. It causes Ansible to run a bit slower than it should, but it guarantees that it works as intended even in this 'manual' scenario.

# Systemd services changed
A service added: ds-config. It is a 2-layer wrapper around /bin/start-ds and stop-ds scripts. See the URL given on why this is needed.

# Role Variables 
TODO if needed
Note that the main dsconfig part(4.)  is highly parametrised, you could call it 'normalised' in SQL terms with no copypasting of elements. Parts 5 and 6 are not parametrised and hence have quite some copypasting. For the tiny bit of dsconfig usage there it would not be too hard to piggyback this on the parametrised framework. For the rest of the code (nontrivial, but still a lot shorter than dsconfig used to be) parametrising is for sure doable but the return-on-investment is debatable. One reason is that we talk not about 1 'shelled' command but three different, each with slightly different syntax; ldapsearch, ldapmodify and ldappasswordmodify.

# Requirements (to other parts)
The role currently runs requiring the Common and Java roles of the underlying Ansible ecosystem.
Requirements configured (now as group_vars on play level, but it could be done at role level too) are JDK/Java version,
java_home directory, expose java_home set to Yes.
So if the Java role would need to be replaced by different ones, these requirements would need to be translated for the new underlying roles.
For installing a cluster, mind the sequence:
1. First install the node which is NOT the config master. In DEV we call this DS2.
2. Then install the config master. It is this one that will have the step to configure the replication process, for both nodes. It also before configuring replication, does a check (ldapsearch) on whether the not-config-master node is up and running.




# Definition of Done
There are limited checks in the role, e.g. to see whether the DS service was already installed and configured. However more checks could be helpful,
this also makes the chance less that in AM and IG rollout errors are found related to mistakes in the DS install/config.


# Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)
* [DS 6 > Configuration Reference](https://backstage.forgerock.com/docs/ds/6/configref/index.html#preface) aka `dsconfig` command.
* Note that the -- commandline options given in the Forgerock website, as mentioned above, at times are buggy. The leading source for the proper ones is the help screen (dsconfig --help).

# TODO


## dsconfig add

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




## Global configuration

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

## Password validators

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
