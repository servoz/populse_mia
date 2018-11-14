##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import tempfile
from datetime import datetime
import yaml
import json
import glob

# PyQt5 imports
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit

# Populse_MIA imports
from populse_mia.project.filter import Filter
from populse_mia.software_properties.config import Config
from populse_mia.utils.utils import set_item_data
from populse_mia.project.database_mia import DatabaseMIA, TAG_ORIGIN_BUILTIN, TAG_ORIGIN_USER

# Populse_db imports
from populse_db.database import FIELD_TYPE_STRING, FIELD_TYPE_LIST_STRING, FIELD_TYPE_JSON, FIELD_TYPE_DATETIME, \
    FIELD_TYPE_INTEGER

COLLECTION_CURRENT = "current"
COLLECTION_INITIAL = "initial"
COLLECTION_BRICK = "brick"

# MIA tags
TAG_CHECKSUM = "Checksum"
TAG_TYPE = "Type"
TAG_EXP_TYPE = "Exp Type"
TAG_FILENAME = "FileName"
TAG_BRICKS = "Bricks"
CLINICAL_TAGS = ["Site", "Spectro", "MR", "PatientRef", "Pathology", "Age", "Sex", "Message"]
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
    """
    Class that handles projects and their associated database

    Attributes:
        - folder: project's path
        - database: populse_db's database object
        - session: database session
        - properties: project's properties
        - undos: list of actions to undo
        - redos: list of actions to redo

    Methods:
        - add_clinical_tags: adds the clinical tags to the project
        - init_filters: initializes the filters at project opening
        - setCurrentFilter: sets the current filter of the project
        - getFilter: returns a Filter object
        - save_current_filter: saves the current filter
        - getFilterName: input box to get the name of the filter to save
        - loadProperties: loads the properties file
        - getName: returns the name of the project
        - setName: sets the name of the project
        - saveConfig: saves the changes in the properties file
        - getDate: returns the date of creation of the project
        - setDate: sets the date of the project
        - getSortedTag: returns the sorted tag of the project
        - setSortedTag: sets the sorted tag of the project
        - getSortOrder: returns the sort order of the project
        - setSortOrder: sets the sort order of the project
        - saveModifications: saves the pending operations of the project (actions still not saved)
        - unsaveModifications: unsaves the pending operations of the project
        - hasUnsavedModifications: returns if the project has unsaved modifications or not
        - undo: undoes the last action made by the user on the project
        - redo: redoes the last action made by the user on the project
        - reput_values: reputs the value objects in the database
    """

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

        self.database = DatabaseMIA('sqlite:///' + os.path.join(self.folder, 'database', 'mia.db'))
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
            self.session.add_field(COLLECTION_CURRENT, TAG_CHECKSUM, FIELD_TYPE_STRING, "Path checksum", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_CHECKSUM, FIELD_TYPE_STRING, "Path checksum", False,
                                   TAG_ORIGIN_BUILTIN, None, None)  # TODO Maybe remove checksum tag from populse_mia.itial table
            self.session.add_field(COLLECTION_CURRENT, TAG_TYPE, FIELD_TYPE_STRING, "Path type", True,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_TYPE, FIELD_TYPE_STRING, "Path type", True,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_CURRENT, TAG_EXP_TYPE, FIELD_TYPE_STRING, "Path exp type", True,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_EXP_TYPE, FIELD_TYPE_STRING, "Path exp type", True,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_CURRENT, TAG_BRICKS, FIELD_TYPE_LIST_STRING, "Path bricks", True,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_INITIAL, TAG_BRICKS, FIELD_TYPE_LIST_STRING, "Path bricks", True,
                                   TAG_ORIGIN_BUILTIN, None, None)

            self.session.add_field(COLLECTION_BRICK, BRICK_NAME, FIELD_TYPE_STRING, "Brick name", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_INPUTS, FIELD_TYPE_JSON, "Brick input(s)", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_OUTPUTS, FIELD_TYPE_JSON, "Brick output(s)", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_INIT, FIELD_TYPE_STRING, "Brick init status", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_INIT_TIME, FIELD_TYPE_DATETIME, "Brick init time", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_EXEC, FIELD_TYPE_STRING, "Brick exec status", False,
                                   TAG_ORIGIN_BUILTIN, None, None)
            self.session.add_field(COLLECTION_BRICK, BRICK_EXEC_TIME, FIELD_TYPE_DATETIME, "Brick exec time", False,
                                   TAG_ORIGIN_BUILTIN, None, None)

            # Adding default tags for the clinical mode
            if config.get_clinical_mode() == 'yes':
                for clinical_tag in CLINICAL_TAGS:
                    if clinical_tag == "Age":
                        field_type = FIELD_TYPE_INTEGER
                    else:
                        field_type = FIELD_TYPE_STRING
                    self.session.add_field(COLLECTION_CURRENT, clinical_tag, field_type, clinical_tag, True,
                                           TAG_ORIGIN_BUILTIN, None, None)
                    self.session.add_field(COLLECTION_INITIAL, clinical_tag, field_type, clinical_tag, True,
                                           TAG_ORIGIN_BUILTIN, None, None)

            self.session.save_modifications() # Base modifications, do not count for unsaved modifications

        self.properties = self.loadProperties()

        self.unsavedModifications = False
        self.undos = []
        self.redos = []
        self.init_filters()

    def add_clinical_tags(self):
        """
        Adds the clinical tags to the project

        :return: the clinical tags that were not already in the project
        """
        return_tags = []
        for clinical_tag in CLINICAL_TAGS:
            if clinical_tag not in self.session.get_fields_names(COLLECTION_CURRENT):
                if clinical_tag == "Age":
                    field_type = FIELD_TYPE_INTEGER
                else:
                    field_type = FIELD_TYPE_STRING
                self.session.add_field(COLLECTION_CURRENT, clinical_tag, field_type, clinical_tag, True,
                                       TAG_ORIGIN_BUILTIN, None, None)
                self.session.add_field(COLLECTION_INITIAL, clinical_tag, field_type, clinical_tag, True,
                                       TAG_ORIGIN_BUILTIN, None, None)
                for scan in self.session.get_documents(COLLECTION_CURRENT):
                    self.session.add_value(COLLECTION_CURRENT, getattr(scan, TAG_FILENAME), clinical_tag,
                                           None)
                    self.session.add_value(COLLECTION_INITIAL, getattr(scan, TAG_FILENAME), clinical_tag,
                                           None)
                return_tags.append(clinical_tag)

        return return_tags

    """ FILTERS """

    def init_filters(self):
        """
        Initializes the filters at project opening
        """

        self.currentFilter = Filter(None, [], [], [], [], [], "")
        self.filters = []

        filters_folder = os.path.join(self.folder, "filters")

        for filename in glob.glob(os.path.join(filters_folder, '*')):
            filter, extension = os.path.splitext(os.path.basename(filename))
            with open(filename, 'r') as f:   # make sure this gets closed automatically as soon as we are done reading
                data = json.load(f)
            filter_object = Filter(filter, data["nots"], data["values"], data["fields"], data["links"],
                                  data["conditions"], data["search_bar_text"])
            self.filters.append(filter_object)

    def setCurrentFilter(self, filter):
        """
        Sets the current filter of the project

        :param filter: new Filter object
        """

        self.currentFilter = filter

    def getFilter(self, filter):
        """
        Returns a Filter object

        :param filter: Filter name
        :return: Filter object
        """
        for filterObject in self.filters:
            if filterObject.name == filter:
                return filterObject

    def save_current_filter(self, advanced_filters):
        """
        Saves the current filter
        """

        (fields, conditions, values, links, nots) = advanced_filters
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

        # We save the filter only if we have a filter name from populse_mia.e popup
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

        text, ok_pressed = QInputDialog.getText(None, "Save a filter", "Filter name: ", QLineEdit.Normal, "")
        if ok_pressed and text != '':
            return text

    """ PROPERTIES """

    def loadProperties(self):
        """
        Loads the properties file
        """
        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def getName(self):
        """
        Returns the name of the project

        :return: the name of the project if it's not Unnamed project, otherwise empty string
        """

        return self.properties["name"]

    def setName(self, name):
        """
        Sets the name of the project if it's not Unnamed project, otherwise does nothing

        :param name: new name of the project
        """

        self.properties["name"] = name

    def saveConfig(self):
        """
        Saves the changes in the properties file
        """

        with open(os.path.join(self.folder, 'properties', 'properties.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.properties, configfile, default_flow_style=False, allow_unicode=True)

    def getDate(self):
        """
        Returns the date of creation of the project

        :return: the date of creation of the project if it's not Unnamed project, otherwise empty string
        """

        return self.properties["date"]

    def setDate(self, date):
        """
        Sets the date of the project

        :param date: new date of the project
        """

        self.properties["date"] = date

    def getSortedTag(self):
        """
        Returns the sorted tag of the project

        :return: the sorted tag of the project if it's not Unnamed project, otherwise empty string
        """

        return self.properties["sorted_tag"]

    def setSortedTag(self, tag):
        """
        Sets the sorted tag of the project

        :param tag: new sorted tag of the project
        """

        old_tag = self.properties["sorted_tag"]
        self.properties["sorted_tag"] = tag
        if old_tag != tag:
            self.unsavedModifications = True

    def getSortOrder(self):
        """
        Returns the sort order of the project

        :return: the sort order of the project if it's not Unnamed project, otherwise empty string
        """

        return self.properties["sort_order"]

    def setSortOrder(self, order):
        """
        Sets the sort order of the project

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
        """
        Unsaves the pending operations of the project
        """
        self.session.unsave_modifications()
        self.unsavedModifications = False

    def hasUnsavedModifications(self):
        """
        Returns if the project has unsaved modifications or not

        :return: True if the project has pending modifications, False otherwise
        """

        return self.unsavedModifications or self.session.has_unsaved_modifications()

    """ UNDO/REDO """

    def undo(self, table):
        """
        Undoes the last action made by the user on the project

        :param table: table on which to apply the modifications
        """

        # To avoid circular imports
        from populse_mia.data_browser.data_browser import not_defined_value
        
        # We can undo if we have an action to revert
        if len(self.undos) > 0:
            to_undo = self.undos.pop()
            self.redos.append(to_undo)  # We pop the undo action in the redo stack
            # The first element of the list is the type of action made by the user (add_tag,
            # remove_tags, add_scans, remove_scans, or modified_values)
            action = to_undo[0]
            if action == "add_tag":
                # For removing the tag added, we just have to memorize the tag name, and remove it
                tag_to_remove = to_undo[1]
                self.session.remove_field(COLLECTION_CURRENT, tag_to_remove)
                self.session.remove_field(COLLECTION_INITIAL, tag_to_remove)
                column_to_remove = table.get_tag_column(tag_to_remove)
                table.removeColumn(column_to_remove)
            if action == "remove_tags":
                # To reput the removed tags, we need to reput the tag in the tag list,
                # and all the tags values associated to this tag
                tags_removed = to_undo[1]  # The second element is a list of the removed tags ([Tag row, origin,
                # unit, default_value])
                for i in range(0, len(tags_removed)):
                    # We reput each tag in the tag list, keeping all the tags params
                    tag_to_reput = tags_removed[i][0]
                    self.session.add_field(COLLECTION_CURRENT, tag_to_reput.field_name, tag_to_reput.type,
                                           tag_to_reput.description, tag_to_reput.visibility, tag_to_reput.origin,
                                           tag_to_reput.unit, tag_to_reput.default_value)
                    self.session.add_field(COLLECTION_INITIAL, tag_to_reput.field_name, tag_to_reput.type,
                                           tag_to_reput.description, tag_to_reput.visibility, tag_to_reput.origin,
                                           tag_to_reput.unit, tag_to_reput.default_value)
                values_removed = to_undo[2]  # The third element is a list of tags values (Value class)
                self.reput_values(values_removed)
                for i in range(0, len(tags_removed)):
                    # We reput each tag in the tag list, keeping all the tags params
                    tag_to_reput = tags_removed[i][0]
                    column = table.get_index_insertion(tag_to_reput.field_name)
                    table.add_column(column, tag_to_reput.field_name)
            if action == "add_scans":
                # To remove added scans, we just need their file name
                scans_added = to_undo[1]  # The second element is a list of added scans to remove
                for i in range(0, len(scans_added)):
                    # We remove each scan added
                    scan_to_remove = scans_added[i]
                    self.session.remove_document(COLLECTION_CURRENT, scan_to_remove)
                    self.session.remove_document(COLLECTION_INITIAL, scan_to_remove)
                    table.removeRow(table.get_scan_row(scan_to_remove))
                    table.scans_to_visualize.remove(scan_to_remove)
                table.itemChanged.disconnect()
                table.update_colors()
                table.itemChanged.connect(table.change_cell_color)
            if action == "remove_scans":
                # To reput a removed scan, we need the scans names, and all the values associated
                scans_removed = to_undo[1]  # The second element is the list of removed scans (Scan class)
                for i in range(0, len(scans_removed)):
                    # We reput each scan, keeping the same values
                    scan_to_reput = scans_removed[i]
                    self.session.add_document(COLLECTION_CURRENT, getattr(scan_to_reput, TAG_FILENAME))
                    self.session.add_document(COLLECTION_INITIAL, getattr(scan_to_reput, TAG_FILENAME))
                    table.scans_to_visualize.append(getattr(scan_to_reput, TAG_FILENAME))
                values_removed = to_undo[2]  # The third element is the list of removed values
                self.reput_values(values_removed)
                table.add_rows(self.session.get_documents_names(COLLECTION_CURRENT))
            if action == "modified_values":
                # To revert a value changed in the databrowser, we need two things: the cell
                # (scan and tag, and the old value)
                modified_values = to_undo[1]  # The second element is a list of modified values (reset,
                # or value changed)
                table.itemChanged.disconnect()
                for i in range(0, len(modified_values)):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    value_to_restore = modified_values[i]
                    scan = value_to_restore[0]
                    tag = value_to_restore[1]
                    old_value = value_to_restore[2]
                    new_value = value_to_restore[3]
                    item = table.item(table.get_scan_row(scan), table.get_tag_column(tag))
                    if old_value is None:
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
            if action == "modified_visibilities":
                # To revert the modifications of the visualized tags
                old_tags = self.session.get_visibles()  # Old list of columns
                visibles = to_undo[1]  # List of the tags visibles before the modification (Tag objects)
                self.session.set_visibles(visibles)
                table.update_visualized_columns(old_tags, self.session.get_visibles())  # Columns updated

    def redo(self, table):
        """
        Redoes the last action made by the user on the project

        :param table: table on which to apply the modifications
        """

        # To avoid circular imports
        from populse_mia.data_browser.data_browser import not_defined_value

        # We can redo if we have an action to make again
        if len(self.redos) > 0:
            to_redo = self.redos.pop()
            self.undos.append(to_redo)  # We pop the redo action in the undo stack
            # The first element of the list is the type of action made by the user
            # (add_tag, remove_tags, add_scans, remove_scans, or modified_values)
            action = to_redo[0]

            if action == "add_tag":
                # For adding the tag, we need the tag name, and all its attributes
                tag_to_add = to_redo[1]
                tag_type = to_redo[2]
                tag_unit = to_redo[3]
                tag_default_value = to_redo[4]
                tag_description = to_redo[5]
                values = to_redo[6]  # List of values stored
                # Adding the tag
                self.session.add_field(COLLECTION_CURRENT, tag_to_add, tag_type, tag_description, True,
                                       TAG_ORIGIN_USER, tag_unit, tag_default_value)
                self.session.add_field(COLLECTION_INITIAL, tag_to_add, tag_type, tag_description, True,
                                       TAG_ORIGIN_USER, tag_unit, tag_default_value)
                # Adding all the values associated
                for value in values:
                    self.session.add_value(COLLECTION_CURRENT, value[0], value[1], value[2])
                    self.session.add_value(COLLECTION_INITIAL, value[0], value[1], value[3])
                column = table.get_index_insertion(tag_to_add)
                table.add_column(column, tag_to_add)

            if action == "remove_tags":
                # To remove the tags, we need the names
                tags_removed = to_redo[1]  # The second element is a list of the removed tags (Tag class)
                for i in range(0, len(tags_removed)):
                    # We reput each tag in the tag list, keeping all the tags params
                    tag_to_remove = tags_removed[i][0].field_name
                    self.session.remove_field(COLLECTION_CURRENT, tag_to_remove)
                    self.session.remove_field(COLLECTION_INITIAL, tag_to_remove)
                    column_to_remove = table.get_tag_column(tag_to_remove)
                    table.removeColumn(column_to_remove)

            if action == "add_scans":
                # To add the scans, we need the FileNames and the values associated to the scans
                scans_added = to_redo[1]  # The second element is a list of the scans to add
                # We add all the scans
                for i in range(0, len(scans_added)):
                    # We remove each scan added
                    scan_to_add = scans_added[i]
                    self.session.add_document(COLLECTION_CURRENT, scan_to_add)
                    self.session.add_document(COLLECTION_INITIAL, scan_to_add)
                    table.scans_to_visualize.append(scan_to_add)
                # We add all the values
                values_added = to_redo[2]  # The third element is a list of the values to add
                for i in range(0, len(values_added)):
                    value_to_add = values_added[i]
                    self.session.add_value(COLLECTION_CURRENT, value_to_add[0], value_to_add[1], value_to_add[2])
                    self.session.add_value(COLLECTION_INITIAL, value_to_add[0], value_to_add[1], value_to_add[3])
                table.add_rows(self.session.get_documents_names(COLLECTION_CURRENT))

            if action == "remove_scans":
                # To remove a scan, we only need the FileName of the scan
                scans_removed = to_redo[1]  # The second element is the list of removed scans (Path class)
                for i in range(0, len(scans_removed)):
                    # We reput each scan, keeping the same values
                    scan_to_remove = getattr(scans_removed[i], TAG_FILENAME)
                    self.session.remove_document(COLLECTION_CURRENT, scan_to_remove)
                    self.session.remove_document(COLLECTION_INITIAL, scan_to_remove)
                    table.scans_to_visualize.remove(scan_to_remove)
                    table.removeRow(table.get_scan_row(scan_to_remove))
                    table.itemChanged.disconnect()
                    table.update_colors()
                    table.itemChanged.connect(table.change_cell_color)

            if action == "modified_values":  # Not working
                # To modify the values, we need the cells, and the updated values
                modified_values = to_redo[1]  # The second element is a list of modified values (reset or value changed)
                table.itemChanged.disconnect()
                for i in range(0, len(modified_values)):
                    # Each modified value is a list of 3 elements: scan, tag, and old_value
                    value_to_restore = modified_values[i]
                    scan = value_to_restore[0]
                    tag = value_to_restore[1]
                    old_value = value_to_restore[2]
                    new_value = value_to_restore[3]

                    item = table.item(table.get_scan_row(scan), table.get_tag_column(tag))
                    if old_value is None:
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

            if action == "modified_visibilities":
                # To revert the modifications of the visualized tags
                old_tags = self.session.get_visibles()  # Old list of columns
                visibles = to_redo[2]  # List of the tags visibles before the modification (Tag objects)
                self.session.set_visibles(visibles)
                table.update_visualized_columns(old_tags, self.session.get_visibles())  # Columns updated

    def reput_values(self, values):
        """
        Reputs the value objects in the database

        :param values: List of Value objects
        """

        for i in range(0, len(values)):
            # We reput each value, exactly the same as it was before
            valueToReput = values[i]
            self.session.add_value(COLLECTION_CURRENT, valueToReput[0], valueToReput[1], valueToReput[2])
            self.session.add_value(COLLECTION_INITIAL, valueToReput[0], valueToReput[1], valueToReput[3])
