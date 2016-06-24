#!/bin/bash

# Copyright 2016, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script checks that a particular dashboard is installed in Kibana on 
# a particular ELK host.
#
# DASHBOARD, ELK_IP, and ELASTIC_PORT must be passed from the command line 
# 
# Example to invoke:
# check_for_dashboard.sh -i 9.27.24.69 -e 9200 -d "Log Analyze Dashboard - Logs-From GUI" 
#

# Get the command line options that were passed to the command
source test_options.sh

# Make sure all required options were passed
if [ -z '${DASHBOARD}' ] || [ -z ${ELK_IP} ] || [ -z ${ELASTIC_PORT} ];
then
   echo 
   echo "Dashboard, ELK IP, and Elasticsearch port are required inputs for check_for_dashboard"
   echo 
   echo "${SYNTAX}"
   exit 1
fi
echo "DASHBOARD:   ${DASHBOARD}"
echo "ELK_IP:      ${ELK_IP}"
echo "ELASTIC_PORT:    ${ELASTIC_PORT}" 

# Check for the dashboard
url="http://${ELK_IP}:${ELASTIC_PORT}/.kibana/_search?pretty&q=_type:dashboard"
result=`curl $url --silent | grep "\"${DASHBOARD}\""`

if [ -z "${result}" ];
then
  echo "Dashboard ${DASHBOARD} not installed"
  exit 1
else
  echo "Dashboard ${DASHBOARD} is installed"
  exit 0
fi
