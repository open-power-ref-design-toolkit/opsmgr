#--- Monitoring commands for OpsMgr role: osa_lxc_memcached

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh memcached check-procs.rb '-p memcached -w 80 -c 320 -W 1 -C 1'

