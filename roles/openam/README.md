Ansible AM Role
=========

This role installs ForgeRock AM (commercial version) on your target host. During development we sometimes use the open source version OpenAM, but in
the end what BKWI needs is AM.

Note: This role is still in active development. There may be unidentified issues and the role variables may change as development continues.
One shortcoming is that in present stage the Vagrant name remains 'openam', and as a consequence some of the variables
used in the playbook/role cannot start with 'am' but need 'openam'. This will change later.

Requirements
------------

Ansible
Note that the 'Amster' utility part of the AM install connects with a ForgeRock DS server.
Hence requirement is that the configured DS server already is up and running. If testing is done on a combined DS/AM node, the DS role hence
has to run before the AM role. If testing is done with separate nodes, provisioning if the DS node goes first. A suggested
enhancement is to do a CURL-like test to check connectivity with the DS node before running the Amster role, and halting if
it cannot be reached.

Role Variables
--------------



Dependencies
------------

- tomcat

This packets will automatically install on task preinstall.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: localhost
      roles:
         - role: openam

Tomcat start on http://domain:8080
OpenAm available on http://domain:8080/am
