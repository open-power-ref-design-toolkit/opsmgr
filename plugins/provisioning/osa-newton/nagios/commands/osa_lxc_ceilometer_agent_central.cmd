#--- Monitoring commands for OpsMgr role: osa_lxc_ceilometer_api

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh ceilometer_api check-procs.rb '-p ceilometer -w 80 -c 320 -W 1 -C 1'

