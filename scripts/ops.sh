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
popd

# predeploy integrates opsmgr with osa
echo "from predeploy/osa running local.yml"
pushd predeploy/osa
ansible-playbook -i inventory local.yml
popd

# stages generated inventory file
cp -f ext/inventory playbooks

# creates the containers
echo "from playbooks running hosts.yml"
pushd playbooks
ansible-playbook -i inventory hosts.yml
popd

# deploys opsmgr and integration plugins
echo "from playbooks running site.yml"
pushd playbooks
ansible-playbook -i inventory site.yml
popd

popd

