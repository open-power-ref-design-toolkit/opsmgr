import os
import base64
from backports import configparser
from Crypto.Cipher import AES  # encryption library
from Crypto.Hash import SHA512
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from opsmgr.inventory.data_model import Base, Device, DeviceRole, Rack

OPSMGR_CONF = "/etc/opsmgr/opsmgr.conf"

def encrypt_data(str_to_encrypt):
    """ encrypt data in string to encoded value
    """
    # _METHOD_ = 'persistent_mgr.encryptData'
    block_size = 32

    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    padding = '{'

    # one-liner to sufficiently pad the text to be encrypted
    pad = lambda s: s + (block_size - len(s) % block_size) * padding

    # one-liners to encrypt/encode and decrypt/decode a string
    # encrypt with AES, encode with base64
    encode_aes = lambda c, s: base64.b64encode(c.encrypt(pad(s)))

    # Read secret key from file.
    passphrase = read_passphrase()

    # create a cipher object using the random secret
    cipher = AES.new(passphrase)

    # encode a string
    str_to_encrypt = encode_aes(cipher, str_to_encrypt)

    return str_to_encrypt.decode("utf-8")


def decrypt_data(str_to_decrypt):
    """ decrypt data in string to plaintext value
    """
    # _METHOD_ = 'persistent_mgr.decryptData'

    # the character used for padding--with a block cipher such as AES, the value
    # you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
    # used to ensure that your value is always a multiple of BLOCK_SIZE
    padding = b'{'

    # one-liners to encrypt/encode and decrypt/decode a string
    decode_aes = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(padding)

    # Read secret key from file.
    passphrase = read_passphrase()

    # create a cipher object using the random secret
    cipher = AES.new(passphrase)

    # decode the encoded string
    decoded = decode_aes(cipher, str_to_decrypt).decode("utf-8")

    return decoded


def read_passphrase():
    """ gets the passphrase info and returns it
    """
    # _METHOD_ = 'persistent_mgr.read_passphrase'
    if os.path.exists(OPSMGR_CONF):
        parser = configparser.ConfigParser()
        parser.read(OPSMGR_CONF, encoding='utf-8')
        passphrase = parser.get('DEFAULT', 'passphrase')
        # Hash the passphrase using a sha512 algorithm and 256 keysize It
        # returns the hashed string.
        key_hash = ''
        unicode_value = passphrase.encode('utf-8')
        hashobj = SHA512.new()
        hashobj.update(unicode_value)
        hash_value = hashobj.hexdigest()
        key_hash = hash_value[len(hash_value) - ((256 // 8)):
                              len(hash_value)]
        return key_hash
    else:
        pass
        #TODO raise an exception here

def read_database_connection():
    """ gets the database connection info and returns it
    """
    if os.path.exists(OPSMGR_CONF):
        parser = configparser.ConfigParser()
        parser.read(OPSMGR_CONF, encoding='utf-8')
        return parser.get('DATABASE', 'connection')
    else:
        pass
        #TODO raise an exception here

def create_database_session():
    """ creates a database session if one is not already created.
    """
    engine = create_engine(read_database_connection())
    Base.metadata.bind = engine
    db_session = sessionmaker(bind=engine)
    return db_session()

def get_device_by_label(session, label):
    """get Device by label
    Args:
        session: Active database session
        label: label to get device that matches
    Returns:
        device found or None
    """
    return session.query(Device).filter(Device.label == label).one_or_none()

def get_device_by_id(session, device_id):
    """get Device by id
    Args:
        session: Active database session
        device_id: id of the device
    Returns:
        device found or None
    """
    return session.query(Device).filter(Device.device_id == device_id).one_or_none()

def get_devices_by_labels(session, labels):
    """get Devices by labels
    Args:
        session: Active database session
        labels: list of labels to get device that matches
    Returns:
        [] Device list of devices found
        [] string list of labels not found
    """
    devices = []
    not_found_labels = []
    labels = [] if labels is None else labels
    for label in labels:
        device = get_device_by_label(session, label)
        if device is None:
            not_found_labels.append(label)
        else:
            devices.append(device)
    return (devices, not_found_labels)

def get_devices_by_ids(session, device_ids):
    """get Devices by ids
    Args:
        session: Active database session
        device_ids: list of ids of the devices
    Returns:
        [] Device list of devices found
        [] list of ids not found
    """
    devices = []
    not_found_ids = []
    device_ids = [] if device_ids is None else device_ids
    for device_id in device_ids:
        device = get_device_by_id(session, device_id)
        if device is None:
            not_found_ids.append(device_id)
        else:
            devices.append(device)
    return (devices, not_found_ids)

def get_devices_by_device_type(session, device_types):
    """get Devices by device_type
    Args:
        session: Active database session
        device_types: list of device_types
    Returns:
        [] Device list of devices found
        [] list of device_types not found
    """
    all_devices = []
    not_found_device_types = []
    device_types = [] if device_types is None else device_types
    for device_type in device_types:
        devices = session.query(Device).filter(Device.device_type == device_type).all()
        if len(devices) == 0:
            not_found_device_types.append(device_type)
        else:
            all_devices.append(devices)
    return (all_devices, not_found_device_types)

def get_all_devices(session):
    """get all devices from the data store
    Args:
        session: Active database session
    Returns:
        [] List of Device classes
    """
    return session.query(Device).order_by(Device.device_id).all()

def get_rack_by_label(session, label):
    """get rack by label
    Args:
        session: Active database session
        label: label to get rack that matches
    Returns:
        rack found or None
    """
    return session.query(Rack).filter(Rack.label == label).one_or_none()

def get_rack_by_id(session, rack_id):
    """get rack by id
    Args:
        session: Active database session
        rack_id: id of the rack
    Returns:
        rack found or None
    """
    return session.query(Rack).filter(Rack.rack_id == rack_id).one_or_none()

def get_racks_by_labels(session, labels):
    """get racks by labels
    Args:
        session: Active database session
        labels: list of labels to get racks that matches
    Returns:
        [] Rack list of racks found
        [] string list of labels not found
    """
    racks = []
    not_found_labels = []
    labels = [] if labels is None else labels
    for label in labels:
        rack = get_rack_by_label(session, label)
        if rack is None:
            not_found_labels.append(label)
        else:
            racks.append(rack)
    return (racks, not_found_labels)

def get_racks_by_ids(session, rack_ids):
    """get racks by ids
    Args:
        session: Active database session
        rack_ids: list of ids of the racks
    Returns:
        [] Rack list of racks found
        [] list of ids not found
    """
    racks = []
    not_found_ids = []
    rack_ids = [] if rack_ids is None else rack_ids
    for rack_id in rack_ids:
        rack = get_rack_by_id(session, rack_id)
        if rack is None:
            not_found_ids.append(rack_id)
        else:
            racks.append(rack)
    return (racks, not_found_ids)

def get_all_racks(session):
    """get all racks from the data store
    Args:
        session: Active database session
    Returns:
        [] List of Rack classes
    """
    return session.query(Rack).order_by(Rack.rack_id).all()

def get_device_roles_by_device_id(session, device_id):
    """ get the roles associated with a device
    Args:
        session: Active database session
        device_id: id of the device
    Return:
        [] List of DeviceRole classes
    """
    return session.query(DeviceRole).filter(DeviceRole.device_id == device_id).all()

def add_racks(session, racks):
    """ Adds the racks in the list to the data store

    Args:
        session: Active database session
        racks:  list of Rack classes
    """
    _add(session, racks)
    session.commit()

def add_devices(session, devices):
    """ Adds the devices in the list to the data store

    Args:
        session: Active database session
        devices:  list of Device classes
    """
    _add(session, devices)
    session.commit()

def add_ssh_keys(session, ssh_keys):
    _add(session, ssh_keys)
    session.commit()

def add_device_roles(session, device_roles):
    _add(session, device_roles)
    session.commit()

def update_rack(session):
    """ Updates racks in data store

    args:
        session: Active database session
    returns:
        nothing
    """
    session.commit()

def update_device(session):
    """ Updates devices in data store

    args:
        session: Active database session
    returns:
        nothing
    """
    session.commit()

def delete_racks(session, racks):
    """Removes list of Rack objects from data store

    args:
        session: Active database session
        racks:  list of Rack objects
    returns:
        nothing
    """
    _delete(session, racks)
    session.commit()

def delete_devices(session, devices):
    """ Removes list of Device objects from data store
        Removes any key associated with a device
    args:
        session: Active database session
        devices: list of Device objects
    returns:
        nothing
    """
    keys = []
    device_roles = []
    devices = [] if devices is None else devices
    for device in devices:
        key = device.key
        if key:
            keys.append(key)
        roles = get_device_roles_by_device_id(session, device.device_id)
        device_roles.extend(roles)
    _delete(session, keys)
    _delete(session, device_roles)
    _delete(session, devices)
    session.commit()

def delete_keys(session, keys):
    """Removes list of key classes from data store

    args:
        session: Active database session
        keys:  list of key classes
    returns:
        nothing
    """
    _delete(session, keys)
    session.commit()

def _add(session, items):
    items = [] if items is None else items
    for item in items:
        session.add(item)

def _delete(session, items):
    items = [] if items is None else items
    for item in items:
        session.delete(item)
