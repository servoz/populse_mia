import sys
import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QAction
import controller
from models import *
from pop_ups import Ui_Dialog_New_Project, Ui_Dialog_Open_Project, Ui_Dialog_Preferences, Ui_Dialog_Save_Project_As
import shutil
import json
from DataBrowser import DataBrowser


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.createUI()

    def createUI(self):

        self.showMaximized()

        # Menubar
        menu_file = self.menuBar().addMenu('File')
        menu_help = self.menuBar().addMenu('Help')
        # TODO: ADD MORE MENUS ?

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

        action_import = QAction('Import', self)
        action_import.setShortcut('Ctrl+I')
        menu_file.addAction(action_import)

        action_settings = QAction('Project properties', self)
        menu_file.addAction(action_settings)

        self.action_preferences = QAction('MIA2 preferences', self)
        menu_file.addAction(self.action_preferences)
        self.action_preferences.setDisabled(True)

        action_exit = QAction('Exit', self)
        action_exit.setShortcut('Ctrl+W')
        menu_file.addAction(action_exit)

        # Connection of the several triggered signals of the actions to some other methods
        action_create.triggered.connect(self.create_project_pop_up)
        action_open.triggered.connect(self.open_project_pop_up)
        action_exit.triggered.connect(self.close)
        action_save.triggered.connect(self.save_project)
        action_save_as.triggered.connect(self.save_project_as)
        action_import.triggered.connect(self.conversion_software)
        self.action_preferences.triggered.connect(self.preferences_pop_up)

        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2')
        self.show()
        return self

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

    @pyqtSlot()
    def modify_ui(self):
        """
        This method will only "allocate" the several tables and lists of the application
        """
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

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setObjectName("centralwidget")

        # Creating the widget that will contain the several tabs
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab_widget.setEnabled(True)

        grid_central_widget = QtWidgets.QGridLayout()  # To make sure it takes the entire space available
        self.central_widget.setLayout(grid_central_widget)
        grid_central_widget.addWidget(self.tab_widget, 0, 0)

        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.tab_widget.sizePolicy().hasHeightForWidth())
        self.tab_widget.setSizePolicy(size_policy)
        self.tab_widget.setStyleSheet("")
        self.tab_widget.setObjectName("tabWidget")

        ################################################################################################################
        # 'Data Browser' tab
        ################################################################################################################

        self.data_browser = DataBrowser(self.project)
        self.tab_widget.addTab(self.data_browser, "Data Browser")

        self.setCentralWidget(self.central_widget)
        # Calling allocate_table_tab that will fill all the tables, lists etc. with the project data
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

    def conversion_software(self):
        # Opens the conversion software to convert the MRI files in Nifti/Json
        import subprocess
        subprocess.call(['java', '-jar', 'MRIManagerJ8.jar', '[ExportNifti] ' + os.path.abspath(self.project.folder) + '/data/raw_data/',
                         '[ExportToMIA] PatientName--StudyName--CreationDate--SeqNumber--Protocol--SequenceName'])

        self.read_log()
        self.data_browser.table_data.update_table()

    def read_log(self):
        import glob

        raw_data_folder = os.path.abspath(self.project.folder) + '/data/raw_data/'

        # Checking all the export logs from MRIManager and taking the most recent
        list_logs = glob.glob(raw_data_folder + "logExport*.json")
        log_to_read = max(list_logs, key=os.path.getctime)

        with open(log_to_read, "r", encoding="utf-8") as file:
            list_dict_log = json.load(file, object_hook=deserializer)

        for dict_log in list_dict_log:
            if dict_log['StatusExport'] == "Export ok":
                file_name = dict_log['NameFile']
                path_name = raw_data_folder
                self.project.addScan(controller.loadScan(str(1), file_name, path_name))
                for tag in self.project.user_tags:
                    user_tag_name = tag['name']
                    for scan in self.project._get_scans():
                        if scan.file_path == file_name:
                            if user_tag_name not in scan.getAllTagsNames():
                                tag = Tag(user_tag_name, "", tag["original_value"], "custom", tag["original_value"])
                                scan.addCustomTag(tag)

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
