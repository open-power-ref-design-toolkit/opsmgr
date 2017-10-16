# Copyright 2016, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import socket
import time

try:
    # python 2.7
    from StringIO import StringIO
except ImportError:
    # python 3.4
    from io import StringIO

import paramiko

from opsmgr.common import constants
from opsmgr.common import exceptions
from opsmgr.common.utils import entry_exit
from opsmgr.inventory.interfaces import IManagerDevicePlugin


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

    @staticmethod
    def get_capabilities():
        return [constants.MONITORING_CAPABLE]

    @entry_exit(exclude_index=[0, 3, 4], exclude_name=["self", "password", "ssh_key_string"])
    def connect(self, host, userid, password=None, ssh_key_string=None):
        _method_ = "RackSwitchPlugin.connect"
        self.host = host
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
                                    allow_agent=False, look_for_keys=False)
            if not self._is_rack_switch():
                raise exceptions.DeviceException(
                    "Device is not a Lenovo Rack Switch")
        except paramiko.AuthenticationException:
            logging.error("%s::userid/password combination not valid. host=%s userid=%s",
                          _method_, host, userid)
            raise exceptions.AuthenticationException(
                "userid/password combination not valid")
        except (paramiko.ssh_exception.SSHException, OSError, socket.timeout) as e:
            logging.exception(e)
            logging.error("%s::Connection timed out. host=%s", _method_, host)
            raise exceptions.ConnectionException("Unable to ssh to the device")

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def disconnect(self):
        if self.client:
            self.client.close()

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_machine_type_model(self):
        return self.machine_type_model

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_serial_number(self):
        return self.serial_number

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_version(self):
        return self.version

    def get_architecture(self):
        return None

    @entry_exit(exclude_index=[0, 1], exclude_name=["self", "new_password"])
    def change_device_password(self, new_password):
        _method_ = "RackSwitchPlugin.change_device_password"

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
            raise exceptions.DeviceException(message)

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def _is_rack_switch(self):
        """Check if the Device type is Lenovo Rack Switch
        """
        (_stdin, stdout, _stderr) = self.client.exec_command(self.SHOW_VERSION_COMMAND)
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

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def _check_connection(self):
        """ The lenovo switch seems to drop a connection really quick if not active in
            shell. Verify the connection is active before using it, and if necessary
            create a new connection
        """
        transport = self.client.get_transport()
        if transport is None or transport.is_active() is False:
            if self.ssh_key_string:
                private_key = paramiko.RSAKey.from_private_key(StringIO(self.ssh_key_string),
                                                               self.password)
                self.client.connect(self.host, username=self.userid, pkey=private_key, timeout=30,
                                    allow_agent=False)
            else:
                self.client.connect(self.host, username=self.userid, password=self.password,
                                    timeout=30, allow_agent=False, look_for_keys=False)
