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
        return path.join(folder,'projects.json')
    
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

    def addDefaultTag(self, tag):
        self.config["default_tags"].append(tag)
        #Then save the modification
        self.saveConfig()

    def removeDefaultTag(self, tag):
        self.config["default_tags"].remove(tag)
        #Then save the modification
        self.saveConfig()

    def getDefaultTags(self):
        return self.config["default_tags"]

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