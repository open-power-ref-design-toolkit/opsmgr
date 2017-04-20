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

CURRENT_DIR=$(dirname $0)
SCRIPTS_DIR=$(readlink -ne $CURRENT_DIR)
$SCRIPTS_DIR/setup-env.sh

# Checkout the openstack-ansible repository
if [ -d /opt/openstack-ansible ]; then

    # Move to the playbooks directory.
    pushd /opt/openstack-ansible/playbooks >/dev/null 2>&1

    echo "force_containers_destroy: true" >> /etc/openstack_deploy/user_clean.yml
    echo "force_containers_data_destroy: true" >> /etc/openstack_deploy/user_clean.yml

    # Destroy all of the running containers.
    openstack-ansible lxc-containers-destroy.yml

    popd >/dev/null 2>&1

    # On the host stop all of the services that run locally and not
    # within a container.
    for i in \
           $(ls /etc/init \
             | grep -e "nova\|swift\|neutron\|cinder" \
             | awk -F'.' '{print $1}'); do \
        service $i stop; \
    done

    # Uninstall the core services that were installed.
    for i in $(pip freeze | grep -e "nova\|neutron\|keystone\|swift\|cinder"); do \
        pip uninstall -y $i; done

    # Remove crusty directories.
    rm -rf /openstack /etc/{neutron,nova,swift,cinder} \
             /var/log/{neutron,nova,swift,cinder}

    # Remove the pip configuration files on the host
    rm -rf /root/.pip

    # Remove the apt package manager proxy
    rm -f /etc/apt/apt.conf.d/00apt-cacher-proxy

    rm -rf /etc/ansible
    rm -rf /etc/openstack_deploy
    rm -rf /opt/openstack-ansible

    lxc-stop -qn ubuntu-xenial-ppc64el
    lxc-destroy -fqn ubuntu-xenial-ppc64el
fi

$SCRIPTS_DIR/unset-env.sh

