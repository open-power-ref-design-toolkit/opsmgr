#--- Monitoring commands for OpsMgr role: osa_lxc_trove

command[trove-taskmanager] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p trove-taskmanager -w 15 -c 30 -W 1 -C 1'
command[trove-conductor] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p trove-conductor -w 15 -c 30 -W 1 -C 1'
command[trove-api] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p trove-api -w 15 -c 30 -W 1 -C 1'

