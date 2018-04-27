import os
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QVariant, QDateTime, QTime, QDate
from datetime import datetime, date, time
from populse_db.database_model import TAG_TYPE_LIST_FLOAT, TAG_TYPE_LIST_STRING, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_DATE, TAG_TYPE_LIST_DATETIME, TAG_TYPE_DATE, TAG_TYPE_TIME, TAG_TYPE_STRING, TAG_TYPE_INTEGER, TAG_TYPE_DATETIME, TAG_TYPE_FLOAT
import ast

def set_item_data(item, value, value_type):
    """
    Sets the item data
    :param item: item to set
    :param value: new item value
    :param value_type: new value type
    """

    if value_type in [TAG_TYPE_LIST_DATETIME, TAG_TYPE_LIST_DATE, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_STRING, TAG_TYPE_LIST_FLOAT]:
        if isinstance(value, str):
            value = ast.literal_eval(value)
        if value_type == TAG_TYPE_LIST_DATE:
            new_list = []
            for subvalue in value:
                new_list.append(subvalue.strftime('%d/%m/%Y'))
            value = new_list
        elif value_type == TAG_TYPE_LIST_DATETIME:
            new_list = []
            for subvalue in value:
                new_list.append(subvalue.strftime('%d/%m/%Y %H:%M:%S.%f'))
            value = new_list
        elif value_type == TAG_TYPE_LIST_TIME:
            new_list = []
            for subvalue in value:
                new_list.append(subvalue.strftime('%H:%M:%S.%f'))
            value = new_list
        value_prepared = str(value)
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_DATETIME:
        if isinstance(value, datetime):
            value_prepared = QDateTime(value)
        elif isinstance(value, QDateTime):
            value_prepared = value
        elif isinstance(value, str):
            format = "%d/%m/%Y %H:%M:%S.%f"
            value_prepared = QDateTime(datetime.strptime(value, format))
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_DATE:
        if isinstance(value, date):
            value_prepared = QDate(value)
        elif isinstance(value, QDate):
            value_prepared = value
        elif isinstance(value, str):
            format = "%d/%m/%Y"
            value_prepared = QDate(datetime.strptime(value, format).date())
        item.setData(Qt.EditRole, QVariant(value_prepared))
    elif value_type == TAG_TYPE_TIME:
        if isinstance(value, time):
            value_prepared = QTime(value)
        elif isinstance(value, QTime):
            value_prepared = value
        elif isinstance(value, str):
            format = "%H:%M:%S.%f"
            value_prepared = QTime(datetime.strptime(value, format).time())
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
    from populse_db.database_model import TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_FLOAT

    if value_type == TAG_TYPE_INTEGER or value_type == TAG_TYPE_LIST_INTEGER and is_subvalue:
        try:
            int(value)
            return True
        except Exception:
            return False
    elif value_type == TAG_TYPE_FLOAT or value_type == TAG_TYPE_LIST_FLOAT and is_subvalue:
        try:
            float(value)
            return True
        except Exception:
            return False
    elif value_type == TAG_TYPE_STRING or value_type == TAG_TYPE_LIST_STRING and is_subvalue:
        try:
            str(value)
            return True
        except Exception:
            return False
    elif value_type in [TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_DATETIME, TAG_TYPE_LIST_DATE, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_STRING, TAG_TYPE_LIST_FLOAT] and not is_subvalue:
        if isinstance(value, str):
            value = ast.literal_eval(value)
        is_valid_value = True
        for subvalue in value:
            if not check_value_type(subvalue, value_type, True):
                is_valid_value = False
                break
        return  is_valid_value
    elif value_type == TAG_TYPE_DATE or value_type == TAG_TYPE_LIST_DATE and is_subvalue:
        if isinstance(value, QDate):
            return True
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y"
                datetime.strptime(value, format).date()
                return True
            except Exception:
                return False
    elif value_type == TAG_TYPE_DATETIME or value_type == TAG_TYPE_LIST_DATETIME and is_subvalue:
        if isinstance(value, QDateTime):
            return True
        elif isinstance(value, str):
            try:
                format = "%d/%m/%Y %H:%M:%S.%f"
                datetime.strptime(value, format)
                return True
            except Exception:
                return False
    elif value_type == TAG_TYPE_TIME or value_type == TAG_TYPE_LIST_TIME and is_subvalue:
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

    if value_type == TAG_TYPE_FLOAT:
        return float(value)
    elif value_type == TAG_TYPE_STRING:
        return str(value)
    elif value_type == TAG_TYPE_INTEGER:
        return int(value)
    elif value_type == TAG_TYPE_DATETIME:
        if isinstance(value, QDateTime):
            return value.toPyDateTime()
        elif isinstance(value, str):
            format = "%d/%m/%Y %H:%M:%S.%f"
            return datetime.strptime(value, format)
    elif value_type == TAG_TYPE_DATE:
        if isinstance(value, QDate):
            return value.toPyDate()
        elif isinstance(value, str):
            format = "%d/%m/%Y"
            return datetime.strptime(value, format).date()
    elif value_type == TAG_TYPE_TIME:
        if isinstance(value, QTime):
            return value.toPyTime()
        elif isinstance(value, str):
            format = "%H:%M:%S.%f"
            return datetime.strptime(value, format).time()
    elif value_type in [TAG_TYPE_LIST_DATETIME, TAG_TYPE_LIST_DATE, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_STRING,
                        TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_FLOAT]:
        old_list = ast.literal_eval(value)
        list_to_return = []
        for old_element in old_list:
            list_to_return.append(table_to_database(old_element, value_type.replace("list_", "")))
        return list_to_return

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