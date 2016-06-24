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

# This script processes the common test case command line options
# Source this file in your script to read command line options and set variables

source /home/ubuntu/development/opsmgr/test/ansible/elk/test_options.sh

statement="http://${ELK_IP}:${ELASTIC_PORT}/_cat/indices"
output1=`curl --silent $statement`
sleep 5
output2=`curl --silent $statement`

difference=`diff <(echo "$output1") <(echo "$output2")`

difference=`echo "$difference" | grep logstash`

difference=(${difference[@]})
logstash_index="${difference[3]}"

count="0"
component=""

while [ $count -lt 7 ]
do

   case "$count" in
   "0")
       component="nova"
       ;;
   "1")
       component="neutron"
       ;;
   "2")
       component="heat"
       ;;
   "3")
       component="cinder"
       ;;
   "4")
       component="keystone"
       ;;
   "5")
       component="glance"
       ;;
   "6")
       component="horizon"
       ;;
   *)
       ;;
   esac

   statement="http://${ELK_IP}:${ELASTIC_PORT}/${logstash_index}/_search?pretty&fields=file&size=100&q=tags:${component}" 
   output1=`curl --silent $statement`
   if [ -z "$output1" ]
   then
      echo "Beaver is not sending $component logs"
   else
      echo "Beaver is sending $component logs"
   fi

count=$[$count+1]
done
