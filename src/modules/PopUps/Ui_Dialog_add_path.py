from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QPushButton, QFileDialog

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
        print(self.project.database.add_path(path, self.type_line_edit.text()))
        self.table.scans_to_visualize.append(path)
        self.table.add_rows(self.project.database.get_paths_names())
        self.close()