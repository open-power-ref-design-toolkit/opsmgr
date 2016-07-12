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

from enum import Enum

OPSMGRLOG = "/var/log/opsmgr/opsmgr.log"
OPSMGRLOG_ERROR = "/var/log/opsmgr/opsmgr_error.log"
OPSMGR_LOG_CONF = "/etc/opsmgr/logging.yaml"

class access_status(Enum):
    """ codes assigned for access status field in device_info class
    """
    SUCCESS = 0
    FAILED_TO_CONNECT = 1
    CREDENTIALS_INVALID = 2
    DEVICE_TYPE_ERROR = 3
    GATHER_IN_PROGRESS = 4
    NO_STATUS = 5

#TODO replace usage with exceptions
class validation_codes(Enum):
    """ codes returned from the validate() call in resoure_mgr module
    """
    SUCCESS = 0
    FAILED_TO_CONNECT = 1
    CREDENTIALS_INVALID = 2
    DEVICE_TYPE_ERROR = 3

class auth_method(Enum):
    """ Authentication method used to access a device
    """
    USERID_PASSWORD = 0
    SSH_KEY_AUTHENTICATION = 1

JSON_IDENTIFIER_ATTR = 'id'
JSON_LABEL_ATTR = 'name'

LOGGING_CAPABLE = 'Logging'
MONITORING_CAPABLE = 'Monitoring'
