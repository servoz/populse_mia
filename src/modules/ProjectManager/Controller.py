import glob
import os.path
import json
import hashlib # To generate the md5 of each scan
from populse_db.database_model import TAG_ORIGIN_BUILTIN, TAG_TYPE_STRING, TAG_ORIGIN_USER, TAG_TYPE_LIST_INTEGER, TAG_TYPE_LIST_DATE, TAG_TYPE_INTEGER, TAG_TYPE_LIST_DATETIME, TAG_TYPE_LIST_FLOAT, TAG_TYPE_TIME, TAG_TYPE_FLOAT, TAG_TYPE_DATE, TAG_TYPE_DATETIME, TAG_TYPE_LIST_TIME, TAG_TYPE_LIST_STRING
from SoftwareProperties.Config import Config
import datetime
import yaml
from time import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from datetime import datetime

def getJsonTagsFromFile(file_path, path):
   """
    :return:
    :param file_path: file path of the Json file
    :param path: project path
    :return: a list of the Json tags of the file"""
   json_tags = []
   with open(os.path.join(path, file_path) + ".json") as f:
       for name,value in json.load(f).items():
            json_tags.append([name, value])
   return json_tags

def read_log(project):

    """ From the log export file of the import software, the data base (here the current project) is loaded with
    the tags"""

    begin = time()

    raw_data_folder = os.path.relpath(os.path.join(project.folder, 'data', 'raw_data'))

    # Checking all the export logs from MRIManager and taking the most recent
    list_logs = glob.glob(os.path.join(raw_data_folder, "logExport*.json"))
    log_to_read = max(list_logs, key=os.path.getctime)

    with open(log_to_read, "r", encoding="utf-8") as file:
        list_dict_log = json.load(file)

    # For history
    historyMaker = []
    historyMaker.append("add_scans")
    scans_added = []
    values_added = []
    tags_added = []
    tags_infos = []
    values_infos = {}
    tag_objects = {}

    # Default tags stored
    config = Config()
    default_tags = config.getDefaultTags()
    tags_to_remove = ["Dataset data file", "Dataset header file"] # List of tags to remove

    # Progressbar
    len_log = len(list_dict_log)
    ui_progressbar = QProgressDialog("Reading exported files", "Cancel", 0, len_log)
    ui_progressbar.setWindowModality(Qt.WindowModal)
    ui_progressbar.setWindowTitle("")
    idx = 0
    for dict_log in list_dict_log:

        # Progressbar
        idx += 1
        ui_progressbar.setValue(idx)
        if ui_progressbar.wasCanceled():
            break

        if dict_log['StatusExport'] == "Export ok":
            file_name = dict_log['NameFile']
            path_name = raw_data_folder
            with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
                data = scan_file.read()
                original_md5 = hashlib.md5(data).hexdigest()

            scans_added.append([file_name, original_md5]) # Scan added to history

            values_infos[file_name] = []

            # For each tag in each scan
            for tag in getJsonTagsFromFile(file_name, path_name): # For each tag of the scan

                # We do the tag only if it's not in the tags to remove
                if tag[0] not in tags_to_remove:
                    properties = tag[1]
                    unit = None
                    format = ''
                    tag_type = TAG_TYPE_STRING
                    description = None
                    if isinstance(properties, dict):
                        value = properties['value']
                        unit = properties['units']
                        if unit == "":
                            unit = None
                        format = properties['format']
                        tag_type = properties['type']
                        if tag_type == "":
                            tag_type = TAG_TYPE_STRING
                        description = properties['description']
                        if description == "":
                            description = None
                    else:
                        value = properties[0]

                    tag_name = tag[0]

                    # Creating date types
                    if format is not None and format != "":
                        format = format.replace("yyyy", "%Y")
                        format = format.replace("MM", "%m")
                        format = format.replace("dd", "%d")
                        format = format.replace("HH", "%H")
                        format = format.replace("mm", "%M")
                        format = format.replace("ss", "%S")
                        format = format.replace("SSS", "%f")
                        if "%Y" in format and "%m" in format and "%d" in format and "%H" in format and "%M" in format and "%S" in format:
                            tag_type = TAG_TYPE_DATETIME
                        elif "%Y" in format and "%m" in format and "%d" in format:
                            tag_type = TAG_TYPE_DATE
                        elif "%H" in format and "%M" in format and "%S" in format:
                            tag_type = TAG_TYPE_TIME

                    if tag_name != "Json_Version":
                        # Preparing value and type
                        if len(value) is 1:
                            value = value[0]
                        else:
                            if tag_type == TAG_TYPE_STRING:
                                tag_type = TAG_TYPE_LIST_STRING
                            elif tag_type == TAG_TYPE_INTEGER:
                                tag_type = TAG_TYPE_LIST_INTEGER
                            elif tag_type == TAG_TYPE_FLOAT:
                                tag_type = TAG_TYPE_LIST_FLOAT
                            elif tag_type == TAG_TYPE_DATE:
                                tag_type = TAG_TYPE_LIST_DATE
                            elif tag_type == TAG_TYPE_DATETIME:
                                tag_type = TAG_TYPE_LIST_DATETIME
                            elif tag_type == TAG_TYPE_TIME:
                                tag_type = TAG_TYPE_LIST_TIME
                            value_prepared = []
                            for value_single in value:
                                value_prepared.append(value_single[0])
                            value = value_prepared

                    if tag_type == TAG_TYPE_DATETIME or tag_type == TAG_TYPE_DATE or tag_type == TAG_TYPE_TIME:
                        if value is not None and value != "":
                            value = datetime.strptime(value, format)
                            if tag_type == TAG_TYPE_TIME:
                                value = value.time()
                            elif tag_type == TAG_TYPE_DATE:
                                value = value.date()

                    # TODO time lists

                    if tag_name in tag_objects:
                        tag_object = tag_objects[tag_name]
                    else:
                        tag_object = project.database.get_tag(tag_name)
                        tag_objects[tag_name] = tag_object
                    if tag_name not in tags_added and tag_object is None:
                        tags_added.append(tag_name)
                        # Adding the tag as it's not in the database yet
                        tags_infos.append([tag_name, TAG_ORIGIN_BUILTIN, tag_type, unit, None,
                                                     description])

                    # The value is accepted if it's not empty or null
                    if value is not None and value != "":
                        values_added.append([file_name, tag_name, value, value]) # Value added to history
                        values_infos[file_name].append([tag_name, value, value])

    ui_progressbar.close()

    # Missing values added thanks to default values
    for tag in project.database.get_tags():
        if tag.origin == TAG_ORIGIN_USER:
            for scan in scans_added:
                if tag.default_value is not None and project.database.get_current_value(scan[0], tag.name) is None:
                    values_added.append([scan[0], tag.name, tag.default_value, None])  # Value added to history
                    values_infos[scan[0]].append([tag.name, tag.default_value, None])

    begin_scans = time()
    project.database.add_paths(scans_added)
    print("add scans : " + str(time() - begin_scans))

    begin_tags = time()
    project.database.add_tags(tags_infos)
    print("add tags : " + str(time() - begin_tags))

    begin_values = time()
    project.database.new_values(values_infos)
    print("add values : " + str(time() - begin_values))

    # For history
    historyMaker.append(scans_added)
    historyMaker.append(values_added)
    project.undos.append(historyMaker)
    project.redos.clear()

    print("read_log time: " + str(time() - begin))

def verify_scans(project, path):
    # Returning the files that are problematic
    return_list = []
    for scan in project.database.get_paths():

        file_name = scan.name
        path_name = os.path.relpath(os.path.join(path, 'data', 'raw_data'))

        if os.path.exists(os.path.join(path_name, file_name) + ".nii"):
            # If the file exists, we do the checksum
            with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
                data = scan_file.read()
                actual_md5 = hashlib.md5(data).hexdigest()

            if actual_md5 != scan.checksum:
                return_list.append(file_name)

        else:
            # Otherwise, we directly add the file in the list
            return_list.append(file_name)

    return return_list

def save_project(database):
    database.saveModifications()
