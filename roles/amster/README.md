# Ansible Role ForgeRock Amster CLI

This Ansible role is used to install, upgrade and remove [ForgeRock Amster CLI](https://backstage.forgerock.com/docs/amster/6.5/user-guide/).

[[_TOC_]]

## Requirements

ForgeRock uses zip files mostly - not tarballs, so to use this role `unzip` is required on target nodes.

Note that the 'Amster' utility part of the AM install connects with a ForgeRock DS server.
Hence requirement is that the configured DS server already is up and running. In a 2-server setup as is now the standard, provisioning of the DS node goes first. The role does a check whether the DS instance is up and running, using the ldapsearch utility which checks on port level.

Also note that the role itself is idempotent: if Amster has been run already (detected through directory /opt/am/<version>/openamcfg), it won't run again. Reason is that in the DS modifications, Amster does some 'create' calls with unique keys.
Hence if your role has changed (e.g. different content of a template like config.amster.j2) and you want to provision afresh, recreate both the DS VM and the AM VM in order for the new Amster settings to have effect! As you see in the check above however requirement is that Amster is installed on the same server as AM. The split into a separate role was done as technically Amster can be a separate machine, but there are no current plans
for this yet. Materialising these plans would mean that the idempotency check above cannot be a local check on the openamcfg directory,
but must become a remote call from the Amster node to a different node (DS or AM) to determine whether it already has been run for this Amster file.
(In the real life situation, the AM/DS nodes get configured using quite a few Amster files - roughly one per Suwinet application.)

Also note that the idempotency check, even if improved as above checking the AM node, is not complete.
The effect of an Amster run is not only a change on the file system of the AM/Amster node, being the openamcfg directory, but also stores data in DS.
If you e.g. throw away an AM-Amster node but not the associated DS node Amster will fail with a not-so-helpful NullPointerException error, see.

https://backstage.forgerock.com/knowledge/kb/article/a81999726


## Role description

1. Download and unpack Amster tool
2. Run the Amster tool, calling the config instance on the associated DS server

# Filesystem before and after situation
Before: no opt/amster and anything below it.

After situation for Amster:
/opt/amster/amster-[version] has the tool.
/opt/am/[version]/openamcfg is created after a succesful run of Amster (and used to check existence, avoiding a duplicate run)
And amster tool makes a lot of changes in how AM works; probably most of them are stored in the associated DS server.



## Role Variables


## Dependencies

## Definition of done

See AM role, Amster changes the behaviour of AM main screen




