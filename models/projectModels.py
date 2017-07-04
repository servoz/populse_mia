from models.generics import GenericItem
from utils.enums import TagType

class Tag(GenericItem):

    def __init__(self, name, replace, value, origin):
        GenericItem.__init__(self)
        self.name = name
        self.replace = replace
        self.value = value
        self.origin = origin


class Scan(GenericItem):

    def __init__(self, file_path):
        GenericItem.__init__(self)
        self.file_path = file_path
        self._tags = []
        self._delete_tags = []

    def _get_tags(self):
        return self._tags

    def _get_delete_tags(self):
        return self._delete_tags

    def _get_json_tags(self):
        return self._json_tags

    def _get_nifti_tags(self):
        return self._nifti_tags

    def _get_custom_tags(self):
        return self._custom_tags
    
    def getAllTags(self):
        result = []
        for origin in TagType:
            result.extend(self.getAllTagsByOrigin(origin.value))
        return result    
   
    def getAllTagsByOrigin(self,origin):
        result = []
        deleteTag = []
        replaceTag = []
        for tag in self._get_delete_tags():
            if tag not in deleteTag and tag.origin == origin:
                deleteTag.append(tag)
                #print('DELETED '+tag.name + ' '+tag.value)
        for tag in self._get_tags():
            #print('INTO GET TAGS '+tag.name + ' '+tag.value)
            if tag not in deleteTag and tag not in result and tag.origin == origin:
                #print('TAG TO BE ADDED '+tag.name + ' '+tag.value)
                if tag.replace != "":
                    result.append(tag)
                    replaceTag.append(tag.replace)
                    for l_tag in result:
                        if l_tag.name == tag.replace:
                            result.remove(l_tag)
                            deleteTag.append(l_tag)
                else:
                    if tag.name in replaceTag:
                        deleteTag.append(tag)
                    else:
                        result.append(tag)
            else:
                pass
        return result
    
    def getAllTagsNames(self):
        result = []
        for origin in TagType:
            result.extend(self.getAllTagsNamesByOrigin(origin))
        return result

    def getAllTagsNamesByOrigin(self, origin):
        result = []
        deleteTag = []
        replaceTag = []
        for tag in self._get_delete_tags():
            if tag.name not in deleteTag and tag.origin == origin.value:
                deleteTag.append(tag.name)
        for tag in self._get_tags():
            if tag.name not in deleteTag and tag.name not in result and tag.origin == origin.value:
                if tag.replace != "":
                    result.append(tag.name)
                    replaceTag.append(tag.replace)
                    for l_tag in result:
                        if l_tag == tag.replace:
                            result.remove(l_tag)
                            deleteTag.append(l_tag)
                else:
                    if tag.name in replaceTag:
                        deleteTag.append(tag.name)
                    else:
                        result.append(tag.name)
            else:
                pass
        return result

    def addTag(self, tagtype, tag):
        if (tagtype == TagType.JSON):
            self._get_tags().append(tag)
        if (tagtype == TagType.NIFTI):
            self._get_tags().append(tag)
        if (tagtype == TagType.CUSTOM):
            self._get_tags().append(tag)
        return self

    def addJsonTag(self, tag):
        self.addTag(TagType.JSON, tag)

    def addNiftiTag(self, tag):
        self.addTag(TagType.NIFTI, tag)

    def addCustomTag(self, tag):
        self.addTag(TagType.CUSTOM, tag)

    def delete_tag(self, tag):
        self._get_delete_tags().append(tag)

class ProjectLight(GenericItem):

    def __init__(self, name):
        GenericItem.__init__(self)
        from time import strftime,localtime
        self.name = name
        self.folder = ""
        self.raw_data = ""
        self.processed_data = ""
        self.bdd_file = ""
        self.date = strftime('%d/%m/%y %H:%M', localtime())
        
class Project(ProjectLight):

    def __init__(self, name):
        ProjectLight.__init__(self,name)
        self._scans = []

    def _get_scans(self):
        return self._scans

    def addScan(self, scan):
        self._get_scans().append(scan)
        
    def addScans(self, scans):
        for scan in scans:
            self.addScan(scan)

    def getAllTags(self):
        result = []
        for origin in TagType:
            result.extend(self.getAllTagsByOrigin(origin))
        return result
    
    def getAllTagsByOrigin(self,origin):
        result = []
        if(isinstance(self, Project)):
            for i in self._get_scans():
                for y in i.getAllTagsByOrigin(origin):
                    if y not in result and y.origin == origin.value:
                        result.append(y)
        

    def getAllTagsNames(self):
        result = []
        for origin in TagType:
            result.extend(self.getAllTagsNamesByOrigin(origin))
        return result

    def getAllTagsNamesByOrigin(self, origin):
        result = []
        if(isinstance(self, Project)):
            result = []
            for scan in self._get_scans():
                for tagname in scan.getAllTagsNamesByOrigin(origin):
                    if tagname not in result:
                        result.append(tagname)
        return result


    

        
        