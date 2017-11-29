import sys
import json
import glob
import os.path
import shutil
from models.projectModels import * 
from utils.enums import TagType
from utils import utils
from utils import jsonTools
from collections import namedtuple
import nibabel as nib

class ProjectController():
    
    def __init__(self,config):
        #set the config
        self.config = config
        #self.parent = parent
        #self.projectModel = ProjectModel(self) # initializes the model containing all data
        #self.view = MyView(self)  #initializes the view
        self.projects = self.loadExistingProjectsList()
        self.activeProject = None
 
        #initialize properties in view, if any
        pass
 
        #initalize properties in model, if any
        pass
     

    #Class used to load the lst of existing project in the app

    def loadExistingProjectsList(self):
        result = []
        projectsPath = self.config.getPathToProjectsDBFile();
        if os.path.exists(projectsPath) and os.stat(projectsPath).st_size != 0:
            with open(projectsPath, "r", encoding="utf-8") as projects:
                result = json.load(projects, object_hook=jsonTools.deserializer)
        return result
        
    def saveExistingProjectsList(self):
        #get folder and file name in config and load list from json file
        projectsPath = self.config.getPathToProjectsDBFile();
        with open(projectsPath, 'w') as f:
            f.write(json.dumps(self.projects, default=jsonTools.serializer))
        

    def loadProject(self,uid):
        #Get the project from existing project list
        for project in self.projects:
            if project.uid == uid:
                #Assemble project folder and project bdd_file
                if os.path.exists(project.bdd_file):
                    with open(project.bdd_file, "r", encoding="utf-8") as projectData:
                        self.activeProject = json.load(projectData, object_hook=jsonTools.deserializer)
                    
    def createProject(self, name, project_data_destination):
        #Check if project with this name alreayd exists
        projectLight = None
        if self.checkProjectNameAlreadyExists(name):
            #then set the view message that project already exist
            print('A project with that name already exists')
            self.view.setLabelError('A project with that name already exists')
        else:
            projectLight = ProjectLight(name)
            #Set project db file and project structure
            self.createProjectDatabase(projectLight)
            #If no project data destination, then project data is in the same folder as MIA program
            if project_data_destination is None or project_data_destination == "": project_data_destination = os.path.join(self.config.getPathToProjectsFolder(),utils.cleanStringForSysName(projectLight.name))
            self.createProjectDataStructure(projectLight,project_data_destination)
            #Add Project to existing ProjectList
            self.projects.append(projectLight)            
            #Save new project into dedictated db file
            try:
                self.saveExistingProjectsList()
            except:
                print("Error while saving project into "+str(self.config.getPathToProjectsDBFile())+" "+str(sys.exc_info()[0]))
            #Cast the projectlight to project
            project = Project(projectLight.name)
            project = castFromProjectLight(project,projectLight)
            #Set create project as current project
            self.activeProject = project
    
    def checkProjectNameAlreadyExists(self,name):
        for project in self.projects:
            if project.name == name: return True
        return False     
    
    def createProjectDatabase(self,project):
        #Remove spaces and strange caracters
        name = utils.cleanStringForSysName(project.name)
        #Get the path where to save project database
        project_path = os.path.join(self.config.getPathToProjectsFolder(),name)
        #create the project folder and the project database file in MIA2
        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path)
                #create project db file
                project.bdd_file = os.path.join(project_path, utils.createJsonFile(project_path, name))
            except:
                self.view.setLabelError("Oops!  There was an error creating project db file: "+os.path.abspath(project_path))
                print("Error in create project db file "+sys.exc_info()[0])
    
    def createProjectDataStructure(self,project,dest_data_folder):
        project_cleaned_name = utils.cleanStringForSysName(project.name)
        #Then create the project data structure according to dest_data_folder given
        if not os.path.exists(dest_data_folder):
            self.view.setLabelError("Given destination folder do not exists")
        else:
            #Create parent folder as projectName_data
            try:
                project.folder = os.path.join(os.path.abspath(dest_data_folder), project_cleaned_name+'_data')
                os.makedirs(project.folder)
                project.raw_data = os.path.join(os.path.abspath(project.folder), 'raw_data')
                os.makedirs(project.raw_data)
                project.processed_data = os.path.join(os.path.abspath(project.folder), 'processed_data')
                os.makedirs(project.processed_data)
            except:
                self.view.setLabelError("Oops!  There was an error creating project structure: "+os.path.abspath(dest_data_folder))
                print("Error in create project structure "+sys.exc_info()[0])
    
   
    '''
    The point is to check for newly copied files into the project raw data folder
    If corresponding scans do not exists, then add them to the project
    '''
    def updateProjectScans(self):
        scans = []
        json_files = utils.getFilesFromFolder(self.activeProject.raw_data,'json')
        nifti_files = utils.getFilesFromFolder(self.activeProject.raw_data,'nii')
    
        checkNiftis = utils.substractLists(json_files, nifti_files)
        checkJsons = utils.substractLists(nifti_files, json_files)
    
        if checkNiftis or checkJsons:
            for missing_nifti in checkNiftis:
                #Set the view with error message
                self.view.setLabelError(missing_nifti, " no nii corresponding file")
                json_files.remove(missing_nifti)
            for missing_json in checkJsons:
                self.view.setLabelError(missing_json, " no json corresponding file")
                nifti_files.remove(missing_json)
            
        for json_file in json_files:
            exists = False
            for scan in self.activeProject._get_scans():
                if json_file == scan.file_path: exists = True
            
            if not exists : scans.append(self.instanciateScanFromFile(json_file))
        #Then append scans to the project
        self.activeProject._get_scans().extend(scans)
    
    def instanciateScanFromFile(self,file_path):
        scan = Scan(file_path)
        for nii_tag in self.getNiftiTagsFromFile(file_path):
            scan.addNiftiTag(nii_tag)
        for json_tag in self.getJsonTagsFromFile(file_path):
            scan.addJsonTag(json_tag)
        return scan
    
    def getAllTags(self,item):
        result = []
        if(isinstance(item, Project) or isinstance(item, Scan)):
            result.extend(item.getAllTags())
        return result
        
    def getAllTagsByOrigin(self,item,origin):
        result = []
        if(isinstance(item, Project) or isinstance(item, Scan)):
            result.extend(item.getAllTagsByOrigin(origin))
        return result
    
    def getAllTagsNames(self,item):
        result = []
        if(isinstance(item, Project) or isinstance(item, Scan)):
            result.extend(item.getAllTagsNames())
        return result
    
    def getAllTagsNamesByOrigin(self,item, origin):
        result = []
        if(isinstance(item, Project) or isinstance(item, Scan)):
            result.extend(item.getAllTagsNamesByOrigin(origin))
        return result
      
    
    def checkListContains(self,listA,listB):
        return list(set(listA) - set(listB))
    
    def getNiftiTagsFromFile(self,file_path):
        nifti_tags = []
        for name, value in nib.load(file_path + ".nii").header.items():
            tag = Tag(name, '_', value, origin=TagType.NIFTI)
            nifti_tags.append(tag)
        return nifti_tags
    
    def getJsonTagsFromFile(self,file_path):
        json_tags = []
        with open(file_path + ".json") as f:
            for name,value in json.load(f).items():
                if value is None:
                    value = ""
                tag = Tag(name, '_', value, origin=TagType.JSON)
                json_tags.append(tag)
        return json_tags
        
    def saveProjectToFile(self):
        utils.saveProjectAsJsonFile(self.activeProject)
    
    
    def getAllTagsFile(self,path_file, project):
        list_tag = []
        for p_scan in project._get_scans():
            if p_scan.file_path == path_file:
                for n_tag in p_scan._get_tags():
                    if n_tag.name not in list_tag:
                        list_tag.append(n_tag.name)
                    else:
                        pass
        return list_tag
    
    def addTag(self,item,tagtype,tag):
        if(isinstance(item, Project) or isinstance(item, Scan)):
            item.addTag(tagtype,tag)
        
    def updateTagName(self,item,tag_name,new_name):
        if(isinstance(item, Project) or isinstance(item, Scan)):
            item.updateTagName(tag_name,new_name)
        
    def updateTagValue(self,item,tag_name,new_value):
        if(isinstance(item, Project) or isinstance(item, Scan)):
            item.updateTagValue(tag_name,new_value)
        
    def deleteTag(self,item,tag):
        if(isinstance(item, Project) or isinstance(item, Scan)):
            item.deleteTag(tag)
    
    