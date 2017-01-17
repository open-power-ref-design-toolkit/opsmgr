#--- Monitoring commands for OpsMgr role: osa_lxc_cinder_scheduler

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh cinder_scheduler check-procs.rb '-p cinder-scheduler -w 15 -c 30 -W 1 -C 1'

