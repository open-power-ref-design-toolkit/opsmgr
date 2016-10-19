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

import os
import re

import paramiko

from backports import configparser
from opsmgr.inventory.interfaces.IManagerDeviceHook import IManagerDeviceHook
from opsmgr.inventory.interfaces.IOperationsPlugin import IOperationsPlugin
from opsmgr.inventory import persistent_mgr, plugins
from opsmgr.common import exceptions
from opsmgr.common.utils import entry_exit

class NagiosPlugin(IManagerDeviceHook, IOperationsPlugin):

    CONFIG_PATH = "/usr/local/nagios/opsmgr/nagios_config"
    HOSTS_DIR = CONFIG_PATH + "/hosts"
    ROLES_DIR = CONFIG_PATH + "/roles"
    CREDS_DIR = CONFIG_PATH + "/.creds"
    NAGIOS_CFG_MASTER_FILE = "/usr/local/nagios/etc/nagios.cfg"
    VERIFY_COMMAND = "sudo /usr/local/nagios/bin/nagios -v " + NAGIOS_CFG_MASTER_FILE
    RELOAD_COMMAND = "sudo service nagios reload"

    OPSMGR_CONF = "/etc/opsmgr/opsmgr.conf"
    NAGIOS_SECTION = "NAGIOS"
    NAGIOS_SERVER = "server"
    NAGIOS_USERID = "userid"
    NAGIOS_SSHKEY = "sshkey"
    
    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_application_url():
        pluginApp = None
        if os.path.exists(NagiosPlugin.OPSMGR_CONF):
            try:
                parser = configparser.ConfigParser()
                parser.read(NagiosPlugin.OPSMGR_CONF, encoding='utf-8')
                web_protcol = parser.get(NagiosPlugin.NAGIOS_SECTION, "web_protocol").strip('"')
                web_proxy = parser.get(NagiosPlugin.NAGIOS_SECTION, "web_proxy").strip('"')
                web_port = parser.get(NagiosPlugin.NAGIOS_SECTION, "web_port").strip('"')
                web_path = parser.get(NagiosPlugin.NAGIOS_SECTION, "web_path").strip('"')
                pluginApp = plugins.PluginApplication("nagios", "monitoring", web_protcol,
                                                      web_proxy, web_port, web_path)
            except configparser.Error:
               # App missing from /etc/opsmgr/opsmgr.conf, may not be installed
               pass
        return pluginApp

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
    @entry_exit(exclude_index=[], exclude_name=[])
    def add_device_post_save(device):
        label = device.label
        device_type = device.resource_type
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
        NagiosPlugin._write_host_config_file(label, device_type, address, hostname)
        NagiosPlugin._reload_nagios()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def add_role_post_save(device, roles):
        hostname = device.hostname
        for resource_role in roles:
            role = resource_role.role
            additional_data = resource_role.additional_data
            NagiosPlugin._write_role_config_file(hostname, role, additional_data)
        NagiosPlugin._reload_nagios()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def remove_device_post_save(device):
        NagiosPlugin._remove_config_files(device.hostname)
        NagiosPlugin._reload_nagios()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def change_device_post_save(device, old_device_info):
        NagiosPlugin._remove_config_files(old_device_info["hostname"])
        NagiosPlugin.add_device_post_save(device)

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _reload_nagios():
        """ Reload the nagios server from within the
            nagios container
        """
        try:
            client = NagiosPlugin._connect()
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
        #try:
            client = NagiosPlugin._connect()
            sftp = client.open_sftp()
            try:
                NagiosPlugin._mkdir(client, NagiosPlugin.CREDS_DIR)
                NagiosPlugin._chown(client, NagiosPlugin.CREDS_DIR, 'nagios', 'nagios')
            except IOError:
                #directory already exist
                pass
            target_file = "/tmp/" + address + ".crd"
            file_handle = sftp.open(target_file, 'w')
            if password is None:
                password = ""
            if key_string is None:
                key_string = ""
            file_handle.write(userid + "\n")
            file_handle.write(password + "\n")
            file_handle.write(key_string + "\n")
            file_handle.close()
            NagiosPlugin._chmod(client, target_file, '0600')
            NagiosPlugin._chown(client, target_file, 'nagios', 'nagios')
            NagiosPlugin._mv(client, target_file, NagiosPlugin.CREDS_DIR)
        #finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _write_host_config_file(label, device_type, address, hostname):
        try:
            client = NagiosPlugin._connect()
            sftp = client.open_sftp()
            try:
                NagiosPlugin._mkdir(client, NagiosPlugin.HOSTS_DIR)
                NagiosPlugin._chown(client, NagiosPlugin.HOSTS_DIR, 'nagios', 'nagios')
            except IOError:
                #directory already exist
                pass
            source_file = NagiosPlugin.HOSTS_DIR + "/" + device_type.replace(" ", "_") + ".host"
            target_file = "/tmp/" + hostname + ".cfg"
            source = sftp.open(source_file, 'r')
            lines = source.readlines()
            target = sftp.open(target_file, 'w')
            for line in lines:
                line = re.sub(r'#@#IP#@#', address, line)
                line = re.sub(r'#@#LABEL#@#', label, line)
                line = re.sub(r'#@#HOSTNAME#@#', hostname, line)
                target.write(line)
            NagiosPlugin._chmod(client, target_file, '0644')
            NagiosPlugin._chown(client, target_file, 'nagios', 'nagios')
            NagiosPlugin._mv(client, target_file, NagiosPlugin.HOSTS_DIR)
        finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _write_role_config_file(hostname, role, additional_data):
        try:
            client = NagiosPlugin._connect()
            sftp = client.open_sftp()
            try:
                NagiosPlugin._mkdir(client, NagiosPlugin.HOSTS_DIR)
                NagiosPlugin._chown(client, NagiosPlugin.HOSTS_DIR, "nagios", "nagios")
                NagiosPlugin._mkdir(client, NagiosPlugin.ROLES_DIR)
                NagiosPlugin._chown(client, NagiosPlugin.ROLES_DIR, "nagios", "nagios")
            except IOError:
                # directory already exists
                pass
            source_file = NagiosPlugin.ROLES_DIR + '/' + role.replace(' ', '_') + ".role"
            if not NagiosPlugin._exists(sftp, source_file):
                source_file = NagiosPlugin.ROLES_DIR + "/generic.role"
            target_file = "/tmp/" + hostname + '-' + role + ".cfg"
            source = sftp.open(source_file, 'r')
            lines = source.readlines()
            target = sftp.open(target_file, 'w')
            data = '"'
            try:
                for k, v in additional_data:
                    data = data + k + '=' + v + ' '
            except:
                # additional_data not defined
                pass
            data = data + '"'
            for line in lines:
                line = re.sub(r'#@#ROLE#@#', role, line)
                line = re.sub(r'#@#DATA#@#', data, line)
                line = re.sub(r'#@#HOSTNAME#@#', hostname, line)
                target.write(line)
            NagiosPlugin._chmod(client, target_file, '0644')
            NagiosPlugin._chown(client, target_file, 'nagios', 'nagios')
            NagiosPlugin._mv(client, target_file, NagiosPlugin.HOSTS_DIR)
        finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _remove_config_files(hostname):
        #try:
            client = NagiosPlugin._connect()
            target_file = NagiosPlugin.HOSTS_DIR + "/" + hostname + "*.cfg"
            try:
                NagiosPlugin._rm(client, target_file)
            except IOError:
                #file already removed
                pass
            target_file = NagiosPlugin.CREDS_DIR + "/." + hostname + ".creds"
            try:
                NagiosPlugin._rm(client, target_file)
            except IOError:
                #file already removed
                pass
        #finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _connect():
        client = paramiko.SSHClient()
        if os.path.exists(NagiosPlugin.OPSMGR_CONF):
            try:
                parser = configparser.ConfigParser()
                parser.read(NagiosPlugin.OPSMGR_CONF, encoding='utf-8')
                server = parser.get(NagiosPlugin.NAGIOS_SECTION, NagiosPlugin.NAGIOS_SERVER).lstrip('"').rstrip('"')
                userid = parser.get(NagiosPlugin.NAGIOS_SECTION, NagiosPlugin.NAGIOS_USERID).lstrip('"').rstrip('"')
                sshkey = parser.get(NagiosPlugin.NAGIOS_SECTION, NagiosPlugin.NAGIOS_SSHKEY).lstrip('"').rstrip('"')
                prvkey = paramiko.RSAKey.from_private_key_file(sshkey)
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(server, username=userid, pkey=prvkey, timeout=30, allow_agent=False)
            except:
                raise exceptions.OpsException("connection to nagios server failed:\n"
                                              "Server: " + server + "\n"
                                              "Userid: " + userid + "\n"
                                              "Sshkey: " + sshkey + "\n")
        return client

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _mkdir(client, dirname):
        (_stdin, stdout, _stderr) = client.exec_command('sudo mkdir -p ' + dirname)
        rc = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        if rc != 0:
            raise exceptions.OpsException("Error when creating directory:\n"
                                          "Command: " + 'sudo mkdir -p ' + dirname + "\n"
                                          "Output: " + output + "\n")

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _mv(client, src, dst):
        (_stdin, stdout, _stderr) = client.exec_command('sudo mv -f ' + src + ' ' + dst)
        rc = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        if rc != 0:
            raise exceptions.OpsException("Error when moving file or directory:\n"
                                          "Command: " + 'sudo mv -f ' + src + ' ' + dst + "\n"
                                          "Output: " + output + "\n")

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _chmod(client, target, perms):
        (_stdin, stdout, _stderr) = client.exec_command('sudo chmod -R ' + perms + ' ' + target)
        rc = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        if rc != 0:
            raise exceptions.OpsException("Error when changing ownership of file or directory:\n"
                                          "Command: " + 'sudo chmod -R ' + perms + ' ' + target + "\n"
                                          "Output: " + output + "\n")

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _chown(client, target, user, group):
        (_stdin, stdout, _stderr) = client.exec_command('sudo chown -R ' + user + "." + group + ' ' + target)
        rc = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        if rc != 0:
            raise exceptions.OpsException("Error when changing ownership of file or directory:\n"
                                          "Command: " + 'sudo chown -R ' + user + "." + group + ' ' + target + "\n"
                                          "Output: " + output + "\n")

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _rm(client, target):
        (_stdin, stdout, _stderr) = client.exec_command('sudo rm -f ' + target)
        rc = stdout.channel.recv_exit_status()
        output = stdout.read().decode()
        if rc != 0:
            raise exceptions.OpsException("Error when removing file or directory:\n"
                                          "Command: " + 'sudo rm -f ' + target + "\n"
                                          "Output: " + output + "\n")

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _exists(sftp, target):
        try:
            sftp.stat(target)
        except IOError, e:
            if e[0] == 2:
                return False
            raise
        else:
            return True



