#!/bin/bash
# Swift disk usage monitoring script for Nagios
#
# Authors:
#   Rakesh Patnaik <patsrakesh@gmail.com>
#
# This file is part of nagios-openstack-monitoring
# (https://github.com/rakesh-patnaik/nagios-openstack-monitoring)
#
# nagios-openstack-monitoring is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# nagios-openstack-monitoring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with nagios-openstack-monitoring.  If not, see <http://www.gnu.org/licenses/>.>.

crit_threshold_pct=80

warn_threshold_pct=80

function usage()
{
    echo "Checks swift objectstore usage"
    echo ""
    echo "./check_swift_du.sh"
    echo "\t-h --help"
    echo "\t-c --critical=$crit_threshold_pct"
    echo "\t-w --warning=$warn_threshold_pct"
    echo ""
}

while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage
            exit
            ;;
        -c | --critical)
            crit_threshold_pct=$VALUE
            ;;
        -w | --warning)
            warn_threshold_pct=$VALUE
            ;;
        *)
            echo "ERROR: unknown parameter \"$PARAM\""
            usage
            exit 1
            ;;
    esac
    shift
done

output=$(sudo /usr/bin/timeout -s 9 1s /usr/bin//openstack/venvs/swift-13.1.0/bin/swift-recon -d | egrep 'space used' | grep -o '[0-9]*')

used_space=$(echo $output | awk '{print $1}')

total_space=$(echo $output | awk '{print $2}')

percent_used=$((100*$used_space/total_space))

if [ $percent_used -gt $crit_threshold_pct ]; then
   echo "CRITICAL: Swift ObjectStore used $used_space bytes of available $total_space bytes. Usage: $percent_used%."
   exit 2
elif [  $percent_used -gt $warn_threshold_pct ]; then
   echo "WARNING: Swift ObjectStore used $used_space bytes of available $total_space bytes. Usage: $percent_used%."
   exit 1
else
   echo "OK: Swift ObjectStore used $used_space bytes of available $total_space bytes"
   exit 0
fi
