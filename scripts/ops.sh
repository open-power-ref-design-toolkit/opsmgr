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
export PROFILE=../recipes/privatecloud-mitaka/profile
ansible-playbook -i $PROFILE/inventory -e "opsmgr_profile=$PROFILE" setup.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/setup.yml, rc=$rc"
    exit 2
fi
popd

# creates the containers
echo "from playbooks running hosts.yml"
pushd playbooks
export PROFILE=../recipes/privatecloud-mitaka/profile
ansible-playbook -i $PROFILE/inventory -e "opsmgr_profile=$PROFILE" hosts.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/hosts.yml, rc=$rc"
    exit 4
fi
popd

# deploys opsmgr and integration plugins
echo "from playbooks running site.yml"
pushd playbooks
export PROFILE=../recipes/privatecloud-mitaka/profile
ansible-playbook -i $PROFILE/inventory -e "opsmgr_profile=$PROFILE" site.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/site.yml, rc=$rc"
    exit 5
fi
popd

popd

