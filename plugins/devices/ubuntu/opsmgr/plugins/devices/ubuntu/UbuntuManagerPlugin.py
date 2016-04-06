import logging
import socket

import paramiko

from opsmgr.inventory.interfaces import IManagerDevicePlugin
from opsmgr.inventory import IntegratedManagerException

UBUNTU_RELEASE_CMD = "lsb_release -a"
RELEASE_TAG = "Release:"

class UbuntuPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    def __init__(self):
        self.client = None
        self.machine_type_model = ""
        self.serial_number = ""

    @staticmethod
    def get_type():
        return "Ubuntu"

    @staticmethod
    def get_web_url(host):
        return None

    def connect(self, host, userid, password, ssh_key_string=None):
        _method_ = "UbuntuPlugin.connect"
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(ssh_key_string, password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30)
            if not self._is_ubuntu():
                raise IntegratedManagerException.InvalidDeviceException(
                    "Device is not a Ubuntu Device")
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
        _method_ = "manage_ubuntu.get_version"
        version = None

        logging.info("ENTER %s", _method_)

        (dummy_stdin, stdout, dummy_stderr) = self.client.exec_command(UBUNTU_RELEASE_CMD)
        rc = stdout.channel.recv_exit_status()
        # get version if command executed successfully
        if rc == 0:
            for line in stdout.read().decode('ascii').splitlines():
                # Parse the output for version
                if RELEASE_TAG in line:
                    version = line.split(':')[1].strip()
                    return version
            logging.error("%s::Could not retrieve version", _method_)
            return None
        else:
            logging.error("%s::Failed to retrieve version.", _method_)
            return None

    def _is_ubuntu(self):
        """Check the OS type is RHEL
        Return True if System is RHEL
        """
        (dummy_stdin, stdout, dummy_stderr) = self.client.exec_command("uname -a")
        return_code = stdout.channel.recv_exit_status()
        if return_code == 0:
            if stdout.read().decode().lower().find("ubuntu") >= 0:
                return True
        return False
