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

from swift_commands import SWIFT_RECON

process = subprocess.Popen([SWIFT_RECON, "-u"], stdout=subprocess.PIPE)

statuscode = 0
errors = []
count = 0
for line in process.stdout.readlines():
    if line.startswith("Not mounted"):
        errors.append(line.strip())
        statuscode = 2
        status = "CRITICAL"
        count = count + 1

if statuscode==0:
    print "OK : All drives mounted"
    sys.exit(0)
else:
    output = "CRITICAL : %d drives unmounted" % count
#    for error in errors:
#        output = output + error + " "
    print output
    sys.exit(2)
        
