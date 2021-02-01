# Ansible Role ForgeRock Directory Services (DS)

This Ansible role is used to install, upgrade and remove [ForgeRock Directory Services](https://backstage.forgerock.com/docs/ds/6.5/install-guide/) components using the [Cross-Platform Zip](https://backstage.forgerock.com/docs/ds/6.5/install-guide/#install-files-zip).


1. Download and unpack
2. Run setup for config instance
3. Create systemd service and enable it
4. Repeat unpack, setup and systemd for user instance


# Filesystem before and after situation
Before: no /opt/ds and anything below it
After: opt/ds/version/config/opendj and version/user/opendj branches. All relevant activity happens in the two opendj/bin directories.
However to check whether the 'setup directory-server' command was already run, we check for existence of the opendj/bak directory; if it exists Ansible skips the setup.

# Systemd services changed
Two services added: ds-config and ds-user. Both are 2-layer wrappers around /opendj/start-ds and stop-ds scripts. See the URL given on why this is needed.

# Code samples and variable usage 
TODO if needed


# All dependencies/requirements to other parts
Note: combined for AM-DS, needs to be separated once we split these two roles into 2 plays.
The role currently runs requiring the Common, Java and Tomcat roles of the underlying Ansible ecosystem.
Requirements configured (now as group_vars for the openam play, but it could be done at role level too) are JDK/Java version, Tomcat version,
java_home directory, tomcat userid, expose java_home set to Yes.
So if the Java and Tomcat roles would need to be replaced by different ones, these requirements would need to be translated for the new underlying roles.


# Definition of Done
Currently this is limited to
a] /opendj/bin/status --offline command gives meaningful output. We use the command to check valid installation (but do accept errors in the output, we have more work to do here)
b] AM install, to be more specific the 'Amster' part of AM, is successful when calling an AM instance configured to use this DS instance.



# Links

* [How do I configure DS/OpenDJ (All versions) to be stopped and started as a service using systemd and systemctl? - Knowledge - BackStage](https://backstage.forgerock.com/knowledge/kb/article/a56766667)


# TODO

1. Starts two instances. Why? What is the purpose / idea of having two instances? Where is this deployment config explained  in ForgeRock documents?



