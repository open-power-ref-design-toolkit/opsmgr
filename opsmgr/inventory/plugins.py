import socket

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

def get_operations_plugins():
    """ Returns a List of PluginApplication classes so the url for an installed application
        can be constructed. For plugins installed on the localhost, it is recommened to not use
        the host field here, but use the host or ip the user specified in the url.
        Hardcoded for Sprint 2, will be fixed in Sprint 3.
    """
    host = socket.getfqdn()
    nagios = PluginApplication("nagios", "monitoring", "http://", host, "80", "/nagios")
    elk = PluginApplication("elk", "logging", "http://", host, "8443", None)
    return [nagios, elk]
