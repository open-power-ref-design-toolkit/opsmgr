# Copyright 2017, IBM US, Inc.
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

import paramiko

from backports import configparser
from opsmgr.inventory.interfaces.IManagerDeviceHook import IManagerDeviceHook
from opsmgr.inventory.interfaces.IOperationsPlugin import IOperationsPlugin
from opsmgr.inventory import plugins
from opsmgr.common import exceptions
from opsmgr.common.utils import entry_exit


class GangliaPlugin(IManagerDeviceHook, IOperationsPlugin):

    CONFIG_PATH = "/etc/ganglia"
    CREDS_DIR = CONFIG_PATH + "/.creds"
    GMOND_CFG_MASTER_FILE = "/etc/ganglia/gmetad.conf"
    VERIFY_COMMAND = "sudo /usr/sbin/gmetad -V"
    RELOAD_COMMAND = "sudo service gmetad reload"

    OPSMGR_CONF = "/etc/opsmgr/opsmgr.conf"
    GANGLIA_SECTION = "GANGLIA"
    GANGLIA_SERVER = "server"
    GANGLIA_USERID = "userid"
    GANGLIA_SSHKEY = "sshkey"

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_application_url():
        pluginApp = None
        if os.path.exists(GangliaPlugin.OPSMGR_CONF):
            try:
                parser = configparser.ConfigParser()
                parser.read(GangliaPlugin.OPSMGR_CONF, encoding='utf-8')
                web_protcol = parser.get(GangliaPlugin.GANGLIA_SECTION, "web_protocol").strip('"')
                web_proxy = parser.get(GangliaPlugin.GANGLIA_SECTION, "web_proxy").strip('"')
                web_port = parser.get(GangliaPlugin.GANGLIA_SECTION, "web_port").strip('"')
                web_path = parser.get(GangliaPlugin.GANGLIA_SECTION, "web_path").strip('"')
                pluginApp = plugins.PluginApplication("ganglia", "monitoring", web_protcol,
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
        address = device.address
        GangliaPlugin._write_gmetad_config_file(address)
        GangliaPlugin._reload_gmetad()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def add_role_post_save(device, roles):
        pass

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def remove_device_post_save(device):
        address = device.address
        GangliaPlugin._remove_config_files(address)
        GangliaPlugin._reload_gmetad()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def change_device_post_save(device, old_device_info):
        new_address = device.address
        old_address = old_device_info["ip-address"]
        if new_address != old_address:
            GangliaPlugin._change_config_files(old_address)
            GangliaPlugin._reload_gmetad()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_status():
        return (None, None)

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _reload_gmetad():
        """ Reload the gmetad server from within the
            ganglia container
        """
        try:
            client = GangliaPlugin._connect()
            # Validate the gmetad config is good
            (_stdin, stdout, _stderr) = client.exec_command(GangliaPlugin.VERIFY_COMMAND)
            rc = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            if rc != 0:
                raise exceptions.OpsException("Validation of the gmetad configuration failed:\n"
                                              "Command: " + GangliaPlugin.VERIFY_COMMAND + "\n"
                                              "Output: " + output + "\n")
            # Reload gmetad service
            (_stdin, stdout, _stderr) = client.exec_command(GangliaPlugin.RELOAD_COMMAND)
            rc = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            if rc != 0:
                raise exceptions.OpsException("service reload of gmetad failed:\n"
                                              "Command: " + GangliaPlugin.RELOAD_COMMAND + "\n"
                                              "Output: " + output + "\n")
        finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _write_gmetad_config_file(address):
        try:
            client = GangliaPlugin._connect()
            cmd = ("cat /etc/ganglia/gmetad.conf |grep " + address + "; if [ $? == 1 ]; then " +
                   "sudo sed -i 's/localhost[[:space:]]*$/" + address +
                   " &/' /etc/ganglia/gmetad.conf; service gmetad restart; fi")
            (_stdin, stdout, _stderr) = client.exec_command(cmd)
            rc = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            if rc != 0:
                raise exceptions.OpsException("Error when change gmetad config file:\n"
                                              "Command: " + cmd + "\n"
                                              "Output: " + output + "\n")
        finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _remove_config_files(address):
        try:
            client = GangliaPlugin._connect()
            cmd = ("cat /etc/ganglia/gmetad.conf |grep " + address + "; if [ $? == 0 ]; then " +
                   "sudo sed -i 's/" + address + "//'  /etc/ganglia/gmetad.conf; service gmetad restart; fi")
            (_stdin, stdout, _stderr) = client.exec_command(cmd)
            rc = stdout.channel.recv_exit_status()
            output = stdout.read().decode()
            if rc != 0:
                raise exceptions.OpsException("Error when change gmetad config file:\n"
                                              "Command: " + cmd + "\n"
                                              "Output: " + output + "\n")
        finally:
            client.close()

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def _connect():
        client = paramiko.SSHClient()
        if os.path.exists(GangliaPlugin.OPSMGR_CONF):
            try:
                parser = configparser.ConfigParser()
                parser.read(GangliaPlugin.OPSMGR_CONF, encoding='utf-8')
                server = parser.get(GangliaPlugin.GANGLIA_SECTION, GangliaPlugin.GANGLIA_SERVER).lstrip('"').rstrip('"')
                userid = parser.get(GangliaPlugin.GANGLIA_SECTION, GangliaPlugin.GANGLIA_USERID).lstrip('"').rstrip('"')
                sshkey = parser.get(GangliaPlugin.GANGLIA_SECTION, GangliaPlugin.GANGLIA_SSHKEY).lstrip('"').rstrip('"')
                prvkey = paramiko.RSAKey.from_private_key_file(sshkey)
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(server, username=userid, pkey=prvkey, timeout=30, allow_agent=False)
            except:
                raise exceptions.OpsException("connection to ganglia server failed:\n"
                                              "Server: " + server + "\n"
                                              "Userid: " + userid + "\n"
                                              "Sshkey: " + sshkey + "\n")
        return client
