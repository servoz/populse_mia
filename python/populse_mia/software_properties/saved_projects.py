# -*- coding: utf-8 -*- #
"""Module that contains the class to handle the projects saved in the software.

Contains:
    Class:
    - SavedProjects

"""

##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import yaml

# Populse_MIA imports
from populse_mia.utils.utils import verCmp
from populse_mia.software_properties.config import Config


class SavedProjects:
    
    """Class that handles all the projects that have been saved in the software.

    Attributes:
        - savedProjects: dictionary of all the saved projects
        - pathsList: list of all the saved projects

    Methods:
        - addSavedProject: adds a new saved project
        - loadSavedProjects: loads the dictionary from the saved_projects.yml
        file
        - saveSavedProjects: saves the dictionary to the saved_projects.yml
        file
        - removeSavedProject: removes a saved project from the config file

    """

    def __init__(self):
        """Initialise the savedProjects attribute from the saved_projects.yml
           file.

        The pathsList attribute is initialised as the value correponding to 
        the "paths" key in the savedProjects dictionary.

        """
        self.savedProjects = self.loadSavedProjects()

        if ((isinstance(self.savedProjects, dict)) and
            ('paths' in self.savedProjects)):
            self.pathsList = self.savedProjects["paths"]
            
            if self.pathsList is None:
                self.pathsList = []

        else:
            self.savedProjects = {"paths" : []}
            self.pathsList = []

    def addSavedProject(self, newPath):
        """Add a new project to save in the savedProjects and pathsList
           attributes.

        Finally, save the savedProjects attribute in the saved_projects.yml
        file.

        :param newPath: new project's path to add

        :returns: the new path's list (pathsList attribute)

        """""
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

    def loadSavedProjects(self):
        """Load the savedProjects dictionary from the saved_projects.yml file.

        If the saved_projects.yml file is not existing, it is created with the
        "{paths: []}" value and the returned dictionnary is {paths: []}.

        :returns: the dictionary

        """
        config = Config()

        try:
            
            with open(os.path.join(config.get_mia_path(), 'properties',
                               'saved_projects.yml'), 'r') as stream:
                
                try:
                    if verCmp(yaml.__version__, '5.1', 'sup'):
                        return yaml.load(stream, Loader=yaml.FullLoader)
                    else:    
                        return yaml.load(stream)
            
                except yaml.YAMLError as exc:
                    print(exc)

        except FileNotFoundError as exc:
            
            with open(os.path.join(config.get_mia_path(), 'properties',
                                   'saved_projects.yml'), 'w') as stream:
                yaml.dump({'paths' : []}, stream, default_flow_style=False)

                return {'paths' : []}

    def saveSavedProjects(self):
        """Saves the savedProjects dictionary to the saved_projects.yml file.

        """
        config = Config()
        
        with (open(os.path.join(config.get_mia_path(), 'properties',
                                'saved_projects.yml'), 'w', encoding='utf8')
              ) as configfile:
            yaml.dump(self.savedProjects, configfile,
                      default_flow_style=False, allow_unicode=True)

    def removeSavedProject(self, path):
        """Removes a saved project from the saved_projects.yml file.

        :param path: path of the saved project to remove

        """

        if path in self.savedProjects["paths"]:
            self.savedProjects["paths"].remove(path)

        self.saveSavedProjects()

