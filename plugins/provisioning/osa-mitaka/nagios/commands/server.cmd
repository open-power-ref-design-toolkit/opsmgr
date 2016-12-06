#--- Monitoring commands for OpsMgr role: server

command[server-cpu]      = sudo /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[server-mem]      = sudo /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[server-disk]     = sudo /etc/nagios/plugins/check-disk.rb 
command[server-logs]     = sudo /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[server-socket]   = sudo /etc/nagios/plugins/check-syslog-socket.rb 
command[server-ntp]      = sudo /etc/nagios/plugins/check-ntp.rb 
command[server-ntpd]     = sudo /etc/nagios/plugins/check-procs.rb -p ntpd -w 30 -c 40 -W 1 -C 1
command[server-rsyslogd] = sudo /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 40 -c 50 -W 1 -C 1
command[server-sshd]     = sudo /etc/nagios/plugins/check-procs.rb -p sshd -w 50 -c 60 -W 1 -C 1
command[server-cron]     = sudo /etc/nagios/plugins/check-procs.rb -p cron -w 40 -c 50 -W 1 -C 1
command[server-br-mgmt]  = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-mgmt
command[server-br-stor]  = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-storage
command[server-br-vlan]  = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-vlan
command[server-br-vxln]  = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-vxlan
