#--- Monitoring commands for OpsMgr role: swift_proxy

command[swift_proxy_cpu]         = sudo /etc/nagios/plugins/check-cpu.rb -w 80 -c 90
command[swift_proxy_mem]         = sudo /etc/nagios/plugins/check-mem.sh -w 250 -c 100
command[swift_proxy_disk]        = sudo /etc/nagios/plugins/check-disk.rb
command[swift_proxy_large_files] = sudo /etc/nagios/plugins/check-for-large-files.sh -d /var/log -s 1048576
command[swift_proxy_slsocket]    = sudo /etc/nagios/plugins/check-syslog-socket.rb
command[swift_proxy_ntp]         = sudo /etc/nagios/plugins/check-ntp.rb
command[swift_proxy_brmgmt]      = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-mgmt
command[swift_proxy_brstor]      = sudo /etc/nagios/plugins/check-netif.rb -c 500 -w 350 --interfaces br-storage
command[swift_proxy_rsyslogd]    = sudo /etc/nagios/plugins/check-procs.rb -p rsyslogd -w 15 -c 30 -W 1 -C 1
command[swift_proxy_sshd]        = sudo /etc/nagios/plugins/check-procs.rb -p sshd -w 15 -c 30 -W 1 -C 1
command[swift_proxy_cron]        = sudo /etc/nagios/plugins/check-procs.rb -p cron -w 15 -c 30 -W 1 -C 1
command[swift_proxy_atd]         = sudo /etc/nagios/plugins/check-procs.rb -p atd -w 15 -c 30 -W 1 -C 1
command[swift_proxy_dbus]        = sudo /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 15 -c 30 -W 1 -C 1
command[swift_proxy_iprupdate]   = sudo /etc/nagios/plugins/check-procs.rb -p iprupdate -w 15 -c 30 -W 1 -C 1
command[swift_proxy_iprdump]     = sudo /etc/nagios/plugins/check-procs.rb -p iprdump -w 15 -c 30 -W 1 -C 1
command[swift_proxy_iprinit]     = sudo /etc/nagios/plugins/check-procs.rb -p iprinit -w 15 -c 30 -W 1 -C 1
command[swift_proxy_apache2]     = sudo /etc/nagios/plugins/check-procs.rb -p apache2 -w 15 -c 30 -W 1 -C 1
command[swift_proxy_memcached]   = sudo /etc/nagios/plugins/check-procs.rb -p memcached -w 15 -c 30 -W 1 -C 1
command[swift_proxy_procs]       = sudo /etc/nagios/plugins/check-procs.rb -p swift-proxy-server -w 250 -c 300 -W 1 -C 1

