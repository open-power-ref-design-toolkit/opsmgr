#--- Monitoring commands for OpsMgr role: osa_lxc_nova_api_metadata

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh nova_api_metadata check-procs.rb '-p nova-api-metadata -w 15 -c 30 -W 1 -C 1'

