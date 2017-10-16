# Copyright 2016, IBM US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
