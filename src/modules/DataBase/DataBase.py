from ProjectManager.models import Project

class DataBase():

    project = Project("")

    def createProject(name):
        global project
        project = Project(name)

    def setProjectFolder(folder):
        global project
        project.folder = folder