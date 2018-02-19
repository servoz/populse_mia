'''
Created on 14 déc. 2017

@author: omonti
'''

from os import path

import yaml


class Config():
    
    def __init__(self):
        self.config = self.loadConfig()
        
    def loadConfig(self):
        with open("config.yml", 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                
    def saveConfig(self):
        with open('config.yml', 'w', encoding='utf8') as configfile:
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