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

class UbuntuPlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    UBUNTU_RELEASE_CMD = "lsb_release -a"
    RELEASE_TAG = "Release:"

    SYSTEM_INFO_CMD = "lscfg -p | grep -A 10 \"System VPD\""
    MACHINE_TYPE_MODEL_TAG = "Machine Type"
    SERIAL_NUMBER_TAG = "Serial Number"

    PASSWORD_CHANGE_COMMAND = "passwd\n"
    PASSWORD_CHANGED_MESSAGE = "password updated successfully"

    def __init__(self):
        self.client = None
        self.machine_type_model = ""
        self.serial_number = ""
        self.userid = ""
        self.password = ""

    @staticmethod
    def get_type():
        return "Ubuntu"

    @staticmethod
    def get_web_url(host):
        return None

    def connect(self, host, userid, password, ssh_key_string=None):
        _method_ = "UbuntuPlugin.connect"
        try:
            self.userid = userid
            self.password = password
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(StringIO(ssh_key_string), password)
                self.client.connect(host, username=userid, pkey=private_key, timeout=30,
                                    allow_agent=False)
            else:
                self.client.connect(host, username=userid, password=password, timeout=30,
                                    allow_agent=False)
            if not self._is_ubuntu():
                raise exceptions.InvalidDeviceException(
                    "Device is not a Ubuntu Device")
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
        if self.machine_type_model == "":
            self._get_system_details()
        return self.machine_type_model

    def get_serial_number(self):
        if self.serial_number == "":
            self._get_system_details()
        return self.serial_number

    def get_version(self):
        _method_ = "manage_ubuntu.get_version"
        version = None

        logging.info("ENTER %s", _method_)

        (_stdin, stdout, _stderr) = self.client.exec_command(self.UBUNTU_RELEASE_CMD)
        rc = stdout.channel.recv_exit_status()
        # get version if command executed successfully
        if rc == 0:
            for line in stdout.read().decode('ascii').splitlines():
                # Parse the output for version
                if self.RELEASE_TAG in line:
                    version = line.split(':')[1].strip()
                    return version
            logging.error("%s::Could not retrieve version", _method_)
            return None
        else:
            logging.error("%s::Failed to retrieve version.", _method_)
            return None

    def get_architecture(self):
        (_stdin, stdout, _stderr) = self.client.exec_command("uname -m")
        architecture = stdout.read().decode().strip()
        return architecture

    def _is_ubuntu(self):
        """Check the OS type is RHEL
        Return True if System is RHEL
        """
        (_stdin, stdout, _stderr) = self.client.exec_command("uname -a")
        return_code = stdout.channel.recv_exit_status()
        if return_code == 0:
            if stdout.read().decode().lower().find("ubuntu") >= 0:
                return True
        return False

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

    def _get_system_details(self):
        found_serial_number_tag = False
        (_stdin, stdout, _stderr) = self.client.exec_command(self.SYSTEM_INFO_CMD)
        for line in stdout.read().decode().splitlines():
            if found_serial_number_tag:
                npos = line.rfind("...")
                if npos >= 0:
                    self.serial_number = line[npos + 3:]
                found_serial_number_tag = False
            elif self.SERIAL_NUMBER_TAG in line:
                # Next line contains the serial number
                found_serial_number_tag = True
            elif self.MACHINE_TYPE_MODEL_TAG in line:
                npos = line.rfind("...")
                if npos >= 0:
                    self.machine_type_model = line[npos + 3:]
