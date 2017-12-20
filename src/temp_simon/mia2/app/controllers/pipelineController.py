from utils.enums import FilterOn
from utils.enums import FilterOperator
from utils import utils
from models.pipelineModels import Filter

class PipelineController():
    def __init__(self,config):
        #set the config
        self.config = config
        self.pipeline = None 
        #self.view = MyView(self)  #initializes the view
        #The view should only communicates with the controller, not with the models
        #So methods may seem duplicates but it's the way to do it
        #So when a model like tree operator updateSTatus, it tells the controller that will update the view accordingly for example
        #In models, the is no view, the controller does all the communication job
 
        #initialize properties in view, if any
        pass
 
        #initalize properties in model, if any
        pass
    
    def setPipeline(self,pipeline):
        self.pipeline = pipeline
    
    def loadPipeline(self, uid):
        pass
    
    def addLink(self,source,destination):
        self.pipeline.addLink(source,destination)
        
    def launchPipeline(self,inputs):#Get the selected inputs on which to launch pipeline
        print("Launching pipeline on "+str(len(inputs)))
        self.pipeline.execute(inputs)
        

def getFilteredScans(scans, filter):
    filteredScans = []
    for scan in scans:
        if(filter.filterOn == FilterOn.TAG):        
            #First check if tag  exists for current
            if(filter.name in scan.getAllTagsNames()):
                #Then check value if has value
                if(filter.value is not None):
                    for tag in scan.getAllTags():
                        if(tag.name == filter.name):
                            if(filter.isExactly):
                                if(filter.isCaseSensitive):
                                    if(utils.normalize_casewith(utils.cleanTagValue(tag.value)) == utils.normalize_casewith(filter.value)):
                                        if scan not in filteredScans: filteredScans.append(scan)
                                else:
                                    if(utils.normalize_caseless(utils.cleanTagValue(tag.value)) == utils.normalize_caseless(filter.value)):
                                        if scan not in filteredScans: filteredScans.append(scan)
                            else:
                                if(filter.isCaseSensitive):
                                    if(utils.normalize_casewith(utils.cleanTagValue(tag.value)) in utils.normalize_casewith(tag.value)):
                                        if scan not in filteredScans: filteredScans.append(scan)
                                else:
                                    if(utils.normalize_caseless(utils.cleanTagValue(tag.value)) in utils.normalize_caseless(tag.value)):
                                        if scan not in filteredScans: filteredScans.append(scan)
                else:
                    #direcltly add scan to results
                    if scan not in filteredScans: filteredScans.append(scan)
        if(filter.filterOn == FilterOn.ATTRIBUTE):
            if(filter.name == FilterOn.FILENAME):
                if(filter.isExactly):
                    if(filter.isCaseSensitive):
                        if(utils.normalize_casewith(scan.file_path) == utils.normalize_casewith(filter.value)):
                            if scan not in filteredScans: filteredScans.append(scan)
                    else:
                        if(utils.normalize_caseless(scan.file_path) == utils.normalize_caseless(filter.value)):
                            if scan not in filteredScans: filteredScans.append(scan)
                else:
                    if(filter.isCaseSensitive):
                        if(utils.normalize_casewith(scan.file_path) in utils.normalize_casewith(tag.value)):
                            if scan not in filteredScans: filteredScans.append(scan)
                    else:
                        if(utils.normalize_caseless(scan.file_path) in utils.normalize_caseless(tag.value)):
                            if scan not in filteredScans: filteredScans.append(scan)
                
    
    return filteredScans
    
#Will return a dictionnary with filter as key and scans as value
def groupScansBy(scans, filterGroupBy):
    groupedScans = dict()
    #If filterGroupOn has a value, then it is just a filter
    if(filterGroupBy.value is not None):
        groupedScans[filterGroupBy] = getFilteredScans(scans, filterGroupBy)    
    else:
        for scan in scans:
            if(filterGroupBy.filterOn == FilterOn.TAG):
                for tag in scan.getAllTags():
                    if tag.name == filterGroupBy.name:
                        #Set a temporary filter as key
                        keyFilter = Filter(filterGroupBy.filterOn, filterGroupBy.name, tag.value, filterGroupBy.isCaseSensitive, filterGroupBy.isExactly, FilterOperator.OR)
                        #check if it does not exists in groupedScans keys
                        if keyFilter not in groupedScans.keys():
                            groupedScans[keyFilter] = [scan]
                        else:
                            groupedScans.get(keyFilter).append(scan)
            if(filterGroupBy.filterOn == FilterOn.ATTRIBUTE):
                if(filterGroupBy.name == FilterOn.FILENAME):
                    #TODO if there is something to do
                    continue    
    #COunt groups            
    for key in groupedScans.keys():
        print('Size of group '+key.name+' '+str(len(groupedScans[key])))
    
    return groupedScans
    