from enum import Enum
from models.generics import GenericItem
from models.projectModels import Tag,Scan
from utils import utils
from utils.enums import OpStatus
from utils.enums import FilterOperator
from utils.enums import FilterOn


class Filter(GenericItem):
        
    def __init__(self, filterOn, name, value, isCaseSensitive, isExactly, operator):
        GenericItem.__init__(self)
        self.filterOn = filterOn #Enum element on which to filter (filename,tag, ...)
        self.name = name #Value on which to filter on
        self.value = value #Value on which to filter on
        self.isCaseSensitive = isCaseSensitive
        self.isExactly = isExactly #In opposition to contains
        self.operator = operator # Enum with AND or OR or NULL
    
    #Methods hash and eq are Mandatory for group by
    def __hash__(self):
        return hash(self.filterOn.value+self.name+self.value+str(self.isCaseSensitive)+str(self.isExactly)+str(self.operator.value))
        
    def __eq__(self, other):
        if(self.filterOn != other.filterOn): return False
        if(self.name != other.name): return False
        if(self.value != other.value): return False
        if(self.isCaseSensitive != other.isCaseSensitive): return False
        if(self.isExactly != other.isExactly): return False
        if(self.operator.value != other.operator.value): return False
        return True
        
    def matches(self,toBeMatched):
        if(self.filterOn == FilterOn.TAG):
            #First check if tag  exists for scan to be matched
            if(self.name in toBeMatched.getAllTagsNames()):
                #Then check value if has value
                if(self.value is not None):
                    for tag in toBeMatched.getAllTags():
                        if(tag.name == self.name):
                            if(self.isExactly):
                                if(self.isCaseSensitive):
                                    if(utils.normalize_casewith(utils.cleanTagValue(tag.value)) == utils.normalize_casewith(self.value)):
                                        return True
                                else:
                                    if(utils.normalize_caseless(utils.cleanTagValue(tag.value)) == utils.normalize_caseless(self.value)):
                                        return True                                        
                            else:
                                if(self.isCaseSensitive):
                                    if(utils.normalize_casewith(utils.cleanTagValue(tag.value)) in utils.normalize_casewith(tag.value)):
                                        return True
                                else:
                                    if(utils.normalize_caseless(utils.cleanTagValue(tag.value)) in utils.normalize_caseless(tag.value)):
                                        return True
        return False
            
    def execute(self):
        print("Loading filter on "+self.filterOn+" value "+self.value)


class TreeOperator(GenericItem):
    
    def __init__(self):
        GenericItem.__init__(self)
        self.status = OpStatus.PENDING #Enum(hold,completed,running,waiting,failed)
        self._inputFilters = [] #list of filterWithOperator in input of the operator
        self._outputFilters = [] #list of filterWithOperator in output of the operator
        self._previousTreeOperators = [] #List of uids of previous operators in the tree
        self._nextTreeOperators = [] #List of uids of previous operators in the tree

    def _get_inputFilters(self):
        return self._inputFilters
    
    def _get_outputFilters(self):
        return self._outputFilters
    
    def _get_previousTreeOperators(self):
        return self._previousTreeOperators

    def _get_nextTreeOperators(self):
        return self._nextTreeOperators
    
    #Gives a list of inputs, return a filtered list
    def filterInputs(self,inputs):
        filteredInputs = []
        #iterate on inputs and add them to list if it matches the filters
        for current in inputs:
            letThrough = []
            for opfilter in self._get_inputFilters():
                if(opfilter.matches(current)):
                    letThrough.append(True)
                else:
                    letThrough.append(False)
            #Depending on filters operator, we add it to inputs or not
            if False not in letThrough: filteredInputs.append(current)
        return filteredInputs
    
    def filterOutputs(self,outputs):
        filteredOutputs = []
        for current in outputs:
            letThrough = []
            for opfilterWO in self._get_inputFilters():
                if(opfilterWO.filter.matches(current)):
                    letThrough.append(True)
                else:
                    letThrough.append(False)
            if False not in letThrough: filteredOutputs.append(current)
        return filteredOutputs
      
    def getInputsScans(self):
        print('getInputsScans...')
        inputs = []
        if(isinstance(self, TreeIterator)):
            inputs.extend(self.treeOperator.getInputsScans())
        if(isinstance(self, TreeFilter)):
            for pc in self._get_pcListToFilter():
                inputs.extend(pc._get_inputScans())
        if(isinstance(self, TreePipeline)):
            inputs.extend(self.pipeline._get_inputScans())
        if(isinstance(self, TreeExecutor)):
            inputs.extend(self.module._get_inputScans())
        return inputs
         
    def getOutputsScansFromPreviousTreeOperator(self):
        print('getOutputsScansFromPreviousTreeOperator...')
        print('ids of previous operators :')
        for pv in self._get_previousTreeOperators():
            print('id : '+str(pv.uid))
        
        outputs = []
        for previous in self._get_previousTreeOperators():
            print('previous operator is '+str(previous.uid)+ ' is '+type(previous).__name__)
            if(isinstance(previous, TreeIterator)):
                outputs.extend(previous.getOutputsScansFromPreviousTreeOperator())
            if(isinstance(previous, TreeFilter)):
                for pc in previous._get_pcListToFilter():
                    outputs.extend(pc._get_outputScans())
            if(isinstance(previous, TreePipeline)):
                outputs.extend(previous.pipeline._get_outputScans())
                print('Is TreePipeline with '+str(len(outputs))+ 'scans')
            if(isinstance(previous, TreeExecutor)):
                outputs.extend(previous.module._get_outputScans())
        return outputs
    
    def filterAndPassInputsToProducerConsumer(self,inputs):
        filteredInputs = self.filterInputs(inputs)
        if(isinstance(self, TreeIterator)):
            self.treeOperator.filterAndPassInputsToProducerConsumer(set(filteredInputs))
        if(isinstance(self, TreeFilter)):
            for pc in self._get_pcListToFilter():
                pc._inputScans.extend(set(filteredInputs))
        if(isinstance(self, TreePipeline)):
            self.pipeline._inputScans.extend(set(filteredInputs))
        if(isinstance(self, TreeExecutor)):
            #self.module._inputScans.extend(set(filteredInputs))
            self.module._inputScans = set(filteredInputs)
    
    def isReadyToExecute(self):
        previousOps = self._get_previousTreeOperators()
        #For each check the status
        previousStatuses = []
        for previous in previousOps:
            previousStatuses.append(previous.status)
        if previousStatuses.count('completed') == len(previousStatuses):
            return True
        else:
            return False
                
    def execute(self):
        print("Executing operator on "+self.uid+" type "+self.otype)


class TreeIterator(TreeOperator):
    
    def __init__(self, iterateOn, treeOperators):
        TreeOperator.__init__(self)
        self.iterateOn = iterateOn #Can iterate on Filter which is set on Tag/Scan/filename setted in filter
        self._treeOperators = treeOperators #treeOperator to execute on each iteration
    
    def _get_treeOperators(self):
        return self._treeOperators  
    
    def execute(self):
        #Get the outputs of previous operators
        inputs = self.getOutputsScansFromPreviousTreeOperator()
        print('Executing tree iterator with '+str(len(inputs))+' scans')
        #Meaning that we will pass the sub group inputs to the tree operator inside the tree iterator
        #Need to group scans according to iterateOn
        groupScansDict = groupScansBy(inputs, self.iterateOn)
        #So we have a dictionnary with grouped scans according to iterator
        #Then we can iterate on dict keys and execute the treeiteraor operator attribute on grouped scans
        for cuFilter in groupScansDict.keys():
            for treeOperator in self._get_treeOperators():
                print('Filter on iterator is '+cuFilter.name+' on '+cuFilter.value)
                treeOperator.filterAndPassInputsToProducerConsumer(groupScansDict[cuFilter])
                treeOperator.execute()
        
            

class TreeExecutor(TreeOperator):
    
    def __init__(self,module):
        TreeOperator.__init__(self)
        self.module = module
    
    def _get_inputFilters(self):
        for consume in self.module._get_consumes():
            self._inputFilters.append(consume)
        return list(self._inputFilters)
    
    def execute(self):
        print("Executing module in executor "+str(self.uid))
        self.module.execute()


class TreePipeline(TreeOperator):
    
    def __init__(self, pipeline):
        TreeOperator.__init__(self)
        self.pipeline = pipeline #Is designed to execute the pipeline inside it
        
    def execute(self):
        print("Executing pipeline in tree pipeline "+str(self.uid))
        self.pipeline.execute()
        
class TreeFilter(TreeOperator):
    
    def __init__(self,filters):
        TreeOperator.__init__(self)
        self.filters = filters #Is designed to execute the pipeline inside it
        self._pcListToFilter = [] #List of ProducerCOnsumers objects on which to use filter
        
    def _get_pcListToFilter(self):
        return self._pcListToFilter


#################""PIPELINE RUN MODELS #################"



class Argument(GenericItem):
    
    def __init__(self, name, argType):
        GenericItem.__init__(self)
        self.name = name
        self.argtype = argType
        
class ArgumentFile(Argument):
    
    def __init__(self, name, filePath):
        Argument.__init__(self, name, 'file')
        self.filePath = filePath
        
class ArgumentParam(Argument):
    
    def __init__(self, name, value):
        Argument.__init__(self, name, 'parameter')
        self.value = value
               
class ProducerConsumer(GenericItem):
        
    def __init__(self, name):
        GenericItem.__init__(self)
        self.name = name
        self._inputScans = [] #List of scans to be used as inputs
        self._outputScans = [] #List of scans created as outputs
        self._inputArgs = [] #List of args to be used as inputs
        self._outputArgs = [] #List of args created as outputs
        self._consumes = []  #Definition of what is consommed by the Object 
        self._produces = [] #Definition of what is produced by the Object 
    
    def _get_inputScans(self):
        return self._inputScans
    
    def _get_outputScans(self):
        return self._outputScans    
    
    def _get_inputArgs(self):
        return self._inputArgs
    
    def _get_outputArgs(self):
        return self._outputArgs
    
    def _get_consumes(self):
        return self._consumes
    
    def _get_produces(self):
        return self._produces
    
    def addConsumesConstraint(self, pcConstraint):
        self._consumes.append(pcConstraint)
        return self._get_consumes()
    
    def removeConsumesConstraint(self, pcConstraint):
        self._consumes.remove(pcConstraint)
        return self._get_consumes()
    
    def addProducesConstraint(self, pcConstraint):
        self._produces.append(pcConstraint)
        return self._get_produces()
    
    def removeProducesConstraint(self, pcConstraint):
        self._produces.remove(pcConstraint)
        return self._get_produces()
        
    def execute(self):
        #GetInputs
        print("Loading "+self.uid+" "+self.name)
        #SetOutputs
        #For now inputs = outputs
        self._get_outputScans().extend(self._get_inputScans())
        

class LauncherTemplate(ProducerConsumer):
        
    def __init__(self, name, ltype):
        ProducerConsumer.__init__(self, name)
        self.ltype = ltype
        self.pathExecutable = "" #Don't know how to launch outside application
       
    def execute(self):
        print("Loading "+self.ltype+" "+self.name)

class ModuleLauncher(ProducerConsumer):
        
    def __init__(self, name, template):
        ProducerConsumer.__init__(self, name)
        self.template = template #Is a LauncherTemplate
        
    def _get_consumes(self):
        self._consumes.extend(self.template._get_consumes())
        return list(self._consumes)
        
    def execute(self):
        print("Loading "+self.name+" "+self.template.name)

class Module(ProducerConsumer):
        
    def __init__(self, name, launcher):
        ProducerConsumer.__init__(self, name)
        self.launcher = launcher #Is a ModuleLauncher
        self.successful = False
        
    def _get_consumes(self):
        self._consumes.extend(self.launcher._get_consumes())
        return list(self._consumes)
       
    def execute(self):
        print("Executing "+self.name+" "+self.launcher.name)
        print("List of inputs ")
        for scan in self._get_inputScans():
            print(scan.file_path)
            
class Pipeline(ProducerConsumer):
        
    def __init__(self, name):
        ProducerConsumer.__init__(self, name)
        self.tree = dict() # Map<level, List<TreeOperator>>
        #Automatically set levl 1 with empty list
        self.tree[1] = []
    
    def getLastLevel(self):
        #if not self.tree: return 1
        return max(self.tree, key=self.tree.get)
    
    #This will add level in the pipeline if it does not exists
    #Move existing operators in sublevels
    def addLevel(self,levelRow):
        #save operators beyond levelRow in temp dictionnary
        tempDict = dict()
        lastLevel = 1
        if self.tree:
            #lastLevel = self.getLastLevel()
            lastLevel = max(self.tree, key=self.tree.get)
        index = levelRow
        while index <= lastLevel :
            #Put temp List(TreeOperator) in tmp dict if there is something to put
            if not self.tree.get(index):
                tempDict[index+1] = self.tree.get(index)
                index += 1
        #Then insert the new Level
        self.tree[levelRow] = []
        #Then update values in tree after the inserted level
        index2 = levelRow+1
        while index2 <= max(tempDict, key=tempDict.get):
            #First add the new level in the tree
            self.tree[index2] = tempDict[index2]
            index2 +=1
            
    def deleteLevel(self,levelRow):
        #save operators beyond levelRow in temp dictionnary
        tempDict = dict()
        #lastLevel = self.getLastLevel()
        lastLevel = max(self.tree, key=self.tree.get)
        #only keeps the ones after the deleted level
        index = levelRow+1
        while index <= lastLevel :
            #Put temp List(TreeOperator) in tmp dict
            tempDict[index] = self.tree.get(index)
            index += 1
        #Then set the new values over previous ones
        index2 = levelRow
        while index2 <= max(tempDict, key=tempDict.get):
            #First add the new level in the tree
            self.tree[index2] = tempDict[index2-1]
            index2 += 1
    
    
    def addOperatorOnLevel(self,levelRow, treeOperator):
        self.tree[levelRow].append(treeOperator)
        
    def removeOperatorOnLevel(self,levelRow, treeOperator):
        self.tree[levelRow].remove(treeOperator)
    
    def getLevelForOperator(self, treeOperator):
        for key in self.tree.keys():
            for op in self.tree.get(key):
                if op is treeOperator: return key
                
    def getOperatorsFromLevel(self, level):
        return self.tree.get(level)        
    
    def execute(self):
        #When executing pipeline
        #we will call execute on each tree operator, when it's its turn
        #So we start by the tree level, get previous operator status
        #If the status is completed or successful or whatever
        #Then we can execute the current operator
        #else we go check the status of previous operator, until we reach the first or the last completed
        #1 get last level
        lastLevel = self.getLastLevel()
        #2 get operator on this level
        self.tryToExecuteOperatorsOnLevel(lastLevel)
                        
        print("Executing pipeline "+self.name)
    
    def tryToExecuteOperatorsOnLevel(self,level):
        levelOperators = self.tree.get(level)
        if(level > 1):
            #For each operator which is not completed, check if previous ones have been completed
            for op in levelOperators:
                if(op.status != 'completed'):
                    if op.isReadyToExecute():
                        op.execute();
                    else:
                        self.tryToExecuteOperatorsOnLevel(level-1)
        else:
            #As we are on level 1, directly execute all operators on this level
            for op in levelOperators:
                op.execute()
    

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
    