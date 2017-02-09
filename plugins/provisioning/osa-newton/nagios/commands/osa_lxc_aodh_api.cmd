#--- Monitoring commands for OpsMgr role: osa_lxc_aodh

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh aodh check-procs.rb '-p aodh -w 80 -c 320 -W 1 -C 1'

