import glob
import os.path
import json
import Utils.utils as utils
import hashlib # To generate the md5 of each scan
from DataBase.DataBaseModel import TAG_ORIGIN_RAW, TAG_TYPE_STRING, TAG_ORIGIN_USER
from SoftwareProperties.Config import Config
import datetime
import yaml
from time import time

def getJsonTagsFromFile(file_path, path):
   """
    :return:
    :param file_path: file path of the Json file
    :param path: project path
    :return: a list of the Json tags of the file"""
   json_tags = []
   with open(os.path.join(path, file_path) + ".json") as f:
       for name,value in json.load(f).items():
            if value is None:
                value = ""
            json_tags.append([name, value])
   return json_tags


def createProject(name, path, parent_folder):
    """

    :param name: project name
    :param path: project path
    :param parent_folder:
    :return: the project object
    """

    # Formating the name to remove spaces et strange characters -> folder name
    #name = utils.remove_accents(name.replace(" ", "_"))
    recorded_path = os.path.relpath(parent_folder)
    new_path = os.path.join(recorded_path, name)

    # Creating the folder with the folder name that has been formatted
    if not os.path.exists(new_path):
        project_parent_folder = os.makedirs(new_path)
        data_folder = os.makedirs(os.path.join(new_path, 'data'))
        #project_folder = os.makedirs(os.path.join(new_path, name))
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

        # Create a json file -> folder_name.json
        #json_file_name = utils.createJsonFile("", name)
        #json_file_name = utils.saveProjectAsJsonFile(name, project)
        #shutil.move(name+'.json', project_path)

        #return project


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

    for dict_log in list_dict_log:

        if dict_log['StatusExport'] == "Export ok":
            file_name = dict_log['NameFile']
            path_name = raw_data_folder
            with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
                data = scan_file.read()
                original_md5 = hashlib.md5(data).hexdigest()

            database.addScan(file_name, original_md5) # Scan added to the database
            scans_added.append([file_name, original_md5]) # Scan added to history

            # We create the tag FileName
            database.addValue(file_name, "FileName", file_name, file_name) # FileName tag added
            values_added.append([file_name, "FileName", file_name])

            start_time = time()

            # For each tag in each scan
            for tag in getJsonTagsFromFile(file_name, path_name): # For each tag of the scan

                value = utils.check_tag_value(tag[1])

                # We only accept the value if it's not empty
                if(value != ""):
                    database.addValue(file_name, tag[0], value, value) # Value added to the database
                    values_added.append([file_name, tag[0], value]) # Value added to history

                    if not tag[0] in import_tags:
                        import_tags.append(tag[0])

            print("--- %s seconds ---" % (time() - start_time))

    # Tags added to the database
    for tag in import_tags:
        # Default tags are already in the database with user origin
        if database.hasTag(tag):
            database.setTagOrigin(tag, TAG_ORIGIN_RAW)
        else:
            if tag in default_tags:
                database.addTag(tag, True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, '', '', '')
            else:
                database.addTag(tag, False, TAG_ORIGIN_RAW, TAG_TYPE_STRING, '', '', '')

    for tag in database.getUserTags():
        # We add the default value if it exists and no value to scan
        database.put_default_values(tag.tag)

    # For history
    historyMaker.append(scans_added)
    historyMaker.append(values_added)
    database.undos.append(historyMaker)
    database.redos.clear()

    print("--- %s seconds ---" % (time() - start_func))

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