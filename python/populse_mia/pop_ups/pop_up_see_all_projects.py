##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os

# PyQt5 imports
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, \
    QVBoxLayout, QMessageBox, QHeaderView
from PyQt5.QtGui import QIcon


class PopUpSeeAllProjects(QDialog):
    """
    Is called when the user wants to create a see all the projects

    Attributes:
        - main_window: main window of the software
        - path: absolute path to the selected project's folder (without the project folder)
        - name: name of the selected project
        - relative_path: relative path to the selected project (with the project folder)

    Methods:
        - checkState: checks if the project still exists and returns the corresponding icon
        - itemToPath: returns the path of the first selected item
        - open_project: switches to the selected project
    """

    def __init__(self, saved_projects, main_window):
        super().__init__()

        self.mainWindow = main_window

        self.setWindowTitle('See all saved projects')
        self.setMinimumWidth(500)

        # Tree widget

        self.label = QLabel()
        self.label.setText('List of saved projects')

        self.treeWidget = QTreeWidget()
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setHeaderLabels(['Name', 'Path', 'State'])

        i = -1
        for path in saved_projects.pathsList:
            i += 1
            text = os.path.basename(path)
            wdg = QTreeWidgetItem()
            wdg.setText(0, text)
            wdg.setText(1, os.path.abspath(path))
            wdg.setIcon(2, self.checkState(path))

            self.treeWidget.addTopLevelItem(wdg)

        hd = self.treeWidget.header()
        hd.setSectionResizeMode(QHeaderView.ResizeToContents)

        # Buttons

        # The 'Open project' push button
        self.pushButtonOpenProject = QPushButton("Open project")
        self.pushButtonOpenProject.setObjectName("pushButton_ok")
        self.pushButtonOpenProject.clicked.connect(self.open_project)

        # The 'Cancel' push button
        self.pushButtonCancel = QPushButton("Cancel")
        self.pushButtonCancel.setObjectName("pushButton_cancel")
        self.pushButtonCancel.clicked.connect(self.close)

        # Layouts
        self.hBoxButtons = QHBoxLayout()
        self.hBoxButtons.addStretch(1)
        self.hBoxButtons.addWidget(self.pushButtonOpenProject)
        self.hBoxButtons.addWidget(self.pushButtonCancel)

        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.label)
        self.vBox.addWidget(self.treeWidget)
        self.vBox.addLayout(self.hBoxButtons)

        self.setLayout(self.vBox)

    def checkState(self, path):
        """
        Checks if the project still exists and returns the corresponding icon

        :param path: path of the project
        :return: either a green "v" or a red cross depending on the existence of the project
        """
        sources_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                          "sources_images")
        if os.path.exists(os.path.join(path)):
            icon = QIcon(os.path.join(sources_images_dir, 'green_v.png'))
        else:
            icon = QIcon(os.path.join(sources_images_dir, 'red_cross.png'))
        return icon

    def item_to_path(self):
        """
        Returns the path of the first selected item

        :return: the path of the first selected item
        """
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

    def open_project(self):
        """
        Switches to the selected project
        """
        file_name = self.item_to_path()
        if file_name != "":
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            self.relative_path = os.path.relpath(file_name)

            project_switched = self.mainWindow.switch_project(self.relative_path, self.relative_path, self.name)

            if project_switched:
                self.accept()
                self.close()
