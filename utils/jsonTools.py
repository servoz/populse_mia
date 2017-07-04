import os
import pathlib
import json
from models.projectModels import Project,Scan,Tag
from models.pipelineModels import *
from utils.enums import TagType


def serializer(obj):
    if isinstance(obj, Project):
        return {'__class__': 'Project',
                'uid': obj.uid,
                'name': obj.name,
                'bdd_file': obj.bdd_file,
                'folder': obj.folder,
                'raw_data': obj.raw_data,
                'processed_data': obj.processed_data,
                'date': obj.date,
                'scans': obj._get_scans()}

    if isinstance(obj, Scan):
        """'_json_tags': obj._get_json_tags(),
        '_nifti_tags': obj._get_nifti_tags(),
        '_custom_tags': obj._get_custom_tags()}"""
        return {'__class__': 'Scan',
                'uid': obj.uid,
                'file_path': obj.file_path,
                'tags': obj._get_tags(),
                'delete_tags': obj._get_delete_tags()}


    if isinstance(obj, Tag):
        return {'__class__': 'Tag',
                'uid': obj.uid,
                'name': obj.name,
                'replace':obj.replace,
                'value': str(obj.value),
                'origin': obj.origin.value}

    raise TypeError(repr(obj) + " is not serializable !")


def deserializer(obj_dict):
    if "__class__" in obj_dict:
        if obj_dict["__class__"] == "Project":
            obj = Project(obj_dict["name"])
            obj.uid = obj_dict["uid"]
            obj.folder = obj_dict["folder"]
            obj.raw_data = obj_dict["raw_data"]
            obj.processed_data = obj_dict["processed_data"]
            obj.bdd_file = obj_dict["bdd_file"]
            obj.date = obj_dict["date"]
            obj._scans = obj_dict["scans"]
            return obj
        if obj_dict["__class__"] == "Scan":
            obj = Scan(obj_dict["file_path"])
            obj.uid = obj_dict["uid"]
            obj._tags = obj_dict["tags"]
            obj._delete_tags = obj_dict["delete_tags"]
            return obj
        if obj_dict["__class__"] == "Tag":
            obj = Tag(obj_dict["name"],obj_dict["replace"],obj_dict["value"],TagType[obj_dict["origin"]])
            obj.uid = obj_dict["uid"]
            return obj
    return obj_dict



def parseFolderContent(pathToFolder,project):
    for dirname, dirnames, filenames in os.walk(pathToFolder):
        for filename in filenames:
            fullElementName = os.path.splitext(os.path.join(dirname, filename))[0]
            #Don't create element for all filenames
            #print("projet "+project.elements)
            isNew = False;
            element = findElementByName(project.elements, fullElementName)            
            if  element is None:
                element = Element(fullElementName)
                isNew = True
            if filename.endswith(".json"):
                element.pathJson = os.path.join(dirname, filename)
            if filename.endswith(".nii"):
                element.pathNii = os.path.join(dirname, filename)
            #Add new element to project only if is new ro we'll have duplicate elements from json/nii
            if isNew:
                project.elements.append(element)
    return project

#Here we parse a json to get all existings tags
def parseJsonForTags(json_data):
    tagsInJson = []
    for k in json_data:
        tagsInJson.append(Tag(k,json_data[k]))
    return tagsInJson


#We an define a list of tag we don't want 
unwantedTags = ["InstanceNumber","SOPClassUID"]

def addTagsFromJsonFiles(project):
    for element in project.elements:
        if element.pathJson != None and element.pathJson != "":
            with open(element.pathJson, "r") as json_file:
                json_data = json.load(json_file)
                #Then add all parsed tags to element
                for tag in parseJsonForTags(json_data):
                    if tag.name not in unwantedTags:
                        #print("NOT IN "+tag.name)
                        addOrUpdateTag(element, tag)
                    """else:
                        print("FORBIDDEN TAG "+tag.name)
            """
            
