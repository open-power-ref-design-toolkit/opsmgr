#--- Monitoring commands for OpsMgr role: osa_lxc_horizon

command[osa_lxc_apache2] = sudo /etc/nagios/plugins/check-lxc.sh horizon check-procs.rb '-p apache2 -w 80 -c 320 -W 1 -C 1'

