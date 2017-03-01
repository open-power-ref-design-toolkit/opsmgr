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
SCRIPTS_DIR=$(dirname $0)
# Get the full path to the scripts directory
SCRIPTS_DIR=$(readlink -ne $SCRIPTS_DIR)
source $SCRIPTS_DIR/process-args.sh

echo "DEPLOY_AIO=$DEPLOY_AIO"
echo "infraNodes=$infraNodes"
echo "allNodes=$allNodes"
echo "GIT_MIRROR=$GIT_MIRROR"

OSA_RELEASE="stable/newton"
OSA_TAG=${OSA_TAG:-"14.0.8"}
OSA_DIR="/opt/openstack-ansible"
OSA_PLAYS="${OSA_DIR}/playbooks"

if [ "$1" == "--help" ]; then
    echo "Usage: bootstrap-cluster-min.sh"
    echo ""
    echo "export DEPLOY_HARDENING=yes|no                     Default is no"
    echo "export ADMIN_PASSWORD=                             Not applicable unless set"
    exit 1
fi

if [ ! -e scripts/bootstrap-cluster-min.sh ]; then
    echo "This script must be run in root directory of the project.  ie. /root/opsmgr"
    exit 1
fi
PCLD_DIR=`pwd`

# Checkout the openstack-ansible repository
INSTALL=False
if [ ! -d /opt/openstack-ansible ]; then
    echo "Installing openstack-ansible..."
    git clone https://github.com/openstack/openstack-ansible ${OSA_DIR}
    if [ $? != 0 ]; then
        echo "Manual retry procedure:"
        echo "1) fix root cause of error if known"
        echo "2) rm -rf /opt/openstack-ansible"
        echo "3) re-run command"
        exit 1
    fi
    pushd ${OSA_DIR} >/dev/null 2>&1
    git checkout ${OSA_RELEASE}
    if [ $? != 0 ]; then
        exit 1
    fi
    git checkout ${OSA_TAG}
    if [ $? != 0 ]; then
        exit 1
    fi
    popd >/dev/null 2>&1
    # An openstack-ansible script is invoked below to install ansible
    rm -rf /etc/ansible
    INSTALL=True
fi

# Bootstrap ansible
if [ ! -d /etc/ansible ]; then
    echo "bootstrap ansible..."
    pushd ${OSA_DIR} >/dev/null 2>&1
    scripts/bootstrap-ansible.sh
    rc=$?
    if [ $rc != 0 ]; then
        echo "scripts/bootstrap-ansible.sh failed, rc=$rc"
        echo "Manual retry procedure:"
        echo "1) fix root cause of error if known"
        echo "2) rm -rf /etc/ansible; rm -rf /opt/ansible-runtime"        
        echo "3) re-run command"
        exit 1
    fi

    # Bootstrap AIO
    scripts/bootstrap-aio.sh
    rc=$?
    if [ $rc != 0 ]; then
        echo "scripts/bootstrap-aio.sh failed, rc=$rc"
        echo "Manual retry procedure:"
        echo "1) fix root cause of error if known"
        echo "2) rm -rf /etc/ansible; rm -rf /opt/ansible-runtime"        
        echo "3) re-run command"
        exit 1
    fi

    popd >/dev/null 2>&1
    INSTALL=True
fi

# Bootstrap opsmgr
echo "Invoking scripts/bootstrap-opsmgr.sh"
scripts/bootstrap-opsmgr.sh $ARGS
rc=$?
if [ $rc != 0 ]; then
    echo "Scripts/bootstrap-opsmgr.sh failed, rc=$rc"
    echo "You may want to continue manually.  cd opsmgr; ./scripts/bootstrap-opsmgr.sh"
    exit 5
fi

# Execute stdc.sh - this removes the configuration files not needed for
# an OpenStack minimal install
scripts/stdc.sh
rc=$?
if [ $rc != 0 ]; then
    echo "Failed running scripts/stdc.sh rc=$rc"
    exit 6
fi
