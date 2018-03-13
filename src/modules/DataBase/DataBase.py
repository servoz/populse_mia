from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from DataBase.DataBaseModel import Tag, Scan, Value, Base, createDatabase
import os
import tempfile
import yaml
from SoftwareProperties.Config import Config
from DataBase.DataBaseModel import TAG_TYPE_STRING, TAG_ORIGIN_USER
import pickle

class DataBase:

    def __init__(self, project_root_folder, new_project):
        """ Database constructor
            New instance when switching project
            :param project_root_folder: projet root folder
                   If None, a temporary folder will be created

            :param new_project: Boolean to know if we have to create the database
                                True when New Project pop up or at the beginning for unnamed project
                                False when Open Project or Save as pop up

            self.isTempProject: To know if it's still unnamed project or not
            self.folder: Project root folder, relative
            self.properties: Properties of the project: Name, date of creation, sorted tag, and sort order (Not for Unnamed project)
            self.unsavedModifications: To know if there are unsaved modifications
            self.history: List of actions done on the project since the last opening
            self.historyHead: Index to know where we are in the history list

            Memory approximation: the database file takes approximately 26 000 octets (1 bytes, 8 bits) per scan

        """
        # We don't have a project root folder at the opening of the software (Unnamed project), we generate a temporary folder
        if(project_root_folder == None):
            self.isTempProject = True
            self.folder = os.path.relpath(tempfile.mkdtemp())
        # We have a project root folder(New, Open, Save As)
        else:
            self.isTempProject = False
            self.folder = project_root_folder
            self.properties = self.loadProperties()
        # We create the database if it does not exists yet (for Unnamed project and New project)
        if(new_project):
            createDatabase(self.folder)
        # We open the database
        engine = create_engine('sqlite:///' + os.path.join(self.folder, 'database', 'mia2.db'))
        Base.metadata.bind = engine
        # We create a session
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
        # If it's a new project, we refresh the list of tags, in case of changes in MIA2 preferences
        if new_project:
            self.refreshTags()
        # Initialisation
        self.unsavedModifications = False
        self.history = []
        self.historyHead = 0

    """ FROM properties/properties.yml """

    def refreshTags(self):
        """ Refreshes the tag if the project is new
            Makes sense if the user just changed the list of default tags in MIA2 preferences
        """

        # Tags cleared
        tags = self.session.query(Tag).filter().all()
        for tag in tags:
            self.session.delete(tag)

        # New tags added
        config = Config()
        if config.getDefaultTags() != None:
            for default_tag in config.getDefaultTags():
                if not self.hasTag(default_tag):
                    # Tags by default set as visible
                    self.addTag(default_tag, True, TAG_ORIGIN_USER, TAG_TYPE_STRING, "", "", "")  # Modify params?
                    self.saveModifications()

    def loadProperties(self):
        """ Loads the properties file (Unnamed project does not have this file) """
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def getName(self):
        """ Returns the name of the project if it's not Unnamed project, otherwise empty string """
        if(self.isTempProject):
            return ""
        else:
            return self.properties["name"]

    def setName(self, name):
        """ Sets the name of the project if it's not Unnamed project, otherwise does nothing
            :param name: new name of the project
        """
        if not self.isTempProject:
            self.properties["name"] = name
            self.saveConfig()

    def saveConfig(self):
        """ Save the changes in the properties file """
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.properties, configfile, default_flow_style=False, allow_unicode=True)

    def getDate(self):
        """ Returns the date of creation of the project if it's not Unnamed project, otherwise empty string """
        if(self.isTempProject):
            return ""
        else:
            return self.properties["date"]

    def getSortedTag(self):
        """ Returns the sorted tag of the project if it's not Unnamed project, otherwise empty string """
        if (self.isTempProject):
            return ""
        else:
            return self.properties["sorted_tag"]

    def setSortedTag(self, tag):
        """ Sets the sorted tag of the project if it's not Unnamed project, otherwise does nothing
            :param tag: new sorted tag of the project
        """
        if not self.isTempProject:
            self.properties["sorted_tag"] = tag
            self.unsavedModifications = True

    def getSortOrder(self):
        """ Returns the sort order of the project if it's not Unnamed project, otherwise empty string """
        if (self.isTempProject):
            return ""
        else:
            return self.properties["sort_order"]

    def setSortOrder(self, order):
        """ Sets the sort order of the project if it's not Unnamed project, otherwise does nothing
            :param order: new sort order of the project (ascending or descending)
        """
        if not self.isTempProject:
            self.properties["sort_order"] = order
            self.unsavedModifications = True


    """ FROM SQlite Database """

    def addScan(self, name, checksum):
        """
        To add a new scan to the project
        :param name: FileName of the scan
        :param checksum: MD5 checksum of the scan file
        """
        scan = Scan(scan=name, checksum=checksum)
        self.session.add(scan)
        self.unsavedModifications = True

    def addTag(self, tag, visible, origin, type, unit, default, description):
        """
        To add a new tag to the project
        :param tag: Tag name
        :param visible: True or False
        :param origin: Raw or user
        :param type: String, Integer, Float, or List
        :param unit:
        :param default:
        :param description:
        """
        tag = Tag(tag=tag, visible=visible, origin=origin, type=type, unit=unit, default=default, description=description)
        self.session.add(tag)
        self.unsavedModifications = True

    def addValue(self, scan, tag, current_value, raw_value):
        """
        To add a new value (a new cell in the databrowser)
        :param scan: FileName of the scan
        :param tag: Tag name
        :param current_value: Current value displayed in the DataBrowser (Raw_value for raw tags and default_value for user tags)
        :param raw_value: Raw value of the cell (None of user tags)
        """
        value = Value(scan=scan, tag=tag, current_value=current_value, raw_value=raw_value)
        self.session.add(value)
        self.unsavedModifications = True

    def getScans(self):
        """
        To get all Scan objects
        :return: All Scan objects
        """
        scans = self.session.query(Scan).filter().all()
        return scans

    def getValues(self):
        """
        To get all values
        :return: All Value objects
        """
        values = self.session.query(Value).filter().all()
        return values

    def getScan(self, scan):
        """
        To get the Scan object of the scan
        :param scan: FileName of the scan
        :return: The Scan object of the scan
        """
        scans = self.session.query(Scan).filter(Scan.scan == scan).all()
        #TODO return error if len(scans) != 1
        return scans[0]

    def getValuesGivenTag(self, tag):
        """
        To get all the values of the tag
        :param tag: Tag name
        :return: A list of Value objects for the tag
        """
        values = self.session.query(Value).filter(Value.tag == tag).all()
        return values

    def getValuesGivenScan(self, scan):
        """
        To get all the values of the scan
        :param scan: FileName of the scan
        :return: A list of Value objects for the scan
        """
        values = self.session.query(Value).filter(Value.scan == scan).all()
        return values

    def getValue(self, scan, tag):
        """
        To get the Value object of the cell <Scan, Tag>
        :param scan: FileName of the scan
        :param tag: Tag name
        :return: The Value object of the cell
        """
        values = self.session.query(Value).filter(Value.tag == tag).filter(Value.scan == scan).all()
        #TODO return error if len(values) != 1
        return values[0]

    def scanHasTag(self, scan, tag):
        """
        To know if the scan has a value for the tag
        :param scan: FileName of the scan
        :param tag: Tag name
        :return: True if the scan has a value for the tag, False otherwise
        """
        values = self.session.query(Value).filter(Value.tag == tag).filter(Value.scan == scan).all()
        return len(values) == 1

    def getTags(self):
        """
        Gives a list of the tags of the project (Tag objects)
        :return: A list of Tag objects of the project
        """
        tags = self.session.query(Tag).filter().all()
        return tags

    def getVisualizedTags(self):
        """
        Gives a list of the visualized tags of the project
        :return: A list of the visualized tags of the project
        """
        tags = self.session.query(Tag).filter(Tag.visible == True).all()
        return tags

    def hasTag(self, tag):
        """
        To know if the tag is in the project
        :param tag: Tag name
        :return: True if the tag is in the project, False otherwise
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        return len(tags) == 1

    def getTagOrigin(self, tag):
        """
        Gives the origin of the tag
        :param tag: Tag name
        :return: The origin of the tag (raw or user)
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].origin

    def getTagVisibility(self, tag):
        """
        Gives the visibility of the tag
        :param tag: Tag name
        :return: The visibility of the tag (True or False)
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].visible

    def getTagDefault(self, tag):
        """
        Gives the default value of the tag
        :param tag: Tag name
        :return: Default value of the tag
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].default

    def getTagUnit(self, tag):
        """
        Gives the unit of the tag
        :param tag: Tag name
        :return: The unit of the tag
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].unit

    def getTagDescription(self, tag):
        """
        Gives the description of the tag
        :param tag: Tag name
        :return: The description of the tag (tooltip displayed when putting the mouse on the headers in the DataBrowser)
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].description

    def getTagType(self, tag):
        """
        Gives the type of the tag
        :param tag: Tag name
        :return: The type of the tag (String, Integer, Float, or List)
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0].type

    def getTag(self, tag):
        """
        Gives the Tag object of the tag
        :param tag: Tag name
        :return: The Tag object associated to the tag
        """
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        return tags[0]

    def getUserTags(self):
        """
        Gives all the user tags of the project
        :return: The list of user tags of the project
        """
        tags = self.session.query(Tag).filter(Tag.origin == TAG_ORIGIN_USER).all()
        return tags

    def setTagVisibility(self, name, visibility):
        """
        Sets the visibility of the tag
        :param name: Tag name
        :param visibility: New visibility (True or False)
        """
        tags = self.session.query(Tag).filter(Tag.tag == name).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.visible = visibility
        self.unsavedModifications = True

    def setTagOrigin(self, name, origin):
        """
        Sets the origin of the tag
        :param name: Tag name
        :param origin: New origin of the tag (raw or user)
        """
        tags = self.session.query(Tag).filter(Tag.tag == name).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        tag.origin = origin
        self.unsavedModifications = True

    def resetAllVisibilities(self):
        """
        Puts the visibility of all tags of the project to False
        """
        tags = self.session.query(Tag).filter().all()
        for tag in tags:
            tag.visible = False
        self.unsavedModifications = True

    def setTagValue(self, scan, tag, new_value):
        """ Sets the value of the cell asked
            :param scan: The FileName of the scan to reset
            :param tag: The tag name to reset
            :param new_value: New value of the cell
        """
        # We only change the cell if the tag is not FileName
        if not tag == "FileName":
            tags = self.session.query(Value).filter(Value.scan==scan).filter(Value.tag==tag).all()
            # There is already a value
            if len(tags) == 1:
                tag = tags[0]
                tag.current_value = new_value
            self.unsavedModifications = True

    def resetTag(self, scan, tag):
        """
        Resets the value of the cell asked, only done on raw tags, does not make sense on user tags
        :param scan: The FileName of the scan to reset
        :param tag: The tag name to reset
        """
        tags = self.session.query(Value).filter(Value.scan==scan).filter(Value.tag==tag).all()
        # TODO return error if len(tags) != 1
        tag = tags[0]
        if(tag.raw_value != None):
            tag.current_value = tag.raw_value
            self.unsavedModifications = True

    def removeScan(self, scan):
        """
        Removes a scan from the project (corresponds to a row in the databrowser)
        Removes the scan from the list of scans (Scan table), and all the values corresponding to this scan (Value table)
        :param scan: FileName of the scan to remove
        """
        # All the values of the scan are removed
        tags = self.session.query(Value).filter(Value.scan == scan).all()
        for tag in tags:
            self.session.delete(tag)
        # The scan is removed from the list of scans
        scans = self.session.query(Scan).filter(Scan.scan == scan).all()
        # TODO return error if len(scans) != 1
        # TODO remove tag if only used for this scan
        self.session.delete(scans[0])
        self.unsavedModifications = True

    def removeTag(self, tag):
        """
        Removes a tag from the project (corresponds to a column in the databrowser)
        We can only remove user tags from the software
        :param tag: Name of the tag to remove
        """
        values = self.session.query(Value).filter(Value.tag == tag).all()
        for value in values:
            self.session.delete(value)
        tags = self.session.query(Tag).filter(Tag.tag == tag).all()
        # TODO return error if len(tags) != 1
        self.session.delete(tags[0])
        self.unsavedModifications = True

    def removeValue(self, scan, tag):
        """
        Removes the value of the tuple <scan, tag> (corresponds to a cell in the databrowser)
        :param scan: FileName of the scan
        :param tag: Name of the tag
        """
        values = self.session.query(Value).filter(Value.scan == scan).filter(Value.tag == tag).all()
        self.session.delete(values[0])
        self.unsavedModifications = True

    def saveModifications(self):
        """
        Saves the pending operations of the project (actions still not saved)
        """
        self.session.commit()
        if not self.isTempProject:
            self.saveConfig()
        self.unsavedModifications = False

    def unsaveModifications(self):
        """
        Unsaves the pending operations of the project (actions still not saved)
        """
        self.session.rollback()
        self.unsavedModifications = False

    def getScansSimpleSearch(self, search):
        """
        Executes the rapid search (search bar) and returns the list of scans that contain the search in their tag values

        :param search: string corresponding to the search
        :return: The list of scans containing the search
        """

        # We take all the scans that contain the search in at least one of their tag values
        values = self.session.query(Value).filter(Value.current_value.like("%" + search + "%")).distinct().all()
        scans = [] # List of scans to return
        for value in values:
            # We add the scan only if the tag is visible in the databrowser
            if self.getTagVisibility(value.tag):
                scans.append(value.scan)
        return scans

    def getScansAdvancedSearch(self, links, fields, conditions, values, nots):
        """
        Executes the advanced search and returns the list of scans corresponding to the criterias

        :param links: list of links (AND/OR)
        :param fields: list of fields (tag name or all visualized tags)
        :param conditions: list of conditions (=, !=, <=, >=, <, >, IN, BETWEEN, CONTAINS)
        :param values: list of values (tag values)
        :param nots: list of nots (NOT?)
        :return: list of scans corresponding to those criterias
        """
        result = [] # list of scans to return
        queries = [] # list of scans of each query (row)
        i = 0
        while i < len(conditions):
            rowResult = self.session.query(Value.scan) # Every scan to start with
            if(fields[i] != "All visualized tags"):
                # Filter on the tag if necessary
                rowResult = rowResult.filter(Value.tag == fields[i])
            # Filter on the condition on the tag value (condition type + value)
            if(conditions[i] == "="):
                rowResult = rowResult.filter(Value.current_value == values[i])
            elif(conditions[i] == "!="):
                rowResult = rowResult.filter(Value.current_value != values[i])
            elif(conditions[i] == ">="):
                rowResult = rowResult.filter(Value.current_value >= values[i])
            elif (conditions[i] == "<="):
                rowResult = rowResult.filter(Value.current_value <= values[i])
            elif (conditions[i] == ">"):
                rowResult = rowResult.filter(Value.current_value > values[i])
            elif (conditions[i] == "<"):
                rowResult = rowResult.filter(Value.current_value < values[i])
            elif (conditions[i] == "CONTAINS"):
                rowResult = rowResult.filter(Value.current_value.contains(values[i]))
            elif (conditions[i] == "IN"):
                rowResult = rowResult.filter(Value.current_value.in_(values[i].split(', ')))
            elif (conditions[i] == "BETWEEN"):
                borders = values[i].split(', ')
                rowResult = rowResult.filter(Value.current_value.between(borders[0], borders[1]))
            if(nots[i] == "NOT"):
                # If NOT, we take the opposite: All scans MINUS the result of the query
                rowResult = self.session.query(Value.scan).except_(rowResult)
            # We add the list of scans to the subresults
            queries.append(rowResult)
            i = i + 1
        # We start with the first row to put the link between the conditions
        # Links are made row by row, there is no priority like in SQL where AND is stronger than OR
        finalQuery = queries[0]
        i = 0
        while i < len(links):
            if(links[i] == "AND"):
                # If the link is AND, we do an intersection between the current result and the next row
                finalQuery = finalQuery.intersect(queries[i + 1])
            else:
                # If the link is OR, we do an union between the current result and the next row
                finalQuery = finalQuery.union(queries[i + 1])
            i = i + 1
        # We take the list of all the scans that respect every conditions
        finalQuery = finalQuery.distinct().all()
        # We create the return list with the name of the scans (FileName)
        for value in finalQuery:
            result.append(value.scan)
        return result

    def check_count_table(self, values):
        """
        Checks if a scan contains all the couples <tag, value> given in parameter
        :param values: List of couple <tag, value> to check
        :return: True if a scan has all the couples <tag, value> given in parameter, False otherwise
        """
        queries = []
        for value in values:
            tag = value[0]
            value = value[1]
            cellResult = self.session.query(Value.scan)  # Every scan to start with
            cellResult = cellResult.filter(Value.tag == tag).filter(Value.current_value == value) # We apply the tag and value filter
            queries.append(cellResult)
        # We put all the cells together, with intersections
        # We only want a scan that has all the values
        finalResult = queries[0]
        i = 0
        while i < len(queries) - 1:
            finalResult = finalResult.intersect(queries[i + 1])
            i = i + 1
        finalResult = finalResult.all()
        # If there is a scan, we return True, and False otherwise
        return len(finalResult) == 1

    def undo(self):
        """
        Undo the last action made by the user on the project
        An history list is maintained, and cleared at every project opening
        An index is kept, showing where the user is in the history, visually
        Every new action made by the user is appended at the end of the history list
        At every undo, the index is decreased
        """

        # We can undo if we have an action to revert: history list not empty, and still some actions to read by the index
        if(self.historyHead > 0 and len(self.history) >= self.historyHead):
            toUndo = self.history[self.historyHead - 1] # Action to revert
            # The first element of the list is the type of action made by the user (add_tag, remove_tags, add_scans, remove_scans, or modified_values)
            action = toUndo[0]
            if(action == "add_tag"):
                # For removing the tag added, we just have to memorize the tag name, and remove it
                tagToRemove = toUndo[1]
                self.removeTag(tagToRemove)
            if (action == "remove_tags"):
                # To reput the removed tags, we need to reput the tag in the tag list, and all the tags values associated to this tag
                tagsRemoved = toUndo[1] # The second element is a list of the removed tags (Tag class)
                i = 0
                while i < len(tagsRemoved):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToReput = tagsRemoved[i]
                    self.addTag(tagToReput.tag, tagToReput.visible, tagToReput.origin, tagToReput.type, tagToReput.unit, tagToReput.default, tagToReput.description)
                    i = i + 1
                valuesRemoved = toUndo[2] # The third element is a list of tags values (Value class)
                i = 0
                while i < len(valuesRemoved):
                    # We reput each tag value in the values, keeping all the attributes
                    valueToReput = valuesRemoved[i]
                    self.addValue(valueToReput.scan, valueToReput.tag, valueToReput.current_value, valueToReput.raw_value)
                    i = i + 1
            if (action == "add_scans"):
                # To remove added scans, we just need their file name
                scansAdded = toUndo[1] # The second element is a list of added scans to remove
                i = 0
                while i < len(scansAdded):
                    # We remove each scan added
                    scanToRemove = scansAdded[i]
                    self.removeScan(scanToRemove)
                    i = i + 1
            if(action == "remove_scans"):
                # To reput a removed scan, we need the scans names, and all the values associated
                scansRemoved = toUndo[1] # The second element is the list of removed scans (Scan class)
                i = 0
                while i < len(scansRemoved):
                    # We reput each scan, keeping the same values
                    scanToReput = scansRemoved[i]
                    self.addScan(scanToReput.scan, scanToReput.checksum)
                    i = i + 1
                valuesRemoved = toUndo[2] # The third element is the list of removed values (Value class)
                i = 0
                while i < len(valuesRemoved):
                    # We reput each value, exactly the same as it was before
                    valueToReput = valuesRemoved[i]
                    self.addValue(valueToReput.scan, valueToReput.tag, valueToReput.current_value, valueToReput.raw_value)
                    i = i + 1
            if (action == "modified_values"):
                # To revert a value changed in the databrowser, we need two things: the cell (scan and tag, and the old value)
                modifiedValues = toUndo[1] # The second element is a list of modified values (reset, or value changed)
                i = 0
                while i < len(modifiedValues):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    valueToRestore = modifiedValues[i]
                    scan = valueToRestore[0]
                    tag = valueToRestore[1]
                    value = valueToRestore[2]
                    if(value == None):
                        # If the cell was NaN (not defined) before, we reput it
                        self.removeValue(scan, tag)
                    else:
                        # If the cell was there before, we just set it to the old value
                        self.setTagValue(scan, tag, value)
                    i = i + 1
            # Reading history index decreased
            self.historyHead = self.historyHead - 1

        #print(len(pickle.dumps(self.history, -1))) # Memory approximation in number of bits

        """
        Approximate results
        
        - Changing 1 cell value: 180 bits
        - Changing 10 cell values: 1350 bits
        - Removing 1 scan: 20000 bits
        - Removing 10 scans: 200000 bits
        - Removing 1 tag: From 300 bits to 4000 bits => Depends on the number of values defined
        - Adding 1 tag: 40 bits
        => By storing the minimum of data to be able to revert the actions, we take way less memory than by storing the whole database after each action
        """