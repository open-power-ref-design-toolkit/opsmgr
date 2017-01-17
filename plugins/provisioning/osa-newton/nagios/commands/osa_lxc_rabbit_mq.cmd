#--- Monitoring commands for OpsMgr role: osa_lxc_rabbit_mq

command[osa_lxc_epmd] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p epmd -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_beam.smp] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p beam.smp -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_server] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p rabbitmq_server -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_gethost] = sudo /etc/nagios/plugins/check-lxc.sh rabbit_mq check-procs.rb '-p inet_gethost -w 15 -c 30 -W 1 -C 1'

