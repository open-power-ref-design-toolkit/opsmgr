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

# Note help text assumes the end user is invoking this script as Genesis is fully automated
# Default value (yes) is reversed for Genesis

if [ "$1" == "--help" ]; then
    echo "Usage: create-cluster-min.sh"
    echo ""
    echo "export DEPLOY_OPSMGR=yes|no                        Default is no"
    echo "export DEPLOY_HARDENING=yes|no                     Default is no"
    echo "export DEPLOY_TEMPEST=yes|no                       Default is no"
    echo "export ADMIN_PASSWORD=                             Not applicable unless set"
    exit 1
fi

if [ ! -e scripts/bootstrap-cluster-min.sh ]; then
    echo "This script must be run in root directory of the project.  ie. /root/opsmgr"
    exit 1
fi
PCLD_DIR=`pwd`

# Save command arguments as source script parses command arguments using optind
ARGS=$@
source scripts/process-args.sh

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

# Configure opsmgr - ELK, Nagios, and Horizon extensions
echo "Invoking scripts/create-cluster-opsmgr.sh"
scripts/create-cluster-opsmgr.sh $ARGS
rc=$?
if [ $rc != 0 ]; then
    echo "Failed scripts/create-cluster-opsmgr.sh, rc=$rc"
    exit 6
fi
popd >/dev/null 2>&1
