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

shopt -s nullglob
set -o pipefail

ulimit -n 100000

function git-clone {
    GIT_URL=$1
    DESIRED_TAG=$2
    TARGET_DIR=$3
    echo "GIT_URL=$GIT_URL"
    echo "DESIRED_TAG=$DESIRED_TAG"
    pushd . >/dev/null 2>&1
    if [ -d $TARGET_DIR ]; then
        cd $TARGET_DIR
        TAG=`git symbolic-ref -q --short HEAD || git describe --tags --exact-match`
        if [ "$TAG" == "$DESIRED_TAG" ]; then
            git pull
            rc=$?
        else
            git checkout $DESIRED_TAG
            rc=$?
        fi
    else
        git clone $GIT_URL $TARGET_DIR
        rc=$?
        if [ $rc == 0 ]; then
            cd $TARGET_DIR
            git checkout $DESIRED_TAG
            rc=$?
        fi
    fi
    popd >/dev/null 2>&1
    if [ $rc != 0 ]; then
        echo "Failed git $TARGET_DIR, rc=$rc"
        exit 3
    fi
}

function set_passwd {
    FILE=$1
    KEY=$2
    VALUE=$3
    if [ ! -z "$VALUE" ]; then
        PATTERN=`grep $KEY $FILE`
        if [ $? == 0 ]; then
            PASSWORD="${PATTERN##*:}"          # Delete everything before ':'
            PASSWORD="${PASSWORD// /}"         # Delete all blanks.  There is no newline
            if [ -z "$PASSWORD" ]; then
                sed -i "s/^$KEY:.*/$KEY: ${VALUE}/" $FILE
            fi
        fi
    fi
}

export ANSIBLE_PARAMETERS=${ANSIBLE_PARAMETERS:-""}
export ANSIBLE_FORCE_COLOR=${ANSIBLE_FORCE_COLOR:-"true"}
export FORKS=${FORKS:-$(grep -c ^processor /proc/cpuinfo)}
export BOOTSTRAP_OPTS=${BOOTSTRAP_OPTS:-""}

function run_ansible {
    openstack-ansible ${ANSIBLE_PARAMETERS} --forks ${FORKS} $@
}

# This inventory is tied to manufacturing
GENESIS_INVENTORY="/var/oprc/inventory.yml"

# Reduce list to unique items
function mkListsUnique {
    if [[ $# -eq 0 ]]; then
        uniqueList=""
    else
        node_array=($@)
        uniqueList=`echo "${node_array[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '`
    fi
}

if [[ $EUID -ne 0 ]]; then
    echo "This script must run as root."
    exit 1
fi

# These command line parameters are not specified if the inventory is generated by Genesis (ie. manufacturing)
infraNodes=""
storageNodes=""
computeNodes=""
OPTIND=1
while getopts "i:c:s:" opt; do
    case "$opt" in
    i)  infraNodes=${OPTARG//,/ }       # {var//,/ } replaces all commas in the list with blanks
        ;;
    s)  storageNodes=${OPTARG//,/ }
        ;;
    c)  computeNodes=${OPTARG//,/ }
        ;;
    esac
done
shift $((OPTIND-1))                    # Now reference remaining arguments with $@, $1, $2, ...

TARGET_OSA_DEPLOY="${1:-/etc}"         # Caller defines target osa deploy directory if arg1 is specified

mkListsUnique $infraNodes $storageNodes $computeNodes
allNodes=$uniqueList

if [ -r $GENESIS_INVENTORY ]; then
    # End user is not invoking commands.  Genesis process sets policy
    if [ -z "$DEPLOY_CEPH" ]; then
        DEPLOY_CEPH=yes
    fi
    if [ -z "$DEPLOY_OPSMGR" ]; then
        DEPLOY_OPSMGR=yes
    fi
    DEPLOY_AIO=no
elif [ "$infraNodes" == "" ]; then
    DEPLOY_AIO=yes
else
    infraArray=( $infraNodes )
    cnt=${#infraArray[@]}
    if [ $cnt -gt 1 ]; then
        DEPLOY_AIO=no
    else
        DEPLOY_AIO=yes
    fi
fi
