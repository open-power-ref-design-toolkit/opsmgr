#!/bin/bash

source $(dirname $0)/env.sh

pushd ${OPSMGR_DIR}
scripts/clean.sh

# opsmgr installation sequence
# please run from opsmgr root directory

# bootstraps ssh proxy, keys & sudoers
# note: requires .ssh/id_rsa|id_rsa.pub
pushd playbooks
ansible-playbook -i inventory local.yml
popd

# predeploy integrates opsmgr with osa
pushd predeploy/osa
ansible-playbook -i inventory local.yml
popd

# stages generated inventory file
cp -f ext/inventory playbooks

# deploys opsmgr and integration plugins
pushd playbooks
ansible-playbook -i inventory site.yml
popd

popd

