#--- Monitoring commands for OpsMgr role: osa_lxc_glance

command[osa_lxc_registry] = sudo /etc/nagios/plugins/check-lxc.sh glance check-procs.rb '-p glance-registry -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_api] = sudo /etc/nagios/plugins/check-lxc.sh glance check-procs.rb '-p glance-api -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_rpcbind] = sudo /etc/nagios/plugins/check-lxc.sh glance check-procs.rb '-p rpcbind -w 15 -c 30 -W 1 -C 1'

