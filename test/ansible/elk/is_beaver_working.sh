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

# This script checks if Beaver is sending logs to logstash on
# a particular ELK host.
#
# ELK_IP, and ELASTIC_PORT and COMPONENT must be passed from the command line
#

source test_options.sh

# Make sure all required options were passed
if [ -z ${ELK_IP} ] || [ -z ${ELASTIC_PORT} ] || [ -z ${COMPONENT} ];
then
   echo
   echo "ELK IP, and Elasticsearch port and Component are required inputs for check_for_dashboard"
   echo
   echo "${SYNTAX}"
   exit 1
fi
echo "ELK_IP:      ${ELK_IP}"
echo "ELASTIC_PORT:    ${ELASTIC_PORT}"
echo "COMPONENT: ${COMPONENT}"

statement="http://${ELK_IP}:${ELASTIC_PORT}/_cat/indices"
output1=`curl --silent $statement`
sleep 5
output2=`curl --silent $statement`

difference=`diff <(echo "$output1") <(echo "$output2")`

difference=`echo "$difference" | grep logstash`

difference=(${difference[@]}) 
logstash_index="${difference[3]}"

statement="http://${ELK_IP}:${ELASTIC_PORT}/${logstash_index}/_search?pretty&fields=file&size=100&q=tags:${COMPONENT}"
output1=`curl --silent $statement | grep total`
result="$output1"

result=(${result[@]})
result="${result[5]}"

result="${result::-1}"

if [ $result -eq 0 ]
then
   echo "Beaver is not sending ${COMPONENT} logs"
   exit 1
else
   echo "Beaver is sending ${COMPONENT} logs"
   exit 0
fi
