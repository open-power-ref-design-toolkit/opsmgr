#--- Monitoring commands for OpsMgr role: osa_lxc_trove_taskmanager

command[trove-taskmanager] = sudo /etc/nagios/plugins/check-lxc.sh trove_taskmanager check-procs.rb '-p trove-taskmanager -w 80 -c 320 -W 1 -C 1'

