from abc import ABCMeta, abstractmethod

class IManagerDevicePlugin(object):
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

    @staticmethod
    @abstractmethod
    def get_logging_capable():
        """Return True if the device generates logs
           that can be used to monitor the health of the device.
        """

    @staticmethod
    @abstractmethod
    def get_monitoring_capable():
        """Return True if the device health can be probed by
           running periodic scripts
        """


    @abstractmethod
    def connect(self, host, userid, password, ssh_key_string):
        """
        """

    @abstractmethod
    def disconnect(self):
        """
        """

    @abstractmethod
    def get_machine_type_model(self):
        """
        """

    @abstractmethod
    def get_serial_number(self):
        """
        """

    @abstractmethod
    def get_version(self):
        """
        """

    @abstractmethod
    def get_architecture(self):
        """
        """

    #@abstractmethod
    #def get_fixes(self):

    @abstractmethod
    def change_device_password(self, new_password):
        """
        """

    #@abstractmethod
    #def change_device_network(self, new_address, subnet=None, gateway=None):
