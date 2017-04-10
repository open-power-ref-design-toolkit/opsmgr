#--- Monitoring commands for OpsMgr role: elasticsearch

command[elasticsearch_procs] = sudo /etc/nagios/plugins/check-lxc.sh elasticsearch check-procs.rb '-p elasticsearch -w 3 -c 3 -W 1 -C 1'
