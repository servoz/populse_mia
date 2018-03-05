from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, \
    QVBoxLayout, QMessageBox, QHeaderView
from PyQt5.QtGui import QIcon
import os
from ProjectManager import controller
from DataBase.DataBase import DataBase
from PopUps.Ui_Dialog_Quit import Ui_Dialog_Quit

class Ui_Dialog_See_All_Projects(QDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that a new project has been opened
    signal_create_project = pyqtSignal()

    def __init__(self, savedProjects, mainWindow):
        super().__init__()

        self.mainWindow = mainWindow

        self.setWindowTitle('See all saved projects')
        self.setMinimumWidth(500)

        ############################### TREE WIDGET ###############################

        self.label = QLabel()
        self.label.setText('List of saved projects')

        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setHeaderLabels(['Name', 'Path', 'State'])

        i = -1
        for path in savedProjects.pathsList:
            i += 1
            text = os.path.basename(path)
            wdg = QTreeWidgetItem()
            wdg.setText(0, text)
            wdg.setText(1, os.path.abspath(path))
            wdg.setIcon(2, self.checkState(path, text))

            self.treeWidget.addTopLevelItem(wdg)

        hd = self.treeWidget.header()
        hd.setSectionResizeMode(QHeaderView.ResizeToContents)

        ############################### BUTTONS ###############################

        # The 'Open project' push button
        self.pushButtonOpenProject = QPushButton("Open project")
        self.pushButtonOpenProject.setObjectName("pushButton_ok")
        self.pushButtonOpenProject.clicked.connect(lambda: self.retranslateUi(self.itemToPath()))

        # The 'Cancel' push button
        self.pushButtonCancel = QPushButton("Cancel")
        self.pushButtonCancel.setObjectName("pushButton_cancel")
        self.pushButtonCancel.clicked.connect(self.close)

        ############################### LAYOUTS ###############################

        self.hBoxButtons = QHBoxLayout()
        self.hBoxButtons.addStretch(1)
        self.hBoxButtons.addWidget(self.pushButtonOpenProject)
        self.hBoxButtons.addWidget(self.pushButtonCancel)

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.label)
        self.vBox.addWidget(self.treeWidget)
        self.vBox.addLayout(self.hBoxButtons)

        self.setLayout(self.vBox)

    def checkState(self, path, text):
        """ Checks if the project still exists and returns the corresponding icon """
        if os.path.exists(os.path.join(path)):
            icon = QIcon(os.path.join('..', 'sources_images', 'green_v.png'))
        else:
            icon = QIcon(os.path.join('..', 'sources_images', 'red_cross.png'))
        return icon

    def itemToPath(self):
        nb_items = len(self.treeWidget.selectedItems())
        if nb_items == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a project to open")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            return ""
        else:
            item = self.treeWidget.selectedItems()[0]
            text = item.text(1)
            return text

    def retranslateUi(self, file_name):
        if file_name != "":
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            #self.path = entire_path
            self.relative_path = os.path.relpath(file_name)

            # If the file exists
            if os.path.exists(self.relative_path):

                if (self.mainWindow.check_unsaved_modifications() == 1):
                    self.mainWindow.pop_up_close = Ui_Dialog_Quit(self.mainWindow.database.getName())
                    self.mainWindow.pop_up_close.save_as_signal.connect(self.mainWindow.saveChoice)
                    self.mainWindow.pop_up_close.exec()
                    can_switch = self.mainWindow.pop_up_close.can_exit()

                else:
                    can_switch = True
                if can_switch:
                    tempDatabase = DataBase(self.relative_path, False)
                    problem_list = controller.verify_scans(tempDatabase, self.relative_path)
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

                    else:
                        self.mainWindow.database.unsaveModifications()

                        controller.open_project(self.name, self.relative_path)

                        self.mainWindow.database = DataBase(self.relative_path, False)
                        self.mainWindow.data_browser.update_database(self.mainWindow.database)
                        scan_names_list = []
                        for scan in self.mainWindow.database.getScans():
                            scan_names_list.append(scan.scan)
                        self.mainWindow.data_browser.table_data.scans_to_visualize = scan_names_list
                        self.mainWindow.data_browser.table_data.update_table()

                        if self.mainWindow.database.isTempProject:
                            self.mainWindow.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - Unnamed project')
                        else:
                            self.mainWindow.setWindowTitle('MIA2 - Multiparametric Image Analysis 2 - ' + self.mainWindow.database.getName())

                        self.accept()
                        self.close()
                        # A signal is emitted to tell that the project has been created
                        self.signal_create_project.emit()
