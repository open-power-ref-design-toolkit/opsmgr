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

OPTIONS=$*
/bin/echo
/bin/echo "Options passed in are ${OPTIONS}"

SYNTAX=$(/bin/cat << EOT
Syntax:
 -x turn on debug
 -d dashboard (enclose in quotes if it contains spaces)
 -i IP address for elk
 -e port for elasticsearch
 -c Component
EOT
)
while getopts "d:i:e:c:x" FLAG;
do 
  case ${FLAG} in
    x) set -x ;;
    d) export DASHBOARD=${OPTARG} ;;
    i) export ELK_IP=${OPTARG} ;;
    e) export ELASTIC_PORT=${OPTARG} ;;
    c) export COMPONENT=${OPTARG} ;;
    *) echo "${SYNTAX}" && exit 1 ;;
  esac
done
shift $((OPTIND-1))
INVALID_OPTIONS=$*
[ -n "${INVALID_OPTIONS}" ] && echo "${SYNTAX}" && echo "Invalid options: ${INVALID_OPTIONS}" && exit 1
