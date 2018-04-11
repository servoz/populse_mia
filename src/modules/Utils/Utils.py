import os
from PyQt5.QtWidgets import QMessageBox

def check_value_type(value, type):
    """
    Checks the type of the new value
    :param value: Value of the cell, str
    :param type: Type expected
    :return: True if the value is valid to replace the old one, False otherwise
    """
    from populse_db.DatabaseModel import TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_STRING

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