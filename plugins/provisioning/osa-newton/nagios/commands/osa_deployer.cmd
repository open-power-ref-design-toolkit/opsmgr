#--- Monitoring commands for OpsMgr role: osa_deployer

command[osa_deployer_dbus] = /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 80 -c 320 -W 1 -C 1

