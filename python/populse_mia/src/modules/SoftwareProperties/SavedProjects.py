import os

import yaml


class SavedProjects:

    def __init__(self):
        self.savedProjects = self.loadSavedProjects()
        self.maxProjects = 5
        self.pathsList = self.savedProjects["paths"]
        if self.pathsList is None:
            self.pathsList = []

    def loadSavedProjects(self):
        with open(os.path.join('..', '..', 'properties', 'saved_projects.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def saveSavedProjects(self):
        with open(os.path.join('..', '..', 'properties', 'saved_projects.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.savedProjects, configfile, default_flow_style=False, allow_unicode=True)

    def addSavedProject(self, newPath):
        if self.pathsList:
            if newPath not in self.pathsList:
                self.pathsList.insert(0, newPath)
                #self.pathsList = self.pathsList[:self.maxProjects]
            elif newPath != self.pathsList[0]:
                self.pathsList.remove(newPath)
                self.pathsList.insert(0, newPath)
                #self.pathsList = self.pathsList[:self.maxProjects]
        else:
            self.pathsList.insert(0, newPath)
        self.savedProjects["paths"] = self.pathsList
        self.saveSavedProjects()
        return self.pathsList

    def getList(self):
        return self.savedProjects["paths"]