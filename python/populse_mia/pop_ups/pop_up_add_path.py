##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import shutil
import hashlib

# PyQt5 imports
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox

# Populse_MIA imports
from populse_mia.project.project import COLLECTION_CURRENT, COLLECTION_INITIAL, TAG_TYPE, TAG_CHECKSUM, TYPE_NII, \
    TYPE_MAT


class PopUpAddPath(QDialog):
    """
    Is called when the user wants to add a document to the project without importing from populse_mia.e MRI File Manager

    Attributes:
        - project: current project in the software
        - databrowser: data browser instance of the software

    Methods:
        - ok_clicked: updates the "scan_list" attribute of several widgets
        - find_type: tries to find the document type when the document is changed
        - file_to_choose: lets the user choose a file to import
        - save_path: adds the path to the database and the data browser
    """

    def __init__(self, project, databrowser):

        super().__init__()
        self.project = project
        self.databrowser = databrowser
        self.setWindowTitle("Add a document")
        self.setModal(True)

        vbox_layout = QVBoxLayout()

        hbox_layout = QHBoxLayout()
        file_label = QLabel("File: ")
        self.file_line_edit = QLineEdit()
        self.file_line_edit.setFixedWidth(300)
        self.file_line_edit.textChanged.connect(self.find_type)
        file_button = QPushButton("Choose a document")
        file_button.clicked.connect(self.file_to_choose)
        hbox_layout.addWidget(file_label)
        hbox_layout.addWidget(self.file_line_edit)
        hbox_layout.addWidget(file_button)
        vbox_layout.addLayout(hbox_layout)

        hbox_layout = QHBoxLayout()
        type_label = QLabel("Type: ")
        self.type_line_edit = QLineEdit()
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(self.type_line_edit)
        vbox_layout.addLayout(hbox_layout)

        hbox_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.save_path)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        hbox_layout.addWidget(self.ok_button)
        hbox_layout.addWidget(cancel_button)
        vbox_layout.addLayout(hbox_layout)

        self.setLayout(vbox_layout)

    def find_type(self):
        """
        Tries to find the document type when the document is changed
        """

        new_file = self.file_line_edit.text()
        filename, file_extension = os.path.splitext(new_file)
        if file_extension == ".nii":
            self.type_line_edit.setText(TYPE_NII)
        elif file_extension == ".mat":
            self.type_line_edit.setText(TYPE_MAT)
        else:
            self.type_line_edit.setText("")

    def file_to_choose(self):
        """
        Lets the user choose a file to import
        """

        fname = QFileDialog.getOpenFileName(self, 'Choose a document to import', '/home')
        if fname[0]:
            self.file_line_edit.setText(fname[0])

    def save_path(self):
        """
        Adds the path to the database and the data browser
        """

        path = self.file_line_edit.text()
        path_type = self.type_line_edit.text()
        if path != "" and os.path.exists(path) and path_type != "":

            # For history
            history_maker = []
            history_maker.append("add_scans")

            path = os.path.relpath(path)
            filename = os.path.basename(path)
            copy_path = os.path.join(self.project.folder, "data", "downloaded_data", filename)
            shutil.copy(path, copy_path)
            with open(path, 'rb') as scan_file:
                data = scan_file.read()
                checksum = hashlib.md5(data).hexdigest()
            path = os.path.join("data", "downloaded_data", filename)
            self.project.session.add_document(COLLECTION_CURRENT, path)
            self.project.session.add_document(COLLECTION_INITIAL, path)
            values_added = []
            self.project.session.add_value(COLLECTION_INITIAL, path, TAG_TYPE, path_type)
            self.project.session.add_value(COLLECTION_CURRENT, path, TAG_TYPE, path_type)
            values_added.append([path, TAG_TYPE, path_type, path_type])
            self.project.session.add_value(COLLECTION_INITIAL, path, TAG_CHECKSUM, checksum)
            self.project.session.add_value(COLLECTION_CURRENT, path, TAG_CHECKSUM, checksum)
            values_added.append([path, TAG_CHECKSUM, checksum, checksum])

            # For history
            history_maker.append([path])
            history_maker.append(values_added)
            self.project.undos.append(history_maker)
            self.project.redos.clear()

            # Databrowser updated
            self.databrowser.table_data.scans_to_visualize = self.project.session.get_documents_names(
                COLLECTION_CURRENT)
            self.databrowser.table_data.scans_to_search = self.project.session.get_documents_names(
                COLLECTION_CURRENT)
            self.databrowser.table_data.add_columns()
            self.databrowser.table_data.fill_headers()
            self.databrowser.table_data.add_rows([path])
            self.databrowser.reset_search_bar()
            self.databrowser.frame_advanced_search.setHidden(True)
            self.databrowser.advanced_search.rows = []
            self.close()
        else:
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Warning)
            self.msg.setText(
                "Invalid arguments")
            self.msg.setInformativeText(
                "The path must exist.\nThe path type can't be empty.")
            self.msg.setWindowTitle("Warning")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()
