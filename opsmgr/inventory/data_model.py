from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Text, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Rack(Base):
    __tablename__ = "rack"
    rack_id = Column(Integer, primary_key=True)

    #user defined label for device
    label = Column(String(255), nullable=False, unique=True)

    data_center = Column(String(255))
    location = Column(String(255))
    notes = Column(Text())

    devices = relationship("Device", back_populates="rack")

    def to_dict_obj(self):
        result = {}
        result["rackid"] = self.rack_id
        result["label"] = self.label
        result["location"] = self.location
        result["data-center"] = self.data_center
        result["notes"] = self.notes
        return result

    def __repr__(self, *args, **kwargs):
        _dict = self.to_dict_obj()
        return str(_dict)

class Device(Base):
    __tablename__ = "device"
    device_id = Column(Integer, primary_key=True)

    #user defined label for device
    label = Column(String(255), nullable=False, unique=True)

    #machine type model and serial number pulled from the device
    machine_type_model = Column(String(64))
    serial_number = Column(String(64))

    #Location of the device within a rack
    eia_location = Column(String(16))

    #Integer of the constants.device_type enum
    device_type = Column(String(64), nullable=False)

    #Version of firmware/software device is running
    version = Column(String(64))

    #architecture of the device
    architecture = Column(String(10))

    #True if able to login to device and validate
    #the info used to discover it is correct.
    validated = Column(Boolean(False))

    #Does login info go in another table?
    userid = Column(String(255))
    password = Column(String(255))

    #Does IP info go in another table?
    address = Column(String(255), unique=True)
    hostname = Column(String(255))

    status = Column(SmallInteger)
    statusTime = Column(DateTime)

    rack_id = Column(Integer, ForeignKey('rack.rack_id'), nullable=False)
    rack = relationship("Rack", back_populates="devices")
    key = relationship("Key", uselist=False, back_populates="device")

    def to_dict_obj(self):
        result = {}
        result["deviceid"] = self.device_id
        result["label"] = self.label
        result["rackid"] = self.rack_id
        result["rack-eia-location"] = self.eia_location
        result["machine-type-model"] = self.machine_type_model
        result["serial-number"] = self.serial_number
        result["ip-address"] = self.address
        result["hostname"] = self.hostname
        result["userid"] = self.userid
        result["password"] = self.password
        result["version"] = self.version
        result["architecture"] = self.architecture
        result["validated"] = self.validated
        result["device-type"] = self.device_type
        result["status"] = self.status
        result["statusTime"] = self.statusTime
        return result

    def __repr__(self, *args, **kwargs):
        _dict = self.to_dict_obj()
        return str(_dict)

class Key(Base):
    __tablename__ = "key"
    key_id = Column(Integer, primary_key=True)

    device_id = Column(Integer, ForeignKey('device.device_id'))
    device = relationship("Device", back_populates="key")
    type = Column(String(10), nullable=False)
    value = Column(Text(), nullable=False)
    password = Column(String(255))

class DeviceRole(Base):
    __tablename__ = "device_role"
    device_id = Column(Integer, ForeignKey('device.device_id'), primary_key=True, nullable=False)
    role = Column(String(30), primary_key=True, nullable=False)

    def __init__(self, device_id, role):
        self.device_id = device_id
        self.role = role

    def __repr__(self):
        return "<DeviceRole('%s', '%s')>" % (self.device_id, self.role)

