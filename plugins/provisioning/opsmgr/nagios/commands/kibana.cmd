#--- Monitoring commands for OpsMgr role: kibana

command[kibana_procs] = sudo /etc/nagios/plugins/check-lxc.sh kibana check-procs.rb '-p kibana -w 1 -c 1 -W 1 -C 1'

