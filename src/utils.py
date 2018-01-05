def getFilePathWithoutExtension(filepath, path):
    return filepath[len(path):filepath.rfind('.')]


def substractLists(listA,listB):
    """

    :param listA: a list
    :param listB: a list
    :return: a list of the elements that are in listA and not in listB
    """
    return list(set(listA) - set(listB))

def createJsonFile(path, name):
    open(path+name+'.json', 'w')
    return name+'.json'

def saveProjectAsJsonFile(name, project):
    import json
    from models import serializer
    with open(name+'.json', 'w') as f:
        f.write(json.dumps(project, default=serializer))

def findPath(name_file):
    from os import path as os_path
    return (os_path.abspath(os_path.split(name_file)[0]))

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