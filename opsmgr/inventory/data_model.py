from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Text, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Rack(Base):
    __tablename__ = "rack"
    rack_id = Column(Integer, primary_key=True)

    #user defined label for rack
    label = Column(String(255), nullable=False, unique=True)

    data_center = Column(String(255))
    room = Column(String(255))
    row = Column(String(255))
    notes = Column(Text())

    resources = relationship("Resource", back_populates="rack")

    def to_dict_obj(self):
        result = {}
        result["rackid"] = self.rack_id
        result["label"] = self.label
        result["room"] = self.room
        result["row"] = self.row
        result["data-center"] = self.data_center
        result["notes"] = self.notes
        return result

    def __repr__(self, *args, **kwargs):
        _dict = self.to_dict_obj()
        return str(_dict)

class Resource(Base):
    __tablename__ = "resource"
    resource_id = Column(Integer, primary_key=True)

    #user defined label for resource
    label = Column(String(255), nullable=False, unique=True)

    #machine type model and serial number pulled from the resource
    machine_type_model = Column(String(64))
    serial_number = Column(String(64))

    #Location of the device within a rack
    eia_location = Column(String(16))

    #Resource type from the plugin that manages it
    resource_type = Column(String(64), nullable=False)

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
    rack = relationship("Rack", back_populates="resources")
    key = relationship("Key", uselist=False, back_populates="resource")

    def to_dict_obj(self):
        result = {}
        result["resourceid"] = self.resource_id
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
        result["resource-type"] = self.resource_type
        result["status"] = self.status
        result["statusTime"] = self.statusTime
        return result

    def __repr__(self, *args, **kwargs):
        _dict = self.to_dict_obj()
        return str(_dict)

class Key(Base):
    __tablename__ = "key"
    key_id = Column(Integer, primary_key=True)

    resource_id = Column(Integer, ForeignKey('resource.resource_id'))
    resource = relationship("Resource", back_populates="key")
    type = Column(String(10), nullable=False)
    value = Column(Text(), nullable=False)
    password = Column(String(255))

class ResourceRole(Base):
    __tablename__ = "resource_role"
    resource_id = Column(Integer, ForeignKey('resource.resource_id'),
                         primary_key=True, nullable=False)
    role = Column(String(30), primary_key=True, nullable=False)

    def __init__(self, resource_id, role):
        self.resource_id = resource_id
        self.role = role

    def __repr__(self):
        return "<ResourceRole('%s', '%s')>" % (self.resource_id, self.role)

