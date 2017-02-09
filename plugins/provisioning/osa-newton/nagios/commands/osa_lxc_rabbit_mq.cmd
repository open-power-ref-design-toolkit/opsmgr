#--- Monitoring commands for OpsMgr role: osa_lxc_rabbit_mq

command[osa_lxc_epmd] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p epmd -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_beam.smp] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p beam.smp -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_server] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p rabbitmq_server -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_gethost] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p inet_gethost -w 80 -c 320 -W 1 -C 1'

