from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog
from functools import partial
from PopUps.Ui_Visualized_Tags import Ui_Visualized_Tags
from PopUps.Ui_Informations import Ui_Informations

from Project.Project import TAG_FILENAME, COLLECTION_CURRENT, COLLECTION_INITIAL

class Ui_Dialog_Settings(QDialog):
    """
    Is called when the user wants to change the software settings
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_settings_change = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.pop_up(project)
        self.old_visibles_tags = [field.name for field in project.database.get_fields(COLLECTION_CURRENT) if field.visibility]

    def pop_up(self, database):
        _translate = QtCore.QCoreApplication.translate

        self.setObjectName("Dialog")
        self.setWindowTitle('Project properties')

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setEnabled(True)

        # The 'Visualized tags" tab
        self.tab_tags = Ui_Visualized_Tags(database)
        self.tab_tags.setObjectName("tab_tags")
        self.tab_widget.addTab(self.tab_tags, _translate("Dialog", "Visualized tags"))

        # The 'Informations" tab
        self.tab_infos = Ui_Informations(database)
        self.tab_infos.setObjectName("tab_infos")
        self.tab_widget.addTab(self.tab_infos, _translate("Dialog", "Informations"))

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, database))

        # The 'Cancel' push button
        self.push_button_cancel = QtWidgets.QPushButton("Cancel")
        self.push_button_cancel.setObjectName("pushButton_cancel")
        self.push_button_cancel.clicked.connect(self.close)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addStretch(1)
        hbox_buttons.addWidget(self.push_button_ok)
        hbox_buttons.addWidget(self.push_button_cancel)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tab_widget)
        vbox.addLayout(hbox_buttons)

        self.setLayout(vbox)

    def ok_clicked(self, project):
        historyMaker = []
        historyMaker.append("modified_visibilities")
        historyMaker.append(self.old_visibles_tags)
        new_visibilities = []
        for tag in project.database.get_fields(COLLECTION_CURRENT):
            tag.visibility = False
        for tag in project.database.get_fields(COLLECTION_INITIAL):
            tag.visibility = False
        for x in range(self.tab_tags.list_widget_selected_tags.count()):
            visible_tag = self.tab_tags.list_widget_selected_tags.item(x).text()
            new_visibilities.append(visible_tag)
            project.database.get_field(COLLECTION_CURRENT, visible_tag).visibility = True
            project.database.get_field(COLLECTION_INITIAL, visible_tag).visibility = True
        new_visibilities.append(TAG_FILENAME)
        project.database.get_field(COLLECTION_CURRENT, TAG_FILENAME).visibility = True
        project.database.get_field(COLLECTION_INITIAL, TAG_FILENAME).visibility = True
        historyMaker.append(new_visibilities)
        project.undos.append(historyMaker)
        project.redos.clear()
        #Database.setName(self.tab_infos.name_value.text())
        self.accept()
        self.close()

