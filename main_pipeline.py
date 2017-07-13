import json
import sys
from models.pipelineModels import *
from models.projectModels import *
from controllers.projectController import *
from controllers.pipelineController import *
from utils import utils
from utils.enums import FilterOperator
from utils.enums import FilterOn
from config.config import Config

print("RUNNING")

print(sys.version)
#Open Project to get inputs
#Try to load the config
config = Config()
print('IS MY CONFIG NULL ? '+str(config))
#The instantiate the Project controller
projectController = ProjectController(config)
projectController.loadProject('8f02013b-7453-43cf-be1a-9509d118abac')
#My inputs scans for running pipeline
inputs = projectController.activeProject._get_scans()
print("INPUTS READY FOR PIPELINE "+str(len(inputs)))

#Create a new Pipeline Controller
pipelineController = PipelineController(config)
#Create a new Pipeline 
mainPipeline = Pipeline('MainPipeline')
print("Pipeline "+mainPipeline.name+' '+str(mainPipeline.uid))
#Set the pipeline onto controller
pipelineController.pipeline = mainPipeline

#Create the pipeline elements
#Create Launcher templates
#Launcher templates
templateSPM = LauncherTemplate('SPM','spm')
templateASL = LauncherTemplate('ASL','asl')
templateCustom = LauncherTemplate('Custom','custom')

#Launchers
launcherT2_SPM  = ModuleLauncher('T2_SPM',templateSPM)
launcherT1_SPM  = ModuleLauncher('T1_SPM',templateSPM)
launcherGrub_ASL  = ModuleLauncher('Grub_ASL',templateASL)
launcher_Average_Calculator = ModuleLauncher('AverageCalculator',templateCustom)
launcher_Matrice_Applicator = ModuleLauncher('MatriceT1Applicator',templateCustom)

#Modules
moduleT1_SPM = Module('MODULE T1 SPM', launcherT1_SPM)
moduleT2_SPM = Module('MODULE T2 SPM', launcherT2_SPM)
moduleGrub_ASL = Module('MODULE Grub ASL', launcherGrub_ASL)
moduleAverage = Module('MODULE AVERAGE', launcher_Average_Calculator)
moduleMatrice = Module('MODULE MATRICE', launcher_Matrice_Applicator)

#Filters
filterT1 = Filter(FilterOn.TAG,'T1', None ,True,True,FilterOperator.OR)
filterT2 = Filter(FilterOn.TAG,'T2', None, True,True,FilterOperator.OR)
filterSeriesDescription = Filter(FilterOn.TAG,'SeriesDescription', '02_MTI-T1' ,True,True,FilterOperator.OR)

#TreeOperators
executorT1_SPM = TreeExecutor(moduleT1_SPM, mainPipeline)
executorT1_SPM.uid = "MY EXECUTOR T1"
treeIterator = TreeIterator(Filter(FilterOn.TAG,'SeriesDescription', None, False, False, FilterOperator.OR), [executorT1_SPM],mainPipeline) 
treeIterator.uid = "MY ITERATOR "
executorT2_SPM = TreeExecutor(moduleT2_SPM, mainPipeline)
executorT2_SPM.uid = "MY EXECUTOR T2 "
executorGrubASL = TreeExecutor(moduleGrub_ASL, mainPipeline)
executorAverage = TreeExecutor(moduleAverage, mainPipeline)
executorMatrice = TreeExecutor(moduleMatrice, mainPipeline)

#Build the pipeline
mainPipeline.addOperator(executorT2_SPM)
mainPipeline.addOperator(treeIterator)
pipelineController.addLink(executorT2_SPM,treeIterator)
treeIterator.addOperator(executorT1_SPM)
print(mainPipeline.tree)

#Execute pipeline
pipelineController.launchPipeline(inputs)