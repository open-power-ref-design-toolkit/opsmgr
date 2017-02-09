#--- Monitoring commands for OpsMgr role: osa_lxc_neutron_server

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh neutron_server check-procs.rb '-p neutron-server -w 80 -c 320 -W 1 -C 1'

