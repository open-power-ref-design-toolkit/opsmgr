#--- Monitoring commands for OpsMgr role: osa_lxc_keystone

command[osa_lxc_ad] = sudo /etc/nagios/plugins/check-lxc.sh keystone check-procs.rb '-p keystone-ad -w 20 -c 30 -W 1 -C 1'
command[osa_lxc_se] = sudo /etc/nagios/plugins/check-lxc.sh keystone check-procs.rb '-p keystone-se -w 20 -c 30 -W 1 -C 1'
command[osa_lxc_apache2] = sudo /etc/nagios/plugins/check-lxc.sh keystone check-procs.rb '-p apache2 -w 15 -c 30 -W 1 -C 1'

