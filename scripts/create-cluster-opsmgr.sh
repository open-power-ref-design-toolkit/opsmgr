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
    echo "Usage: create-cluster-opsmgr.sh"
    exit 1
fi

if [ ! -e scripts/create-cluster-opsmgr.sh ]; then
    echo "This script must be run from the opsmgr directory"
    exit 1
fi

PCLD_DIR=`pwd`

SCRIPTS_DIR=$(dirname $0)
source $SCRIPTS_DIR/process-args.sh

pushd $PCLD_DIR/recipes/privatecloud-newton >/dev/null 2>&1
echo "Invoking run.sh in privatecloud-newton"
mkdir profile
./run.sh
rc=$?
if [ $rc != 0 ]; then
    echo "Failed recipes/privatecloud-newton/run.sh, rc=$rc"
    exit 6
fi
popd >/dev/null 2>&1

pushd $PCLD_DIR/playbooks >/dev/null 2>&1
export OPSMGR_RECIPE=privatecloud-newton
export OPSMGR_DIR=`pwd`/..
export OPSMGR_PRL=$OPSMGR_DIR/recipes/$OPSMGR_RECIPE/profile
rm -rf *.log .facts/

# Execute the final steps of installing Operations Manager 
echo "Invoking playbook setup.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory setup.yml
rc=$?
if [ $rc != 0 ]; then
	echo "Failed to execute playbooks/setup.yml, rc=$rc"
        exit 7
fi

echo "Invoking playbook hosts.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory hosts.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/hosts.yml, rc=$rc"
        exit 8
fi

echo "Invoking playbook site.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory site.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/site.yml, rc=$rc"
        exit 9
fi

echo "Invoking playbook targets.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory targets.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/targets.yml, rc=$rc"
        exit 10 
fi
popd >/dev/null 2>&1
