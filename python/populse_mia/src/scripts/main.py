##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
import os
import yaml
import pkgutil
import inspect

# PyQt5 imports
from PyQt5.QtCore import QDir, QLockFile, Qt
from PyQt5.QtWidgets import QApplication

# Populse_MIA imports
from main_window.main_window import MainWindow
from project.project import Project
from software_properties.config import Config
from software_properties.saved_projects import SavedProjects

# soma-base imports
from soma.path import find_in_path
from soma.qt_gui.qt_backend.Qt import QMessageBox

# Warning: the "imageViewer" variable corresponds to a main_window object
main_window = None

"""
@atexit.register
"""


def clean_up():
    """
    Cleans up the software during "normal" closing
    """

    global main_window

    print("clean up done")

    config = Config()
    opened_projects = config.get_opened_projects()
    opened_projects.remove(main_window.project.folder)
    config.set_opened_projects(opened_projects)
    main_window.remove_raw_files_useless()


class NipypePackages:
    def __init__(self):
        self.packages = {}

    def add_package(self, module_name, class_name=None, flag=True):
        """
        Adds a package and its modules to the package tree

        :param module_name: name of the module
        :param class_name: name of the class
        """
        if module_name:

            # Reloading the package
            if module_name in sys.modules.keys():
                del sys.modules[module_name]

            try:   
                __import__(module_name)
                pkg = sys.modules[module_name]

                # Checking if there are subpackages
                for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                    
                    if ispkg:

                        if flag:
                            
                            print('\nExploring submodules of {0} ...\n'.format(module_name))
                            flag=False
                            
                        print(str(module_name + '.' + modname))
                        self.add_package(str(module_name + '.' + modname), flag=flag)

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

            except ModuleNotFoundError as e:
                pass
  
            return self.packages


def verify_processes():
    """
    When the software is launched, if Nipype's interfaces are yet unavailable,
    tries to make them available in the processes library
    """

    proc_content_flag = False

    if os.path.isfile(os.path.join('..', '..', 'properties', 'process_config.yml')):
                      
        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'r') as stream:
            proc_content = yaml.load(stream)
            proc_content_flag = True
            
    if (not proc_content_flag) or (
            proc_content_flag and not proc_content) or (
                 proc_content_flag and 'Packages' not in proc_content.keys()) or (
                    proc_content_flag and 'Packages' in proc_content.keys()
                    and 'nipype' not in proc_content['Packages'].keys()):  # test the short circuit

        try:
            __import__('nipype.interfaces')
            nipype_pgks = NipypePackages()
            mod_name = 'nipype.interfaces'
            pkg_dic = nipype_pgks.add_package(mod_name)
            final_pkgs = {}
            final_pkgs["Packages"] = pkg_dic
            
            if proc_content_flag and proc_content:

                if 'Packages' in proc_content:
                    for item in proc_content['Packages']:
                        final_pkgs['Packages'][item] = proc_content['Packages'][item]

                if 'Paths' in proc_content:
                    for item in proc_content['Paths']:
                        final_pkgs["Paths"] = proc_content['Paths']
            
        except ImportError as e:
            print('\n' + '*'*37)
            print('MIA warning: {0}'.format(e))
            print('*'*37 + '\n')

            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Warning: {0}".format(e))
            msg.setText("Package {0} not found !\nPlease install the python-nipype package ...".format('nipype'))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            del app
                
            if proc_content_flag and proc_content and ('Packages' in proc_content.keys()) \
                    and (proc_content['Packages'].keys()):
                final_pkgs = proc_content

            else:
                final_pkgs = {}
                final_pkgs["Packages"] = {}

        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'w', encoding='utf8') as stream:
            yaml.dump(final_pkgs, stream, default_flow_style=False, allow_unicode=True)


def verify_saved_projects():
    """
    Verifies if the projects saved in saved_projects.yml are still on the disk

    :return: the list of the deleted projects
    """
    saved_projects_object = SavedProjects()
    saved_projects_list = saved_projects_object.pathsList
    deleted_projects = []
    for saved_project in saved_projects_list:
        if not os.path.isdir(saved_project):
            deleted_projects.append(saved_project)
            saved_projects_object.removeSavedProject(saved_project)

    return deleted_projects


def launch_mia():
    global main_window

    app = QApplication(sys.argv)
    QApplication.setOverrideCursor(Qt.WaitCursor)

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

    deleted_projects = verify_saved_projects()

    project = Project(None, True)
    main_window = MainWindow(project, deleted_projects=deleted_projects)
    main_window.show()
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
