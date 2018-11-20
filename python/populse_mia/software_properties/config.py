##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import yaml


class Config:
    """
    Object that handles the configuration of the software

    Attributes:
        - config: dictionary containing the several elements of the config

    Methods:
        - loadConfig: reads the config in the config.yml file
        - saveConfig: saves the config to the config.yml file
        - getPathToProjectsFolder: returns the project's path
        - getPathData: returns the data's path
        - getPathToProjectsDBFile: returns the already-saved projects's path
        - setPathToData: sets the data's path
        - isAutoSave: checks if auto-save mode is activated
        - setAutoSave: sets the auto-save mode
        - getBackgroundColor: returns the background color
        - setBackgroundColor: sets the background color
        - getTextColor: return the text color
        - setTextColor: sets the text color
        - getShowAllSlices: returns if the "show all slices" checkbox of the mini viewer is activated
        - setShowAllSlices: sets the "show all slices" checkbox of the mini viewer
        - getNbAllSlicesMax: returns the maximum number of slices to display in the mini viewer
        - setNbAllSlicesMax: sets the maximum number of slices to display in the mini viewer
        - getThumbnailTag: returns the tag that is displayed in the mini viewer
        - setThumbnailTag: sets the tag that is displayed in the mini viewer
        - getChainCursors: returns if the "chain cursors" checkbox of the mini viewer is activated
        - setChainCursors: sets the "chain cursors" checkbox of the mini viewer
        - get_opened_projects: returns the opened projects
        - set_opened_projects: sets the opened projects
        - get_matlab_path: returns the path of Matlab's executable
        - set_matlab_path: sets the path of Matlab's executable
        - get_matlab_standalone_path: returns the path of Matlab Compiler Runtime
        - set_matlab_standalone_path: sets the path of Matlab Compiler Runtime
        - get_spm_path: returns the path of SPM12 (license version)
        - set_spm_path: sets the path of SPM12 (license version)
        - get_spm_standalone_path: returns the path of SPM12 (standalone version)
        - set_spm_standalone_path: sets the path of SPM12 (standalone version)
        - get_matlab_command: returns Matlab command
        - set_use_spm: sets the value of "use spm" checkbox in the preferences
        - get_use_spm: returns the value of "use spm" checkbox in the preferences
        - set_use_spm_standalone: sets the value of "use spm standalone" checkbox in the preferences
        - get_use_spm_standalone: returns the value of "use spm standalone" checkbox in the preferences
        - set_use_matlab: sets the value of "use matlab" checkbox in the preferences
        - get_use_matlab: returns the value of "use matlab" checkbox in the preferences
        - set_clinical_mode: sets the value of "clinical mode" checkbox in the preferences
        - get_clinical_mode: returns the value of "clinical mode" checkbox in the preferences
        - set_projects_save_path: sets the folder where the projects are saved
        - get_projects_save_path: returns the folder where the projects are saved
        - set_max_projects: sets the maximum number of projects displayed in the "Saved projects" menu
        - get_max_projects: returns the maximum number of projects displayed in the "Saved projects" menu
        - set_mia_path: sets the software's install path
        - get_mia_path: returns the software's install path
        - set_mri_conv_path: sets the MRIManager.jar path
        - get_mri_conv_path: sets the MRIManager.jar path
    """

    def __init__(self):
        self.config = self.loadConfig()
        if "mia_path" not in self.config.keys():
            self.config["mia_path"] = self.get_mia_path()
            self.saveConfig()

    def loadConfig(self):
        with open(os.path.join(self.get_mia_path(), 'properties', 'config.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def saveConfig(self):
        with open(os.path.join(self.get_mia_path(), 'properties', 'config.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.config, configfile, default_flow_style=False, allow_unicode=True)
            
    def getPathToProjectsFolder(self):
        return self.config["paths"]["projects"]
    
    def getPathData(self):
        return self.config["paths"]["data"]
    
    def getPathToProjectsDBFile(self):
        folder = self.getPathToProjectsFolder()
        return os.path.join(folder, 'projects.json')
    
    def setPathToData(self,path):
        if path is not None and path != '':
            self.config["paths"]["data"] = path
            # Then save the modification
            self.saveConfig()

    def isAutoSave(self):
        return self.config["auto_save"]

    def setAutoSave(self, save):
        self.config["auto_save"] = save
        # Then save the modification
        self.saveConfig()

    def getBackgroundColor(self):
        return self.config["background_color"]

    def setBackgroundColor(self, color):
        self.config["background_color"] = color
        # Then save the modification
        self.saveConfig()

    def getTextColor(self):
        return self.config["text_color"]

    def setTextColor(self, color):
        self.config["text_color"] = color
        # Then save the modification
        self.saveConfig()

    def getShowAllSlices(self):
        return self.config["show_all_slices"]

    def setShowAllSlices(self, show_all_slices):
        self.config["show_all_slices"] = show_all_slices
        # Then save the modification
        self.saveConfig()

    def getNbAllSlicesMax(self):
        return self.config["nb_slices_max"]

    def setNbAllSlicesMax(self, nb_slices_max):
        self.config["nb_slices_max"] = nb_slices_max
        # Then save the modification
        self.saveConfig()

    def getThumbnailTag(self):
        return self.config["thumbnail_tag"]

    def setThumbnailTag(self, thumbnail_tag):
        self.config["thumbnail_tag"] = thumbnail_tag
        # Then save the modification
        self.saveConfig()

    def getChainCursors(self):
        return self.config["chain_cursors"]

    def setChainCursors(self, chain_cursors):
        self.config["chain_cursors"] = chain_cursors
        # Then save the modification
        self.saveConfig()

    def get_opened_projects(self):
        return self.config["opened_projects"]

    def set_opened_projects(self, new_projects):
        self.config["opened_projects"] = new_projects
        # Then save the modification
        self.saveConfig()

    def get_matlab_path(self):
        try:
            return self.config["matlab"]
        except KeyError:
            return ""

    def set_matlab_path(self, path):
        self.config["matlab"] = path
        # Then save the modification
        self.saveConfig()

    def get_matlab_standalone_path(self):
        try:
            return self.config["matlab_standalone"]
        except KeyError:
            return ""

    def set_matlab_standalone_path(self, path):
        self.config["matlab_standalone"] = path
        # Then save the modification
        self.saveConfig()

    def get_spm_path(self):
        try:
            return self.config["spm"]
        except KeyError:
            return ""

    def set_spm_path(self, new_projects):
        self.config["spm"] = new_projects
        # Then save the modification
        self.saveConfig()

    def get_spm_standalone_path(self):
        try:
            return self.config["spm_standalone"]
        except KeyError:
            return ""

    def set_spm_standalone_path(self, new_projects):
        self.config["spm_standalone"] = new_projects
        # Then save the modification
        self.saveConfig()

    def get_matlab_command(self):
        if self.config["use_spm_standalone"] == "yes":
            return '{0}'.format(self.config["spm_standalone"]) + os.sep + \
                   'run_spm12.sh {0}'.format(self.config["matlab_standalone"]) + os.sep + ' script'
        elif self.config["use_matlab"] == "yes":
            return self.config["matlab"]
        else:
            return None

    def set_use_spm(self, use_spm):
        self.config["use_spm"] = use_spm
        # Then save the modification
        self.saveConfig()

    def get_use_spm(self):
        try:
            return self.config["use_spm"]
        except KeyError:
            return "no"

    def set_use_spm_standalone(self, use_spm_standalone):
        self.config["use_spm_standalone"] = use_spm_standalone
        # Then save the modification
        self.saveConfig()

    def get_use_spm_standalone(self):
        try:
            return self.config["use_spm_standalone"]
        except KeyError:
            return "no"

    def set_use_matlab(self, use_matlab):
        self.config["use_matlab"] = use_matlab
        # Then save the modification
        self.saveConfig()

    def get_use_matlab(self):
        try:
            return self.config["use_matlab"]
        except KeyError:
            return "no"

    def set_clinical_mode(self, clinical_mode):
        self.config["clinical_mode"] = clinical_mode
        # Then save the modification
        self.saveConfig()

    def get_clinical_mode(self):
        try:
            return self.config["clinical_mode"]
        except KeyError:
            return "yes"

    def set_projects_save_path(self, path):
        self.config["projects_save_path"] = path
        # Then save the modification
        self.saveConfig()

    def get_projects_save_path(self):
        try:
            return self.config["projects_save_path"]
        except KeyError:
            if not os.path.isdir(os.path.join(self.get_mia_path(), 'projects')):
                os.mkdir(os.path.join(self.get_mia_path(), 'projects'))
            return os.path.join(self.get_mia_path(), 'projects')

    def set_max_projects(self, max_projects):
        self.config["max_projects"] = max_projects
        # Then save the modification
        self.saveConfig()

    def get_max_projects(self):
        try:
            return float(self.config["max_projects"])
        except KeyError:
            return 5.0

    def set_mia_path(self, path):
        self.config["mia_path"] = path
        # Then save the modification
        self.saveConfig()

    def get_mia_path(self):
        # During the installation, the mia path is stored in the user's .populse_mia folder in configuration.yml
        dot_mia_config = os.path.join(os.path.expanduser("~"), ".populse_mia", "configuration.yml")
        if os.path.isfile(dot_mia_config):
            with open(dot_mia_config, 'r') as stream:
                try:
                    mia_home_config = yaml.load(stream)
                    if "dev_mode" in mia_home_config.keys() and mia_home_config["dev_mode"] == "yes":
                        return os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', '..'))

                    return mia_home_config["mia_path"]
                except yaml.YAMLError:
                    return os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', '..'))
                except KeyError:
                    return os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', '..'))
        else:
            try:
                return self.config["mia_path"]
            except KeyError:
                return os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', '..'))
            except AttributeError:
                return os.path.abspath(os.path.join(os.path.realpath(__file__), '..', '..', '..', '..'))

    def set_mri_conv_path(self, path):
        self.config["mri_conv_path"] = path
        # Then save the modification
        self.saveConfig()

    def get_mri_conv_path(self):
        try:
            return self.config["mri_conv_path"]
        except KeyError:
            return ""
        except AttributeError:
            return ""
