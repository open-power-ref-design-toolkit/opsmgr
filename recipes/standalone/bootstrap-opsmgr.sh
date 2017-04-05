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

# Get the full path to the scripts directory
SCRIPTS_DIR=$(dirname $0)
SCRIPTS_DIR=$(readlink -ne $SCRIPTS_DIR)
ARGS=$@
source $SCRIPTS_DIR/args.sh

# Sets opsmgr variables
OPSMGR_DIR="${SCRIPTS_DIR}/../.."
#The following sets OPSMGR_RECIPE if not already set
: ${OPSMGR_RECIPE:=standalone}
export OPSMGR_RECIPE
RECIPE_DIR="${OPSMGR_DIR}/recipes/${OPSMGR_RECIPE}"
OPSMGR_PRL="${RECIPE_DIR}/profile"

# Apply patches to opsmgr if "diffs" directory exists
echo "Applying patches"
if [ -d $OPSMGR_DIR/diffs ]; then
    pushd / >/dev/null 2>&1
    for f in $OPSMGR_DIR/diffs/*.patch; do
        patch -N -p1 < $f
    done
    popd >/dev/null 2>&1
fi

# Bootstrap opsmgr
if [ ! -d ${OPSMGR_DIR}/recipes ]; then
    echo "bootstrap opsmgr..."
    pushd ${OPSMGR_DIR}/recipes >/dev/null 2>&1
    ansible-playbook -e "opsmgr_lib=../lib" -i $OPSMGR_PRL/inventory setup.yml
    rc=$?
    if [ $rc != 0 ]; then
        echo "Failed running opsmgr recipes/setup.yml, rc=$rc"
        exit 2
    fi
    ansible-playbook updatessh.yml
    rc=$?
    if [ $rc != 0 ]; then
        echo "Failed to update /etc/ssh/sshd_config and/or /etc/ssh/ssh_config, rc=$rc"
        exit 3
    fi
    popd >/dev/null 2>&1
    INSTALL=True
fi

