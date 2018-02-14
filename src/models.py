class Tag:

    def __init__(self, name, replace, value, origin, original_value):
        self.name = name
        self.replace = replace
        self.value = value
        self.origin = origin
        self.original_value = original_value

    def resetTag(self):
        self.value = self.original_value

    def cloneTag(self, new_name):
        return Tag(new_name, self.replace, self.value, "custom", self.original_value)

class Scan:

    def __init__(self, uid, file_path):
        self.uid = uid
        self.file_path = file_path
        self._tags = []
        self._delete_tags = []

    def __lt__(self, other):
        return self.file_path < other.file_path

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
            if tag.name in deleteTag:
                result.append(tag)
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
            if tag.name in deleteTag:
                result.append(tag.name)

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

    def replaceTag(self, tag_to_add, tag_name_to_replace, tag_type):

        for tag in self.getAllTags():
            if tag.name == tag_name_to_replace:
                self._tags.remove(tag)
        self.addTag(tag_type, tag_to_add)


    def addTag(self, tagtype, tag):
        if tagtype == "json" or tagtype == "Json":
            self._get_tags().append(tag)
        if tagtype == "nifti" or tagtype == "Nifti":
            self._get_tags().append(tag)
        if tagtype == "custom" or tagtype == "Custom":
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

    def delete_tag_by_name(self, tag_name):
        for tag in self.getAllTags():
            if tag.name == tag_name:
                self._tags.remove(tag)

class Project:

    def __init__(self, name):
        import time
        self.name = name
        self.folder = ""
        self.bdd_file = ""
        self.date = time.strftime('%d/%m/%y %H:%M', time.localtime())
        self._scans = []
        self.user_tags = []
        self.sort_tags = ['FileName']
        self.sort_order = "ascending"
        self.tags_to_visualize = ['FileName', 'PatientName', 'AcquisitionDate']  # Has to be read from MIA2 preferences later

    def add_user_tag(self, name, original_value):
        self.user_tags.append({'name': name, 'original_value': original_value})

    def remove_user_tag(self, name):
        for tag in self.user_tags:
            if tag['name'] == name:
                self.user_tags.remove()

    def _get_scans(self):
        return self._scans

    def addScan(self, scan):
        self._get_scans().append(scan)

    def getAllTags(self):
        result = []
        for scan in self._get_scans():
            tags = scan.getAllTags()
            for i in range(len(tags)):
                if tags[i] not in result:
                    result.append(tags[i])
        return result

    def getAllTagsNames(self):
        result = []
        for scan in self._get_scans():
            tagnames = scan.getAllTagsNames()
            for i in range(len(tagnames)):
                if tagnames[i] not in result:
                    result.append(tagnames[i])

        return result

    def add_tag(self, tag):
        for scan in self._get_scans():
            scan.addTag("custom", tag)

    def remove_tag_by_name(self, tag_name):
        for user_tag in self.user_tags:
            if user_tag['name'] == tag_name:
                self.user_tags.remove(user_tag)
                self.tags_to_visualize.remove(tag_name)
        for scan in self._get_scans():
            scan.delete_tag_by_name(tag_name)

    def clone_tag(self, tag_to_clone, new_tag_name):
        # Finding the tag to clone (getting the original value)
        i = 0
        for scan in self._get_scans():
            if i == 1:
                break
            for tag in scan.getAllTags():
                if tag.name == tag_to_clone:
                    original_value = tag.original_value
                    self.add_user_tag(new_tag_name, original_value)
                    i += 1
                    break

        # Cloning it
        for scan in self._get_scans():
            for tag in scan.getAllTags():
                if tag.name == tag_to_clone:
                    new_tag = tag.cloneTag(new_tag_name)
                    scan.addTag(tag.origin, new_tag)

    def remove_scan(self, scan_path):
        for scan in self._get_scans():
            if scan.file_path == scan_path:
                self._scans.remove(scan)

    def reset_sort_tags(self):
        self.sort_tags = []

    def add_sort_tag(self, tag_name):
        self.sort_tags.append(tag_name)

    def sort_by_tags(self):
        # for tag_name in self.sort_tags: #TODO: HAVE TO DEAL WITH THE MULTISORTING CASE
        tag_name = self.sort_tags[0]
        list_tags = []
        for scan in self._get_scans():
            for tag in scan.getAllTags():
                if tag.name == tag_name:
                    list_tags.append(tag.value[0])

        # Sorting according to the tag values
        if self.sort_order == "ascending":
            self._scans = [x for _, x in sorted(zip(list_tags, self._scans))]
        elif self.sort_order == "descending":
            self._scans = [x for _, x in sorted(zip(list_tags, self._scans), reverse=True)]


def serializer(obj):
    import numpy as np
    if isinstance(obj, Project):
        return {'__class__': 'Project',
                'name': obj.name,
                'bdd_file': obj.bdd_file,
                'folder': obj.folder,
                'date': obj.date,
                'scans': obj._get_scans(),
                'user_tags': obj.user_tags,
                'sort_tags': obj.sort_tags,
                'sort_order': obj.sort_order,
                'tags_to_visualize': obj.tags_to_visualize}

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
        if type(obj.value) is np.ndarray:
            value = obj.value.tolist()
        elif isinstance(obj.value, bytes):
            print(obj.name)
            value = obj.value.decode('utf-8')
        else:
            value = obj.value

        if type(obj.original_value) is np.ndarray:
            original_value = obj.original_value.tolist()
        elif isinstance(obj.original_value, bytes):
            original_value = obj.original_value.decode('utf-8')
        else:
            original_value = obj.original_value
        return {'__class__': 'Tag',
                'name': obj.name,
                'replace': obj.replace,
                'value': value, #str(obj.value)
                'origin': obj.origin,#str(obj.original_value) below
                'original_value': original_value}

    raise TypeError(repr(obj) + " is not serializable !")


def deserializer(obj_dict):
    if "__class__" in obj_dict:
        if obj_dict["__class__"] == "Project":
            obj = Project(obj_dict["name"])
            obj.folder = obj_dict["folder"]
            obj.bdd_file = obj_dict["bdd_file"]
            obj.date = obj_dict["date"]
            obj._scans = obj_dict["scans"]
            obj.user_tags = obj_dict["user_tags"]
            obj.sort_tags = obj_dict["sort_tags"]
            obj.sort_order = obj_dict["sort_order"]
            obj.tags_to_visualize = obj_dict["tags_to_visualize"]
            return obj
        if obj_dict["__class__"] == "Scan":
            obj = Scan(obj_dict["uid"], obj_dict["file_path"])
            obj._tags = obj_dict["tags"]
            obj._delete_tags = obj_dict["delete_tags"]
            return obj
        if obj_dict["__class__"] == "Tag":
            obj = Tag(obj_dict["name"], obj_dict["replace"], obj_dict["value"], obj_dict["origin"],
                      obj_dict["original_value"])

            return obj
    return obj_dict