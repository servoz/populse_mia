from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QDialog, QPushButton, QLabel
import os
from ProjectManager import controller
import Utils.utils as utils

class Ui_Dialog_Open_Project(QFileDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.Directory)

        # Setting the projects directory as default
        if not(os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects'))):
            os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects'))
        self.setDirectory(os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects')))

    def retranslateUi(self, file_name):
        #file_name = self.getExistingDirectory(self, "Select a project directory")
        file_name = file_name[0]
        #file_name = utils.remove_accents(file_name.replace(" ", "_"))
        if file_name:
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            #self.path = entire_path
            self.relative_path = os.path.relpath(file_name)

            # If the file exists
            if os.path.exists(os.path.join(self.relative_path, self.name, self.name + '.json')):
                self.close()
                # A signal is emitted to tell that the project has been created
                self.signal_create_project.emit()
            else:
                _translate = QtCore.QCoreApplication.translate
                self.dialog_box = QDialog()
                self.label = QLabel(self.dialog_box)
                self.label.setText(_translate("MainWindow", 'This name already exists in this parent folder'))
                self.push_button_ok = QPushButton(self.dialog_box)
                self.push_button_ok.setText('OK')
                self.push_button_ok.clicked.connect(self.dialog_box.close)
                hbox = QHBoxLayout()
                hbox.addWidget(self.label)
                hbox.addWidget(self.push_button_ok)

                self.dialog_box.setLayout(hbox)