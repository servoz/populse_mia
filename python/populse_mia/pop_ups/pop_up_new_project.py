##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os

# PyQt5 imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog

# Populse_MIA imports
from populse_mia.utils import utils


class PopUpNewProject(QFileDialog):
    """
    Is called when the user wants to create a new project

    Attributes:
        - path: absolute path to the project's folder (without the project folder)
        - name: name of the project
        - relative_path: relative path to the new project (with the project folder)
        - relative_subpath: relative path to the new project (without the project folder)
    Method:
        - get_filename: sets the widget's attributes depending on the selected file name
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setLabelText(QFileDialog.Accept, "Create")
        self.setAcceptMode(QFileDialog.AcceptSave)

        # Setting the projects directory as default
        utils.set_projects_directory_as_default(self)

    def get_filename(self, file_name_tuple):
        """
        Sets the widget's attributes depending on the selected file name

        :param file_name_tuple: tuple obtained with the selectedFiles method
        :return: real file name
        """
        file_name = file_name_tuple[0]
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
