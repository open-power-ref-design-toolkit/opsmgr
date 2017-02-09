#--- Monitoring commands for OpsMgr role: osa_host

command[osa_compute_nova]    = /etc/nagios/plugins/check-procs.rb -p nova -w 80 -c 320 -W 1 -C 1
command[osa_compute_libvirt] = /etc/nagios/plugins/check-procs.rb -p libvirtd -w 80 -c 320 -W 1 -C 1
command[osa_compute_neutron] = /etc/nagios/plugins/check-procs.rb -p neutron -w 80 -c 320 -W 1 -C 1


