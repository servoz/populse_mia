class Tag:

    def __init__(self, name, replace, value, origin):
        self.name = name
        self.replace = replace
        self.value = value
        self.origin = origin


class Scan:

    def __init__(self, uid, file_path):
        self.uid = uid
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
        deleteTag = []
        replaceTag = []
        for tag in self._get_delete_tags():
            if tag not in deleteTag:
                deleteTag.append(tag)
        for tag in self._get_tags():
            if tag not in deleteTag and tag not in result:
                # If the tag has to replace another one (that is specified in tag.replace)
                if tag.replace != "":
                    # The tag is added in the result list
                    result.append(tag)
                    # The tag that has to be replaced is placed in the replaceTag list
                    replaceTag.append(tag.replace)
                    for l_tag in result:
                        # The tag that has to be replaced is eventually deleted
                        if l_tag.name == tag.replace:
                            result.remove(l_tag)
                            deleteTag.append(l_tag)
                # If there is no need to replace another tag
                else:
                    # Checking if this tag has to be replaced
                    if tag.name in replaceTag:
                        deleteTag.append(tag)
                    else:
                        result.append(tag)
            else:
                pass
        return result

    def getAllTagsNames(self):
        result = []
        deleteTag = []
        replaceTag = []
        for tag in self._get_delete_tags():
            if tag.name not in deleteTag:
                deleteTag.append(tag.name)
        for tag in self._get_tags():
            if tag.name not in deleteTag and tag.name not in result:
                # If the tag has to replace another one (that is specified in tag.replace)
                if tag.replace != "":
                    # The tag is added in the result list
                    result.append(tag.name)
                    # The tag that has to be replaced is placed in the replaceTag list
                    replaceTag.append(tag.replace)
                    for l_tag in result:
                        # The tag that has to be replaced is eventually deleted
                        if l_tag == tag.replace:
                            result.remove(l_tag)
                            deleteTag.append(l_tag)
                # If there is no need to replace another tag
                else:
                    # Checking if this tag has to be replaced
                    if tag.name in replaceTag:
                        deleteTag.append(tag.name)
                    else:
                        result.append(tag.name)
            else:
                pass
        return result


    def addTag(self, tagtype, tag):
        if (tagtype == "json"):
            self._get_tags().append(tag)
        if (tagtype == "nifti"):
            self._get_tags().append(tag)
        if (tagtype == "custom"):
            self._get_tags().append(tag)
        return self

    def addJsonTag(self, tag):
        self.addTag("json", tag)

    def addNiftiTag(self, tag):
        self.addTag("nifti", tag)

    def addCustomTag(self, tag):
        self.addTag("custom", tag)

    def delete_tag(self, tag):
        self._get_delete_tags().append(tag)

class Project:

    def __init__(self, name):
        import time
        self.name = name
        self.folder = ""
        self.bdd_file = ""
        self.date = time.strftime('%d/%m/%y %H:%M', time.localtime())
        self._scans = []

    def _get_scans(self):
        return self._scans

    def addScan(self, scan):
        self._get_scans().append(scan)

    def getAllTags(self):
        result = []
        for i in self._get_scans():
            for y in i.getAllTags():
                if y not in result:
                    result.append(y)
        return result

    def getAllTagsNames(self):
        result = []
        for scan in self._get_scans():
            for tagname in scan.getAllTagsNames():
                if tagname not in result:
                    result.append(tagname)
        return result


def serializer(obj):
    if isinstance(obj, Project):
        return {'__class__': 'Project',
                'name': obj.name,
                'bdd_file': obj.bdd_file,
                'folder': obj.folder,
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
                'name': obj.name,
                'replace':obj.replace,
                'value': str(obj.value),
                'origin': obj.origin}

    raise TypeError(repr(obj) + " is not serializable !")


def deserializer(obj_dict):
    if "__class__" in obj_dict:
        if obj_dict["__class__"] == "Project":
            obj = Project(obj_dict["name"])
            obj.folder = obj_dict["folder"]
            obj.bdd_file = obj_dict["bdd_file"]
            obj.date = obj_dict["date"]
            obj._scans = obj_dict["scans"]
            return obj
        if obj_dict["__class__"] == "Scan":
            obj = Scan(obj_dict["uid"], obj_dict["file_path"])
            obj._tags = obj_dict["tags"]
            obj._delete_tags = obj_dict["delete_tags"]
            return obj
        if obj_dict["__class__"] == "Tag":
            obj = Tag(obj_dict["name"],obj_dict["replace"],obj_dict["value"],obj_dict["origin"])
            return obj
    return obj_dict