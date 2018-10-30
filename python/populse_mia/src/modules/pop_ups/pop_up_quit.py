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


class PopUpQuit(QDialog):
    """
    Is called when the user closes the software and the current project has been modified

    Attributes:
        - database: current database in the project
        - bool_exit: boolean equals to True if we can exit the software

    Methods:
        - save_as_clicked: makes the actions to save the project
        - do_not_save_clicked: makes the actions not to save the project
        - cancel_clicked: makes the actions to cancel the action
        - can_exit: returns the value of bool_exit
    """

    save_as_signal = pyqtSignal()
    do_not_save_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self, database):
        super().__init__()

        self.database = database

        self.bool_exit = False

        self.setWindowTitle("Confirm exit")

        label = QLabel(self)
        label.setText('Do you want to exit without saving ' + self.database.getName() + '?')

        push_button_save_as = QPushButton("Save", self)
        push_button_do_not_save = QPushButton("Do not save", self)
        push_button_cancel = QPushButton("Cancel", self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(push_button_save_as)
        hbox.addWidget(push_button_do_not_save)
        hbox.addWidget(push_button_cancel)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        push_button_save_as.clicked.connect(self.save_as_clicked)
        push_button_do_not_save.clicked.connect(self.do_not_save_clicked)
        push_button_cancel.clicked.connect(self.cancel_clicked)

    def save_as_clicked(self):
        """
        Makes the actions to save the project
        """
        self.save_as_signal.emit()
        self.bool_exit = True
        self.close()

    def do_not_save_clicked(self):
        """
        Makes the actions not to save the project
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
