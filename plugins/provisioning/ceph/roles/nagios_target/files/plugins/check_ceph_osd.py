#!/usr/bin/env python
#
#  Copyright (c) 2013 Catalyst IT http://www.catalyst.net.nz
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse
import os
import re
import subprocess
import sys
import socket

__version__ = '1.5.0'

# default ceph values
CEPH_COMMAND = '/usr/bin/ceph'

# nagios exit code
STATUS_OK = 0
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_UNKNOWN = 3

def main():

  # parse args
  parser = argparse.ArgumentParser(description="'ceph osd' nagios plugin.")
  parser.add_argument('-e','--exe', help='ceph executable [%s]' % CEPH_COMMAND)
  parser.add_argument('-c','--conf', help='alternative ceph conf file')
  parser.add_argument('-m','--monaddress', help='ceph monitor address[:port]')
  parser.add_argument('-i','--id', help='ceph client id')
  parser.add_argument('-k','--keyring', help='ceph client keyring file')
  parser.add_argument('-V','--version', help='show version and exit', action='store_true')
  parser.add_argument('-H','--host', help='osd host', required=True)
  parser.add_argument('-I','--osdid', help='osd id', required=False)
  parser.add_argument('-o','--out', help='check osds that are set OUT', default=False, action='store_true', required=False)
  args = parser.parse_args()

  # validate args
  ceph_exec = args.exe if args.exe else CEPH_COMMAND
  if not os.path.exists(ceph_exec):
    print "OSD ERROR: ceph executable '%s' doesn't exist" % ceph_exec
    return STATUS_UNKNOWN

  if args.version:
    print 'version %s' % __version__
    return STATUS_OK

  if args.conf and not os.path.exists(args.conf):
    print "OSD ERROR: ceph conf file '%s' doesn't exist" % args.conf
    return STATUS_UNKNOWN

  if args.keyring and not os.path.exists(args.keyring):
    print "OSD ERROR: keyring file '%s' doesn't exist" % args.keyring
    return STATUS_UNKNOWN

  if not args.osdid:
    args.osdid = '[^ ]*'

  if not args.host:
    print "OSD ERROR: no OSD hostname given"
    return STATUS_UNKNOWN

  try:
    args.host = socket.gethostbyname(args.host)
  except socket.gaierror:
    print 'OSD ERROR: could not resolve %s' % args.host
    return STATUS_UNKNOWN


  # build command
  ceph_cmd = [ceph_exec]
  if args.monaddress:
      ceph_cmd.append('-m')
      ceph_cmd.append(args.monaddress)
  if args.conf:
      ceph_cmd.append('-c')
      ceph_cmd.append(args.conf)
  if args.id:
      ceph_cmd.append('--id')
      ceph_cmd.append(args.id)
  if args.keyring:
      ceph_cmd.append('--keyring')
      ceph_cmd.append(args.keyring)
  ceph_cmd.append('osd')
  ceph_cmd.append('dump')

  # exec command
  p = subprocess.Popen(ceph_cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  output, err = p.communicate()

  if err or not output:
    print "OSD ERROR: %s" % err
    return STATUS_ERROR

  # escape IPv4 host address
  osd_host = args.host.replace('.', '\.')
  # escape IPv6 host address
  osd_host = osd_host.replace('[', '\[')
  osd_host = osd_host.replace(']', '\]')
  up = re.findall(r"^(osd\.%s) up.* %s:" % (args.osdid, osd_host), output, re.MULTILINE)
  if args.out:
    down = re.findall(r"^(osd\.%s) down.* %s:" % (args.osdid, osd_host), output, re.MULTILINE)
    down_in = re.findall(r"^(osd\.%s) down[ ]+in.* %s:" % (args.osdid, osd_host), output, re.MULTILINE)
    down_out = re.findall(r"^(osd\.%s) down[ ]+out.* %s:" % (args.osdid, osd_host), output, re.MULTILINE)
  else:
    down = re.findall(r"^(osd\.%s) down[ ]+in.* %s:" % (args.osdid, osd_host), output, re.MULTILINE)
    down_in = down
    down_out = re.findall(r"^(osd\.%s) down[ ]+out.* %s:" % (args.osdid, osd_host), output, re.MULTILINE)

  if down:
    print "OSD WARN: Down OSD%s on %s: %s" % ('s' if len(down)>1 else '', args.host, " ".join(down))
    print "Up OSDs: " + " ".join(up)
    print "Down+In OSDs: " + " ".join(down_in)
    print "Down+Out OSDs: " + " ".join(down_out)
    return STATUS_WARNING

  if up:
    print "OSD OK"
    print "Up OSDs: " + " ".join(up)
    print "Down+In OSDs: " + " ".join(down_in)
    print "Down+Out OSDs: " + " ".join(down_out)
    return STATUS_OK

  print "OSD WARN: no OSD.%s found on host %s" % (args.osdid, args.host)
  return STATUS_WARNING

if __name__ == "__main__":
    sys.exit(main())