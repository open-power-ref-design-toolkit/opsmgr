class IntegratedManagerException(Exception):
    """
    Base exception for all integrated manager exceptions.
    Nothing should raise this exception.
    """
    pass

class IntegratedManagerDeviceException(Exception):
    """
    Base exception for exceptions raised by device plugins
    """
    pass

class AuthenticationException(IntegratedManagerDeviceException):
    """
    Exception raised when authentication failed
    """
    pass

class ConnectionException(IntegratedManagerDeviceException):
    """
    Exception raised when a connection to the device can not be made.
    """
    pass

class InvalidDeviceException(IntegratedManagerDeviceException):
    """
    Exception raised when a plugin is trying to connect to a device it
    doesn't support
    """
