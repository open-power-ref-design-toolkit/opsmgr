#--- Monitoring commands for OpsMgr role: osa_controller

command[osa_controller_keystone_se] = /etc/nagios/plugins/check-procs.rb -p keystone_se -w 15 -c 30 -W 1 -C 1
command[osa_controller_keystone_ad] = /etc/nagios/plugins/check-procs.rb -p keystone_ad -w 15 -c 30 -W 1 -C 1
command[osa_controller_haproxy] = /etc/nagios/plugins/check-procs.rb -p 'haproxy.*-f /etc/haproxy/haproxy.cfg' -w 15 -c 30 -W 1 -C 1
#command[osa_controller_mysqld] = /etc/nagios/plugins/check-procs.rb -p mysqld -w 15 -c 30 -W 1 -C 1
command[osa_controller_rabbitmq] = /etc/nagios/plugins/check-procs.rb -p rabbitmq -w 15 -c 30 -W 1 -C 1

