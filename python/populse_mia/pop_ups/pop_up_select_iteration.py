##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QCheckBox, QLabel
from PyQt5.QtCore import Qt


class PopUpSelectIteration(QDialog):
    """
    Is called when the user wants to run an iterated pipeline

    Attributes:
        - iterated_tag: name of the iterated tag
        - tag_values: values that can take the iterated tag
        - final_values: selected values on which to iterate the pipeline

    Methods:
        - ok_clicked: sends the selected values to the pipeline manager
    """

    def __init__(self, iterated_tag, tag_values):
        super().__init__()

        self.iterated_tag = iterated_tag
        self.tag_values = tag_values
        self.final_values = []
        self.setWindowTitle("Iterate pipeline run over tag {0}".format(self.iterated_tag))

        self.v_box = QVBoxLayout()

        # Label
        self.label = QLabel("Select values to iterative over:")
        self.v_box.addWidget(self.label)

        self.check_boxes = []
        for tag_value in self.tag_values:
            check_box = QCheckBox(tag_value)
            check_box.setCheckState(Qt.Checked)
            self.check_boxes.append(check_box)
            self.v_box.addWidget(check_box)

        self.h_box_bottom = QHBoxLayout()
        self.h_box_bottom.addStretch(1)

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton("OK")
        self.push_button_ok.setObjectName("pushButton_ok")
        self.push_button_ok.clicked.connect(self.ok_clicked)
        self.h_box_bottom.addWidget(self.push_button_ok)

        # The 'Cancel' push button
        self.push_button_cancel = QtWidgets.QPushButton("Cancel")
        self.push_button_cancel.setObjectName("pushButton_cancel")
        self.push_button_cancel.clicked.connect(self.close)
        self.h_box_bottom.addWidget(self.push_button_cancel)

        self.final_layout = QVBoxLayout()
        self.final_layout.addLayout(self.v_box)
        self.final_layout.addLayout(self.h_box_bottom)
        self.setLayout(self.final_layout)

    def ok_clicked(self):
        """
        Sends the selected values to the pipeline manager
        """
        final_values = []
        for check_box in self.check_boxes:
            if check_box.isChecked():
                final_values.append(check_box.text())

        self.final_values = final_values

        self.accept()
        self.close()
