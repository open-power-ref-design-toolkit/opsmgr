#--- Monitoring commands for OpsMgr role: osa_host

command[osa_compute_nova]    = /etc/nagios/plugins/check-procs.rb -p nova -w 30 -c 40 -W 1 -C 1
command[osa_compute_libvirt] = /etc/nagios/plugins/check-procs.rb -p libvirtd -w 30 -c 40 -W 1 -C 1
command[osa_compute_neutron] = /etc/nagios/plugins/check-procs.rb -p neutron -w 30 -c 40 -W 1 -C 1
command[osa_compute_syslog]  = /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 30 -c 40 -W 1 -C 1
command[osa_compute_beaver]  = /etc/nagios/plugins/check-procs.rb -p beaver -w 30 -c 40 -W 1 -C 1


