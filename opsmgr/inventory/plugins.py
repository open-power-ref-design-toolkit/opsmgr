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
    def _load_operations_plugins():
        """
        Find the operations plugins and return them as a
        dictonary[name]=plugin class
        """
        return load_plugin_by_namespace(I_OPERATIONS_PLUGINS)
