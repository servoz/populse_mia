##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os

# PyQt5 imports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import  QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, \
    QHBoxLayout, QCheckBox, QTableWidget, QComboBox, QLabel

# MIA imports
from populse_mia.pipeline_manager.process_mia import ProcessMIA
from populse_mia.pop_ups.pop_up_select_tag_count_table import PopUpSelectTagCountTable
from populse_mia.project.project import COLLECTION_CURRENT, TAG_FILENAME
from populse_mia.utils.tools import ClickableLabel


class IterationTable(QWidget):
    """
    Widget that handles pipeline iteration.

    Attributes:
        - project: current project in the software
        - scan_list: list of the selected database files
        - iteration_scans: list of the selected scans for the current iteration step
        - main_window: software's main_window
        - iterated_tag: tag on which to iterate
        - values_list: list that contains lists of all the values that the visualized tags can take

    Methods:
        - refresh_layout: updates the layout of the widget
        - add_tag: adds a tag to visualize in the iteration table
        - remove_tag: removes a tag to visualize in the iteration table
        - update_table: updates the iteration table
        - select_visualized_tag: opens a pop-up to let the user select which tag to visualize in the iteration table
        - fill_values: fill values_list depending on the visualized tags
        - select_iterated_tag: opens a pop-up to let the user select on which tag to iterate
        - update_iterated_tag: updates the widget
        - emit_iteration_table_updated: emits a signal when the iteration scans have been updated
    """

    iteration_table_updated = pyqtSignal(list)

    def __init__(self, project, scan_list, main_window):
        """
        Initialization of the IterationTable widget

        :param project: current project in the software
        :param scan_list: list of the selected database files
        :param main_window: software's main_window
        """

        QWidget.__init__(self)

        ProcessMIA.project = project
        self.project = project

        if not scan_list:
            self.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)
        else:
            self.scan_list = scan_list

        self.main_window = main_window
        self.iterated_tag = None

        # values_list will contain the different values of each selected tag
        self.values_list = [[], []]

        # Checkbox to choose to iterate the pipeline or not
        self.check_box_iterate = QCheckBox("Iterate pipeline")
        self.check_box_iterate.stateChanged.connect(self.emit_iteration_table_updated)

        # Label "Iterate over:"
        self.label_iterate = QLabel("Iterate over:")

        # Label that displays the name of the selected tag
        self.iterated_tag_label = QLabel("Select a tag")

        # Push button to select the tag to iterate
        self.iterated_tag_push_button = QPushButton("Select")
        self.iterated_tag_push_button.clicked.connect(self.select_iteration_tag)

        # QComboBox
        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.update_table)

        # QTableWidget
        self.iteration_table = QTableWidget()

        # Label tag
        self.label_tags = QLabel("Tags to visualize:")

        # Each push button will allow the user to visualize a tag in the iteration browser
        push_button_tag_1 = QPushButton()
        push_button_tag_1.setText("SequenceName")
        push_button_tag_1.clicked.connect(lambda: self.select_visualized_tag(0))

        push_button_tag_2 = QPushButton()
        push_button_tag_2.setText("AcquisitionDate")
        push_button_tag_2.clicked.connect(lambda: self.select_visualized_tag(1))

        # The list of all the push buttons (the user can add as many as he or she wants)
        self.push_buttons = []
        self.push_buttons.insert(0, push_button_tag_1)
        self.push_buttons.insert(1, push_button_tag_2)

        # Labels to add/remove a tag (a push button)
        self.add_tag_label = ClickableLabel()
        self.add_tag_label.setObjectName('plus')
        sources_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                          "sources_images")
        add_tag_picture = QPixmap(os.path.relpath(os.path.join(sources_images_dir, "green_plus.png")))
        add_tag_picture = add_tag_picture.scaledToHeight(15)
        self.add_tag_label.setPixmap(add_tag_picture)
        self.add_tag_label.clicked.connect(self.add_tag)

        self.remove_tag_label = ClickableLabel()
        remove_tag_picture = QPixmap(os.path.relpath(os.path.join(sources_images_dir, "red_minus.png")))
        remove_tag_picture = remove_tag_picture.scaledToHeight(20)
        self.remove_tag_label.setPixmap(remove_tag_picture)
        self.remove_tag_label.clicked.connect(self.remove_tag)

        # Layout
        self.v_layout = QVBoxLayout()
        self.setLayout(self.v_layout)
        self.refresh_layout()

    def refresh_layout(self):
        """
        Updates the layout of the widget
        Called in widget's initialization and when a tag push button is added or removed.

        """

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
        self.v_layout.addWidget(self.iteration_table)

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
        """
        Adds a tag to visualize in the iteration table

        """

        idx = len(self.push_buttons)
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.push_buttons) + 1))
        push_button.clicked.connect(lambda: self.select_visualized_tag(idx))
        self.push_buttons.insert(len(self.push_buttons), push_button)
        self.refresh_layout()

    def remove_tag(self):
        """
        Removes a tag to visualize in the iteration table
        Removes also the corresponding values in values_list

        """

        push_button = self.push_buttons[-1]
        push_button.deleteLater()
        push_button = None
        del self.push_buttons[-1]
        del self.values_list[-1]
        self.refresh_layout()

    def update_table(self):
        """
        Updates the iteration table

        """

        # Updating the scan list
        if not self.scan_list:
            self.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)

        # Clearing the table and preparing its columns
        self.iteration_table.clear()
        self.iteration_table.setColumnCount(len(self.push_buttons))

        # Headers
        for idx in range(len(self.push_buttons)):
            header_name = self.push_buttons[idx].text()
            if header_name not in self.project.session.get_fields_names(COLLECTION_CURRENT):
                print("{0} not in the project's tags".format(header_name))
                return

            item = QTableWidgetItem()
            item.setText(header_name)
            self.iteration_table.setHorizontalHeaderItem(idx, item)

        # Searching the database scans that correspond to the iterated tag value
        filter_query = "({" + self.iterated_tag + "} " + "==" + " \"" + self.combo_box.currentText() + "\")"
        scans_list = self.project.session.filter_documents(COLLECTION_CURRENT, filter_query)
        scans_res = [getattr(document, TAG_FILENAME) for document in scans_list]

        # Taking the intersection between the found database scans and the user selection in the data_browser
        self.iteration_scans = list(set(scans_res).intersection(self.scan_list))
        self.iteration_table.setRowCount(len(self.iteration_scans))

        # Filling the table cells
        row = -1
        for scan_name in self.iteration_scans:
            row += 1
            for idx in range(len(self.push_buttons)):
                tag_name = self.push_buttons[idx].text()

                item = QTableWidgetItem()
                item.setText(str(self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)))
                self.iteration_table.setItem(row, idx, item)

        # This will change the scans list in the current Pipeline Manager tab
        self.iteration_table_updated.emit(self.iteration_scans)

    def select_visualized_tag(self, idx):
        """
        Opens a pop-up to let the user select which tag to visualize in the iteration table

        :param idx: index of the clicked push button
        """

        popUp = PopUpSelectTagCountTable(self.project, self.project.session.get_fields_names(COLLECTION_CURRENT),
                                         self.push_buttons[idx].text())
        if popUp.exec_():
            self.push_buttons[idx].setText(popUp.selected_tag)
            self.fill_values(idx)
            self.update_table()

    def fill_values(self, idx):
        """
        Fill values_list depending on the visualized tags

        :param idx:
        """

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

    def select_iteration_tag(self):
        """
        Opens a pop-up to let the user select on which tag to iterate

        """

        ui_select = PopUpSelectTagCountTable(self.project,
                                             self.project.session.get_fields_names(COLLECTION_CURRENT),
                                             self.iterated_tag)
        if ui_select.exec_():
            self.update_iterated_tag(ui_select.selected_tag)

    def update_iterated_tag(self, tag_name):
        """
        Updates the widget when the iterated tag is modified

        :param tag_name: name of the iterated tag
        """

        if not self.scan_list:
            self.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)

        self.iterated_tag_push_button.setText(tag_name)
        self.iterated_tag = tag_name
        self.iterated_tag_label.setText(tag_name + ":")

        # Update combo_box
        scans_names = self.project.session.get_documents_names(COLLECTION_CURRENT)
        scans_names = list(set(scans_names).intersection(self.scan_list))

        # tag_values_list contains all the values that can take the iterated tag
        self.tag_values_list = []
        for scan_name in scans_names:
            tag_value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
            if str(tag_value) not in self.tag_values_list:
                self.tag_values_list.append(str(tag_value))

        self.combo_box.clear()
        self.combo_box.addItems(self.tag_values_list)

        self.update_table()

    def emit_iteration_table_updated(self):
        """
        Emits a signal when the iteration scans have been updated

        """

        if self.check_box_iterate.checkState():
            if hasattr(self, 'scans'):
                self.iteration_table_updated.emit(self.iteration_scans)
            else:
                self.iteration_table_updated.emit(self.scan_list)
        else:
            self.iteration_table_updated.emit(self.scan_list)

