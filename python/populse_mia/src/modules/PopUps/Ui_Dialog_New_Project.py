from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
import os
import Utils.Utils as utils

class Ui_Dialog_New_Project(QFileDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.setOption(QFileDialog.DontUseNativeDialog)
        self.setLabelText(QFileDialog.Accept, "Create")
        self.setAcceptMode(QFileDialog.AcceptSave)

        # Setting the projects directory as default
        utils.set_projects_directory_as_default(self)

    def retranslateUi(self, file_name):
        # file_name = self.selectedFiles()
        file_name = file_name[0]
        #file_name = Utils.remove_accents(file_name.replace(" ", "_"))
        if file_name:
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            self.relative_path = os.path.relpath(file_name)
            self.relative_subpath = os.path.relpath(self.path)

            if not os.path.exists(self.relative_path):
                self.close()
                # A signal is emitted to tell that the project has been created
                self.signal_create_project.emit()
            else:
                utils.message_already_exists()

        return file_name
