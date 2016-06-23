#!/bin/bash

# This script checks that a particular dashboard is installed in Kibana on 
# a particular ELK host.
#
# DASHBOARD and  ELK_IP must be passed from the command line
#
# Example to invoke:
# check_for_dashboard.sh -i 9.27.24.69 -d "Log Analyze Dashboard - Logs-From GUI" 
#

# Get the command line options that were passed to the command
source test_options.sh

# Make sure all required options were passed
if [ -z '${DASHBOARD}' ] || [ -z ${ELK_IP} ];
then
   echo "Dashboard and elk ip are required inputs for check_for_dashboard"
   echo "${SYNTAX}"
   exit 1
fi
echo "DASHBOARD:   ${DASHBOARD}"
echo "ELK_IP:      ${ELK_IP}"

# Check for the dashboard
url="http://${ELK_IP}:9200/.kibana/_search?pretty&q=_type:dashboard"
result=`curl $url --silent | grep "${DASHBOARD}"`

if [ -z '${result}' ];
then
  echo "Dashboard ${DASHBOARD} not installed"
  exit 1
else
  echo "Dashboard ${DASHBOARD} is installed"
  exit 0
fi
