##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog

# Populse_MIA imports
from populse_mia.pop_ups.pop_up_visualized_tags import PopUpVisualizedTags
from populse_mia.pop_ups.pop_up_information import PopUpInformation
from populse_mia.project.project import TAG_FILENAME


class PopUpProperties(QDialog):
    """
    Is called when the user wants to change the current project's properties

    Attributes:
        - project: current project in the software
        - databrowser: data browser instance of the software
        - old_tags: visualized tags before opening this dialog

    Methods:
        - ok_clicked: saves the modifications and updates the data browser
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_settings_change = pyqtSignal()

    def __init__(self, project, databrowser, old_tags):
        super().__init__()
        self.setModal(True)
        self.project = project
        self.databrowser = databrowser
        self.old_tags = old_tags

        _translate = QtCore.QCoreApplication.translate

        self.setObjectName("Dialog")
        self.setWindowTitle('project properties')

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setEnabled(True)

        # The 'Visualized tags" tab
        self.tab_tags = PopUpVisualizedTags(self.project, self.project.session.get_visibles())
        self.tab_tags.setObjectName("tab_tags")
        self.tab_widget.addTab(self.tab_tags, _translate("Dialog", "Visualized tags"))

        # The 'Informations" tab
        self.tab_infos = PopUpInformation(self.project)
        self.tab_infos.setObjectName("tab_infos")
        self.tab_widget.addTab(self.tab_infos, _translate("Dialog", "Informations"))

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(self.ok_clicked)

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

    def ok_clicked(self):
        """
        Saves the modifications and updates the data browser
        """
        history_maker = ["modified_visibilities", self.old_tags]
        new_visibilities = []

        for x in range(self.tab_tags.list_widget_selected_tags.count()):
            visible_tag = self.tab_tags.list_widget_selected_tags.item(x).text()
            new_visibilities.append(visible_tag)

        new_visibilities.append(TAG_FILENAME)
        self.project.session.set_visibles(new_visibilities)
        history_maker.append(new_visibilities)

        self.project.undos.append(history_maker)
        self.project.redos.clear()

        # Columns updated
        self.databrowser.table_data.update_visualized_columns(self.old_tags, self.project.session.get_visibles())
        self.accept()
        self.close()

