#!/bin/bash

# opsmgr installation sequence
# please run from opsmgr root directory

# bootstrap ssh proxy, keys & sudoers
pushd playbooks
ansible-playbook -i inventory local.yml
popd

# predeploy integrates opsmgr with osa
pushd predeploy/osa
ansible-playbook -i inventory local.yml
mv ansible.log local.log
mkdir -p ../../ext
cp -f etc/* ../../ext
cp -f etc/.spec ../../ext
popd

# sets up staging files for deployment
pushd ext
sudo mkdir -p /etc/opsmgr
sudo cp -f .spec /etc/opsmgr
sudo cp -f /root/.ssh/id_rsa .
sudo chmod 600 id_rsa
cp -f inventory ../playbooks
popd

# deploys opsmgr and integration plugins
pushd playbooks
ansible-playbook -i inventory site.yml
popd


