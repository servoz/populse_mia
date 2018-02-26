from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QDialog, QPushButton, QLabel
import os
from ProjectManager import controller
import Utils.utils as utils

class Ui_Dialog_Save_Project_As(QFileDialog):
    """
    Is called when the user wants to save a project under another name
    """

    # Signal that will be emitted at the end to tell that the new file name has been chosen
    signal_saved_project = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setLabelText(QFileDialog.Accept, "Save as")
        self.setOption(QFileDialog.ShowDirsOnly, True)
        self.setAcceptMode(QFileDialog.AcceptSave)

        # Setting the projects directory as default
        if not(os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects'))):
            os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects'))
        self.setDirectory(os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects')))
        self.finished.connect(self.return_value)

    def return_value(self):
        file_name = self.selectedFiles()
        if len(file_name) > 0:
            file_name = file_name[0]
            #file_name = utils.remove_accents(file_name.replace(" ", "_"))
            if file_name:
                entire_path = os.path.abspath(file_name)
                self.path, self.name = os.path.split(entire_path)
                self.total_path = entire_path
                self.relative_path = os.path.relpath(file_name)
                self.relative_subpath = os.path.relpath(self.path)

                if not os.path.exists(self.relative_path):
                    controller.createProject(self.name, '~', self.relative_subpath)
                    self.close()
                    # A signal is emitted to tell that the project has been created
                    self.signal_saved_project.emit()
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

            return file_name
