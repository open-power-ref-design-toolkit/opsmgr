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

import gettext
# establish _ in global namespace
gettext.install('opsmgr', '/usr/share/locale')
import logging

from opsmgr.inventory import persistent_mgr, resource_mgr
from opsmgr.common.utils import entry_exit, push_message, load_plugin_by_namespace
from opsmgr.inventory.data_model import Rack

I_MANAGER_RACK_HOOK = "opsmgr.inventory.interfaces.IManagerRackHook"

@entry_exit(exclude_index=[], exclude_name=[])
def add_rack(label, data_center='', room='', row='', notes=''):
    """add rack to the list of racks in the configuration managed

    Args:
        label: label for rack
        data_center: data center location (free form)
        room: Room in the data center of the rack (free form)
        row: Row in the room of the rack (free form)
        notes: freeform notes associated with this rack to describe its use, mgmt, etc.
    Returns:
        RC: integer return code
        Message: string with message associated with return code
    """
    _method_ = 'rack_mgr.add_rack'
    label = label.strip()
    message = None

    session = persistent_mgr.create_database_session()

    # get existing rack info for next set of checks
    racks_info = persistent_mgr.get_all_racks(session)

    for rack in racks_info:
        if rack.label == label:
            message = _(
                "The rack label (%s) conflicts with a rack label in the configuration file.") \
                % label
            return 101, message

    rack_info = Rack()
    rack_info.label = label
    rack_info.room = room
    rack_info.row = row
    rack_info.data_center = data_center
    rack_info.notes = notes

    hooks = _load_inventory_rack_plugins()
    hook_name = 'unknown' #keeps pylint happy
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_rack_pre_save(rack_info)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s). Unable to add rack: Reason: %s") % (hook_name, e)
        return 102, message

    persistent_mgr.add_racks(session, [rack_info])

    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.add_rack_post_save(rack_info)
    except Exception as e:
        logging.exception(e)
        message = _("After rack was added. Error in plugin (%s): %s") % (hook_name, e)

    logging.info("%s::add rack(%s) success", _method_, label)
    if not message:
        message = _("Added rack successfully.")

    session.close()
    return 0, message

@entry_exit(exclude_index=[], exclude_name=[])
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
    all_tags = ['label', 'rackid', 'data-center', 'room', 'row', 'notes']
    brief_tags = ['label']
    result = {}

    session = persistent_mgr.create_database_session()
    # decide the set of data to return
    if isbriefly:
        tags = brief_tags
    else:
        tags = all_tags

    # get rack based on labels and rack ids
    if labels:
        racks, _not_found_racks = persistent_mgr.get_racks_by_labels(session, labels)
    elif rackids:
        racks, _not_found_racks = persistent_mgr.get_racks_by_ids(session, rackids)
    else:
        racks = persistent_mgr.get_all_racks(session)

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
        table_columns_titles.append(_get_racktag_text_id(tag))
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
        # add final form of rack info to result
        result_racks.append(rack_output)

    result['racks'] = result_racks

    message = ""
    result['message'] = message
    session.close()
    return 0, result

@entry_exit(exclude_index=[], exclude_name=[])
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
    _method_ = 'rack_mgr.remove_rack'

    session = persistent_mgr.create_database_session()

    if labels or rackids:
        all_racks = False

    # get the right set of racks based on input
    if rackids is not None:
        racks, not_found_rack_values = persistent_mgr.get_racks_by_ids(session, rackids)
    elif labels is not None:
        racks, not_found_rack_values = persistent_mgr.get_racks_by_labels(session, labels)
    elif all_racks:
        racks = persistent_mgr.get_all_racks(session)
    else:
        message = \
            "Error: remove_rack called without specifying to remove either a label, id or all"
        return -1, message

    devices = persistent_mgr.get_all_devices(session)

    hooks = _load_inventory_rack_plugins()
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
        persistent_mgr.delete_racks(session, remove_racks)
        labels_message = resource_mgr.get_labels_message(
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
        labels_message = resource_mgr.get_labels_message(
            not_remove_racks, is_return_rackid, 'rack_id')
        message = push_message(message, _("racks not removed: %s") % labels_message)
        for rack_msg in not_remove_racks_msgs:
            message = push_message(message, rack_msg)
        ret = 102
    if len(not_found_rack_values) > 0:
        labels_message = resource_mgr.get_labels_message(
            not_found_rack_values, is_return_rackid, 'rack_id')
        message = push_message(message, _("racks not found: %s") % labels_message)
        ret = 101
    message = push_message(message, result_message)
    session.close()
    return ret, message

@entry_exit(exclude_index=[], exclude_name=[])
def change_rack_properties(label=None, rackid=None, new_label=None, data_center=None,
                           room=None, row=None, notes=None):
    ''' Change the rack properties in the data store

    Arguments:
        label: label for the rack
        rackid: rackid for the rack
        new_label: new label to set for the rack
        data_center: free form field to describe the data center
        room: free form field for the room in the data center
        row: free form field for the row in the room
        notes: free form set of notes about the rack

    Returns:
        rc: int indicating the success (0) or failure of the method
        message: nls enabled message to  respond with on failure

    '''
    _method_ = 'rack_mgr.change_rack_properties'
    logging.info("ENTRY %s", _method_)

    message = None
    session = persistent_mgr.create_database_session()

    # check if no properties changed
    properties = [new_label, data_center, room, row, notes]
    if all(prop is None for prop in properties):
        logging.info("EXIT %s Nothing to change", _method_)
        return 0, ""

    if rackid:
        rack = persistent_mgr.get_rack_by_id(session, rackid)
    else:
        rack = persistent_mgr.get_rack_by_label(session, label)

    rack_des = label if rackid is None else rackid
    if not rack:
        logging.error(
            "%s::Failed to change rack properties, rack (%s) is not found.", _method_, rack_des)
        message = _(
            "Failed to change rack properties, rack (%s) is not found.") % (rack_des)
        logging.info("EXIT %s rack not found", _method_)
        return 101, message

    if new_label is not None:
        # trying to change rack label
        if new_label != rack.label:
            # have a different label need to check if already exists....
            rack_new_label = persistent_mgr.get_rack_by_label(session, new_label)
            if rack_new_label is not None:
                # found the new label exists
                error_message = _("Failed to change rack properties. The new rack label "
                                  "%(new_label)s already exists.") % {"new_label": new_label}
                return 102, error_message
            # ok now to set the new label
            rack.label = new_label

    if data_center is not None:
        rack.data_center = data_center
    if room is not None:
        rack.room = room
    if row is not None:
        rack.row = row
    if notes is not None:
        rack.notes = notes

    hooks = _load_inventory_rack_plugins()
    hook_name = 'unknown' #keeps pylint happy
    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.change_rack_pre_save(rack)
    except Exception as e:
        logging.exception(e)
        message = _("Error in plugin (%s). Unable to change rack: Reason: %s") % (hook_name, e)
        return 102, message

    persistent_mgr.update_rack(session)

    try:
        for hook_name, hook_plugin in hooks.items():
            hook_plugin.change_rack_post_save(rack)
    except Exception as e:
        logging.exception(e)
        message = _("After rack properties were changed, Error in plugin (%s): %s") % (hook_name, e)

    logging.info("EXIT %s rack properties changed", _method_)
    if not message:
        message = _("Changed rack property successfully.")
    session.close()
    return 0, message

@entry_exit(exclude_index=[], exclude_name=[])
def get_rack_id_by_label(rack_label):
    """
    Find the rack id for the rack label
    Returns:
        rack_id or None
    """
    rack_id = None
    session = persistent_mgr.create_database_session()
    rack = persistent_mgr.get_rack_by_label(session, rack_label)
    if rack:
        rack_id = rack.rack_id
    session.close()
    return rack_id

def _get_racktag_text_id(tag_name):
    racktag_id = {
        'rackid': _('id'),
        'label': _('label'),
        'mgrRackId': _('manager rack'),
        'role': _('role'),
        'data-center': _('data center'),
        'room': _('room'),
        'row': _('row'),
        'notes': _('notes'),
    }
    if tag_name in racktag_id:
        return racktag_id[tag_name]
    return tag_name

def _load_inventory_rack_plugins():
    """
    Find the inventory rack plugins and return them as
    dictonary[name]=plugin class
    """
    return load_plugin_by_namespace(I_MANAGER_RACK_HOOK)
