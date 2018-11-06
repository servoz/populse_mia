##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import ast
import os
from datetime import datetime, date, time
import dateutil.parser

# PyQt5 imports
from PyQt5.QtCore import Qt, QVariant, QDateTime, QTime, QDate
from PyQt5.QtWidgets import QMessageBox

# Populse_MIA imports
from populse_mia.software_properties.config import Config

# Populse_db imports
from populse_db.database import FIELD_TYPE_INTEGER, FIELD_TYPE_LIST_INTEGER, FIELD_TYPE_STRING, FIELD_TYPE_BOOLEAN, \
    FIELD_TYPE_FLOAT, FIELD_TYPE_TIME, FIELD_TYPE_DATE, FIELD_TYPE_DATETIME, FIELD_TYPE_LIST_TIME, \
    FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_DATE, LIST_TYPES, FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_BOOLEAN, \
    FIELD_TYPE_LIST_STRING


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


def check_value_type(value, value_type, is_subvalue=False):
    """
    Checks the type of a new value

    :param value: Value of the cell
    :param value_type: Type expected
    :param is_subvalue: To know if the value is a subvalue of a list
    :return: True if the value is valid to replace the old one, False otherwise
    """

    if value_type == FIELD_TYPE_INTEGER or value_type == FIELD_TYPE_LIST_INTEGER and is_subvalue:
        try:
            int(value)
            return True
        except Exception:
            return False
    elif value_type == FIELD_TYPE_FLOAT or value_type == FIELD_TYPE_LIST_FLOAT and is_subvalue:
        try:
            float(value)
            return True
        except Exception:
            return False
    elif value_type == FIELD_TYPE_BOOLEAN or value_type == FIELD_TYPE_LIST_BOOLEAN and is_subvalue:
        return value == "True" or value == True or value == "False" or value == False
    elif value_type == FIELD_TYPE_STRING or value_type == FIELD_TYPE_LIST_STRING and is_subvalue:
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
    elif value_type == FIELD_TYPE_DATE or value_type == FIELD_TYPE_LIST_DATE and is_subvalue:
        if isinstance(value, QDate):
            return True
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y"
                datetime.strptime(value, format).date()
                return True
            except Exception:
                return False
    elif value_type == FIELD_TYPE_DATETIME or value_type == FIELD_TYPE_LIST_DATETIME and is_subvalue:
        if isinstance(value, QDateTime):
            return True
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y %H:%M:%S.%f"
                datetime.strptime(value, format)
                return True
            except Exception:
                return False
    elif value_type == FIELD_TYPE_TIME or value_type == FIELD_TYPE_LIST_TIME and is_subvalue:
        if isinstance(value, QTime):
            return True
        elif isinstance(value, str):
            try:
                format = "%H:%M:%S.%f"
                datetime.strptime(value, format).time()
                return True
            except Exception:
                return False


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
            list_to_return.append(table_to_database(old_element, value_type.replace("list_", "")))
        return list_to_return


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


def set_filters_directory_as_default(dialog):
    """
    Sets the filters directory as default (Json files)

    :param dialog: current file dialog
    """
    if not (os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'filters'))):
        os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'filters'))
    dialog.setDirectory(
        os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'filters')))
