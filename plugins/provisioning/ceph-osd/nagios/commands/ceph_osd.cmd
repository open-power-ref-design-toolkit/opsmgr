#--- Monitoring commands for OpsMgr role: ceph_osd

#command[check_ceph_osd] = sudo /usr/bin/python /etc/nagios/plugins/check-ceph-osd.py -H 127.0.0.1

command[check_osd_proc] = /etc/nagios/plugins/check-procs.rb -p ceph-osd -w 15 -c 30 -W 1 -C 1

