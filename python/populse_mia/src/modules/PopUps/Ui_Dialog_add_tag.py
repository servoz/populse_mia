from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QMessageBox
from Utils.Tools import ClickableLabel
from Utils.Utils import check_value_type
import os
import ast
from datetime import datetime
from Project.database_mia import TAG_UNIT_MS, TAG_UNIT_MM, TAG_UNIT_HZPIXEL, TAG_UNIT_DEGREE, TAG_UNIT_MHZ
from Project.Project import COLLECTION_CURRENT
from populse_db.database import FIELD_TYPE_LIST_TIME, FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_DATE, \
    FIELD_TYPE_LIST_STRING, FIELD_TYPE_LIST_BOOLEAN, FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_INTEGER, LIST_TYPES, \
    FIELD_TYPE_STRING, FIELD_TYPE_INTEGER, FIELD_TYPE_FLOAT, FIELD_TYPE_BOOLEAN, FIELD_TYPE_TIME, FIELD_TYPE_DATETIME, \
    FIELD_TYPE_DATE


class Default_value_list_creation(QDialog):

    def __init__(self, parent, type):
        super().__init__()

        # Current type chosen
        self.type = type

        self.parent = parent

        # The table that will be filled
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(1)

        value = self.parent.text()

        if value != "":
            try:
                list_value = ast.literal_eval(value)
                if isinstance(list_value, list):

                    # If the previous value was already a list, we fill it

                    self.table.setColumnCount(len(list_value))

                    for i in range(0, self.table.columnCount()):
                        item = QtWidgets.QTableWidgetItem()
                        item.setText(str(list_value[i]))
                        self.table.setItem(0, i, item)

                else:
                    self.default_init_table()

            except Exception as e:
                self.default_init_table()
        else:
            self.default_init_table()

        self.resize_table()

        # Ok button
        ok_button = QtWidgets.QPushButton("Ok")
        ok_button.clicked.connect(self.update_default_value)

        # Cancel button
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        # Button to add an element to the list
        self.add_element_label = ClickableLabel()
        self.add_element_label.setObjectName('plus')
        add_element_picture = QtGui.QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        add_element_picture = add_element_picture.scaledToHeight(15)
        self.add_element_label.setPixmap(add_element_picture)
        self.add_element_label.clicked.connect(self.add_element)

        # Button to remove the last element of the list
        self.remove_element_label = ClickableLabel()
        self.remove_element_label.setObjectName('minus')
        remove_element_picture = QtGui.QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        remove_element_picture = remove_element_picture.scaledToHeight(20)
        self.remove_element_label.setPixmap(remove_element_picture)
        self.remove_element_label.clicked.connect(self.remove_element)

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.h_box_final = QHBoxLayout()
        self.list_layout = QHBoxLayout()

        self.h_box_final.addWidget(ok_button)
        self.h_box_final.addWidget(cancel_button)

        self.list_layout.addWidget(self.table)
        self.list_layout.addWidget(self.remove_element_label)
        self.list_layout.addWidget(self.add_element_label)

        self.v_box_final.addLayout(self.list_layout)
        self.v_box_final.addLayout(self.h_box_final)

        self.setLayout(self.v_box_final)

    def default_init_table(self):
        """
        Default init table when no previous value
        """

        # Table filled with a single element at the beginning if no value
        self.table.setColumnCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.table.setItem(0, 0, item)

    def update_default_value(self):

        database_value = []
        valid_values = True

        # For each value
        for i in range(0, self.table.columnCount()):
            item = self.table.item(0, i)
            text = item.text()

            try:
                if self.type == FIELD_TYPE_LIST_INTEGER:
                    database_value.append(int(text))
                elif self.type == FIELD_TYPE_LIST_FLOAT:
                    database_value.append(float(text))
                elif self.type == FIELD_TYPE_LIST_BOOLEAN:
                    if text == "True":
                        database_value.append(True)
                    elif text == "False":
                        database_value.append(False)
                    else:
                        raise ValueError("Not a boolean value")
                elif self.type == FIELD_TYPE_LIST_STRING:
                    database_value.append(str(text))
                elif self.type == FIELD_TYPE_LIST_DATE:
                    format = "%d/%m/%Y"
                    datetime.strptime(text, format).date()
                    database_value.append(text)
                elif self.type == FIELD_TYPE_LIST_DATETIME:
                    format = "%d/%m/%Y %H:%M:%S.%f"
                    datetime.strptime(text, format)
                    database_value.append(text)
                elif self.type == FIELD_TYPE_LIST_TIME:
                    format = "%H:%M:%S.%f"
                    datetime.strptime(text, format).time()
                    database_value.append(text)

            except Exception:
                # Error if invalid value
                valid_values = False
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Invalid value")
                msg.setInformativeText("The value " + text + " is invalid with the type " + self.type)
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()
                break

        if valid_values:
            self.parent.setText(str(database_value))
            self.close()

    def add_element(self):
        """
        One more element added to the list
        """
        self.table.setColumnCount(self.table.columnCount() + 1)
        item = QtWidgets.QTableWidgetItem()
        self.table.setItem(0, self.table.columnCount() - 1, item)
        self.resize_table()

    def remove_element(self):
        """
        Removes the last element of the list
        """
        if self.table.columnCount() > 1:
            self.table.setColumnCount(self.table.columnCount() - 1)
            self.resize_table()
            self.adjustSize()

    def resize_table(self):
        """
        To resize the pop up depending on the table
        """
        self.table.resizeColumnsToContents()
        total_width = 0
        total_height = 0
        i = 0
        while i < self.table.columnCount():
            total_width += self.table.columnWidth(i)
            total_height += self.table.rowHeight(i)
            i += 1
        if total_width + 20 < 900:
            self.table.setFixedWidth(total_width + 20)
            self.table.setFixedHeight(total_height + 25)
        else:
            self.table.setFixedWidth(900)
            self.table.setFixedHeight(total_height + 40)

class Default_Value_QLine_Edit(QtWidgets.QLineEdit):
    """
    Overrides the QLineEdit for the default value
    We need to override the MousePressEvent
    """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def mousePressEvent(self, event):
        """
        Mouse pressed on the QLineEdit
        :param event:
        """

        if self.parent.type in LIST_TYPES:
            # We display the pop up to create the list if the checkbox is checked, otherwise we do nothing
            self.list_creation = Default_value_list_creation(self, self.parent.type)
            self.list_creation.show()
            if self.list_creation.exec_():
                pass


class Ui_Dialog_add_tag(QDialog):
    """
    Is called when the user wants to add a tag to the project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_add_tag = pyqtSignal()

    def __init__(self, databrowser, project):
        super().__init__()
        self.project = project
        self.databrowser = databrowser
        self.type = FIELD_TYPE_STRING # Type is string by default
        self.pop_up()
        self.setMinimumWidth(700)
        self.setWindowTitle("Add a tag")

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
        self.text_edit_default_value = Default_Value_QLine_Edit(self)
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
        self.combo_box_unit = QtWidgets.QComboBox(self)
        self.combo_box_unit.setObjectName("combo_box_unit")
        self.combo_box_unit.addItem(None)
        self.combo_box_unit.addItem(TAG_UNIT_MS)
        self.combo_box_unit.addItem(TAG_UNIT_MM)
        self.combo_box_unit.addItem(TAG_UNIT_MHZ)
        self.combo_box_unit.addItem(TAG_UNIT_HZPIXEL)
        self.combo_box_unit.addItem(TAG_UNIT_DEGREE)

        # The 'Type' label
        self.label_type = QtWidgets.QLabel(self)
        self.label_type.setTextFormat(QtCore.Qt.AutoText)
        self.label_type.setObjectName("type")

        # The 'Type' text edit
        self.combo_box_type = QtWidgets.QComboBox(self)
        self.combo_box_type.setObjectName("combo_box_type")
        self.combo_box_type.addItem("String")
        self.combo_box_type.addItem("Integer")
        self.combo_box_type.addItem("Float")
        self.combo_box_type.addItem("Boolean")
        self.combo_box_type.addItem("Date")
        self.combo_box_type.addItem("Datetime")
        self.combo_box_type.addItem("Time")
        self.combo_box_type.addItem("String List")
        self.combo_box_type.addItem("Integer List")
        self.combo_box_type.addItem("Float List")
        self.combo_box_type.addItem("Boolean List")
        self.combo_box_type.addItem("Date List")
        self.combo_box_type.addItem("Datetime List")
        self.combo_box_type.addItem("Time List")
        self.combo_box_type.currentTextChanged.connect(self.on_activated)

        # Layouts
        v_box_labels = QVBoxLayout()
        v_box_labels.addWidget(self.label_tag_name)
        v_box_labels.addWidget(self.label_default_value)
        v_box_labels.addWidget(self.label_description_value)
        v_box_labels.addWidget(self.label_unit_value)
        v_box_labels.addWidget(self.label_type)

        v_box_edits = QVBoxLayout()
        v_box_edits.addWidget(self.text_edit_tag_name)
        default_layout = QHBoxLayout()
        default_layout.addWidget(self.text_edit_default_value)
        v_box_edits.addLayout(default_layout)
        v_box_edits.addWidget(self.text_edit_description_value)
        v_box_edits.addWidget(self.combo_box_unit)
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
        """
        Type updated
        :param text: New type
        """

        print("on activated")

        if text == "String":
            self.type = FIELD_TYPE_STRING
        elif text == "Integer":
            self.type = FIELD_TYPE_INTEGER
            self.text_edit_default_value.setPlaceholderText("Please enter an integer")
        elif text == "Float":
            self.type = FIELD_TYPE_FLOAT
            self.text_edit_default_value.setPlaceholderText("Please enter a float")
        elif text == "Boolean":
            self.type = FIELD_TYPE_BOOLEAN
            self.text_edit_default_value.setPlaceholderText("Please enter a boolean (True or False)")
        elif text == "Date":
            self.type = FIELD_TYPE_DATE
            self.text_edit_default_value.setPlaceholderText("Please enter a date in the following format: dd/mm/yyyy")
        elif text == "Datetime":
            self.type = FIELD_TYPE_DATETIME
            self.text_edit_default_value.setPlaceholderText("Please enter a datetime in the following format: dd/mm/yyyy hh:mm:ss.zzz")
        elif text == "Time":
            self.type = FIELD_TYPE_TIME
            self.text_edit_default_value.setPlaceholderText("Please enter a time in the following format: hh:mm:ss.zzz")
        elif text == "String List":
            self.type = FIELD_TYPE_LIST_STRING
        elif text == "Integer List":
            self.type = FIELD_TYPE_LIST_INTEGER
        elif text == "Float List":
            self.type = FIELD_TYPE_LIST_FLOAT
        elif text == "Boolean List":
            self.type = FIELD_TYPE_LIST_BOOLEAN
        elif text == "Date List":
            self.type = FIELD_TYPE_LIST_DATE
        elif text == "Datetime List":
            self.type = FIELD_TYPE_LIST_DATETIME
        elif text == "Time List":
            self.type = FIELD_TYPE_LIST_TIME

    def ok_action(self):

        # Tag name checked
        name_already_exists = False
        if self.text_edit_tag_name.text() in self.project.session.get_fields_names(COLLECTION_CURRENT):
            name_already_exists = True

        # Default value checked
        default_value = self.text_edit_default_value.text()
        wrong_default_value_type = not check_value_type(default_value, self.type, False)

        # Tag name can't be empty
        if self.text_edit_tag_name.text() == "":
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("The tag name cannot be empty")
            self.msg.setInformativeText("Please enter a tag name")
            self.msg.setWindowTitle("Error")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()

        # Tag name can't exist already
        elif name_already_exists:
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("This tag name already exists")
            self.msg.setInformativeText("Please select another tag name")
            self.msg.setWindowTitle("Error")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()

        # The default value must be valid
        elif wrong_default_value_type:
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("Invalid default value")
            self.msg.setInformativeText("The default value " + default_value + " is invalid with the type " + self.type + ".")
            self.msg.setWindowTitle("Error")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()

        # Ok
        else:
            self.accept()
            self.new_tag_name = self.text_edit_tag_name.text()
            self.new_default_value = self.text_edit_default_value.text()
            self.new_tag_description = self.text_edit_description_value.text()
            self.new_tag_unit = self.combo_box_unit.currentText()
            if self.new_tag_unit == '':
                self.new_tag_unit = None
            self.databrowser.add_tag_infos(self.new_tag_name, self.new_default_value, self.type, self.new_tag_description, self.new_tag_unit)
            self.close()