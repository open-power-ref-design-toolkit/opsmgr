#--- Monitoring commands for OpsMgr role: nagios

command[nagios_procs] = sudo /etc/nagios/plugins/check-lxc.sh nagios check-procs.rb '-p nagios -w 60 -c 120 -W 1 -C 1'
command[nagios_http_port] = sudo /usr/lib/nagios/plugins/check_http -H HostName -u http://HostName:8001/nagios
