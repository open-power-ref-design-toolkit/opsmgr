**OpsMgr Standalone**
=====================

The OpsMgr Standalone recipe is used to install and configure all 
required components to run the Operational Management stack from 
scratch, including infrastructure projects such as MySQL, RabbitMQ, 
Memcached and HAProxy. In addition, two basic OpenStack projects 
are installated to provide credential and access management 
(Keystone) and an extensible Web User Interface (Horizon).

OpsMgr itself and integrated Operational applications such as Nagios 
Core and the ELK Stack are installed and configured appropriately for 
standalone operation. Monitoring agent components for the Ops 
applications, such as NRPE (Nagios Remote Process Executor) and 
Filebeat (a log collector for Logstash), are also installed and 
configured appropriately on all managed endpoints in the cluster.

Finally, depending on what roles are associated with each managed 
endpoints, different Ops packages are configured in the stack and the 
respective Ops applications and agents.

OpsMgr Standalone can be reused by recipes that need basic Hardware 
and Operating System monitoring capabilities. For installation 
purposes it requres the following component::

   * Genesis (for bare metal installation)

To install OpsMgr in Standalone mode please perform the following 
steps in the deployment node:

1. | Clone opsmgr project from GitHub:
   | https://github.com/open-power-ref-design-toolkit/opsmgr

2. | (Optional) Update the cluster inventory file to list additional 
management roles for each managed node.
This can be achieved by editing the file:
   | /var/oprc/inventory.yml
   | Examples of valid management roles supported by OpsMgr are:
   | ubuntu - for nodes where the "Ubuntu Linux OS Ops package" will be 
deployed
   | nvidia\_gpu - for nodes where the "NVidia GPU Ops package" will be 
deployed

Once inventory is configured and initial cluster genesis runs users can 
provision the OpsMgr Standalone stack by running the the following scripts 
in sequence::

   > bootstrap-prereq.sh
   > bootstrap-opsmgr.sh
   > provision-prereq.sh
   > provision-opsmgr.sh

If a re-install is desired there are clean-up scripts for the user's 
convenience. They must be run prior to a re-install of the OpsMgr 
Standalone stack. To do it please run the following scripts in sequence::

   > clean-prereq.sh
   > clean-opsmgr.sh

If an uninstall of OpsMgr is desired please perform the following steps:

  * From the deployer node:
      * Run the clean.yml playbook from the playbooks directory to remove 
the OpsMgr containers
      * Edit the ~/.ssh/config file and remove each Host entry that uses 
the IdentityFile opsmgr.key
  * From each controller node:
      * Remove the directory /etc/opsmgr
      * From /etc/haproxy/conf.d remove the configuration files for 
Elasticsearch, Kibana, Logstash and Nagios and restart the haproxy service
  * From each controller node and endpoint being monitored:
      * Use apt purge to remove filebeat and nagios-nrpe-server
      * Remove the directories /etc/nagios and /etc/filebeat

Please consult `this project's main README file 
<https://github.com/open-power-ref-design-toolkit/opsmgr>`_ for a general 
overview of OpsMgr and information on how to access its components.

