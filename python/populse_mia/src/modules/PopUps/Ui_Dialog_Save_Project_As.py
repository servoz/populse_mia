##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog
import os
import Utils.Utils as utils


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
        utils.set_projects_directory_as_default(self)

        self.finished.connect(self.return_value)

    def return_value(self):
        file_name = self.selectedFiles()
        if len(file_name) > 0:
            file_name = file_name[0]
            #file_name = Utils.remove_accents(file_name.replace(" ", "_"))
            projects_folder = os.path.join(os.path.join(os.path.relpath(os.curdir), '..', '..'), 'projects')
            projects_folder = os.path.abspath(projects_folder)
            if file_name and file_name != projects_folder:
                entire_path = os.path.abspath(file_name)
                self.path, self.name = os.path.split(entire_path)
                self.total_path = entire_path
                self.relative_path = os.path.relpath(file_name)
                self.relative_subpath = os.path.relpath(self.path)

                if not os.path.exists(self.relative_path) and self.name is not '':
                    self.close()
                    # A signal is emitted to tell that the project has been created
                    self.signal_saved_project.emit()
                else:
                    utils.message_already_exists()

            return file_name
