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

    def undo(self, table):
        """
        Undo the last action made by the user on the project
        """

        from PyQt5 import QtCore
        from DataBrowser.DataBrowser import not_defined_value

        # We can undo if we have an action to revert
        if len(self.undos) > 0:
            toUndo = self.undos.pop()
            self.redos.append(toUndo)  # We pop the undo action in the redo stack
            # The first element of the list is the type of action made by the user (add_tag, remove_tags, add_scans, remove_scans, or modified_values)
            action = toUndo[0]
            if (action == "add_tag"):
                # For removing the tag added, we just have to memorize the tag name, and remove it
                tagToRemove = toUndo[1]
                self.removeTag(tagToRemove)
                column_to_remove = table.get_tag_column(tagToRemove)
                table.removeColumn(column_to_remove)
            if (action == "remove_tags"):
                # To reput the removed tags, we need to reput the tag in the tag list, and all the tags values associated to this tag
                tagsRemoved = toUndo[1]  # The second element is a list of the removed tags (Tag class)
                i = 0
                while i < len(tagsRemoved):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToReput = tagsRemoved[i]
                    self.addTag(tagToReput.tag, tagToReput.visible, tagToReput.origin, tagToReput.type, tagToReput.unit,
                                tagToReput.default, tagToReput.description)
                    i += 1
                valuesRemoved = toUndo[2]  # The third element is a list of tags values (Value class)
                self.reput_values(valuesRemoved)
                i = 0
                while i < len(tagsRemoved):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToReput = tagsRemoved[i]
                    column = table.get_index_insertion(tagToReput.tag)
                    table.add_column(column, tagToReput.tag)
                    i += 1
            if (action == "add_scans"):
                # To remove added scans, we just need their file name
                scansAdded = toUndo[1]  # The second element is a list of added scans to remove
                i = 0
                while i < len(scansAdded):
                    # We remove each scan added
                    scanToRemove = scansAdded[i][0]
                    self.removeScan(scanToRemove)
                    table.removeRow(table.get_scan_row(scanToRemove))
                    table.scans_to_visualize.remove(scanToRemove)
                    i += 1
            if (action == "remove_scans"):
                # To reput a removed scan, we need the scans names, and all the values associated
                scansRemoved = toUndo[1]  # The second element is the list of removed scans (Scan class)
                i = 0
                while i < len(scansRemoved):
                    # We reput each scan, keeping the same values
                    scanToReput = scansRemoved[i]
                    self.addScan(scanToReput.scan, scanToReput.checksum)
                    table.scans_to_visualize.append(scanToReput.scan)
                    i += 1
                valuesRemoved = toUndo[2]  # The third element is the list of removed values (Value class)
                self.reput_values(valuesRemoved)
                table.add_rows(self.getScansNames())
            if (action == "modified_values"):
                # To revert a value changed in the databrowser, we need two things: the cell (scan and tag, and the old value)
                modifiedValues = toUndo[1]  # The second element is a list of modified values (reset, or value changed)
                table.itemChanged.disconnect()
                i = 0
                while i < len(modifiedValues):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    valueToRestore = modifiedValues[i]
                    scan = valueToRestore[0]
                    tag = valueToRestore[1]
                    old_value = valueToRestore[2]
                    item = table.item(table.get_scan_row(scan), table.get_tag_column(tag))
                    if (old_value == None):
                        # If the cell was not defined before, we reput it
                        self.removeValue(scan, tag)
                        item.setData(QtCore.Qt.EditRole, QtCore.QVariant(not_defined_value))
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)
                    else:
                        # If the cell was there before, we just set it to the old value
                        self.database.set_value(scan, tag, str(old_value))
                        item.setData(QtCore.Qt.EditRole, QtCore.QVariant(str(old_value)))
                        table.update_color(scan, tag, item, table.get_scan_row(scan))
                    i += 1
                table.itemChanged.connect(table.change_cell_color)
            if (action == "modified_visibilities"):
                # To revert the modifications of the visualized tags
                old_tags = self.getVisualizedTags()  # Old list of columns
                visibles = toUndo[1]  # List of the tags visibles before the modification (Tag objects)
                self.resetAllVisibilities()  # Reset of the visibilities
                for visible in visibles:
                    # We reput each old tag visible
                    self.setTagVisibility(visible.tag, True)
                table.update_visualized_columns(old_tags)  # Columns updated

    def reput_values(self, values):
        """
        To reput the Value objects in the Database
        :param values: List of Value objects
        """
        i = 0
        while i < len(values):
            # We reput each value, exactly the same as it was before
            valueToReput = values[i]
            self.addValue(valueToReput.scan, valueToReput.tag, valueToReput.current_value, valueToReput.raw_value)
            i += 1

    def redo(self, table):
        """
        Redo the last action made by the user on the project
        """

        from PyQt5 import QtCore

        # We can redo if we have an action to make again
        if len(self.redos) > 0:
            toRedo = self.redos.pop()
            self.undos.append(toRedo)  # We pop the redo action in the undo stack
            # The first element of the list is the type of action made by the user (add_tag, remove_tags, add_scans, remove_scans, or modified_values)
            action = toRedo[0]
            if (action == "add_tag"):
                # For adding the tag, we need the tag name, and all its attributes
                tagToAdd = toRedo[1]
                tagType = toRedo[2]
                tagUnit = toRedo[3]
                tagDefaultValue = toRedo[4]
                tagDescription = toRedo[5]
                values = toRedo[6]  # List of values stored
                # Adding the tag
                self.addTag(tagToAdd, True, TAG_ORIGIN_USER, tagType, tagUnit, tagDefaultValue, tagDescription)
                # Adding all the values associated
                for value in values:
                    self.addValue(value[0], value[1], value[2], value[3])
                column = table.get_index_insertion(tagToAdd)
                table.add_column(column, tagToAdd)
            if (action == "remove_tags"):
                # To remove the tags, we need the names
                tagsRemoved = toRedo[1]  # The second element is a list of the removed tags (Tag class)
                i = 0
                while i < len(tagsRemoved):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToRemove = tagsRemoved[i].tag
                    self.removeTag(tagToRemove)
                    column_to_remove = table.get_tag_column(tagToRemove)
                    table.removeColumn(column_to_remove)
                    i += 1
            if (action == "add_scans"):
                # To add the scans, we need the FileNames and the values associated to the scans
                scansAdded = toRedo[1]  # The second element is a list of the scans to add
                # We add all the scans
                i = 0
                while i < len(scansAdded):
                    # We remove each scan added
                    scanToAdd = scansAdded[i]
                    self.addScan(scanToAdd[0], scanToAdd[1])
                    table.scans_to_visualize.append(scanToAdd[0])
                    i += 1
                # We add all the values
                i = 0
                valuesAdded = toRedo[2]  # The third element is a list of the values to add
                while i < len(valuesAdded):
                    valueToAdd = valuesAdded[i]
                    self.addValue(valueToAdd[0], valueToAdd[1], valueToAdd[2], valueToAdd[2])
                    i += 1
                table.add_rows(self.getScansNames())
            if (action == "remove_scans"):
                # To remove a scan, we only need the FileName of the scan
                scansRemoved = toRedo[1]  # The second element is the list of removed scans (Scan class)
                i = 0
                while i < len(scansRemoved):
                    # We reput each scan, keeping the same values
                    scanToRemove = scansRemoved[i].scan
                    self.removeScan(scanToRemove)
                    table.scans_to_visualize.remove(scanToRemove)
                    i += 1
            if (action == "modified_values"):  # Not working
                # To modily the values, we need the cells, and the updated values
                modifiedValues = toRedo[1]  # The second element is a list of modified values (reset, or value changed)
                table.itemChanged.disconnect()
                i = 0
                while i < len(modifiedValues):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    valueToRestore = modifiedValues[i]
                    scan = valueToRestore[0]
                    tag = valueToRestore[1]
                    # valueToRestore[2] is the old value of the cell
                    new_value = valueToRestore[3]
                    self.database.set_value(scan, tag, new_value)
                    item = table.item(table.get_scan_row(scan), table.get_tag_column(tag))
                    item.setData(QtCore.Qt.EditRole, QtCore.QVariant(str(new_value)))
                    table.update_color(scan, tag, item, table.get_scan_row(scan))
                    i += 1
                table.itemChanged.connect(table.change_cell_color)
            if (action == "modified_visibilities"):
                # To revert the modifications of the visualized tags
                old_tags = self.getVisualizedTags()  # Old list of columns
                visibles = toRedo[2]  # List of the tags visibles after the modification (Tag objects)
                self.resetAllVisibilities()  # Reset of the visibilities
                for visible in visibles:
                    # We reput each new tag visible
                    self.setTagVisibility(visible, True)
                table.update_visualized_columns(old_tags)  # Columns updated

