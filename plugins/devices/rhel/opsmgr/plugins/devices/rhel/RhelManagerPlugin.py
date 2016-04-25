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

RHEL_RELEASE_FILE = "/etc/redhat-release"
RELEASE_TAG = "Red Hat Enterprise"

class RhelPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    PASSWORD_CHANGE_COMMAND = "passwd\n"
    PASSWORD_CHANGED_MESSAGE = "all authentication tokens updated successfully"

    def __init__(self):
        self.client = None
        self.machine_type_model = ""
        self.serial_number = ""
        self.userid = ""
        self.password = ""

    @staticmethod
    def get_type():
        return "Redhat Enterprise Linux"

    @staticmethod
    def get_web_url(host):
        return None

    def connect(self, host, userid, password=None, ssh_key_string=None):
        _method_ = "RhelPlugin.connect"
        self.userid = userid
        self.password = password
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_string), password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30,
                                    allow_agent=False)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30,
                                    allow_agent=False)
            if not self._is_guest_rhel():
                raise exceptions.InvalidDeviceException(
                    "Device is not a RHEL Device")
        except paramiko.AuthenticationException:
            logging.error("%s::userid/password combination not valid. host=%s userid=%s",
                          _method_, host, userid)
            raise exceptions.AuthenticationException(
                "userid/password combination not valid")
        except (paramiko.ssh_exception.SSHException, OSError, socket.timeout) as e:
            logging.exception(e)
            logging.error("%s::Connection timed out. host=%s", _method_, host)
            raise exceptions.ConnectionException("Unable to ssh to the device")

    def disconnect(self):
        if self.client:
            self.client.close()

    def get_machine_type_model(self):
        return self.machine_type_model

    def get_serial_number(self):
        return self.serial_number

    def get_version(self):
        version = None
        (dummy_stdin, stdout, dummy_stderr) = self.client.exec_command("cat " + RHEL_RELEASE_FILE)
        for line in stdout.read().decode().splitlines():
            if line.startswith(RELEASE_TAG):
                version = line.split(' ')[6]
                break
        return version

    def _is_guest_rhel(self):
        """Check the OS type is RHEL
        Return True if System is RHEL
        """
        (dummy_stdin, stdout, dummy_stderr) = self.client.exec_command(
            "test -e " + RHEL_RELEASE_FILE)
        rc = stdout.channel.recv_exit_status()
        return True if rc == 0 else False

    def change_device_password(self, new_password):
        """Update the password for the logged in userid.
        """

        client_shell = self.client.invoke_shell()
        client_shell.send(self.PASSWORD_CHANGE_COMMAND)
        if self.userid != "root":
            time.sleep(2)
            client_shell.send(self.password + "\n")
        time.sleep(2)
        client_shell.send(new_password + "\n")
        time.sleep(2)
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
            raise exceptions.DeviceException(message)
