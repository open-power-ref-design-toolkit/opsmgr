from opsmgr.inventory import rack_mgr, resource_mgr

def add_rack(label, data_center='', room='', row='', notes=''):
    return rack_mgr.add_rack(label, data_center, room, row, notes)

def add_device(label, device_type, address, userid, password, rackid='', rack_location='',
               ssh_key=None):
    return resource_mgr.add_resource(label, device_type, address, userid, password,
                                     rackid, rack_location, ssh_key, offline=False)

def change_device_password(label=None, deviceid=None, old_password=None, new_password=None):
    return resource_mgr.change_resource_password(label, deviceid, old_password, new_password)

def change_device_properties(label=None, deviceid=None, new_label=None,
                             userid=None, password=None, address=None,
                             rackid=None, rack_location=None, ssh_key=None):
    return resource_mgr.change_resource_properties(label, deviceid, new_label, userid, password,
                                                   address, rackid, rack_location, ssh_key)

def list_devices(labels=None, isbriefly=False, device_types=None, deviceids=None,
                 list_device_id=False, is_detail=False, racks=None):
    return resource_mgr.list_resources(labels, isbriefly, device_types, deviceids, list_device_id,
                                       is_detail, racks)

def remove_device(labels=None, all_devices=False, deviceids=None):
    return resource_mgr.remove_resource(labels, all_devices, deviceids)


def list_racks(labels=None, isbriefly=False, rackids=None):
    return rack_mgr.list_racks(labels, isbriefly, rackids)

def remove_rack(labels=None, all_racks=False, rackids=None):
    return rack_mgr.remove_rack(labels, all_racks, rackids)

def change_rack_properties(label=None, rackid=None, new_label=None, data_center=None,
                           room=None, row=None, notes=None):
    return rack_mgr.change_rack_properties(label, rackid, new_label, data_center,
                                           room, row, notes)

def list_supported_device_types():
    return resource_mgr.list_resource_types()
