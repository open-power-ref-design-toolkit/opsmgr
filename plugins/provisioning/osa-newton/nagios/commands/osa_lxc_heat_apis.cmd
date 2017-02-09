#--- Monitoring commands for OpsMgr role: osa_lxc_heat_apis

command[osa_lxc_cfn] = sudo /etc/nagios/plugins/check-lxc.sh heat_apis check-procs.rb '-p heat-api-cfn -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_cloudwatch] = sudo /etc/nagios/plugins/check-lxc.sh heat_apis check-procs.rb '-p heat-api-cloudwatch -w 80 -c 320 -W 1 -C 1'
command[osa_lxc_api] = sudo /etc/nagios/plugins/check-lxc.sh heat_apis check-procs.rb '-p heat-api -w 80 -c 320 -W 1 -C 1'

