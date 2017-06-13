#--- Monitoring commands for OpsMgr role: osa_lxc_swift_proxy

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-procs.rb '-p swift -w 100 -c 400 -W 1 -C 1'
command[swift_load_01m]          = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-load.py -i  1m -w 75 -c 90
command[swift_load_05m]          = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-load.py -i  5m -w 75 -c 90
command[swift_load_15m]          = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-load.py -i 15m -w 75 -c 90
command[swift_space]             = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-space.py -w 75 -c 90
command[swift_md5]               = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-md5.py
command[swift_unmounted]         = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-unmounted.py
command[swift_usage]             = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-usage.sh
command[swift_orphans]           = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-orphans.py
command[swift_dispersion]        = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-swift-dispersion.py

