from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog
from functools import partial
from PopUps.Ui_Visualized_Tags import Ui_Visualized_Tags
from PopUps.Ui_Informations import Ui_Informations

class Ui_Dialog_Settings(QDialog):
    """
    Is called when the user wants to change the software settings
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_settings_change = pyqtSignal()

    def __init__(self, project, database):
        super().__init__()
        self.pop_up(project, database)

    def pop_up(self, project, database):
        _translate = QtCore.QCoreApplication.translate

        self.setObjectName("Dialog")
        self.setWindowTitle('Project properties')

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setEnabled(True)

        # The 'Visualized tags" tab
        self.tab_tags = Ui_Visualized_Tags(project)
        self.tab_tags.setObjectName("tab_tags")
        self.tab_widget.addTab(self.tab_tags, _translate("Dialog", "Visualized tags"))

        # The 'Informations" tab
        self.tab_infos = Ui_Informations(project, database)
        self.tab_infos.setObjectName("tab_infos")
        self.tab_widget.addTab(self.tab_infos, _translate("Dialog", "Informations"))

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, project, database))

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

    def ok_clicked(self, project, database):
        project.tags_to_visualize = []
        database.resetAllVisibilities()
        for x in range(self.tab_tags.list_widget_selected_tags.count()):
            project.tags_to_visualize.append(self.tab_tags.list_widget_selected_tags.item(x).text())
            database.setTagVisibility(self.tab_tags.list_widget_selected_tags.item(x).text(), True)
        database.saveModifications()
        #database.setName(self.tab_infos.name_value.text())
        self.accept()
        self.close()

