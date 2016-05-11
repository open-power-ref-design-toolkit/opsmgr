import os
import re
import subprocess
from opsmgr.inventory.interfaces.IManagerDeviceHook import IManagerDeviceHook
from opsmgr.inventory import persistent_mgr
from opsmgr.common import exceptions

class NagiosPlugin(IManagerDeviceHook):

    NAGIOS_CONTAINER_NAME = "nagios"
    CONFIG_PATH = "/etc/opsmgr/nagios_config"
    COMMANDS_DIR = CONFIG_PATH + "/commands"
    HOSTS_DIR = CONFIG_PATH + "/hosts"
    CREDS_DIR = CONFIG_PATH + "/.creds"
    NAGIOS_CFG_MASTER_FILE = "/usr/local/nagios/etc/nagios.cfg"
    LXC_COMMAND = "lxc-attach -n " + NAGIOS_CONTAINER_NAME + " -- "
    VERIFY_COMMAND = LXC_COMMAND + "/usr/local/nagios/bin/nagios -v " + NAGIOS_CFG_MASTER_FILE
    RELOAD_COMMAND = LXC_COMMAND + "service nagios reload"
    LXC_COMMAND = "lxc-attach -n " + NAGIOS_CONTAINER_NAME

    @staticmethod
    def add_device_pre_save(device):
        pass

    @staticmethod
    def remove_device_pre_save(device):
        pass

    @staticmethod
    def change_device_pre_save(device, old_device_info):
        pass

    @staticmethod
    def add_device_post_save(device):
        label = device.label
        device_type = device.device_type
        address = device.address
        hostname = device.hostname
        userid = device.userid
        key = device.key
        if key:
            key_string = key.value
            password = persistent_mgr.decrypt_data(key.password)
        else:
            key_string = None
            password = persistent_mgr.decrypt_data(device.password)

        NagiosPlugin._write_creds_file(address, userid, password, key_string)
        NagiosPlugin._write_config_file(label, device_type, address, hostname)
        NagiosPlugin._reload_nagios()

    @staticmethod
    def remove_device_post_save(device):
        NagiosPlugin._remove_config_files(device.address)
        NagiosPlugin._reload_nagios()

    @staticmethod
    def change_device_post_save(device, old_device_info):
        NagiosPlugin._remove_config_files(old_device_info["ip-address"])
        NagiosPlugin.add_device_post_save(device)

    @staticmethod
    def _reload_nagios():
        """ Reload the nagios server from within the
            nagios container
        """
        # Validate the nagios config is good
        (rc, output) = subprocess.getstatusoutput(NagiosPlugin.VERIFY_COMMAND)
        if rc != 0:
            raise exceptions.OpsException("Validation of the nagios configuration failed:\n"
                                          "Command: " + NagiosPlugin.VERIFY_COMMAND + "\n"
                                          "Output: " + output + "\n")

        (rc, output) = subprocess.getstatusoutput(NagiosPlugin.RELOAD_COMMAND)
        if rc != 0:
            raise exceptions.OpsException("service reload of nagios failed:\n"
                                          "Command: " + NagiosPlugin.RELOAD_COMMAND + "\n"
                                          "Output: " + output + "\n")
    @staticmethod
    def _write_creds_file(address, userid, password, key_string):
        if not os.path.exists(NagiosPlugin.CREDS_DIR):
            os.mkdir(NagiosPlugin.CREDS_DIR)
        target_file = NagiosPlugin.CREDS_DIR + "/." + address + ".creds"

        if password is None:
            password = ""
        if key_string is None:
            key_string = ""
        with open(target_file, 'w') as target:
            target.write(userid + "\n")
            target.write(password + "\n")
            target.write(key_string + "\n")

    @staticmethod
    def _write_config_file(label, device_type, address, hostname):
        source_file = NagiosPlugin.HOSTS_DIR + "/" + device_type.replace(" ", "_") + ".host"
        target_file = NagiosPlugin.HOSTS_DIR + "/" + address + ".cfg"
        with open(source_file, 'r') as source:
            lines = source.readlines()
        with open(target_file, 'w') as target:
            for line in lines:
                line = re.sub(r'#@#IP#@#', address, line)
                line = re.sub(r'#@#LABEL#@#', label, line)
                line = re.sub(r'#@#HOSTNAME#@#', hostname, line)
                target.write(line)

    @staticmethod
    def _remove_config_files(address):
        target_file = NagiosPlugin.HOSTS_DIR + "/" + address + ".cfg"
        if os.path.exists(target_file):
            os.remove(target_file)
        target_file = NagiosPlugin.CREDS_DIR + "/" + address + ".creds"
        if os.path.exists(target_file):
            os.remove(target_file)

