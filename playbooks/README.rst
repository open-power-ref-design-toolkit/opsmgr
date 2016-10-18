OpsMgr Main Playbooks
==========================

This is a collection of playbooks intended to install an OpsMgr control plane.

Pre-requirements::

   * Ansible and networking already installed (suggest use of OSA's scripts)
   * An OpsMgr Recipe playbook has previously generated profile data
   * The OpsMgr profile data has been properly configured
   * All cluster nodes are accessible via ssh and have sudo configured

As an alternative users can run the following playbook to setup ssh and sudo::

   > ansible-playbook -e "OPSMGR_LIB=../lib" i localhost, setup.yml -kK

The first time the setup.yml playbook runs with the -kK parameters it will ask
for user and sudo creentials (assumes same for all nodes) and then configures
ssh proxy in the local host and sudoers in the remote nodes. Any subsequent call
to OpsMgr playbooks can be done without need of credentials.

The setup.yml playbook assumes a ssh key pair is created and under ~/.ssh.

After this initial setup use this command to run additional OpsMgr playbooks::

   > export OPSMGR_PRL=<recipe_directory>/profile
   > ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory <playbook>

The sequence of playbooks to run is as follows::

   * hosts.yml (creates OpsMgr LXC containers)
   * setup.yml (necessary a second time to setup LXC containers)
   * mysql.yml (installs MySQL - if the recipe uses it)
   * haproxy.yml (installs HAProxy optionally and/or configures an existing one)
   * nagios.yml (installs/configures Nagios server)
   * logstash.yml (nstalls/configures Logstash)
   * elasticsearch.yml (installs/configures ElasticSearch)
   * kibana.yml (installs/configures Kibana)
   * opsmgr.yml (installs the OpsMgr service and optionally its dashboard)
   * targets.yml (iterates over target types and calls provisioning plugins)

For convenience all of the above playbooks with exception of hosts.yml and
targets.yml are include in sequence in site.yml. So, a complete run of the
main OpsMgr playbooks must call, at a minimum: hosts.yml, site.yml, targets.yml.

The specific provioning plugins that targets.yml will call depend on the profile.
A profile's host group triggers calls to a provisioning plugin with same name.
For example, in the osa-mitaka profile's inventory file we find the following groups::

  * [opsmgr]
  * [osa-mitaka]

This means that when targets.yml executes it will lookup and call (if it exists) two
proviioning plugins, one called "opsmgr" and another called "osa-mitaka".

The [opsmgr] host group denotes which nodes the OpsMgr main playbooks will use to
install the OpsMgr control plane. At this moment there is no provisioning plugin for
this group, so the targets.yml run skips it. In the future we may add specific
confiuration to manage the OpsMgr control plane (self-managing), by adding a plugin
called "opsmgr".

The [osa-mitaka] host group denotes the OpenStack-Ansible provisioner node, not the
multiple controllers, storage and compute nodes that comprise an OpenStack cluster.
The reason is that the "osa-mitaka" provisioning plugin reads the information about
these additional nodes directly from OSA's dynamic configuration. So, a recipe with
a [osa-mitaka] host group doesn't have to list each individual node only the deployer.

IMPORTANT::

   * Hosts listed in a group that correspond to a provisioning plugin MUST declare
     the ansible_ssh_host parameter with the value of that host's IP address.
     Example:
     [standard]
     localhost ansible_ssh_host=172.29.236.100

Other kinds of recipes may mix and match different kinds of clustered applications.
It's up to the user to build custom recipes and the custom provisioning plugins it
may need (if not yet available).

Once the targets.yml playbook runs successfully the OpsMgr cluster is ready for use.
Please note that individual integrated Ops applications such as Nagios or ELK may
need additioanl steps. For example, on Nagios users may want to tweak the frequency
of checks, or other configuration parameters. And on ELK, the first time we open the
Kibana user interface it will ask for the creation of a default index. Please consult
each applications' own documentation for more information.

To tear the OpsMgr control plance cluster down you can use the following::

   > ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory

Updates are not fully supported yet. If an update to OpsMgr is needed, please run
the same procedures as in initial installation, selectively.

