#!/bin/sh
cat /etc/openstack-release | grep "DISTRIB_RELEASE" | awk -F '[=&]' '{print $2}'
