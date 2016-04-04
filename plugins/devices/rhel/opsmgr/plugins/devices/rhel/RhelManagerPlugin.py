import logging
import socket

import paramiko

from opsmgr.inventory.interfaces import IManagerDevicePlugin
from opsmgr.inventory import IntegratedManagerException

RHEL_RELEASE_FILE = "/etc/redhat-release"
RELEASE_TAG = "Red Hat Enterprise"

class RhelPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    def __init__(self):
        self.client = None
        self.machine_type_model = ""
        self.serial_number = ""

    @staticmethod
    def get_type():
        return "Redhat Enterprise Linux"

    @staticmethod
    def get_web_url(host):
        return None

    def connect(self, host, userid, password):
        _method_ = "RhelPlugin.connect"
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(host, username=userid,
                                password=password, timeout=30)
            if not self._is_guest_rhel():
                raise IntegratedManagerException.InvalidDeviceException(
                    "Device is not a RHEL Device")
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
