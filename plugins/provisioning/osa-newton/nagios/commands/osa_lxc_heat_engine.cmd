#--- Monitoring commands for OpsMgr role: osa_lxc_heat_engine

command[osa_lxc_engine] = sudo /etc/nagios/plugins/check-lxc.sh heat_engine check-procs.rb '-p heat-engine -w 15 -c 30 -W 1 -C 1'

