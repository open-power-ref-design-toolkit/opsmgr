import logging
import subprocess
from opsmgr.common import constants
from opsmgr.common import exceptions
from opsmgr.common import utils
from opsmgr.inventory.interfaces import IManagerDevicePlugin

class PowerNodePlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    IPMI_TOOL = "/usr/local/bin/ipmitool"

    def __init__(self):
        self.host = None
        self.password = None
        self.version = None
        self.machine_type_model = ""
        self.serial_number = ""

    @staticmethod
    def get_type():
        return "PowerNode"

    @staticmethod
    def get_web_url(host):
        return "https://" + host

    @staticmethod
    def get_capabilities():
        return [constants.MONITORING_CAPABLE]

    def connect(self, host, userid, password=None, ssh_key_string=None):
        """connect to the BMC and store the mtm and serial number
        """
        _method__ = "PowerNodePlugin.connect"
        self.host = host
        self.password = password

        if ssh_key_string is not None:
            raise exceptions.AuthenticationException("SSH Key Authentication "
                                                     "is not supported for PowerNode devices")
        # the command will take a long time to dump device info if device id is not specified,
        # so assume the mtm info should be stored in device 0
        cmd_parms = [self.IPMI_TOOL, "-I", "lanplus", "-H",
                     host, "-P", password, "fru", "print", "0", "-v"]
        (rc, message) = utils.execute_command(" ".join(cmd_parms))
        if rc != 0:
            logging.warning("%s::ipmi query failed with output %s", _method__, message)
            # have to check the failure reason : password incorrect or ip incorrect
            # 1 -- "Failed to connect the device."
            #  2 -- "The userid/password combination is not valid."
            for line in message:
                if "HMAC is invalid" in line:
                    raise exceptions.ConnectionException(
                        "Unable to connect to the device using IPMI")
                elif "Get Auth Capabilities error" in line:
                    raise exceptions.AuthenticationException(
                        "password is not valid")
        for line in message:
            if "Product Part Number" in line:
                self.machine_type_model = line.split(":")[1].strip()
            elif "Product Serial" in line:
                self.serial_number = line.split(":")[1].strip()

    def disconnect(self):
        pass

    def get_machine_type_model(self):
        return self.machine_type_model

    def get_serial_number(self):
        return self.serial_number

    def get_version(self):
        _method_ = "PowerNodePlugin.get_version"
        cmd_parms = [self.IPMI_TOOL, "-I", "lanplus", "-H",
                     self.host, "-P", self.password, "mc", "info"]
        (rc, message) = utils.execute_command(" ".join(cmd_parms))
        if rc != 0:
            logging.warning("%s::ipmi query failed with output %s", _method_, message)
            raise exceptions.DeviceException("ipmi query failed with output %s" % message)
        for line in message:
            if "Firmware Revision" in line:
                self.version = line.split(":")[1].strip()
                break
        return self.version

    def get_architecture(self):
        return None

    def change_device_password(self, new_password):
        """Update the password of the ipmi default user on the BMC of the openpower server.
        """
        _method_ = "PowerNodePlugin.change_device_password"
        try:
            subprocess.check_output([self.IPMI_TOOL, "-I", "lanplus", "-H", self.host,
                                     "-P", self.password, "user", "set", "password", "1",
                                     new_password], stderr=subprocess.DEVNULL)
            verify_result = subprocess.check_output([self.IPMI_TOOL, "-I", "lanplus",
                                                     "-H", self.host, "-P", new_password, "user",
                                                     "test", "1", "20", new_password],
                                                    stderr=subprocess.DEVNULL)
            verify_result = verify_result.decode().strip()
            if verify_result.lower() != 'success':
                raise exceptions.DeviceException("Failed to login to IPMI with new password. "
                                                 "Error Message %s: " % verify_result)
        except subprocess.CalledProcessError:
            raise exceptions.DeviceException("Failed to change password on the device.")
