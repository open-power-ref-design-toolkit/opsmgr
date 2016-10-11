#--- Monitoring commands for OpsMgr role: osa_storage

command[osa_host_cinder_volume] = /etc/nagios/plugins/check-procs.rb -p cinder-volume -w 15 -c 30 -W 1 -C 1
command[osa_host_cinder_backup] = /etc/nagios/plugins/check-procs.rb -p cinder-backup -w 15 -c 30 -W 1 -C 1

