import yaml
from os import path

class Config():
    
    def __init__(self):
        self.config = self.loadConfig()
    
    
    def loadConfig(self):
        with open("config/config.yml", 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                
    def saveConfig(self):
        with open('config/config.yml', 'w', encoding='utf8') as configfile:
            yaml.dump(self.config, configfile, default_flow_style=False, allow_unicode=True)
            
    def getPathToProjectsFolder(self):
        return self.config["paths"]["projects"]
    
    def getPathToProjectsDBFile(self):
        folder = self.getPathToProjectsFolder()
        return path.join(folder,'projects.json')
    
    def setPathToData(self,path):
        if(path is not None and path != ''):
            self.config["paths"]["data"] = path
            #Then save the modification
            self.saveConfig()