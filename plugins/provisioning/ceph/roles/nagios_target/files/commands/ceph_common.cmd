#--- Monitoring commands for OpsMgr role: ceph_common

command[ceph_cpu]         = sudo /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[ceph_mem]         = sudo /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[ceph_disk]        = sudo /etc/nagios/plugins/check-disk.rb
command[ceph_large_files] = sudo /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[ceph_slsocket]    = sudo /etc/nagios/plugins/check-syslog-socket.rb
command[ceph_ntp]         = sudo /etc/nagios/plugins/check-ntp.rb
#command[ceph_brmgmt]      = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-mgmt
#command[ceph_brstor]      = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-storage
command[ceph_rsyslogd]    = sudo /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 15 -c 30 -W 1 -C 1
command[ceph_sshd]        = sudo /etc/nagios/plugins/check-procs.rb -p sshd -w 15 -c 30 -W 1 -C 1
command[ceph_cron]        = sudo /etc/nagios/plugins/check-procs.rb -p cron -w 15 -c 30 -W 1 -C 1
command[ceph_atd]         = sudo /etc/nagios/plugins/check-procs.rb -p atd -w 15 -c 30 -W 1 -C 1
command[ceph_dbus]        = sudo /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 15 -c 30 -W 1 -C 1
