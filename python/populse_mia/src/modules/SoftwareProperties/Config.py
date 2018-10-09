##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

'''
Created on 14 déc. 2017

@author: omonti
'''

import os
import yaml


class Config:

    def __init__(self):
        self.config = self.loadConfig()

    def loadConfig(self):
        with open(os.path.join('..', '..', 'properties', 'config.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                
    def saveConfig(self):
        with open(os.path.join('..', '..', 'properties', 'config.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.config, configfile, default_flow_style=False, allow_unicode=True)
            
    def getPathToProjectsFolder(self):
        return self.config["paths"]["projects"]
    
    def getPathData(self):
        return self.config["paths"]["data"]
    
    def getPathToProjectsDBFile(self):
        folder = self.getPathToProjectsFolder()
        return os.path.join(folder,'projects.json')
    
    def setPathToData(self,path):
        if(path is not None and path != ''):
            self.config["paths"]["data"] = path
            #Then save the modification
            self.saveConfig()

    def isAutoSave(self):
        return self.config["auto_save"]

    def setAutoSave(self, save):
        self.config["auto_save"] = save
        #Then save the modification
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
        if self.config["use_spm"] == "yes":
            return '{0}/run_spm12.sh {1}/ script'.format(self.config["spm"], self.config["matlab"])
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
