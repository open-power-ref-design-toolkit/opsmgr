#--- Monitoring commands for OpsMgr role: osa_lxc_trove

command[trove-cpu] = sudo /etc/nagios/plugins/check-lxc.sh trove check-cpu.rb '-w 80 -c 90'
command[trove-mem] = sudo /etc/nagios/plugins/check-lxc.sh trove check-mem.sh '-w 250 -c 100'
command[trove-disk] = sudo /etc/nagios/plugins/check-lxc.sh trove check-disk.rb ''
command[trove-large_files] = sudo /etc/nagios/plugins/check-lxc.sh trove check-for-large-files.sh '-d /var/log -s 1048576'
command[trove-slsocket] = sudo /etc/nagios/plugins/check-lxc.sh trove check-syslog-socket.rb ''
command[trove-ntp] = sudo /etc/nagios/plugins/check-lxc.sh trove check-ntp.rb ''
command[trove-eth0] = sudo /etc/nagios/plugins/check-lxc.sh trove check-netif.rb '-c 500 -w 350 --interfaces eth0'
command[trove-eth1] = sudo /etc/nagios/plugins/check-lxc.sh trove check-netif.rb '-c 500 -w 350 --interfaces eth1'
command[trove-rsyslogd] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p rsyslogd -w 15 -c 30 -W 1 -C 1'
command[trove-sshd] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p sshd -w 15 -c 30 -W 1 -C 1'
command[trove-cron] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p cron -w 15 -c 30 -W 1 -C 1'
command[trove-dbus] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p dbus-daemon -w 15 -c 30 -W 1 -C 1'
command[trove-taskmanager] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p trove-taskmanager -w 15 -c 30 -W 1 -C 1'
command[trove-conductor] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p trove-conductor -w 15 -c 30 -W 1 -C 1'
command[trove-api] = sudo /etc/nagios/plugins/check-lxc.sh trove check-procs.rb '-p trove-api -w 15 -c 30 -W 1 -C 1'

