from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QTableWidget, QFrame, \
    QVBoxLayout, QMessageBox, QHeaderView
from PyQt5.QtGui import QIcon, QPixmap
import os
from ProjectManager import controller
from DataBase.DataBase import DataBase
from PopUps.Ui_Select_Tag_Count_Table import Ui_Select_Tag_Count_Table
from Utils.Tools import ClickableLabel

from functools import reduce # Valid in Python 2.6+, required in Python 3
import operator


class CountTable(QDialog):
    """
    Is called when the user wants to verify precisely the scans of the project.
    """

    def __init__(self, database=None):
        super().__init__()

        self.database = database
        self.values_list = [[], []]

        self.frame_back = QFrame()

        self.label_tags = QLabel('Tags: ')

        push_button_tag_1 = QPushButton()
        push_button_tag_1.setText("Tag n°1")
        push_button_tag_1.clicked.connect(lambda: self.select_tag(0))

        push_button_tag_2 = QPushButton()
        push_button_tag_2.setText("Tag n°2")
        push_button_tag_2.clicked.connect(lambda: self.select_tag(1))

        self.tag_labels = []
        self.tag_labels.insert(0, push_button_tag_1)
        self.tag_labels.insert(1, push_button_tag_2)

        self.remove_tag_label = ClickableLabel()
        remove_tag_picture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        remove_tag_picture = remove_tag_picture.scaledToHeight(20)
        self.remove_tag_label.setPixmap(remove_tag_picture)
        self.remove_tag_label.clicked.connect(self.remove_tag)

        self.add_tag_label = ClickableLabel()
        self.add_tag_label.setObjectName('plus')
        add_tag_picture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        add_tag_picture = add_tag_picture.scaledToHeight(15)
        self.add_tag_label.setPixmap(add_tag_picture)
        self.add_tag_label.clicked.connect(self.add_tag)

        self.push_button_count = QPushButton()
        self.push_button_count.setText('Count scans')
        self.push_button_count.clicked.connect(self.count_scans)

        self.table = QTableWidget()

        self.v_box_final = QVBoxLayout()
        self.setLayout(self.v_box_final)
        self.refresh_layout()

    def refresh_layout(self):
        self.h_box_top = QHBoxLayout()
        self.h_box_top.setSpacing(10)
        self.h_box_top.addWidget(self.label_tags)

        for tag_label in self.tag_labels:
            self.h_box_top.addWidget(tag_label)

        self.h_box_top.addWidget(self.add_tag_label)
        self.h_box_top.addWidget(self.remove_tag_label)
        self.h_box_top.addWidget(self.push_button_count)
        self.h_box_top.addStretch(1)

        self.v_box_final.addLayout(self.h_box_top)
        self.v_box_final.addWidget(self.table)

    def add_tag(self):
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.tag_labels) + 1))
        push_button.clicked.connect(lambda: len(self.tag_labels))
        self.tag_labels.insert(len(self.tag_labels), push_button)
        self.refresh_layout()

    def remove_tag(self):
        push_button = self.tag_labels[-1]
        push_button.deleteLater()
        push_button = None
        del self.tag_labels[-1]
        del self.values_list[-1]
        self.refresh_layout()

    def select_tag(self, idx):
        popUp = Ui_Select_Tag_Count_Table(self.database, self.tag_labels[idx].text())
        if popUp.exec_() == QDialog.Accepted:
            self.tag_labels[idx].setText(popUp.selected_tag)
            self.fill_values(idx)

    def fill_values(self, idx):
        tag_name = self.tag_labels[idx].text()
        values = self.database.getValuesGivenTag(tag_name)
        if len(self.values_list) < idx:
            self.values_list.insert(idx, [])
        for value in values:
            if value.current_value not in self.values_list[idx]:
                self.values_list[idx].append(value.current_value)

    def count_scans(self):
        self.nb_values = []
        for values in self.values_list:
            self.nb_values.append(len(values))

        nb_row = reduce(operator.mul, self.nb_values[:-1], 1)
        nb_col = len(self.values_list) - 1 + self.nb_values[-1]

        self.table.setRowCount(nb_row)
        self.table.setColumnCount(nb_col)


        #header_name = self.tag_labels[idx].text()
        pass