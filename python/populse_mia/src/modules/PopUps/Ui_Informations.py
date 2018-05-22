from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit


class Ui_Informations(QWidget):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.retranslate_Ui(project)

    def retranslate_Ui(self, database):
        _translate = QtCore.QCoreApplication.translate

        name_label = QLabel("Name: ")
        self.name_value = QLineEdit(database.getName())
        folder_label = QLabel("Root folder: " + database.folder)
        date_label = QLabel("Date of creation: " + database.getDate())

        box = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(name_label)
        row.addWidget(self.name_value)
        box.addLayout(row)
        box.addWidget(folder_label)
        box.addWidget(date_label)
        box.addStretch(1)

        self.setLayout(box)
