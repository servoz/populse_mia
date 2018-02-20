import glob
import os.path
import json
import nibabel as nib
from ProjectManager.models import Tag, Scan, Project, serializer, deserializer
import Utils.utils as utils
import shutil
import hashlib # To generate the md5 of each scan
#from pop_ups import Ui_Dialog_Save_Project_As
#from PyQt5.QtWidgets import QDialog
#from MainWindow import Main_Window
#from RecentProjects import RecentProjects


def getJsonTagsFromFile(file_path, path):
    """

        :param file_path: file path of the Json file
        :param path: project path
        :return: a list of the Json tags of the file
        """
    json_tags = []
    with open(os.path.join(path, file_path) + ".json") as f:
        for name,value in json.load(f).items():
            if value is None:
                value = ""
            tag = Tag(name, '_', value, origin='Json', original_value=value)
            json_tags.append(tag)
    return json_tags


def loadScan(uid,file_path, path, original_md5):
    """

    :param uid: uid
    :param file_path: name of the file
    :param path: path of the file
    :return: a scan object with the Nifti and Json tags of the file
    """
    scan = Scan(uid, file_path, original_md5)

    for json_tag in getJsonTagsFromFile(file_path, path):
        scan.addJsonTag(json_tag)
    return scan


def createProject(name, path, parent_folder):
    """

    :param name: project name
    :param path: project path
    :param parent_folder:
    :return: the project object
    """
    # Instanciate project with name
    project = Project(name)
    project.name = name

    # Formating the name to remove spaces et strange characters -> folder name
    name = utils.remove_accents(name.replace(" ", "_"))
    recorded_path = os.path.relpath(parent_folder)
    new_path = os.path.join(recorded_path, name)

    # Creating the folder with the folder name that has been formatted
    if not os.path.exists(new_path):
        project_parent_folder = os.makedirs(new_path)
        data_folder = os.makedirs(os.path.join(new_path, 'data'))
        project_folder = os.makedirs(os.path.join(new_path, name))
        project_path = os.path.join(new_path, name)
        raw_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'raw_data'))
        derived_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'derived_data'))

        project.folder = new_path
        project.bdd_file = path

        # Create a json file -> folder_name.json
        json_file_name = utils.createJsonFile("", name)
        json_file_name = utils.saveProjectAsJsonFile(name, project)
        shutil.move(name+'.json', project_path)


        return project


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
        with open(file_path+".json", "r", encoding="utf-8")as fichier:
            project = json.load(fichier, object_hook=deserializer)

        return project


def read_log(project):
    """ From the log export file of the import software, the data base (here the current project) is loaded with
    the tags"""

    raw_data_folder = os.path.relpath(os.path.join(project.folder, 'data', 'raw_data'))

    # Checking all the export logs from MRIManager and taking the most recent
    list_logs = glob.glob(os.path.join(raw_data_folder, "logExport*.json"))
    log_to_read = max(list_logs, key=os.path.getctime)

    with open(log_to_read, "r", encoding="utf-8") as file:
        list_dict_log = json.load(file, object_hook=deserializer)

    for dict_log in list_dict_log:
        if dict_log['StatusExport'] == "Export ok":
            file_name = dict_log['NameFile']
            path_name = raw_data_folder
            with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
                data = scan_file.read()
                original_md5 = hashlib.md5(data).hexdigest()
            scan_to_add = loadScan(str(1), file_name, path_name, original_md5)
            list_to_add = []
            list_to_add.append(file_name)
            tag_to_add = Tag("FileName", "", list_to_add, "Json", list_to_add)
            scan_to_add.addJsonTag(tag_to_add)
            project.addScan(scan_to_add)
            for tag in project.user_tags:
                user_tag_name = tag['name']
                for scan in project._get_scans():
                    if scan.file_path == file_name:
                        if user_tag_name not in scan.getAllTagsNames():
                            tag = Tag(user_tag_name, "", tag["original_value"], "custom", tag["original_value"])
                            scan.addCustomTag(tag)


def verify_scans(project):
    # Returning the files that are problematic
    return_list = []
    for scan in project._get_scans():

        file_name = scan.file_path
        path_name = os.path.relpath(os.path.join(project.folder, 'data', 'raw_data'))

        with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
            data = scan_file.read()
            actual_md5 = hashlib.md5(data).hexdigest()

        if actual_md5 != scan.original_md5:
            return_list.append(file_name)

    return return_list


def save_project(project):
    project_path = os.path.join(project.folder, project.name, project.name)
    utils.saveProjectAsJsonFile(project_path, project)