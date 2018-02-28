from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog


class Ui_Dialog_remove_tag(QDialog):
    """
     Is called when the user wants to remove a user tag to the project
     """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_remove_tag = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.database = database
        self.pop_up()

    def pop_up(self):
        _translate = QtCore.QCoreApplication.translate
        self.setObjectName("Remove a tag")

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton(self)
        self.push_button_ok.setObjectName("push_button_ok")
        self.push_button_ok.setText(_translate("Remove a tag", "OK"))


        hbox_buttons = QHBoxLayout()
        hbox_buttons.addStretch(1)
        hbox_buttons.addWidget(self.push_button_ok)

        # The "Tag list" label
        self.label_tag_list = QtWidgets.QLabel(self)
        self.label_tag_list.setTextFormat(QtCore.Qt.AutoText)
        self.label_tag_list.setObjectName("label_tag_list")
        self.label_tag_list.setText(_translate("Remove a tag", "Available tags:"))

        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.search_str)

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.label_tag_list)
        hbox_top.addStretch(1)
        hbox_top.addWidget(self.search_bar)

        # The list of tags
        self.list_widget_tags = QtWidgets.QListWidget(self)
        self.list_widget_tags.setObjectName("listWidget_tags")
        self.list_widget_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_top)
        vbox.addWidget(self.list_widget_tags)
        vbox.addLayout(hbox_buttons)

        self.setLayout(vbox)

        #DATABASE
        for tag in self.database.getUserTags():
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag.tag))

        #PROJECT
        """for tag in self.project.user_tags:
            tag_name = tag['name']
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag_name))"""

        self.setLayout(vbox)

        # Connecting the OK push button
        self.push_button_ok.clicked.connect(self.ok_action)

    def search_str(self, str_search):
        _translate = QtCore.QCoreApplication.translate

        if str_search != "":
            return_list = []
            for tag in self.database.getUserTags():
                tag_name = tag.tag
                if str_search.upper() in tag_name.upper():
                    return_list.append(tag_name)
        else:
            return_list = []
            for tag in self.database.getUserTags():
                tag_name = tag.tag
                return_list.append(tag_name)
        self.list_widget_tags.clear()
        for tag_name in return_list:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag_name))

    def ok_action(self):

        self.accept()
        self.close()

    def get_values(self):
        self.tag_names_to_remove = []
        for item in self.list_widget_tags.selectedItems():
            self.tag_names_to_remove.append(item.text())
        return self.tag_names_to_remove

