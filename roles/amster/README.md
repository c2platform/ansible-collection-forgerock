# Ansible Role ForgeRock Amster CLI

This Ansible role is used to install, upgrade and remove [ForgeRock Amster CLI](https://backstage.forgerock.com/docs/amster/6.5/user-guide/).

[[_TOC_]]

## Requirements

ForgeRock uses zip files mostly - not tarballs, so to use this role `unzip` is required on target nodes.

Note that the 'Amster' utility part of the AM install connects with a ForgeRock DS server.
Hence requirement is that the configured DS server already is up and running. If testing is done on a combined DS/AM node, the DS role hence
has to run before the Amster role. If testing is done with separate nodes, provisioning of the DS node goes first. A suggested
enhancement is to do a CURL-like test to check connectivity with the DS node before running the Amster role, and halting if
it cannot be reached; this is in scope of the User Story to split into separate AM and DS plays.

Also note that the role itself is idempotent: if Amster has been run already (detected through directory /opt/am/<version>/openamcfg), it won't run again. Reason is that in the DS modifications, Amster does some 'create' calls with unique keys.
Hence if your role has changed (e.g. different content of a template like config.amster.j2) and you want to provision afresh, recreate both the DS VM and the AM VM in order for the new Amster settings to have effect! As you see in the check above however requirement is that Amster is installed on the same server as AM. The split into a separate role was done as technically Amster can be a separate machine, but there are no current plans
for this yet. Materialising these plans would mean that the idempotency check above cannot be a local check on the openamcfg directory,
but must become a remote call from the Amster node to a different node (DS or AM) to determine whether it already has been run.

## Role description

1. Download and unpack Amster tool
2. Run the Amster tool, calling the config instance on the associated DS server

# Filesystem before and after situation
Before: no opt/amster and anything below it.

After situation for Amster:
/opt/amster/<version> has the tool.
/opt/am/<version>/openamcfg is created after a succesful run of Amster (and used to check existence, avoiding a duplicate run)
And amster tool makes a lot of changes in how AM works; probably most of them are stored in the associated DS server.



## Role Variables


## Dependencies

## Definition of done

See AM role, Amster changes the behaviour of AM main screen




