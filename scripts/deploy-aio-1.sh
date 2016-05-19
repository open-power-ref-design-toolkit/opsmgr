#!/usr/bin/env bash

# Before executing this script, the following manually patches are recommended:
#
#   /etc/ansible/roles/galera_client/tasks/galera_client_install_apt.yml
#       Set retries: 25 and delay: 10
#       Reason: circumvent poor network performance
#
#   /etc/ansible/roles/pip_install/tasks/main.yml
#       Set retries: 25 and delay: 10 in both "Get Modern PIP" and "Get Modern PIP using fallback URL"
#       Reason: circumvent poor network performance
#

set -e -u
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

# Install some prerequisite packages 
apt-get -y install git
apt-get -y install build-essential libssl-dev libffi-dev python-dev

OA_DIR="/opt/openstack-ansible"

# Checkout the openstack-ansible repository
if [ ! -d /opt/openstack-ansible ]; then
    git clone https://github.com/openstack/openstack-ansible $OA_DIR
    cd $OA_DIR 
    git checkout 13.1.0
fi
cd $OA_DIR 

BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_repo=http://us.archive.ubuntu.com/ubuntu/"
BOOTSTRAP_OPTS="${BOOTSTRAP_OPTS} bootstrap_host_ubuntu_security_repo=http://security.ubuntu.com/ubuntu/" 

if [ ! -d /etc/ansible ]; then
    scripts/bootstrap-ansible.sh
fi

#   /etc/ansible/roles/galera_client/tasks/galera_client_install_apt.yml
#       Set retries: 25 and delay: 10
#       Reason: circumvent poor network performance
#
#   /etc/ansible/roles/pip_install/tasks/main.yml
#       Set retries: 25 and delay: 10 in both "Get Modern PIP" and "Get Modern PIP using fallback URL"
#       Reason: circumvent poor network performance

echo "Some manual setup is required to avoid download failures.  Use local apt servers to avoid this issue."
echo ""
echo "vi /etc/ansible/roles/galera_client/tasks/galera_client_install_apt.yml"
echo "Set retries: 25 and delay: 10"
echo ""
echo "vi /etc/ansible/roles/pip_install/tasks/main.yml"
echo "Set retries: 25 and delay: 10 in both \"Get Modern PIP\" and \"Get Modern PIP using fallback URL\""
echo ""
echo "Run ./scripts/deploy-aio-2.sh"

