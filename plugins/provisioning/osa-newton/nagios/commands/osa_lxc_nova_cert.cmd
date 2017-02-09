#--- Monitoring commands for OpsMgr role: osa_lxc_nova_cert

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh nova_cert check-procs.rb '-p nova-cert -w 80 -c 320 -W 1 -C 1'

