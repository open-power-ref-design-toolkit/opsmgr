from abc import ABCMeta, abstractmethod

class IManagerDeviceHook(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_application_url():
        pass

    @staticmethod
    @abstractmethod
    def add_device_pre_save(device):
        pass

    @staticmethod
    @abstractmethod
    def remove_device_pre_save(device):
        pass

    @staticmethod
    @abstractmethod
    def change_device_pre_save(device, old_device_info):
        pass

    @staticmethod
    @abstractmethod
    def add_device_post_save(device):
        pass

    @staticmethod
    @abstractmethod
    def remove_device_post_save(device):
        pass

    @staticmethod
    @abstractmethod
    def change_device_post_save(device, old_device_info):
        pass
