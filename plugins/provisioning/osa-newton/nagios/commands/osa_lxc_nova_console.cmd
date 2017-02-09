#--- Monitoring commands for OpsMgr role: osa_lxc_nova_console

command[osa_lxc_proxy] = sudo /etc/nagios/plugins/check-lxc.sh nova_console check-procs.rb '-p proxy -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_consoleauth] = sudo /etc/nagios/plugins/check-lxc.sh nova_console check-procs.rb '-p nova-consoleauth -w 80 -c 320 -W 1 -C 1'

