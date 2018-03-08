import glob
import os.path
import json
import Utils.utils as utils
import hashlib # To generate the md5 of each scan
from DataBase.DataBaseModel import TAG_ORIGIN_RAW, TAG_TYPE_STRING
from SoftwareProperties.Config import Config
import datetime
import yaml

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


def open_project(name, path):
    """

    :param name: project name
    :param path: project path
    :return: the project object
    """
    path = os.path.relpath(path)
    if os.path.exists(path):
        project_path = os.path.join(path, name)
        file_path = os.path.join(project_path, name)
        #with open(file_path+".json", "r", encoding="utf-8")as fichier:
            #project = json.load(fichier, object_hook=deserializer)

        #return project


def read_log(database):
    """ From the log export file of the import software, the data base (here the current project) is loaded with
    the tags"""

    raw_data_folder = os.path.relpath(os.path.join(database.folder, 'data', 'raw_data'))

    # Checking all the export logs from MRIManager and taking the most recent
    list_logs = glob.glob(os.path.join(raw_data_folder, "logExport*.json"))
    log_to_read = max(list_logs, key=os.path.getctime)

    with open(log_to_read, "r", encoding="utf-8") as file:
        list_dict_log = json.load(file)

    for dict_log in list_dict_log:
        if dict_log['StatusExport'] == "Export ok":
            file_name = dict_log['NameFile']
            path_name = raw_data_folder
            with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
                data = scan_file.read()
                original_md5 = hashlib.md5(data).hexdigest()
            #scan_to_add = loadScan(str(1), file_name, path_name, original_md5)
            #list_to_add = []
            #list_to_add.append(file_name)
            #tag_to_add = Tag("FileName", "", list_to_add, "Json", list_to_add)

            #### Database
            database.addScan(file_name, original_md5)
            database.addValue(file_name, "FileName", file_name, file_name)
            tag_already_in_database = False
            for database_tag in database.getTags():
                database_tag = database_tag.tag
                if ("FileName" == database_tag):
                    tag_already_in_database = True
            if not tag_already_in_database:
                config = Config()
                if ("FileName" in config.getDefaultTags()):
                    database.addTag("FileName", True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, '', '', '')
                else:
                    database.addTag("FileName", False, TAG_ORIGIN_RAW, TAG_TYPE_STRING, '', '', '')
            else:
                database.setTagOrigin("FileName", TAG_ORIGIN_RAW)
            for tag in getJsonTagsFromFile(file_name, path_name):
                database.addValue(file_name, tag[0], utils.check_tag_value(tag[1]), utils.check_tag_value(tag[1]))
                tag_already_in_database = False
                for database_tag in database.getTags():
                    database_tag = database_tag.tag
                    if(tag[0] == database_tag):
                        tag_already_in_database = True
                if not tag_already_in_database:
                    config = Config()
                    if(tag[0] in config.getDefaultTags()):
                        database.addTag(tag[0], True, TAG_ORIGIN_RAW, TAG_TYPE_STRING, '', '', '')
                    else:
                        database.addTag(tag[0], False, TAG_ORIGIN_RAW, TAG_TYPE_STRING, '', '', '')
                else:
                    database.setTagOrigin(tag[0], TAG_ORIGIN_RAW)

            #### Database

            """scan_to_add.addJsonTag(tag_to_add)
            project.addScan(scan_to_add)
            for tag in project.user_tags:
                user_tag_name = tag['name']
                for scan in project._get_scans():
                    if scan.file_path == file_name:
                        if user_tag_name not in scan.getAllTagsNames():
                            tag = Tag(user_tag_name, "", tag["original_value"], "custom", tag["original_value"])
                            scan.addCustomTag(tag)"""

def verify_scans(database, path):
    # Returning the files that are problematic
    return_list = []
    for scan in database.getScans():

        file_name = scan.scan
        path_name = os.path.relpath(os.path.join(path, 'data', 'raw_data'))

        with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
            data = scan_file.read()
            actual_md5 = hashlib.md5(data).hexdigest()

        if actual_md5 != scan.checksum:
            return_list.append(file_name)

    return return_list


def save_project(database):
    #project_path = os.path.join(database.folder, database.getName(), database.getName())
    #utils.saveProjectAsJsonFile(project_path, project)
    database.saveModifications()