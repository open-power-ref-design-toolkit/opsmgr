#--- Monitoring commands for OpsMgr role: osa_lxc_gnocchi

command[osa_lxc_gnocchi-metricd] = sudo /etc/nagios/plugins/check-lxc.sh gnocchi check-procs.rb '-p gnocchi-metricd -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_gnocchi-wsgi] = sudo /etc/nagios/plugins/check-lxc.sh gnocchi check-procs.rb '-p wsgi:gnocchi -w 15 -c 30 -W 1 -C 1'
 
