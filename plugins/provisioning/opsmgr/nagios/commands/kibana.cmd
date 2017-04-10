#--- Monitoring commands for OpsMgr role: kibana

command[kibana_procs] = sudo /etc/nagios/plugins/check-lxc.sh kibana check-procs.rb '-p kibana -w 3 -c 3 -W 1 -C 1'
