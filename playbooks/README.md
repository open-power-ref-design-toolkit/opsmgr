# Instructions for installing Nagios in an lxc container on the opsmgr server.

These instructions should be updated as other containers [ELK] are provided.

These instructions are written for Ubuntu 14.04 64 bit and are meant to be run on the opsmgr server. This is so ansible can access the lxc container it creates on the local network.

There are two roles/playbooks:
The opsmgr roles will create the lxc-container with a static ip and forward port 80 to the static ip.
The nagios_container will install nagios on the static ip.

After running these steps, the nagios web interface can be accessed at http://<host>/nagios  nagiosadmin/nagiosadmin

# Install Ansible
**sudo apt-get install python-pip python-dev git libffi-dev**
**sudo pip install ansible==1.9.4 markupsafe**


# git the code
Setup your ssh key for git (see the top level readme for help on this step)

**cd ~**

**git clone git@gitlabhost.rtp.raleigh.ibm.com:Ulysses/opsmgr.git**

# Configure variables
**cd ~/opsmgr/playbooks**

edit inventory_sample with the ip address of your system
**opsmgr ansible_ssh_host=<your ip>**

edit (if necessary) roles/opsmgr/vars/main.yml with the ssh user for the host and the password of the user for the sudo command. 
**ansible_ssh_user: userid**
**ansible_become_pass: PASSW0RD**

# Create SSH Key
Create (if neccesary) an ssh key to allow ansible to ssh into the host and nagios container. (If you already have an the ssh key ~/.ssh/id_rsa and ~/.ssh/id_rsa.pub), this step can be skipped.

Run: **ssh-keygen** and press enter 3 times to accept default values.

Run:
**cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys**
**chmod 700 ~/.ssh**
**chmod 600 ~/.ssh/authorized_keys**


#Run the ansible playbook:
**export ANSIBLE_HOST_KEY_CHECKING=False**
**/usr/local/bin/ansible-playbook site.yml -i inventory_sample**
