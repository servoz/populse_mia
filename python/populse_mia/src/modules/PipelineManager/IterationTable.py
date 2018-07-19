#!/usr/bin/python3

import datetime
import os
import sip
import sys
import uuid

from collections import OrderedDict

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QByteArray, Qt, QStringListModel, QLineF, QPointF, \
    QRectF, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QPixmap, QPainter, QPainterPath, \
    QCursor, QBrush, QIcon
from PyQt5.QtWidgets import QMenuBar, QMenu, qApp, QGraphicsScene, \
    QTextEdit, QGraphicsLineItem, QGraphicsRectItem, QTableWidgetItem, \
    QGraphicsEllipseItem, QDialog, QPushButton, QVBoxLayout, QWidget, \
    QSplitter, QApplication, QToolBar, QAction, QHBoxLayout, QCheckBox, QTableWidget, QComboBox, QLabel

from matplotlib.backends.qt_compat import QtWidgets
from traits.trait_errors import TraitError

from PipelineManager.Process_mia import Process_mia
from PopUps.Ui_Select_Tag_Count_Table import Ui_Select_Tag_Count_Table
from Project.Project import COLLECTION_CURRENT

from traits.api import TraitListObject, Undefined
from capsul.api import get_process_instance, StudyConfig, PipelineNode

from PipelineManager.callStudent import callStudent
from Project.Project import COLLECTION_CURRENT, COLLECTION_INITIAL, COLLECTION_BRICK, BRICK_NAME, BRICK_OUTPUTS, \
    BRICK_INPUTS, TAG_BRICKS, BRICK_INIT, BRICK_INIT_TIME, TAG_TYPE, TAG_EXP_TYPE, TAG_FILENAME, TAG_CHECKSUM, TYPE_NII, \
    TYPE_MAT
from SoftwareProperties.Config import Config
from .NodeController import NodeController
from .PipelineEditor import PipelineEditorTabs
from .process_library import ProcessLibraryWidget

from Utils.Tools import ClickableLabel


class IterationTable(QWidget):

    iteration_table_updated = pyqtSignal(list)

    def __init__(self, project, scan_list, main_window):
        QWidget.__init__(self)

        Process_mia.project = project
        self.project = project
        if not scan_list:
            self.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)
        else:
            self.scan_list = scan_list
        self.main_window = main_window
        self.iterated_tag = None

        # values_list will contain the different values of each selected tag
        self.values_list = [[], []]

        # Checkbox to choose to iterate or not
        self.check_box_iterate = QCheckBox("Iterate pipeline")
        self.check_box_iterate.stateChanged.connect(self.emit_iteration_table_updated)

        # Label "Iterate over:"
        self.label_iterate = QLabel("Iterative over:")

        # Label that displays the name of the selected tag
        self.iterated_tag_label = QLabel("Select a tag")

        # Push button to select the tag to iterate
        self.iterated_tag_push_button = QPushButton("Select")
        self.iterated_tag_push_button.clicked.connect(self.display_tags)

        # QComboBox
        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.update_table)

        # QTableWidget
        self.table = QTableWidget()

        # Label tag
        self.label_tags = QLabel("Tags to visualize:")

        # Each push button will allow the user to visualize a tag in the iteration browser
        push_button_tag_1 = QPushButton()
        push_button_tag_1.setText("SequenceName")
        push_button_tag_1.clicked.connect(lambda: self.select_tag(0))

        push_button_tag_2 = QPushButton()
        push_button_tag_2.setText("AcquisitionDate")
        push_button_tag_2.clicked.connect(lambda: self.select_tag(1))

        # The list of all the push buttons (the user can add as many as he or she wants)
        self.push_buttons = []
        self.push_buttons.insert(0, push_button_tag_1)
        self.push_buttons.insert(1, push_button_tag_2)

        # Labels to add/remove a tag (a push button)
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

        # Layout

        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.refresh_layout()

    def refresh_layout(self):
        """ Methods that update the layouts (especially when a tag push button
        is added or removed. """

        first_v_layout = QVBoxLayout()
        first_v_layout.addWidget(self.check_box_iterate)

        second_v_layout = QVBoxLayout()
        second_v_layout.addWidget(self.label_iterate)
        second_v_layout.addWidget(self.iterated_tag_label)

        third_v_layout = QVBoxLayout()
        third_v_layout.addWidget(self.iterated_tag_push_button)
        third_v_layout.addWidget(self.combo_box)

        top_layout = QHBoxLayout()
        top_layout.addLayout(first_v_layout)
        top_layout.addLayout(second_v_layout)
        top_layout.addLayout(third_v_layout)

        self.v_layout.addLayout(top_layout)
        self.v_layout.addWidget(self.table)

        self.h_box = QHBoxLayout()
        self.h_box.setSpacing(10)
        self.h_box.addWidget(self.label_tags)

        for tag_label in self.push_buttons:
            self.h_box.addWidget(tag_label)

        self.h_box.addWidget(self.add_tag_label)
        self.h_box.addWidget(self.remove_tag_label)
        self.h_box.addStretch(1)

        self.v_layout.addLayout(self.h_box)

    def add_tag(self):
        """ Method that adds a push button. """
        idx = len(self.push_buttons)
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.push_buttons) + 1))
        push_button.clicked.connect(lambda: self.select_tag(idx))
        self.push_buttons.insert(len(self.push_buttons), push_button)
        self.refresh_layout()

    def remove_tag(self):
        """ Method that removes a push buttons and makes the changes
        in the list of values. """
        push_button = self.push_buttons[-1]
        push_button.deleteLater()
        push_button = None
        del self.push_buttons[-1]
        del self.values_list[-1]
        self.refresh_layout()

    def update_table(self):
        if not self.scan_list:
            self.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)
        self.table.clear()
        self.table.setColumnCount(len(self.push_buttons))

        # Headers
        for idx in range(len(self.push_buttons)):
            header_name = self.push_buttons[idx].text()
            if header_name not in self.project.session.get_fields_names(COLLECTION_CURRENT):
                print("{0} not in the project's tags".format(header_name))
                return
            # TODO: if the header_name is not in the session, show a QMessageBox
            item = QTableWidgetItem()
            item.setText(header_name)
            self.table.setHorizontalHeaderItem(idx, item)

        filter_query = "({" + self.iterated_tag + "} " + "==" + " \"" + self.combo_box.currentText() + "\")"
        scans_list = self.project.session.filter_documents(COLLECTION_CURRENT, filter_query)
        scans_res = [getattr(document, TAG_FILENAME) for document in scans_list]
        self.scans = list(set(scans_res).intersection(self.scan_list))
        self.table.setRowCount(len(self.scans))
        row = -1
        for scan_name in self.scans:
            row += 1
            for idx in range(len(self.push_buttons)):
                tag_name = self.push_buttons[idx].text()

                item = QTableWidgetItem()
                item.setText(str(self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)))
                self.table.setItem(row, idx, item)

        # This will change the scans list in the current Pipeline Manager tab
        self.iteration_table_updated.emit(self.scans)

    def select_tag(self, idx):
        """ Method that calls a pop-up to choose a tag. """
        popUp = Ui_Select_Tag_Count_Table(self.project, self.project.session.get_fields_names(COLLECTION_CURRENT),
                                          self.push_buttons[idx].text())
        if popUp.exec_():
            self.push_buttons[idx].setText(popUp.selected_tag)
            self.fill_values(idx)
            self.update_table()

    def fill_values(self, idx):
        """ Method that fills the values list when a tag is added
        or removed. """
        tag_name = self.push_buttons[idx].text()
        values = []
        for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
            current_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag_name)
            if current_value is not None:
                values.append(current_value)

        idx_to_fill = len(self.values_list)
        while len(self.values_list) <= idx:
            self.values_list.insert(idx_to_fill, [])
            idx_to_fill += 1

        if self.values_list[idx] is not None:
            self.values_list[idx] = []

        for value in values:
            if value not in self.values_list[idx]:
                self.values_list[idx].append(value)

    def display_tags(self):
        ui_select = Ui_Select_Tag_Count_Table(self.project,
                                              self.project.session.get_fields_names(COLLECTION_CURRENT),
                                              self.iterated_tag)
        if ui_select.exec_():
            self.update_iterated_tag(ui_select.selected_tag)

    def update_iterated_tag(self, tag_name):

        self.iterated_tag_push_button.setText(tag_name)
        self.iterated_tag = tag_name
        self.iterated_tag_label.setText(tag_name + ":")

        # Update combo_box
        scans_names = self.project.session.get_documents_names(COLLECTION_CURRENT)
        self.tag_values_list = []
        for scan_name in scans_names:
            tag_value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
            if str(tag_value) not in self.tag_values_list:
                self.tag_values_list.append(str(tag_value))

        self.combo_box.clear()
        self.combo_box.addItems(self.tag_values_list)

        self.update_table()

    def emit_iteration_table_updated(self):
        self.iteration_table_updated.emit(self.scans)
