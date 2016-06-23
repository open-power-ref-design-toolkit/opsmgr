#!/bin/bash
pushd playbooks
ansible-playbook -kK -i localhost, -e '{ "ssh_hosts": ["localhost"] }' local.yml
popd


