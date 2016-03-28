from enum import Enum

OPSMGRLOG = "/var/log/opsmgr.log"
OPSMGRLOG_ERROR = "/var/log/opsmgr_error.log"
OPSMGR_LOG_CONF = "/usr/local/ops_mgr/etc/logging.yaml"

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
    """ codes returned from the validate() call in device_mgr module
    """
    SUCCESS = 0
    FAILED_TO_CONNECT = 1
    CREDENTIALS_INVALID = 2
    DEVICE_TYPE_ERROR = 3
    UNSUPPORTED_FUNCTION = 10

JSON_IDENTIFIER_ATTR = 'id'
JSON_LABEL_ATTR = 'name'
