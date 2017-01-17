#--- Monitoring commands for OpsMgr role: osa_lxc_repo

command[osa_lxc_nginx] = sudo /etc/nagios/plugins/check-lxc.sh repo check-procs.rb '-p nginx -w 15 -c 30 -W 1 -C 1'

