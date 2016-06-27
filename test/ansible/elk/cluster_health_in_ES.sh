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

# This script checks the Health status of the cluster in Elastic Search on
# a particular ELK host.
#
# ELK_IP, and ELASTIC_PORT must be passed from the command line
#

source test_options.sh

# Make sure all required options were passed
if [ -z ${ELK_IP} ] || [ -z ${ELASTIC_PORT} ];
then
   echo
   echo "ELK IP, and Elasticsearch port are required inputs for check_for_dashboard"
   echo
   echo "${SYNTAX}"
   exit 1
fi
echo "ELK_IP:      ${ELK_IP}"
echo "ELASTIC_PORT:    ${ELASTIC_PORT}"

statement="http://${ELK_IP}:${ELASTIC_PORT}/_cluster/health?pretty=true"
result=`curl --silent $statement | grep status`

if [[ "${result}" == *"red"* ]];
then
  echo "The cluster health status in Elastic Search is red"
  exit 1
else
  echo "The cluster health status in Elastic Search is not red"
  exit 0
fi
