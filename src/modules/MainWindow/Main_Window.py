'''
Created on 11 janv. 2018

@author: omonti

'''
import subprocess
import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QAction, QLineEdit, \
    QMainWindow, QDialog, QMessageBox, QMenu, QInputDialog
from SoftwareProperties.SavedProjects import SavedProjects
from SoftwareProperties.Config import Config
import DataBrowser.DataBrowser
from ImageViewer.ImageViewer import ImageViewer
from NodeEditor.PipeLine_Irmage import ProjectEditor
from PopUps.Ui_Dialog_New_Project import Ui_Dialog_New_Project
from PopUps.Ui_Dialog_Open_Project import Ui_Dialog_Open_Project
from PopUps.Ui_Dialog_Preferences import Ui_Dialog_Preferences
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings
from PopUps.Ui_Dialog_Save_Project_As import Ui_Dialog_Save_Project_As
from PopUps.Ui_Dialog_Quit import Ui_Dialog_Quit
from PopUps.Ui_Dialog_See_All_Projects import Ui_Dialog_See_All_Projects

import ProjectManager.controller as controller
import shutil
from DataBase.DataBase import DataBase

class Main_Window(QMainWindow):
    """
    Primary master class

    Attributes
    ----------


    Methods
    -------


    """
    def __init__(self, database):

        ############### Main Window ################################################################
        super(Main_Window, self).__init__()

        self.database = database

        ############### initial setting ############################################################
        config = Config()
        self.currentRep = config.getPathData()

        self.saved_projects = SavedProjects()
        self.saved_projects_list = self.saved_projects.pathsList

        self.saved_projects_actions = []

        ################ Create actions & menus ####################################################

        config = Config()
        background_color = config.getBackgroundColor()
        text_color = config.getTextColor()
        self.setStyleSheet("background-color:" + background_color + ";color:" + text_color + ";")

        self.create_actions()
        self.create_menus()

        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2')
        self.statusBar().showMessage('Please create a new project (Ctrl+N) or open an existing project (Ctrl+O)')

        # BELOW : WAS AT THE END OF MODIFY_UI
        self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - Unnamed project')
        ################ Create Tabs ###############################################################
        self.create_tabs()
        self.setCentralWidget(self.centralWindow)
        self.showMaximized()

    def create_actions(self):
        """ Create the actions in each menu """

        self.action_create = QAction('New project', self)
        self.action_create.setShortcut('Ctrl+N')

        self.action_open = QAction('Open project', self)
        self.action_open.setShortcut('Ctrl+O')

        self.action_save = QAction('Save project', self)
        self.action_save.setShortcut('Ctrl+S')

        self.action_save_as = QAction('Save project as', self)
        self.action_save_as.setShortcut('Ctrl+Shift+S')

        self.action_save_current_filter = QAction('Save current filter', self)

        self.action_import = QAction(QIcon(os.path.join('..', 'sources_images', 'Blue.png')), 'Import', self)
        self.action_import.setShortcut('Ctrl+I')

        for i in range(self.saved_projects.maxProjects):
            self.saved_projects_actions.append(QAction(self, visible=False,
                                                       triggered=self.open_recent_project))

        self.action_see_all_projects = QAction('See all projects', self)

        self.action_project_properties = QAction('Project properties', self)

        self.action_software_preferences = QAction('MIA2 preferences', self)

        self.action_exit = QAction(QIcon(os.path.join('..', 'sources_images', 'exit.png')), 'Exit', self)
        self.action_exit.setShortcut('Ctrl+W')

        self.action_undo = QAction('Undo', self)
        self.action_undo.setShortcut('Ctrl+Z')

        self.action_redo = QAction('Redo', self)
        self.action_redo.setShortcut('Ctrl+Y')

        # Connection of the several triggered signals of the actions to some other methods
        self.action_create.triggered.connect(self.create_project_pop_up)
        self.action_open.triggered.connect(self.open_project_pop_up)
        self.action_exit.triggered.connect(self.close)
        self.action_save.triggered.connect(self.saveChoice)
        self.action_save_as.triggered.connect(self.save_project_as)
        self.action_save_current_filter.triggered.connect(lambda : self.data_browser.save_current_filter())
        self.action_import.triggered.connect(self.import_data)
        self.action_see_all_projects.triggered.connect(self.see_all_projects)
        self.action_project_properties.triggered.connect(self.project_properties_pop_up)
        self.action_software_preferences.triggered.connect(self.software_preferences_pop_up)
        self.action_undo.triggered.connect(self.undo)
        self.action_redo.triggered.connect(self.redo)

    def create_menus(self):
        """ Create the menubar """

        # Menubar
        self.menu_file = self.menuBar().addMenu('File')
        self.menu_edition = self.menuBar().addMenu('Edition')
        self.menu_help = self.menuBar().addMenu('Help')
        self.menu_about = self.menuBar().addMenu('About')

        # Submenu of menu_file menu
        self.menu_saved_projects = QMenu('Saved projects', self)

        # Actions in the "File" menu
        self.menu_file.addAction(self.action_create)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_save_current_filter)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_import)
        self.menu_file.addSeparator()
        self.menu_file.addMenu(self.menu_saved_projects)
        for i in range(self.saved_projects.maxProjects):
            self.menu_saved_projects.addAction(self.saved_projects_actions[i])
        self.menu_saved_projects.addSeparator()
        self.menu_saved_projects.addAction(self.action_see_all_projects)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_software_preferences)
        self.menu_file.addAction(self.action_project_properties)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)
        self.update_recent_projects_actions()

        # Actions in the "Edition" menu
        self.menu_edition.addAction(self.action_undo)
        self.menu_edition.addAction(self.action_redo)

        # Actions in the "Help" menu
        self.menu_help.addAction('Documentations')
        self.menu_help.addAction('Credits')

    def undo(self):
        """
        To undo the last action done by the user
        """
        self.database.undo() # Action reverted in the database

        # Gui refreshed
        scan_names_list = []
        for scan in self.database.getScans():
            scan_names_list.append(scan.scan)
        self.data_browser.table_data.scans_to_visualize = scan_names_list

        # Reset of headers
        self.data_browser.table_data.nb_columns = len(self.database.getVisualizedTags())
        self.data_browser.table_data.setColumnCount(self.data_browser.table_data.nb_columns)
        self.data_browser.table_data.initialize_headers()
        self.data_browser.table_data.fill_headers()

        self.data_browser.table_data.update_table()

    def redo(self):
        """
        To redo the last action made by the user
        """
        self.database.redo() # Action remade in the database

        # Gui refreshed
        scan_names_list = []
        for scan in self.database.getScans():
            scan_names_list.append(scan.scan)
        self.data_browser.table_data.scans_to_visualize = scan_names_list

        # Reset of headers
        self.data_browser.table_data.nb_columns = len(self.database.getVisualizedTags())
        self.data_browser.table_data.setColumnCount(self.data_browser.table_data.nb_columns)
        self.data_browser.table_data.initialize_headers()
        self.data_browser.table_data.fill_headers()

        self.data_browser.table_data.update_table()

    def closeEvent(self, event):
        """ Overriding the closing event to check if there are unsaved modifications """

        if (self.check_unsaved_modifications() == 1):
            self.pop_up_close = Ui_Dialog_Quit(self.database)
            self.pop_up_close.save_as_signal.connect(self.saveChoice)
            self.pop_up_close.exec()
            can_exit = self.pop_up_close.can_exit()

        # TODO: ADD THE CASE WHEN THE PROJECT IS NAMED BUT NOT WITH THE CURRENT VERSION
        # TODO: IF THE FILE DIALOG (SAVE PROJECT AS) IS CLOSED, THE PROGRAM STOPS, IT'S NOT LIKE CANCEL
        else:
            can_exit = True

        if can_exit:
            self.remove_raw_files_useless() # To remove the useless raw files
            event.accept()
        else:
            event.ignore()

    def remove_raw_files_useless(self):
        """
        Removes the useless raw files of the current project
        """
        import glob

        # If it's unnamed project, we can remove the whole project
        if self.database.isTempProject:
            shutil.rmtree(self.database.folder)
        else:
            for filename in glob.glob(os.path.join(os.path.relpath(self.database.folder), 'data', 'raw_data', '*')):
                scan, extension = os.path.splitext(os.path.basename(filename))
                # We remove the file only if it's not a scan still in the project, and if it's not a logExport
                if not self.database.hasScan(scan) and "logExport" not in scan:
                    os.remove(filename)


    def saveChoice(self):
        """ Checks if the project needs to be saved as or just saved """
        if (self.database.isTempProject):
            self.save_project_as()
        else:
            controller.save_project(self.database)

    def check_unsaved_modifications(self):
        """ Check if there are differences between the current project and the data base
            Returns 1 if there are unsaved modifications, 0 otherwise

        """
        # TODO DO THE CHECK WITH THE DATABASE STRUCTURE
        if (self.database.isTempProject and len(self.database.getScans()) > 0):
            return 1
        if (self.database.isTempProject):
            return 0
        if (self.database.unsavedModifications):
            return 1
        else:
            return 0

    @pyqtSlot()
    def modify_ui(self):
        """ Each time a project is opened or created, this function refreshes the GUI + the current project from
         the data base """

        self.create_tabs()
        self.setCentralWidget(self.centralWindow)
        if self.database.isTempProject:
            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - Unnamed project')
        else:
            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - ' + self.database.getName())
        self.statusBar().showMessage('')

    def create_tabs(self):
        """ Creates the tabs """
        self.config = Config()
        self.currentRep = self.config.getPathData()

        self.tabs = QTabWidget()
        self.tabs.setAutoFillBackground(False)
        self.tabs.setStyleSheet('QTabBar{font-size:14pt;font-family:Times;text-align: center;color:blue;}')
        self.tabs.setMovable(True)

        self.textInfo = QLineEdit(self)
        self.textInfo.resize(500, 40)
        self.textInfo.setText('Welcome to Irmage')

        self.data_browser = DataBrowser.DataBrowser.DataBrowser(self.database)
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

    def save_project_as(self):
        """ Open a pop-up to save the current project as """

        import glob
        exPopup = Ui_Dialog_Save_Project_As()
        if exPopup.exec_() == QDialog.Accepted:

            old_folder = self.database.folder
            file_name = exPopup.relative_path
            data_path = os.path.join(os.path.relpath(exPopup.relative_path), 'data')
            database_path = os.path.join(os.path.relpath(exPopup.relative_path), 'database')

            # List of projects updated
            self.saved_projects_list = self.saved_projects.addSavedProject(file_name)
            self.update_recent_projects_actions()

            # Data files copied
            if os.path.exists(os.path.join(old_folder, 'data')):
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'raw_data', '*.*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'raw_data'))
                for filename in glob.glob(os.path.join(os.path.relpath(old_folder), 'data', 'derived_data', '*.*')):
                    shutil.copy(filename, os.path.join(os.path.relpath(data_path), 'derived_data'))

            # First we register the database before commiting the last pending modifications
            shutil.copy(os.path.join(os.path.relpath(old_folder), 'database', 'mia2.db'), os.path.join(os.path.relpath(old_folder), 'database', 'mia2_before_commit.db'))

            # We commit the last pending modifications
            self.database.saveModifications()

            # We copy the database with all the modifications commited in the new project
            if os.path.exists(os.path.join(old_folder, 'database')):
                os.mkdir(os.path.relpath(database_path))
                shutil.copy(os.path.join(os.path.relpath(old_folder), 'database', 'mia2.db'), os.path.relpath(database_path))

            # We remove the database with all the modifications saved in the old project
            os.remove(os.path.join(os.path.relpath(old_folder), 'database', 'mia2.db'))

            # We reput the database without the last modifications in the old project
            shutil.copy(os.path.join(os.path.relpath(old_folder), 'database', 'mia2_before_commit.db'), os.path.join(os.path.relpath(old_folder), 'database', 'mia2.db'))

            self.remove_raw_files_useless() # We remove the useless files from the old project

            # Project updated everywhere
            self.database = DataBase(exPopup.relative_path, False)

            self.update_project(file_name) # Project updated everywhere

            # Once the user has selected the new project name, the 'signal_saved_project" signal is emitted
            # Which will be connected to the modify_ui method that controls the following processes
            exPopup.signal_saved_project.connect(self.modify_ui)

    def create_project_pop_up(self):

        if (self.check_unsaved_modifications() == 1):
            self.pop_up_close = Ui_Dialog_Quit(self.database.getName())
            self.pop_up_close.save_as_signal.connect(self.saveChoice)
            self.pop_up_close.exec()
            can_switch = self.pop_up_close.can_exit()

        else:
            can_switch = True
        if can_switch:

            # Opens a pop-up when the 'New Project' action is clicked and updates the recent projects
            self.exPopup = Ui_Dialog_New_Project()

            # Once the user has selected his project, the 'signal_create_project" signal is emitted
            # Which will be connected to the modify_ui method that controls the following processes
            self.exPopup.signal_create_project.connect(self.modify_ui)

            if self.exPopup.exec_() == QDialog.Accepted:

                self.remove_raw_files_useless()  # We remove the useless files from the old project

                file_name = self.exPopup.selectedFiles()
                self.exPopup.retranslateUi(self.exPopup.selectedFiles())
                file_name = self.exPopup.relative_path

                self.database = DataBase(self.exPopup.relative_path, True)

                self.update_project(file_name) # Project updated everywhere

    def open_project_pop_up(self):
        """ Opens a pop-up when the 'Open Project' action is clicked and updates the recent projects """
        # Ui_Dialog() is defined in pop_ups.py

        self.exPopup = Ui_Dialog_Open_Project()
        self.exPopup.signal_create_project.connect(self.modify_ui)
        if self.exPopup.exec_() == QDialog.Accepted:

            file_name = self.exPopup.selectedFiles()
            self.exPopup.retranslateUi(file_name)
            file_name = self.exPopup.relative_path

            self.switch_project(self.exPopup.relative_path, file_name, self.exPopup.name)  # We switch project

    def open_recent_project(self):
        """ Opens a recent project """
        action = self.sender()
        if action:
            file_name = action.data()
            entire_path = os.path.abspath(file_name)
            path, name = os.path.split(entire_path)
            relative_path = os.path.relpath(file_name)

            self.switch_project(relative_path, file_name, name) # We switch project

    def switch_project(self, path, file_name, name):
        """
        Called to switch project if it's possible
        :param path: relative path of the new project
        :param file_name: raw file_name
        """

        # If the file exists
        if os.path.exists(os.path.join(path)):

            # We check for unsaved modifications
            if (self.check_unsaved_modifications() == 1):

                # If there are unsaved modifications, we ask the user what he wants to do
                self.pop_up_close = Ui_Dialog_Quit(self.database)
                self.pop_up_close.save_as_signal.connect(self.saveChoice)
                self.pop_up_close.exec()
                can_switch = self.pop_up_close.can_exit()

            else:
                can_switch = True

            # We can open a new project
            if can_switch:

                # We check for invalid scans in the project
                tempDatabase = DataBase(path, False)
                problem_list = controller.verify_scans(tempDatabase, path)

                # Message if invalid files
                if problem_list != []:
                    str_msg = ""
                    for element in problem_list:
                        str_msg += element + "\n\n"
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(
                        "These files have been modified or removed since they have been converted for the first time:")
                    msg.setInformativeText(str_msg)
                    msg.setWindowTitle("Warning")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.buttonClicked.connect(msg.close)
                    msg.exec()
                    return False

                # No errors in files, we can open the project
                else:
                    self.remove_raw_files_useless()  # We remove the useless files from the old project

                    self.database = tempDatabase  # New database

                    self.update_project(file_name) # Project updated everywhere

                    return True

        # The project doesn't exist anymore
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("The project selected doesn't exist anymore:")
            msg.setInformativeText(
                "The project selected " + name + " doesn't exist anymore.\nPlease select another one.")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            return False

    def update_project(self, file_name):
        """
        Updates the project once the database has been updated
        :param file_name: File name of the new project
        """

        self.data_browser.update_database(self.database)  # Database update databrowser

        # We reset the headers
        self.data_browser.table_data.nb_columns = len(self.database.getVisualizedTags())
        self.data_browser.table_data.setColumnCount(self.data_browser.table_data.nb_columns)
        self.data_browser.table_data.initialize_headers()
        self.data_browser.table_data.fill_headers()

        # List of scans refreshed with all the scans of the project
        scan_names_list = []
        for scan in self.database.getScans():
            scan_names_list.append(scan.scan)
        self.data_browser.table_data.scans_to_visualize = scan_names_list

        self.data_browser.table_data.update_table()  # Table updated with the new project

        # Window name updated
        if self.database.isTempProject:
            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - Unnamed project')
        else:
            self.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - ' + self.database.getName())

        # List of project updated
        self.saved_projects_list = self.saved_projects.addSavedProject(file_name)
        self.update_recent_projects_actions()

    def update_recent_projects_actions(self):
        """ Updates the list of recent projects """
        if self.saved_projects_list != []:
            for i in range(min(len(self.saved_projects_list), self.saved_projects.maxProjects)):
                text = os.path.basename(self.saved_projects_list[i])
                self.saved_projects_actions[i].setText(text)
                self.saved_projects_actions[i].setData(self.saved_projects_list[i])
                self.saved_projects_actions[i].setVisible(True)

    def see_all_projects(self):
        """ Opens a pop-up when the 'See all projects' action is clicked and show the recent projects """
        # Ui_Dialog() is defined in pop_ups.py
        self.exPopup = Ui_Dialog_See_All_Projects(self.saved_projects, self)
        self.exPopup.signal_create_project.connect(self.modify_ui)
        if self.exPopup.exec_() == QDialog.Accepted:
            file_name = self.exPopup.relative_path
            self.saved_projects_list = self.saved_projects.addSavedProject(file_name)
            self.update_recent_projects_actions()

            problem_list = controller.verify_scans(self.database, self.exPopup.relative_path)
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

    def project_properties_pop_up(self):
        """ Opens the Project properties pop-up """
        self.pop_up_settings = Ui_Dialog_Settings(self.database)
        self.pop_up_settings.setGeometry(300, 200, 800, 600)
        self.pop_up_settings.show()

        if self.pop_up_settings.exec_() == QDialog.Accepted:
            self.data_browser.table_data.update_table()

    def software_preferences_pop_up(self):
        """ Opens the MIA2 preferences pop-up """
        self.pop_up_preferences = Ui_Dialog_Preferences(self)
        self.pop_up_preferences.setGeometry(300, 200, 800, 600)
        self.pop_up_preferences.show()

        if self.pop_up_preferences.exec_() == QDialog.Accepted:
            self.data_browser.table_data.update_table()

    def import_data(self):
        """ Calls the import software (MRI File Manager), reads the imported files and loads them into the
         data base """
        # Opens the conversion software to convert the MRI files in Nifti/Json
        code_exit = subprocess.call(['java', '-Xmx4096M', '-jar', os.path.join('..', '..', 'ressources', 'MRI_File_Manager', 'MRIManager.jar'),
                         '[ExportNifti] ' + os.path.join(self.database.folder, 'data', 'raw_data'),
                         '[ExportToMIA] PatientName-StudyName-CreationDate-SeqNumber-Protocol-SequenceName-AcquisitionTime',
                         'CloseAfterExport'])
        # 'NoLogExport'if we don't want log export

        if code_exit == 0:
            controller.read_log(self.database)

            scan_names_list = []
            for scan in self.database.getScans():
                scan_names_list.append(scan.scan)

            self.data_browser.table_data.scans_to_visualize = scan_names_list

            self.data_browser.table_data.nb_rows = len(scan_names_list)
            self.data_browser.table_data.setRowCount(self.data_browser.table_data.nb_rows)
            self.data_browser.table_data.update_table()

        else:
            pass


