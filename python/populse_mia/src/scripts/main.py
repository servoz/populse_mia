#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
import os

from PyQt5.QtCore import QDir, QLockFile
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from Project.Project import Project
from SoftwareProperties.Config import Config
import pkgutil
import inspect
from soma.path import find_in_path
import yaml

imageViewer = None

"""
@atexit.register
"""


def clean_up():
    """
    Cleans up the software during "normal" closing
    """

    global imageViewer

    print("clean up done")

    config = Config()
    opened_projects = config.get_opened_projects()
    opened_projects.remove(imageViewer.project.folder)
    config.set_opened_projects(opened_projects)
    imageViewer.remove_raw_files_useless()


class NipypePackages():
    def __init__(self):
        self.packages = {}

    def add_package(self, module_name, class_name=None):
        """
        Adds a package and its modules to the package tree

        :param module_name: name of the module
        :param class_name: name of the class
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
                    print(str(module_name + '.' + modname))
                    self.add_package(str(module_name + '.' + modname))

            for k, v in sorted(list(pkg.__dict__.items())):
                if class_name and k != class_name:
                    continue
                # Checking each class of in the package
                if inspect.isclass(v):
                    try:
                        find_in_path(k)
                        # get_process_instance(v)
                    except:
                        # TODO: WHICH TYPE OF EXCEPTION?
                        pass
                    else:
                        # Updating the tree's dictionnary
                        path_list = module_name.split('.')
                        path_list.append(k)
                        pkg_iter = self.packages
                        for element in path_list:
                            if element in pkg_iter.keys():
                                pkg_iter = pkg_iter[element]
                            else:
                                if element is path_list[-1]:
                                    pkg_iter[element] = 'process_enabled'
                                else:
                                    pkg_iter[element] = {}
                                    pkg_iter = pkg_iter[element]

            return self.packages


def verify_processes():
    """
    When the software is launched for the first time, adding all Nipype's interfaces to
    the available processes
    """

    if not os.path.isfile(os.path.join('..', '..', 'properties', 'process_config.yml')):
        try:
            __import__('nipype.interfaces')
        except ImportError as e:
            print('MIA warning: Nipype not found')
            print(e)
        nipype_pgks = NipypePackages()
        mod_name = 'nipype.interfaces'
        pkg_dic = nipype_pgks.add_package(mod_name)
        final_pkgs = {}
        final_pkgs["Packages"] = pkg_dic
        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'w', encoding='utf8') as stream:
            yaml.dump(final_pkgs, stream, default_flow_style=False, allow_unicode=True)


def launch_mia():
    global imageViewer

    def my_excepthook(type, value, tback):
        # log the exception here

        print("excepthook")

        clean_up()

        # then call the default handler
        sys.__excepthook__(type, value, tback)

        sys.exit(1)

    sys.excepthook = my_excepthook

    # Working from the scripts directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    lock_file = QLockFile(QDir.temp().absoluteFilePath('lock_file_populse_mia.lock'))
    if not lock_file.tryLock(100):
        # Software already opened in another instance
        pass
    else:
        # No instances of the software is opened, the list of opened projects can be cleared
        config = Config()
        config.set_opened_projects([])

    app = QApplication(sys.argv)

    project = Project(None, True)

    imageViewer = Main_Window(project)
    imageViewer.show()

    app.exec()


if __name__ == '__main__':

    # WILL BE REMOVED WHEN ISSUE #27 WILL BE RESOLVED
    """config = Config()
    spm_standalone_path = config.get_spm_standalone_path()
    matlab_standalone_path = config.get_matlab_standalone_path()

    # OS.ENVRION TEST
    _environ = os.environ.copy()
    try:
        _environ["FORCE_SPMMCR"] = '1'
        _environ["SPMMCRCMD"] = os.path.join(spm_standalone_path, 'run_spm12.sh') + ' ' + \
                                matlab_standalone_path + os.sep + " script"
    finally:
        os.environ.clear()
        os.environ.update(_environ)"""

    verify_processes()
    launch_mia()