#!/usr/bin/env bash
#
# Copyright 2016 IBM Corp.
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

if [ "$1" == "--help" ]; then
    echo "Usage: deploy-elk"
    echo ""
    echo "export KIBANA_PASSWORD=                            Not applicable unless set"
    exit 1
fi

if [ ! -e scripts/deploy-elk.sh ]; then
    echo "This script must be run from /root/os-services/opsmgr or opsmgr"
    exit 1
fi

# Checkout the openstack-ansible repository
if [ ! -d /opt/openstack-ansible ]; then
    echo "Error -- openstack-ansible is not configured!"
    exit 1
fi

if [ ! -d /etc/ansible ]; then
    echo "Error -- ansible is not configured!"
    exit 1
fi

if [ ! -d /etc/openstack_deploy ]; then
    echo "Error -- openstack is not configured!"
    exit 1
fi

SCRIPTS_DIR=$(dirname $0)
source $SCRIPTS_DIR/process-args.sh

echo "DEPLOY_AIO=$DEPLOY_AIO"
echo "InfraNodes=$infraNodes"
echo "allNodes=$allNodes"

echo "Copying opsmgr user variables and secrets to ${TARGET_OSA_DEPLOY}/openstack_deploy"
cp -R predeploy/elk/etc/openstack_deploy ${TARGET_OSA_DEPLOY}

echo "Generating passwords"

# Set password in file for named secret if it is not set in file and environment variable is set
set_passwd /etc/openstack_deploy/user_secrets_opsmgr.yml kibana_password $KIBANA_PASSWORD

# Ensure all needed passwords and tokens are generated
./scripts/pw-token-gen.py --file /etc/openstack_deploy/user_secrets_opsmgr.yml

echo "Running OSA playbooks"

pushd /opt/openstack-ansible/playbooks >/dev/null 2>&1
run_ansible setup-hosts.yml               # Setup the hosts and build containers
rc=$?
if [ $rc != 0 ]; then
    echo "Failed setup-hosts.yml"
    exit 2
fi     
run_ansible setup-infrastructure.yml      # Run the playbook to configure containers
rc=$?
if [ $rc != 0 ]; then
    echo "Failed setup-infrastructure.yml"
    exit 3
fi     
popd >/dev/null 2>&1

echo "Running ELK playbooks"

cd predeploy/elk
run_ansible elk.yml

