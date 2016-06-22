#!/bin/bash

# This script processes the common test case command line options
# Source this file in your script to read command line options and set variables

OPTIONS=$*
/bin/echo "Options passed in are ${OPTIONS}"

SYNTAX=$(/bin/cat << EOT
Syntax:
 -x turn on debug
 -d dashboard (enclose in quotes if it contains spaces)
 -i IP address for elk
 -e port for elasticsearch
 -k port for kibana
 -u userid for kibana
 -p password for kibana
EOT
)
while getopts "d:i:e:k:u:p:x" FLAG;
do 
  case ${FLAG} in
    x) export set x ;;
    d) export DASHBOARD=${OPTARG} ;;
    i) export ELK_IP=${OPTARG} ;;
    e) export ELASTIC_PORT=${OPTARG} ;;
    k) export KIBANA_PORT=${OPTARG} ;;
    u) export KIBANA_USER=${OPTARG} ;;
    p) export KIBANA_PW=${OPTARG} ;;
    *) echo "${SYNTAX}" && exit 1 ;;
  esac
done
shift $((OPTIND-1))
INVALID_OPTIONS=$*
[ -n "${INVALID_OPTIONS}" ] && echo "${SYNTAX}" && echo "Invalid options: ${INVALID_OPTIONS}" && exit 1
