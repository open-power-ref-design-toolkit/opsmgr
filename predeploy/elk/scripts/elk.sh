#!/bin/bash

set -e -x
set -o pipefail

ADMIN_PASSWORD="passw0rd"
NET_MAX_SPEED=1000

export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-""}
export ANSIBLE_FORCE_COLOR=${ANSIBLE_FORCE_COLOR:-"true"}
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-""}

# Assumes starts in the opsmgr directory
if [ ! -e scripts/deploy-elk.sh ]; then
    echo "Assumes one starts in the opsmgr directory.  ie. /root/opsmgr, ~/opsmgr, ..."
    exit 1
fi
OPSMGRDIR=`pwd`
ELKDEPLOY=${OPSMGRDIR}/predeploy/elk
OSADEPLOY=${ELKDEPLOY}/etc/openstack_deploy

# Checkout the openstack-ansible repository
if [ ! -d /opt/openstack-ansible ]; then
    echo "Error -- Openstack is not configured!"
    exit 1
fi

if [ ! -d /etc/ansible ]; then
    echo "Error -- Openstack is not configured!"
    exit 1
fi

if [ ! -d /etc/openstack_deploy ]; then
    echo "Error -- Openstack is not configured!"
    exit 1
fi

export FORKS=${FORKS:-$(grep -c ^processor /proc/cpuinfo)}

function run_ansible {
  openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}

OA_DIR="/opt/openstack-ansible"

BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_repo=http://us.archive.ubuntu.com/ubuntu/"
BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_security_repo=http://security.ubuntu.com/ubuntu/" 

cd $OA_DIR 

# Enable playbook callbacks from OSA to display playbook statistics
grep -q callback_plugins playbooks/ansible.cfg || sed -i '/\[defaults\]/a callback_plugins = plugins/callbacks' playbooks/ansible.cfg

# Don't deploy security hardening
if grep -q '^apply_security_hardening:' /etc/openstack_deploy/user_variables.yml
then
    sed -i "s/^apply_security_hardening:.*/apply_security_hardening: false/" /etc/openstack_deploy/user_variables.yml
else
    echo "apply_security_hardening: false" >> /etc/openstack_deploy/user_variables.yml
fi

OS_VARS="${OSADEPLOY}/user_extras_variables.yml"
OS_SECRETS="${OSADEPLOY}/user_extras_secrets.yml"

# Set the kibana admin password
sed -i "s/kibana_password:.*/kibana_password: ${ADMIN_PASSWORD}/" ${OS_SECRETS}

# Set network speed for vms
sed -i "s/net_max_speed:.*/net_max_speed: ${NET_MAX_SPEED}/" ${OS_VARS}

# Ensure all needed passwords and tokens are generated
./scripts/pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml
./scripts/pw-token-gen.py --file ${OS_SECRETS}

cp -R ${OSADEPLOY} /etc

cd ${OA_DIR}/playbooks/

# Setup the hosts and build the basic containers
run_ansible setup-hosts.yml

# Begin the OPSMGR installation
cd ${ELKDEPLOY}/

# Configure ELK stack in separate containers
run_ansible elk.yml

