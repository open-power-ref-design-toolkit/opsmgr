#--- Monitoring commands for OpsMgr role: osa_lxc_ceilometer_collector

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh ceilometer_collector check-procs.rb '-p ceilometer -w 80 -c 320 -W 1 -C 1'

