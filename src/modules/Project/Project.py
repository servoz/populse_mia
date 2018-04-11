from populse_db.Database import Database
import os
import tempfile
import yaml
from SoftwareProperties.Config import Config
from Project.Filter import Filter
from populse_db.DatabaseModel import TAG_TYPE_STRING, TAG_ORIGIN_USER, TAG_ORIGIN_RAW

class Project:

    def __init__(self, project_root_folder, new_project):

        if project_root_folder is None:
            self.isTempProject = True
            self.folder = os.path.relpath(tempfile.mkdtemp())
        else:
            self.isTempProject = False
            self.folder = project_root_folder
            self.properties = self.loadProperties()
        self.database = Database(os.path.join(self.folder, 'database', 'mia2.db'))
        if new_project:
            self.refreshTags()
        self.unsavedModifications = False
        self.undos = []
        self.redos = []
        self.initFilters()

    def initFilters(self):
        """
        Init of the filters at project opening
        """

        import json
        import glob

        self.currentFilter = Filter(None, [], [], [], [], [], "")
        self.filters = []

        filters_folder = os.path.join(self.folder, "filters")

        for filename in glob.glob(os.path.join(filters_folder, '*')):
            filter, extension = os.path.splitext(os.path.basename(filename))
            data = json.load(open(filename))
            filterObject = Filter(filter, data["nots"], data["values"], data["fields"], data["links"],
                                  data["conditions"], data["search_bar_text"])
            self.filters.append(filterObject)

    def loadProperties(self):
        """ Loads the properties file (Unnamed project does not have this file) """
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def getName(self):
        """ Returns the name of the project if it's not Unnamed project, otherwise empty string """
        if (self.isTempProject):
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
        if (self.isTempProject):
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

    def refreshTags(self):
        """
        Refreshes the tags
        """

        # Tags cleared
        for tag in self.database.get_tags_names():
            self.database.remove_tag(tag)

        # New tags added
        config = Config()
        if config.getDefaultTags() != None:
            for default_tag in config.getDefaultTags():
                if self.database.get_tag(default_tag) is None:
                    # Tags by default set as visible
                    self.database.add_tag(default_tag, True, TAG_ORIGIN_USER, TAG_TYPE_STRING, None, None, None)

        self.database.set_tag_origin("FileName", TAG_ORIGIN_RAW)

    def saveModifications(self):
        """
        Saves the pending operations of the project (actions still not saved)
        """

        self.database.save_modifications()
        if not self.isTempProject:
            self.saveConfig()
        self.unsavedModifications = False

    def hasUnsavedModifications(self):
        """
        Knowing if the project has unsaved modifications or not
        :return: True if the project has pending modifications, False otherwise
        """

        return self.unsavedModifications or self.database.has_unsaved_modifications()
