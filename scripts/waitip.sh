#!/bin/bash
ip=""
if=$1
until [[ $ip =~ [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} ]]; do
  /bin/sleep 1
  ip=$(
    /sbin/ifconfig $if |
    /usr/bin/awk -F'(inet add?r:| +|:)' '/inet add?r/{print $3}'
  )
done
/bin/sleep 3

