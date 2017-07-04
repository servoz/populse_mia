from os import path,listdir,walk
import glob
import shutil
import fnmatch


def getFilePathWithoutExtension(filename, folder):
    filepath = path.join(folder,filename)
    return filepath[:filepath.rfind('.')]


def getFilesFromFolder(folder_path, file_type):
    resultList = []
    #DEPENDING ON WHICH VERSION OF PYTHON IS RUNNING...
    #globPattern = folder_path+'/**/*.'+file_type
    #for current in (glob.glob(globPattern)) :
    #    resultList.append(getFilePathWithoutExtension(current, folder_path))
    
    for root, dirnames, filenames in walk(folder_path):
        for filename in fnmatch.filter(filenames, '*.'+file_type):
            resultList.append(getFilePathWithoutExtension(filename, root))    
        
    return resultList
    
def copytree(src, dst, symlinks=False, ignore=None):
    for item in listdir(src):
        s = path.join(src, item)
        d = path.join(dst, item)
        if path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def substractLists(listA,listB):
    return list(set(listA) - set(listB))

def createJsonFile(path_to_file,filename):
    open(path.join(path_to_file,filename+'.json'), 'w')
    return filename+'.json'

def saveProjectAsJsonFile(project):
    import json
    from utils import jsonTools
    with open(project.bdd_file, 'w') as f:
        f.write(json.dumps(project, default=jsonTools.serializer))

def findPath(name_file):
    from os import path as os_path
    return (os_path.abspath(os_path.split(name_file)[0]))

def cleanStringForSysName(strToClean):
    return remove_accents((strToClean.lower()).replace(" ", "_"))

def remove_accents(txt):
    ch1 = u"àâçéèêëîïôùûüÿ"
    ch2 = u"aaceeeeiiouuuy"
    s = ""
    for c in txt:
        i = ch1.find(c)
        if i >= 0:
            s += ch2[i]
        else:
            s += c
    return s

def normalize_caseless(text):
    import unicodedata
    return unicodedata.normalize("NFKD", text.casefold())

def normalize_casewith(text):
    import unicodedata
    return unicodedata.normalize("NFKD", text)

#USED FOR TESTING ONLY
def cleanTagValue(tagValue):
    tagValue = tagValue.replace("[", "")
    tagValue = tagValue.replace("]", "")
    tagValue = tagValue.replace("'", "")
    return tagValue


    