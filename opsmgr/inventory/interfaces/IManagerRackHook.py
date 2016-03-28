from abc import ABCMeta, abstractmethod

class IManagerRackHook(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def add_rack_pre_save(rack):
        pass

    @staticmethod
    @abstractmethod
    def remove_rack_pre_save(rack):
        pass

    @staticmethod
    @abstractmethod
    def change_rack_pre_save(rack):
        pass

    @staticmethod
    @abstractmethod
    def add_rack_post_save(rack):
        pass

    @staticmethod
    @abstractmethod
    def remove_rack_post_save(rack):
        pass

    @staticmethod
    @abstractmethod
    def change_rack_post_save(rack):
        pass
