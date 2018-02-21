from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout

from functools import partial



class Ui_Visualized_Tags(QWidget):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.retranslate_Ui(project)

    def retranslate_Ui(self, project):
        _translate = QtCore.QCoreApplication.translate

        # Two buttons to select or unselect tags
        self.push_button_select_tag = QtWidgets.QPushButton(self)
        self.push_button_select_tag.setObjectName("pushButton_select_tag")
        self.push_button_select_tag.clicked.connect(self.click_select_tag)

        self.push_button_unselect_tag = QtWidgets.QPushButton(self)
        self.push_button_unselect_tag.setObjectName("pushButton_unselect_tag")
        self.push_button_unselect_tag.clicked.connect(self.click_unselect_tag)

        self.push_button_select_tag.setText(_translate("MainWindow", "-->"))
        self.push_button_unselect_tag.setText(_translate("MainWindow", "<--"))

        vbox_tag_buttons = QVBoxLayout()
        vbox_tag_buttons.addWidget(self.push_button_select_tag)
        vbox_tag_buttons.addWidget(self.push_button_unselect_tag)

        # The "Tag list" label
        self.label_tag_list = QtWidgets.QLabel(self)
        self.label_tag_list.setTextFormat(QtCore.Qt.AutoText)
        self.label_tag_list.setObjectName("label_tag_list")
        self.label_tag_list.setText(_translate("MainWindow", "Available tags:"))

        # The search bar to search in the list of tags
        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(partial(self.search_str, project))

        # The list of tags
        self.list_widget_tags = QtWidgets.QListWidget(self)
        self.list_widget_tags.setObjectName("listWidget_tags")
        self.list_widget_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        hbox_top_left = QHBoxLayout()
        hbox_top_left.addWidget(self.label_tag_list)
        hbox_top_left.addWidget(self.search_bar)

        vbox_top_left = QVBoxLayout()
        vbox_top_left.addLayout(hbox_top_left)
        vbox_top_left.addWidget(self.list_widget_tags)

        # List of the tags selected by the user
        self.list_widget_selected_tags = QtWidgets.QListWidget(self)
        self.list_widget_selected_tags.setObjectName("listWidget_visualized_tags")
        self.list_widget_selected_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        hbox_tags = QHBoxLayout()
        hbox_tags.addLayout(vbox_top_left)
        hbox_tags.addLayout(vbox_tag_buttons)
        hbox_tags.addWidget(self.list_widget_selected_tags)

        self.setLayout(hbox_tags)

        for tag_name in project.tags_to_visualize:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_selected_tags.addItem(item)
            item.setText(tag_name)

        for tag_name in project.getAllTagsNames():
            item = QtWidgets.QListWidgetItem()
            if tag_name not in project.tags_to_visualize:
                self.list_widget_tags.addItem(item)
                item.setText(tag_name)

    def search_str(self, project, str_search):
        return_list = []
        if str_search != "":
            for tag_name in project.getAllTagsNames():
                if str_search.upper() in tag_name.upper():
                    if tag_name not in project.tags_to_visualize:
                        return_list.append(tag_name)
        else:
            for tag_name in project.getAllTagsNames():
                if tag_name not in project.tags_to_visualize:
                    return_list.append(tag_name)
        self.list_widget_tags.clear()
        for tag_name in return_list:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(tag_name)

    def click_select_tag(self):
        # Put the selected tags in the "selected tag" table
        rows = sorted([index.row() for index in self.list_widget_tags.selectedIndexes()],
                      reverse=True)
        for row in rows:
            # assuming the other listWidget is called listWidget_2
            self.list_widget_selected_tags.addItem(self.list_widget_tags.takeItem(row))

    def click_unselect_tag(self):
        # Remove the unselected tags from the "selected tag" table
        rows = sorted([index.row() for index in self.list_widget_selected_tags.selectedIndexes()],
                      reverse=True)
        for row in rows:
            self.list_widget_tags.addItem(self.list_widget_selected_tags.takeItem(row))
