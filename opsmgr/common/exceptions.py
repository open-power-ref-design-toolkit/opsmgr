
class OpsException(Exception):
    """
    Base exception for all operational management exceptions
    """
    pass

class ConnectionException(OpsException):
    """
    Exception raised when a remote connection can not be made
    """
    pass

class AuthenticationException(OpsException):
    """
    Exception raised when authentication fails
    """
    pass

class DeviceException(OpsException):
    """
    Base exception for exceptions raised by inventory devices
    """
    pass

class InvalidDeviceException(DeviceException):
    """
    Exception raised when a plugin is trying to connect to a device it
    doesn't support
    """

class ProviderException(OpsException):
    """
    Base exception for exceptions raised by discovery providers
    """
    pass

