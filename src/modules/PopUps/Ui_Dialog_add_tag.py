from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QMessageBox


class Ui_Dialog_add_tag(QDialog):
    """
    Is called when the user wants to add a tag to the project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_add_tag = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.database = database
        self.type = str
        self.pop_up()

    def pop_up(self):
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

        # The 'Description value' label
        self.label_description_value = QtWidgets.QLabel(self)
        self.label_description_value.setTextFormat(QtCore.Qt.AutoText)
        self.label_description_value.setObjectName("description_value")

        # The 'Description value' text edit
        self.text_edit_description_value = QtWidgets.QLineEdit(self)
        self.text_edit_description_value.setObjectName("textEdit_description_value")

        # The 'Unit value' label
        self.label_unit_value = QtWidgets.QLabel(self)
        self.label_unit_value.setTextFormat(QtCore.Qt.AutoText)
        self.label_unit_value.setObjectName("unit_value")

        # The 'Unit value' text edit
        self.text_edit_unit_value = QtWidgets.QLineEdit(self)
        self.text_edit_unit_value.setObjectName("textEdit_unit_value")

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
        v_box_labels.addWidget(self.label_description_value)
        v_box_labels.addWidget(self.label_unit_value)
        v_box_labels.addWidget(self.label_type)

        v_box_edits = QVBoxLayout()
        v_box_edits.addWidget(self.text_edit_tag_name)
        v_box_edits.addWidget(self.text_edit_default_value)
        v_box_edits.addWidget(self.text_edit_description_value)
        v_box_edits.addWidget(self.text_edit_unit_value)
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
        self.label_description_value.setText(_translate("Add a tag", "Description:"))
        self.label_unit_value.setText(_translate("Add a tag", "Unit:"))
        self.label_type.setText(_translate("Add a tag", "Tag type:"))

        # Connecting the OK push button
        self.push_button_ok.clicked.connect(self.ok_action)

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

    def ok_action(self):
        name_already_exists = False
        for tag in self.database.getTags():
            if tag.tag == self.text_edit_tag_name.text():
                name_already_exists = True
        if (self.text_edit_tag_name.text() == ""):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("The tag name cannot be empty")
            msg.setInformativeText("Please enter a tag name")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
        elif name_already_exists:
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
        self.new_tag_description = self.text_edit_description_value.text()
        self.new_tag_unit = self.text_edit_unit_value.text()
        return self.new_tag_name, self.new_default_value, self.type, self.new_tag_description, self.new_tag_unit