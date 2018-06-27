from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QCheckBox, QComboBox, QVBoxLayout, QHBoxLayout, QDialog, QLabel, QLineEdit, QPushButton, \
    QFileDialog, QMessageBox
from functools import partial

from SoftwareProperties.Config import Config

import os

class Ui_Dialog_Preferences(QDialog):
    """
    Is called when the user wants to change the software preferences
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()

    def __init__(self, main):
        super().__init__()
        self.pop_up(main)

    def pop_up(self, main):
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
        self.appearance_layout.addStretch(1)
        self.tab_appearance.setLayout(self.appearance_layout)

        # The 'Tools" tab
        self.tab_tools = QtWidgets.QWidget()
        self.tab_tools.setObjectName("tab_tools")
        self.tab_widget.addTab(self.tab_tools, _translate("Dialog", "Tools"))

        self.labels_layout = QVBoxLayout()
        self.values_layout = QVBoxLayout()
        self.global_layout = QHBoxLayout()

        self.save_label = QLabel("Auto_save ")
        self.labels_layout.addWidget(self.save_label)
        self.save_checkbox = QCheckBox('', self)
        if config.isAutoSave() == "yes":
            self.save_checkbox.setChecked(1)
        self.values_layout.addWidget(self.save_checkbox)

        self.matlab_label = QLabel("MCR (MatLab Compiler Runtime) path ")
        self.matlab_choice = QLineEdit(config.get_matlab_path())
        self.matlab_browse = QPushButton("Browse")
        self.matlab_browse.clicked.connect(self.browse_matlab)

        self.spm_label = QLabel("SPM standalone path ")
        self.spm_choice = QLineEdit(config.get_spm_path())
        self.spm_browse = QPushButton("Browse")
        self.spm_browse.clicked.connect(self.browse_spm)

        self.use_spm_label = QLabel("Use SPM standalone for the pipelines")
        self.labels_layout.addWidget(self.use_spm_label)
        self.use_spm_checkbox = QCheckBox('', self)
        self.use_spm_checkbox.stateChanged.connect(self.use_spm_changed)
        if config.get_use_spm() == "yes":
            self.use_spm_checkbox.setChecked(1)
        else:
            self.use_spm_checkbox.setChecked(1)
            self.use_spm_checkbox.setChecked(0)
        self.values_layout.addWidget(self.use_spm_checkbox)

        self.labels_layout.addWidget(self.matlab_label)
        self.matlab_value_layout = QHBoxLayout()
        self.matlab_value_layout.addWidget(self.matlab_choice)
        self.matlab_value_layout.addWidget(self.matlab_browse)
        self.values_layout.addLayout(self.matlab_value_layout)

        self.labels_layout.addWidget(self.spm_label)
        self.spm_value_layout = QHBoxLayout()
        self.spm_value_layout.addWidget(self.spm_choice)
        self.spm_value_layout.addWidget(self.spm_browse)
        self.values_layout.addLayout(self.spm_value_layout)

        self.labels_layout.addStretch(1)
        self.values_layout.addStretch(1)
        self.global_layout.addLayout(self.labels_layout)
        self.global_layout.addLayout(self.values_layout)
        self.tab_tools.setLayout(self.global_layout)

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(partial(self.ok_clicked, main))

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

    def use_spm_changed(self):
        """
        Called when the use_spm checkbox is changed
        """

        if not self.use_spm_checkbox.isChecked():
            self.matlab_choice.setDisabled(True)
            self.spm_choice.setDisabled(True)
            self.matlab_label.setDisabled(True)
            self.spm_label.setDisabled(True)
            self.spm_browse.setDisabled(True)
            self.matlab_browse.setDisabled(True)
        else:
            self.matlab_choice.setDisabled(False)
            self.spm_choice.setDisabled(False)
            self.matlab_label.setDisabled(False)
            self.spm_label.setDisabled(False)
            self.spm_browse.setDisabled(False)
            self.matlab_browse.setDisabled(False)

    def browse_matlab(self):
        """
        Called when matlab browse button is clicked
        """

        fname = QFileDialog.getExistingDirectory(self, 'Choose MRC directory', '/home')
        if fname:
            self.matlab_choice.setText(fname)

    def browse_spm(self):
        """
        Called when spm browse button is clicked
        """

        fname = QFileDialog.getExistingDirectory(self, 'Choose SPM standalone directory', '/home')
        if fname:
            self.spm_choice.setText(fname)

    def ok_clicked(self, main):
        config = Config()

        # Auto-save
        if self.save_checkbox.isChecked():
            config.setAutoSave("yes")
        else:
            config.setAutoSave("no")

        # Use SPM
        if self.use_spm_checkbox.isChecked():
            config.set_use_spm("yes")
        else:
            config.set_use_spm("no")

        # SPM and MCR paths checks and update
        matlab_input = self.matlab_choice.text()
        spm_input = self.spm_choice.text()
        if os.path.exists(matlab_input) and "MATLAB/MATLAB_Runtime/v93" in matlab_input:
            config.set_matlab_path(matlab_input)
        else:
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("Invalid MCR path")
            self.msg.setInformativeText("The MCR path entered {0} is invalid.".format(matlab_input))
            self.msg.setWindowTitle("Error")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()
            return
        if os.path.exists(spm_input) and "spm12" in spm_input:
            config.set_spm_path(spm_input)
        else:
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("Invalid SPM standalone path")
            self.msg.setInformativeText("The SPM standalone path entered {0} is invalid.".format(spm_input))
            self.msg.setWindowTitle("Error")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()
            return

        #Colors
        background_color = self.background_color_combo.currentText()
        text_color = self.text_color_combo.currentText()
        config.setBackgroundColor(background_color)
        config.setTextColor(text_color)
        main.setStyleSheet("background-color:" + background_color + ";color:" + text_color + ";")

        self.signal_preferences_change.emit()
        self.accept()
        self.close()