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

SCRIPTS_DIR=$(dirname $0)
source $SCRIPTS_DIR/process-args.sh

### calls main OpsMgr installation and Nagios integration playbooks
scripts/ops.sh
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running scripts/ops.sh rc=$rc"
    exit 3
fi

