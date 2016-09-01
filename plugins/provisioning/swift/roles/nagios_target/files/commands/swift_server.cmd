#--- Monitoring commands for OpsMgr role: swift_server

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
command[swift_proxy_dbus]        = sudo /etc/nagios/plugins/check-procs.rb -p dbus-daemon -w 15 -c 30 -W 1 -C 1
command[swift_proxy_apache2]     = sudo /etc/nagios/plugins/check-procs.rb -p apache2 -w 15 -c 30 -W 1 -C 1
command[swift_proxy_haproxy]     = sudo /etc/nagios/plugins/check-procs.rb -p haproxy -w 15 -c 30 -W 1 -C 1
command[swift_proxy_objsvr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-server -w 250 -c 300 -W 1 -C 1
command[swift_proxy_objaud]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrsvr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-server -w 250 -c 300 -W 1 -C 1
command[swift_proxy_ctraud]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrrep]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-sync -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrsyn]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_accsvr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-server -w 250 -c 300 -W 1 -C 1
command[swift_proxy_accrpr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-reaper -w 15 -c 30 -W 1 -C 1
command[swift_proxy_accaud]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_accrep]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-replicator -w 15 -c 30 -W 1 -C 1

