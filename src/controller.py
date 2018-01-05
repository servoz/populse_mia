import glob
import os.path
import json
import nibabel as nib
from models import Tag, Scan, Project, serializer, deserializer
import utils
import shutil


def loadList(list, path):
    """

    :param list: a list of file paths
    :param path: the path of the project
    :return: the list of the file paths without extension
    """
    resultList = []
    for current in list:
        resultList.append(utils.getFilePathWithoutExtension(current, path))
    return resultList

def checkListContains(listA, listB):
    """

    :param listA: a list
    :param listB: a list
    :return: a list of the elements that are in listA and not in listB
    """
    return list(set(listA) - set(listB))

def getNiftiTagsFromFile(file_path, path):
    """

    :param file_path: file path of the Nifti file
    :param path: project path
    :return: a list of the Nifti tags of the file
    """
    nifti_tags = []
    for name, value in nib.load(path + file_path + ".nii").header.items():
        tag = Tag(name, '_', value, origin='Nifti')
        nifti_tags.append(tag)
    return nifti_tags

def getJsonTagsFromFile(file_path, path):
    """

        :param file_path: file path of the Json file
        :param path: project path
        :return: a list of the Json tags of the file
        """
    json_tags = []
    with open(path + file_path + ".json") as f:
        for name,value in json.load(f).items():
            if value is None:
                value = ""
            tag = Tag(name, '_', value, origin='Json')
            json_tags.append(tag)
    return json_tags


def loadScan(uid,file_path, path):
    """

    :param uid: uid
    :param file_path: name of the file
    :param path: path of the file
    :return: a scan object with the Nifti and Json tags of the file
    """
    scan = Scan(uid, file_path)
    for nii_tag in getNiftiTagsFromFile(file_path, path):
        scan.addNiftiTag(nii_tag)
    for json_tag in getJsonTagsFromFile(file_path, path):
        scan.addJsonTag(json_tag)
    return scan

def listdirectory(name, path):
    """

    :param name: project name
    :param path: project path
    :return: the corresponding Project object
    """
    absolute_path = os.path.abspath(path)
    # Getting the lists of all Json and Nifti files without extension to compare them
    json_files = loadList(glob.glob(absolute_path+'/**/*.json',  recursive=True), path)
    nifti_files = loadList(glob.glob(absolute_path + '/**/*.nii', recursive=True), path)

    # Checking if there is Json files that have no corresponding Nifti files
    checkNiftis = utils.substractLists(json_files, nifti_files)
    # Checking if there is Nifti files that have no corresponding Json files
    checkJsons = utils.substractLists(nifti_files, json_files)

    if checkNiftis or checkJsons:
        for missing_nifti in checkNiftis:
            print(missing_nifti, " no nii corresponding file")
            json_files.remove(missing_nifti)
        for missing_json in checkJsons:
            print(missing_json, " no json corresponding file")
            nifti_files.remove(missing_json)

    # Creating the Project object and adding the scans to it
    project = Project(name)
    uid = 1
    for json_file in json_files:
        project.addScan(loadScan(str(uid),json_file, path))
        uid+=1
    return project


def showResults(project):
    """
    Printing the several project parameters
    :param project: the current project object
    :return:
    """
    print(project.name)
    print(project.bdd_file)
    print(project.folder)
    print(project.date)
    for p_scan in project._get_scans():
        print("UID:"+p_scan.uid)
        print("file_path:" + p_scan.file_path)
        print("TAGS:")
        for n_tag in p_scan._get_tags():
            print("name:" + n_tag.name, "replace:" + n_tag.replace, "value:" + str(n_tag.value), "origin:" + n_tag.origin)


def createProject(name, path, parent_folder):
    """

    :param name: project name
    :param path: project path
    :param parent_folder:
    :return: the project object
    """
    # Instanciate project with name
    project = listdirectory(name, path)
    project.name = name
    # Formating the name to remove spaces et strange characters -> folder name
    name = utils.remove_accents((name.lower()).replace(" ", "_"))
    recorded_path = os.path.abspath(parent_folder)
    new_path = os.path.join(recorded_path, name)
    # Creating the folder with the folder name that has been formatted
    if not os.path.exists(new_path):
        project_parent_folder = os.makedirs(new_path)
        data_folder = os.makedirs(os.path.join(new_path, 'data'))
        #config_project_folder = os.makedirs(os.path.join(new_path, 'config_'+name))
        project_folder = os.makedirs(os.path.join(new_path, name))
        project_path = os.path.join(new_path, name)
        raw_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'raw_data'))
        treat_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'treat_data'))
        # si le repertoire a bien été créé, set l'attribut folder du projet avec ton folder name (j'ai ajouté le folder name à la classe projet)
        #setattr(Project, project.folder, name)  #pas sur du tout....
        project.folder = name
        project.bdd_file = path
        # créé un fichier json avec le même nom que le repertoire -> folder_name.json
        json_file_name = utils.createJsonFile("", name)
        json_file_name = utils.saveProjectAsJsonFile(name, project)
        shutil.move(name+'.json', project_path)
        # set l'attribut bdd_file de ton projet avec le nom de ce json
        # setattr(Project, project.bdd_file, json_file_name)
        #project.bdd_file = json_file_name
        # retourne l'objet Projet que tu viens de crééer'

        return project
    """else:
        print('This name of project already exists')
        name = input('Give a new name for this project : ')
        createProject(name, path)"""

"""def createProject(name, path):
    #instanciate project with name
    project = listdirectory(name, 'D :\data_nifti_json')
    project.name = name
    # formate le name pour virer espaces et caractère bizarres -> folder name
    name = utils.remove_accents((name.lower()).replace(" ", "_"))
    recorded_path = utils.findPath("controller")
    new_path = os.path.join(recorded_path, name)
    project_parent_folder = os.makedirs(new_path)
    data_folder = os.makedirs(os.path.join(new_path, 'data'))
    project_folder = os.makedirs(os.path.join(new_path, name))
    project_path = os.path.join(new_path, name)
    raw_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'raw_data'))
    treat_data_folder = os.makedirs(os.path.join(os.path.join(new_path, 'data'), 'treat_data'))
    # si le repertoire a bien été créé, set l'attribut folder du projet avec ton folder name (j'ai ajouté le folder name à la classe projet)
    # setattr(Project, project.folder, name)  #pas sur du tout....
    project.folder = name
    project.bdd_file = path
    # créé un fichier json avec le même nom que le repertoire -> folder_name.json
    json_file_name = utils.createJsonFile("", name)
    json_file_name = utils.saveProjectAsJsonFile(name, project)
    shutil.move(name + '.json', project_path)
    # set l'attribut bdd_file de ton projet avec le nom de ce json
    # setattr(Project, project.bdd_file, json_file_name)
    # project.bdd_file = json_file_name
    # retourne l'objet Projet que tu viens de crééer'

    return project"""



def open_project(name, path):
    """

    :param name: project name
    :param path: project path
    :return: the project object
    """
    path = os.path.abspath(path)
    if os.path.exists(path):
        project_path = os.path.join(path, name)
        file_path = os.path.join(project_path, name)
        with open(file_path+".json", "r", encoding="utf-8")as fichier:
            project = json.load(fichier, object_hook=deserializer)
        return project
    #else:
        #print("This name of project does not exist, try a new one")


def getAllTagsFile(path_file, project):
    """

    :param path_file: path of the scans
    :param project: the project object
    :return: a list of all the tags of the project of a certain scan file (path_file)
    """
    list_tag = []
    for p_scan in project._get_scans():
        if p_scan.file_path == path_file:
            for n_tag in p_scan._get_tags():
                if n_tag.name not in list_tag:
                    list_tag.append(n_tag.name)
                else:
                    pass
    return list_tag


def getAllTags(project):
    """

    :param project: the project object
    :return: a list of all the tags of the project
    """
    list_tag = []
    for p_scan in project._get_scans():
        for n_tag in p_scan._get_tags():
            if n_tag.name not in list_tag:
                list_tag.append(n_tag.name)
            else:
                pass
    return list_tag


def add_tag_with_value(tagName, value):
    """

    :param tagName: tag name
    :param value: value of the tag name
    :return:
    """
    Scan._tags.append(Tag(tagName, '_', value, 'custom'))

def modified_tag_value (project, tagName, newValue):
    """

    :param project: the project object
    :param tagName: tag name
    :param newValue: new value of the tag
    :return: the modified project object
    """
    for scan in project._get_scans():
        for n_tag in scan._get_tags():
            if n_tag.name == tagName:
                scan._tags.append(Tag(n_tag.name, '', newValue, 'custom'))
                break
            else:
                pass
    return project

def modified_tag_name(project, tagName, newName):
    """

    :param project: the project object
    :param tagName: tag name
    :param newName: new name of the tag
    :return: the modified project object
    """
    for scan in project._get_scans():
        for n_tag in scan._get_tags():
            if n_tag.name == tagName:
                scan._tags.append(Tag(newName, tagName, n_tag.value, 'custom'))
                break
            else:
                pass
    return project

"""test = listdirectory('test', 'D:\data_nifti_json')
print(showResults(test))"""
"""test = modified_tag_name(test, 'InversionTime', 'AAAAA')
print(showResults(test))
print(Project.getAllTagsNames(test))
print(type(test))"""
#print(listdirectory('D:\data_nifti_json'))
#print("le resultat est: ", getAllTagsFile("D:\\data_nifti_json\\1_Rat_M10_J15\\393217_03_pCASL\\1", listdirectory('D:\data_nifti_json')))
#print(len(getAllTagsFile("D:\\data_nifti_json\\1_Rat_M10_J15\\393217_03_pCASL\\1", listdirectory('D:\data_nifti_json'))))
#print("le resultat est: ", getAllTags(listdirectory('D:\data_nifti_json')))
#print(len(getAllTags(listdirectory('D:\data_nifti_json'))))
#print(len(listdirectory('D:\data_nifti_json')._get_scans()))

"""utils.saveJsonFile("Json1", listdirectory('D:\data_nifti_json'))
utils.findPath("json1.json")"""
#print(showResults(listdirectory('D:\data_nifti_json')))
#print(json.dumps(listdirectory('D:\data_nifti_json'), default=serializer))

#print(len((listdirectory('D:\data_nifti_json')).getAllTagsNames()))
#
#print(showResults(createProject('test4', 'D:\data_nifti_json', 'C:\\Users\Roxane\Desktop')))
#print(showResults(open_project('test4', 'C:\\Users\Roxane\Desktop\\test4')))


#createProject('ca_marche', 'D:\data_nifti_json')



#print(showResults(open_project('ca_marche', 'C:\\Users\Roxane\PycharmProjects\BDD\\test')))