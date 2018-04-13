import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QVariant, QDateTime, QTime, QDate
from datetime import datetime, date, time

def set_item_data(item, value):
    """
    Sets the item data
    :param item: item to set
    :param value: new item value
    """

    if isinstance(value, list):
        item.setData(Qt.EditRole, QVariant(str(value)))
    elif isinstance(value, datetime):
        value_date = QDateTime(value)
        item.setData(Qt.EditRole, QVariant(value_date))
    elif isinstance(value, date):
        value_date = QDate(value)
        item.setData(Qt.EditRole, QVariant(value_date))
    elif isinstance(value, time):
        value_date = QTime(value)
        item.setData(Qt.EditRole, QVariant(value_date))
    else:
        item.setData(Qt.EditRole, QVariant(value))

def check_value_type(value, type, is_subvalue=False):
    """
    Checks the type of the new value
    :param value: Value of the cell, str
    :param type: Type expected
    :param is_subvalue: To know if the value is a subvalue of a list
    :return: True if the value is valid to replace the old one, False otherwise
    """
    from populse_db.DatabaseModel import TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_FLOAT

    if type == TAG_TYPE_INTEGER or type == TAG_TYPE_LIST_INTEGER and is_subvalue:
        try:
            int(value)
            return True
        except ValueError:
            return False
    elif type == TAG_TYPE_FLOAT or type == TAG_TYPE_LIST_FLOAT and is_subvalue:
        try:
            float(value)
            return True
        except ValueError:
            return False
    # Otherwise, str
    else:
        try:
            str(value)
            return True
        except ValueError:
            return False
    # TODO add other types

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