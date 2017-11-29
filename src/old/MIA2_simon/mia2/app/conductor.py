import json
import sys
from models.pipelineModels import *
from models.projectModels import *
from controllers import projectController as controller
from utils import utils
from utils.enums import FilterOperator
from utils.enums import FilterOn

print("RUNNING")

print(sys.version)
#Open Project
myProject = controller.open_project('ca_marche', '/home/sloury/Documents/MIA2/BDD/ca_marche')

#for tagname in myProject.getAllTagsNames():
#    print('TAG NAME '+tagname)

#GET ALL INPUTS
allInputs = myProject._get_scans()

#Create a new PIpeline and set it in Tree TreePipeline as basis
mainPipeline = Pipeline('MainPipeline')
print("Pipeline "+mainPipeline.name+' '+str(mainPipeline.uid))
mainTreePipeline = TreePipeline(mainPipeline);
#This mainPipeline is the first entry of all inputs
mainPipeline._get_inputScans().extend(allInputs)
#For now we have to set outputs = inputs for testing
mainPipeline._get_outputScans().extend(mainPipeline._get_inputScans())
print('PIPELINE SIZE OF INPUTS SCANS '+str(len(mainPipeline._get_inputScans())))
print('PIPELINE SIZE OF OUTPUTS SCANS '+str(len(mainPipeline._get_outputScans())))


#for current in myProject.getAllTags():
    #print('Tag '+current.name+' value '+current.value)
#Create Launcher templates
#SPM Launcher template
templateSPM = LauncherTemplate('SPM','spm')
#ASL launcher template
templateASL = LauncherTemplate('ASL','asl')
#Custom launcher template
templateCustom = LauncherTemplate('Custom','custom')

#Launchers
launcherT2_SPM  = ModuleLauncher('T2_SPM',templateSPM)
launcherT1_SPM  = ModuleLauncher('T1_SPM',templateSPM)
launcherGrub_ASL  = ModuleLauncher('Grub_ASL',templateASL)
launcher_Average_Calculator = ModuleLauncher('AverageCalculator',templateCustom)
launcher_Matrice_Applicator = ModuleLauncher('MatriceT1Applicator',templateCustom)

#The Launcher Matric Applicator MUST consumes a matrice defined as an Argument File Type
argMatrice = ArgumentFile('mymatrice','/path/to/my/matrice')
#It will also apply only on Scans tagged T1
filterT1 = Filter(FilterOn.TAG,'T1', None ,True,True,FilterOperator.OR)
filterSeriesDescription = Filter(FilterOn.TAG,'SeriesDescription', '02_MTI-T1' ,True,True,FilterOperator.OR)

#Then we can add those constraints as a consumers of the MatriceT1ApplicatorLauncher
launcher_Matrice_Applicator._get_consumes().append(argMatrice)
launcher_Matrice_Applicator._get_consumes().append(filterT1)
launcherT1_SPM.addConsumesConstraint(filterSeriesDescription)

#Add consumes constraint on launcherT2_SPM
#It will only consumes scans that are T2 tagged
filterT2 = Filter(FilterOn.TAG,'T2', None, True,True,FilterOperator.OR)
launcherT2_SPM.addConsumesConstraint(filterT2)

#Then we create Modules that are the elements that will be used to run data processing
moduleT1_SPM = Module('MODULE T1 SPM', launcherT1_SPM)
moduleT2_SPM = Module('MODULE T2 SPM', launcherT2_SPM)
moduleGrub_ASL = Module('MODULE Grub ASL', launcherGrub_ASL)
moduleAverage = Module('MODULE AVERAGE', launcher_Average_Calculator)
moduleMatrice = Module('MODULE MATRICE', launcher_Matrice_Applicator)

#Print consumes of moduleT1_SPM, should be same as launcherT1_SPM
print('moduleT1_SPM Consumes :')
for consume in moduleT1_SPM._get_consumes():
    print('TYPE '+type(consume).__name__)
    print(' filterOn: '+consume.filterOn.value)
    print(' name:'+str(consume.name))
    print(' value:'+str(consume.value))

#Create tree executors for those modules
executorT1_SPM = TreeExecutor(moduleT1_SPM)
print('executorT1_SPM get input filters :')
for consume in executorT1_SPM._get_inputFilters():
    print('TYPE '+type(consume).__name__)
    print(' filterOn: '+consume.filterOn.value)
    print(' name:'+str(consume.name))
    print(' value:'+str(consume.value))
    
#We want to use executorT1_SPM
#We want to iterate on SeriesDescription as Patient ID is always the same
treeIterator = TreeIterator(Filter(FilterOn.TAG,'SeriesDescription', None, False, False, FilterOperator.OR), [executorT1_SPM]) 
#Create the first level of the pipeline tree
mainPipeline.addLevel(1)
print('SIZE OF PIPELINE AFTER ADD LEVEL '+str(len(mainPipeline.tree.keys())))
#Set up a tree iterator at the first level of the main pipeline
mainPipeline.addOperatorOnLevel(1,treeIterator)

print('SIZE OF PIPELINE AFTER ADD OPERATOR ON LEVEL '+str(len(mainPipeline.tree.keys())))

#As the iterator is on level 1, its previousOperator is the mainPipeline
treeIterator._previousTreeOperators.append(mainTreePipeline)
print('PREVIOUS OPERATORS')
for pv in treeIterator._get_previousTreeOperators():
    print('pv '+pv.getClassName()+' '+str(pv.uid))
#Then set inputs filtered to its TreeOperator
#the problem is that the executor in the pipeline cant get its inputs from previous pipeline as its is the one running and running the operators inside it
#get level for iteraotr
#treeIterator.execute()


#Tries t filter input at the entry of T1 module
#print('allInputs size before filtering on 02_MTI-T1 '+str(len(allInputs)))
#print('Filtering on T1 from moduleT1_SPM ...')
#filteredInputs = executorT1_SPM.filterInputs(allInputs)
#print('filteredInputs size after filtering on 02_MTI-T1 '+str(len(filteredInputs)))


executorT1_SPM._get_inputFilters().append(filterT1)
#Same thing for T2
executorT2_SPM = TreeExecutor(moduleT2_SPM)

executorT2_SPM._get_inputFilters().append(filterT2)
#Executor for GrubASL module
executorGrubASL = TreeExecutor(moduleGrub_ASL)
#Executor for Average module
executorAverage = TreeExecutor(moduleAverage)
#For the matrice, we alreayd know what it is supposed to consumes, so it will automatically add filters from child to parent
#On the init of a module executor, add filter from consumes
executorMatrice = TreeExecutor(moduleMatrice)

#Then create a pipeline from those module executors



#Execute makepipeline
mainTreePipeline.execute()