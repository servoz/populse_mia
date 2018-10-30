##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout


class PopUpFilterSelection(QDialog):
    """
    Is called when the user wants to open a filter that has already been saved

    Attributes:
        - project: current project in the software

    Methods:
        - search_str: matches the searched pattern with the saved filters
        - ok_clicked: actions when the "OK" button is clicked
        - cancel_clicked: closes the pop-up
    """

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.setModal(True)

        _translate = QtCore.QCoreApplication.translate

        # The "Filter list" label
        self.label_filter_list = QtWidgets.QLabel(self)
        self.label_filter_list.setTextFormat(QtCore.Qt.AutoText)
        self.label_filter_list.setObjectName("label_filter_list")
        self.label_filter_list.setText(_translate("main_window", "Available filters:"))

        # The search bar to search in the list of filters
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.search_str)

        # The list of filters
        self.list_widget_filters = QtWidgets.QListWidget(self)
        self.list_widget_filters.setObjectName("listWidget_tags")
        self.list_widget_filters.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.push_button_ok = QtWidgets.QPushButton(self)
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.setText("OK")
        self.push_button_ok.clicked.connect(self.ok_clicked)

        self.push_button_cancel = QtWidgets.QPushButton(self)
        self.push_button_cancel.setObjectName("pushButton_cancel")
        self.push_button_cancel.setText("Cancel")
        self.push_button_cancel.clicked.connect(self.cancel_clicked)

        hbox_top_left = QHBoxLayout()
        hbox_top_left.addWidget(self.label_filter_list)
        hbox_top_left.addWidget(self.search_bar)

        vbox_top_left = QVBoxLayout()
        vbox_top_left.addLayout(hbox_top_left)
        vbox_top_left.addWidget(self.list_widget_filters)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addStretch(1)
        hbox_buttons.addWidget(self.push_button_ok)
        hbox_buttons.addWidget(self.push_button_cancel)

        vbox_final = QVBoxLayout()
        vbox_final.addLayout(vbox_top_left)
        vbox_final.addLayout(hbox_buttons)

        self.setLayout(vbox_final)

    def search_str(self, str_search):
        """
        Matches the searched pattern with the saved filters

        :param str_search: string pattern to search
        """
        return_list = []
        if str_search != "":
            for filter in self.project.filters:
                if str_search.upper() in filter.name.upper():
                    return_list.append(filter.name)
        else:
            for filter in self.project.filters:
                return_list.append(filter.name)

        for idx in range(self.list_widget_filters.count()):
            item = self.list_widget_filters.item(idx)
            if item.text() in return_list:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def ok_clicked(self):
        """
        Actions when the "OK" button is clicked
        """
        # Has to be override in the PopUpSelectFilter* classes
        pass

    def cancel_clicked(self):
        """
        Closes the pop-up
        """
        self.close()
