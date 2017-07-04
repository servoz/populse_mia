from controllers.projectController import ProjectController
from config.config import Config 
from utils import utils
from shutil import copytree

print("RUNNING")

#Try to load the config
config = Config()
print('IS MY CONFIG NULL ? '+str(config))
#The instantiate the Project controller
projectController = ProjectController(config)
#display the list of existing projects
for project in projectController.projects:
    print('NAME '+project.name)
    print('FOLDER '+project.folder)
   
#Create a new Project
projectController.createProject("SimonTest",None)
#Copy raw data into projet raw data folder
#copytree("/home/sloury/workspace_neon/ProjectManager/myProject/nifti",projectController.activeProject.raw_data)
print("Copy raw data into project folder...")
utils.copytree("/home/sloury/workspace_neon/ProjectManager/myProject/nifti",projectController.activeProject.raw_data)
print("Copy raw data into project folder.... Done")
#Add scans to the project
print("Update project scans....")
projectController.updateProjectScans()
print("Update project scans.... Done with "+str(len(projectController.activeProject._get_scans()))+" scans added")
for scan in projectController.activeProject._get_scans():
    print("Scan file :"+scan.file_path)


print("Save project to db....")
projectController.saveProjectToFile()
print("Save project to db....Done")    
#Load the project from data
'''
projectController.loadProject('1')
print("selectedProject "+projectController.loadedProject.name)
for scan in projectController.loadedProject._get_scans():
    print("SCAN IS "+scan.uid)
    print("SCAN FILE IS "+scan.file_path)

'''



