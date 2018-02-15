from os import path

import yaml


class RecentProjects:

    def __init__(self):
        self.recentProjects = self.loadRecentProjects()
        self.maxProjects = 5
        self.pathsList = self.recentProjects["paths"]
        if self.pathsList is None:
            self.pathsList = []

    def loadRecentProjects(self):
        with open("recent_projects.yml", 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def saveRecentProjects(self):
        with open('recent_projects.yml', 'w', encoding='utf8') as configfile:
            yaml.dump(self.recentProjects, configfile, default_flow_style=False, allow_unicode=True)

    def addRecentProject(self, newPath):
        if self.pathsList:
            if newPath not in self.pathsList:
                self.pathsList.insert(0, newPath)
                self.pathsList = self.pathsList[:self.maxProjects]
            elif newPath != self.pathsList[0]:
                self.pathsList.remove(newPath)
                self.pathsList.insert(0, newPath)
                self.pathsList = self.pathsList[:self.maxProjects]
        else:
            self.pathsList.insert(0, newPath)
        self.recentProjects["paths"] = self.pathsList
        self.saveRecentProjects()
        return self.pathsList

    def getList(self):
        return self.recentProjects["paths"]