from enum import Enum
from models.generics import GenericItem
from models.projectModels import Tag,Scan
from utils import utils
from utils.enums import OpStatus
from utils.enums import FilterOperator
from utils.enums import FilterOn
from multiprocessing import Process
import logging

#Filter is used to filter given inputs (any GenericItem should be managed (Scan,Argument,Tag)
#It is filtered on given type, according to name and/or value
class Filter(GenericItem):
        
    def __init__(self, filterOn, name, value, isCaseSensitive, isExactly, operator):
        GenericItem.__init__(self)
        self.filterOn = filterOn #Enum element on which to filter (filename,tag, ...)
        self.name = name #Value on which to filter on
        self.value = value #Value on which to filter on
        self.isCaseSensitive = isCaseSensitive
        self.isExactly = isExactly #In opposition to contains
        self.operator = operator # Enum with AND or OR or NONE Operators mechanism has to be implemented
    
    #Methods hash and eq are Mandatory for group by
    def __hash__(self):
        return hash(self.filterOn.value+str(self.name)+str(self.value)+str(self.isCaseSensitive)+str(self.isExactly)+str(self.operator.value))
    
    #Must override the basic __eq__ method as we don't want to compare uid
    #We compare only others attributes so 2 filters can be equals even with a different uid
    #For exemple, with the executionKey mechanism, we have to compare Filters used as key
    def __eq__(self, other):
        if(self.filterOn != other.filterOn): return False
        if(self.name != other.name): return False
        if(self.value != other.value): return False
        if(self.isCaseSensitive != other.isCaseSensitive): return False
        if(self.isExactly != other.isExactly): return False
        if(self.operator.value != other.operator.value): return False
        return True
    
    #Check if this one is better than the applyFilter method
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
    
    #Used for debugging right now       
    def execute(self):
        print("Loading filter on "+self.filterOn+" value "+self.value)



        
#The TreeOperator is the parent class for all elements in the pipeline tree
#It has all common method used for executing, filter inputs, launchJobs   
class TreeOperator(GenericItem):
    
    def __init__(self, pipeline = None,owner=None):
        GenericItem.__init__(self)
        self._statuses = dict()
        self._inputs = dict()
        self._outputs = dict()
        self._inputFilters = [] #list of filterWithOperator in input of the operator
        self._outputFilters = [] #list of filterWithOperator in output of the operator
        self._links = [] #List of links ids
        self.pipeline = pipeline
        self._results = dict()
        self.owner = owner
        
    #Statuses are stored in a dictionnary because a same instance of TreeOperator can run the doJob method multiple times
    #Each runned doJob method is done with an executionKey that also have a status
    #dict(executionKey,OpSTatus)
    def getStatuses(self):
        return self._statuses

    #Inputs are stored the same way as statuses
    #It's possible to have different list of inputs for different executionKeys
    #inputs have been filtered on inputFilters when entering the execute method
    #dict(executionKey,[inputs])
    def getInputs(self):
        return self._inputs
    
    #Smae thing for outputs
    #There are filtered on outputFilters
    #dict(executionKey,[outputs])
    def getOutputs(self):
        return self._outputs

    #A list of filters on which every inputs will be filtered before being send to the doJob method
    def getInputFilters(self):
        return self._inputFilters
    
    #A list of filters on which every outputs will be filtered after getting out of the doJob method
    def getOutputFilters(self):
        return self._outputFilters
    
    #Get a list of TreeLink that represents which operators this one is linked to
    #It can be a source or a destination
    def getLinks(self):
        return self._links
    
    #Same thing as outputs and inputs
    #Having a result dict allows to retrieve results of the doJob method without output filtering
    #dict(executionKey,[inputs])
    def getResults(self):
        return self._results
    
    #It returns a list of uid corresponding to the previous operators before this one that are in the pipeline tree dict
    #Based on links, it's possible to find operatos that are a source for this one
    def getPreviousTreeOperatorsIds(self):
        previousOps = []
        #get the links from operator
        for link_uid in self.getLinks():
            #find the link object into pipeline parent
            link = self.pipeline.tree[link_uid]
            #Only where current is destination
            if link.destination == self.uid: 
                previousOps.append(link.source)
        for prevs in previousOps:
            print("previous "+prevs)
            print ("With status "+self.pipeline.tree[prevs].getStatus().value)
            
        return previousOps

    #It returns a list of uid corresponding to the next operators efter this one that are in the pipeline tree dict
    #Based on links, it's possible to find operatos that are a destination for this one
    def getNextTreeOperatorsIds(self):
        nextOps = []
        #get the links from operator
        for link_uid in self.getLinks():
            #find the link object into pipeline parent
            link = self.pipeline.tree[link_uid]
            #Only where current is source
            if link.source == self.uid: 
                nextOps.append(link.destination)
        return nextOps
    
    #Update a status in the statuses dict
    #TODO on update status, we should tell the pipeline that something happened 
    #and then the pipeline will chek if something can be started
    def updateStatus(self,executionKey,status):
        self.getStatuses()[executionKey] = status
        #Tell the pipeline that status has changed
        self.pipeline.onUpdateStatus(self,executionKey)
        #If the status is failed then all next operators will be unexecutables
        if status == OpStatus.FAILED:
            for op_uid in self.getNextTreeOperatorsIds():
                self.pipeline.tree[op_uid].getStatuses()[executionKey] = OpStatus.UNEXECUTABLE
        elif status == OpStatus.COMPLETED:
            #call pipeline to launch next operators
            self.pipeline.executeNext()
    
    #A treeOperator status depends of all statuses stored in the statuses dict
    #In many cases, there is only one status in dict with executionKey = blankKey
    def getStatus(self):
        #return a status according to what is stored in statuses dict
        statuses = []
        for skey in self.getStatuses().keys():
            statuses.append(self.getStatuses()[skey])
        if statuses:
            if statuses.count(OpStatus.COMPLETED) == len(statuses):
                return OpStatus.COMPLETED
            if OpStatus.FAILED in statuses:
                return OpStatus.FAILED
            if OpStatus.UNEXECUTABLE in statuses:
                return OpStatus.UNEXECUTABLE
            if OpStatus.RUNNING in statuses:
                return OpStatus.RUNNING
            if statuses.count(OpStatus.PENDING) == len(statuses):
                return OpStatus.PENDING
        return OpStatus.PENDING
        
    #Gives a list of filters and elements , return a filtered list
    #TODO test and check if it's better than matches method from Filter
    def filterElements(self,filtersList,elements):
        result = elements
        if filtersList:
            for f in filtersList:
                if f.operator == FilterOperator.AND:
                    result = applyFilter(f, result)
                elif f.operator == FilterOperator.OR:
                    result.extend(applyFilter(f, result))
        return result
    
    #Check if the given executionKey is the BlankKey
    def isBlankKey(self,executionKey):
        if executionKey == getBlankKey(): return True
        return False
    
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
      
        
    #The idea behind the executionKey is that in an iterator for exemple, one of the iteration has been completed, 
    #we know it thanks to the correcponding status in dict
    #So if we want to execute the next operator in pipeline on the same executionKey, we can do it by getting only the corresponding outputs
    #Even if the others iterations aren't COMPLETED or FAILED
    def getOutputsFromPreviousTreeOperators(self,previousOperatorsIds=[],executionKey=None):
        #To get outputs from previous operator, we try to get the outputs corresponding to the execution Key given
        #Should mostlty be The blankFilter
        if executionKey == None: executionKey = getBlankKey()
        outputs = []
        for previousId in previousOperatorsIds:
            #if isBlankKey, get All outputs from previous operator
            outputsKeys = self.pipeline.tree[previousId].getOutputs().keys()
            if self.isBlankKey(executionKey):
                for output_exec_key in outputsKeys:
                    outputs.extend(self.pipeline.tree[previousId].getOutputs()[output_exec_key])
            else:
                for output_exec_key in self.pipeline.tree[previousId].getOutputs().keys():
                    #check if the outputs key list contains the input key list
                    if output_exec_key == executionKey:
                        #Then get the corresponding output
                        outputs.extend(self.pipeline.tree[previousId].getOutputs()[output_exec_key])
        return outputs
    
           
    #the tree operator will be executed on given inputs and on given exeucteOn
    #The executeOn comes from Iterator and is mainly a tag name for example
    #If the executeOn is not given as parameter, it will be set as the BlankKey
    #The execute method should not be overriden in childs as it does the filetring, the update statuts... etc
    #All those actions are common for each  operators so one implementation is enough
    def execute(self, inputs=[], executeOn=None,):
        #
        #The only key in the inputs/results/outputs dict() is executeOn
        #Default executeOn key is the blank filter
        #If there is an executeOn key then use it to set the results
        #1) Filter given inputs according to operator input filters
        #2) Set the corresponding inputs with its executeOn key in inputs dict()
        #3) doJob will return a set of results that are put in result[executionKey] = doJob(inputs)
        #4) Filter given results according to operator output filters
        #5) for each row of results, set the output[executeOn] = filtered(results)
        #6) The next operator will get the outputs according to execution Key, mostly it should be the BlankFilter, but sometimes, we use the execution key
        #to get the right outputs and send it to the operator as inputs
        #7) in get outputs from previous, if the next one is not executed in the same iterator so don't have the key, and call outputs using blank iterator,
        #send all outputs in a same list 
        #8) All information can be displayed during display and dont have to be explicitly into the dicts()
        
        #Get the execution key
        executionKey = self.getExecutionKey(executeOn)
        #Update the status corresponding to the execution key
        #Set status to RUNNING for the key
        self.updateStatus(executionKey,OpStatus.RUNNING)
        #Get outputs from previous operators only if previous operators exists
        previousOperatorsIds = self.getPreviousTreeOperatorsIds()
        if previousOperatorsIds:
            inputs.extend(self.getOutputsFromPreviousTreeOperators(previousOperatorsIds,executionKey))
                
        #1)Filter given inputs
        filteredInputs = self.filterElements(self.getInputFilters(), inputs)
        #Set the inputs of the operator with execution key
        self.getInputs()[executionKey] = filteredInputs
        #Get inputs from previous operators
        print("Executing operator on "+self.uid)
        #doJob() method takes executionKey as parameter to know on which filtered scan, an operator has been used
        try:
            #use multithreading for executions
            #TODO Manage multithreading and return results in the operator results dictionary
            #process = Process(target = self.doJob(filteredInputs))
            #process.start()
            
            #Set the results by key/resultList
            self.getResults()[executionKey] = self.doJob(filteredInputs)
            #Filter the results using output filters and set them in outputs dict
            self.getOutputs()[executionKey] = self.filterElements(self.getOutputFilters(), self.getResults()[executionKey])
              
            #TODO The idea here and it does not work
            #An iterator should not be set as completed or else while any of the running job inside it is still pending/running
            if(isinstance(self,TreeIterator)):
                while self.getStatus() == OpStatus.RUNNING or self.getStatus() == OpStatus.PENDING:
                    pass
                else:
                    self.updateStatus(executionKey,self.getStatus())
            else:
                self.updateStatus(executionKey,OpStatus.COMPLETED) 
        except Exception as e:
            logging.error(e, exc_info=True)
            self.updateStatus(executionKey,OpStatus.FAILED)
            self.status = OpStatus.FAILED
    
    #The executionKey returned is a tuple of list that can be stored in dict as it is immutable
    #It is easy to get bak to list from tuple
    def getExecutionKey(self,executeOn):
        if executeOn is None: 
            return getBlankKey()
        else:
            return tuple([executeOn])
    
    def getListFromExecutionKey(self,key):
        return list(key)

    def doJob(self,inputs):
        #Nothin to do, it is a parent class
        #The doJob method is detailed in each operator
        pass

#Used to define links between operators
#one way
#one is source
#one is destination
#As it is a TreeOperator, it can be given a job if needed
#But don't forget to change the getStatus in this case
class TreeLink(TreeOperator):
        
    def __init__(self, source,destination, pipeline = None):
        TreeOperator.__init__(self,pipeline)
        self.source = source #id of tree operator source of link
        self.destination = destination #id of operator destination of link
        
    #As treeLinks are part of the pipeline tree but are not waiting for job executon,
    #Its status will always be COMPLETED so pipeline will not try to execute it
    def getStatus(self):
        return OpStatus.COMPLETED    

#The iterator can be the owner of executors (view Operator constructor)
#It ownes a list of operators and gives inputs to the firsts in it
#Then it iterates on given iterateOn
class TreeIterator(TreeOperator):
    
    def __init__(self, iterateOn, treeOperators, pipeline = None):
        TreeOperator.__init__(self,pipeline)
        self.iterateOn = iterateOn #Can iterate on Filter which is set on Tag/Scan/filename setted in filter
        self._treeOperators = treeOperators #treeOperators to execute on each iteration
    
    def getTreeOperators(self):
        return self._treeOperators  

    def addOperator(self, operator):
        self._treeOperators.append(operator)
        #Add the iterator as the owner
        operator.owner = self
        if self.pipeline is not None: 
            self.pipeline.addOperator(operator)
    
    #The status of an iterator depends of the statuses of all its operators
    def getStatus(self):
        opStatuses = []
        for op in self.getTreeOperators():
            opStatuses.append(op.getStatus())
        if opStatuses:
            if opStatuses.count(OpStatus.COMPLETED) == len(opStatuses):
                return OpStatus.COMPLETED
            if OpStatus.FAILED in opStatuses:
                return OpStatus.FAILED
            if OpStatus.UNEXECUTABLE in opStatuses:
                return OpStatus.UNEXECUTABLE
            if OpStatus.RUNNING in opStatuses:
                return OpStatus.RUNNING
            if opStatuses.count(OpStatus.PENDING) == len(opStatuses):
                return OpStatus.PENDING
        return OpStatus.PENDING
    
    def doJob(self,inputs):
        #Meaning that we will pass the sub group inputs to the tree operator inside the tree iterator
        #Need to group scans according to iterateOn
        print("INPUTS SIZE FOR ITERATOR "+str(len(self.getInputs())))
        groupInputsDict = groupInputsBy(inputs, self.iterateOn)
        #So we have a dictionnary with grouped scans according to iterator
        print("GROUPED SCANS "+str(len(groupInputsDict.keys())))
        #Then we can iterate on dict keys and execute the treeiteraor operator attribute on grouped scans
        for cuFilter in groupInputsDict.keys():
            #here the cuFilter used for grouping inputs is used as execution key
            #so on each iteration, the same executor instance can be called on different executionKey
            #each time it does a job, the executionKey and the outputs are differents
            #So the next operator in iterator can start its job if the given key is ready
            executionKey = self.getExecutionKey(cuFilter)
            #We can firstly set up the statuses dict to know how much running instances there will be
            #Using that we can also calculate percentage of completion for the iterator
            for treeOperator in self.getTreeOperators():
                print('Setting up statuses with key '+cuFilter.name+' on '+cuFilter.value)
                treeOperator.updateStatus(executionKey,OpStatus.PENDING)
            
        for cuFilter in groupInputsDict.keys():
            executionKey = self.getExecutionKey(cuFilter)            
            #For each iterator, execute the operator
            #it will call the execute method in TreeOperator parent, so filter inputs and manage status
            #The doJob method of each operator iterated will be called also
            for treeOperator in self.getTreeOperators():
                print('Filter on iterator is '+cuFilter.name+' on '+cuFilter.value)
                if treeOperator.getStatuses()[executionKey] == OpStatus.PENDING:
                    self.getResults()[executionKey] = treeOperator.execute(groupInputsDict[cuFilter],executionKey)

#Contains a module and is used to do the real job
#It will get mandatory filter according to the producer/consumer it contains
#it will also use the filter set as on any TreeOperator
class TreeExecutor(TreeOperator):
    
    def __init__(self,module, pipeline = None):
        TreeOperator.__init__(self,pipeline)
        self.module = module
    
    def getInputFilters(self):
        for consume in self.module.getConsumes():
            self._inputFilters.append(consume)
        return list(self._inputFilters)
    
    def doJob(self,inputs):
        print("Executing module in executor "+str(self.uid))
        outputs = inputs
        return outputs


#Like an iterator it can contains a pipeline, contaning itself other operators
#TODO manage execution and doJob 
#TODO manage status 
class TreePipeline(TreeOperator):
    
    def __init__(self, pipeline, pipelineOwner = None):
        TreeOperator.__init__(self,pipelineOwner)
        self.pipeline = pipeline #Is designed to execute the pipeline inside it
        
    def doJob(self,inputs):
        print("Executing pipeline in tree pipeline "+str(self.uid))
        self.pipeline.execute(self.getInputs())

#TreeFilter is put in the pipeline tree
#Given inputs will be automatically filtered and availables for next operator as outputs
#thanks to the execute method of parent TreeOperator
#TODO manage status ?     
class TreeFilter(TreeOperator):
    
    def __init__(self,filters, pipeline= None):
        TreeOperator.__init__(self, pipeline)
        self.filters = filters #Is designed to execute the pipeline inside it
        
    def doJob(self,inputs):
        #Nothing to do, filter should be automatic in the parent, tree operator execute method
        pass
        

#################""PIPELINE RUN MODELS #################"


#Argument is a generic item
#It is considered as in input like scan/tag 
#Difference between scan and argument can be made in the producer/consumer when calling a treatment
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
 
#The producr consumer allows to set mandatory Filter on input/output in consumes/produces
#TODO Filters can be automatially generated if it consumes a designed scan type for example              
class ProducerConsumer(GenericItem):
        
    def __init__(self, name, owner=None):
        GenericItem.__init__(self)
        self.name = name
        self.owner = owner
        self._consumes = []  #Definition of what is consommed by the Object 
        self._produces = [] #Definition of what is produced by the Object 
        
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
        
    def execute(self,inputs):
        print("Executing "+self.uid+" "+self.name)
        outputs = []
        #outputs = doYourJob(inputs)
        return outputs

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
        for input in inputs:
            if isinstance(input, Scan):
                print(input.file_path)
            
#The main object
#Has a tree dict with operator uid as key and operator as value
#So we can easily find an operator in the tree and manage it
class Pipeline(ProducerConsumer):
        
    def __init__(self, name):
        ProducerConsumer.__init__(self, name)
        self.tree = dict() # Map<operator id, TreeOperator
        
        
    def addOperator(self,operator):
        self.tree[operator.uid]= operator
        
    def removeOperator(self,operator):
        del self.tree[operator.uid]
        
    def addLink(self,source,destination):
        link = TreeLink(source.uid,destination.uid,self)
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
    
    def findOperatorsWithoutPrevious(self):
        result = []
        for op_uid in self.tree.keys():
            #we dont want the ones that are the first in a tree iterator or tree pipeline
            if not self.tree[op_uid].getPreviousTreeOperatorsIds() and self.tree[op_uid].owner is None: 
                result.append(self.tree[op_uid])
        return result 
    
    def findOperatorsWithoutNext(self):
        result = []
        for op_uid in self.tree.keys():
            #we dont want the ones that are the last in a tree iterator or tree pipeline
            if not self.tree[op_uid].getNextTreeOperators() and self.tree[op_uid].owner is None: 
                result.append(self.tree[op_uid])
        return result                
    
    #Return all statuses in the pipeline tree as OpStatus
    def getTreeStatuses(self):
        treeStatuses = []
        #get all status from tree at this time (links are always completed)
        for op_uid in self.tree.keys():
            treeStatuses.append(self.tree[op_uid].getStatus())
            print(type(self.tree[op_uid]).__name__+" "+op_uid+" STATUS "+self.tree[op_uid].getStatus().value)
        return treeStatuses
    
    #TODO what to do if an operator changes its status
    def onUpdateStatus(self,operator,executionKey):
        print("Status updated for operator "+operator.uid+" "+operator.getStatus().value+" on executionKey "+str(executionKey))
            
    #If number of COMPLETED/FAILED/UNEXECUTABLE == size of tree
    #Then the pipeline is done even if it is not completed
    def isPipelineDone(self):
        treeStatuses = self.getTreeStatuses()
        if (treeStatuses.count(OpStatus.COMPLETED)+treeStatuses.count(OpStatus.FAILED)+treeStatuses.count(OpStatus.UNEXECUTABLE)) == len(self.tree.keys()):
            return True
        return False
            
    def getPipelineStatus(self):
        treeStatuses = self.getTreeStatuses()
        if treeStatuses.__contains__(OpStatus.FAILED):return OpStatus.FAILED
        return OpStatus.COMPLETED   
        
    #Name speaks
    #If not previous ids ans not owned by a TreeIterator or a TreePipeline, so owner is empty, then it's ready
    #If it has a previous one, check status of previous one and is considered ready if previous one is completed
    #Is ready if the previous operator is completed on the given key
    def findOperatorsReady(self):
        result = []
        for op_uid in self.tree.keys():
            #No need to check on TreeLinks
            if not isinstance(self.tree[op_uid], TreeLink):
                previousIds = self.tree[op_uid].getPreviousTreeOperatorsIds()
                #If do not have precedence
                print("STATUS OF OPERATOR "+op_uid+" "+type(self.tree[op_uid]).__name__+" "+self.tree[op_uid].getStatus().value)
                if not previousIds and self.tree[op_uid].getStatus() == OpStatus.PENDING and self.tree[op_uid].owner is None: 
                    result.append(self.tree[op_uid])
                else:
                    if self.tree[op_uid].getStatus() == OpStatus.PENDING and self.tree[op_uid].owner is None:
                        previousOpsStatuses = []
                        for previousOpUid in previousIds:
                            previousOpsStatuses.append(self.tree[previousOpUid].getStatus())
                        if previousOpsStatuses.count(OpStatus.COMPLETED) == len(previousIds):
                            result.append(self.tree[op_uid])
        return result
    
    
    def execute(self,inputs):
        #we will call execute on each tree operator, when it's its turn
        #So iterate on operators ready
        #First get the first operators to launch, meaining the ones without previous op and not in another operator
        firstRow = self.findOperatorsWithoutPrevious()
        for op in firstRow:
            op.execute(inputs)
        #Then wait
        while not self.isPipelineDone():
            self.executeNext()
        
        self.status = self.getPipelineStatus()  
        
        print("Pipeline status is  "+self.status.value)
        return self.status
    
    #Find operators ready and execute them
    def executeNext(self):
        readyOps = self.findOperatorsReady()
        print("OPERATORS READY FOR EXECUTION")
        for op in readyOps:
            print("OP ID "+op.uid)
            #manage inputs/outputs of operators
            previousOpIds = op.getPreviousTreeOperatorsIds()
            #MAYBE USE the MULTITHREADING HERE 
            op.execute(op.getOutputsFromPreviousTreeOperators(previousOpIds))
    

def applyFilter(filterToApply, elements):
    filteredList = []
    for element in elements:
        if isinstance(element, Scan):
            if(filterToApply.filterOn == FilterOn.TAG):        
                #First check if tag  exists for current
                if(filterToApply.name in element.getAllTagsNames()):
                    #Then check value if has value
                    if(filterToApply.value is not None):
                        for tag in element.getAllTags():
                            if(tag.name == filterToApply.name):
                                if(filterToApply.isExactly):
                                    if(filterToApply.isCaseSensitive):
                                        if(utils.normalize_casewith(utils.cleanTagValue(tag.value)) == utils.normalize_casewith(filterToApply.value)):
                                            if element not in filteredList: filteredList.append(element)
                                    else:
                                        if(utils.normalize_caseless(utils.cleanTagValue(tag.value)) == utils.normalize_caseless(filterToApply.value)):
                                            if element not in filteredList: filteredList.append(element)
                                else:
                                    if(filterToApply.isCaseSensitive):
                                        if(utils.normalize_casewith(utils.cleanTagValue(tag.value)) in utils.normalize_casewith(tag.value)):
                                            if element not in filteredList: filteredList.append(element)
                                    else:
                                        if(utils.normalize_caseless(utils.cleanTagValue(tag.value)) in utils.normalize_caseless(tag.value)):
                                            if element not in filteredList: filteredList.append(element)
                    else:
                        #direcltly add scan to results
                        if element not in filteredList: filteredList.append(element)
            if(filterToApply.filterOn == FilterOn.ATTRIBUTE):
                if(filterToApply.name == FilterOn.FILENAME):
                    if(filterToApply.isExactly):
                        if(filterToApply.isCaseSensitive):
                            if(utils.normalize_casewith(element.file_path) == utils.normalize_casewith(filterToApply.value)):
                                if element not in filteredList: filteredList.append(element)
                        else:
                            if(utils.normalize_caseless(element.file_path) == utils.normalize_caseless(filterToApply.value)):
                                if element not in filteredList: filteredList.append(element)
                    else:
                        if(filterToApply.isCaseSensitive):
                            if(utils.normalize_casewith(element.file_path) in utils.normalize_casewith(tag.value)):
                                if element not in filteredList: filteredList.append(element)
                        else:
                            if(utils.normalize_caseless(element.file_path) in utils.normalize_caseless(tag.value)):
                                if element not in filteredList: filteredList.append(element)
                    
        
    return filteredList
    
#Will return a dictionnary with filter as key and items as value
#inputs are mostly scans but can be any generix items
#argument/scans can be sorted just for the execution of a module launcher for example
def groupInputsBy(scans, filterGroupBy):
    groupedInputs = dict()
    #If filterGroupOn has a value, then it is just a filter
    if(filterGroupBy.value is not None):
        groupedInputs[filterGroupBy] = applyFilter(filterGroupBy, scans)  
    else:
        for scan in scans:
            if(filterGroupBy.filterOn == FilterOn.TAG):
                for tag in scan.getAllTags():
                    if tag.name == filterGroupBy.name:
                        #Set a temporary filter as key
                        keyFilter = Filter(filterGroupBy.filterOn, filterGroupBy.name, tag.value, filterGroupBy.isCaseSensitive, filterGroupBy.isExactly, FilterOperator.OR)
                        #check if it does not exists in groupedInputs keys
                        if keyFilter not in groupedInputs.keys():
                            groupedInputs[keyFilter] = [scan]
                        else:
                            groupedInputs.get(keyFilter).append(scan)
            if(filterGroupBy.filterOn == FilterOn.ATTRIBUTE):
                if(filterGroupBy.name == FilterOn.FILENAME):
                    #TODO if there is something to do
                    continue    
    #COunt groups            
    for key in groupedInputs.keys():
        print('Size of group '+key.name+' '+str(len(groupedInputs[key])))
    
    return groupedInputs
    
    
def getBlankKey():
    bFilter = Filter(FilterOn.BLANK, None, None, False, False, FilterOperator.NONE)
    bFilter.uid = 'BlankFilter'
    return tuple([bFilter])