#Known issues
#https://bugs.python.org/issue9694 argparse required arguments displayed under "optional arguments"

import argparse
import getpass
import gettext
# establish _ in global namespace
gettext.install('opsmgr', '/usr/share/locale')
import sys

import paramiko

import opsmgr.discovery.discovery_mgr as discovery_mgr
import opsmgr.inventory.device_mgr as device_mgr
import opsmgr.inventory.persistent_mgr as persistent_mgr
import opsmgr.inventory.remote_access as remote_access
from opsmgr.common.utils import get_strip_strings_array
from opsmgr.common.utils import LoggingService

def _prompt_for_key_password(key_file, password=None):
    """ Given a key_file will attempt read it, if password is None
        and a password is required, will prompt for the password
    """
    try:
        paramiko.RSAKey.from_private_key_file(key_file, password)
    except paramiko.PasswordRequiredException:
        password = getpass.getpass(_("SSH Key password:"))
        paramiko.RSAKey.from_private_key_file(key_file, password)

    return password


def _read_key_file(key_file, password=None):
    """ Given a key_file will return the string contents
        of the key and it's password.
    """
    ssh_key_string = None
    if key_file:
        password = _prompt_for_key_password(key_file, password)
        file = open(key_file)
        ssh_key_string = file.read()
        file.close()
    return (ssh_key_string, password)

def add_device(args):
    ssh_key_string = None
    if args.key:
        try:
            (ssh_key_string, password) = _read_key_file(args.key, args.password)
        except (IOError, paramiko.SSHException) as e:
            message = _("Error reading key file: %s") % e
            return -1, message
    elif args.password:
        password = args.password
    else:
        new_password = getpass.getpass(_("Device password:"))
        if not new_password:
            message = _("Please input a valid password and retry the command.")
            return -1, message
        password = new_password

    rack_id = None
    if args.rack:
        rack = persistent_mgr.get_rack_by_label(args.rack)
        if rack:
            rack_id = rack.rack_id
        else:
            error_message = _("Rack label (%s) was not found.") % args.rack
            return -1, error_message

    return device_mgr.add_device(args.label, args.type, args.address, args.user,
                                 password, rack_id, args.rack_location, ssh_key_string)

def add_rack(args):
    return device_mgr.add_rack(args.label, args.data_center, args.location, args.notes)

def change_device(args):
    ssh_key_string = None
    if args.key:
        try:
            (ssh_key_string, password) = _read_key_file(args.key, args.password)
        except (IOError, paramiko.SSHException) as e:
            message = _("Error reading key file: %s") % e
            return -1, message
    elif args.prompt_password:
        new_password = getpass.getpass(_("Device password:"))
        if not new_password:
            message = _("Please input a valid password and retry the command.")
            return -1, message
        password = new_password
    else:
        password = args.password

    rackid = None
    if args.rack:
        rack = persistent_mgr.get_rack_by_label(args.rack)
        if rack:
            # found the matching rack.
            rackid = rack.rack_id
        else:
            message = _("Input label for rack option (%s) not found.") % (args.rack)
            return -1, message

    if (not password and not args.address and not args.new_label and not rackid
            and not args.rack_location and not ssh_key_string):
        message = _("You must specify at least one property to be modified.")
        return -1, message

    return device_mgr.change_device_properties(label=args.label, userid=args.user,
                                               password=password, address=args.address,
                                               new_label=args.new_label, rackid=rackid,
                                               rack_location=args.rack_location,
                                               ssh_key=ssh_key_string)

def change_device_password(args):
    if not args.oldpassword:
        old_password = getpass.getpass(prompt='Enter the current Password:')
    else:
        old_password = args.oldpassword

    if not args.newpassword:
        new_password1 = getpass.getpass(prompt='Enter new Password:')
        new_password2 = getpass.getpass(prompt='Re-enter new Password:')
        if new_password1 == new_password2:
            new_password = new_password1
        else:
            message = _("The new passwords are not same.")
            return -1, message
    else:
        new_password = args.newpassword

    if not args.label and not args.oldpassword and not args.newpassword:
        message = _("You must specify at least label in the command.")
        return -1, message

    return device_mgr.change_device_password(label=args.label, old_password=old_password,
                                             new_password=new_password)

def change_rack(args):
    if not args.new_label and not args.data_center and not args.location and not args.notes:
        message = _("You must specify at least one property to be modified.")
        return -1, message
    return device_mgr.change_rack_properties(label=args.label, new_label=args.new_label,
                                             data_center=args.data_center,
                                             location=args.location, notes=args.notes)

def list_devices(args):
    labels = None
    types = None
    rack_ids = None
    if args.label:
        labels = get_strip_strings_array(str(args.label))
    if args.type:
        types = get_strip_strings_array(str(args.type))
    if args.rack:
        rack_ids = []
        racks = get_strip_strings_array(str(args.rack))
        racks, dummy_not_found_racks = persistent_mgr.get_racks_by_labels(racks)
        for rack in racks:
            rack_ids.append(rack.rack_id)

    (rc, result_dict) = device_mgr.list_devices(labels, args.briefly, types, racks=rack_ids)

    result = ""
    try:
        SEPARATOR = ","
        labels_array = result_dict['column_titles']
        tags_array = result_dict['column_tags']

        if not args.briefly:
            # find the device id and remove from both arrays to generate list
            # result without the device id info.
            deviceid_index = tags_array.index('deviceid')
            del tags_array[deviceid_index]
            del labels_array[deviceid_index]

        # create the CSV header line
        header = ""
        for label in labels_array:
            if header:
                header += SEPARATOR
            header += label
        header += "\n"
        result += header

        rack_id_to_label_map = {}
        rc, rack_dict = device_mgr.list_racks()
        racks = rack_dict['racks']
        for rack in racks:
            racklabel = rack['label']
            rackid = rack['rackid']
            rack_id_to_label_map[rackid] = racklabel

        devices = result_dict['devices']
        for device in devices:
            # per device create the CSV line for the device
            line = ""
            for tag in tags_array:
                if line:
                    line += SEPARATOR
                if tag == 'rackid':
                    # resolve the rackid to a label
                    rackid = device['rackid']
                    output_rack_label = rack_id_to_label_map[rackid]
                    line += output_rack_label
                elif tag == 'status':
                    line += str(device[tag])
                elif tag == 'statusTime':
                    line += str(device[tag])
                elif tag == 'auth_method':
                    line += str(device[tag])
                else:
                    # normal handling
                    line += device[tag] if device[tag] else ''
            line += "\n"
            result += line
    except KeyError:
        #if a key is missing the error will be in the message
        pass

    # if a message, now output it
    if result_dict['message']:
        result += "\n"
        result += result_dict['message']
    return (rc, result)

def list_racks(args):
    labels = None
    if args.label:
        labels = get_strip_strings_array(str(args.label))

    (rc, result_dict) = device_mgr.list_racks(labels, args.briefly)

    result = ""
    try:
        SEPARATOR = ","
        labels_array = result_dict['column_titles']
        tags_array = result_dict['column_tags']

        if not args.briefly:
            # find the rack id and remove from both arrays to generate list
            # result without the rack id info.
            rackid_index = tags_array.index('rackid')
            del tags_array[rackid_index]
            del labels_array[rackid_index]

        # create the CSV header line
        header = ""
        for label in labels_array:
            if header:
                header += SEPARATOR
            header += label
        header += "\n"
        result += header

        racks = result_dict['racks']
        for rack in racks:
            # per rack create the CSV line for the rack
            line = ""
            for tag in tags_array:
                if line:
                    line += SEPARATOR
                line += rack[tag] if rack[tag] else ''
            line += "\n"
            result += line
    except KeyError:
        #if a key is missing the error will be in the message
        pass

    # if a message, now output it
    if result_dict['message']:
        result += "\n"
        result += result_dict['message']
    return (rc, result)

def list_supported_device_types():
    device_types = device_mgr.list_supported_device_types()
    result = ",".join(device_types)
    return 0, result

def remote_access_cmd(args):
    return remote_access.remote_access(args.label)

def remove_device(args):
    labels = None
    if args.label:
        labels = get_strip_strings_array(str(args.label))
    return device_mgr.remove_device(labels, args.all)

def remove_rack(args):
    labels = get_strip_strings_array(str(args.label))
    return device_mgr.remove_rack(labels)

def list_discovery_plugins():
    discovery_plugins = discovery_mgr.list_plugins()
    result = ",".join(discovery_plugins)
    return 0, result

def find_resources():
    return discovery_mgr.find_resources()

def import_resources(args):
    if args.label:
        resource = args.label.strip()
    else:
        resource = '*'
    return discovery_mgr.import_resources(resource, args.offline)



def main(argv=sys.argv[1:]):
    LoggingService().init_cli_logging()

    parser = argparse.ArgumentParser(description='Integrated Manager Commands')
    subparsers = parser.add_subparsers(dest='operation', help='Actions')

    #Three letter variable names are parser + command name
    #pad = Parser add_device
    #plr = Parser list_rack

    #add_device
    pad = subparsers.add_parser('add_device', help='Add a device to be managed')
    pad.add_argument('-l', '--label', required=True, help='Label for the device being added')
    pad.add_argument('-u', '--user', required=True,
                     help='The authorized user id to the device being added')
    pad.add_argument('-p', '--password',
                     help='The password of the authorized user or private key,'
                          ' if not specified prompts for the password')
    pad.add_argument('-k', '--key', help='private key to authenticate the user id')
    pad.add_argument('-a', '--address', required=True,
                     help='Ip Address or hostname for the device being added')
    pad.add_argument('-t', '--type', choices=device_mgr.list_supported_device_types(),
                     help='The type of the device being added')
    pad.add_argument('-r', '--rack', help='The rack label, defaults to the first rack')
    pad.add_argument('--rack-location', help='The location in the rack of the device being added')

    #add_rack
    par = subparsers.add_parser('add_rack', help='Add a rack to group devices')
    par.add_argument('-l', '--label', required=True, help='Label for the rack being added')
    par.add_argument('--data-center',
                     help='Descriptive name of the data center where the rack resides')
    par.add_argument('--location', help='Location within the data center of the rack')
    par.add_argument('-n', '--notes',
                     help='Text notes with any additional information about the rack')

    #change_device
    pcd = subparsers.add_parser('change_device', help='Modify parameters associated with a device')
    pcd.add_argument('-l', '--label', required=True, help='Label for the device being modified')
    pcd.add_argument('--new-label', help='New label for the device')
    pcd.add_argument('-u', '--user', help='Authorized user id of the device')
    pcd.add_argument('-p', '--password', help='The password of the authorized user or private key')
    pcd_mxg = pcd.add_mutually_exclusive_group()
    pcd_mxg.add_argument('-P', '--prompt-password', action='store_true',
                         help='Prompts for entry of the password')
    pcd_mxg.add_argument('-k', '--key', help='private key to authenticate the userid id')
    pcd.add_argument('-a', '--address', help='New Ip Address or hostname of the device')
    pcd.add_argument('-r', '--rack', help='The label of the rack to assign the device to')
    pcd.add_argument('--rack-location', help='The location in the rack of the device')

    #change_device_password
    pcdp = subparsers.add_parser('change_device_password', help='Change the password on the device')
    pcdp.add_argument('-l', '--label', required=True, help='Label for the device being modified')
    pcdp.add_argument('-o', '--oldpassword', help='The current password of the device')
    pcdp.add_argument('-n', '--newpassword', help='The new password of the device')

    #change_rack
    pcr = subparsers.add_parser('change_rack', help='Modify parameters associated with a rack')
    pcr.add_argument('-l', '--label', required=True, help='Label for the rack being modified')
    pcr.add_argument('--new-label', help='New label for the rack.')
    pcr.add_argument('--data-center',
                     help='Decriptive name of the data cneter where the rack resides')
    pcr.add_argument('--location', help='Location within the data center of the rack')
    pcr.add_argument('-n', '--notes',
                     help='Text notes with any additional information about the rack')

    #list_devices
    pld = subparsers.add_parser('list_devices', help='List the managed devices')
    pld_mxg = pld.add_mutually_exclusive_group()
    pld.add_argument('-b', '--briefly', action='store_true', help='Only list the device labels')
    pld_mxg.add_argument('-l', '--label',
                         help='The label of the device to list, multiple labels are comma'
                              ' separated.')
    pld_mxg.add_argument('-t', '--type',
                         help='The type of the device to list, multiple types are comma separated.')
    pld_mxg.add_argument('-r', '--rack',
                         help='The rack label of the device to list, multiple rack labels are'
                              ' comma separated.')

    #list_rack
    plr = subparsers.add_parser('list_racks', help='List the managed racks')
    plr.add_argument('-b', '--briefly', action='store_true', help='Only list the rack labels')
    plr.add_argument('-l', '--label',
                     help='The label of the rack to list, multiple labels are comma separated.')

    #list_supported_device_types
    subparsers.add_parser('list_supported_device_types',
                          help='List the supported device types')

    #remote_access
    pra = subparsers.add_parser('remote_access',
                                help='Interactive ssh session to a managed device.')
    pra.add_argument('-l', '--label', required=True,
                     help='Label of the device to ceate ssh session for.')

    #remove_device
    prd = subparsers.add_parser('remove_device', help='Removes a managed device')
    #prd.add_argument('-f', '--force', action='store_true',
    #                 help='Forces the removal of the device')
    prd_mxg = prd.add_mutually_exclusive_group()
    prd_mxg.add_argument('-a', '--all', action='store_true', help='Removes all the devices')
    prd_mxg.add_argument('-l', '--label',
                         help='Label of device to remove, multiple labels are comma separated.')

    #remove_rack
    prr = subparsers.add_parser('remove_rack', help='Removes a rack having no devices')
    prr.add_argument('-l', '--label', required=True, help='Label of the rack to be removed.')

    #list_discovery_plugins
    subparsers.add_parser('list_discovery_plugins',
                          help='List the supported discovery plugin types')

    #find_resources
    subparsers.add_parser('find_resources',
                          help='Loads all supported discovery plugins and lists resources ' \
                               'from them')

    #import_resources
    pir = subparsers.add_parser('import_resources',
                                help='Loads all supported discovery plugins and imports ' \
                                     'resources from them')
    pir.add_argument('--offline', action='store_true',
                     help='Imports resource into Inventory even if it is offline.')
    pir.add_argument('-l', '--label', required=False,
                     help='Label of the resource to import into Inventory. If omitted, ' \
                          'all are imported.')

    message = ''
    rc = -1
    args = parser.parse_args(argv)

    if args.operation == 'add_device':
        (rc, message) = add_device(args)
    elif args.operation == 'add_rack':
        (rc, message) = add_rack(args)
    elif args.operation == 'change_device':
        (rc, message) = change_device(args)
    elif args.operation == 'change_device_password':
        (rc, message) = change_device_password(args)
    elif args.operation == 'change_rack':
        (rc, message) = change_rack(args)
    elif args.operation == 'list_devices':
        (rc, message) = list_devices(args)
    elif args.operation == 'list_racks':
        (rc, message) = list_racks(args)
    elif args.operation == 'list_supported_device_types':
        (rc, message) = list_supported_device_types()
    elif args.operation == 'remote_access':
        (rc, message) = remote_access_cmd(args)
    elif args.operation == 'remove_device':
        (rc, message) = remove_device(args)
    elif args.operation == 'remove_rack':
        (rc, message) = remove_rack(args)
    elif args.operation == 'list_discovery_plugins':
        (rc, message) = list_discovery_plugins()
    elif args.operation == 'find_resources':
        (rc, message) = find_resources()
    elif args.operation == 'import_resources':
        (rc, message) = import_resources(args)
    else:
        parser.print_help()


    if message:
        print(message)
    return rc

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
