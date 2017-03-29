#--- Monitoring commands for OpsMgr role: logstash

command[logstash_procs] = sudo /etc/nagios/plugins/check-lxc.sh logstash check-procs.rb '-p logstash -w 1 -c 1 -W 1 -C 1'

