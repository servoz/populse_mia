import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QVariant, QDateTime, QTime, QDate
from datetime import datetime, date, time
from populse_db.DatabaseModel import TAG_TYPE_LIST_FLOAT, TAG_TYPE_LIST_STRING, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_DATE, TAG_TYPE_LIST_DATETIME, TAG_TYPE_DATE, TAG_TYPE_TIME, TAG_TYPE_STRING, TAG_TYPE_INTEGER, TAG_TYPE_DATETIME, TAG_TYPE_FLOAT

def set_item_data(item, value, value_type):
    """
    Sets the item data
    :param item: item to set
    :param value: new item value
    :param value_type: new value type
    """

    import ast

    if value_type in [TAG_TYPE_LIST_DATETIME, TAG_TYPE_LIST_DATE, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_STRING, TAG_TYPE_LIST_FLOAT]:
        if isinstance(value, str):
            value = ast.literal_eval(value)
        value_prepared = str(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_DATETIME:
        if isinstance(value, datetime):
            value_prepared = QDateTime(value)
        elif isinstance(value, QDateTime):
            value_prepared = value
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_DATE:
        if isinstance(value, date):
            value_prepared = QDate(value)
        elif isinstance(value, QDate):
            value_prepared = value
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_TIME:
        if isinstance(value, time):
            value_prepared = QTime(value)
        elif isinstance(value, QTime):
            value_prepared = value
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_FLOAT:
        value_prepared = float(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_INTEGER:
        value_prepared = int(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_STRING:
        value_prepared = str(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))

def check_value_type(value, value_type, is_subvalue=False):
    """
    Checks the type of the new value
    :param value: Value of the cell
    :param value_type: Type expected
    :param is_subvalue: To know if the value is a subvalue of a list
    :return: True if the value is valid to replace the old one, False otherwise
    """
    from populse_db.DatabaseModel import TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_FLOAT

    if value_type == TAG_TYPE_INTEGER or value_type == TAG_TYPE_LIST_INTEGER and is_subvalue:
        try:
            int(value)
            return True
        except ValueError:
            return False
    elif value_type == TAG_TYPE_FLOAT or value_type == TAG_TYPE_LIST_FLOAT and is_subvalue:
        try:
            float(value)
            return True
        except ValueError:
            return False
    elif value_type == TAG_TYPE_STRING or value_type == TAG_TYPE_LIST_STRING and is_subvalue:
        try:
            str(value)
            return True
        except ValueError:
            return False
    elif value_type == TAG_TYPE_DATE or value_type == TAG_TYPE_LIST_DATE and is_subvalue:
        return isinstance(value, QDate)
    elif value_type == TAG_TYPE_DATETIME or value_type == TAG_TYPE_LIST_DATETIME and is_subvalue:
        return isinstance(value, QDateTime)
    elif value_type == TAG_TYPE_TIME or value_type == TAG_TYPE_LIST_TIME and is_subvalue:
        return isinstance(value, QTime)

def table_to_database(value, value_type):
    """
    Prepares the value to the database
    :param value: Value to convert
    :param value_type: Value type
    :return: The value converted for the database
    """

    if value_type == TAG_TYPE_FLOAT:
        return float(value_type)
    elif value_type == TAG_TYPE_STRING:
        return str(value_type)
    elif value_type == TAG_TYPE_INTEGER:
        return int(value_type)
    elif value_type == TAG_TYPE_DATETIME:
        if isinstance(value, QDateTime):
            return value.toPyDateTime()
    elif value_type == TAG_TYPE_DATE:
        if isinstance(value, QDate):
            return value.toPyDate()
    elif value_type == TAG_TYPE_TIME:
        if isinstance(value, QTime):
            return value.toPyTime()

    # TODO list types

def message_already_exists():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText("This name already exists in this parent folder")
    msg.setWindowTitle("Warning")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.buttonClicked.connect(msg.close)
    msg.exec()


def set_projects_directory_as_default(dialog):
    # Setting the projects directory as default
    if not (os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects'))):
        os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects'))
    dialog.setDirectory(
        os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects')))

def set_filters_directory_as_default(dialog):
    # Setting the filters directory as default (Json files)
    if not (os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'filters'))):
        os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'filters'))
    dialog.setDirectory(
        os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'filters')))