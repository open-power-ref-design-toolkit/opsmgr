#--- Monitoring commands for OpsMgr role: osa_lxc_nova_scheduler

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh nova_scheduler check-procs.rb '-p nova-scheduler -w 80 -c 320 -W 1 -C 1'

