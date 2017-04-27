**OpsMgr for Cloud**
====================

The OpsMgr for Cloud recipe is used to install and configure 
the Operational Management stack into an existing Cloud 
environment. It reuses the Cloud infrastructure's basic 
projects such as Galera, RabbitMQ, Memcached and HAProxy. 
In addition, the OpsMgr user interface extends the OpenStack 
Horizon dashboard.

OpsMgr itself and integrated Operational applications such as 
Nagios Core and the ELK Stack are installed and configured 
appropriately for Cloud operation. Monitoring agent components 
for the Ops applications, such as NRPE (Nagios Remote Process 
Executor) and Filebeat (a log collector for Logstash), are also 
installed and configured appropriately on all managed endpoints 
in the cluster.

Finally, depending on what roles are associated with each 
managed endpoints, different Ops packages are configured in the 
stack and the respective Ops applications and agents.

OpsMgr for Cloud can be reused by OpenStack-based recipes that 
need to monitor resources at various layers: Hardware,
Operating System, basic Infrastructure and OpenStack services. 
For installation purposes it requres the following component::

   * Genesis (for bare metal installation)
   * OS-Services (for OpenStack-Ansible installation on OpenPOWER nodes)

To install OpsMgr in Cloud mode please perform the following steps 
in the deployment node:

1. | Clone opsmgr project from GitHub:
   | https://github.com/open-power-ref-design-toolkit/opsmgr

2. | (Optional) Update the cluster inventory file to list additional 
management roles for each managed node.
This can be achieved by editing the file:
   | /var/oprc/inventory.yml
   | Examples of valid management roles supported by OpsMgr are:
   | ubuntu - for nodes where the "Ubuntu Linux OS Ops package" will be 
deployed
   | osa-newton - for the node where "OpenStack-Ansible" has been 
deployed from (usually same as OpsMgr)

Obs.: the "osa-newton" Ops package automatically configures separately 
all nodes in an OpenStack deployment, including Control Plane nodes, 
Compute nodes and Storage nodes.

After inventory is configured and both initial cluster genesis and o
s-service runs users can provision the OpsMgr Standalone stack by 
running the the following scripts::

   > ./scripts/bootstrap-opsmgr.sh
   > ./scripts/create-cluster-opsmgr.sh

For convenience the os-services component can automatically orchestrate 
the deployment of an OpsMgr for Cloud stack components by calling the 
above scripts if the following environment variables are set prior to 
initial provisioning::

   > export DEPLOY_OPSMGR=yes
   > export ANSIBLE_HOST_KEY_CHECKING=False

If an uninstall of OpsMgr is desired please perform the following steps:

  * From the deployer node:
      * Run the clean.yml playbook from the playbooks directory to 
remove the OpsMgr containers
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

