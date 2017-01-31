#--- Monitoring commands for OpsMgr role: osa_lxc_nova_scheduler

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh nova_scheduler check-procs.rb '-p nova-scheduler -w 15 -c 30 -W 1 -C 1'

