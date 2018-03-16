import os
from PyQt5.QtWidgets import QMessageBox


def database_to_table(value):
    """
    Converts a value from the database to the databrowser
    :param value: Value to convert
    :return: The value converted for the table
    """
    import ast

    # String from Database converted in List
    list_value = ast.literal_eval(value)

    # If there is a single element, we return it directly
    if len(list_value) == 1:
        return str(list_value[0])
    # Otherwise, we return the str representation of the list
    else:
        return str(list_value)

def table_to_database(value):
    """
    Converts a value from the table (str) to the database
    :param value: Value to convert
    :return: The value converted for the database (list)
    """
    return "['" + value + "']"

def check_value_type(value, type):
    """
    Checks the type of the new value
    :param value: Value of the cell, str
    :param type: Type expected
    :return: True if the value is valid to replace the old one, False otherwise
    """
    from DataBase.DataBaseModel import TAG_TYPE_INTEGER, TAG_TYPE_FLOAT, TAG_TYPE_STRING

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

def check_tag_value(tag):
    """
    NOT USED ANYMORE
    :param tag: Tag value to convert
    :return:
    """
    txt = ""
    if len(tag) == 1:
        txt = str(tag[0])
    else:
        for idx, item in enumerate(tag):
            if isinstance(item, list):
                txt += str(item[0])
            else:
                txt += str(item)
            if idx < len(tag) - 1: # < len(current_value)
                txt += ", "
    return txt


def compare_values(tag):
    """ Compares the actual value and the original value of a tag and returns if they are the same or not"""
    """print(tag.original_value)
    print(type(tag.original_value))
    print(tag.value)
    print(type(tag.value))"""

    if tag.original_value is None:
        if tag.value is None:
            return True
        else:
            return False

    elif isinstance(tag.original_value, list):
        return tag.original_value[0] == tag.value[0]


def text_to_tag_value(text_value, tag):
    """ From the text value of an item (a string), this function returns the corresponding tag value, written the right way,
    depending on its type"""

    tag_value = []

    if text_value == "" or text_value is None:
        tag_value.append("")

    elif len(text_value) > 0 and text_value[0] == '[':
        string_values = []
        value = ""
        # We check all the characters each list to determine if it is an int, float or a string
        for idx, char in enumerate(text_value):
            if char == '[':
                value = ""
            elif char == ']':
                if text_value[idx - 1] != ']':
                    string_values.append("".join(value))
            else:
                value += str(char)
        # From string value, we check the type of data
        for element in string_values:
            a = 0
            b = 0
            for char in element:
                if char.isdigit() or char == '-' or char == '+':
                    a += 1
                if char == '.' or char.lower() == 'e':
                    b += 1

            if a == len(element) - 1 and a > 0 and b == 0:
                int_result = int(element)
                list_int = []
                list_int.append(int_result)
                tag_value.append(list_int)

            elif (a == len(element) - 1 or a == len(element) - 2) and a > 0 and (b == 1 or b == 2):
                float_result = float(element)
                list_float = []
                list_float.append(float_result)
                tag_value.append(list_float)

            else:
                list_string = []
                list_string.append(element)
                tag_value.append(list_string)

    else:
        tp = type(tag.original_value[0])
        tag_value.append(tp(text_value))

    return tag_value


def text_to_list(text_value):
    string_values = []
    value = ""
    # We check all the characters each list to determine if it is an int, float or a string
    for idx, char in enumerate(text_value):
        if char == ',':
            string_values.append("".join(value))
            value = ""
        else:
            value += str(char)
        if idx == len(text_value) - 1:
            string_values.append("".join(value))

    tag_value = []
    # From string value, we check the type of data
    for element in string_values:
        a = 0
        b = 0
        for char in element:
            if char.isdigit() or char == '-' or char == '+':
                a += 1
            if char == '.' or char.lower() == 'e':
                b += 1

        if a == len(element) and a > 0 and b == 0:
            int_result = int(element)
            list_int = []
            list_int.append(int_result)
            tag_value.append(list_int)

        elif (a == len(element) or a == len(element) - 1) and a > 0 and (b == 1 or b == 2):
            float_result = float(element)
            list_float = []
            list_float.append(float_result)
            tag_value.append(list_float)

        else:
            list_string = []
            list_string.append(element)
            tag_value.append(list_string)

    return tag_value


"""
# First version of check_tag_value (not behaving the right way for this project)
def check_tag_value(tag, which_value):
    txt = ""
    if which_value == 'value':
        if tag.origin.upper() == 'JSON' or tag.origin.upper() == 'CUSTOM':
            if isinstance(tag.value, list):
                if len(tag.value) == 1:
                    txt = str(tag.value[0])
                else:
                    txt = str(tag.value)
            elif isinstance(tag.value, (np.ndarray, np.generic)):
                txt = str(tag.value)
            else:
                if tag.value[0] == "[":
                    if tag.value[1] == '"' or tag.value[1] == "'":
                        txt = str(tag.value[2:len(tag.value) - 2])
                    else:
                        txt = str(tag.value[1:len(tag.value) - 1])
        else:
            txt = str(tag.value)

    elif which_value == 'original_value':
        if tag.origin.upper() == 'JSON' or tag.origin.upper() == 'CUSTOM':
            if isinstance(tag.original_value, list):
                if len(tag.original_value) == 1:
                    txt = str(tag.original_value[0])
                else:
                    txt = str(tag.original_value)
            elif isinstance(tag.original_value, (np.ndarray, np.generic)):
                txt = str(tag.original_value)
            else:
                if tag.original_value[0] == "[":
                    if tag.original_value[1] == '"' or tag.original_value[1] == "'":
                        txt = str(tag.original_value[2:len(tag.original_value) - 2])
                    else:
                        txt = str(tag.original_value[1:len(tag.original_value) - 1])
        else:
            txt = str(tag.original_value)

    else:
        print("which_value has to be 'value' or 'original_value'")
        txt = 'error'

    return txt
"""


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