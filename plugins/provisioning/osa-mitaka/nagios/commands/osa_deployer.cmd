#--- Monitoring commands for OpsMgr role: osa_deployer

command[osa_deployer_dbus] = /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 30 -c 40 -W 1 -C 1

