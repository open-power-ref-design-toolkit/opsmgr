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

from backports import configparser
from opsmgr.inventory.interfaces.IOperationsPlugin import IOperationsPlugin
from opsmgr.inventory import plugins
from opsmgr.common.utils import entry_exit

class ELKPlugin(IOperationsPlugin):

    OPSMGR_CONF = "/etc/opsmgr/opsmgr.conf"
    ELK_SECTION = "ELK"

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_application_url():
        pluginApp = None
        if os.path.exists(ELKPlugin.OPSMGR_CONF):
            try:
                parser = configparser.ConfigParser()
                parser.read(ELKPlugin.OPSMGR_CONF, encoding='utf-8')
                web_protcol = parser.get(ELKPlugin.ELK_SECTION, "web_protocol")
                web_proxy = parser.get(ELKPlugin.ELK_SECTION, "web_proxy")
                web_port = parser.get(ELKPlugin.ELK_SECTION, "web_port")
                application = "ELK"
                capability = "logging"
                pluginApp = plugins.PluginApplication(application, capability, web_protcol,
                                                      web_proxy, web_port, None)
            except configparser.Error:
               # App missing from /etc/opsmgr/opsmgr.conf, may not be installed
               pass
        return pluginApp

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_status():
        return (None, None)
 
