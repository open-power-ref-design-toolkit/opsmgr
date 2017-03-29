#--- Monitoring commands for OpsMgr role: elasticsearch

command[elasticsearch_procs] = sudo /etc/nagios/plugins/check-lxc.sh elasticsearch check-procs.rb '-p elasticsearch -w 1 -c 1 -W 1 -C 1'

