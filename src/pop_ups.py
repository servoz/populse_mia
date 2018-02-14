from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QDialog, QPushButton, QLabel, \
    QMessageBox
import os
from functools import partial
import controller

class Ui_Dialog_New_Project(QFileDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.setOption(QFileDialog.DontUseNativeDialog)
        self.setLabelText(QFileDialog.Accept, "Create")
        self.setAcceptMode(QFileDialog.AcceptSave)
        #self.setFileMode(QFileDialog.Directory)
        # # Setting the Home directory as default
        if not(os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects'))):
            os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects'))
        self.setDirectory(os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects')))
        #self.finished.connect(self.return_value)

    #def return_value(self):
    def retranslateUi(self, file_name):
        # file_name = self.selectedFiles()
        file_name = file_name[0]
        if file_name:
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            #self.path = entire_path
            self.relative_path = os.path.relpath(file_name)
            self.relative_subpath = os.path.relpath(self.path)

            if not os.path.exists(self.relative_path):
                controller.createProject(self.name, self.relative_subpath, self.relative_subpath)
                self.close()
                # A signal is emitted to tell that the project has been created
                self.signal_create_project.emit()
            else:
                _translate = QtCore.QCoreApplication.translate
                self.dialog_box = QDialog()
                self.label = QLabel(self.dialog_box)
                self.label.setText(_translate("MainWindow", 'This name already exists in this parent folder'))
                self.push_button_ok = QPushButton(self.dialog_box)
                self.push_button_ok.setText('OK')
                self.push_button_ok.clicked.connect(self.dialog_box.close)
                hbox = QHBoxLayout()
                hbox.addWidget(self.label)
                hbox.addWidget(self.push_button_ok)

                self.dialog_box.setLayout(hbox)

        return file_name


class Ui_Dialog_Open_Project(QFileDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()

        #self.setLabelText(QFileDialog.Accept, "Open")
        self.setOption(QFileDialog.DontUseNativeDialog, True)
        self.setFileMode(QFileDialog.Directory)
        #self.setOption(QFileDialog.ShowDirsOnly)
        # # Setting the Home directory as default
        if not(os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects'))):
            os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects'))
        self.setDirectory(os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects')))
        # self.setDirectory(os.path.expanduser("~"))
        #self.retranslateUi()

    def retranslateUi(self, file_name):
        #file_name = self.getExistingDirectory(self, "Select a project directory")
        file_name = file_name[0]
        if file_name:
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            #self.path = entire_path
            self.relative_path = os.path.relpath(file_name)

            # If the file exists
            if os.path.exists(os.path.join(self.relative_path, self.name, self.name + '.json')):
                controller.open_project(self.name, self.relative_path)
                self.close()
                # A signal is emitted to tell that the project has been created
                self.signal_create_project.emit()
            else:
                _translate = QtCore.QCoreApplication.translate
                self.dialog_box = QDialog()
                self.label = QLabel(self.dialog_box)
                self.label.setText(_translate("MainWindow", 'This name already exists in this parent folder'))
                self.push_button_ok = QPushButton(self.dialog_box)
                self.push_button_ok.setText('OK')
                self.push_button_ok.clicked.connect(self.dialog_box.close)
                hbox = QHBoxLayout()
                hbox.addWidget(self.label)
                hbox.addWidget(self.push_button_ok)

                self.dialog_box.setLayout(hbox)

class Ui_Dialog_add_tag(QDialog):
    """
    Is called when the user wants to add a tag to the project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_add_tag = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.type = str
        self.pop_up(project)

    def pop_up(self, project):
        self.setObjectName("Add a tag")

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton(self)
        self.push_button_ok.setObjectName("push_button_ok")

        # The 'Tag name' label
        self.label_tag_name = QtWidgets.QLabel(self)
        self.label_tag_name.setTextFormat(QtCore.Qt.AutoText)
        self.label_tag_name.setObjectName("tag_name")

        # The 'Tag name' text edit
        self.text_edit_tag_name = QtWidgets.QLineEdit(self)
        self.text_edit_tag_name.setObjectName("textEdit_tag_name")

        # The 'Default value' label
        self.label_default_value = QtWidgets.QLabel(self)
        self.label_default_value.setTextFormat(QtCore.Qt.AutoText)
        self.label_default_value.setObjectName("default_value")

        # The 'Default value' text edit
        self.text_edit_default_value = QtWidgets.QLineEdit(self)
        self.text_edit_default_value.setObjectName("textEdit_default_value")

        # The 'Default value' label
        self.label_type = QtWidgets.QLabel(self)
        self.label_type.setTextFormat(QtCore.Qt.AutoText)
        self.label_type.setObjectName("type")

        # The 'Default value' text edit
        self.combo_box_type = QtWidgets.QComboBox(self)
        self.combo_box_type.setObjectName("combo_box_type")
        self.combo_box_type.addItem("String")
        self.combo_box_type.addItem("Integer")
        self.combo_box_type.addItem("Float")
        self.combo_box_type.addItem("List")
        self.combo_box_type.activated[str].connect(self.on_activated)

        # The status bar
        self.info_label = QtWidgets.QLabel(self)
        self.info_label.setStyleSheet('QLabel{font-size:10pt;font:italic;}')
        """self.hbox = QHBoxLayout(self)
        self.hbox.addWidget(self.status_bar)"""

        # Layouts
        v_box_labels = QVBoxLayout()
        v_box_labels.addWidget(self.label_tag_name)
        v_box_labels.addWidget(self.label_default_value)
        v_box_labels.addWidget(self.label_type)

        v_box_edits = QVBoxLayout()
        v_box_edits.addWidget(self.text_edit_tag_name)
        v_box_edits.addWidget(self.text_edit_default_value)
        v_box_edits.addWidget(self.combo_box_type)

        h_box_top = QHBoxLayout()
        h_box_top.addLayout(v_box_labels)
        h_box_top.addSpacing(50)
        h_box_top.addLayout(v_box_edits)

        h_box_ok = QHBoxLayout()
        h_box_ok.addStretch(1)
        h_box_ok.addWidget(self.push_button_ok)

        v_box_total = QVBoxLayout()
        v_box_total.addLayout(h_box_top)
        v_box_total.addLayout(h_box_ok)
        v_box_total.addWidget(self.info_label)

        self.setLayout(v_box_total)

        # Filling the title of the labels and push buttons
        _translate = QtCore.QCoreApplication.translate
        self.push_button_ok.setText(_translate("Add a tag", "OK"))
        self.label_tag_name.setText(_translate("Add a tag", "Tag name:"))
        self.label_default_value.setText(_translate("Add a tag", "Default value:"))
        self.label_type.setText(_translate("Add a tag", "Tag type:"))

        # Connecting the OK push button
        self.push_button_ok.clicked.connect(lambda: self.ok_action(project))

    def on_activated(self, text):
        if text == "String":
            self.type = str
            self.info_label.setText('')
        elif text == "Integer":
            self.type = int
            self.info_label.setText('')
        elif text == "Float":
            self.type = float
            self.info_label.setText('')
        else:
            self.type = list
            self.info_label.setText('Please seperate each list item by a comma. No need to use brackets.')

    def ok_action(self, project):
        name_already_exists = False
        for tag_name in project.getAllTagsNames():
            if tag_name == self.text_edit_tag_name.text():
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
        else:
            self.accept()
            self.close()

    def get_values(self):
        self.new_tag_name = self.text_edit_tag_name.text()
        self.new_default_value = self.text_edit_default_value.text()
        return self.new_tag_name, self.new_default_value, self.type


class Ui_Dialog_clone_tag(QDialog):
    """
    Is called when the user wants to clone a tag to the project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_clone_tag = pyqtSignal()

    def __init__(self, project):
        super().__init__()
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

        for tag_name in project.getAllTagsNames():
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag_name))

        self.setLayout(vbox)

        # Connecting the OK push button
        self.push_button_ok.clicked.connect(lambda: self.ok_action(project))

    def search_str(self, project, str_search):
        _translate = QtCore.QCoreApplication.translate
        return_list = []
        if str_search != "":
            for tag_name in project.getAllTagsNames():
                if str_search.upper() in tag_name.upper():
                    return_list.append(tag_name)
        else:
            return_list = project.getAllTagsNames()

        self.list_widget_tags.clear()
        for tag_name in return_list:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag_name))

    def ok_action(self, project):
        name_already_exists = False
        for tag_name in project.getAllTagsNames():
            if tag_name == self.line_edit_new_tag_name.text():
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
        else:
            self.accept()
            self.close()

    def get_values(self):
        self.tag_to_replace = self.list_widget_tags.selectedItems()[0].text()
        self.new_tag_name = self.line_edit_new_tag_name.text()
        return self.tag_to_replace, self.new_tag_name


class Ui_Dialog_remove_tag(QDialog):
    """
     Is called when the user wants to remove a user tag to the project
     """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_remove_tag = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.project = project
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

        for tag in self.project.user_tags:
            tag_name = tag['name']
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            item.setText(_translate("Dialog", tag_name))

        self.setLayout(vbox)

        # Connecting the OK push button
        self.push_button_ok.clicked.connect(self.ok_action)

    def search_str(self, str_search):
        _translate = QtCore.QCoreApplication.translate

        if str_search != "":
            return_list = []
            for tag in self.project.user_tags:
                tag_name = tag['name']
                if str_search.upper() in tag_name.upper():
                    return_list.append(tag_name)
        else:
            return_list = []
            for tag in self.project.user_tags:
                tag_name = tag['name']
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
                if tag_name not in project.tags_to_visualize():
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


class Ui_Informations(QWidget):
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

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Property', 'Value'))

        item = QTableWidgetItem("Name")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem(project.name)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(0, 1, item)

        item = QTableWidgetItem("Folder")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem(project.folder)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(1, 1, item)

        item = QTableWidgetItem("Date of creation")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(2, 0, item)

        item = QTableWidgetItem(project.date)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(2, 1, item)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()

        box = QVBoxLayout()
        box.addWidget(self.tableWidget)

        self.setLayout(box)


class Ui_Dialog_Preferences(QDialog):
    """
    Is called when the user wants to change the software preferences
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.pop_up(project)

    def pop_up(self, project):
        _translate = QtCore.QCoreApplication.translate

        self.setObjectName("Dialog")
        self.setWindowTitle('MIA2 preferences')

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setEnabled(True)

        # The 'Appearance" tab
        self.tab_appearance = QtWidgets.QWidget()
        self.tab_appearance.setObjectName("tab_appearance")
        self.tab_widget.addTab(self.tab_appearance, _translate("Dialog", "Appearance"))

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, project))

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
        # Action to define
        self.accept()
        self.close()


class Ui_Dialog_Settings(QDialog):
    """
    Is called when the user wants to change the software settings
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_settings_change = pyqtSignal()

    def __init__(self, project):
        super().__init__()
        self.pop_up(project)

    def pop_up(self, project):
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
        self.tab_infos = Ui_Informations(project)
        self.tab_infos.setObjectName("tab_infos")
        self.tab_widget.addTab(self.tab_infos, _translate("Dialog", "Informations"))

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, project))

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
        project.tags_to_visualize = []
        for x in range(self.tab_tags.list_widget_selected_tags.count()):
            project.tags_to_visualize.append(self.tab_tags.list_widget_selected_tags.item(x).text())
        self.accept()
        self.close()


class Ui_Dialog_Save_Project_As(QFileDialog):
    """
    Is called when the user wants to save a project under another name
    """

    # Signal that will be emitted at the end to tell that the new file name has been chosen
    signal_saved_project = pyqtSignal()

    def __init__(self):
        super().__init__()
        #self.setOption(QFileDialog.DontUseNativeDialog)
        self.setLabelText(QFileDialog.Accept, "Save as")
        self.setOption(QFileDialog.ShowDirsOnly, True)
        self.setAcceptMode(QFileDialog.AcceptSave)
        #self.setFileMode(QFileDialog.Directory)
        # # Setting the Home directory as default
        if not(os.path.exists(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects'))):
            os.makedirs(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects'))
        self.setDirectory(os.path.expanduser(os.path.join(os.path.join(os.path.relpath(os.curdir), '..'), 'projects')))
        # self.setDirectory(os.path.expanduser("~"))
        self.finished.connect(self.return_value)

    def return_value(self):
        file_name = self.selectedFiles()
        file_name = file_name[0]
        if file_name:
            entire_path = os.path.abspath(file_name)
            self.path, self.name = os.path.split(entire_path)
            self.total_path = entire_path
            self.relative_path = os.path.relpath(file_name)
            self.relative_subpath = os.path.relpath(self.path)

            if not os.path.exists(self.relative_path):
                controller.createProject(self.name, '~', self.relative_subpath)
                self.close()
                # A signal is emitted to tell that the project has been created
                self.signal_saved_project.emit()
            else:
                _translate = QtCore.QCoreApplication.translate
                self.dialog_box = QDialog()
                self.label = QLabel(self.dialog_box)
                self.label.setText(_translate("MainWindow", 'This name already exists in this parent folder'))
                self.push_button_ok = QPushButton(self.dialog_box)
                self.push_button_ok.setText('OK')
                self.push_button_ok.clicked.connect(self.dialog_box.close)
                hbox = QHBoxLayout()
                hbox.addWidget(self.label)
                hbox.addWidget(self.push_button_ok)

                self.dialog_box.setLayout(hbox)

        return file_name

class Ui_Dialog_Type_Problem(QDialog):
    """
    Is called when the user changes a value that is not in the right type
    """
    ok_signal = pyqtSignal()

    def __init__(self, tp):
        super().__init__()

        tp_str = str(tp)
        self.setWindowTitle("Type error")

        label = QLabel(self)
        label.setText('This value should be of type ' + tp_str[8:-2])

        push_button_ok = QPushButton("OK", self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(push_button_ok)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        push_button_ok.clicked.connect(self.ok_clicked)

    def ok_clicked(self):
        self.ok_signal.emit()
        self.close()



class Ui_Dialog_Quit(QDialog):
    """
    Is called when the user changes a value that is not in the right type
    """
    save_as_signal = pyqtSignal()
    do_not_save_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self, project):
        super().__init__()

        self.project = project
        self.bool_exit = False

        self.setWindowTitle("Confirm exit")

        label = QLabel(self)
        label.setText('Do you want to exit without saving ' + project.name + '?')

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
        self.save_as_signal.emit()
        self.bool_exit = True
        self.close()

    def do_not_save_clicked(self):
        self.bool_exit = True
        self.close()

    def cancel_clicked(self):
        self.bool_exit = False
        self.close()

    def can_exit(self):
        return self.bool_exit