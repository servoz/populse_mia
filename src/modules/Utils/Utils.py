import os
from PyQt5.QtWidgets import QMessageBox


def database_to_table(value):
    """
    Converts a value from the Database to the DataBrowser
    :param value: Value to convert
    :return: The value converted for the table
    """
    import ast

    # String from Database converted in List
    list_value = ast.literal_eval(value)

    # If there is a single element, we return it directly
    if len(list_value) == 1:
        if isinstance(list_value[0], list):
            # List
            return str(list_value)
        else:
            return str(list_value[0])
    # Otherwise, we return the str representation of the list
    else:
        return str(list_value)

def table_to_database(value, type):
    """
    Converts a value from the table (str) to the Database
    :param value: Value to convert
    :param type: Type of tag value
    :return: The value converted for the Database (list)
    """
    import ast
    from Database.DatabaseModel import TAG_TYPE_STRING
    try:
        list_value = ast.literal_eval(value)
        if isinstance(list_value, list):
            # The value is a list
            return str(list_value)
        else:
            # The value is a single value, we return it as a list
            if type == TAG_TYPE_STRING:
                return "['" + list_value + "']"
            else:
                return "[" + list_value + "]"
    except Exception:
        # The value is a single value, we return it as a list
        if type == TAG_TYPE_STRING:
            return "['" + value + "']"
        else:
            return "[" + value + "]"

def check_value_type(value, type):
    """
    Checks the type of the new value
    :param value: Value of the cell, str
    :param type: Type expected
    :return: True if the value is valid to replace the old one, False otherwise
    """
    from Database.DatabaseModel import TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_STRING

    if type == TAG_TYPE_INTEGER:
        try:
            int(value)
            return True
        except ValueError:
            return False
    elif type == TAG_TYPE_FLOAT:
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