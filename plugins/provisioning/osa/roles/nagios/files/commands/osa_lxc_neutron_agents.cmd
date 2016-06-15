#--- Monitoring commands for OpsMgr role: osa_lxc

command[osa_lxc_cpu] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-cpu.rb '-w 80 -c 90'
command[osa_lxc_mem] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-mem.sh '-w 250 -c 100'
command[osa_lxc_disk] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-disk.rb ''
command[osa_lxc_large_files] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-for-large-files.sh '-d /var/log -s 1048576'
command[osa_lxc_slsocket] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-syslog-socket.rb ''
command[osa_lxc_ntp] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-ntp.rb ''
command[osa_lxc_eth0] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-netif.rb '-c 500 -w 350 --interfaces eth0'
command[osa_lxc_eth1] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-netif.rb '-c 500 -w 350 --interfaces eth1'
command[osa_lxc_dhcp] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-dhcp-agent -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_linuxbridge] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-linuxbridge-agent -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_metering] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-metering-agent -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_l3] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-l3-agent -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_metadata] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-metadata-agent -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_proxy] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-ns-metadata-proxy -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_hatool] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-ha-tool -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_rsyslogd] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p rsyslogd -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_sshd] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p sshd -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_cron] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p cron -w 15 -c 30 -W 1 -C 1'
command[osa_lxc_dbus] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p dbus-daemon -w 15 -c 30 -W 1 -C 1'





