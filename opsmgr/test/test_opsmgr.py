import paramiko as sshconnect
import getpass
import os
import unittest

output_string = 'label,rack id,rack location,machine type model,serial number,ip-address,userid,version,device type'
ssh_session = None
ip_address = ""
user = ""
_pass = ""


class SSHUtility(object):
    def __init__(self):
        global ip_address
        global user
        global _pass
     
        ip_address = '127.0.0.1'
        user = 'ubuntu'
        _pass = 'tpmPassw0rd'

        global ssh_session
        if not ssh_session:
            ssh_session = sshconnect.SSHClient()
            ssh_session.set_missing_host_key_policy(sshconnect.AutoAddPolicy())
            ssh_session.connect(ip_address, username=user, password=_pass)


    def execute_command(self, command='ls'):
        global ssh_session
        stdin, stdout, stderr = ssh_session.exec_command(command)
        output = stdout.read().rstrip()
        # print 'This is error  = ',stderr.readlines()
        if output_string == 'pass':
            return 0
        else:
            return output

    def __exit__(self):
        global ssh_session
        ssh_session.close()


class Test_1(unittest.TestCase):
    def test_list_device(self):
        x = SSHUtility()
        x.execute_command('opsmgr remove_device --all')
        x.execute_command('opsmgr add_device -l rhel -u root -p PASSW0RD -a 9.27.24.68')
        line = x.execute_command('opsmgr list_devices | tee >(wc -l) | tail -c 2 ')
        ip =x.execute_command('''opsmgr list_devices | egrep -o  '([0-9]{1,3}\.){3}[0-9]{1,3}' ''')
        print ip
        x.execute_command('opsmgr add_device -l v7000 -u superuser -p stor1virt -a 9.114.44.11')
        line = x.execute_command('opsmgr list_devices | tee >(wc -l) | tail -c 2 ')

    def test_add_device(self):
        x = SSHUtility()
        x.execute_command('opsmgr remove_device --all')
        print x.execute_command('opsmgr add_device -l rhel -u root -p PASSW0RD -a 9.27.24.68')

    def test_list_racks(self):
        x = SSHUtility()
        x.execute_command('opsmgr remove_device --all')
        print x.execute_command('opsmgr list_racks')


    def test_remove_device(self):
        x = SSHUtility()
        print x.execute_command('opsmgr remove_device --all')

    def test_remove_rack(self):
        x = SSHUtility()
        print x.execute_command('opsmgr remove_device --all')
        print x.execute_command('opsmgr remove_rack -l Default')





if __name__ == '__main__':
    unittest.main()
#    return False
