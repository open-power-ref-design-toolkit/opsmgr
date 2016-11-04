#!/usr/bin/python
#
# Nagios plugin to check Ceph cluster state
#
# This plugin check ceph health, number of OSDs UP, number of MONs UP
# and PGs states to determine Ceph cluster status.
#
#  Usage: check_ceph_status [options]
#
#  Options:
#    -h, --help            show this help message and exit
#    -d, --debug
#    -b BIN, --bin=BIN     Ceph binary (default : /usr/bin/ceph)
#    --conf=CONF           Ceph configuration file
#    -m MON, --mon=MON     Ceph monitor address[:port]
#    -i ID, --id=ID        Ceph client id
#    -k KEYRING, --keyring=KEYRING
#                          Ceph client keyring file
#    -w WARNLOSTOSD, --warning-lost-osd=WARNLOSTOSD
#                          Warning number of non-up OSDs (default : 1)
#    -c CRITLOSTOSD, --critical-lost-osd=CRITLOSTOSD
#                          Critical number of non-up OSDs (default : 2)
#    -W WARNLOSTMON, --warning-lost-mon=WARNLOSTMON
#                          Warning number of non-up MONs (default : 1)
#    -C CRITLOSTMON, --critical-lost-mon=CRITLOSTMON
#                          Critical number of non-up MONs (default : 2)
#
# Copyright (c) 2013 Benjamin Renard <brenard@zionetrix.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import sys,os,json,subprocess,re
from optparse import OptionParser

# default ceph values
CEPH_COMMAND = '/usr/bin/ceph'
WARN_LOST_OSD = 1
CRIT_LOST_OSD = 2
WARN_LOST_MON = 1
CRIT_LOST_MON = 2

# nagios exit code
STATUS = {
	'OK': 0,
	'WARNING': 1,
	'CRITICAL': 2,
	'UNKNOWN': 3
}

parser = OptionParser()
parser.add_option('-d',
                  '--debug',
                  action="store_true",
                  dest="debug",
                  default=False)

parser.add_option('-b',
                  '--bin',
                  action="store",
                  dest="bin",
                  help="Ceph binary (default : %s)" % CEPH_COMMAND,
                  type='string',
                  default=CEPH_COMMAND)

parser.add_option('--conf',
                  action="store",
                  dest="conf",
                  help="Ceph configuration file",
                  type='string',
                  default=None)

parser.add_option('-m',
                  '--mon',
                  action="store",
                  dest="mon",
                  help="Ceph monitor address[:port]",
                  type='string',
                  default=None)

parser.add_option('-i',
                  '--id',
                  action="store",
                  dest="id",
                  help="Ceph client id",
                  type='string',
                  default=None)

parser.add_option('-k',
                  '--keyring',
                  action="store",
                  dest="keyring",
                  help="Ceph client keyring file",
                  type='string',
                  default=None)

parser.add_option('-w',
                  '--warning-lost-osd',
                  action="store",
                  dest="warnlostosd",
                  help="Warning number of non-up OSDs (default : %s)" % WARN_LOST_OSD,
                  type='int',
                  default=WARN_LOST_OSD)

parser.add_option('-c',
                  '--critical-lost-osd',
                  action="store",
                  dest="critlostosd",
                  help="Critical number of non-up OSDs (default : %s)" % CRIT_LOST_OSD,
                  type='int',
                  default=CRIT_LOST_OSD)

parser.add_option('-W',
                  '--warning-lost-mon',
                  action="store",
                  dest="warnlostmon",
                  help="Warning number of non-up MONs (default : %s)" % WARN_LOST_MON,
                  type='int',
                  default=WARN_LOST_MON)

parser.add_option('-C',
                  '--critical-lost-mon',
                  action="store",
                  dest="critlostmon",
                  help="Critical number of non-up MONs (default : %s)" % CRIT_LOST_MON,
                  type='int',
                  default=CRIT_LOST_MON)

(options, args) = parser.parse_args()

 # validate args
if not os.path.exists(options.bin):
    print "ERROR: ceph executable '%s' doesn't exist" % options.bin
    sys.exit(STATUS['UNKNOWN'])

if options.conf and not os.path.exists(options.conf):
    print "ERROR: ceph conf file '%s' doesn't exist" % options.conf
    sys.exit(STATUS['UNKNOWN'])

if options.keyring and not os.path.exists(options.keyring):
    print "ERROR: keyring file '%s' doesn't exist" % options.keyring
    sys.exit(STATUS['UNKNOWN'])

# build command
ceph_cmd = [options.bin]
if options.mon:
    ceph_cmd.append('-m')
    ceph_cmd.append(options.mon)
if options.conf:
    ceph_cmd.append('-c')
    ceph_cmd.append(options.conf)
if options.id:
    ceph_cmd.append('--id')
    ceph_cmd.append(options.id)
if options.keyring:
    ceph_cmd.append('--keyring')
    ceph_cmd.append(options.keyring)
ceph_cmd.append('status')
ceph_cmd.append('--format=json')

# exec command
p = subprocess.Popen(ceph_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
output, err = p.communicate()

if output:
	data=json.loads(output)

	status='OK'

	health=data['health']['overall_status']
	if health=='HEALTH_WARN':
		status='WARNING'
	elif health=='HEALTH_CRIT':
		status='CRITICAL'

	total_mon=len(data['monmap']['mons'])
	#total_mon_up=len(data['health']['timechecks']['mons'])
	total_mon_up=len(data['health']['timechecks'])

	num_lost_mon=total_mon-total_mon_up
	if num_lost_mon==0:
		monstate="(MONs UP : %s/%s)" % (total_mon_up,total_mon)
	else:
		monstate="%s MONs down (MONs UP : %s/%s)" % (num_lost_mon,total_mon_up,total_mon)
		if num_lost_mon >= options.critlostmon:
			status='CRITICAL'
		elif num_lost_mon >= options.warnlostmon and status!='CRITICAL':
			status='WARNING'

	total_osd=data['osdmap']['osdmap']['num_osds']
	total_osd_up=data['osdmap']['osdmap']['num_up_osds']

	num_lost_osd=total_osd-total_osd_up

	if num_lost_osd>=options.critlostosd:
		status='CRITICAL'
	elif num_lost_osd>=options.warnlostosd and status!='CRITICAL':
		status='WARNING'

	total_pg=data['pgmap']['num_pgs']
	pgstate=""
	for st in data['pgmap']['pgs_by_state']:
		if re.search('(down|inconsistent|imcomplete|stale)',st['state_name'],re.IGNORECASE):
			status='CRITICAL'
			pgstate="%s / %s PGs %s" % (pgstate,st['count'],st['state_name'])
		elif re.search('(replay|degraded|repair|recovering|backfill)',st['state_name'],re.IGNORECASE):
			if status!='CRITICAL':
				status="WARNING"
			pgstate="%s / %s PGs %s" % (pgstate,st['count'],st['state_name'])
		elif st['state_name']=="active+clean":
			pgstate="%s / %s/%s PGs active+clean" % (pgstate,st['count'],total_pg)

	msg="%s : %s%s %s" % (status,health,pgstate,monstate)


	if num_lost_osd==0:
		print "%s (OSDs UP : %s/%s)" % (msg,total_osd_up,total_osd)
	else:
		print "%s / %s OSDs down (OSDs UP : %s/%s)" % (msg,num_lost_osd,total_osd_up,total_osd)
	sys.exit(STATUS[status])
else:
	print "UNKNOWN : fail to execute ceph status command"
	sys.exit(STATUS['UNKNOWN'])
