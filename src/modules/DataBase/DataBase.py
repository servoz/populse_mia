from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from DataBase.DataBaseModel import Tag, Scan, Value, Base, createDatabase
import os
import tempfile

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
        print("isTempProject : " + str(self.isTempProject))
        print("folder : " + self.folder)

    def addScan(self, name, checksum):
        scan = Scan(scan=name, checksum=checksum)
        self.session.add(scan)
        self.session.commit()

    def addTag(self, tag, visible, origin, type, unit, default, description):
        tag = Tag(tag=tag, visible=visible, origin=origin, type=type, unit=unit, default=default, description=description)
        self.session.add(tag)
        self.session.commit()

    def addValue(self, scan, tag, value):
        value = Value(scan=scan, tag=tag, current_value=value, raw_value=value)
        self.session.add(value)
        self.session.commit()

    def getScans(self):
        scans = self.session.query(Scan).filter().all()
        print("list of scans : " + scans)
        return scans

    def getValues(self):
        values = self.session.query(Value).filter().all()
        print("list of values : " + values)
        return values

    def getVisualizedTags(self):
        tags = self.session.query(Tag).filter(Tag.visible == True).all()
        print("list of visible tags : " + tags)
        return tags

    def setTagVisibility(self, name, visibility):
        Tag.update().\
            where(Tag.tag == name).\
            values(visible = visibility)
        self.session.commit()

    def setTagValue(self, scan, tag, new_value):
        Value.update().\
            where(Value.scan == scan and Value.tag == tag).\
            values(current_value = new_value)
        self.session.commit()

    def resetTag(self, scan, tag):
        Value.update(). \
            where(Value.scan == scan and Value.tag == tag). \
            values(current_value=Value.raw_value)
        self.session.commit()

    def removeScan(self, scan):
        Scan.delete().where(Scan.scan == scan)
        Value.delete().where(Value.scan == scan)
        self.session.commit()