#--- Monitoring commands for OpsMgr role: swift_object

command[swift_proxy_objsvr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-server -w 250 -c 300 -W 1 -C 1
command[swift_proxy_objaud]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_objupd]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-updater -w 15 -c 30 -W 1 -C 1
command[swift_proxy_objrep]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-replicator -w 15 -c 30 -W 1 -C 1
command[swift_proxy_objexp]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-object-expirer -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrsvr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-server -w 250 -c 300 -W 1 -C 1
command[swift_proxy_ctraud]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrupd]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-updater -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrrec]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-reconciler -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrrep]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-replicator -w 15 -c 30 -W 1 -C 1
command[swift_proxy_ctrsyn]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-container-sync -w 15 -c 30 -W 1 -C 1
command[swift_proxy_accsvr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-server -w 250 -c 300 -W 1 -C 1
command[swift_proxy_accrpr]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-reaper -w 15 -c 30 -W 1 -C 1
command[swift_proxy_accaud]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-auditor -w 15 -c 30 -W 1 -C 1
command[swift_proxy_accrep]      = sudo /etc/nagios/plugins/check-procs.rb -p swift-account-replicator -w 15 -c 30 -W 1 -C 1

