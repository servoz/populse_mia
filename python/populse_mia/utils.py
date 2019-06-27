# -*- coding: utf-8 -*- #

"""Class and functions used across the software

:Contains:
    :Class:
        - ClickableLabel
    :Functions:
        - check_value_type
        - message_already_exists
        - set_filters_directory_as_default
        - set_item_data
        - set_projects_directory_as_default
        - table_to_database
"""


##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import ast
import os
import re
from datetime import datetime, date, time
import dateutil.parser

# PyQt5 imports
from PyQt5.QtCore import Qt, QVariant, QDateTime, QTime, QDate
from PyQt5.QtWidgets import (
    QDialog, QTableWidget, QVBoxLayout, QHBoxLayout,
    QTableWidgetItem, QPushButton, QMessageBox)

# Populse_db imports
from populse_db.database import (
    FIELD_TYPE_INTEGER, FIELD_TYPE_STRING, FIELD_TYPE_BOOLEAN,
    FIELD_TYPE_FLOAT, FIELD_TYPE_TIME, FIELD_TYPE_DATE, FIELD_TYPE_DATETIME,
    LIST_TYPES, FIELD_TYPE_LIST_BOOLEAN, FIELD_TYPE_LIST_INTEGER,
    FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_STRING, FIELD_TYPE_LIST_DATE,
    FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_TIME)

from populse_mia.software_properties import Config

# Populse_MIA imports
from populse_mia.data_manager.project import COLLECTION_CURRENT


class ModifyTable(QDialog):
    """
    Verify precisely the scans of the project and update the table after a
      modification.

    Methods:
        - fill_table: fill the table
        - update_table_values: update the table in the database
    """

    def __init__(self, project, value, types, scans, tags):
        """
        Initialization of the ModifyTable class

        :param project: Instance of project
        :param value: List of values of the cell
        :param types: Value types
        :param scans: Scans of the rows
        :param tags: Tags of the columns
        """
        super().__init__()

        self.setModal(True)

        # Variables init
        self.types = types
        self.scans = scans
        self.tags = tags
        self.project = project
        self.value = value

        # The table that will be filled
        self.table = QTableWidget()

        # Filling the table
        self.fill_table()

        # Ok button
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.update_table_values)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.h_box_final = QHBoxLayout()

        self.h_box_final.addWidget(ok_button)
        self.h_box_final.addWidget(cancel_button)

        self.v_box_final.addWidget(self.table)
        self.v_box_final.addLayout(self.h_box_final)

        self.setLayout(self.v_box_final)

    def fill_table(self):
        """Fill the table."""
        # Sizes
        self.table.setColumnCount(len(self.value))
        self.table.setRowCount(1)

        # Values filled
        for i in range (0, self.table.columnCount()):
            column_elem = self.value[i]
            item = QTableWidgetItem()
            item.setText(str(column_elem))
            self.table.setItem(0, i, item)

        # Resize
        self.table.resizeColumnsToContents()
        total_width = 0
        total_height = 0
        i = 0
        while i < self.table.columnCount():
            total_width += self.table.columnWidth(i)
            total_height += self.table.rowHeight(i)
            i += 1
        if total_width + 20 < 900:
            self.table.setFixedWidth(total_width + 20)
            self.table.setFixedHeight(total_height + 25)
        else:
            self.table.setFixedWidth(900)
            self.table.setFixedHeight(total_height + 40)

    def update_table_values(self):
        """Update the table in the database when the 'OK' button is clicked."""

        valid = True

        # For each value, type checked
        for i in range (0, self.table.columnCount()):
            item = self.table.item(0, i)
            text = item.text()

            valid_type = True
            for tag_type in self.types:
                if not check_value_type(text, tag_type, True):
                    valid_type = False
                    type_problem = tag_type
                    break

            # Type checked
            if not valid_type:

                # Error dialog if invalid cell
                valid = False
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Invalid value")
                msg.setInformativeText("The value " + text +
                                       " is invalid with the type " +
                                       type_problem)
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()
                break

        if valid:
            # Database updated only if valid type for every cell

            for cell in range (0, len(self.scans)):
                scan = self.scans[cell]
                tag = self.tags[cell]
                tag_object = self.project.session.get_field(
                    COLLECTION_CURRENT, tag)
                tag_type = tag_object.type

                database_value = []

                # For each value
                for i in range (0, self.table.columnCount()):
                    item = self.table.item(0, i)
                    text = item.text()

                    if tag_type == FIELD_TYPE_LIST_INTEGER:
                        database_value.append(int(text))
                    elif tag_type == FIELD_TYPE_LIST_FLOAT:
                        database_value.append(float(text))
                    elif tag_type == FIELD_TYPE_LIST_STRING:
                        database_value.append(str(text))
                    elif tag_type == FIELD_TYPE_LIST_DATE:
                        format = "%d/%m/%Y"
                        subvalue = datetime.strptime(text, format).date()
                        database_value.append(subvalue)
                    elif tag_type == FIELD_TYPE_LIST_DATETIME:
                        format = "%d/%m/%Y %H:%M"
                        subvalue = datetime.strptime(text, format)
                        database_value.append(subvalue)
                    elif tag_type == FIELD_TYPE_LIST_TIME:
                        format = "%H:%M"
                        subvalue = datetime.strptime(text, format).time()
                        database_value.append(subvalue)

                # Database updated for every cell
                self.project.session.set_value(
                    COLLECTION_CURRENT, scan, tag, database_value)

            self.close()


def check_value_type(value, value_type, is_subvalue=False):
    """
    Checks the type of a new value

    :param value: Value of the cell
    :param value_type: Type expected
    :param is_subvalue: To know if the value is a subvalue of a list
    :return: True if the value is valid to replace the old one, False otherwise
    """
    if (value_type == FIELD_TYPE_INTEGER or
            value_type == FIELD_TYPE_LIST_INTEGER and is_subvalue):
        try:
            int(value)
            return True
        except Exception:
            return False
    elif (value_type == FIELD_TYPE_FLOAT or
          value_type == FIELD_TYPE_LIST_FLOAT and is_subvalue):
        try:
            float(value)
            return True
        except Exception:
            return False
    elif (value_type == FIELD_TYPE_BOOLEAN or
        value_type == FIELD_TYPE_LIST_BOOLEAN and is_subvalue):
        return (value == "True" or value == True or value == "False" or
                value == False)
    elif (value_type == FIELD_TYPE_STRING or
            value_type == FIELD_TYPE_LIST_STRING and is_subvalue):
        try:
            str(value)
            return True
        except Exception:
            return False
    elif value_type in LIST_TYPES and not is_subvalue:
        if isinstance(value, str):
            value = ast.literal_eval(value)
        is_valid_value = True
        for subvalue in value:
            if not check_value_type(subvalue, value_type, True):
                is_valid_value = False
                break
        return is_valid_value
    elif (value_type == FIELD_TYPE_DATE or
            value_type == FIELD_TYPE_LIST_DATE and is_subvalue):
        if isinstance(value, QDate):
            return True
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y"
                datetime.strptime(value, format).date()
                return True
            except Exception:
                return False
    elif (value_type == FIELD_TYPE_DATETIME or
            value_type == FIELD_TYPE_LIST_DATETIME and is_subvalue):
        if isinstance(value, QDateTime):
            return True
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y %H:%M:%S.%f"
                datetime.strptime(value, format)
                return True
            except Exception:
                return False
    elif (value_type == FIELD_TYPE_TIME or
          value_type == FIELD_TYPE_LIST_TIME and is_subvalue):
        if isinstance(value, QTime):
            return True
        elif isinstance(value, str):
            try:
                format = "%H:%M:%S.%f"
                datetime.strptime(value, format).time()
                return True
            except Exception:
                return False


def message_already_exists():
    """
    Displays a message box to tell that a name already exists
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("This name already exists in this parent folder")
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.buttonClicked.connect(msg.close)
    msg.exec()


def set_filters_directory_as_default(dialog):
    """
    Sets the filters directory as default (Json files)

    :param dialog: current file dialog
    """
    if not (os.path.exists(os.path.join(
            os.path.join(os.path.relpath(
                os.curdir), '..', '..'), 'filters'))):
        os.makedirs(os.path.join(
            os.path.join(os.path.relpath(
                os.curdir), '..', '..'), 'filters'))
    dialog.setDirectory(
        os.path.expanduser(os.path.join(
            os.path.join(os.path.relpath(
                os.curdir), '..', '..'), 'filters')))


def set_item_data(item, value, value_type):
    """
    Sets the item data in the data browser

    :param item: item to set
    :param value: new item value
    :param value_type: new value type
    """

    if value_type in LIST_TYPES:
        if isinstance(value, str):
            value = ast.literal_eval(value)
        if value_type == FIELD_TYPE_LIST_DATE:
            new_list = []
            for subvalue in value:
                new_list.append(subvalue.strftime('%d/%m/%Y'))
            value = new_list
        elif value_type == FIELD_TYPE_LIST_DATETIME:
            new_list = []
            for subvalue in value:
                new_list.append(subvalue.strftime('%d/%m/%Y %H:%M:%S.%f'))
            value = new_list
        elif value_type == FIELD_TYPE_LIST_TIME:
            new_list = []
            for subvalue in value:
                new_list.append(subvalue.strftime('%H:%M:%S.%f'))
            value = new_list
        value_prepared = str(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_DATETIME:
        if isinstance(value, datetime):
            value_prepared = QDateTime(value)
        elif isinstance(value, QDateTime):
            value_prepared = value
        elif isinstance(value, str):
            format = "%d/%m/%Y %H:%M:%S.%f"
            value_prepared = QDateTime(datetime.strptime(value, format))
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_DATE:
        if isinstance(value, date):
            value_prepared = QDate(value)
        elif isinstance(value, QDate):
            value_prepared = value
        elif isinstance(value, str):
            format = "%d/%m/%Y"
            value_prepared = QDate(datetime.strptime(value, format).date())
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_TIME:
        if isinstance(value, time):
            value_prepared = QTime(value)
        elif isinstance(value, QTime):
            value_prepared = value
        elif isinstance(value, str):
            format = "%H:%M:%S.%f"
            value_prepared = QTime(datetime.strptime(value, format).time())
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_FLOAT:
        value_prepared = float(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_INTEGER:
        value_prepared = int(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_BOOLEAN:
        value_prepared = value
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == FIELD_TYPE_STRING:
        value_prepared = str(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))


def set_projects_directory_as_default(dialog):
    """
    Sets the projects directory as default

    :param dialog: current file dialog
    """
    config = Config()
    projects_directory = config.get_projects_save_path()
    if not os.path.exists(projects_directory):
        os.makedirs(projects_directory)
    dialog.setDirectory(projects_directory)


def table_to_database(value, value_type):
    """
    Prepares the value to the database

    :param value: Value to convert
    :param value_type: Value type
    :return: The value converted for the database
    """

    if value_type == FIELD_TYPE_FLOAT:
        return float(value)
    elif value_type == FIELD_TYPE_STRING:
        return str(value)
    elif value_type == FIELD_TYPE_INTEGER:
        return int(value)
    elif value_type == FIELD_TYPE_BOOLEAN:
        if value == "True" or value == True:
            return True
        elif value == "False" or value == False:
            return False
    elif value_type == FIELD_TYPE_DATETIME:
        if isinstance(value, QDateTime):
            return value.toPyDateTime()
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y %H:%M:%S.%f"
                date_typed = datetime.strptime(value, format)
            except Exception:
                date_typed = dateutil.parser.parse(value)
            return date_typed

    elif value_type == FIELD_TYPE_DATE:
        if isinstance(value, QDate):
            return value.toPyDate()
        elif isinstance(value, str):
            format = "%d/%m/%Y"
            return datetime.strptime(value, format).date()
    elif value_type == FIELD_TYPE_TIME:
        if isinstance(value, QTime):
            return value.toPyTime()
        elif isinstance(value, str):
            format = "%H:%M:%S.%f"
            return datetime.strptime(value, format).time()
    elif value_type in LIST_TYPES:
        old_list = ast.literal_eval(value)
        list_to_return = []
        for old_element in old_list:
            list_to_return.append(table_to_database(
                old_element, value_type.replace("list_", "")))
        return list_to_return


