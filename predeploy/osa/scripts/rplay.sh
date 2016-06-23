#!/bin/bash
pushd /tmp/osa
/usr/local/bin/openstack-ansible remote.yml > remote.log 2>&1
popd
