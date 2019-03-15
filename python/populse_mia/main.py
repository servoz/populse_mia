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
import pkgutil
import inspect
import yaml
import copy

# PyQt5 imports
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QDir, QLockFile, Qt

# soma-base imports
from soma.path import find_in_path
from soma.qt_gui.qt_backend.Qt import QMessageBox

# populse_mia imports
# from populse_mia.software_properties.config import Config
# from populse_mia.software_properties.saved_projects import SavedProjects
# from populse_mia.main_window.main_window import MainWindow
# from populse_mia.project.project import Project

main_window = None

"""
@atexit.register
"""


class PackagesInstall:
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
                            print('\nExploring submodules of {0} ...'.format(module_name))
                            flag = False

                        print('- ', str(module_name + '.' + modname))
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
                print(
                    '\nWhen attempting to add a package and its modules to the package tree, the following exception was caught:')
                print('{0}'.format(e))

            return self.packages


def clean_up():
    """
    Cleans up the software during "normal" closing
    """
    from populse_mia.software_properties.config import Config

    global main_window

    print("clean up done")

    config = Config()
    opened_projects = config.get_opened_projects()
    opened_projects.remove(main_window.project.folder)
    config.set_opened_projects(opened_projects)
    main_window.remove_raw_files_useless()


def deepCompDic(old_dic, new_dic, level="0"):
    """
    Recursive comparison of the old_dic and new _dic dictionary. If all keys are recursively
    identical, the final value at the end of the whole tree in old_dic is kept in the
    new _dic. To sum up, this function is used to keep up the user display preferences in
    the processes library of the Pipeline Manager Editor.
    """
    PY3 = sys.version_info[0] == 3

    if PY3:

        if isinstance(old_dic, str):
            return True

    else:
        if isinstance(old_dic, basestring):
            return True

    for key in old_dic:

        if key not in new_dic:

            if level == "0":
                pass

            elif level == "+1":
                return False

        elif deepCompDic(old_dic[str(key)], new_dic[str(key)], level="+1"):
            new_dic[str(key)] = old_dic[str(key)]


def launch_mia():
    # Populse_MIA imports
    from populse_mia.main_window.main_window import MainWindow
    from populse_mia.project.project import Project
    from populse_mia.software_properties.config import Config

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


def main():
    '''
    Checks if Populse_MIA is called from the site/dist packages or from a cloned git repository.
    Updates the dev_mode parameter accordingly. Tries to update the mia_path if necessary.
    Launchs the verify_processes() function, then the launch_mia() function (mia's real launch !!).
    When mia is exited, sets the dev_mode parameter to "no.
    - If launched from a cloned git repository ("developper mode"):
        - adds the good path to the sys.path
        - if the ~/.populse_mia/configuration.yml exists, updates
          the dev_mode parameter to "yes"
        - if the ~/.populse_mia/configuration.yml is not existing
          nothing is done.
  - if launched from the site/dist packages ("user mode"):
        - if the ~/.populse_mia/configuration.yml exists, updates
          the dev_mode parameter to "no" and if not found update
          the mia_path parameter.
        - if the ~/.populse_mia/configuration.yml is not existing,
          it is tried to create this file with the good dev_mode
          and mia_path parameters
    '''
    if not os.path.dirname(os.path.dirname(os.path.realpath(__file__))) in sys.path: # "developer" mode
        print('Populse_MIA in "developer" mode')
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        dot_mia_config = os.path.join(os.path.expanduser("~"), ".populse_mia", "configuration.yml")
        
        if not os.path.isfile(dot_mia_config):
            print('\n{0} has been detected.'.format(dot_mia_config))
            
            with open(dot_mia_config, 'r') as stream:
                # mia_home_config = yaml.load(stream, Loader=yaml.FullLoader) ## from version 5.1
                mia_home_config = yaml.load(stream) ## version < 5.1
                
            mia_home_config["dev_mode"] = "yes"
            
            with open(dot_mia_config, 'w', encoding='utf8') as configfile:
                yaml.dump(mia_home_config, configfile, default_flow_style=False, allow_unicode=True)

        else:
            print('\n{0} has not been detected.'.format(dot_mia_config))
        verify_processes()

    else:                                                                            # "user" mode
        dot_mia_config = os.path.join(os.path.expanduser("~"), ".populse_mia", "configuration.yml")
        
        try:
            with open(dot_mia_config, 'r') as stream:
                # mia_home_config = yaml.load(stream, Loader=yaml.FullLoader) ## from version 5.1
                mia_home_config = yaml.load(stream) ## version < 5.1
            verify_processes()

        except Exception as e:                                                      # the config file does not exist
            print('\n~/.populse_mia/configuration.yml has not been opened: ', e)
            mia_home_config = {}
            
            mia_home_config["dev_mode"] = "no"

            #Open popup, user choose the path to .populse_mia/populse_mia
            app = QApplication(sys.argv)
            msg = QDialog()
            msg.setWindowTitle("MIA path selection")
            #msg.setWindowFlags(msg.windowFlags() | Qt.CustomizeWindowHint)
            #msg.setWindowFlag(Qt.WindowCloseButtonHint, False)
            vbox_layout = QVBoxLayout()

            hbox_layout = QHBoxLayout()
            file_label = QLabel("Please select the MIA path (directory with\n "
                                "the processes, properties & resources directories): ")
            msg.file_line_edit = QLineEdit()
            msg.file_line_edit.setFixedWidth(400)
            #msg.file_line_edit.textChanged.connect()
            file_button = QPushButton("Browse")
            file_button.clicked.connect(partial(browse_mia_path, msg))
            vbox_layout.addWidget(file_label)
            hbox_layout.addWidget(msg.file_line_edit)
            hbox_layout.addWidget(file_button)
            vbox_layout.addLayout(hbox_layout)

            hbox_layout = QHBoxLayout()
            msg.ok_button = QPushButton("Ok")
            msg.ok_button.clicked.connect(partial(ok_mia_path, msg))
            hbox_layout.addWidget(msg.ok_button)
            vbox_layout.addLayout(hbox_layout)

            msg.setLayout(vbox_layout)
            msg.exec()
            del app

        # try:                                                                        # try to create config
        #     if not os.path.exists(os.path.dirname(dot_mia_config)):
        #         os.mkdir(os.path.dirname(dot_mia_config))
        #         print('\nThe {0} file is created ...'.format(dot_mia_config))
        #
        #     with open(dot_mia_config, 'w', encoding='utf8') as configfile:
        #         yaml.dump(mia_home_config, configfile, default_flow_style=False, allow_unicode=True)
        #
        # except Exception as e:
        #     print('\nCould not write the {0} configuration file: {1} ...'.format(dot_mia_config, e))

    launch_mia()

    # Setting the dev_mode to "no" when exiting mia, if ~/.populse_mia/configuration.yml file exists
    dot_mia_config = os.path.join(os.path.expanduser("~"), ".populse_mia", "configuration.yml")
    
    if os.path.isfile(dot_mia_config):
        
        with open(dot_mia_config, 'r') as stream:
            # mia_home_config = yaml.load(stream, Loader=yaml.FullLoader) ## from version 5.1
            mia_home_config = yaml.load(stream) ## version < 5.1
            
        mia_home_config["dev_mode"] = "no"
        
        with open(dot_mia_config, 'w', encoding='utf8') as configfile:
            yaml.dump(mia_home_config, configfile, default_flow_style=False, allow_unicode=True)

def browse_mia_path(dialog):
    dname = QFileDialog.getExistingDirectory(dialog, "Please select MIA path")
    dialog.file_line_edit.setText(dname)

def ok_mia_path(dialog):
    mia_home_config = {}
    mia_home_config["dev_mode"] = "no"
    mia_home_config["mia_path"] = dialog.file_line_edit.text()
    print(mia_home_config)
    dot_mia_config = os.path.join(os.path.expanduser("~"), ".populse_mia", "configuration.yml")
    with open(dot_mia_config, 'w', encoding='utf8') as configfile:
        yaml.dump(mia_home_config, configfile, default_flow_style=False, allow_unicode=True)

    try:
        verify_processes()
        dialog.close()
    except Exception as e:
        print('\nCould not fetch the configuration file: {0} ...'.format(e))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Error: MIA path directory incorrect")
        msg.setText("Error : Please select the MIA path (directory with\n "
                    "the processes, properties & resources directories): ")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)
        msg.exec()

def verify_processes():
    """
    When the software is launched, if nipype or mia_processes packages needs to be
    updated in the processes library of the Pipeline Manager library, tries to make
    them available
    """
    # Populse_MIA imports
    from populse_mia.software_properties.config import Config

    print('\n Checking the installed versions of nipype and mia_processes ...')
    print(' ***************************************************************')
    proc_content = False
    nipypeVer = False
    miaProcVer = False
    pack2install = []
    config = Config()

    try:
        __import__('nipype')
        nipypeVer = sys.modules['nipype'].__version__
        __import__('mia_processes')
        miaProcVer = sys.modules['mia_processes'].__version__

    except ImportError as e:
        print('\n' + '*' * 37)
        print('MIA warning: {0}'.format(e))
        print('*' * 37 + '\n')
        app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning: {0}".format(e))

        if nipypeVer is False:
            pckg = 'nipype'

        elif miaProcVer is False:
            pckg = 'mia_processes'
 
        msg.setText("Package {0} not found !\nPlease install the package and start again mia ...".format(pckg))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)
        msg.exec()
        del app
        return

    if os.path.isfile(os.path.join(config.get_mia_path(), 'properties', 'process_config.yml')):

        with open(os.path.join(config.get_mia_path(), 'properties', 'process_config.yml'), 'r') as stream:
            # proc_content = yaml.load(stream, Loader=yaml.FullLoader) ## from version 5.1
            proc_content = yaml.load(stream) ## version < 5.1

    if (isinstance(proc_content, dict)) and ('Packages' in proc_content):
        othPckg = [f for f in proc_content['Packages'] if f not in ['mia_processes', 'nipype']]

    if 'othPckg' in dir():

        for pckg in othPckg:

            try:
                __import__(pckg)

            except ImportError:

                if (not os.path.relpath(os.path.join(config.get_mia_path(), 'processes')) in sys.path) and (
                        not os.path.abspath(os.path.join(config.get_mia_path(), 'processes')) in sys.path):
                    sys.path.append(os.path.abspath(os.path.join(config.get_mia_path(), 'processes')))

                    try:
                        __import__(pckg)

                        if ('Paths' in proc_content) and (isinstance(proc_content['Paths'], list)):

                            if (not os.path.relpath(os.path.join(config.get_mia_path(), 'processes')) in proc_content['Paths']) and (
                                    not os.path.abspath(os.path.join(config.get_mia_path(), 'processes')) in proc_content['Paths']):
                                proc_content['Paths'].append(os.path.abspath(os.path.join(config.get_mia_path(), 'processes')))

                        else:
                            proc_content['Paths'] = [os.path.abspath(os.path.join(config.get_mia_path(), 'processes'))]

                        with open(os.path.join(config.get_mia_path(), 'properties', 'process_config.yml'),
                                  'w', encoding='utf8') as stream:
                            yaml.dump(proc_content, stream, default_flow_style=False, allow_unicode=True)

                        sys.path.remove(os.path.abspath(os.path.join(config.get_mia_path(), 'processes')))

                    except ImportError as e:
                        print('{0}'.format(e))
                        app = QApplication(sys.argv)
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setWindowTitle("Warning: {0}".format(e))
                        msg.setText(("The {0} processes library has not been found in {1}.\n To prevent mia crash when using it, "
                                     "please Remove (see File > Package library manager) or load again "
                                     "(see More > Install processes) this processes library").format(
                                         pckg, os.path.abspath(os.path.join(config.get_mia_path(), 'processes'))))
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.buttonClicked.connect(msg.close)
                        msg.exec()
                        del app
                        sys.path.remove(os.path.abspath(os.path.join(config.get_mia_path(), 'processes')))

                else:
                    print("No module named '{0}'".format(pckg))
                    app = QApplication(sys.argv)
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Warning: {0}".format(e))
                    msg.setText(("The {0} processes library has not been found in {1}.\n To prevent mia crash when using it, "
                                 "please Remove (see File > Package library manager) or load again "
                                 "(see More > Install processes) this processes library").format(
                                     pckg, os.path.abspath(os.path.join(config.get_mia_path(), 'processes'))))
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.buttonClicked.connect(msg.close)
                    msg.exec()
                    del app

    if (not isinstance(proc_content, dict)) or (
       (isinstance(proc_content, dict)) and ('Packages' not in proc_content)) or (
       (isinstance(proc_content, dict)) and ('Versions' not in proc_content)):
        pack2install = ['nipype.interfaces', 'mia_processes']

    else:

        if ((isinstance(proc_content, dict)) and ('Packages' in proc_content) and (
                'nipype' not in proc_content['Packages'])) or (
                (isinstance(proc_content, dict)) and ('Versions' in proc_content) and (
                'nipype' not in proc_content['Versions'])) or (
                (isinstance(proc_content, dict)) and ('Versions' in proc_content) and (
                'nipype' in proc_content['Versions']) and (proc_content['Versions']['nipype'] != nipypeVer)):
            pack2install.append('nipype.interfaces')

        if ((isinstance(proc_content, dict)) and ('Packages' in proc_content) and (
                'mia_processes' not in proc_content['Packages'])) or (
                (isinstance(proc_content, dict)) and ('Versions' in proc_content) and (
                'mia_processes' not in proc_content['Versions'])) or (
                (isinstance(proc_content, dict)) and ('Versions' in proc_content) and (
                'mia_processes' in proc_content['Versions']) and (proc_content['Versions']['mia_processes'] != miaProcVer)):
            pack2install.append('mia_processes')

    final_pckgs = {}
    final_pckgs["Packages"] = {}
    final_pckgs["Versions"] = {}

    for pckg in pack2install:

        package = PackagesInstall()
        pckg_dic = package.add_package(pckg)

        for item in pckg_dic:
            final_pckgs["Packages"][item] = pckg_dic[item]

        if 'nipype' in pckg:
            final_pckgs["Versions"]["nipype"] = nipypeVer
            print('\n** Upgrading the {0} library processes to {1} version ...'.format(pckg, nipypeVer))                                          

        if 'mia_processes' in pckg:
            final_pckgs["Versions"]["mia_processes"] = miaProcVer
            print('\n** Upgrading the {0} library processes to {1} version ...'.format(pckg, miaProcVer))

    if pack2install:

        if not any("nipype" in s for s in pack2install):
             print('\n** The nipype library processes in mia use already the installed version ', nipypeVer)

        elif not any("mia_processes" in s for s in pack2install):
            print('\n** The mia_processes library in mia use already the installed version ', miaProcVer)
 
        if ((isinstance(proc_content, dict)) and ('Paths' in proc_content)):

            for item in proc_content['Paths']:
                final_pckgs["Paths"] = proc_content['Paths']

        if ((isinstance(proc_content, dict)) and ('Versions' in proc_content)):

            for item in proc_content['Versions']:

                if item not in final_pckgs['Versions']:
                    final_pckgs['Versions'][item] = proc_content['Versions'][item]

        if ((isinstance(proc_content, dict)) and ('Packages' in proc_content)):
            deepCompDic(proc_content['Packages'], final_pckgs['Packages'])

            for item in proc_content['Packages']:

                if item not in final_pckgs['Packages']:
                    final_pckgs['Packages'][item] = proc_content['Packages'][item]

        with open(os.path.join(config.get_mia_path(), 'properties', 'process_config.yml'),
                  'w', encoding='utf8') as stream:
            yaml.dump(final_pckgs, stream, default_flow_style=False, allow_unicode=True)

    else:
        print('\n- mia use already the installed version of nipype and mia_processes ({0} and {1} respectively)'.format(nipypeVer, miaProcVer))

def verify_saved_projects():
    """
    Verifies if the projects saved in saved_projects.yml are still on the disk

    :return: the list of the deleted projects
    """

    # Populse_MIA imports
    from populse_mia.software_properties.saved_projects import SavedProjects

    saved_projects_object = SavedProjects()
    saved_projects_list = copy.deepcopy(saved_projects_object.pathsList)
    deleted_projects = []
    for saved_project in saved_projects_list:
        if not os.path.isdir(saved_project):
            deleted_projects.append(saved_project)
            saved_projects_object.removeSavedProject(saved_project)

    return deleted_projects




if __name__ == '__main__':
    main()
