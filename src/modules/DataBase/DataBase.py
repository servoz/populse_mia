from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.DataBaseModel import Tag, Scan, Value, Base, createDatabase
import os
import tempfile

class DataBase:

    def __init__(self, project_root_folder):
        if(project_root_folder == None):
            self.isTempProject = True
            tf = tempfile.TemporaryDirectory()
            self.folder = os.path.relpath(tf.name)
            createDatabase(self.folder)
        else:
            self.isTempProject = False
            self.folder = project_root_folder
        engine = create_engine('sqlite:///' + os.path.join(self.folder, 'database', 'mia2.db'))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        print(self.isTempProject)
        print(self.folder)

    def addScan(self, name, checksum):
        scan = Scan(scan=name, checksum=checksum)
        self.session.add(scan)
        self.session.commit()

    def addTag(self, tag, visible, origin, type, unit, default, description):
        tag = Tag(tag=tag, visible=visible, origin=origin, type=type, unit=unit, default=default, description=description)
        self.session.add(tag)
        self.session.commit()