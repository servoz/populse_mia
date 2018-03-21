from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QHBoxLayout, QDialog, QPushButton, QLabel
import os
import ProjectManager.controller as controller
import Utils.utils as utils
from DataBase.DataBaseModel import createDatabase

class Ui_Dialog_Export_Current_Filter(QFileDialog):
    """
    Is called when the user wants to save the current filter
    """

    # Signal that will be emitted at the end to tell that the filter has been saved
    signal_save_current_filter = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setDefaultSuffix(".json")
        self.setLabelText(QFileDialog.Accept, "Create")
        self.setAcceptMode(QFileDialog.AcceptSave)

        # Setting the filters directory as default
        utils.set_filters_directory_as_default(self)

    def retranslateUi(self, file_name):
        file_name = file_name[0]
        if file_name:
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            self.relative_path = os.path.relpath(file_name)
            self.relative_subpath = os.path.relpath(self.path)

            if not os.path.exists(self.relative_path):
                self.close()
                # A signal is emitted to tell that the project has been created
                self.signal_save_current_filter.emit()
            else:
                utils.message_already_exists()

        return file_name
