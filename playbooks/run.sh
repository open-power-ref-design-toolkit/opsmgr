#!/bin/sh
mkdir -p /etc/opsmgr
cp -f ./.spec /etc/opsmgr
rm -f ansible.log
ansible-playbook -i inventory --sudo site.yml
