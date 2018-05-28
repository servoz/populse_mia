from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog, QMessageBox
import os
import shutil
import hashlib

class Ui_Dialog_add_path(QDialog):
    """
    Is called when the user wants to add a path to the project
    """

    def __init__(self, project, table):

        super().__init__()
        self.project = project
        self.table = table
        self.setWindowTitle("Add a path")

        vbox_layout = QVBoxLayout()

        hbox_layout = QHBoxLayout()
        file_label = QLabel("File: ")
        self.file_line_edit = QLineEdit()
        self.file_line_edit.setFixedWidth(300)
        file_button = QPushButton("Choose a path")
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
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.save_path)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        hbox_layout.addWidget(ok_button)
        hbox_layout.addWidget(cancel_button)
        vbox_layout.addLayout(hbox_layout)

        self.setLayout(vbox_layout)

    def file_to_choose(self):
        """
        Lets the user choose a file to import
        """

        fname = QFileDialog.getOpenFileName(self, 'Choose a path to import', '/home')
        if fname[0]:
            self.file_line_edit.setText(fname[0])

    def save_path(self):

        path = self.file_line_edit.text()
        path_type = self.type_line_edit.text()
        if path != "" and os.path.exists(path) and path_type != "":
            path = os.path.relpath(path)
            filename = os.path.basename(path)
            copy_path = os.path.join(self.project.folder, "data", "downloaded_data", filename)
            shutil.copy(path, copy_path)
            with open(path, 'rb') as scan_file:
                data = scan_file.read()
                checksum = hashlib.md5(data).hexdigest()
            path = os.path.join("data", "downloaded_data", filename)
            self.project.database.add_document(path)
            self.project.database.new_value(path, "Type", path_type, path_type)
            self.project.database.new_value(path, "Checksum", checksum, checksum)
            self.table.scans_to_visualize.append(path)
            self.table.add_rows(self.project.database.get_documents_names())
        self.close()