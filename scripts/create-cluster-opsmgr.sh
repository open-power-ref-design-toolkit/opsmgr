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
    echo "Usage: create-cluster-opsmgr [-i <controllernode1,...>] [-s <storagenode1,...>] [-c <computenode1,...>]"
    echo ""
    echo "export KIBANA_PASSWORD=                            Not applicable unless set"
    exit 1
fi

if [ ! -e scripts/bootstrap-opsmgr.sh ]; then
    echo "This script must be run from /root/os-services/opsmgr or opsmgr"
    exit 1
fi

SCRIPTS_DIR=$(dirname $0)
source $SCRIPTS_DIR/process-args.sh

echo "DEPLOY_AIO=$DEPLOY_AIO"
echo "InfraNodes=$infraNodes"
echo "allNodes=$allNodes"

echo "Generating passwords"

# Set password in file for named secret if it is not set in file and environment variable is set
set_passwd /etc/openstack_deploy/user_secrets_opsmgr.yml kibana_password $KIBANA_PASSWORD

# Ensure all needed passwords and tokens are generated
pushd /opt/openstack-ansible >/dev/null 2>&1
./scripts/pw-token-gen.py --file /etc/openstack_deploy/user_secrets_opsmgr.yml
popd >/dev/null 2>&1

echo "Running elk playbooks"
pushd playbooks_elk >/dev/null 2>&1
run_ansible elk.yml
popd >/dev/null 2>&1
