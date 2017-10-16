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
