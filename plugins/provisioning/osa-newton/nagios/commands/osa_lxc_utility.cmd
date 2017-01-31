#--- Monitoring commands for OpsMgr role: osa_lxc_utility

command[osa_lxc_cpu] = sudo /etc/nagios/plugins/check-lxc.sh utility check-cpu.rb '-w 80 -c 90'

