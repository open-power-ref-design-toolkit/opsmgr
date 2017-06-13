#!/usr/bin/python

import sys
import os
import subprocess

from swift_commands import SWIFT_ORPHANS

p = subprocess.Popen([SWIFT_ORPHANS, "-a 1"], stdout=subprocess.PIPE)

ret = 0
lines = []
count = 0
for line in p.stdout.readlines():
    if line:
        lines.append(line.strip())
        ret = 2
        count = count + 1

if ret == 0:
    output = "OK : No Swift Orphans found"
else:
    output = "CRITICAL : %d Swift Orphans found" % count

print output
sys.exit(ret)
        
