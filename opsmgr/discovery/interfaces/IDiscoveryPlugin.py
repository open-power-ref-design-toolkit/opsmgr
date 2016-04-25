from abc import ABCMeta, abstractmethod

class IDiscoveryPlugin(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_type():
        """Type of provider this plugin supports
        :returns: String
        """

    @abstractmethod
    def find_resources(self):
        """
        """

    @abstractmethod
    def import_resources(self, resource_label='*', offline=False):
        """
        """

    @abstractmethod
    def connect(self, host, userid, password, ssh_key_string):
        """
        """

    @abstractmethod
    def disconnect(self):
        """
        """

