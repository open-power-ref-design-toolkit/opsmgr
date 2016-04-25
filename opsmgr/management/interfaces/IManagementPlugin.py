from abc import ABCMeta, abstractmethod

class IManagementPlugin(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_type():
        """Type of device this plugin supports.
        :returns: String
        """

    @staticmethod
    @abstractmethod
    def get_web_url(host):
        """Return the web url to access the device
           with the given hostname or ip address
        :returns: String web url or None
        """

    @abstractmethod
    def get_version(self):
        """
        """

    @abstractmethod
    def configure(self):
        pass

    @abstractmethod
    def unconfigure(self):
        pass

    @abstractmethod
    def configure_resource(self, resource):
        pass

    @abstractmethod
    def unconfigure_resource(self, resource):
        pass

    @abstractmethod
    def connect(self, host, userid, password, ssh_key_string):
        """
        """

    @abstractmethod
    def disconnect(self):
        """
        """

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def restart(self):
        pass

