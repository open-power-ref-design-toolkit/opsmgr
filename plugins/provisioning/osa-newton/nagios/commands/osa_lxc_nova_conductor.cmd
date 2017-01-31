#--- Monitoring commands for OpsMgr role: osa_lxc_nova_conductor

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh nova_conductor check-procs.rb '-p nova-conductor -w 15 -c 30 -W 1 -C 1'

