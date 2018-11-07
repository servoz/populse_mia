##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import yaml
from populse_mia.software_properties.config import Config


class SavedProjects:
    """
    Class that handles all the projects that have been saved in the software

    Attributes:
        - savedProjects: dictionary of all the saved projects
        - maxProjects: maximum projects to display in the "See all project" menu
        - pathsList: list of all the saved projects

    Methods:
        - loadSavedProjects: loads the dictionary from the saved_projects.yml file
        - saveSavedProjects: saves the dictionary to the saved_projects.yml file
        - addSavedProject: adds a new saved project
        - removeSavedProject: removes a saved project from the config file
        - getList: returns the list of the saved projects
    """

    def __init__(self):
        self.savedProjects = self.loadSavedProjects()
        self.maxProjects = 5
        self.pathsList = self.savedProjects["paths"]
        if self.pathsList is None:
            self.pathsList = []

    def loadSavedProjects(self):
        """
        Loads the dictionary from the saved_projects.yml file

        :return: the dictionary
        """
        config = Config()
        with open(os.path.join(config.get_mia_path(), 'properties', 'saved_projects.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def saveSavedProjects(self):
        """
        Saves the dictionary to the saved_projects.yml file
        """
        config = Config()
        with open(os.path.join(config.get_mia_path(), 'properties', 'saved_projects.yml'), 'w', encoding='utf8') \
                as configfile:
            yaml.dump(self.savedProjects, configfile, default_flow_style=False, allow_unicode=True)

    def addSavedProject(self, newPath):
        """
        Adds a new saved project

        :param newPath: new project's path to add
        :return: the new path's list
        """
        if self.pathsList:
            if newPath not in self.pathsList:
                self.pathsList.insert(0, newPath)
            elif newPath != self.pathsList[0]:
                self.pathsList.remove(newPath)
                self.pathsList.insert(0, newPath)
        else:
            self.pathsList.insert(0, newPath)
        self.savedProjects["paths"] = self.pathsList
        self.saveSavedProjects()
        return self.pathsList

    def removeSavedProject(self, path):
        """
        Removes a saved project from the config file

        :param path: path of the saved project to remove
        """

        if path in self.savedProjects["paths"]:
            self.savedProjects["paths"].remove(path)

        self.saveSavedProjects()

    def getList(self):
        """
        Returns the list of the saved projects

        :return: the list of the saved projects
        """
        return self.savedProjects["paths"]
