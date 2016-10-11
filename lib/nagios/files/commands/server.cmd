#--- Monitoring commands for OpsMgr role: server

command[server-cpu]      = /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[server-mem]      = /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[server-disk]     = /etc/nagios/plugins/check-disk.rb 
command[server-logs]     = /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[server-socket]   = /etc/nagios/plugins/check-syslog-socket.rb 
command[server-ntp]      = /etc/nagios/plugins/check-ntp.rb 
command[server-eth10]    = /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces eth10
command[server-eth11]    = /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces eth11
command[server-ntpd]     = /etc/nagios/plugins/check-procs.rb -p ntpd -w 30 -c 40 -W 1 -C 1
command[server-rsyslogd] = /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 30 -c 40 -W 1 -C 1
command[server-sshd]     = /etc/nagios/plugins/check-procs.rb -p sshd -w 30 -c 40 -W 1 -C 1
command[server-cron]     = /etc/nagios/plugins/check-procs.rb -p cron -w 30 -c 40 -W 1 -C 1

