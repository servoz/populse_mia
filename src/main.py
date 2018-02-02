'''
Created on 11 janv. 2018

@author: omonti

'''
import subprocess
import sys
import os
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QTabWidget, QApplication, QVBoxLayout, \
    QMenuBar, QAction, qApp, QLineEdit, QMainWindow, QDialog

from Config import Config
from DataBrowser.DataBrowser import DataBrowser   
from ImageViewer.ImageViewer import ImageViewer
from NodeEditor.PipeLine_Irmage import ProjectEditor
from models import *
from pop_ups import Ui_Dialog_New_Project, Ui_Dialog_Open_Project, Ui_Dialog_Preferences, Ui_Dialog_Save_Project_As
import controller
import shutil



class Project_Irmage(QMainWindow):
    def __init__(self):
        
        ############### Main Window ################################################################
        super(Project_Irmage, self).__init__()
        
        ############### initial setting ############################################################
        config = Config()
        self.currentRep = config.getPathData()
        self.showMaximized()

        ################ Create Menus ##############################################################

        # Menubar
        menu_file = self.menuBar().addMenu('File')
        menu_help = self.menuBar().addMenu('Help')
        menu_about = self.menuBar().addMenu('About')

        # Actions in the "File" menu
        action_create = QAction('New project', self)
        action_create.setShortcut('Ctrl+N')
        menu_file.addAction(action_create)

        action_open = QAction('Open project', self)
        action_open.setShortcut('Ctrl+O')
        menu_file.addAction(action_open)

        action_save = QAction('Save project', self)
        action_save.setShortcut('Ctrl+S')
        menu_file.addAction(action_save)

        action_save_as = QAction('Save project as', self)
        action_save_as.setShortcut('Ctrl+Shift+S')
        menu_file.addAction(action_save_as)

        action_import = QAction(QIcon('sources_images/Blue.png'), 'Import', self)
        action_import.setShortcut('Ctrl+I')
        menu_file.addAction(action_import)

        action_settings = QAction('Project properties', self)
        menu_file.addAction(action_settings)

        self.action_preferences = QAction('MIA2 preferences', self)
        menu_file.addAction(self.action_preferences)
        self.action_preferences.setDisabled(True)

        action_exit = QAction(QIcon('sources_images/exit.png'), 'Exit', self)
        action_exit.setShortcut('Ctrl+W')
        menu_file.addAction(action_exit)

        menu_help.addAction('Documentations')
        menu_help.addAction('Credits')

        # Connection of the several triggered signals of the actions to some other methods
        action_create.triggered.connect(self.create_project_pop_up)
        action_open.triggered.connect(self.open_project_pop_up)
        action_exit.triggered.connect(self.close)
        action_save.triggered.connect(self.save_project)
        action_save_as.triggered.connect(self.save_project_as)
        action_import.triggered.connect(self.import_data)
        self.action_preferences.triggered.connect(self.preferences_pop_up)

        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2')
        self.statusBar().showMessage('Please create a new project (Ctrl+N) or open an existing project (Ctrl+O)')
        #self.show()
        #return self

        #self.project = {}

    def modify_ui(self):
        self.action_preferences.setDisabled(False)

        # This list will later contain all the tags in the project
        self.list_selected_tags = []

        # We get the name and the path of the current project to open it
        name = self.exPopup.name
        path = self.exPopup.path + '/' + name
        self.project = controller.open_project(name, path)

        for file in self.project._get_scans():
            for n_tag in file._get_tags():
                if n_tag.origin == 'custom' and n_tag.name not in self.project.tags_to_visualize:
                    self.project.tags_to_visualize.append(n_tag.name)

        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - ' + self.project.name)
        ################ Create Tabs ###############################################################
        self.create_tabs()
        self.setCentralWidget(self.centralWindow)


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

        self.data_browser = DataBrowser(self.project)
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
        file_name = self.exPopup.return_value()

        # Once the user has selected his project, the 'signal_create_project" signal is emitted
        # Which will be connected to the modify_ui method that controls the following processes
        self.exPopup.signal_create_project.connect(self.modify_ui)
        self.exPopup.show()

    def open_project_pop_up(self):
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_Open_Project()
        self.exPopup.signal_create_project.connect(self.modify_ui)
        if self.exPopup.exec_() == QDialog.Accepted:
            self.exPopup.retranslateUi(self.exPopup.selectedFiles())

    def preferences_pop_up(self):
        self.pop_up_preferences = Ui_Dialog_Preferences(self.project)
        self.pop_up_preferences.setGeometry(300, 200, 800, 600)
        self.pop_up_preferences.show()

        if self.pop_up_preferences.exec_() == QDialog.Accepted:
            self.project.tags_to_visualize = self.pop_up_preferences.get_values()
            self.data_browser.table_data.update_table()

    def import_data(self):
        # Opens the conversion software to convert the MRI files in Nifti/Json
        subprocess.call(['java', '-Xmx4096M', '-jar', 'MRIManagerJ8.jar',
                         '[ExportNifti] ' + os.path.abspath(self.project.folder) + '/data/raw_data/',
                         '[ExportToMIA] PatientName-StudyName-CreationDate-SeqNumber-Protocol-SequenceName-AcquisitionTime'])

        controller.read_log(self.project)
        self.data_browser.table_data.update_table()

    def save_project(self):
        project_path = os.path.abspath(self.project.folder) + '/' + self.project.name + '/' + self.project.name
        utils.saveProjectAsJsonFile(project_path, self.project)

    def save_project_as(self):
        from datetime import datetime
        import glob
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_Save_Project_As()
        self.exPopup.exec()

        old_folder = self.project.folder
        self.project.folder = self.exPopup.total_path
        self.project.name = self.exPopup.name
        self.project.date = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        data_path = os.path.abspath(self.project.folder) + '/data/'

        for filename in glob.glob(os.path.join(os.path.abspath(old_folder + '/data/raw_data'), '*.*')):
            shutil.copy(filename, data_path + 'raw_data/')
        for filename in glob.glob(os.path.join(os.path.abspath(old_folder + '/data/treat_data'), '*.*')):
            shutil.copy(filename, data_path + 'treat_data/')

        project_path = os.path.abspath(self.project.folder) + '/' + self.project.name + '/' + self.project.name
        utils.saveProjectAsJsonFile(project_path, self.project)

        # Once the user has selected the new project name, the 'signal_saved_project" signal is emitted
        # Which will be connected to the modify_ui method that controls the following processes
        self.exPopup.signal_saved_project.connect(self.modify_ui)

   
"""class createTabs(QWidget):
    def __init__(self):
        super(createTabs, self).__init__()

        self.config = Config()
        self.currentRep = self.config.getPathData()
               
        self.tabs = QTabWidget()
        self.tabs.setAutoFillBackground(False)
        self.tabs.setStyleSheet('QTabBar{font-size:14pt;font-family:Times;text-align: center;color:blue;}')
        self.tabs.setMovable(True)
        
        self.textInfo = QLineEdit(self)
        self.textInfo.resize(500,40)
        #self.textInfo.setEnabled(False)
        self.textInfo.setText('Welcome to Irmage')
                        
        self.tabs.addTab(DataBrowser(self.textInfo), "Data Browser")
        self.tabs.addTab(ProjectEditor(self.textInfo), "Pipeline Manager")
               
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.tabs)
        self.verticalLayout.addWidget(self.textInfo)"""
   
          
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    imageViewer = Project_Irmage()
    imageViewer.show()

    sys.exit(app.exec_())