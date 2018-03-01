from sqlalchemy import create_engine, update, Table
from sqlalchemy.orm import sessionmaker
from DataBase.DataBaseModel import Tag, Scan, Value, Base, createDatabase
import os
import tempfile
import yaml
from SoftwareProperties.Config import Config
from DataBase.DataBaseModel import TAG_ORIGIN_RAW, TAG_TYPE_STRING, TAG_ORIGIN_USER
import re

class DataBase:

    def __init__(self, project_root_folder, new_project):
        if(project_root_folder == None):
            self.isTempProject = True
            self.folder = os.path.relpath(tempfile.mkdtemp())
        else:
            self.isTempProject = False
            self.folder = project_root_folder
            self.properties = self.loadProperties()
        if(new_project):
            createDatabase(self.folder)
        engine = create_engine('sqlite:///' + os.path.join(self.folder, 'database', 'mia2.db'))
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        print("new database : " + self.folder)
        if new_project:
            config = Config()
            for default_tag in config.getDefaultTags():
                # Tags by default set as visible
                self.addTag(default_tag, True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, "", "", "") # Modify params
                self.saveModifications()

    """ FROM properties/properties.yml """

    def loadProperties(self):
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def getName(self):
        if(self.isTempProject):
            return ""
        else:
            return self.properties["name"]

    def setName(self, name):
        if not self.isTempProject:
            self.properties["name"] = name
            self.saveConfig()

    def saveConfig(self):
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.properties, configfile, default_flow_style=False, allow_unicode=True)

    def getDate(self):
        if(self.isTempProject):
            return ""
        else:
            return self.properties["date"]

    def getSortedTag(self):
        if (self.isTempProject):
            return ""
        else:
            return self.properties["sorted_tag"]

    def setSortedTag(self, tag):
        if not self.isTempProject:
            self.properties["sorted_tag"] = tag
            self.saveConfig()

    def getSortOrder(self):
        if (self.isTempProject):
            return ""
        else:
            return self.properties["sort_order"]

    def setSortOrder(self, order):
        if not self.isTempProject:
            self.properties["sort_order"] = order
            self.saveConfig()


    """ FROM SQlite Database """

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

    def getValuesGivenTag(self, tag):
        values = self.session.query(Value).filter(Value.tag == tag).all()
        return values

    def getValuesGivenScan(self, scan):
        values = self.session.query(Value).filter(Value.scan == scan).all()
        return values

    def getValue(self, scan, tag):
        values = self.session.query(Value).filter(Value.tag == tag).filter(Value.scan == scan).all()
        #TODO return error if len(values) != 1
        return values[0]

    def scanHasTag(self, scan, tag):
        values = self.session.query(Value).filter(Value.tag == tag).filter(Value.scan == scan).all()
        return len(values) == 1

    def getTags(self):
        tags = self.session.query(Tag).filter().all()
        return tags

    def getVisualizedTags(self):
        tags = self.session.query(Tag).filter(Tag.visible == True).all()
        return tags

    def getTagOrigin(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].origin

    def getTagVisibility(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].visible

    def getTagType(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].type

    def getTagDescription(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].description

    def getUserTags(self):
        tags = self.session.query(Tag).filter(Tag.origin == TAG_ORIGIN_USER).all()
        return tags

    def setTagVisibility(self, name, visibility):
        tags = self.session.query(Tag).filter(Tag.tag == name).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.visible = visibility

    def resetAllVisibilities(self):
        tags = self.session.query(Tag).filter().all()
        for tag in tags:
            tag.visible = False

    def setTagValue(self, scan, tag, new_value):
        tags = self.session.query(Value).filter(Value.scan==scan).filter(Value.tag==tag).all()
        #TODO return error if len(tags) != 1
        tag = tags[0]
        tag.current_value = new_value

    def resetTag(self, scan, tag):
        tags = self.session.query(Value).filter(Value.scan==scan).filter(Value.tag==tag).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.current_value = tag.raw_value

    def removeScan(self, scan):
        tags = self.session.query(Value).filter(Value.scan == scan).all()
        for tag in tags:
            self.session.delete(tag)
        scans = self.session.query(Scan).filter(Scan.scan == scan).all()
        # TODO return error if len(scans) != 1
        self.session.delete(scans[0])

    def removeTag(self, tag):
        values = self.session.query(Value).filter(Value.tag == tag).all()
        for value in values:
            self.session.delete(value)
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        self.session.delete(tags[0])

    def saveModifications(self):
        self.session.commit()

    def getScansSimpleSearch(self, search):
        values = self.session.query(Value).filter(Value.current_value.contains(search)).all()
        scans = []
        for value in values:
            if not value.scan in scans and self.getTagVisibility(value.tag):
                scans.append(value.scan)
        return scans