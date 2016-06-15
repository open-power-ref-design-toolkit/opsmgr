from abc import ABCMeta, abstractmethod

class IOperationsPlugin(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_application_url():
        pass
