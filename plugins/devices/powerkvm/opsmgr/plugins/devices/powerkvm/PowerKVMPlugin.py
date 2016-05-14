import logging
import socket
import time

try:
    #python 2.7
    from StringIO import StringIO
except ImportError:
    #python 3.4
    from io import StringIO

import paramiko

from opsmgr.common import exceptions
from opsmgr.inventory.interfaces import IManagerDevicePlugin

class PowerKVMPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    SYSTEM_INFO_CMD = "lscfg -p | grep -A 10 \"System VPD\""
    MACHINE_TYPE_MODEL_TAG = "Machine Type"
    SERIAL_NUMBER_TAG = "Serial Number"

    RELEASE_CMD = "lsb_release -a"
    RELEASE_TAG = "Release"

    def __init__(self):
        self.client = None
        self.host = None
        self.userid = None
        self.machine_type_model = ""
        self.serial_number = ""

    @staticmethod
    def get_type():
        return "PowerKVM"

    @staticmethod
    def get_web_url(host):
        return "https://" + host + ":8001"

    def connect(self, host, userid, password=None, ssh_key_string=None):
        _method_ = "PowerKVMPlugin.connect"
        self.host = host
        self.userid = userid
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_string), password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30)

            if not self._is_power_kvm():
                raise exceptions.InvalidDeviceException("Device is not a PowerKVM system")
        except paramiko.AuthenticationException:
            logging.error("%s::userid/password combination not valid. host=%s userid=%s",
                          _method_, host, userid)
            raise exceptions.AuthenticationException("userid/password combination not valid")
        except (paramiko.ssh_exception.SSHException, OSError, socket.timeout) as e:
            logging.exception(e)
            logging.error("%s::Connection timed out. host=%s", _method_, host)
            raise exceptions.ConnectionException("Unable to ssh to the device")

    def disconnect(self):
        if self.client:
            self.client.close()

    def get_machine_type_model(self):
        if self.machine_type_model == "":
            self._get_system_details()
        return self.machine_type_model

    def get_serial_number(self):
        if self.serial_number == "":
            self._get_system_details()
        return self.serial_number

    def get_version(self):
        version = None
        (_stdin, stdout, _stderr) = self.client.exec_command(PowerKVMPlugin.RELEASE_CMD)
        rc = stdout.channel.recv_exit_status()
        if rc == 0:
            for line in stdout.read().decode().splitlines():
                if PowerKVMPlugin.RELEASE_TAG in line:
                    version = line.split(':')[1].strip()
        return version

    def change_device_password(self, new_password):
        _method_ = "PowerKVMPlugin.change_device_password"
        client_shell = self.client.invoke_shell()
        change_user_passwd = "echo -e \"" + new_password + "\\n" + new_password + \
                             "\" | (passwd --stdin " + self.userid + ")"
        client_shell.send(change_user_passwd)
        time.sleep(5)
        client_shell.close()
        test_connect = PowerKVMPlugin()
        try:
            test_connect.connect(self.host, self.userid, new_password)
        except exceptions.DeviceException as e:
            logging.exception(e)
            logging.error("%s::Failed to login with new password, login exception was thrown: "
                          "%s", _method_, str(e))
            raise e

    def _is_power_kvm(self):
        """Return true if it's a PowerKVM system
        """
        power_kvm = False
        (_stdin, stdout, _stderr) = self.client.exec_command('uname -a')
        rc = stdout.channel.recv_exit_status()
        if rc == 0:
            if stdout.read().decode().lower().find("pkvm") >= 0:
                power_kvm = True
        return power_kvm

    def _get_system_details(self):
        found_serial_number_tag = False
        (_stdin, stdout, _stderr) = self.client.exec_command(PowerKVMPlugin.SYSTEM_INFO_CMD)
        for line in stdout.read().decode().splitlines():
            if found_serial_number_tag:
                npos = line.rfind("...")
                if npos >= 0:
                    self.serial_number = line[npos + 3:]
                found_serial_number_tag = False
            elif PowerKVMPlugin.SERIAL_NUMBER_TAG in line:
                # Next line contains the serial number
                found_serial_number_tag = True
            elif PowerKVMPlugin.MACHINE_TYPE_MODEL_TAG in line:
                npos = line.rfind("...")
                if npos >= 0:
                    self.machine_type_model = line[npos + 3:]
