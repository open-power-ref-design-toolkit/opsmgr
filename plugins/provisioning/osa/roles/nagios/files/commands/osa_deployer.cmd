#--- Monitoring commands for OpsMgr role: osa_deployer

command[osa_deployer_cpu] = /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[osa_deployer_mem] = /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[osa_deployer_disk] = /etc/nagios/plugins/check-disk.rb 
command[osa_deployer_large_files] = /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[osa_deployer_slsocket] = /etc/nagios/plugins/check-syslog-socket.rb 
command[osa_deployer_ntp] = /etc/nagios/plugins/check-ntp.rb 
command[osa_deployer_eth10] = /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces eth10
command[osa_deployer_eth11] = /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces eth11
command[osa_deployer_ntpd] = /etc/nagios/plugins/check-procs.rb -p ntpd -w 30 -c 40 -W 1 -C 1
command[osa_deployer_rsyslogd] = /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 30 -c 40 -W 1 -C 1
command[osa_deployer_sshd] = /etc/nagios/plugins/check-procs.rb -p sshd -w 30 -c 40 -W 1 -C 1
command[osa_deployer_cron] = /etc/nagios/plugins/check-procs.rb -p cron -w 30 -c 40 -W 1 -C 1
command[osa_deployer_dbus] = /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 30 -c 40 -W 1 -C 1

