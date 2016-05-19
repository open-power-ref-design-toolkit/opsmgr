#!/usr/bin/env bash

set -e -x
set -o pipefail

ADMIN_PASSWORD="passw0rd"

export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-""}
export ANSIBLE_FORCE_COLOR=${ANSIBLE_FORCE_COLOR:-"true"}
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-""}

# Assumes starts in the opsmgr directory
if [ ! -e scripts/deploy-aio-1.sh ]; then
    echo "Assumes one starts in the opsmgr directory.  ie. /root/opsmgr"
    exit 1
fi
OPSMGRDIR=`pwd`

export FORKS=${FORKS:-$(grep -c ^processor /proc/cpuinfo)}

function run_ansible {
  openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}

OA_DIR="/opt/openstack-ansible"

# Checkout the openstack-ansible repository
if [ ! -d /opt/openstack-ansible ]; then
    echo "Need to run ./scripts/deploy-aio-1.sh first"
    exit 1
fi
cd $OA_DIR 

BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_repo=http://us.archive.ubuntu.com/ubuntu/"
BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_security_repo=http://security.ubuntu.com/ubuntu/" 

if [ ! -d /etc/ansible ]; then
    echo "Need to run ./scripts/deploy-aio-2.sh first"
    exit 1
fi

if [ ! -d /etc/openstack_deploy ]; then
    scripts/bootstrap-aio.sh
fi

# Enable playbook callbacks from OSA to display playbook statistics
grep -q callback_plugins playbooks/ansible.cfg || sed -i '/\[defaults\]/a callback_plugins = plugins/callbacks' playbooks/ansible.cfg

# Don't deploy security hardening
if grep -q '^apply_security_hardening:' /etc/openstack_deploy/user_variables.yml
then
    sed -i "s/^apply_security_hardening:.*/apply_security_hardening: false/" /etc/openstack_deploy/user_variables.yml
else
    echo "apply_security_hardening: false" >> /etc/openstack_deploy/user_variables.yml
fi

OS_VARS="${OPSMGRDIR}/etc/openstack_deploy/user_extras_variables.yml"
OS_SECRETS="${OPSMGRDIR}/etc/openstack_deploy/user_extras_secrets.yml"

# Set the kibana admin password
sed -i "s/kibana_password:.*/kibana_password: ${ADMIN_PASSWORD}/" ${OS_SECRETS}

# Set network speed for vms
echo "net_max_speed: 1000" >>${OS_VARS}

cp ${OS_SECRETS} /etc/openstack_deploy/
cp ${OS_VARS} /etc/openstack_deploy/

# Ensure all needed passwords and tokens are generated
./scripts/pw-token-gen.py --file /etc/openstack_deploy/user_secrets.yml
./scripts/pw-token-gen.py --file ${OS_SECRETS}

# Copy container definitions for elk
cp ${OPSMGRDIR}/etc/openstack_deploy/env.d/* /etc/openstack_deploy/env.d/

cd ${OA_DIR}/playbooks/

# Setup the hosts and build the basic containers
run_ansible setup-hosts.yml

# Setup the infrastructure
run_ansible setup-infrastructure.yml

# This section is duplicated from OSA/run-playbooks as RPC doesn't currently
# make use of run-playbooks. (TODO: hughsaunders)
# Note that switching to run-playbooks may inadvertently convert to repo build from repo clone.
# When running in an AIO, we need to drop the following iptables rule in any neutron_agent containers
# to ensure that instances can communicate with the neutron metadata service.
# This is necessary because in an AIO environment there are no physical interfaces involved in
# instance -> metadata requests, and this results in the checksums being incorrect.
ansible neutron_agent -m command \
                      -a '/sbin/iptables -t mangle -A POSTROUTING -p tcp --sport 80 -j CHECKSUM --checksum-fill'
ansible neutron_agent -m shell \
                      -a 'DEBIAN_FRONTEND=noninteractive apt-get install iptables-persistent'

# Setup openstack
run_ansible setup-openstack.yml

if [[ "${DEPLOY_TEMPEST}" == "yes" ]]; then
    # Deploy tempest
    run_ansible os-tempest-install.yml
fi

# Begin the OPSMGR installation
cd ${OPSMGRDIR}/playbooks/

# Configure ELK stack in separate containers
run_ansible setup_logging.yml

# Reconfigure haproxy for ELK containers 
run_ansible haproxy.yml
