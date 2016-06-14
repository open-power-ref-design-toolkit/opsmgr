import logging
from opsmgr.common import constants
from opsmgr.common import exceptions
from opsmgr.common.utils import entry_exit, execute_command
from opsmgr.inventory.interfaces import IManagerDevicePlugin

class PowerNodePlugin(IManagerDevicePlugin.IManagerDevicePlugin):

    IPMI_TOOL = "/usr/local/bin/ipmitool"

    def __init__(self):
        self.host = None
        self.userid = None
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

    @entry_exit(exclude_index=[0, 3, 4], exclude_name=["self", "password", "ssh_key_string"])
    def connect(self, host, userid, password=None, ssh_key_string=None):
        """connect to the BMC and store the mtm and serial number
        """
        _method_ = "PowerNodePlugin.connect"
        self.host = host
        self.userid = userid
        self.password = password

        if ssh_key_string is not None:
            raise exceptions.AuthenticationException("SSH Key Authentication "
                                                     "is not supported for PowerNode devices")
        cmd_parms = [self.IPMI_TOOL, "-I", "lanplus", "-H",
                     host, "-U", userid, "-P", password, "fru", "print"]
        (_rc, stdout, stderr) = execute_command(" ".join(cmd_parms))
        logging.warning("%s::ipmi query standard error output %s", _method_, stderr)
        for line in stderr:
            if "Unable to establish IPMI" in line:
                raise exceptions.ConnectionException(
                    "Unable to connect to the device using IPMI")
        for line in stdout:
            if "Chassis Part Number" in line:
                self.machine_type_model = line.split(":")[1].strip()
            elif "Chassis Serial" in line:
                self.serial_number = line.split(":")[1].strip()

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def disconnect(self):
        pass

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_machine_type_model(self):
        return self.machine_type_model

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_serial_number(self):
        return self.serial_number

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_version(self):
        _method_ = "PowerNodePlugin.get_version"
        cmd_parms = [self.IPMI_TOOL, "-I", "lanplus", "-H", self.host,
                     "-U", self.userid, "-P", self.password, "mc", "info"]
        (rc, stdout, stderr) = execute_command(" ".join(cmd_parms))
        if rc != 0:
            logging.warning("%s::ipmi query failed with output %s", _method_, stderr)
            raise exceptions.DeviceException("ipmi query failed with output %s" % stderr)
        for line in stdout:
            if "Firmware Revision" in line:
                self.version = line.split(":")[1].strip()
                break
        return self.version

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def get_architecture(self):
        return None

    @entry_exit(exclude_index=[0, 1], exclude_name=["self", "new_password"])
    def change_device_password(self, new_password):
        """Update the password of the ipmi default user on the BMC of the openpower server.
        """
        _method_ = "PowerNodePlugin.change_device_password"
        user_number = self._get_user_number()
        cmd_parms = [self.IPMI_TOOL, "-I", "lanplus", "-H", self.host, "-U", self.userid,
                     "-P", self.password, "user", "set", "password", user_number, new_password]
        (rc, _stdout, stderr) = execute_command(" ".join(cmd_parms))
        if rc != 0:
            logging.error("%s::ipmi password change failed with output %s", _method_, stderr)
            raise exceptions.DeviceException("ipmi password change failed with output %s" % stderr)

    @entry_exit(exclude_index=[0], exclude_name=["self"])
    def _get_user_number(self):
        """Each user in IPMI has a number associated with that is used on the command line
           when modifying a user. This method will find the number associated with the userid
        """
        _method_ = "PowerNodePlugin._get_user_number"
        user_id = None
        cmd_parms = [self.IPMI_TOOL, "-I", "lanplus", "-H", self.host, "-U", self.userid,
                     "-P", self.password, "user", "list"]
        (rc, stdout, stderr) = execute_command(" ".join(cmd_parms))
        if rc != 0:
            logging.warning("%s::ipmi query failed with output %s", _method_, stderr)
            raise exceptions.DeviceException("ipmi query failed with output %s" % stderr)
        for line in stdout:
            ids = line.split()[0]
            user = line.split()[1]
            if user == self.userid:
                user_id = ids
                break
        if user_id:
            return user_id
        else:
            raise exceptions.DeviceException("Failed to determine the id for the user: %s" %
                                             self.userid)

