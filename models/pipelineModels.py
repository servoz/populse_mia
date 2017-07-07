from enum import Enum
from models.generics import GenericItem
from models.projectModels import Tag,Scan
from utils import utils
from utils.enums import OpStatus
from utils.enums import FilterOperator
from utils.enums import FilterOn
from multiprocessing import Process


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
        if isinstance(toBeMatched, Scan):
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
        if isinstance(toBeMatched, Argument):
            '''TODO implements filter on argument'''
            return True
        return False
            
    def execute(self):
        print("Loading filter on "+self.filterOn+" value "+self.value)



        
    
class TreeOperator(GenericItem):
    
    def __init__(self, pipeline = None):
        GenericItem.__init__(self)
        self.status = OpStatus.PENDING #Enum(hold,completed,running,waiting,failed)
        self._inputFilters = [] #list of filterWithOperator in input of the operator
        self._outputFilters = [] #list of filterWithOperator in output of the operator
        self._links = [] #List of links ids
        self.pipeline = pipeline

    def getInputFilters(self):
        return self._inputFilters
    
    def getOutputFilters(self):
        return self._outputFilters
    
    def getLinks(self):
        return self._links
    
    def getPreviousTreeOperatorsIds(self):
        previousOps = []
        #get the links from operator
        for link_uid in self.getLinks():
            #find the link object into pipeline parent
            link = self.pipeline.tree[link_uid]
            #Only where current is destination
            if link.destination == self.uid: previousOps.append(link.source)
        return previousOps

    def getNextTreeOperatorsIds(self):
        nextOps = []
        #get the links from operator
        for link_uid in self.getLinks():
            #find the link object into pipeline parent
            link = self.pipeline.tree[link_uid]
            #Only where current is source
            if link.source == self.uid: nextOps.append(link.destination)
        return nextOps
    
    #on update status, we should call check if pipeline completed
    def updateStatus(self,status):
        self.status = status
        #Tell the pipeline that status has changed
        self.pipeline.onUpdateStatus(self)
        #If the status is failed then all next operators will be unexecutables
        if status == OpStatus.FAILED:
            for op_uid in self.getNextTreeOperators():
                self.pipeline.tree[op_uid].status = OpStatus.UNEXECUTABLE
        elif status == OpStatus.COMPLETED:
            #call pipeline to launch next operators
            self.pipeline.executeNext()
    
    #Gives a list of inputs, return a filtered list
    def filterInputs(self,inputs):
        filteredInputs = []
        #iterate on inputs and add them to list if it matches the filters
        for current in inputs:
            letThrough = []
            for opfilter in self.getInputFilters():
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
            for opfilterWO in self.getOutputFilters():
                if(opfilterWO.filter.matches(current)):
                    letThrough.append(True)
                else:
                    letThrough.append(False)
            if False not in letThrough: filteredOutputs.append(current)
        return filteredOutputs
      
    def getInputs(self):
        print('getInputs...')
        inputs = []
        if(isinstance(self, TreeIterator)):
            for top in self.getTreeOperators():
                inputs.extend(top.getInputs())
        if(isinstance(self, TreeFilter)):
            for pc in self.getPcListToFilter():
                inputs.extend(pc.getInputs())
        if(isinstance(self, TreePipeline)):
            inputs.extend(self.pipeline.getInputs())
        if(isinstance(self, TreeExecutor)):
            inputs.extend(self.module.getInputs())
        return self.filterInputs(inputs)
    
    def getOutputs(self):
        print('getOutputsScans...')
        outputs = []
        #TreeIterator, get outputs from operator inside iterator
        if(isinstance(self, TreeIterator)):
            outputs.extend(self.treeOperator.getOutputs())
        #TreeFilter, get Filtered outputs
        if(isinstance(self, TreeFilter)):
            for pc in self.getPcListToFilter():
                outputs.extend(pc.getOutputs())
        #TreePipeline getOutputs from pipeline inside it
        if(isinstance(self, TreePipeline)):
            outputs.extend(self.pipeline.getOutputs())
        #TreeExecutor getOutputs from module
        if(isinstance(self, TreeExecutor)):
            outputs.extend(self.module.getOutputs())
        return self.filterOutputs(outputs)
         
    def getOutputsFromPreviousTreeOperators(self):
        print('getOutputsFromPreviousTreeOperator...')
        print('ids of previous operators :')
        for pv in self.getPreviousTreeOperatorsIds():
            print('id : '+str(pv))
        
        outputs = []
        #If there is no previous operator, then get the inputs of parent Pipeline
        previousOpIds = self.getPreviousTreeOperatorsIds()
        if not previousOpIds:
            outputs = self.pipeline.getInputs()
        else:
            for pid in self.getPreviousTreeOperatorsIds():
                previous = self.pipeline[pid]
                outputs.extend(previous.getOutputs())
        return outputs
    
    def filterAndPassInputsToProducerConsumer(self,inputs):
        filteredInputs = self.filterInputs(inputs)
        if(isinstance(self, TreeIterator)):
            for top in self.getTreeOperators():
                top.filterAndPassInputsToProducerConsumer(set(filteredInputs))
        if(isinstance(self, TreeFilter)):
            for pc in self.getPcListToFilter():
                pc._inputs.extend(set(filteredInputs))
        if(isinstance(self, TreePipeline)):
            self.pipeline._inputs.extend(set(filteredInputs))
        if(isinstance(self, TreeExecutor)):
            #self.module._inputScans.extend(set(filteredInputs))
            self.module._inputs.extend(set(filteredInputs))
            print("Module in executor has "+str(len(self.module._inputs))+" scans")
    
    def isReadyToExecute(self):
        previousOps = self.getPreviousTreeOperatorsIds()
        #For each check the status
        previousStatuses = []
        for previous in previousOps:
            previousStatuses.append(previous.status)
        if previousStatuses.count('completed') == len(previousStatuses):
            return True
        else:
            return False
                
    #the tree operator will be executed on given inputs
    def execute(self,inputs):
        #Set status to RUNNING
        self.updateStatus(OpStatus.RUNNING)
        #Get inputs from previous operators
        #inputs = self.getOutputsFromPreviousTreeOperators()
        self.filterAndPassInputsToProducerConsumer(inputs)
        print("Executing operator on "+self.uid)
        self.doJob()
                
        

    def doJob(self):
        #Nothin to do, it is a parent class
        pass

class TreeLink(TreeOperator):
        
    def __init__(self, source,destination, pipeline = None):
        TreeOperator.__init__(self,pipeline)
        self.status = OpStatus.COMPLETED
        self.source = source #id of tree operator source of link
        self.destination = destination #id of operator destination of link

class TreeIterator(TreeOperator):
    
    def __init__(self, iterateOn, treeOperators, pipeline = None):
        TreeOperator.__init__(self,pipeline)
        self.iterateOn = iterateOn #Can iterate on Filter which is set on Tag/Scan/filename setted in filter
        self._treeOperators = treeOperators #treeOperator to execute on each iteration
    
    def getTreeOperators(self):
        return self._treeOperators  
    
    def doJob(self):
        #Meaning that we will pass the sub group inputs to the tree operator inside the tree iterator
        #Need to group scans according to iterateOn
        groupScansDict = groupScansBy(self.getInputs(), self.iterateOn)
        #So we have a dictionnary with grouped scans according to iterator
        #Then we can iterate on dict keys and execute the treeiteraor operator attribute on grouped scans
        for cuFilter in groupScansDict.keys():
            for treeOperator in self.getTreeOperators():
                print('Filter on iterator is '+cuFilter.name+' on '+cuFilter.value)
                treeOperator.execute(groupScansDict[cuFilter])
        
            

class TreeExecutor(TreeOperator):
    
    def __init__(self,module, pipeline = None):
        TreeOperator.__init__(self,pipeline)
        self.module = module
    
    def getInputFilters(self):
        for consume in self.module.getConsumes():
            self._inputFilters.append(consume)
        return list(self._inputFilters)
    
    def doJob(self):
        print("Executing module in executor "+str(self.uid))
        #In the tree executor, we use multithreading for execution
        #process = Process(target = self.module.execute(self.getInputs()))
        #process.start()
        self.updateStatus(OpStatus.COMPLETED)
        


class TreePipeline(TreeOperator):
    
    def __init__(self, pipeline, pipelineOwner = None):
        TreeOperator.__init__(self,pipelineOwner)
        self.pipeline = pipeline #Is designed to execute the pipeline inside it
        
    def doJob(self):
        print("Executing pipeline in tree pipeline "+str(self.uid))
        self.pipeline.execute(self.getInputs())
        
class TreeFilter(TreeOperator):
    
    def __init__(self,filters, pipeline= None):
        TreeOperator.__init__(self, pipeline)
        self.filters = filters #Is designed to execute the pipeline inside it
        self._pcListToFilter = [] #List of ProducerCOnsumers objects on which to use filter
        
    def getPcListToFilter(self):
        return self._pcListToFilter

    def doJob(self):
        #Nothing to do, filter should be automatic
        pass
        

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
        
    def __init__(self, name, owner=None):
        GenericItem.__init__(self)
        self.name = name
        self.owner = owner
        self._inputs = [] #List of inputs (scans,arguments,file...)
        self._outputs = [] #List of outputs (scans,arguments,file...)
        self._consumes = []  #Definition of what is consommed by the Object 
        self._produces = [] #Definition of what is produced by the Object 
    
    def getInputs(self):
        return self._inputs
    
    def getOutputs(self):
        return self._outputs    
        
    def getConsumes(self):
        return self._consumes
    
    def getProduces(self):
        return self._produces
    
    def addConsumesConstraint(self, pcConstraint):
        self._consumes.append(pcConstraint)
        return self.getConsumes()
    
    def removeConsumesConstraint(self, pcConstraint):
        self._consumes.remove(pcConstraint)
        return self.getConsumes()
    
    def addProducesConstraint(self, pcConstraint):
        self._produces.append(pcConstraint)
        return self.getProduces()
    
    def removeProducesConstraint(self, pcConstraint):
        self._produces.remove(pcConstraint)
        return self.getProduces()
        
    def execute(self):
        #GetInputs
        print("Loading "+self.uid+" "+self.name)
        #SetOutputs
        #For now inputs = outputs
        self.getOutputs().extend(self.getInputs())
        self.owner.updateStatus(status)

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
        
    def getConsumes(self):
        self._consumes.extend(self.template.getConsumes())
        return list(self._consumes)
        
    def execute(self):
        print("Loading "+self.name+" "+self.template.name)

class Module(ProducerConsumer):
        
    def __init__(self, name, launcher):
        ProducerConsumer.__init__(self, name)
        self.launcher = launcher #Is a ModuleLauncher
        self.successful = False
        
    def getConsumes(self):
        self._consumes.extend(self.launcher.getConsumes())
        return list(self._consumes)
       
    def execute(self,inputs):
        print("Executing "+self.name+" "+self.launcher.name)
        print("List of inputs ")
        for scan in inputs:
            print(scan.file_path)
            
class Pipeline(ProducerConsumer):
        
    def __init__(self, name):
        ProducerConsumer.__init__(self, name)
        self.tree = dict() # Map<operator id, TreeOperator
        
    
    def getLastLevel(self):
        #if not self.tree: return 1
        return max(self.tree, key=self.tree.get)
    
    def addOperator(self,operator):
        self.tree[operator.uid]= operator
        
    def removeOperator(self,operator):
        del self.tree[operator.uid]
        
    def addLink(self,source,destination):
        link = TreeLink(source,destination,self)
        #Add the link to source and destination operators
        self.tree[source.uid].getLinks().append(link.uid)
        self.tree[destination.uid].getLinks().append(link.uid)
        #Add the link into the pipeline tree
        self.addOperator(link)
        
    def removeLink(self,link):
        #Get the source and destination of link into the tree
        for link_uid in self.tree[link.source].getLinks():
            if link.uid == link_uid: self.tree[link.source].getLinks().remove(link_uid)
        for link_uid in self.tree[link.destination].getLinks():
            if link.uid == link_uid: self.tree[link.destination].getLinks().remove(link_uid)
        #Remove the link from the tree
        self.removeOperator(link)
    
    
    def findOperatorsWithoutNext(self):
        result = []
        for op_uid in self.tree.keys():
            if not self.tree[op_uid].getNextTreeOperators(): result.append(self.tree[op_uid])
        return result                
    
    def getTreeStatuses(self):
        treeStatuses = []
        #get all status from tree at this time (links are always completed)
        for op_uid in self.tree.keys():
            treeStatuses.append(self.tree[op_uid].status)
        return treeStatuses
    
    def onUpdateStatus(self,operator):
        print("Status updated for operator "+operator.uid+" "+operator.status.value)
            
    def isPipelineDone(self):
        treeStatuses = self.getTreeStatuses()            
        if (treeStatuses.count(OpStatus.COMPLETED)+treeStatuses.count(OpStatus.FAILED)) == len(self.tree.keys()):
            return True
        return False
            
    def getPipelineStatus(self):
        treeStatuses = self.getTreeStatuses()
        if treeStatuses.__contains__(OpStatus.FAILED):return OpStatus.FAILED
        return OpStatus.COMPLETED   
        
    
    def findOperatorsReady(self):
        result = []
        for op_uid in self.tree.keys():
            #If do not have precedence
            if not self.tree[op_uid].getPreviousTreeOperatorsIds() and self.tree[op_uid].status == OpStatus.PENDING: 
                result.append(self.tree[op_uid])
            else:
                if self.tree[op_uid].status == OpStatus.PENDING:
                    previousOpsStatuses = []
                    for previousOpUid in self.tree[op_uid].getPreviousTreeOperatorsIds():
                        previousOpsStatuses.append(self.tree[previousOpUid].status)
                    if previousOpsStatuses.count(OpStatus.COMPLETED) == len(self.tree[op_uid].getPreviousTreeOperatorsIds()):
                        result.append(self.tree[op_uid])
        return result
    
    
    def execute(self,inputs):
        self.getInputs().extend(inputs)
        #When executing pipeline
        #we will call execute on each tree operator, when it's its turn
        #So iterate on operators ready
        while not self.isPipelineDone():
            self.executeNext()
        
        self.status = self.getPipelineStatus()  
        
        print("Pipeline status is  "+self.status.value)
        return self.status
    
    def executeNext(self):
        readyOps = self.findOperatorsReady()
        print("OPERATORS READY FOR EXECUTION")
        for op in readyOps:
            print("OP ID "+op.uid)
            #manage inputs/outputs of operators
            op.execute(op.getOutputsFromPreviousTreeOperators())
    

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
    