'''
Created on 11 janv. 2018

@author: omonti

'''
import subprocess
import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QTabWidget, QApplication, QVBoxLayout, QAction, QLineEdit, QMainWindow, QDialog, QMessageBox
from Config import Config
from RecentProjects import RecentProjects
import DataBrowser.DataBrowser
from ImageViewer.ImageViewer import ImageViewer
from NodeEditor.PipeLine_Irmage import ProjectEditor
from models import *
from pop_ups import Ui_Dialog_New_Project, Ui_Dialog_Open_Project, Ui_Dialog_Preferences, Ui_Dialog_Settings, Ui_Dialog_Save_Project_As, Ui_Dialog_Quit
import controller
import shutil
import utils
import json

class Project_Irmage(QMainWindow):
    def __init__(self):
        
        ############### Main Window ################################################################
        super(Project_Irmage, self).__init__()
        
        ############### initial setting ############################################################
        config = Config()
        self.currentRep = config.getPathData()

        self.recent_projects = RecentProjects()
        self.recent_projects_list = self.recent_projects.pathsList

        self.recent_projects_actions = []

        ################ Create actions & menus ####################################################

        self.create_actions()
        self.create_menus()

        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2')
        self.statusBar().showMessage('Please create a new project (Ctrl+N) or open an existing project (Ctrl+O)')

        self.project = Project("")

        tmp_dir_exists = False
        while not tmp_dir_exists:
            # Checking if the temp directory exists
            check_path = os.path.join(os.path.relpath(os.path.curdir), 'temp_data')
            check_path_2 = os.path.join(os.path.relpath(os.path.curdir), 'temp_data_2')
            check_path_3 = os.path.join(os.path.relpath(os.path.curdir), 'temp_data_folder')

            if not os.path.exists(check_path):
                self.project.folder = check_path
                self.temp_dir = check_path
                os.makedirs(check_path)
                tmp_dir_exists = True
            elif not os.path.exists(check_path_2):
                self.project.folder = check_path_2
                self.temp_dir = check_path_2
                os.makedirs(check_path_2)
                tmp_dir_exists = True
            elif not os.path.exists(check_path_3):
                self.project.folder = check_path_3
                self.temp_dir = check_path_3
                os.makedirs(check_path_3)
                tmp_dir_exists = True
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Temporary folders already exists in the current folder")
                msg.setInformativeText("Please remove temp_data or temp_data_2 or temp_data_folder")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()


        self.first_save = True
        # BELOW : WAS AT THE END OF MODIFY_UI
        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - Unnamed project')
        ################ Create Tabs ###############################################################
        self.create_tabs()
        self.setCentralWidget(self.centralWindow)
        self.showMaximized()

    def create_actions(self):

        self.action_create = QAction('New project', self)
        self.action_create.setShortcut('Ctrl+N')

        self.action_open = QAction('Open project', self)
        self.action_open.setShortcut('Ctrl+O')

        self.action_save = QAction('Save project', self)
        self.action_save.setShortcut('Ctrl+S')

        self.action_save_as = QAction('Save project as', self)
        self.action_save_as.setShortcut('Ctrl+Shift+S')

        self.action_import = QAction(QIcon(os.path.join('sources_images', 'Blue.png')), 'Import', self)
        self.action_import.setShortcut('Ctrl+I')

        for i in range(self.recent_projects.maxProjects):
            self.recent_projects_actions.append(QAction(self, visible=False,
                                                triggered=self.open_recent_project))
        self.action_settings = QAction('Project properties', self)

        self.action_preferences = QAction('MIA2 preferences', self)

        self.action_exit = QAction(QIcon(os.path.join('sources_images', 'exit.png')), 'Exit', self)
        self.action_exit.setShortcut('Ctrl+W')

        # Connection of the several triggered signals of the actions to some other methods
        self.action_create.triggered.connect(self.create_project_pop_up)
        self.action_open.triggered.connect(self.open_project_pop_up)
        self.action_exit.triggered.connect(self.close)
        self.action_save.triggered.connect(self.save_project)
        self.action_save_as.triggered.connect(self.save_project_as)
        self.action_import.triggered.connect(self.import_data)
        self.action_preferences.triggered.connect(self.preferences_pop_up)
        self.action_settings.triggered.connect(self.settings_pop_up)

    def create_menus(self):

        # Menubar
        self.menu_file = self.menuBar().addMenu('File')
        self.menu_help = self.menuBar().addMenu('Help')
        self.menu_about = self.menuBar().addMenu('About')

        # Actions in the "File" menu
        self.menu_file.addAction(self.action_create)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_import)
        self.menu_file.addSeparator()
        for i in range(self.recent_projects.maxProjects):
            self.menu_file.addAction(self.recent_projects_actions[i])
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_settings)
        self.menu_file.addAction(self.action_preferences)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.update_recent_projects_actions()

        # Actions in the "Help" menu
        self.menu_help.addAction('Documentations')
        self.menu_help.addAction('Credits')

    def closeEvent(self, event):
        if (self.check_unsaved_modifications() == 1):
            self.pop_up_close = Ui_Dialog_Quit(self.project) # Crash if red cross clicked
            self.pop_up_close.save_as_signal.connect(self.save_project)
            self.pop_up_close.exec()
            can_exit = self.pop_up_close.can_exit()

        #TODO: ADD THE CASE WHEN THE PROJECT IS NAMED BUT NOT WITH THE CURRENT VERSION
        #TODO: IF THE FILE DIALOG (SAVE PROJECT AS) IS CLOSED, THE PROGRAM CRASHES
        else:
            can_exit = True

        if can_exit:
            event.accept()
            if os.path.exists(self.temp_dir):
                if os.path.exists(os.path.join(self.temp_dir, 'data')):
                    shutil.rmtree(os.path.join(self.temp_dir, 'data'))
                os.rmdir(self.temp_dir)
        else:
            event.ignore()

    def check_unsaved_modifications(self):
        if(self.project.name == ""):
            return 1
        project_path = os.path.join(self.project.folder, self.project.name)
        file_path = os.path.join(project_path, self.project.name)
        with open(file_path+".json", "r", encoding="utf-8")as fichier:
            project = json.load(fichier, object_hook=deserializer)
            if not (self.project.name == project.name):
                return 1
            if not (self.project.folder == project.folder):
                return 1
            if not (self.project.date == project.date):
                return 1
            if not (self.project.tags_to_visualize == project.tags_to_visualize):
                return 1
            for scan in project._get_scans():
                scanFound = 0
                for scan2 in self.project._get_scans():
                    if(scan.file_path == scan2.file_path):
                        scanFound = 1
                        for tag in scan.getAllTags():
                            tagFound = 0
                            for tag2 in scan2.getAllTags():
                                if(tag.name == tag2.name):
                                    tagFound = 1
                                    if not (tag.value == tag2.value):
                                        return 1
                                    break
                        if tagFound == 0:
                            return 1
                        break
                if scanFound == 0:
                    return 1

        return 0

    @pyqtSlot()
    def modify_ui(self):

        # This list will later contain all the tags in the project
        self.list_selected_tags = []

        # We get the name and the path of the current project to open it
        name = self.exPopup.name
        path = os.path.join(self.exPopup.path, name)
        self.project = controller.open_project(name, path)

        #QtCore.QMetaObject.connectSlotsByName(self)

        for file in self.project._get_scans():
            for n_tag in file._get_tags():
                if n_tag.origin == 'custom' and n_tag.name not in self.project.tags_to_visualize:
                    self.project.tags_to_visualize.append(n_tag.name)

        self.create_tabs()
        self.setCentralWidget(self.centralWindow)
        if self.project.name == "":
            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - Unnamed project')
        else:
            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - ' + self.project.name)
        self.statusBar().showMessage('')
        #self.data_browser.table_data.update_table(self.project)


    def create_tabs(self):
        self.config = Config()
        self.currentRep = self.config.getPathData()

        self.tabs = QTabWidget()
        self.tabs.setAutoFillBackground(False)
        self.tabs.setStyleSheet('QTabBar{font-size:14pt;font-family:Times;text-align: center;color:blue;}')
        self.tabs.setMovable(True)

        self.textInfo = QLineEdit(self)
        self.textInfo.resize(500, 40)
        # self.textInfo.setEnabled(False)
        self.textInfo.setText('Welcome to Irmage')

        self.data_browser = DataBrowser.DataBrowser.DataBrowser(self.project)
        self.tabs.addTab(self.data_browser, "Data Browser")

        self.image_viewer = ImageViewer(self.textInfo)
        self.tabs.addTab(self.image_viewer, "Image Viewer")

        self.pipeline_manager = ProjectEditor(self.textInfo)
        self.tabs.addTab(self.pipeline_manager, "Pipeline Manager")

        verticalLayout = QVBoxLayout()
        verticalLayout.addWidget(self.tabs)
        verticalLayout.addWidget(self.textInfo)
        self.centralWindow = QWidget()
        self.centralWindow.setLayout(verticalLayout)

    def create_project_pop_up(self):
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_New_Project()
        #file_name = self.exPopup.return_value()
        self.first_save = False

        # Once the user has selected his project, the 'signal_create_project" signal is emitted
        # Which will be connected to the modify_ui method that controls the following processes
        self.exPopup.signal_create_project.connect(self.modify_ui)

        if self.exPopup.exec_() == QDialog.Accepted:
            file_name = self.exPopup.selectedFiles()
            self.exPopup.retranslateUi(self.exPopup.selectedFiles())
            file_name = self.exPopup.relative_path
            self.recent_projects_list = self.recent_projects.addRecentProject(file_name)
            self.update_recent_projects_actions()
            if os.path.exists(self.temp_dir):
                if os.path.exists(os.path.join(self.temp_dir, 'data')):
                    shutil.rmtree(os.path.join(self.temp_dir, 'data'))
                os.rmdir(self.temp_dir)

    def open_project_pop_up(self):
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_Open_Project()
        self.first_save = False
        self.exPopup.signal_create_project.connect(self.modify_ui)
        if self.exPopup.exec_() == QDialog.Accepted:
            file_name = self.exPopup.selectedFiles()
            self.exPopup.retranslateUi(file_name)
            file_name = self.exPopup.relative_path
            self.recent_projects_list = self.recent_projects.addRecentProject(file_name)
            self.update_recent_projects_actions()
            if os.path.exists(self.temp_dir):
                if os.path.exists(os.path.join(self.temp_dir, 'data')):
                    shutil.rmtree(os.path.join(self.temp_dir, 'data'))
                os.rmdir(self.temp_dir)

            problem_list = controller.verify_scans(self.project)
            if problem_list != []:
                str_msg = ""
                for element in problem_list:
                    str_msg += element + "\n\n"
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("These files have been modified since they have been converted for the first time:")
                msg.setInformativeText(str_msg)
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()

    def open_recent_project(self):
        action = self.sender()
        if action:
            file_name = action.data()
            entire_path = os.path.abspath(file_name)
            path, name = os.path.split(entire_path)
            relative_path = os.path.relpath(file_name)

            # If the file exists
            if os.path.exists(os.path.join(relative_path, name, name + '.json')):
                list_to_add = []
                controller.open_project(name, relative_path)
                self.recent_projects_list = self.recent_projects.addRecentProject(file_name)
                self.update_recent_projects_actions()
                self.exPopup = Ui_Dialog_New_Project()
                self.exPopup.path = path
                self.exPopup.name = name
                self.modify_ui()
            else:
                print("TODO: ADD AN ERROR DIALOG")

    def update_recent_projects_actions(self):
        if self.recent_projects_list != []:
            for i in range(len(self.recent_projects_list)):
                text = os.path.basename(self.recent_projects_list[i])
                self.recent_projects_actions[i].setText(text)
                self.recent_projects_actions[i].setData(self.recent_projects_list[i])
                self.recent_projects_actions[i].setVisible(True)


    def preferences_pop_up(self):
        self.pop_up_preferences = Ui_Dialog_Preferences(self.project)
        self.pop_up_preferences.setGeometry(300, 200, 800, 600)
        self.pop_up_preferences.show()

        if self.pop_up_preferences.exec_() == QDialog.Accepted:
            self.data_browser.table_data.update_table(self.project)

    def settings_pop_up(self):
        self.pop_up_settings = Ui_Dialog_Settings(self.project)
        self.pop_up_settings.setGeometry(300, 200, 800, 600)
        self.pop_up_settings.show()

        if self.pop_up_settings.exec_() == QDialog.Accepted:
            self.data_browser.table_data.update_table(self.project)

    def import_data(self):
        # Opens the conversion software to convert the MRI files in Nifti/Json
        subprocess.call(['java', '-Xmx4096M', '-jar', 'MRIManagerJ8.jar',
                         '[ExportNifti] ' + os.path.join(self.project.folder, 'data', 'raw_data'),
                         '[ExportToMIA] PatientName-StudyName-CreationDate-SeqNumber-Protocol-SequenceName-AcquisitionTime',
                         'CloseAfterExport'])
        # 'NoLogExport'if we don't want log export

        controller.read_log(self.project)
        self.data_browser.table_data.update_table(self.project)

    def save_project(self):

        if self.project.name == "":
            self.save_project_as()
        else:
            project_path = os.path.join(self.project.folder, self.project.name, self.project.name)
            utils.saveProjectAsJsonFile(project_path, self.project)
            self.first_save = False

    def save_project_as(self):
        from datetime import datetime
        import glob
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_Save_Project_As()
        # self.exPopup.exec()
        if self.exPopup.exec_() == QDialog.Accepted:
            old_folder = self.project.folder
            self.project.folder = self.exPopup.relative_path
            self.project.name = self.exPopup.name
            self.project.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            data_path = os.path.join(os.path.relpath(self.project.folder), 'data')

            if os.path.exists(os.path.join(old_folder, 'data')):
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'raw_data', '*.*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'raw_data'))
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'derived_data', '*.*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'derived_data'))

            project_path = os.path.join(os.path.relpath(self.project.folder), self.project.name, self.project.name)
            utils.saveProjectAsJsonFile(project_path, self.project)

            if self.first_save:
                if os.path.exists(os.path.join(old_folder, 'data')):
                    shutil.rmtree(os.path.join(old_folder, 'data'))
                if os.listdir(old_folder) == []:
                    os.rmdir(old_folder)

            # Once the user has selected the new project name, the 'signal_saved_project" signal is emitted
            # Which will be connected to the modify_ui method that controls the following processes
            self.exPopup.signal_saved_project.connect(self.modify_ui)

            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - ' + self.project.name)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    imageViewer = Project_Irmage()
    imageViewer.show()

    sys.exit(app.exec_())