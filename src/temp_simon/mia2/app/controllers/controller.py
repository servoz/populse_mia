import glob
import os.path
import json
#import nibabel as nib
from app.models.projectBuildModels import Project,Tag,Scan
from app.utils import utils as utils
from app.utils import jsonTools as jsonTools
from app.utils.enums import TagType
import shutil




"""test = listdirectory('test', 'D:\data_nifti_json')
print(showResults(test))"""
"""test = modified_tag_name(test, 'InversionTime', 'AAAAA')
print(showResults(test))
print(Project.getAllTagsNames(test))
print(type(test))"""
#print(listdirectory('D:\data_nifti_json'))
#print("le resultat est: ", getAllTagsFile("D:\\data_nifti_json\\1_Rat_M10_J15\\393217_03_pCASL\\1", listdirectory('D:\data_nifti_json')))
#print(len(getAllTagsFile("D:\\data_nifti_json\\1_Rat_M10_J15\\393217_03_pCASL\\1", listdirectory('D:\data_nifti_json'))))
#print("le resultat est: ", getAllTags(listdirectory('D:\data_nifti_json')))
#print(len(getAllTags(listdirectory('D:\data_nifti_json'))))
#print(len(listdirectory('D:\data_nifti_json')._get_scans()))

"""utils.saveJsonFile("Json1", listdirectory('D:\data_nifti_json'))
utils.findPath("json1.json")"""
#print(showResults(listdirectory('D:\data_nifti_json')))
#print(json.dumps(listdirectory('D:\data_nifti_json'), default=serializer))

#print(len((listdirectory('D:\data_nifti_json')).getAllTagsNames()))
#
#print(showResults(createProject('test4', 'D:\data_nifti_json', 'C:\\Users\Roxane\Desktop')))
#print(showResults(open_project('test4', 'C:\\Users\Roxane\Desktop\\test4')))


#createProject('ca_marche', 'D:\data_nifti_json')



#print(showResults(open_project('ca_marche', 'C:\\Users\Roxane\PycharmProjects\BDD\\test')))