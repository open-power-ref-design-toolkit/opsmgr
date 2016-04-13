import gettext
# establish _ in global namespace
gettext.install('opsmgr', '/usr/share/locale')
import logging
import socket

try:
    #python 2.7
    from StringIO import StringIO
except ImportError:
    #python 3.4
    from io import StringIO

from datetime import datetime
from stevedore import extension

import opsmgr.inventory.constants as constants
import opsmgr.inventory.persistent_mgr as persistent_mgr
import opsmgr.inventory.IntegratedManagerException as IntegratedManagerException

from opsmgr.inventory.data_model import Rack, Device, Key
from opsmgr.inventory.utils import entry_exit, is_valid_address

I_MANAGER_DEVICE_PLUGIN = "opsmgr.inventory.interfaces.IManagerDevicePlugin"
I_MANAGER_DEVICE_HOOK = "opsmgr.inventory.interfaces.IManagerDeviceHook"
I_MANAGER_RACK_HOOK = "opsmgr.inventory.interfaces.IManagerRackHook"

def get_racktag_text_id(tag_name):
    racktag_id = {
        'rackid': _('id'),
        'label': _('label'),
        'mgrRackId': _('manager rack'),
        'location': _('rack location'),
        'role': _('role'),
        'data-center': _('data center'),
        'notes': _('notes'),
    }
    if tag_name in racktag_id:
        return racktag_id[tag_name]
    return tag_name

def get_devicetag_text_id(tag_name):
    devicetag_id = {
        'deviceid': _('id'),
        'label': _('label'),
        'rackid': _('rack id'),
        'rack-eia-location': _('rack location'),
        'machine-type-model': _('machine type model'),
        'serial-number': _('serial number'),
        'ipv4-service-address': _('ipv4 address'),
        'hostname': _('hostname'),
        'userid': _('userid'),
        'password': _('password'),
        'device-type': _('device type'),
        'auth-method': _('authentication method'),
        'status': _('access status'),
        'statusTime': _('access timestamp')
    }

    if tag_name in devicetag_id:
        return devicetag_id[tag_name]
    return tag_name

def _load_plugin_by_namespace(namespace):
    plugins = {}
    extensions = extension.ExtensionManager(namespace=namespace)

    for ext in extensions:
        plugins[ext.name] = ext.plugin()
    return plugins

def load_device_plugins():
    """
    Find the device plugins and return them as a
    dictonary[name]=plugin class
    """
    return _load_plugin_by_namespace(I_MANAGER_DEVICE_PLUGIN)

def load_inventory_device_plugins():
    """
    Find the inventory device plugins and return them as
    dictonary[name]=plugin class
    """
    return _load_plugin_by_namespace(I_MANAGER_DEVICE_HOOK)

def load_inventory_rack_plugins():
    """
    Find the inventory rack plugins and return them as
    dictonary[name]=plugin class
    """
    return _load_plugin_by_namespace(I_MANAGER_RACK_HOOK)

def push_message(message, new_message):
    if new_message is not None and len(new_message) > 0:
        if message:
            message = message + '\n' +  new_message
        else:
            message = new_message
    return message

def get_labels_message(items, is_return_deviceid=False, id_attr_name="device_id"):
    """get the labels from the list of items using the label attr of the object,
    otherwise use the idAttrName passed

    Args:
        items: list of items to get values for
        isReturnDeviceId: if true returns the device ids for the items as the list of items
        idAttrName: name of attribute name to use for the device id value when prior arg is true
    Returns:
        string with list of lables or device ids based on input
    """
    labels_message = ""
    for obj in items:
        if len(labels_message) > 0:
            labels_message += ', '
        if isinstance(obj, str):
            labels_message += obj
        else:
            labels_message += obj.label if not is_return_deviceid else getattr(
                obj, id_attr_name)
    return labels_message

def _check_device_exist(address):
    devices = persistent_mgr.get_all_devices()
    if not devices:
        return False
    for device in devices:
        if address == device.address:
            return True
    return False

def check_device_exist_by_props(device_type, mtm, serialnum):
    if device_type is None:
        return False
    if serialnum is None:
        serialnum = ''
    if mtm is None:
        mtm = ''
    (devices, dummy_not_found_types) = persistent_mgr.get_devices_by_device_type([device_type])
    found = False
    for device in devices:
        if device.serial == serialnum and device.mtm == mtm:
            found = True
    return found

def add_rack(label, data_center='', location='', notes=''):
    """add rack to the list of racks in the configuration managed

    Args:
        label: label for rack
        data_center: data center location (free form)
        location: location in the data center (free form)
        notes: freeform notes associated with this rack to describe its use, mgmt, etc.
    Returns:
        RC: integer return code
        Message: string with message associated with return code
    """
    _method_ = 'device_mgr.add_rack'
    label = label.strip()
    message = None

    # get existing rack info for next set of checks
    racks_info = persistent_mgr.get_all_racks()

    for rack in racks_info:
        if rack.label == label:
            message = _(
                "The rack label (%s) conflicts with a rack label in the configuration file.") \
                % label
            return 101, message

    rack_info = Rack()
    rack_info.label = label
    rack_info.location = location
    rack_info.data_center = data_center
    rack_info.notes = notes

    hooks = load_inventory_rack_plugins()
    hook_name = 'unknown' #keeps pylint happy
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_rack_pre_save(rack_info)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s). Unable to add rack: Reason: %s") % (hook_name, e)
        return 102, message

    persistent_mgr.add_racks([rack_info])

    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_rack_post_save(rack_info)
    except Exception as e:
        logging.exception(e)
        message = _("After rack was added. Error in plugin (%s): %s") % (hook_name, e)

    logging.info("%s::add rack(%s) success", _method_, label)
    if not message:
        message = _("Added rack successfully.")
    return 0, message

def validate_address(address):
    """Make sure the address is a valid IPv4 address and is not in use

    Args:
        address:  proposed new IPv4 Address
    Returns:
        rc:   return code
            0   if IP address is valid
            111 if IP address is invalid form
            108 if IP address is already in use by another inventoried system.
    """
    _method_ = "device_mgr.validate_address"
    if not is_valid_address(address):
        logging.error("%s::IP address is invalid (%s).", _method_, address)
        message = _("IP address is invalid (%s).") % (address)
        return 111, message
    if _check_device_exist(address):
        error_message = _("The IP address '%s' that is specified is already being used by"
                          " another device or virtual machine in the network.") % (address)
        return 108, error_message
    return 0, ""


def validate_label(label):
    """Make sure the label is not in use

    Args:
        label:  proposed new label
    Returns:
        rc:   return code
                0 if all ok
                101 if label already in use
        message: error message associated with failure

    """
    devices_info = persistent_mgr.get_all_devices()
    for device in devices_info:
        if device.label == label:
            error_message = _("The label '%s' that is specified is already being used by another"
                              " device or virtual machine in the network.") % (label)
            return 101, error_message
    return 0, ""

def add_device(label, device_type, address, userid, password, rackid='', rack_location='',
               ssh_key=None):

    """add device to the list of devices in the configuration managed

    Args:
        label: label for device
        device_type: type of device from device enumeration
        address: IP address of device
        userid:  string with device userid
        password:  string with device password (or password for ssh key)
        rackid: string identify rack id, if not specified will default to management rack
        rack:_location string identifying rack location
        ssh_key: io.StringIO stream of the ssh key
    Returns:
        RC: integer return code
        Message: string with message associated with return code
    """
    _method_ = 'device_mgr.add_device'
    message = None
    label = label.strip()
    address = address.strip()
    ipv4 = ""
    hostname = ""
    # check if the address is hostname or ipv4
    if is_valid_address(address):
        ipv4 = address
        hostname = socket.gethostbyaddr(address)[0]
    else:
        hostname = socket.getfqdn(address)
        ipv4 = socket.gethostbyname(hostname)

    rc, message = validate_address(ipv4)

    if rc != 0:
        return rc, message
    rc, message = validate_label(label)
    if rc != 0:
        return rc, message

    validate_ret, device_type, mtm, serialnum, version = validate(
        ipv4, userid, password, device_type, ssh_key)
    if validate_ret != 0:
        logging.error(
            "%s::failed to add device, validate device(%s) return value(%d).",
            _method_, label, validate_ret)
        error_message = None
        if validate_ret == 1:
            error_message = _("Failed to connect the device.")
        elif validate_ret == 2:
            error_message = _("The userid/password combination is not valid.")
        elif validate_ret == 3:
            error_message = _("No plugin capable of managing device was found.")
        elif validate_ret == 109:
            error_message = _("Connect timeout.")
        return validate_ret, error_message
    else:
        if check_device_exist_by_props(device_type, mtm, serialnum):
            logging.error("%s::failed to add device, device(machine-type-model=%s, "
                          "serial-number=%s) is already managed.", _method_, mtm, serialnum)
            error_message = _("The device is not added, a device with the same serial number and"
                              " machine type model is found in the configuration file.")
            return 110, error_message

    # figure out the rack ID to add the device under
    if rackid:
        rack = persistent_mgr.get_rack_by_id(rackid)
    else:
        # don't have a rack id. find first the rack and assign it there
        try:
            racks_info = persistent_mgr.get_all_racks()
            rack = racks_info[0]
        except IndexError:
            #No rack exist, create one
            rack = Rack()
            rack.label = "Default"
            persistent_mgr.add_racks([rack])

    device_info = Device()
    device_info.rack = rack
    device_info.eia_location = rack_location
    device_info.machine_type_model = mtm
    device_info.serial_number = serialnum
    device_info.address = ipv4
    device_info.hostname = hostname
    device_info.userid = userid
    if password and not ssh_key:
        device_info.password = persistent_mgr.encrypt_data(password)
    device_info.label = label
    device_info.device_type = device_type
    device_info.version = version
    device_info.status = constants.access_status.SUCCESS.value
    device_info.statusTime = datetime.utcnow()
    # we are adding the device after validation, set validated.
    device_info.validated = True

    hooks = load_inventory_device_plugins()
    hook_name = 'unknown' #keeps pylint happy
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_device_pre_save(device_info)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s). Unable to add device: Reason: %s") % (hook_name, e)
        return 102, message

    persistent_mgr.add_devices([device_info])

    if ssh_key:
        key_info = Key()
        key_info.device = device_info
        key_info.type = "RSA"
        key_info.value = ssh_key.getvalue()
        if password:
            key_info.password = persistent_mgr.encrypt_data(password)
        persistent_mgr.add_ssh_keys([key_info])

    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_device_post_save(device_info)
    except Exception as e:
        logging.exception(e)
        message = _("After device was added. Error in plugin (%s): %s") % (hook_name, e)

    if not message:
        message = _("Added device successfully.")
    return 0, message

def change_device_password(label=None, deviceid=None, old_password=None, new_password=None):

    method_ = 'device_mgr.device_change_password'
    message = None
    label = label.strip()

    # gain access to the device object for the targeted item.
    if deviceid is not None:
        device = persistent_mgr.get_device_by_id(deviceid)
        device_des = deviceid
    else:
        device = persistent_mgr.get_device_by_label(label)
        device_des = label
    if not device:
        logging.error("%s::Failed to change device password device (%s) is not found.",
                      method_, device_des)
        message = _(
            "Failed to change device password, device (%s) is not found.") % (device_des)
        return 101, message
    device_type = device.device_type

    plugins = load_device_plugins()

    if device_type:
        plugin = plugins[device_type]
        try:
            plugin.connect(device.address, device.userid, old_password)
            plugin.change_device_password(new_password)
            plugin.disconnect()
        except KeyError:
            logging.error("%s::plugin(%s) not found", method_, device_type)
        except Exception as e:
            logging.exception(e)
            logging.warning("%s:plugin. Exception running change_device_password: %s",
                            method_, e)

   # Now change the password in the database
    device.password = persistent_mgr.encrypt_data(new_password)
    if not message:
        message = _("Changed device password successfully.")
    return 0, message

def list_devices(labels=None, isbriefly=False, device_types=None, deviceids=None,
                 list_device_id=False, is_detail=False, racks=None):
    """Get a list of devices based on the information present in that arguments.
    Device ID's will override labels.  labels or device ids will limit response to those items.

    Args:
        labels: list of labels to get device info for.
        isbriefly: indicates if brief response desired (defaults to just labels)
        device_types: list of device types to limit return device information to.
        deviceids:
        list_device_id: to include the device ID in the returned data set to True
        is_detail: Set to true to include detailed information for the object
        racks: list of rack identifiers containing rack ids

    Returns:
        integer with return code
        dictionary with results based on parameters
            Dictionary entries:
                message:  any message returned for the processing of this method
                column_titles: dictionary of column titles accessed via the tag name they represent.
                devices:  list of device information packed in a dictionary structure
                racks: list of rack information packed in a dictionary structure
    """
    _method_ = 'device_mgr.list_devices'
    logging.debug("ENTRY %s", _method_)
    all_tags = ['label', 'rackid', 'rack-eia-location', 'machine-type-model',
                'serial-number', 'ip-address', 'hostname', 'userid', 'version', 'device-type',
                'status', 'statusTime']
    brief_tags = ['label']
    result = {}

    # get the list of device types requested as an array
    device_types_array = device_types
    # get the rack ids requested as an array
    rack_ids_array = racks
    # decide the set of data to return
    tags = all_tags
    if is_detail:
        isbriefly = False
    if isbriefly:
        tags = brief_tags
    # include deviceid info in returned data if requested.
    if list_device_id:
        tags.insert(0, 'deviceid')

    # get devices based on labels and device ids
    if deviceids is not None:
        devices, dummy_not_found_values = persistent_mgr.get_devices_by_ids(
            deviceids)
    elif labels is not None:
        devices, dummy_not_found_values = persistent_mgr.get_devices_by_labels(
            labels)
    else:
        devices = persistent_mgr.get_all_devices()

    # check if labels returned anything if specified
    if len(devices) == 0 and labels:
        message = _("No device labeled as \'%s\'") % labels
        result['message'] = message
        logging.debug("EXIT %s label not found", _method_)
        return 101, result

    logging.debug("%s: before filtering", _method_)

    # possibly filter by device types if specified
    filtered_result_devices = []
    if device_types_array:
        for device in devices:
            if device.device_type in device_types_array:
                filtered_result_devices.append(device)
    else:
        filtered_result_devices = devices

    # possibly filter by rack ids
    rack_filtered_devices = []
    if rack_ids_array:
        for device in filtered_result_devices:
            if device.rack_id in rack_ids_array:
                rack_filtered_devices.append(device)
    else:
        rack_filtered_devices = filtered_result_devices

    logging.debug("%s: before add table info", _method_)

    # add table column info
    table_columns_titles = []
    result['column_tags'] = tags
    for tag in tags:
        table_columns_titles.append(get_devicetag_text_id(tag))
    result['column_titles'] = table_columns_titles

    logging.debug("%s: before add devices to output", _method_)
    result_devices = []
    for device in rack_filtered_devices:
        device_dict = device.to_dict_obj()
        device_output = {}
        for tag in tags:
            tag_value = device_dict.get(tag)
            if tag == 'machine-type-model' or tag == 'serial-number':
                tag_value = tag_value.replace(',', ' ')
            device_output[tag] = tag_value

        # check if caller wants extra detail.
        if is_detail:
            management_interfaces = device_dict.get('management-interface')
            # if any additional interfaces to report for device.
            if management_interfaces:
                result_extra_interfaces = []
                for management_interface in management_interfaces:
                    additional_interfaces_info = {}
                    additional_interfaces_info[
                        'qualifier'] = management_interface.get('qualifier')
                    additional_interfaces_info[
                        'ipv4-address'] = management_interface.get('ipv4-address')
                    result_extra_interfaces.append(additional_interfaces_info)
                device_output['management-interface'] = result_extra_interfaces

        # add final form of device info to result
        result_devices.append(device_output)

    result['devices'] = result_devices

    message = ""
    result['message'] = message
    logging.debug("EXIT %s normal", _method_)
    return 0, result

def list_racks(labels=None, isbriefly=False, rackids=None):
    """Get a list of racks based on the information present in that arguments.

    Args:
        labels: specify racks as list of labels
        rackids:Specify racks as list to get the data returned limited to systems on those racks

    Returns:
        integer with return code
        dictionary with results based on parameters
            Dictionary entries:
                message:  any message returned for the processing of this method
                column_tags: array of column tags
                column_titles: array of column titles
                racks: list of rack information packed in a dictionary structure
    """
    all_tags = ['label', 'rackid', 'data-center', 'location', 'notes']
    brief_tags = ['label']
    result = {}

    # decide the set of data to return
    if isbriefly:
        tags = brief_tags
    else:
        tags = all_tags

    # get rack based on labels and device ids
    if labels:
        racks, dummy_not_found_racks = persistent_mgr.get_racks_by_labels(labels)
    elif rackids:
        racks, dummy_not_found_racks = persistent_mgr.get_racks_by_ids(rackids)
    else:
        racks = persistent_mgr.get_all_racks()

    # check if labels returned anything if specified
    if len(racks) == 0 and labels:
        message = _("No racks labeled as \'%s\'") % labels
        result['message'] = message
        return 101, result

    # already filtered by get_racks_info call
    filtered_racks = racks

    # add table column info
    table_columns_titles = []
    result['column_tags'] = tags
    for tag in tags:
        table_columns_titles.append(get_racktag_text_id(tag))
    result['column_titles'] = table_columns_titles

    result_racks = []
    for rack in filtered_racks:
        rack_dict = rack.to_dict_obj()
        rack_output = {}
        for tag in tags:
            tag_value = rack_dict.get(tag)
            if tag_value is None:
                tag_value = ''
            rack_output[tag] = tag_value
        # add final form of device info to result
        result_racks.append(rack_output)

    result['racks'] = result_racks

    message = ""
    result['message'] = message
    return 0, result


def remove_rack(labels=None, all_racks=False, rackids=None):
    '''Remove racks based on information present in the arguments

    If the option rackids is specified, then the option labels will be ignored

    Args:
        labels        List of labels of racks to remove
        all_racks     indicate all racks (except the manager rack (1)) to be removed.
        rackids       list of rack ids to remove
    Returns:
        ret    return code
        message message if provided with return code
    '''
    _method_ = 'device_mgr.remove_rack'
    if labels or rackids:
        all_racks = False

    # get the right set of racks based on input
    if rackids is not None:
        racks, not_found_rack_values = persistent_mgr.get_racks_by_ids(rackids)
    elif labels is not None:
        racks, not_found_rack_values = persistent_mgr.get_racks_by_labels(labels)
    elif all_racks:
        racks = persistent_mgr.get_all_racks()
    else:
        message = \
            "Error: remove_rack called without specifying to remove either a label, id or all"
        return -1, message



    devices = persistent_mgr.get_all_devices()

    hooks = load_inventory_rack_plugins()
    hook_name = 'unknown' #keeps pylint happy

    message = None
    remove_racks = []
    not_remove_racks = []
    not_remove_racks_msgs = []

    for rack in racks:
        label = rack.label
        rack_id = rack.rack_id

        devices_in_rack = []
        for device in devices:
            if device.rack_id == rack_id:
                devices_in_rack.append(device)
                logging.warning("%s::found device (%s) still in  rack.", _method_, device.label)

        if len(devices_in_rack) > 0:
            # don't allow removing if rack in use
            not_remove_racks.append(rack)
            not_remove_racks_msgs.append(
                _("Rack (%s) has devices. Only racks without devices can be removed.") % label)
            logging.warning(
                "%s::rack (%s) has devices. only empty racks can be removed.", _method_, label)
            continue

        try:
            for hook_name, hook_plugin in hooks.items():
                hook_plugin.remove_rack_pre_save(rack)
        except Exception as e:
            logging.exception(e)
            not_remove_racks.append(rack)
            not_remove_racks_msgs.append(
                _("Error in plugin (%s). Unable to remove resource: Reason: %s") % (hook_name, e))
            continue

        # ok to remove rack.
        remove_racks.append(rack)

    result_message = ""
    ret = 0
    is_return_rackid = False
    if len(remove_racks) > 0:
        persistent_mgr.delete_racks(remove_racks)
        labels_message = get_labels_message(
            remove_racks, is_return_rackid, 'rack_id')
        message = push_message(message, _("racks removed: %s") % labels_message)

        #Call hook for remove_rack_post_save
        for rack in remove_racks:
            try:
                for hook_name, hook_plugin in hooks.items():
                    hook_plugin.remove_rack_post_save(rack)
            except Exception as e:
                logging.exception(e)
                message = push_message(message, _("After rack (%s) was removed. "
                                                  "Error in plugin (%s): %s") % \
                       (rack.label, hook_name, e))

    if len(not_remove_racks) > 0:
        labels_message = get_labels_message(
            not_remove_racks, is_return_rackid, 'rack_id')
        message = push_message(message, _("racks not removed: %s") % labels_message)
        for rack_msg in not_remove_racks_msgs:
            message = push_message(message, rack_msg)
        ret = 102
    if len(not_found_rack_values) > 0:
        labels_message = get_labels_message(
            not_found_rack_values, is_return_rackid, 'rack_id')
        message = push_message(message, _("racks not found: %s") % labels_message)
        ret = 101
    message = push_message(message, result_message)
    return ret, message


def remove_device(labels=None, all_devices=False, deviceids=None):
    '''Remove devices based on information present in the arguments

    If the option deviceIDs is specified, then the options labels and all_devices
    will be ignored. If the option labels is specified then the all_devices
    option will be ignored.


    Args:
        labels        List of labels of devices to remove
        all_devices   indicate all devices to be removed.
        deviceids     list of device ids to remove
    Returns:
        ret    return code
        message message if provided with return code
    '''
    #_method_ = 'device_mgr.remove_device'
    not_found_values = []
    if labels or deviceids:
        all_devices = False
    # get devices based on labels and device ids
    if deviceids is not None:
        devices, not_found_values = persistent_mgr.get_devices_by_ids(deviceids)
    elif labels is not None:
        devices, not_found_values = persistent_mgr.get_devices_by_labels(labels)
    elif all_devices:
        devices = persistent_mgr.get_all_devices()
    else:
        message = \
            ("Error: remove_device called without specifying to remove either a label, id or all")
        return -1, message

    hooks = load_inventory_device_plugins()
    hook_name = 'unknown' #keeps pylint happy

    message = None
    remove_devices = []
    not_remove_devices = []

    for device in devices:
        try:
            for hook_name, hook_plugin in hooks.items():
                hook_plugin.remove_device_pre_save(device)
        except Exception as e:
            logging.exception(e)
            message += _("Error in plugin (%s). Unable to remove resource: Reason: %s") % \
                       (hook_name, e)
            not_remove_devices.append(device)
            continue
        remove_devices.append(device)

    ret = 0
    is_return_deviceid = False
    if len(remove_devices) > 0:
        persistent_mgr.delete_devices(remove_devices)
        labels_message = get_labels_message(remove_devices, is_return_deviceid)
        message = push_message(message, _("devices removed: %s.") % labels_message)

        #Call hook for remove_device_post_save
        for device in remove_devices:
            try:
                for hook_name, hook_plugin in hooks.items():
                    hook_plugin.remove_device_post_save(device)
            except Exception as e:
                logging.exception(e)
                message = push_message(message, _("After device was removed. Error in plugin " \
                                       "(%s): %s") % (hook_name, e))

    if len(not_remove_devices) > 0:
        labels_message = get_labels_message(not_remove_devices, is_return_deviceid)
        message = push_message(message, _("devices not removed: %s.") % labels_message)
        ret = 102
    if len(not_found_values) > 0:
        labels_message = get_labels_message(not_found_values, is_return_deviceid)
        message = push_message(message, _("devices not found: %s") % labels_message)
        ret = 101

    return ret, message


def _validate(address, userid, password, device_type, ssh_key=None):
    """ Validate the password, address and userid information

    Args:
        address:  ip v4 address for the device to validate
        userid:  userid of the device to validate
        password:  password for the device
        device_type: device type of device to validate the info for
        ssh_key:   io.StringIO stream of the ssh key
    Returns:
        rc:  return code for the operation
        message:  message to return to user in case of non 0 return code
    """
    _method_ = 'device_mgr._validate'
    # have a userid and pw to try at this point with only new pw,
    # verify the new password as valid to set as the persisted pw
    message = ""
    validate_result = validate(address, userid, password, device_type, ssh_key)
    rc = validate_result[0]
    if rc == 0:
        logging.info("%s::validate device data successfully.", _method_)
        message = _("Validated device data successfully.")
    elif rc == 10:
        # validate does not work on device type  so can't tell if change pw
        # will work.
        logging.info(
            "%s::unable to validate device data with device.", _method_)
    else:
        # rc we go indicates no attempt to change password should be tried get
        # response message and return
        logging.error(
            "%s::failed to validate device info for (%s) return value(%d).", _method_, address, rc)

        if rc == 1:
            message = _("Failed to connect the device.")
        elif rc == 2:
            message = _("Authentication error connecting to device.")
        elif rc == 3:
            message = _("Device unknown.")
        elif rc == 9:
            message = _("Root access is required to manage this device.")
    return rc, message


def validate(address, userid, password, device_type, ssh_key=None):
    '''
    validate that the device is reachable with the credentials provided.

    Args:
        address    IPv4 address to the device.
        userid     Userid to access the device with
        password   Password to access the device with (or ssh_key password)
        device_type string identifying device type to validate as.
        ssh_key:   io.StringIO stream of the ssh key
    Returns:
        rc, device_type, mtm, serialnum, version_details, Interfaces

        where rc defined to be one of:
            0 - Success
            1 - failed to connect
            2 - userid/password invalid
            3 - device type error
            4 - SVC not using superuser
            9 - root is required
            10  device type does not support function
    '''
    _method_ = 'device_mgr.validate'
    logging.info("ENTER %s::address=%s userid=%s device_type=%s",
                 _method_, address, userid, device_type)
    plugins = load_device_plugins()

    if device_type:
        plugin = plugins[device_type]
        try:
            plugin = plugins[device_type]
            plugin.connect(address, userid, password, ssh_key)
            mtm = plugin.get_machine_type_model()
            serialnum = plugin.get_serial_number()
            version = plugin.get_version()
            plugin.disconnect()
            return (constants.validation_codes.SUCCESS.value, device_type, mtm, serialnum, version)
        except KeyError:
            logging.error("%s::plugin(%s) not found", _method_, device_type)
            return (constants.validation_codes.DEVICE_TYPE_ERROR.value,
                    None, None, None, None)
        except IntegratedManagerException.ConnectionException:
            return (constants.validation_codes.FAILED_TO_CONNECT.value,
                    None, None, None, None)
        except IntegratedManagerException.AuthenticationException:
            return (constants.validation_codes.CREDENTIALS_INVALID.value,
                    None, None, None, None)
        except Exception as e:
            logging.exception(e)
            logging.warning("%s:plugin(%s). Exception running validate: %s",
                            _method_, plugin.__class__.__name__, e)
    else: #Try all plugins
        for plugin_device_type, plugin in plugins.items():
            try:
                plugin.connect(address, userid, password, ssh_key)
                mtm = plugin.get_machine_type_model()
                serialnum = plugin.get_serial_number()
                version = plugin.get_version()
                plugin.disconnect()
                device_type = plugin_device_type
                break
            except Exception as e:
                logging.exception(e)
                logging.warning("%s:plugin(%s). Exception running validate: %s",
                                _method_, plugin.__class__.__name__, e)
                continue
        if device_type:
            return (constants.validation_codes.SUCCESS.value, device_type, mtm, serialnum, version)

    return (constants.validation_codes.DEVICE_TYPE_ERROR.value, None, None, None, None)

def change_rack_properties(label=None, rackid=None, new_label=None, data_center=None,
                           location=None, notes=None):
    ''' Change the rack properties in the data store

    Arguments:
        label: label for the rack
        rackid: rackid for the rack
        new_label: new label to set for the rack
        data_center: free form field to describe the data center
        location: free form location to describe the location of data center in the rack
        notes: free form set of notes about the rack

    Returns:
        rc: int indicating the success (0) or failure of the method
        message: nls enabled message to  respond with on failure

    '''
    _method_ = 'device_mgr.change_rack_properties'
    logging.info("ENTRY %s", _method_)

    message = None
    # check if no properties changed
    if new_label is None and data_center is None and \
            location is None and notes is None:
        logging.info("EXIT %s Nothing to change", _method_)
        return 0, ""

    if rackid:
        rack = persistent_mgr.get_rack_by_id(rackid)
    else:
        rack = persistent_mgr.get_rack_by_label(label)

    device_des = label if rackid is None else rackid
    if not rack:
        logging.error(
            "%s::Failed to change rack properties, rack (%s) is not found.", _method_, device_des)
        message = _(
            "Failed to change rack properties, rack (%s) is not found.") % (device_des)
        logging.info("EXIT %s rack not found", _method_)
        return 101, message

    if new_label is not None:
        # trying to change rack label
        if new_label != rack.label:
            # have a different label need to check if already exists....
            rack_new_label = persistent_mgr.get_rack_by_label(new_label)
            if rack_new_label is not None:
                # found the new label exists
                error_message = _("Failed to change rack properties. The new rack label "
                                  "%(new_label)s already exists.") % {"new_label": new_label}
                return 102, error_message
            # ok now to set the new label
            rack.label = new_label

    if data_center is not None:
        rack.data_center = data_center
    if location is not None:
        rack.location = location
    if notes is not None:
        rack.notes = notes

    hooks = load_inventory_rack_plugins()
    hook_name = 'unknown' #keeps pylint happy
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.change_rack_pre_save(rack)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s). Unable to change rack: Reason: %s") % (hook_name, e)
        return 102, message

    persistent_mgr.update_rack([rack])

    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_rack_post_save(rack_info)
    except Exception as e:
        logging.exception(e)
        message = _("After rack properties were changed, Error in plugin (%s): %s") % (hook_name, e)

    logging.info("EXIT %s rack properties changed", _method_)
    if not message:
        message = _("Changed rack property successfully.")
    return 0, message

def _change_device_key(device, address, userid, ssh_key_string, password):
    """ Validate the new ssh key works, and change the device properties
        prior to saving the device.

    Args:
        device - original device properties
        address - new address if changed, else old address
        userid - new userid if changed, else old userid
        ssh_key_string: io.StringIO stream of the ssh key - new
        password - password for the ssh key if any
    Returns:
        rc, message - if rc 0, updated device object
        if rc non 0, message with failure
    """
    rc, message = _validate(address, userid, password, device.device_type, ssh_key_string)
    if rc == 0:
        # Update the device and key object for the new ssh_key
        if device.key: #existing key to update
            key_info = device.key
        else: #new key needs created
            key_info = Key()
            key_info.device = device
            key_info.type = "RSA"
        key_info.value = ssh_key_string.getvalue()
        if password:
            key_info.password = persistent_mgr.encrypt_data(password)
        else:
            key_info.password = None

        device.password = None # using ssh_key authentication
    return (rc, message)

def _change_device_userpass(device, address, userid, password):
    """ Validate the userid password works and change the device_propeties
        prior to the saving the device.
        Doesn't update any password on the device itself
    Args:
        device - original device properties
        address - new address if changed, else old address
        userid - new userid if changed, else old userid
        password - password of the userid
    Returns:
        rc, message - if rc 0, updated device object
        if rc non 0, message with failure
    """
    rc, message = _validate(address, userid, password, device.device_type, None)
    if rc == 0:
        #Update the device object for the new userid/password
        device.userid = userid
        device.password = persistent_mgr.encrypt_data(password)
    return (rc, message)



@entry_exit(exclude_index=[], exclude_name=["password"])
def change_device_properties(label=None, deviceid=None, new_label=None,
                             userid=None, password=None, address=None,
                             rackid=None, rack_location=None, ssh_key=None):
    """ Change the device properties in the data store

    Args:
        label: the existing label of the device (this or device id should be provided)
        deviceid: the device id of the device to change
        new_label:  new label to set for the device
        userid: the userid to set as userid managing the device.
        password: password of the userid or the ssh key
        address: the ip address or the hostname to set for the device
        rackid:  rack id to set for the device
        rack_location: location in the rack of the element
        ssh_key: io.StringIO stream of the ssh key

    Returns:
        rc:  return code
        message: completion message indicating reason for non zero rc (translated)
    """
    _method_ = 'device_mgr.change_device_properties'
    message = None

    # no properties changed
    properties = [new_label, userid, password, address, rackid, rack_location, ssh_key]
    if all(prop is None for prop in properties):
        return 0, ""

    # gain access to the device object for the targeted item.
    if deviceid is not None:
        device = persistent_mgr.get_device_by_id(deviceid)
        device_des = deviceid
    else:
        device = persistent_mgr.get_device_by_label(label)
        device_des = label
    if not device:
        logging.error("%s::Failed to change device properties device (%s) is not found.",
                      _method_, device_des)
        message = _(
            "Failed to change device properties, device (%s) is not found.") % (device_des)
        return 101, message

    address_changed = False
    # check if we now need to handle an IP address change in the change properties
    ip_address = ""
    hostname = ""

    if address is not None:
        if is_valid_address(address):
            ip_address = address
            hostname = socket.gethostbyaddr(address)[0]
        else:
            hostname = socket.getfqdn(address)
            ip_address = socket.gethostbyname(hostname)

        if ip_address != device.address:
            # check if id is of good form and not already in use as long as its
            # different from the one we have
            rc, message = validate_address(ip_address)
            if rc != 0:
                logging.error(
                    "%s::Failed to validate supplied address: %s", _method_, ip_address)
                return rc, message
            else:
                # now handle the IP address change
                address_changed = True
                logging.info("%s: IP address changed.", _method_)
                device.address = ip_address
                device.hostname = hostname
    else:
        # we may need the address for authorization changes, make sure its set
        ip_address = device.address

    # if we made it here we, have an ip address to use and maybe using a
    # changed address.
    if address_changed or userid is not None or password is not None or ssh_key is not None:
        # validate that the existing credentials work with the new IP
        # address or the new credentials are valid

        # Figure out if we are:
        # 1. Replacing the userid and password with another userid and pasword
        # 2. Replacing the ssh_key with another ssh_key (may or may not have a password)
        # 3. Replacing the userid and password with an ssh_key
        # 4. Replacing the ssh_key with a userid nad password
        # 5. Not changing anything just the ip address
        # Figure out and set old_auth and new_auth to either userpass or key

        if device.key is not None:
            old_auth = "key"
        else:
            old_auth = "userpass"
        
        if ssh_key is not None:
            new_auth = "key"
        elif userid is not None or password is not None:
            new_auth = "userpass"
        else:
            new_auth = None

        device_type = device.device_type
        if userid:
            temp_userid = userid
        else:
            temp_userid = device.userid

        temp_password = None
        if password:
            temp_password = password
        else:
            if device.password is not None:
                temp_password = persistent_mgr.decrypt_data(device.password)
        if ssh_key:
            temp_ssh_key = ssh_key
        else:
            if device.key:
                key = device.key
                temp_ssh_key = StringIO(key.value)
                if key.password:
                    password = persistent_mgr.decrypt_data(key.password)

        if new_auth == "key":
            rc, message = _change_device_key(device, ip_address, temp_userid,
                                             temp_ssh_key, temp_password)
        elif new_auth == "userpass":
            rc, message = _change_device_userpass(device, ip_address, temp_userid, temp_password)
        else:
            rc, message = _validate(ip_address, temp_userid, temp_password,
                                    device_type, temp_ssh_key)
        if rc != 0:
            # return error if unable to validate with currently set info
            return rc, message
        else:
            device.status = constants.access_status.SUCCESS.value
            device.statusTime = datetime.utcnow()

    if new_label is not None and new_label != device.label:
        # have new label and the new label differs from the existing label for
        # the target device
        rc, message = validate_label(new_label)
        if rc != 0:
            # another device already exists with the label
            logging.error("%s::failed to change device properties, a device with the new label (%s)"
                          " already exists.", _method_, new_label)
            message = _("Failed to change device properties, a device with the new label"
                        " (%(label)s) already exists.") % {'label': new_label}
            return 104, message

        device.label = new_label
    if rackid is not None:
        device.rack_id = rackid
    if rack_location is not None:
        device.eia_location = rack_location

    #pre_save hooks
    hooks = load_inventory_device_plugins()
    hook_name = 'unknown' #keeps pylint happy
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.change_device_pre_save(device)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s). Unable to change device: Reason: %s") % (hook_name, e)
        return 102, message

    # commit the change.
    logging.info(
        "%s: commit device changes now. device info: %s", _method_, device)
    persistent_mgr.update_device([device])

    if old_auth == "key" and new_auth == "userpass":
        # Need to delete ssh key from database
        key_info = device.key
        persistent_mgr.delete_keys([key_info])

    #post_save hooks
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.change_device_post_save(device)
    except Exception as e:
        logging.exception(e)
        message = push_message(message, _("After device properties were changed, " \
                               "Error in plugin (%): %s") % (hook_name, e))

    # return success
    logging.info("EXIT %s device properties changed", _method_)
    message = push_message(message, _("Changed device successfully."))
    return 0, message

def get_rackid(rack_label):
    ''' Return rackid for a given rack label

    Args:
        rack_label: label for the rack to get the id for
    Returns:
        rack id
    '''
    rackid = None
    rc, rack_dict = list_racks()
    if rc == 0:
        racks = rack_dict['racks']
        for rack in racks:
            if rack['label'] == rack_label:
                rackid = rack['rackid']
                break
    return rackid

def list_supported_device_types():
    return sorted(load_device_plugins().keys())
