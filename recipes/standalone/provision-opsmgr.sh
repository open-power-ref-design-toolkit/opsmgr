#!/usr/bin/env bash
#
# Copyright 2017 IBM Corp.
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

# Note help text assumes the end user is invoking this script as Genesis is fully automated
# Default value (yes) is reversed for Genesis

# Get the full path to the scripts directory
SCRIPTS_DIR=$(dirname $0)
SCRIPTS_DIR=$(readlink -ne $SCRIPTS_DIR)
$SCRIPTS_DIR/setup-env.sh

ARGS=$@
source $SCRIPTS_DIR/args.sh

# Sets opsmgr variables
OPSMGR_DIR="${SCRIPTS_DIR}/../.."
: ${OPSMGR_RECIPE:=standalone}
export OPSMGR_RECIPE
RECIPE_DIR="${OPSMGR_DIR}/recipes/${OPSMGR_RECIPE}"
OPSMGR_PRL="${RECIPE_DIR}/profile"

# Configure opsmgr recipes
pushd ${RECIPE_DIR} >/dev/null 2>&1
echo "Invoking run.sh in recipe"
rm -rf *.log .facts/
mkdir profile
./run.sh
rc=$?
if [ $rc != 0 ]; then
    echo "Failed to run opsmgr recipe run.sh, rc=$rc"
    exit 6
fi
popd >/dev/null 2>&1

# Setup opsmgr
pushd ${OPSMGR_DIR}/playbooks >/dev/null 2>&1
echo "Invoking playbook setup.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory setup.yml
rc=$?
if [ $rc != 0 ]; then
	echo "Failed to execute playbooks/setup.yml, rc=$rc"
        exit 7
fi
popd >/dev/null 2>&1

# Configure opsmgr hosts
pushd ${OPSMGR_DIR}/playbooks >/dev/null 2>&1
echo "Invoking playbook hosts.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory hosts.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/hosts.yml, rc=$rc"
        exit 8
fi
popd >/dev/null 2>&1

# Configure opsmgr control plane
pushd ${OPSMGR_DIR}/playbooks >/dev/null 2>&1
echo "Invoking playbook site.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR patch_ui=true" -i $OPSMGR_PRL/inventory site.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/site.yml, rc=$rc"
        exit 9
fi
popd >/dev/null 2>&1

# Configure opsmgr targets
pushd ${OPSMGR_DIR}/playbooks >/dev/null 2>&1
echo "Invoking playbook targets.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory targets.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/targets.yml, rc=$rc"
        exit 10
fi
popd >/dev/null 2>&1

# Customize opsmgr 
pushd ${OPSMGR_DIR}/playbooks >/dev/null 2>&1
echo "Invoking playbook customize.yml from the opsmgr/playbooks directory"
ansible-playbook -e "opsmgr_dir=$OPSMGR_DIR" -i $OPSMGR_PRL/inventory customize.yml
rc=$?
if [ $rc != 0 ]; then
        echo "Failed to execute playbooks/customize.yml, rc=$rc"
        exit 11
fi
popd >/dev/null 2>&1

$SCRIPTS_DIR/unset-env.sh

