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
ARGS=$@
source $SCRIPTS_DIR/args.sh

# Configure openstack-ansible
pushd /opt/openstack-ansible > /dev/null 2>&1
echo "Invoking run-playbooks.sh"
scripts/run-playbooks.sh
rc=$?
if [ $rc != 0 ]; then
    echo "Failed scripts/run-playbooks.sh, rc=$rc"
    exit 4
fi
popd >/dev/null 2>&1

