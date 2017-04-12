#--- Monitoring commands for OpsMgr role: osa_lxc_neutron_agents

command[osa_lxc_linuxbridge] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-linuxbridge-agent -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_metering] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-metering-agent -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_l3] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-l3-agent -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_metadata] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-metadata-agent -w 80 -c 320 -W 1 -C 1'
#command[osa_lxc_lbaasv2] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p lbaasv2-agent -w 80 -c 320 -W 1 -C 1'
#command[osa_lxc_hatool] = sudo /etc/nagios/plugins/check-lxc.sh neutron_agents check-procs.rb '-p neutron-ha-tool -w 80 -c 320 -W 1 -C 1'

