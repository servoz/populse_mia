import numpy as np


def getFilePathWithoutExtension(filepath, path):
    return filepath[len(path):filepath.rfind('.')]


def substractLists(listA,listB):
    """

    :param listA: a list
    :param listB: a list
    :return: a list of the elements that are in listA and not in listB
    """
    return list(set(listA) - set(listB))


def createJsonFile(path, name):
    open(path+name+'.json', 'w')
    return name+'.json'


def saveProjectAsJsonFile(name, project):
    import json
    from models import serializer
    """for scan in project._get_scans():
        for tag in scan.getAllTags():
            print(tag.name)
            print(tag.value)
            print(tag.original_value)
            print("")"""

    with open(name+'.json', 'w') as f:
        f.write(json.dumps(project, default=serializer))


def findPath(name_file):
    from os import path as os_path
    return (os_path.abspath(os_path.split(name_file)[0]))


def remove_accents(txt):
    ch1 = u"àâçéèêëîïôùûüÿ"
    ch2 = u"aaceeeeiiouuuy"
    s = ""
    for c in txt:
        i = ch1.find(c)
        if i >= 0:
            s += ch2[i]
        else:
            s += c
    return s


def check_tag_value(tag, which_value):
    txt = ""
    if which_value == 'value':
        if tag.origin == 'Json' or tag.origin == 'custom':
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
        if tag.origin == 'Json' or tag.origin == 'custom':
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
