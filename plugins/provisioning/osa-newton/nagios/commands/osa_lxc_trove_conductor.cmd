#--- Monitoring commands for OpsMgr role: osa_lxc_trove_conductor

command[trove-conductor] = sudo /etc/nagios/plugins/check-lxc.sh trove_conductor check-procs.rb '-p trove-conductor -w 80 -c 320 -W 1 -C 1'

