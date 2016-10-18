#!/usr/bin/python

import sys
import os
import subprocess
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interval", dest="interval",
                  help="choice for average internal [1m, 5m, 15m]", default="1m", type="string")
parser.add_option("-w", "--warning", dest="warning",
                  help="threshold for WARNING", default="75", type="int")
parser.add_option("-c", "--critical", dest="critical",
                  help="threshold for CRITICAL", default="90", type="int")

(options, args) = parser.parse_args()

process = subprocess.Popen(["/openstack/venvs/swift-13.1.0/bin/swift-recon", "-l"], stdout=subprocess.PIPE)

# looking for line like
#[5m_load_avg] low: 14, high: 22, avg: 18.0, total: 108, Failed: 0.0%, no_result: 0, reported: 6
#[15m_load_avg] low: 14, high: 21, avg: 17.6, total: 105, Failed: 0.0%, no_result: 0, reported: 6
#[1m_load_avg] low: 14, high: 26, avg: 19.8, total: 118, Failed: 0.0%, no_result: 0, reported: 6

for line in process.stdout.readlines():
    if line.startswith("[" + options.interval + "_load_avg] low: "):
        usage_line_parts = line.split(" ")
	i=0
        for part in usage_line_parts:
            if part=="high:":
                load = usage_line_parts[i+1]
                break
            i+=1

        if load==None:
            print "UNKNOWN : swift high load average could not be located in %s" % line
            sys.exit(3)

        high = float(load.split(",")[0])
        if high>options.critical:
            print "CRITICAL : swift high load average at %d%%" % high
            sys.exit(2)
        
        if high>options.warning:
            print "WARNING : swift high load average at %d%%" % high
            sys.exit(1)
         
        print "OK : %s" % line
        sys.exit(0)


print "UNKNOWN: load average line not found"
sys.exit(3)

