from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy import create_engine
import os

TAG_ORIGIN_RAW = "raw"
TAG_ORIGIN_USER = "user"
TAG_TYPE_STRING = "string"
TAG_TYPE_INTEGER = "integer"
TAG_TYPE_FLOAT = "float"
TAG_TYPE_LIST = "list"

Base = declarative_base()

def createDatabase(project_root_folder):
    os.mkdir(os.path.join(project_root_folder, 'database'))
    engine = create_engine('sqlite:///' + os.path.join(project_root_folder, 'database', 'mia2.db'))
    Base.metadata.create_all(engine)

class Scan(Base):
    __tablename__ = 'scan'
    scan = Column(String, primary_key=True)
    checksum = Column(String, nullable=False)

    def __repr__(self):
        return "<Scan(scan='%s', checksum='%s')>" % (self.scan, self.checksum)

class Tag(Base):
    __tablename__ = 'tag'
    tag = Column(String, primary_key=True)
    visible = Column(Boolean, nullable=False)
    origin = Column(Enum(TAG_ORIGIN_RAW, TAG_ORIGIN_USER), nullable=False)
    type = Column(Enum(TAG_TYPE_STRING, TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_LIST), nullable=False)
    unit = Column(Enum(''), nullable=False)
    default = Column(String, nullable=False)
    description = Column(String, nullable=False)
    def __repr__(self):
        return "<Tag(tag='%s', visible='%s', origin='%s', type='%s', unit='%s', default='%s', description='%s')>" % (self.tag, self.visible, self.origin, self.type, self.unit, self.default, self.description)

class Value(Base):
    __tablename__ = 'value'
    scan = Column(String, ForeignKey(Scan.scan), primary_key=True)
    tag = Column(String, ForeignKey(Tag.tag), primary_key=True)
    current_value = Column(String, nullable=False)
    raw_value = Column(String, nullable=True)

    def __repr__(self):
        return "<Value(scan='%s', tag='%s', current_value='%s', raw_value='%s')>" % (self.scan, self.tag, self.current_value, self.raw_value)