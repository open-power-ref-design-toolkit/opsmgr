import logging
import socket
import time

import paramiko

from opsmgr.inventory.interfaces import IManagerDevicePlugin
from opsmgr.inventory import IntegratedManagerException

class RackSwitchPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    SHOW_VERSION_COMMAND = "show version"
    VERSION_TAG = "Software Version"
    SERIAL_NUM_TAG = "Switch Serial"
    MTM_TAG = "MTM Value"

    ENABLE_COMMAND = "enable\n"
    PASSWORD_CHANGE_COMMAND = "password\n"

    PASSWORD_CHANGED_MESSAGE = "Password changed and applied"

    def __init__(self):
        self.client = None
        self.host = None
        self.userid = None
        self.password = None
        self.ssh_key_string = None
        self.machine_type_model = ""
        self.serial_number = ""
        self.version = ""

    @staticmethod
    def get_type():
        return "LenovoRackSwitch"

    @staticmethod
    def get_web_url(host):
        return "https://" + host

    def connect(self, host, userid, password=None, ssh_key_string=None):
        _method_ = "RackSwitchPlugin.connect"
        self.host = host
        self.userid = userid
        self.password = password
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(ssh_key_string, password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30)
            if not self._is_rack_switch():
                raise IntegratedManagerException.InvalidDeviceException(
                    "Device is not a Lenovo Rack Switch")
        except paramiko.AuthenticationException:
            logging.error("%s::userid/password combination not valid. host=%s userid=%s",
                          _method_, host, userid)
            raise IntegratedManagerException.AuthenticationException(
                "userid/password combination not valid")
        except (paramiko.ssh_exception.SSHException, OSError, socket.timeout) as e:
            logging.exception(e)
            logging.error("%s::Connection timed out. host=%s", _method_, host)
            raise IntegratedManagerException.ConnectionException("Unable to ssh to the device")

    def disconnect(self):
        if self.client:
            self.client.close()

    def get_machine_type_model(self):
        return self.machine_type_model

    def get_serial_number(self):
        return self.serial_number

    def get_version(self):
        return self.version

    def change_device_password(self, new_password):
        _method_ = "RackSwitchPlugin.change_device_password"
        logging.info("ENTER %s::host=%s userid=%s", _method_, self.host, self.userid)

        self._check_connection()
        client_shell = self.client.invoke_shell()
        client_shell.send(self.PASSWORD_CHANGE_COMMAND)
        client_shell.send(self.password + "\n")
        client_shell.send(new_password + "\n")
        client_shell.send(new_password + "\n")
        time.sleep(5)
        output = client_shell.recv(1000).decode()
        client_shell.close()
        if self.PASSWORD_CHANGED_MESSAGE in output:
            logging.info("Password changed for " + self.userid + " successfully")
        else:
            message = "Failed to change password for %s. Console output: %s" % \
                      (self.userid, output)
            logging.warning(message)
            raise IntegratedManagerException.IntegratedManagerDeviceException(message)

    def _is_rack_switch(self):
        """Check if the Device type is Lenovo Rack Switch
        """
        (dummy_stdin, stdout, dummy_stderr) = self.client.exec_command(self.SHOW_VERSION_COMMAND)
        output = stdout.read().decode()
        for line in output.splitlines():
            if self.VERSION_TAG in line:
                self.version = line.split()[2]
            elif self.MTM_TAG in line:
                self.machine_type_model = line.split()[-1]
            elif self.SERIAL_NUM_TAG in line:
                self.serial_number = line.split()[-1]

        # if MTM is found, must be a rack switch
        if self.machine_type_model == "":
            return False
        else:
            return True

    def _check_connection(self):
        """ The lenovo switch seems to drop a connection really quick if not active in
            shell. Verify the connection is active before using it, and if necessary
            create a new connection
        """
        transport = self.client.get_transport()
        if transport is None or transport.is_active() is False:
            if self.ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(self.ssh_key_string, self.password)
                self.client.connect(self.host, username=self.userid, pkey=private_key, timeout=30)
            else:
                self.client.connect(self.host, username=self.userid,
                                    password=self.password, timeout=30)
