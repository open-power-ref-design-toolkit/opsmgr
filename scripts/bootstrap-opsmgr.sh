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
    echo "Usage: bootstrap-opsmgr.sh [-i <controllernode1,...>] [-s <storagenode1,...>] [-c <computenode1,...>]"
    echo ""
    echo "export KIBANA_PASSWORD=                            Not applicable unless set"
    exit 1
fi

if [ ! -e scripts/bootstrap-opsmgr.sh ]; then
    echo "This script must be run from the opsmgr directory"
    exit 1
fi

SCRIPTS_DIR=$(dirname $0)
source $SCRIPTS_DIR/process-args.sh

echo "DEPLOY_AIO=$DEPLOY_AIO"
echo "infraNodes=$infraNodes"
echo "allNodes=$allNodes"

echo "Applying patches"

# TODO(luke): Need to apply patches to all controller nodes for opsmgr resiliency

if [ -d diffs ]; then
    push / >/dev/null 2>&1
    for f in diffs/*.patch; do
        patch -N -p1 < $f
    done
    popd >/dev/null 2>&1
fi

echo "Copying opsmgr user variables and secrets to ${TARGET_OSA_DEPLOY}/openstack_deploy"
cp -R predeploy/elk/etc/openstack_deploy ${TARGET_OSA_DEPLOY}
rc=$?
if [ $rc != 0 ]; then
    echo "Failed cp secrets and variables to ${TARGET_OSA_DEPLOY}"
    exit 2
fi

echo "These files may be viewed and edited before they are activated by create-cluster-opsmgr.sh"
