##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QPushButton, QLabel


class PopUpClosePipeline(QDialog):
    """
    Is called when the user closes a pipeline editor that has been modified

    Attributes:
        - pipeline_name: name of the pipeline (basename)
        - bool_save_as: boolean to True if the pipeline needs to be saved
        - bool_exit: boolean to True if we can exit the editor
        - save_as_signal: signal emitted to save the pipeline under another name
        - do_not_save_signal: signal emitted to close the editor
        - cancel_signal: signal emitted to cancel the action

    Methods:
        - save_as_clicked: makes the actions to save the pipeline
        - do_not_save_clicked: makes the actions not to save the pipeline
        - cancel_clicked: makes the actions to cancel the action
        - can_exit: returns the value of bool_exit
    """

    save_as_signal = pyqtSignal()
    do_not_save_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self, pipeline_name):
        super().__init__()

        self.pipeline_name = pipeline_name

        self.bool_exit = False
        self.bool_save_as = False

        self.setWindowTitle("Confirm pipeline closing")

        label = QLabel(self)
        label.setText('Do you want to close the pipeline without saving ' + self.pipeline_name + '?')

        self.push_button_save_as = QPushButton("Save", self)
        self.push_button_do_not_save = QPushButton("Do not save", self)
        self.push_button_cancel = QPushButton("Cancel", self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.push_button_save_as)
        hbox.addWidget(self.push_button_do_not_save)
        hbox.addWidget(self.push_button_cancel)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.push_button_save_as.clicked.connect(self.save_as_clicked)
        self.push_button_do_not_save.clicked.connect(self.do_not_save_clicked)
        self.push_button_cancel.clicked.connect(self.cancel_clicked)

    def save_as_clicked(self):
        """
        Makes the actions to save the pipeline
        """
        self.save_as_signal.emit()
        self.bool_save_as = True
        self.bool_exit = True
        self.close()

    def do_not_save_clicked(self):
        """
        Makes the actions not to save the pipeline
        """
        self.bool_exit = True
        self.close()

    def cancel_clicked(self):
        """
        Makes the actions to cancel the action
        """
        self.bool_exit = False
        self.close()

    def can_exit(self):
        """
        Returns the value of bool_exit

        :return: bool_exit value
        """
        return self.bool_exit
