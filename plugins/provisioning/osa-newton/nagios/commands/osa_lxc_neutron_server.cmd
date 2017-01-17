#--- Monitoring commands for OpsMgr role: osa_lxc_neutron_server

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh neutron_server check-procs.rb '-p neutron-server -w 15 -c 30 -W 1 -C 1'

