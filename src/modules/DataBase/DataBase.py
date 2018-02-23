from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from DataBase.DataBaseModel import Tag, Scan, Value, Base, createDatabase
import os

class DataBase:

    def __init__(self, project_root_folder):
        if(project_root_folder == None):
            self.isTempProject = True
            self.folder = os.path.join(os.path.relpath(os.curdir), '..', '..', 'temp_project')
            os.mkdir(self.folder)
            createDatabase(self.folder)
        else:
            self.isTempProject = False
            self.folder = project_root_folder
        engine = create_engine('sqlite:///' + os.path.join(self.folder, 'database', 'mia2.db'))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def addScan(self, name, checksum):
        scan = Scan(scan=name, checksum=checksum)
        self.session.add(scan)

    def addTag(self, tag, visible, origin, type, unit, default, description):
        tag = Tag(tag=tag, visible=visible, origin=origin, type=type, unit=unit, default=default, description=description)
        self.session.add(tag)

    def addValue(self, scan, tag, value):
        value = Value(scan=scan, tag=tag, current_value=value, raw_value=value)
        self.session.add(value)

    def getScans(self):
        scans = self.session.query(Scan).filter().all()
        return scans

    def getValues(self):
        values = self.session.query(Value).filter().all()
        return values

    def getTags(self):
        tags = self.session.query(Tag.tag).filter().all()
        return tags

    def getVisualizedTags(self):
        tags = self.session.query(Tag.tag).filter(Tag.visible == True).all()
        return tags

    def setTagVisibility(self, name, visibility):
        Tag.update().\
            where(Tag.tag == name).\
            values(visible = visibility)

    def setTagValue(self, scan, tag, new_value):
        Value.update().\
            where(Value.scan == scan and Value.tag == tag).\
            values(current_value = new_value)

    def resetTag(self, scan, tag):
        Value.update(). \
            where(Value.scan == scan and Value.tag == tag). \
            values(current_value=Value.raw_value)

    def removeScan(self, scan):
        Scan.delete().where(Scan.scan == scan)
        Value.delete().where(Value.scan == scan)

    def saveModifications(self):
        self.session.commit()