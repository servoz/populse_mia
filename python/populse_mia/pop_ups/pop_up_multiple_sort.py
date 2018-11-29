##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os

# PyQt5 imports
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QComboBox, QVBoxLayout
from PyQt5.QtGui import QPixmap

# Populse_MIA imports
from populse_mia.pop_ups.pop_up_select_tag_count_table import PopUpSelectTagCountTable
from populse_mia.utils.tools import ClickableLabel
from populse_mia.project.project import COLLECTION_CURRENT


class PopUpMultipleSort(QDialog):
    """
    Is called to sort the data browser's table depending on multiple tags

    Attributes:
        - project: current project in the software
        - table_data_browser: data browser's table of the software
        - values_list: list containing the values that can take each selected tag
        - list_tags: list of the selected tags

    Methods:
        - refresh_layout: updates the layouts (especially when a tag push button is added or removed)
        - add_tag: adds a push button
        - remove_tag: removes a push buttons and makes the changes in the list of values
        - select_tag: calls a pop-up to choose a tag
        - fill_values: fills the values list when a tag is added or removed
        - sort_scans: collects the information and send them to the data browser
    """
    def __init__(self, project, table_data_browser):
        super().__init__()
        self.project = project
        self.table_data_browser = table_data_browser

        self.setModal(True)
        self.setWindowTitle("Multiple sort")

        # values_list will contain the different values of each selected tag
        self.values_list = [[], []]
        self.list_tags = []

        self.label_tags = QLabel('Tags: ')

        # Each push button will allow the user to add a tag to the count table
        push_button_tag_1 = QPushButton()
        push_button_tag_1.setText("Tag n°1")
        push_button_tag_1.clicked.connect(lambda: self.select_tag(0))

        push_button_tag_2 = QPushButton()
        push_button_tag_2.setText("Tag n°2")
        push_button_tag_2.clicked.connect(lambda: self.select_tag(1))

        # The list of all the push buttons (the user can add as many as he or she wants)
        self.push_buttons = []
        self.push_buttons.insert(0, push_button_tag_1)
        self.push_buttons.insert(1, push_button_tag_2)

        # Labels to add/remove a tag (a push button)
        sources_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                          "sources_images")
        self.remove_tag_label = ClickableLabel()
        remove_tag_picture = QPixmap(os.path.relpath(os.path.join(sources_images_dir, "red_minus.png")))
        remove_tag_picture = remove_tag_picture.scaledToHeight(20)
        self.remove_tag_label.setPixmap(remove_tag_picture)
        self.remove_tag_label.clicked.connect(self.remove_tag)

        self.add_tag_label = ClickableLabel()
        self.add_tag_label.setObjectName('plus')
        add_tag_picture = QPixmap(os.path.relpath(os.path.join(sources_images_dir, "green_plus.png")))
        add_tag_picture = add_tag_picture.scaledToHeight(15)
        self.add_tag_label.setPixmap(add_tag_picture)
        self.add_tag_label.clicked.connect(self.add_tag)

        # Combobox to choose if the sort order is ascending or descending
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Ascending", "Descending"])

        # Push button that is pressed to launch the computations
        self.push_button_sort = QPushButton()
        self.push_button_sort.setText('Sort scans')
        self.push_button_sort.clicked.connect(self.sort_scans)

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.setLayout(self.v_box_final)
        self.refresh_layout()

    def refresh_layout(self):
        """
        Updates the layouts (especially when a tag push button is added or removed)
        """
        self.h_box_top = QHBoxLayout()
        self.h_box_top.setSpacing(10)
        self.h_box_top.addWidget(self.label_tags)

        for tag_label in self.push_buttons:
            self.h_box_top.addWidget(tag_label)

        self.h_box_top.addWidget(self.add_tag_label)
        self.h_box_top.addWidget(self.remove_tag_label)
        self.h_box_top.addWidget(self.combo_box)
        self.h_box_top.addWidget(self.push_button_sort)
        self.h_box_top.addStretch(1)

        self.v_box_final.addLayout(self.h_box_top)

    def add_tag(self):
        """
        Adds a push button
        """
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.push_buttons) + 1))
        push_button.clicked.connect(lambda: self.select_tag(len(self.push_buttons) - 1))
        self.push_buttons.insert(len(self.push_buttons), push_button)
        self.refresh_layout()

    def remove_tag(self):
        """
        Removes a push buttons and makes the changesn in the list of values
        """
        push_button = self.push_buttons[-1]
        push_button.deleteLater()
        push_button = None
        del self.push_buttons[-1]
        del self.values_list[-1]
        self.refresh_layout()

    def select_tag(self, idx):
        """
        Calls a pop-up to choose a tag

        :param idx: index of the pressed push button
        """
        pop_up = PopUpSelectTagCountTable(self.project, self.project.session.get_visibles(), self.push_buttons[idx].text())
        if pop_up.exec_():
            self.push_buttons[idx].setText(pop_up.selected_tag)
            self.fill_values(idx)

    def fill_values(self, idx):
        """
        Fills the values list when a tag is added or removed

        :param idx: index of the pressed push button
        """
        tag_name = self.push_buttons[idx].text()
        if len(self.values_list) <= idx:
            self.values_list.insert(idx, [])
        if self.values_list[idx] is not None:
            self.values_list[idx] = []
        for scan in self.project.session.get_fields_names(COLLECTION_CURRENT):
            current_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag_name)
            if current_value not in self.values_list[idx]:
                self.values_list[idx].append(current_value)

    def sort_scans(self):
        """
        Collects the information and send them to the data browser
        """
        self.order = self.combo_box.itemText(self.combo_box.currentIndex())
        for push_button in self.push_buttons:
            self.list_tags.append(push_button.text())
        self.accept()
        self.table_data_browser.multiple_sort_infos(self.list_tags, self.order)
