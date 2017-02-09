#--- Monitoring commands for OpsMgr role: osa_lxc_swift_proxy

command[osa_lxc_procs] = sudo /etc/nagios/plugins/check-lxc.sh swift_proxy check-procs.rb '-p swift -w 80 -c 320 -W 1 -C 1'

