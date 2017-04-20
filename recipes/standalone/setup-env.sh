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

if [[ $EUID -eq 0 ]]; then
    ulimit -n 100000
    # work-around for when genesis runs in the same node as osa
    # we need to copy the genesis key to root's id_rsa so that passwordless
    # sudo works for osa
    if [ -f ~/.ssh/id_rsa_ansible-generated ]; then
        if [ -f ~root/.ssh/id_rsa ]; then
            mv -f ~root/.ssh/id_rsa ~root/.ssh/id_rsa.bak
        fi
        if [ -f ~root/.ssh/id_rsa.pub ]; then
            mv -f ~root/.ssh/id_rsa.pub ~root/.ssh/id_rsa.pub.bak
        fi
        cp -f ~/.ssh/id_rsa_ansible-generated ~root/.ssh/id_rsa
        cp -f ~/.ssh/id_rsa_ansible-generated.pub ~root/.ssh/id_rsa.pub
    fi
else
    # work-around for when genesis runs in the same node as opsmgr
    # we need to copy the genesis key to id_rsa so that passwordless
    # sudo works for opsmgr
    if [ -f ~/.ssh/id_rsa_ansible-generated ]; then
        if [ -f ~/.ssh/id_rsa ]; then
            mv -f ~/.ssh/id_rsa ~/.ssh/id_rsa.bak
        fi
        if [ -f ~/.ssh/id_rsa.pub ]; then
            mv -f ~/.ssh/id_rsa.pub ~/.ssh/id_rsa.pub.bak
        fi
        cp -f ~/.ssh/id_rsa_ansible-generated ~/.ssh/id_rsa
        cp -f ~/.ssh/id_rsa_ansible-generated.pub ~/.ssh/id_rsa.pub
    fi
fi
