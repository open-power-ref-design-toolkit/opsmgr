#!/usr/bin/python
#
#   Copyright 2012 iomart Cloud Services Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import sys
import os
import subprocess
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-w", "--warning", dest="warning",
                  help="threshold for WARNING", default="70", type="int")
parser.add_option("-c", "--critical", dest="critical",
                  help="threshold for CRITICAL", default="80", type="int")

(options, args) = parser.parse_args()

process = subprocess.Popen(["swift-recon", "-d"], stdout=subprocess.PIPE)

# looking for line like
# Disk usage: lowest: 18.02%, highest: 29.2%, avg: 25.8431666667%

for line in process.stdout.readlines():
    if line.startswith("Disk usage: lowest"):
        usage_line_parts = line.split(" ")
	i=0
        for part in usage_line_parts:
            if part=="highest:":
                highest_percent = usage_line_parts[i+1]
                break
            i+=1

        if highest_percent==None:
            print "UNKNOWN : highest percentage could not be located in %s" % line
            sys.exit(3)

        highest = float(highest_percent.split("%")[0])
        if highest>options.critical:
            print "CRITICAL : at least one disk at %d%%" % highest
            sys.exit(2)
        
        if highest>options.warning:
            print "WARNING : at least one disk at %d%%" % highest
            sys.exit(1)
         
        print "OK : %s" % line
        sys.exit(0)


print "UNKNOWN: Disk usage line not found"
sys.exit(3)        
