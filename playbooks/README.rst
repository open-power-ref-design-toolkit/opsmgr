OpsMgr Main Playbooks
==========================

This is a collection of playbooks intended to install an OpsMgr control plane.

Pre-requirements::

   * Ansible and networking already installed (suggest use of OSA's scripts)
   * An OpsMgr Recipe playbook has previously generated profile data
   * The OpsMgr profile data has been properly configured
   * All cluster nodes are accessible via SSH and have sudo configured

As an alternative users can run the following playbook to setup SSH and sudo::

   > ansible-playbook -e "opsmgr_dir=`pwd`/.." -i inventory setup.yml -kK

The first time the setup.yml playbook is run with the -kK parameters it will
ask for user and sudo credentials to configure SSH proxy on the local host and
sudoers on the remote nodes. The same credentials are used for all nodes.
Subsequent calls to OpsMgr playbooks can be done without need of credentials.

The setup.yml playbook assumes an SSH key pair exists under ~/.ssh.

After this initial setup, use the following commands to run additional OpsMgr
playbooks::

   > export OPSMGR_RECIPE=<recipe name>
   > export OPSMGR_DIR=`pwd`/..
   > export OPSMGR_PRL=$OPSMGR_DIR/recipes/$OPSMGR_RECIPE/profile
   > ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory <playbook>

The sequence of playbooks to run is as follows::

   * hosts.yml (creates OpsMgr LXC containers)
   * mysql.yml (installs MySQL - if the recipe uses it)
   * haproxy.yml (installs HAProxy optionally and/or configures an existing one)
   * nagios.yml (installs/configures Nagios server)
   * logstash.yml (installs/configures Logstash)
   * elasticsearch.yml (installs/configures Elasticsearch)
   * kibana.yml (installs/configures Kibana)
   * opsmgr.yml (installs the OpsMgr service and optionally its dashboard)
   * targets.yml (iterates over target types and calls provisioning plugins)

For convenience, all of the above playbooks with the exception of hosts.yml and
targets.yml are included in sequence in site.yml. A complete run of the
main OpsMgr playbooks must call, at a minimum: hosts.yml, site.yml, targets.yml.

The specific provisioning plugins that targets.yml calls depend on the profile.
A profile's host group triggers calls to a provisioning plugin with same name.
For example, in the osa-newton profile's inventory the following groups exist::

  * [opsmgr]
  * [osa-newton]

This means that when targets.yml executes it will lookup and call (if it exists) two
provisioning plugins, one called "opsmgr" and another called "osa-newton".

The [opsmgr] host group denotes which nodes the OpsMgr main playbooks will use to
install the OpsMgr control plane. At this moment there is no provisioning plugin for
this group, so the targets.yml run skips it. In the future, a specific configuration
may be added to manage the OpsMgr control plane (self-managing), by adding a plugin
called "opsmgr".

The [osa-newton] host group denotes the OpenStack-Ansible provisioner node, not the
multiple controllers, storage and compute nodes that comprise an OpenStack cluster.
The reason is that the "osa-newton" provisioning plugin reads the information about
these additional nodes directly from OSA's dynamic configuration. So, a recipe with
a [osa-newton] host group doesn't have to list each individual node only the deployer.

IMPORTANT::

   * Hosts listed in a group that correspond to a provisioning plugin MUST declare
     the ansible_ssh_host parameter with the value of that host's IP address.
     Example:
     [standard]
     localhost ansible_ssh_host=172.29.236.100

Other kinds of recipes may mix and match different kinds of clustered applications.
It's up to the user to build custom recipes and custom provisioning plugins it
may need (if not yet available).

Once the targets.yml playbook runs successfully the OpsMgr cluster is ready for use.
Note that individual integrated Ops applications such as Nagios and ELK may
need additional steps. For example, for Nagios users may want to tweak the frequency
of checks, or other configuration parameters. 

To tear down the OpsMgr control plane cluster, use the following::

   > ansible-playbook -e "opsmgr_dir=`pwd`/.." -i $OPSMGR_PRL/inventory clean.yml

Updates are not fully supported yet. If an update to OpsMgr is needed, run the
correct playbook for that update.

