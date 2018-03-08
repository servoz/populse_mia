from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.DataBaseModel import Tag, Scan, Value, Base, createDatabase
import os
import tempfile
import yaml
from SoftwareProperties.Config import Config
from DataBase.DataBaseModel import TAG_TYPE_STRING, TAG_ORIGIN_USER

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
        if new_project:
            self.refreshTags()
        self.unsavedModifications = False
        self.history = []
        self.historyHead = 0

    """ FROM properties/properties.yml """

    def refreshTags(self):

        #Tags cleared
        tags = self.session.query(Tag).filter().all()
        for tag in tags:
            self.session.delete(tag)

        #New tags added
        config = Config()
        if config.getDefaultTags() != None:
            for default_tag in config.getDefaultTags():
                if not self.hasTag(default_tag):
                    # Tags by default set as visible
                    self.addTag(default_tag, True, TAG_ORIGIN_USER, TAG_TYPE_STRING, "", "", "")  # Modify params?
                    self.saveModifications()

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
            self.unsavedModifications = True

    def getSortOrder(self):
        if (self.isTempProject):
            return ""
        else:
            return self.properties["sort_order"]

    def setSortOrder(self, order):
        if not self.isTempProject:
            self.properties["sort_order"] = order
            self.saveConfig()
            self.unsavedModifications = True


    """ FROM SQlite Database """

    def addScan(self, name, checksum):
        scan = Scan(scan=name, checksum=checksum)
        self.session.add(scan)
        self.unsavedModifications = True

    def addTag(self, tag, visible, origin, type, unit, default, description):
        tag = Tag(tag=tag, visible=visible, origin=origin, type=type, unit=unit, default=default, description=description)
        self.session.add(tag)
        self.unsavedModifications = True

    def addValue(self, scan, tag, current_value, raw_value):
        value = Value(scan=scan, tag=tag, current_value=current_value, raw_value=raw_value)
        self.session.add(value)
        self.unsavedModifications = True

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

    def hasTag(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        return len(tags) == 1

    def getTagOrigin(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].origin

    def getTagVisibility(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].visible

    def getTagDefault(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].default

    def getTagUnit(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].unit

    def getTagDescription(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].description

    def getTagType(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].type

    def getTag(self, tag):
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0]

    def getUserTags(self):
        tags = self.session.query(Tag).filter(Tag.origin == TAG_ORIGIN_USER).all()
        return tags

    def setTagVisibility(self, name, visibility):
        tags = self.session.query(Tag).filter(Tag.tag == name).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.visible = visibility
        self.unsavedModifications = True

    def setTagOrigin(self, name, origin):
        tags = self.session.query(Tag).filter(Tag.tag == name).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.origin = origin
        self.unsavedModifications = True

    def resetAllVisibilities(self):
        tags = self.session.query(Tag).filter().all()
        for tag in tags:
            tag.visible = False
        self.unsavedModifications = True

    def setTagValue(self, scan, tag, new_value):
        tags = self.session.query(Value).filter(Value.scan==scan).filter(Value.tag==tag).all()
        #TODO return error if len(tags) != 1
        tag = tags[0]
        tag.current_value = new_value
        self.unsavedModifications = True

    def resetTag(self, scan, tag):
        tags = self.session.query(Value).filter(Value.scan==scan).filter(Value.tag==tag).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.current_value = tag.raw_value
        self.unsavedModifications = True

    def removeScan(self, scan):
        tags = self.session.query(Value).filter(Value.scan == scan).all()
        for tag in tags:
            self.session.delete(tag)
        scans = self.session.query(Scan).filter(Scan.scan == scan).all()
        # TODO return error if len(scans) != 1
        self.session.delete(scans[0])
        self.unsavedModifications = True

    def removeTag(self, tag):
        values = self.session.query(Value).filter(Value.tag == tag).all()
        for value in values:
            self.session.delete(value)
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        self.session.delete(tags[0])
        self.unsavedModifications = True

    def saveModifications(self):
        self.session.commit()
        self.unsavedModifications = False

    def unsaveModifications(self):
        self.session.rollback()
        self.unsavedModifications = False

    def getScansSimpleSearch(self, search):
        values = self.session.query(Value).filter(Value.current_value.contains(search)).all()
        scans = []
        for value in values:
            if not value.scan in scans and self.getTagVisibility(value.tag):
                scans.append(value.scan)
        return scans

    def getScansAdvancedSearch(self, links, fields, conditions, values, nots):
        masterRequest = ""
        i = 0
        while i < len(conditions):
            request = ""
            if(nots[i] == "NOT"):
                request = request + "select scan from Value EXCEPT "
            request = request + "select scan from Value where "
            condition = ""
            if(fields[i] != "All visualized tags"):
                condition = condition + "tag == '" + fields[i] + "' and "
            if(conditions[i] == "CONTAINS"):
                condition = condition + "current_value LIKE '%" + values[i] + "%'"
            elif(conditions[i] == "IN"):
                condition = condition + "current_value IN " + values[i]
            elif (conditions[i] == "BETWEEN"):
                condition = condition + "current_value BETWEEN " + values[i]
            else:
                condition = condition + "current_value " + conditions[i] + " '" + values[i] + "'"
            request = request + condition
            if i < len(conditions) - 1:
                if(links[i] == "AND"):
                    request = request + " INTERSECT "
                else:
                    request = request + " UNION "
            masterRequest = masterRequest + request
            i = i + 1
        result = self.session.execute(masterRequest)
        scans = []
        for row in result:
            if not row[0] in scans:
                scans.append(row[0])
        return scans

    def undo(self):
        print(self.history)
        if(self.historyHead > 0 and len(self.history) >= self.historyHead):
            toUndo = self.history[self.historyHead - 1]
            action = toUndo[0]
            if(action == "add_tag"):
                tagToRemove = toUndo[1]
                self.removeTag(tagToRemove)
            if (action == "remove_tags"):
                scansRemoved = toUndo[1]
                i = 0
                while i < len(scansRemoved):
                    tagToReput = scansRemoved[i]
                    self.addTag(tagToReput.tag, tagToReput.visible, tagToReput.origin, tagToReput.type, tagToReput.unit, tagToReput.default, tagToReput.description)
                    i = i + 1
                valuesRemoved = toUndo[2]
                i = 0
                while i < len(valuesRemoved):
                    valueToReput = valuesRemoved[i]
                    self.addValue(valueToReput.scan, valueToReput.tag, valueToReput.current_value, valueToReput.raw_value)
                    i = i + 1
            self.historyHead = self.historyHead - 1