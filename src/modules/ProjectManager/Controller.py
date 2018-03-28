import glob
import os.path
import json
import Utils.Utils as utils
import hashlib # To generate the md5 of each scan
from Database.DatabaseModel import TAG_ORIGIN_RAW, TAG_TYPE_STRING, TAG_ORIGIN_USER
from SoftwareProperties.Config import Config
import datetime
import yaml
from time import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog

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


def createProject(name, path, parent_folder):
    """
    Creates a new project
    :param name: project name
    :param path: project path
    :param parent_folder: project folder
    :return: the project object
    """

    # Formating the name to remove spaces et strange characters -> folder name
    recorded_path = os.path.relpath(parent_folder)
    new_path = os.path.join(recorded_path, name)

    # Creating the folder with the folder name that has been formatted
    if not os.path.exists(new_path):
        project_parent_folder = os.makedirs(new_path)
        data_folder = os.makedirs(os.path.join(new_path, 'data'))
        project_path = os.path.join(new_path, name)
        raw_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'raw_data'))
        derived_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'derived_data'))

        #Properties
        os.mkdir(os.path.join(new_path, 'properties'))
        properties = dict(
            name=name,
            date=datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            sorted_tag='',
            sort_order=''
        )
        with open(os.path.join(new_path, 'properties', 'properties.yml'), 'w', encoding='utf8') as propertyfile:
            yaml.dump(properties, propertyfile, default_flow_style=False, allow_unicode=True)


def read_log(database):

    start_func = time()

    """ From the log export file of the import software, the data base (here the current project) is loaded with
    the tags"""

    raw_data_folder = os.path.relpath(os.path.join(database.folder, 'data', 'raw_data'))

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

    # Default tags stored
    config = Config()
    default_tags = config.getDefaultTags()
    import_tags = []
    import_tags_names = []
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

            database.addScan(file_name, original_md5) # Scan added to the Database
            scans_added.append([file_name, original_md5]) # Scan added to history

            # We create the tag FileName
            database.addValue(file_name, "FileName", utils.table_to_database(file_name, TAG_TYPE_STRING), None) # FileName tag added
            values_added.append([file_name, "FileName", utils.table_to_database(file_name, TAG_TYPE_STRING)])

            #start_time = time()

            # For each tag in each scan
            for tag in getJsonTagsFromFile(file_name, path_name): # For each tag of the scan

                # We do the tag only if it's not in the tags to remove
                if tag[0] not in tags_to_remove:
                    properties = tag[1]
                    unit = None
                    format = ''
                    type = TAG_TYPE_STRING
                    description = None
                    if isinstance(properties, dict):
                        value = properties['value']
                        unit = properties['units']
                        if unit == "":
                            unit = None
                        format = properties['format']
                        type = properties['type']
                        if type == "":
                            type = TAG_TYPE_STRING
                        description = properties['description']
                        if description == "":
                            description = None
                    else:
                        value = properties[0]

                    value = str(value) # Value list converted in str

                    # We have to put Json_Version tag value to list
                    if tag[0] == "Json_Version":
                        value = "['" + value + "']"

                    # We only accept the value if it's not empty or null
                    if value is not None and utils.database_to_table(value) is not "":
                        database.addValue(file_name, tag[0], value, value) # Value added to the Database
                        values_added.append([file_name, tag[0], value]) # Value added to history

                        if not tag[0] in import_tags_names:
                            import_tags.append([tag[0], type, unit, description])
                            import_tags_names.append(tag[0])

            #print("Loop --- %s seconds ---" % (time() - start_time))

    ui_progressbar.close()

    # Progressbar
    len_tags = len(import_tags)
    ui_progressbar = QProgressDialog("Importing tags in database", "Cancel", 0, len_tags)
    ui_progressbar.setWindowModality(Qt.WindowModal)
    ui_progressbar.setWindowTitle("")
    idx = 0

    # Tags added to the Database
    for tag in import_tags:

        # Progressbar
        idx += 1
        ui_progressbar.setValue(idx)
        if ui_progressbar.wasCanceled():
            break

        #start_time = time()

        # Default tags are already in the Database with user origin
        tag_name = tag[0]
        tag_type = tag[1]
        tag_unit = tag[2]
        tag_description = tag[3]
        if database.hasTag(tag_name):
            tag_object = database.getTag(tag_name)
            tag_object.origin = TAG_ORIGIN_RAW
            tag_object.description = tag_description
            tag_object.unit = tag_unit
            tag_object.type = tag_type
        else:
            if tag_name in default_tags:
                database.addTag(tag_name, True, TAG_ORIGIN_RAW, tag_type, tag_unit, None, tag_description)
            else:
                database.addTag(tag_name, False, TAG_ORIGIN_RAW, tag_type, tag_unit, None, tag_description)

        #print("Tag --- %s seconds ---" % (time() - start_time))
    ui_progressbar.close()
    # start_time = time()
    # Missing values added thanks to default values
    for tag in database.getUserTags():
        for scan in scans_added:
            #loop_time = time()
            if tag.default is not None and not database.scanHasTag(scan[0], tag.tag):
                database.addValue(scan[0], tag.tag, tag.default, None)
            #print("Value added --- %s seconds ---" % (time() - loop_time))
    #print("Values added --- %s seconds ---" % (time() - start_time))

    # For history
    historyMaker.append(scans_added)
    historyMaker.append(values_added)
    database.undos.append(historyMaker)
    database.redos.clear()

    #print("total --- %s seconds ---" % (time() - start_func))

def verify_scans(database, path):
    # Returning the files that are problematic
    return_list = []
    for scan in database.getScans():

        file_name = scan.scan
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