from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QCheckBox, QMenu, QComboBox, QListWidget, QInputDialog, QLineEdit, QVBoxLayout, \
    QHBoxLayout, QDialog,  QLabel
from functools import partial
from SoftwareProperties.Config import Config


class Ui_Dialog_Preferences(QDialog):
    """
    Is called when the user wants to change the software preferences
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()

    def __init__(self, project, main):
        super().__init__()
        self.pop_up(project, main)

    def pop_up(self, project, main):
        _translate = QtCore.QCoreApplication.translate

        self.setObjectName("Dialog")
        self.setWindowTitle('MIA2 preferences')

        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.setEnabled(True)

        # The 'Appearance" tab
        self.tab_appearance = QtWidgets.QWidget()
        self.tab_appearance.setObjectName("tab_appearance")
        self.tab_widget.addTab(self.tab_appearance, _translate("Dialog", "Appearance"))

        config = Config()

        self.appearance_layout = QVBoxLayout()
        self.appearance_layout.addStretch(1)
        self.label_background_color = QLabel("Background color")
        self.background_color_combo = QComboBox(self)
        self.background_color_combo.addItem("")
        self.background_color_combo.addItem("Black")
        self.background_color_combo.addItem("Blue")
        self.background_color_combo.addItem("Green")
        self.background_color_combo.addItem("Grey")
        self.background_color_combo.addItem("Orange")
        self.background_color_combo.addItem("Red")
        self.background_color_combo.addItem("Yellow")
        self.background_color_combo.addItem("White")
        background_color = config.getBackgroundColor()
        self.background_color_combo.setCurrentText(background_color)
        self.label_text_color = QLabel("Text color")
        self.text_color_combo = QComboBox(self)
        self.text_color_combo.addItem("")
        self.text_color_combo.addItem("Black")
        self.text_color_combo.addItem("Blue")
        self.text_color_combo.addItem("Green")
        self.text_color_combo.addItem("Grey")
        self.text_color_combo.addItem("Orange")
        self.text_color_combo.addItem("Red")
        self.text_color_combo.addItem("Yellow")
        self.text_color_combo.addItem("White")
        text_color = config.getTextColor()
        self.text_color_combo.setCurrentText(text_color)
        self.appearance_layout.addWidget(self.label_background_color)
        self.appearance_layout.addWidget(self.background_color_combo)
        self.appearance_layout.addWidget(self.label_text_color)
        self.appearance_layout.addWidget(self.text_color_combo)
        self.tab_appearance.setLayout(self.appearance_layout)

        # The 'Tools" tab
        self.tab_tools = QtWidgets.QWidget()
        self.tab_tools.setObjectName("tab_tools")
        self.tab_widget.addTab(self.tab_tools, _translate("Dialog", "Tools"))

        self.tools_layout = QVBoxLayout()
        self.save_checkbox = QCheckBox('Auto Save (only on saved projects, does not work on default unnamed project)', self)

        if(config.isAutoSave() == "yes"):
            self.save_checkbox.setChecked(1)
        self.tools_layout.addWidget(self.save_checkbox)
        self.label_default_tags = QLabel("Default tags visualized")
        self.list_default_tags = QListWidget()
        self.default_tags = config.getDefaultTags()
        self.list_default_tags.addItems(self.default_tags)
        self.list_default_tags.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.handleItemClicked, self.list_default_tags))
        self.list_default_tags.customContextMenuRequested.connect(partial(self.handleItemClicked, project))
        self.tools_layout.addWidget(self.label_default_tags)
        self.tools_layout.addWidget(self.list_default_tags)
        self.tab_tools.setLayout(self.tools_layout)

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, project, main))

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

    def ok_clicked(self, project, main):
        config = Config()
        if self.save_checkbox.isChecked():
            config.setAutoSave("yes")
        else:
            config.setAutoSave("no")
        background_color = self.background_color_combo.currentText()
        text_color = self.text_color_combo.currentText()
        config.setBackgroundColor(background_color)
        config.setTextColor(text_color)
        main.setStyleSheet("background-color:" + background_color + ";color:" + text_color + ";")
        self.accept()
        self.close()

    def handleItemClicked(self, project, pos):
        menu = QMenu(self)
        actionRemoveTag = menu.addAction("Remove tag")
        actionAddTag = menu.addAction("Add a new tag")
        # Show the context menu.
        action = menu.exec_(self.list_default_tags.mapToGlobal(pos))
        if action == actionRemoveTag:
            tag = self.list_default_tags.currentItem().text()
            config = Config()
            config.removeDefaultTag(tag)
            self.list_default_tags.clear()
            self.default_tags = config.getDefaultTags()
            self.list_default_tags.addItems(self.default_tags)
        elif action == actionAddTag:
            config = Config()
            res = self.getText()
            if not res == None:
                config.addDefaultTag(res)
                self.list_default_tags.clear()
                self.default_tags = config.getDefaultTags()
                self.list_default_tags.addItems(self.default_tags)
        project.refresh_tags()
    def getText(self):
        text, okPressed = QInputDialog.getText(self, "Add a new tag", "Tag name: ", QLineEdit.Normal, "")
        if okPressed and text != '':
            return text
