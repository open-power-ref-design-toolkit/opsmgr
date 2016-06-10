import os
import re

import paramiko

from backports import configparser
from opsmgr.inventory.interfaces.IManagerDeviceHook import IManagerDeviceHook
from opsmgr.inventory import persistent_mgr
from opsmgr.common import exceptions

class NagiosPlugin(IManagerDeviceHook):

    CONFIG_PATH = "/usr/local/nagios/opsmgr"
    HOSTS_DIR = CONFIG_PATH + "/hosts"
    CREDS_DIR = CONFIG_PATH + "/.creds"
    NAGIOS_CFG_MASTER_FILE = "/usr/local/nagios/etc/nagios.cfg"
    VERIFY_COMMAND = "/usr/local/nagios/bin/nagios -v " + NAGIOS_CFG_MASTER_FILE
    RELOAD_COMMAND = "service nagios reload"

    OPSMGR_CONF = "/etc/opsmgr/opsmgr.conf"
    OPSMGR_SECTION = "NAGIOS"
    OPSMGR_NAGIOS_SERVER = "server"

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
            if key.password is not None:
                password = persistent_mgr.decrypt_data(key.password)
            else:
                password = None
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
        nagios_host = NagiosPlugin._get_nagios_server()
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(nagios_host, timeout=30)

            # Validate the nagios config is good
            (_stdin, stdout, _stderr) = client.exec_command(NagiosPlugin.VERIFY_COMMAND)
            rc = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            if rc != 0:
                raise exceptions.OpsException("Validation of the nagios configuration failed:\n"
                                              "Command: " + NagiosPlugin.VERIFY_COMMAND + "\n"
                                              "Output: " + output + "\n")
            # Reload nagios service
            (_stdin, stdout, _stderr) = client.exec_command(NagiosPlugin.RELOAD_COMMAND)
            rc = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            if rc != 0:
                raise exceptions.OpsException("service reload of nagios failed:\n"
                                              "Command: " + NagiosPlugin.RELOAD_COMMAND + "\n"
                                              "Output: " + output + "\n")
        finally:
            client.close()

    @staticmethod
    def _write_creds_file(address, userid, password, key_string):
        nagios_host = NagiosPlugin._get_nagios_server()
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(nagios_host, timeout=30)
            sftp = client.open_sftp()
            try:
                sftp.mkdir(NagiosPlugin.CREDS_DIR)
            except IOError:
                #directory already exist
                pass
            file_handle = sftp.open(NagiosPlugin.CREDS_DIR + "/." + address + ".creds", 'w')
            if password is None:
                password = ""
            if key_string is None:
                key_string = ""
            file_handle.write(userid + "\n")
            file_handle.write(password + "\n")
            file_handle.write(key_string + "\n")
            file_handle.close()
        finally:
            client.close()

    @staticmethod
    def _write_config_file(label, device_type, address, hostname):
        nagios_host = NagiosPlugin._get_nagios_server()
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(nagios_host, timeout=30)
            sftp = client.open_sftp()

            source_file = NagiosPlugin.HOSTS_DIR + "/" + device_type.replace(" ", "_") + ".host"
            target_file = NagiosPlugin.HOSTS_DIR + "/" + address + ".cfg"
            source = sftp.open(source_file, 'r')
            lines = source.readlines()
            target = sftp.open(target_file, 'w')
            for line in lines:
                line = re.sub(r'#@#IP#@#', address, line)
                line = re.sub(r'#@#LABEL#@#', label, line)
                line = re.sub(r'#@#HOSTNAME#@#', hostname, line)
                target.write(line)
        finally:
            client.close()

    @staticmethod
    def _remove_config_files(address):
        nagios_host = NagiosPlugin._get_nagios_server()
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(nagios_host, timeout=30)
            sftp = client.open_sftp()

            target_file = NagiosPlugin.HOSTS_DIR + "/" + address + ".cfg"
            try:
                sftp.remove(target_file)
            except IOError:
                #file already removed
                pass
            target_file = NagiosPlugin.CREDS_DIR + "/." + address + ".creds"
            try:
                sftp.remove(target_file)
            except IOError:
                #file already removed
                pass
        finally:
            client.close()

    @staticmethod
    def _get_nagios_server():
        server = None
        if os.path.exists(NagiosPlugin.OPSMGR_CONF):
            parser = configparser.ConfigParser()
            parser.read(NagiosPlugin.OPSMGR_CONF, encoding='utf-8')
            server = parser.get(NagiosPlugin.OPSMGR_SECTION, NagiosPlugin.OPSMGR_NAGIOS_SERVER)
        return server
