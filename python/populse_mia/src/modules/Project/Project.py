import os
import tempfile
from datetime import datetime

import yaml

from Project.Filter import Filter
from SoftwareProperties.Config import Config
from Utils.Utils import set_item_data

from Project.database_mia import Database_mia, TAG_ORIGIN_BUILTIN, TAG_ORIGIN_USER

# MIA collections
from populse_db.database import FIELD_TYPE_STRING, FIELD_TYPE_LIST_STRING, FIELD_TYPE_JSON, FIELD_TYPE_DATETIME

COLLECTION_CURRENT = "current"
COLLECTION_INITIAL = "initial"
COLLECTION_BRICK = "brick"

# MIA tags
TAG_CHECKSUM = "Checksum"
TAG_TYPE = "Type"
TAG_EXP_TYPE = "Exp Type"
TAG_FILENAME = "FileName"
TAG_BRICKS = "Bricks"
BRICK_ID = "ID"
BRICK_NAME = "Name"
BRICK_INPUTS = "Input(s)"
BRICK_OUTPUTS = "Output(s)"
BRICK_INIT = "Init"
BRICK_EXEC = "Exec"
BRICK_INIT_TIME = "Init Time"
BRICK_EXEC_TIME = "Exec Time"

TYPE_NII = "Scan"
TYPE_MAT = "Matrix"

class Project:

    def __init__(self, project_root_folder, new_project):

        if project_root_folder is None:
            self.isTempProject = True
            self.folder = os.path.relpath(tempfile.mkdtemp())
        else:
            self.isTempProject = False
            self.folder = project_root_folder

        # Checks that the project is not already opened
        config = Config()
        opened_projects = config.get_opened_projects()
        if self.folder not in opened_projects:
            opened_projects.append(self.folder)
            config.set_opened_projects(opened_projects)
        else:
            raise IOError(
                "The project at " + str(self.folder) + " is already opened in another instance of the software.")

        self.database = Database_mia('sqlite:///' + os.path.join(self.folder, 'database', 'mia.db'))
        self.session = self.database.__enter__()

        if new_project:

            if not os.path.exists(self.folder):
                os.makedirs(self.folder)

            if not os.path.exists(os.path.join(self.folder, "database")):
                os.makedirs(os.path.join(self.folder, "database"))

            if not os.path.exists(os.path.join(self.folder, "filters")):
                os.makedirs(os.path.join(self.folder, "filters"))

            if not os.path.exists(os.path.join(self.folder, "data")):
                os.makedirs(os.path.join(self.folder, "data"))

            if not os.path.exists(os.path.join(self.folder, "data", "raw_data")):
                os.makedirs(os.path.join(self.folder, "data", "raw_data"))

            if not os.path.exists(os.path.join(self.folder, "data", "derived_data")):
                os.makedirs(os.path.join(self.folder, "data", "derived_data"))

            if not os.path.exists(os.path.join(self.folder, "data", "downloaded_data")):
                os.makedirs(os.path.join(self.folder, "data", "downloaded_data"))

            # Properties file created
            os.mkdir(os.path.join(self.folder, 'properties'))
            if self.isTempProject:
                name = "Unnamed project"
            else:
                name = os.path.basename(self.folder)
            properties = dict(
                name=name,
                date=datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                sorted_tag=TAG_FILENAME,
                sort_order=0
            )
            with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'w', encoding='utf8') as propertyfile:
                yaml.dump(properties, propertyfile, default_flow_style=False, allow_unicode=True)

            # Adding current and initial collections
            self.session.add_collection(COLLECTION_CURRENT, TAG_FILENAME, True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_collection(COLLECTION_INITIAL, TAG_FILENAME, True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_collection(COLLECTION_BRICK, BRICK_ID, False, TAG_ORIGIN_BUILTIN, None, None)

            # Tags manually added
            self.session.add_field(COLLECTION_CURRENT, TAG_CHECKSUM, FIELD_TYPE_STRING, "Path checksum", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_CHECKSUM, FIELD_TYPE_STRING, "Path checksum", False, TAG_ORIGIN_BUILTIN, None, None) # TODO Maybe remove checksum tag from initial table
            self.session.add_field(COLLECTION_CURRENT, TAG_TYPE, FIELD_TYPE_STRING, "Path type", True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_TYPE, FIELD_TYPE_STRING, "Path type", True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_CURRENT, TAG_EXP_TYPE, FIELD_TYPE_STRING, "Path exp type", True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_EXP_TYPE, FIELD_TYPE_STRING, "Path exp type", True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_CURRENT, TAG_BRICKS, FIELD_TYPE_LIST_STRING, "Path bricks", True, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_BRICKS, FIELD_TYPE_LIST_STRING, "Path bricks", True, TAG_ORIGIN_BUILTIN, None, None)

            self.session.add_field(COLLECTION_BRICK, BRICK_NAME, FIELD_TYPE_STRING, "Brick name", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_INPUTS, FIELD_TYPE_JSON, "Brick input(s)", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_OUTPUTS, FIELD_TYPE_JSON, "Brick output(s)", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_INIT, FIELD_TYPE_STRING, "Brick init status", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_INIT_TIME, FIELD_TYPE_DATETIME, "Brick init time", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_EXEC, FIELD_TYPE_STRING, "Brick exec status", False, TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_EXEC_TIME, FIELD_TYPE_DATETIME, "Brick exec time", False, TAG_ORIGIN_BUILTIN, None, None)

            self.session.save_modifications() # Base modifications, do not count for unsaved modifications

        self.properties = self.loadProperties()

        self.unsavedModifications = False
        self.undos = []
        self.redos = []
        self.initFilters()

    """ FILTERS """

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

    def setCurrentFilter(self, filter):
        """
        To set the current filter of the project
        :param filter: new Filter object
        """

        self.currentFilter = filter

    def getFilter(self, filter):
        """
        To get a Filter object
        :param filter: Filter name
        :return: Filter object
        """
        for filterObject in self.filters:
            if filterObject.name == filter:
                return filterObject

    def save_current_filter(self, advancedFilters):
        """
        To save the current filter
        :return:
        """

        from PyQt5.QtWidgets import QMessageBox
        import json

        (fields, conditions, values, links, nots) = advancedFilters
        self.currentFilter.fields = fields
        self.currentFilter.conditions = conditions
        self.currentFilter.values = values
        self.currentFilter.links = links
        self.currentFilter.nots = nots

        # Getting the path
        filters_path = os.path.join(self.folder, "filters")

        # Filters folder created if it does not already exists
        if not os.path.exists(filters_path):
            os.mkdir(filters_path)

        filter_name = self.getFilterName()

        # We save the filter only if we have a filter name from the popup
        if filter_name != None:
            file_path = os.path.join(filters_path, filter_name + ".json")

            if os.path.exists(file_path):
                # Filter already exists
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("The filter already exists in the project")
                msg.setInformativeText("The project already has a filter named " + filter_name)
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()

            else:
                # Json filter file written
                with open(file_path, 'w') as outfile:
                    new_filter = Filter(filter_name, self.currentFilter.nots, self.currentFilter.values,
                                        self.currentFilter.fields, self.currentFilter.links,
                                        self.currentFilter.conditions, self.currentFilter.search_bar)
                    json.dump(new_filter.json_format(), outfile)
                    self.filters.append(new_filter)

    def getFilterName(self):
        """
        Input box to get the name of the filter to save
        """

        from PyQt5.QtWidgets import QInputDialog, QLineEdit

        text, okPressed = QInputDialog.getText(None, "Save a filter", "Filter name: ", QLineEdit.Normal, "")
        if okPressed and text != '':
            return text

    """ PROPERTIES """

    def loadProperties(self):
        """ Loads the properties file """
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def getName(self):
        """ Returns the name of the project if it's not Unnamed project, otherwise empty string """

        return self.properties["name"]

    def setName(self, name):
        """ Sets the name of the project if it's not Unnamed project, otherwise does nothing
            :param name: new name of the project
        """

        self.properties["name"] = name

    def saveConfig(self):
        """ Save the changes in the properties file """

        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.properties, configfile, default_flow_style=False, allow_unicode=True)

    def getDate(self):
        """ Returns the date of creation of the project if it's not Unnamed project, otherwise empty string """

        return self.properties["date"]

    def setDate(self, date):
        """ Sets the date of the project
            :param date: new date of the project
        """

        self.properties["date"] = date

    def getSortedTag(self):
        """ Returns the sorted tag of the project if it's not Unnamed project, otherwise empty string """

        return self.properties["sorted_tag"]

    def setSortedTag(self, tag):
        """ Sets the sorted tag of the project
            :param tag: new sorted tag of the project
        """

        old_tag = self.properties["sorted_tag"]
        self.properties["sorted_tag"] = tag
        if old_tag != tag:
            self.unsavedModifications = True

    def getSortOrder(self):
        """ Returns the sort order of the project if it's not Unnamed project, otherwise empty string """

        return self.properties["sort_order"]

    def setSortOrder(self, order):
        """ Sets the sort order of the project if it's not Unnamed project, otherwise does nothing
            :param order: new sort order of the project (ascending or descending)
        """

        old_order = self.properties["sort_order"]
        self.properties["sort_order"] = order
        if old_order != order:
            self.unsavedModifications = True

    """ UTILS """

    """ MODIFICATIONS """

    def saveModifications(self):
        """
        Saves the pending operations of the project (actions still not saved)
        """

        self.session.save_modifications()
        self.saveConfig()
        self.unsavedModifications = False

    def unsaveModifications(self):
        self.session.unsave_modifications()
        self.unsavedModifications = False

    def hasUnsavedModifications(self):
        """
        Knowing if the project has unsaved modifications or not
        :return: True if the project has pending modifications, False otherwise
        """

        return self.unsavedModifications or self.session.has_unsaved_modifications()

    """ UNDO/REDO """

    def undo(self, table):
        """
        Undo the last action made by the user on the project
        """

        from DataBrowser.DataBrowser import not_defined_value

        # We can undo if we have an action to revert
        if len(self.undos) > 0:
            toUndo = self.undos.pop()
            self.redos.append(toUndo)  # We pop the undo action in the redo stack
            # The first element of the list is the type of action made by the user (add_tag,
            # remove_tags, add_scans, remove_scans, or modified_values)
            action = toUndo[0]
            if (action == "add_tag"):
                # For removing the tag added, we just have to memorize the tag name, and remove it
                tagToRemove = toUndo[1]
                self.session.remove_field(COLLECTION_CURRENT, tagToRemove)
                self.session.remove_field(COLLECTION_INITIAL, tagToRemove)
                column_to_remove = table.get_tag_column(tagToRemove)
                table.removeColumn(column_to_remove)
            if (action == "remove_tags"):
                # To reput the removed tags, we need to reput the tag in the tag list, and all the tags values associated to this tag
                tagsRemoved = toUndo[1]  # The second element is a list of the removed tags ([Tag row, origin, unit, default_value])
                for i in range(0, len(tagsRemoved)):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToReput = tagsRemoved[i][0]
                    self.session.add_field(COLLECTION_CURRENT, tagToReput.field_name, tagToReput.type, tagToReput.description, tagToReput.visibility, tagToReput.origin, tagToReput.unit, tagToReput.default_value)
                    self.session.add_field(COLLECTION_INITIAL, tagToReput.field_name, tagToReput.type,tagToReput.description, tagToReput.visibility, tagToReput.origin, tagToReput.unit, tagToReput.default_value)
                valuesRemoved = toUndo[2]  # The third element is a list of tags values (Value class)
                self.reput_values(valuesRemoved)
                for i in range(0, len(tagsRemoved)):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToReput = tagsRemoved[i][0]
                    column = table.get_index_insertion(tagToReput.field_name)
                    table.add_column(column, tagToReput.field_name)
            if (action == "add_scans"):
                # To remove added scans, we just need their file name
                scansAdded = toUndo[1]  # The second element is a list of added scans to remove
                for i in range(0, len(scansAdded)):
                    # We remove each scan added
                    scanToRemove = scansAdded[i]
                    self.session.remove_document(COLLECTION_CURRENT, scanToRemove)
                    self.session.remove_document(COLLECTION_INITIAL, scanToRemove)
                    table.removeRow(table.get_scan_row(scanToRemove))
                    table.scans_to_visualize.remove(scanToRemove)
                table.itemChanged.disconnect()
                table.update_colors()
                table.itemChanged.connect(table.change_cell_color)
            if (action == "remove_scans"):
                # To reput a removed scan, we need the scans names, and all the values associated
                scansRemoved = toUndo[1]  # The second element is the list of removed scans (Scan class)
                for i in range(0, len(scansRemoved)):
                    # We reput each scan, keeping the same values
                    scanToReput = scansRemoved[i]
                    self.session.add_document(COLLECTION_CURRENT, getattr(scanToReput, TAG_FILENAME))
                    self.session.add_document(COLLECTION_INITIAL, getattr(scanToReput, TAG_FILENAME))
                    table.scans_to_visualize.append(getattr(scanToReput, TAG_FILENAME))
                valuesRemoved = toUndo[2]  # The third element is the list of removed values
                self.reput_values(valuesRemoved)
                table.add_rows(self.session.get_documents_names(COLLECTION_CURRENT))
            if (action == "modified_values"):
                # To revert a value changed in the databrowser, we need two things: the cell (scan and tag, and the old value)
                modifiedValues = toUndo[1]  # The second element is a list of modified values (reset, or value changed)
                table.itemChanged.disconnect()
                for i in range(0, len(modifiedValues)):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    valueToRestore = modifiedValues[i]
                    scan = valueToRestore[0]
                    tag = valueToRestore[1]
                    old_value = valueToRestore[2]
                    new_value = valueToRestore[3]
                    item = table.item(table.get_scan_row(scan), table.get_tag_column(tag))
                    if (old_value == None):
                        # If the cell was not defined before, we reput it
                        self.session.remove_value(COLLECTION_CURRENT, scan, tag)
                        self.session.remove_value(COLLECTION_INITIAL, scan, tag)
                        set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)
                    else:
                        # If the cell was there before, we just set it to the old value
                        self.session.set_value(COLLECTION_CURRENT, scan, tag, old_value)
                        set_item_data(item, old_value, self.session.get_field(COLLECTION_CURRENT, tag).type)
                        # If the new value is None, the not defined font must be removed
                        if new_value is None:
                            font = item.font()
                            font.setItalic(False)
                            font.setBold(False)
                            item.setFont(font)
                table.update_colors()
                table.itemChanged.connect(table.change_cell_color)
            if (action == "modified_visibilities"):
                # To revert the modifications of the visualized tags
                old_tags = self.session.get_visibles()  # Old list of columns
                visibles = toUndo[1]  # List of the tags visibles before the modification (Tag objects)
                self.session.set_visibles(visibles)
                table.update_visualized_columns(old_tags, self.session.get_visibles())  # Columns updated

    def reput_values(self, values):
        """
        To reput the Value objects in the Database
        :param values: List of Value objects
        """

        for i in range(0, len(values)):
            # We reput each value, exactly the same as it was before
            valueToReput = values[i]
            self.session.add_value(COLLECTION_CURRENT, valueToReput[0], valueToReput[1], valueToReput[2])
            self.session.add_value(COLLECTION_INITIAL, valueToReput[0], valueToReput[1], valueToReput[3])

    def redo(self, table):
        """
        Redo the last action made by the user on the project
        """

        from DataBrowser.DataBrowser import not_defined_value

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
                self.session.add_field(COLLECTION_CURRENT, tagToAdd, tagType, tagDescription, True, TAG_ORIGIN_USER, tagUnit, tagDefaultValue)
                self.session.add_field(COLLECTION_INITIAL, tagToAdd, tagType, tagDescription, True, TAG_ORIGIN_USER, tagUnit, tagDefaultValue)
                # Adding all the values associated
                for value in values:
                    self.session.add_value(COLLECTION_CURRENT, value[0], value[1], value[2])
                    self.session.add_value(COLLECTION_INITIAL, value[0], value[1], value[3])
                column = table.get_index_insertion(tagToAdd)
                table.add_column(column, tagToAdd)
            if (action == "remove_tags"):
                # To remove the tags, we need the names
                tagsRemoved = toRedo[1]  # The second element is a list of the removed tags (Tag class)
                for i in range(0, len(tagsRemoved)):
                    # We reput each tag in the tag list, keeping all the tags params
                    tagToRemove = tagsRemoved[i][0].field_name
                    self.session.remove_field(COLLECTION_CURRENT, tagToRemove)
                    self.session.remove_field(COLLECTION_INITIAL, tagToRemove)
                    column_to_remove = table.get_tag_column(tagToRemove)
                    table.removeColumn(column_to_remove)
            if (action == "add_scans"):
                # To add the scans, we need the FileNames and the values associated to the scans
                scansAdded = toRedo[1]  # The second element is a list of the scans to add
                # We add all the scans
                for i in range(0, len(scansAdded)):
                    # We remove each scan added
                    scanToAdd = scansAdded[i]
                    self.session.add_document(COLLECTION_CURRENT, scanToAdd)
                    self.session.add_document(COLLECTION_INITIAL, scanToAdd)
                    table.scans_to_visualize.append(scanToAdd)
                # We add all the values
                valuesAdded = toRedo[2]  # The third element is a list of the values to add
                for i in range(0, len(valuesAdded)):
                    valueToAdd = valuesAdded[i]
                    self.session.add_value(COLLECTION_CURRENT, valueToAdd[0], valueToAdd[1], valueToAdd[2])
                    self.session.add_value(COLLECTION_INITIAL, valueToAdd[0], valueToAdd[1], valueToAdd[3])
                table.add_rows(self.session.get_documents_names(COLLECTION_CURRENT))
            if (action == "remove_scans"):
                # To remove a scan, we only need the FileName of the scan
                scansRemoved = toRedo[1]  # The second element is the list of removed scans (Path class)
                for i in range(0, len(scansRemoved)):
                    # We reput each scan, keeping the same values
                    scanToRemove = getattr(scansRemoved[i], TAG_FILENAME)
                    self.session.remove_document(COLLECTION_CURRENT, scanToRemove)
                    self.session.remove_document(COLLECTION_INITIAL, scanToRemove)
                    table.scans_to_visualize.remove(scanToRemove)
                    table.removeRow(table.get_scan_row(scanToRemove))
                    table.itemChanged.disconnect()
                    table.update_colors()
                    table.itemChanged.connect(table.change_cell_color)
            if (action == "modified_values"):  # Not working
                # To modify the values, we need the cells, and the updated values
                modifiedValues = toRedo[1]  # The second element is a list of modified values (reset, or value changed)
                table.itemChanged.disconnect()
                for i in range(0, len(modifiedValues)):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    valueToRestore = modifiedValues[i]
                    scan = valueToRestore[0]
                    tag = valueToRestore[1]
                    old_value = valueToRestore[2]
                    new_value = valueToRestore[3]

                    item = table.item(table.get_scan_row(scan), table.get_tag_column(tag))
                    if old_value == None:
                        # Font reput to normal in case it was a not defined cell
                        font = item.font()
                        font.setItalic(False)
                        font.setBold(False)
                        item.setFont(font)
                    self.session.set_value(COLLECTION_CURRENT, scan, tag, new_value)
                    if new_value is None:
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)
                        set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
                    else:
                        set_item_data(item, new_value, self.session.get_field(COLLECTION_CURRENT, tag).type)
                table.update_colors()
                table.itemChanged.connect(table.change_cell_color)
            if (action == "modified_visibilities"):
                # To revert the modifications of the visualized tags
                old_tags = self.session.get_visibles()  # Old list of columns
                visibles = toRedo[2]  # List of the tags visibles before the modification (Tag objects)
                self.session.set_visibles(visibles)
                table.update_visualized_columns(old_tags, self.session.get_visibles())  # Columns updated