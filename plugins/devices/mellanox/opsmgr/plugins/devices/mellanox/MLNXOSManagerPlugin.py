import logging
import socket
import time

import paramiko

from opsmgr.inventory.interfaces import IManagerDevicePlugin
from opsmgr.inventory import IntegratedManagerException

class MLNXOSPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    SHOW_INVENTORY_COMMAND = "show inventory\n"
    CHASSIS_INFORMATION = "CHASSIS"
    GET_VERSION_COMMAND = "show version | include \"Product release:\"\n"
    VERSION_TAG = "Product release"

    ENABLE_COMMAND = "enable\n"
    CONFIGURE_TERMINAL_COMMAND = "configure terminal\n"

    def __init__(self):
        self.client = None
        self.host = None
        self.userid = None
        self.machine_type_model = ""
        self.serial_number = ""

    @staticmethod
    def get_type():
        return "MLNX-OS"

    @staticmethod
    def get_web_url(host):
        return "https://" + host

    def connect(self, host, userid, password=None, ssh_key_string=None):
        _method_ = "MLNXOSPlugin.connect"
        self.host = host
        self.userid = userid
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(ssh_key_string, password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30)
            if not self._is_mellanox_switch():
                raise IntegratedManagerException.InvalidDeviceException(
                    "Device is not a Mellanox Switch")
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
        version = None
        client_shell = self.client.invoke_shell()
        client_shell.send(self.GET_VERSION_COMMAND)
        time.sleep(2)
        output = client_shell.recv(500).decode()
        for line in output.splitlines():
            if line.startswith(self.VERSION_TAG):
                version = line.split()[2]
                break
        return version

    def change_device_password(self, new_password):
        _method_ = "MLNXOSPlugin.change_device_password"
        logging.info("ENTER %s::host=%s userid=%s", _method_, self.host, self.userid)
        client_shell = self.client.invoke_shell()
        client_shell.send(self.ENABLE_COMMAND)
        client_shell.send(self.CONFIGURE_TERMINAL_COMMAND)
        client_shell.send("username " + self.userid + " password 0 " + new_password + "\n")
        time.sleep(5)
        client_shell.close()
        test_connect = MLNXOSPlugin()
        try:
            test_connect.connect(self.host, self.userid, new_password)
        except IntegratedManagerException.IntegratedManagerDeviceException as e:
            logging.exception(e)
            logging.error("%s::Failed to login with new password, login exception was thrown: "
                          "%s", _method_, str(e))
            raise e

    def _is_mellanox_switch(self):
        """Check if the Device type is Mellanox
        """
        client_shell = self.client.invoke_shell()
        client_shell.send(self.SHOW_INVENTORY_COMMAND)
        time.sleep(2)
        output = client_shell.recv(5000).decode()
        for line in output.splitlines():
            if line.startswith(self.CHASSIS_INFORMATION):
                self.machine_type_model = line.split()[2]
                self.serial_number = line.split()[3]
                break

        # if MTM is found, must be mellanox switch
        if self.machine_type_model == "":
            return False
        else:
            return True
