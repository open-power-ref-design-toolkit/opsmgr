#--- Monitoring commands for OpsMgr role: osa_lxc_trove_api

command[trove-api] = sudo /etc/nagios/plugins/check-lxc.sh trove_api check-procs.rb '-p trove-api -w 80 -c 320 -W 1 -C 1'

