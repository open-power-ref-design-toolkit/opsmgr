OpsMgr ansible playbooks

Pre-requisites:
- Ubuntu 14.04 (trusty)
- Ansible > 1.9 < 2.0

Introduction:

OpsMgr consist of a "core" component that creates lxc containers on a controller host (specified in inventory under group "opsmgr_hosts") and target hosts (specified in inventory under group "opsmgr_targets") that correspond to the endpoints managed by the framework.

The lxc containers host open applications that aim to provide operational management for the target hosts (or cluster of hosts). These open applications can play roles such as health monitoring, log collectino & analysis, provisioning, compliance and updates, configuration and scaling, and other operation-time tasks. There are clearly open applications that specialize in such tasks and we aim to reuse them for the purpose of building a self-contained operational management framework.

In addition to these open applications the framework also manages target endpoints that play a specific role. These targets could be of different types:
- firmware
- operating systems
- services
- virtualized resources
- virtualized payloads
- containers
- applications
- clusters of applications
- other management frameworks (e.g. openstack)

In order to provision and manage these types of resources OpsMgr is extensible via plugins. Depending on the type of managed resource it may need implementaition of multiple types of plugins to play nicely with the integrated OpsMgr framework. Examples of plugin types are:
- Provisioning (ansible playbooks that help deploy components of the integrated open applications)
- Discovery (python modules that collect endpoint data and feed into OpsMgr's inventory)
- Inventory (python modules that implement the OpsMgr inventory model for a resource)
- Operations - these are integration points with the Open applicatoins integrated by OpsMgr; different integrated applications will need different configuration in order to manage any given resource, and they might even have plugins of their own that provide additional management capabilities. It's the task of the OpsMgr operations plugin to provide that integration point with open applications.

Contents:

OpsMgr provisioning is accomplished via ansible playbooks. The "core" integration with open application servers is performed in the "playbooks" directory of OpsMgr (this location). 
The following core plays/roles are implemented so far:
- bootstrap.yml: convenience play to set up a common ssh key and sudoers access (as needed) all inventory hosts.
- site.yml: end-to-end playbook that orchestrates the main plays (except bootstrap and teardown).
- hosts.yml: build lxc containers for integrated open applications and adds them into dynamic inventory.
- opsmgr.yml Installs the opsmgr CLI, UI and plugins in a horizon container
- local.yml: sets up ssh key and sudoers for the created containers.
- <app>.yml: plays that are responsible for installing the server side of integrated open applications.
- targets.yml: play that discovers what types of resources are defined into inventory and spawns calls to the integrated provisioning plugins.
- teardown.yml: convenience play to tear down previously created containers.

Initially only the Nagios Core application is integrated, for monitoring purposes. The corresponding play is called nagios.yml.

In addition, each type of resource that is managed by OpsMgr will need additional provisioning plugins, located under "plugins/provisioning".
In our first release the only type of resource supported is "osa" (short for OpenStack-Ansible), which is the host where OSA has previously run to provision an OpenStack cluster.
Our "osa" plugin is located under ../plugins/provisioning/osa, and the play's main entry point is site.yml.

**Important** - this plugin assumes that the target host has an existing dynamic inventory populated by OpenStack-Ansible. Our play analyses OSA's dynamic inventory to determine other hosts in the OpenStack cluster, their associated roles, their associated lxc containers (tht host OpenStack services) and the role they play in the cluster.


Installation:

Pre-requisites:
- Ubuntu 14.04 (trusty)
- Ansible > 1.9 < 2.0

Configuration files:
- "inventory" contains the host groups to host lxc containers (opsmgr_hosts), the opsmgr ui (opsmgr) and that point to managed endpoints (opsmgr_targets).
- "vars/containers.yml" defines the lxc containers that will be created and their "roles" (e.g. a container that hosts Nagios Core is assigned the "nagios" role). This field of the container controls which integrated play will be called afterwards to install the open integrated applications.

How to run:

1) (optional, if ssh key/sudo is not yet set) the bootstrap.yml play sets up a common ssh key (opsmgr.key/pub) to be used during deploy:
ansible-playbook -i inventory -u <user> -kK bootstrap.yml
= this will prompt for the user's ssh and sudo passwords

2) end-to-end playbook that deploys OpsMgr core unto "opsmgr_hosts" hosts and spawns calls to provisioning plugins unto "opsmgr_targets" hosts:
ansible-playbook -i inventory site.yml

Obs: For resource type "role" discovery it's necessary that "opsmgr_targets" hosts have a pre-populated file under "/etc/opsmgr/.spec" with the following contents:
opsmgr_spec:
  - <resource_type>

Where <resource_type> corresponds to a supported plugin under ../plugins/provisionning.

At this time only the resource_type of "osa" is supported, but we welcome additions to other types of resources by the open community.
In addition, community contributions to integrate other open applications are mostly welcome as well (e.g. ELK, Zabbix, Landspace, SaltStack, etc.).

After running these steps Nagios should be pre-installed into the defined lxc containers and properly configured and pre-populated with lots of probes to monitor all OpenStack hosts and containers/services.

