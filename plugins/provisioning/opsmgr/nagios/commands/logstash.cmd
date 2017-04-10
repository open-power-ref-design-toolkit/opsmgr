#--- Monitoring commands for OpsMgr role: logstash

command[logstash_procs] = sudo /etc/nagios/plugins/check-lxc.sh logstash check-procs.rb '-p logstash -w 3 -c 3 -W 1 -C 1'
