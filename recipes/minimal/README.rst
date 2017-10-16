**OpsMgr Minimal**
==================

The OpsMgr Minimal recipe is used to install and configure the
Operational Management stack into a generic cluster of servers
and a minimal set of infrastructure components that includes a
database (currently MySQL is supported).

OpsMgr itself and integrated Operational applications such as
Nagios Core and the ELK Stack are installed and configured
appropriately for cluster operation. Monitoring agent components
for the Ops applications, such as NRPE (Nagios Remote Process
Executor) and Filebeat (a log collector for Logstash), are also
installed and configured appropriately on all managed endpoints
in the cluster.

All components are installed in the host operating system in the
nodes they reside. There is no integrated user interface portal
or inventory management function, but each integrated Ops application
can still be accessed via their own user interfaces.

Finally, depending on what roles are associated with each managed
endpoints, different Ops packages are configured in the stack and
the respective Ops applications and agents.

OpsMgr Minimal can be reused by recipes that need basic Hardware and
Operating System monitoring capabilities. For installation purposes it
requres the following component::

   * Genesis (for bare metal installation)

To install OpsMgr in Minimal mode please perform the following steps
in the deployment node:

1. | Clone opsmgr project from GitHub:
   | https://github.com/open-power-ref-design-toolkit/opsmgr

2. | (Optional) Update the cluster inventory file to list additional
     management roles for each managed node. This can be achieved by editing the file:
   | /var/oprc/inventory.yml
   | Examples of valid management roles supported by OpsMgr are:
   | ubuntu - for nodes where the "Ubuntu Linux OS Ops package" will be
     deployed
   | rhel - for nodes where the "RedHat Linux OS Ops package" will be
     deployed

After inventory is configured and both initial cluster genesis and
os-service runs users can configure the OpsMgr Minimal stack for deployment
by running the the following script::

   > ./run.sh

Once this playbook runs you can call the main OpsMgr deployment playbooks by
modifying the values of OPSMGR_RECIPE and other key environment variables to
reference this recipe.

Example::

   > cd ../../playbooks
   > export OPSMGR_RECIPE=minimal
   > export OPSMGR_DIR=`pwd`/..
   > export OPSMGR_PRL=$OPSMGR_DIR/recipes/$OPSMGR_RECIPE/profile
   > ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory <playbook_name>

Automated uninstall of OpsMgr minimal configuration is currently not supported.
Please perform cleanup and re-install steps manually.

Please consult `this project's main README file <https://github.com/open-power-ref-design-toolkit/opsmgr>`_
for a general overview of OpsMgr and information on how to access its components.

