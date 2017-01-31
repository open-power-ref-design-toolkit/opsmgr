#--- Monitoring commands for OpsMgr role: osa_lxc_aodh

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh aodh check-procs.rb '-p aodh -w 15 -c 30 -W 1 -C 1'

