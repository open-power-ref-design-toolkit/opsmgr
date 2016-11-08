#!/bin/bash

source $(dirname $0)/env.sh

pushd ${OPSMGR_DIR}

# opsmgr installation sequence
# please run from opsmgr root directory

# creates profile for integrated OSA installation
echo "from recipes/privatecloud-mitaka running site.yml"
pushd recipes/privatecloud-mitaka
ansible-playbook -e "opsmgr_lib=../../lib" -i inventory site.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr recipes/privatecloud-mitaka/site.yml, rc=$rc"
    exit 2
fi
popd

# bootstraps ssh proxy, keys & sudoers
# note: requires .ssh/id_rsa|id_rsa.pub
echo "from playbooks running setup.yml"
pushd playbooks
export OPSMGR_PRL=../recipes/privatecloud-mitaka/profile
ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory setup.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/setup.yml, rc=$rc"
    exit 2
fi
popd

# creates the containers
echo "from playbooks running hosts.yml"
pushd playbooks
ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory hosts.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/hosts.yml, rc=$rc"
    exit 4
fi
popd

# deploys opsmgr and integration plugins
echo "from playbooks running site.yml"
pushd playbooks
ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory site.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/site.yml, rc=$rc"
    exit 5
fi
popd

# deploys beaver and nrpe on the endpoints
echo "from playbooks running targets.yml"
pushd playbooks
ansible-playbook -e "OPSMGR_LIB=../lib" -i $OPSMGR_PRL/inventory targets.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/targets.yml, rc=$rc"
    exit 6
fi
popd

popd
