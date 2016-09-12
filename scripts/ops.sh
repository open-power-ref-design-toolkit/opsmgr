#!/bin/bash

source $(dirname $0)/env.sh

pushd ${OPSMGR_DIR}
scripts/clean.sh

# opsmgr installation sequence
# please run from opsmgr root directory

# bootstraps ssh proxy, keys & sudoers
# note: requires .ssh/id_rsa|id_rsa.pub
echo "from playbooks running local.yml"
pushd playbooks
ansible-playbook -i inventory local.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/local.yml, rc=$rc"
    exit 2
fi
popd

# predeploy integrates opsmgr with osa
echo "from predeploy/osa running local.yml"
pushd predeploy/osa
ansible-playbook -i inventory local.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr predeploy/osa/local.yml, rc=$rc"
    exit 3
fi
popd

# stages generated inventory file
cp -f ext/inventory playbooks

# creates the containers
echo "from playbooks running hosts.yml"
pushd playbooks
ansible-playbook -i inventory hosts.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/hosts.yml, rc=$rc"
    exit 4
fi
popd

# deploys opsmgr and integration plugins
echo "from playbooks running site.yml"
pushd playbooks
ansible-playbook -i inventory site.yml
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running opsmgr playbooks/site.yml, rc=$rc"
    exit 5
fi
popd

popd

