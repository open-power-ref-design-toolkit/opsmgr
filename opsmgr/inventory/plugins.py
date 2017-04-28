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

from opsmgr.common.utils import entry_exit, load_plugin_by_namespace

I_OPERATIONS_PLUGINS = "opsmgr.inventory.interfaces.IOperationsPlugin"

class PluginApplication():

    def __init__(self, name, function, protocol, host, port, path):
        self.name = name
        self.function = function
        self.protocol = protocol
        self.host = host
        self.port = port
        self.path = path

    def get_name(self):
        return self.name
    def get_function(self):
        return self.function
    def get_protocol(self):
        return self.protocol
    def get_host(self):
        return self.host
    def get_port(self):
        return self.port
    def get_path(self):
        return self.path

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_operations_plugins():
        """ Returns a List of PluginApplication classes so the url for an installed application
            can be constructed. For plugins installed on the localhost, it is recommened to not use
            the host field here, but use the host or ip the user specified in the url.
        """
        plugin_apps = []
        plugins = PluginApplication._load_operations_plugins()
        for _plugin_name, plugin_class in plugins.items():
            plugin_app = plugin_class.get_application_url()
            if plugin_app is not None:
                plugin_apps.append(plugin_app)
        return plugin_apps

    @staticmethod
    @entry_exit(exclude_index=[], exclude_name=[])
    def get_plugins_status():
        """ Returns two list of Strings for critical and warning messages from
            all plugins on the localhost.
        """
        critical_messages = []
        warning_messages = []
        plugins = PluginApplication._load_operations_plugins()
        for _plugin_name, plugin_class in plugins.items():
            (crit, warn) = plugin_class.get_status()
            if crit is not None:
                critical_messages.extend(crit)
            if warn is not None:
                warning_messages.extend(warn)
        return (critical_messages, warning_messages)

    @staticmethod
    def _load_operations_plugins():
        """
        Find the operations plugins and return them as a
        dictonary[name]=plugin class
        """
        return load_plugin_by_namespace(I_OPERATIONS_PLUGINS)
