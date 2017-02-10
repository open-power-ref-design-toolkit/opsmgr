Provisioning Plugin: Nvidia-GPU
===============================
Use this plugin to install the check_gpu_sensor nagios plugin for Nvidia

Edit, if necessary, .../opsmgr/lib/gpu/roles/nvidia_gpu/defaults/main.yml for the following variables::

   nvidia_driver: /usr/lib/nvidia-361  #The path to the nvidia driver installed on the systems
   pcie_generation: 3                  #The PCIe Generation of the graphics cards. Found with the command "nvidia-smi -a"
   pcie_link_width_max:                #The PCIe Link Width. Found with the command "nvidia-smi -a"


Modify the inventory file of the recipe used to install OpsMgr::

   ..../opsmgr/recipes/<recipe name>/profile/inventory

To contain an nvidida-gpu host group with each host containing a gpu listed in the format 
"<hostname> ansible_ssh_host=<ip address>". For example::

   [nvidia_gpu]
   host1 ansible_ssh_host=192.168.1.100
   host2 ansible_ssh_host=192.168.1.101
   host3 ansible_ssh_host=192.168.1.102

Then run the targets.yml playbook in .../opsmgr/playbooks

Please consult the README in the playbooks directory for more information on how to run the playbook.
