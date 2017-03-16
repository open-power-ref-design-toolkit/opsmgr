#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
# Swift dispersion monitoring script for Nagios
#
# Copyright © 2012 eNovance <licensing@enovance.com>
#
# Author: Julien Danjou <julien@danjou.info>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import subprocess
import os
import sys
import json

from swift_commands import SWIFT_DISPERSION_REPORT

STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3
STATE_DEPENDENT=4

p = subprocess.Popen([SWIFT_DISPERSION_REPORT,"-j"],shell=False,stdout=subprocess.PIPE)
report = p.stdout.read()
rep1 = report[report.find("{"):len(report)]
stats = json.loads(rep1)

msgs = []
state = STATE_OK

# type_ is either "objects", "container"
for type_, values in stats.iteritems():

    msgs.append("%.2f%% %ss found" % (values['pct_found'], type_))

    if ("missing_1" in values) and values['missing_one'] > 0:
        msgs.append("%d %ss missing one copy" % (values['missing_one'], type_))
        state = max(state, STATE_WARNING)

    if ("missing_2" in values) and values['missing_two'] > 0:
        msgs.append("%d %ss missing two copies" % (values['missing_two'], type_))
        state = max(state, STATE_WARNING)

    if ("missing_all" in values) and values['missing_all'] > 0:
        msgs.append("%d %ss missing ALL copies" % (values['missing_all'], type_))
        state = max(state, STATE_CRITICAL)

print ", ".join(msgs)
sys.exit(state)
