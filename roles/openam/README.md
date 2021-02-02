Ansible AM Role
=========

This role installs ForgeRock AM (commercial version) on your target host. During development we sometimes use the open source version OpenAM, but in
the end what BKWI needs is AM.

Note: This role is still in active development. There may be unidentified issues and the role variables may change as development continues.
One shortcoming is that in present stage the Vagrant name remains 'openam', and as a consequence some of the variables
used in the playbook/role cannot start with 'am' but need 'openam'. This will change later.

Requirements
------------

Note that the 'Amster' utility part of the AM install connects with a ForgeRock DS server.
Hence requirement is that the configured DS server already is up and running. If testing is done on a combined DS/AM node, the DS role hence
has to run before the AM role. If testing is done with separate nodes, provisioning of the DS node goes first. A suggested
enhancement is to do a CURL-like test to check connectivity with the DS node before running the Amster role, and halting if
it cannot be reached; this is in scope of the User Story to split into separate AM and DS plays.

# Ansible Role ForgeRock Access Management(AM)

This Ansible role is used to install, upgrade and remove AM including the Amster configuration tool on a node.


1. Download and unpack WARfile (both in AM and in Tomcat WebApp directory)
2. Download and unpack Amster tool
3. Run the Amster tool, calling the config instance on the associated DS server


# Filesystem before and after situation
Before: no /opt/am and opt/amster and anything below it. And no user forgerock and its homedirectory.
After for AM:  
User and homedirectory for forgerock.
/opt/am has the unpacked war file.
Same war file is also deployed as am.war under /opt/tomcat/webapps (our Tomcat role might have this directory name as variable, using it instead of hardcoding would then be better.)

After situation for Amster:
/opt/amster/<version> has the tool.
/opt/am/<version>/openamcfg is created after a succesful run of Amster (and used to check existence, avoiding a duplicate run)
And amster tool makes a lot of changes in how AM works; probably most of them are stored in the associated DS server.


# Code samples and variable usage 
TODO if needed


# All dependencies/requirements to other parts
Note: combined for AM-DS, needs to be separated once we split these two roles into 2 plays.
The role currently runs requiring the Common, Java and Tomcat roles of the underlying Ansible ecosystem.
Requirements configured (now as group_vars for the openam play, but it could be done at role level too) are JDK/Java version, Tomcat version,
java_home directory, tomcat userid, expose java_home set to Yes.
So if the Java and Tomcat roles would need to be replaced by different ones, these requirements would need to be translated for the new underlying roles.

Tomcat package will automatically install on task preinstall.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: localhost
      roles:
         - role: openam

Tomcat start on http://domain:8080
OpenAm available on http://domain:8080/am



# Definition of Done
Currently this is limited to
a] Before Amster has run, being able to access the bare bones AM console at the link given above.
b] After Amster has run, the AM console then will have been changed into a more complete dialogue where login is possible with the credentials specified in the Ansible template.






