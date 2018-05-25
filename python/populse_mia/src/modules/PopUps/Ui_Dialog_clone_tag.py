from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QMessageBox
from functools import partial

class Ui_Dialog_clone_tag(QDialog):
    """
    Is called when the user wants to clone a tag to the project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_clone_tag = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.setWindowTitle("Clone a tag")
        self.pop_up(project)

    def pop_up(self, project):
        _translate = QtCore.QCoreApplication.translate
        self.setObjectName("Clone a tag")

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton(self)
        self.push_button_ok.setObjectName("push_button_ok")
        self.push_button_ok.setText(_translate("Clone a tag", "OK"))

        # The 'New tag name' text edit
        self.line_edit_new_tag_name = QtWidgets.QLineEdit(self)
        self.line_edit_new_tag_name.setObjectName("lineEdit_new_tag_name")

        # The 'New tag name' label
        self.label_new_tag_name = QtWidgets.QLabel(self)
        self.label_new_tag_name.setTextFormat(QtCore.Qt.AutoText)
        self.label_new_tag_name.setObjectName("label_new_tag_name")
        self.label_new_tag_name.setText(_translate("Clone a tag", "New tag name:"))

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.label_new_tag_name)
        hbox_buttons.addWidget(self.line_edit_new_tag_name)
        hbox_buttons.addStretch(1)
        hbox_buttons.addWidget(self.push_button_ok)

        # The "Tag list" label
        self.label_tag_list = QtWidgets.QLabel(self)
        self.label_tag_list.setTextFormat(QtCore.Qt.AutoText)
        self.label_tag_list.setObjectName("label_tag_list")
        self.label_tag_list.setText(_translate("Clone a tag", "Available tags:"))

        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(partial(self.search_str, project))

        hbox_top = QHBoxLayout()
        hbox_top.addWidget(self.label_tag_list)
        hbox_top.addStretch(1)
        hbox_top.addWidget(self.search_bar)

        # The list of tags
        self.list_widget_tags = QtWidgets.QListWidget(self)
        self.list_widget_tags.setObjectName("listWidget_tags")
        self.list_widget_tags.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox_top)
        vbox.addWidget(self.list_widget_tags)
        vbox.addLayout(hbox_buttons)

        self.setLayout(vbox)

        tags_lists = project.database.get_tags_names()
        tags_lists.remove("Checksum")
        for tag in tags_lists:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag))
        self.list_widget_tags.sortItems()

        self.setLayout(vbox)

        # Connecting the OK push button
        self.push_button_ok.clicked.connect(lambda: self.ok_action(project))

    def search_str(self, project, str_search):
        _translate = QtCore.QCoreApplication.translate
        return_list = []
        tags_lists = project.database.get_tags_names()
        tags_lists.remove("Checksum")
        if str_search != "":
            for tag in tags_lists:
                if str_search.upper() in tag.upper():
                    return_list.append(tag)
        else:
            for tag in tags_lists:
                return_list.append(tag)

        self.list_widget_tags.clear()
        for tag_name in return_list:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag_name))
        self.list_widget_tags.sortItems()

    def ok_action(self, project):
        name_already_exists = False
        for tag in project.database.get_tags():
            if tag.name == self.line_edit_new_tag_name.text():
                name_already_exists = True
        if name_already_exists:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("This tag name already exists")
            msg.setInformativeText("Please select another tag name")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
        elif self.line_edit_new_tag_name.text() == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("The tag name can't be empty")
            msg.setInformativeText("Please select a tag name")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
        elif len(self.list_widget_tags.selectedItems()) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("The tag to clone must be selected")
            msg.setInformativeText("Please select a tag to clone")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
        else:
            self.accept()
            self.close()

    def get_values(self):
        self.tag_to_replace = self.list_widget_tags.selectedItems()[0].text()
        self.new_tag_name = self.line_edit_new_tag_name.text()
        return self.tag_to_replace, self.new_tag_name