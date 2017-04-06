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

echo "DEPLOY_AIO=$DEPLOY_AIO"
echo "infraNodes=$infraNodes"
echo "allNodes=$allNodes"
echo "GIT_MIRROR=$GIT_MIRROR"

OSA_RELEASE="stable/newton"
OSA_TAG=${OSA_TAG:-"14.1.1"}
OSA_DIR="/opt/openstack-ansible"
OSA_PLAYS="${OSA_DIR}/playbooks"

if [ "$1" == "--help" ]; then
    echo "Usage: bootstrap-kernel.sh"
    echo ""
    echo "export DEPLOY_HARDENING=yes|no                     Default is no"
    echo "export ADMIN_PASSWORD=                             Not applicable unless set"
    exit 1
fi

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

# Apply patches to /opt/openstack-ansible so that bootstrap-ansible.sh
# related patches are applied before bootstrap-ansible.sh is run.
if [ -d $PCLD_DIR/diffs ]; then

    echo "Applying patches to /opt/openstack-ansible"
    pushd / >/dev/null 2>&1

    for f in ${PCLD_DIR}/diffs/opt-openstack-ansible-*.patch; do
        patch -N -p1 < $f
        rc=$?
        if [ $rc != 0 ]; then
            echo "Applying patches to /opt/openstack-ansible failed, rc=$rc"
            echo "Patch $f could not be applied"
            echo "Manual retry procedure:"
            echo "1) fix patch $f"
            echo "2) rm -rf /opt/openstack-ansible"
            echo "3) re-run command"
            exit 1
        fi
    done

    popd >/dev/null 2>&1
fi

# Bootstrap kernel components
if [ ! -d /etc/ansible ]; then
    echo "bootstrap ansible..."
    pushd ${OSA_DIR} >/dev/null 2>&1
    # Bootstrap Ansible
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

