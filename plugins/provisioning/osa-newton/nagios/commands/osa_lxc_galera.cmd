#--- Monitoring commands for OpsMgr role: osa_lxc_galera

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh galera check-procs.rb '-p mysqld -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_safe] = sudo /etc/nagios/plugins/check-lxc.sh galera check-procs.rb '-p mysqld_safe -w 80 -c 320 -W 1 -C 1'

