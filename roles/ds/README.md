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

# Systemd services changed
A service added: ds-config. It is a 2-layer wrapper around /bin/start-ds and stop-ds scripts. See the URL given on why this is needed.

# Code samples and variable usage 
TODO if needed


# All dependencies/requirements to other parts
The role currently runs requiring the Common and Java roles of the underlying Ansible ecosystem.
Requirements configured (now as group_vars on play level, but it could be done at role level too) are JDK/Java version,
java_home directory, expose java_home set to Yes.
So if the Java role would need to be replaced by different ones, these requirements would need to be translated for the new underlying roles.

# Definition of Done
There are limited checks in the role, e.g. to see whether the DS service was already installed and configured. However more checks could be helpful,
this also makes the chance less that in AM and IG rollout errors are found related to mistakes in the DS install/config.


# Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)


# TODO


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
