#--- Monitoring commands for OpsMgr role: server

command[server-cpu]      = sudo /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[server-mem]      = sudo /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[server-disk]     = sudo /etc/nagios/plugins/check-disk.rb -x iso9660
command[server-logs]     = sudo /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[server-socket]   = sudo /etc/nagios/plugins/check-syslog-socket.rb
command[server-rsyslogd] = sudo /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 80 -c 320 -W 1 -C 1
command[server-sshd]     = sudo /etc/nagios/plugins/check-procs.rb -p sshd -w 80 -c 320 -W 1 -C 1
command[server-cron]     = sudo /etc/nagios/plugins/check-procs.rb -p cron -w 80 -c 320 -W 1 -C 1

command[SSH]              = sudo /usr/lib/nagios/plugins/check_ssh -4 HostName
command[Current_Load]     = sudo /usr/lib/nagios/plugins/check_load -w 20.0,16.0,12.0 -c 60.0,36.0,24.0
command[Current_Users]    = sudo /usr/lib/nagios/plugins/check_users -w 20 -c 50
command[Total_Processes]  = sudo /usr/lib/nagios/plugins/check_procs -w 250 -c 400 -s RSZDT

