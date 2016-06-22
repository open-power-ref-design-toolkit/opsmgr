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
