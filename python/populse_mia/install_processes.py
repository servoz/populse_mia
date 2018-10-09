"""
Script used to install MIA processes easily.
MIA_processes.zip needs to be placed in MIA's root folder (same place as this script)

"""

import os
import sys
import yaml
import zipfile
import inspect
import pkgutil

# Soma import
from soma.path import find_in_path

###################################################################
# ZIP FILE TO UNZIP
#
path_to_zip_file = 'MIA_processes.zip'
#
###################################################################


def add_package(proc_dic, module_name):
    """
    Adds a package and its modules to the package tree


    :param proc_dic: the process tree-dictionary
    :param module_name: name of the module
    :return: proc_dic: the modified process tree-dictionary
    """

    if module_name:

        # Reloading the package
        if module_name in sys.modules.keys():
            del sys.modules[module_name]

        __import__(module_name)
        pkg = sys.modules[module_name]

        # Checking if there are subpackages
        for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
            if ispkg:
                add_package(proc_dic, str(module_name + '.' + modname))

        for k, v in sorted(list(pkg.__dict__.items())):
            # Checking each class of in the package
            if inspect.isclass(v):
                try:
                    find_in_path(k)
                except:
                    pass
                else:
                    # Updating the tree's dictionnary
                    path_list = module_name.split('.')
                    path_list.append(k)
                    pkg_iter = proc_dic
                    for element in path_list:
                        if element in pkg_iter.keys():
                            pkg_iter = pkg_iter[element]
                        else:
                            if element is path_list[-1]:
                                pkg_iter[element] = 'process_enabled'
                            else:
                                pkg_iter[element] = {}
                                pkg_iter = pkg_iter[element]

        return proc_dic


if __name__ == '__main__':

    # Extraction of the zipped content
    print("Extracting MIA processes...")
    if os.path.isfile(path_to_zip_file):
        zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    else:
        raise FileNotFoundError("File {0} not found in MIA's root folder".format(path_to_zip_file))

    zip_ref.extractall('processes')
    zip_ref.close()

    print("MIA processes extracted")

    # Process config update
    print("Updating process config...")
    if not os.path.isfile(os.path.join('properties', 'process_config.yml')):
        open(os.path.join('properties', 'process_config.yml'), 'a').close()

    with open(os.path.join('properties', 'process_config.yml'), 'r') as stream:
        try:
            process_dic = yaml.load(stream)
        except yaml.YAMLError as exc:
            process_dic = {}
            print(exc)

    if process_dic is None:
        process_dic = {}

    try:
        packages = process_dic["Packages"]
    except KeyError:
        packages = {}
    except TypeError:
        packages = {}

    try:
        paths = process_dic["Paths"]
    except KeyError:
        paths = []
    except TypeError:
        paths = []

    sys.path.append(os.path.join('processes'))
    final_package_dic = add_package(packages, "MIA_processes")

    if not os.path.abspath(os.path.join('processes')) in paths:
        paths.append(os.path.abspath(os.path.join('processes')))

    process_dic["Packages"] = final_package_dic
    process_dic["Paths"] = paths
    # Idea: Should we encrypt the path ?

    with open(os.path.join('properties', 'process_config.yml'), 'w', encoding='utf8') as stream:
        yaml.dump(process_dic, stream, default_flow_style=False, allow_unicode=True)

    print("Process config updated")
    print("")
