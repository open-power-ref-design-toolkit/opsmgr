#--- Monitoring commands for OpsMgr role: ceph_monitor

command[check_ceph_health]       = sudo /usr/bin/python /etc/nagios/plugins/check-ceph-health.py
command[check_ceph_mon]          = sudo /usr/bin/python /etc/nagios/plugins/check-ceph-mon.py -I `hostname`
command[check_ceph_df]           = sudo /usr/bin/python /etc/nagios/plugins/check-ceph-df.py -W 80 -C 95
command[check_ceph_status]       = sudo /usr/bin/python /etc/nagios/plugins/check-ceph-status.py -m `/sbin/ifconfig br-storage|grep inet|head -1|sed 's/\:/ /'|awk '{print $3}'`

command[check_mon_proc] = /etc/nagios/plugins/check-procs.rb -p ceph-mon -w 15 -c 30 -W 1 -C 1

