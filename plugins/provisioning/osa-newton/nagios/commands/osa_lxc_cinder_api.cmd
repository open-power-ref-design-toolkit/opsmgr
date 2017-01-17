#--- Monitoring commands for OpsMgr role: osa_lxc_cinder_api

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh cinder_api check-procs.rb '-p cinder-api -w 15 -c 30 -W 1 -C 1'

