##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################


import os
import operator
from functools import reduce  # Valid in Python 2.6+, required in Python 3

# PyQt5 imports
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QTableWidget, QVBoxLayout, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt

# Populse_MIA imports
from populse_mia.pop_ups.pop_up_select_tag_count_table import PopUpSelectTagCountTable
from populse_mia.utils.tools import ClickableLabel
from populse_mia.utils.utils import set_item_data, table_to_database
from populse_mia.project.project import COLLECTION_CURRENT, TAG_FILENAME


class CountTable(QDialog):
    """
    Tool to precisely verify the scans of the project.

    It is composed of push buttons on its top, each one corresponding to a tag selected by the user.
    When, the "Count scans" button is clicked, a table is created with all the combinations possible
    for the values of the first n-1 tags. Then, the m values that can take the last tag are displayed
    in the header of the m last columns of the table. The cells are then filled with a green plus or
    a red cross depending on if there is at least a scan that has all the tags values or not.

    Example:

    Assume that the current project has scans for two patients (P1 and P2) and three time points (T1,
    T2 and T3). For each (patient, time point), several sequences have been made (two RARE, one MDEFT
    and one FLASH). Selecting [PatientName, TimePoint, SequenceName] as tags, the table will be:

    +-------------+-----------+------+-------+-------+
    | PatientName | TimePoint | RARE | MDEFT | FLASH |
    +=============+===========+======+=======+=======+
    | P1          | T1        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P1          | T2        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P1          | T3        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P2          | T1        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P2          | T2        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P2          | T3        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+

    with v(n) meaning that n scans corresponds of the selected values for (PatientName, TimePoint,
    SequenceName).

    If no scans corresponds for a triplet value, a red cross will be displayed. For example, if the
    user forgets to import one RARE for P1 at T2 and one FLASH for P2 at T3. The table will be:

    +-------------+-----------+------+-------+-------+
    | PatientName | TimePoint | RARE | MDEFT | FLASH |
    +=============+===========+======+=======+=======+
    | P1          | T1        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P1          | T2        | v(1) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P1          | T3        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P2          | T1        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P2          | T2        | v(2) | v(1)  | v(1)  |
    +-------------+-----------+------+-------+-------+
    | P2          | T3        | v(2) | v(1)  | x     |
    +-------------+-----------+------+-------+-------+

    Thus, thanks to the CountTable tool, he or she directly knows if some scans are missing.


    Attributes:
        - project: current project in the software
        - values_list: list that contains lists of all the values that the visualized tags can take

    Methods:
        - refresh_layout: updates the layout of the widget
        - add_tag: adds a tag to visualize in the count table
        - remove_tag: removes a tag to visualize in the count table
        - select_tag: opens a pop-up to select which tag to visualize in the count table
        - fill_values: fill values_list depending on the visualized tags
        - count_scans: counts the number of scans depending on the selected tags and displays the result in the table
        - fill_headers: fills the headers of the table depending on the selected tags
        - fill_first_tags: fills the cells of the table corresponding to the (n-1) first selected tags
        - fill_last_tag: fills the cells corresponding to the last selected tag
        - prepare_filter: prepares the filter in order to fill the count table

    """

    def __init__(self, project):
        """
        Initialization of the Count Table

        :param project: current project in the software
        """

        super().__init__()

        self.project = project

        self.setModal(True)
        self.setWindowTitle("Count table")

        # Font
        self.font = QFont()
        self.font.setBold(True)

        # values_list will contain the different values of each selected tag
        self.values_list = [[], []]

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

        # Push button that is pressed to launch the computations
        self.push_button_count = QPushButton()
        self.push_button_count.setText('Count scans')
        self.push_button_count.clicked.connect(self.count_scans)

        # The table that will be filled
        self.table = QTableWidget()

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.setLayout(self.v_box_final)
        self.refresh_layout()

    def refresh_layout(self):
        """
        Updates the layout of the widget
        """

        self.h_box_top = QHBoxLayout()
        self.h_box_top.setSpacing(10)
        self.h_box_top.addWidget(self.label_tags)

        for tag_label in self.push_buttons:
            self.h_box_top.addWidget(tag_label)

        self.h_box_top.addWidget(self.add_tag_label)
        self.h_box_top.addWidget(self.remove_tag_label)
        self.h_box_top.addWidget(self.push_button_count)
        self.h_box_top.addStretch(1)

        self.v_box_final.addLayout(self.h_box_top)
        self.v_box_final.addWidget(self.table)

    def add_tag(self):
        """
        Adds a tag to visualize in the count table
        """

        idx = len(self.push_buttons)
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.push_buttons) + 1))
        push_button.clicked.connect(lambda: self.select_tag(idx))
        self.push_buttons.insert(len(self.push_buttons), push_button)
        self.refresh_layout()

    def remove_tag(self):
        """
        Removes a tag to visualize in the count table
        """

        push_button = self.push_buttons[-1]
        push_button.deleteLater()
        push_button = None
        del self.push_buttons[-1]
        del self.values_list[-1]
        self.refresh_layout()

    def select_tag(self, idx):
        """
        Opens a pop-up to select which tag to visualize in the count table

        :param idx: the index of the selected push button
        """

        pop_up = PopUpSelectTagCountTable(self.project, self.project.session.get_fields_names(COLLECTION_CURRENT),
                                          self.push_buttons[idx].text())
        if pop_up.exec_():
            if pop_up.selected_tag is not None:
                self.push_buttons[idx].setText(pop_up.selected_tag)
                self.fill_values(idx)

    def fill_values(self, idx):
        """
        Fill values_list depending on the visualized tags

        :param idx: index of the select tag
        """

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

    def count_scans(self):
        """
        Counts the number of scans depending on the selected tags and displays the result in the table
        """

        for tag_values in self.values_list:
            if len(tag_values) == 0:
                return
        if self.project.session.get_field(COLLECTION_CURRENT, self.push_buttons[-1].text()) is None:
            return

        # Clearing the table
        self.table.clear()

        # nb_values will contain, for each index, the number of
        # different values that a tag can take
        self.nb_values = []
        for values in self.values_list:
            self.nb_values.append(len(values))

        # The number of rows will be the multiplication of all these
        # values
        self.nb_row = reduce(operator.mul, self.nb_values[:-1], 1)

        # The number of columns will be the addition of the number of
        # selected tags (minus 1) and the number of different values
        # that can take the last selected tag
        self.nb_col = len(self.values_list) - 1 + self.nb_values[-1]

        self.table.setRowCount(self.nb_row)
        self.table.setColumnCount(self.nb_col)

        self.fill_headers()
        self.fill_first_tags()
        self.fill_last_tag()

        self.table.resizeColumnsToContents()

    def fill_headers(self):
        """
        Fills the headers of the table depending on the selected tags
        """

        idx_end = 0
        # Headers
        for idx in range(len(self.values_list) - 1):
            header_name = self.push_buttons[idx].text()
            item = QTableWidgetItem()
            item.setText(header_name)
            self.table.setHorizontalHeaderItem(idx, item)
            idx_end = idx

        # idx_last_tag corresponds to the index of the (n-1)th tag
        self.idx_last_tag = idx_end
        last_tag = self.push_buttons[len(self.values_list) - 1].text()
        last_tag_type = self.project.session.get_field(COLLECTION_CURRENT, last_tag).type
        for header_name in self.values_list[-1]:
            idx_end += 1
            item = QTableWidgetItem()
            set_item_data(item, header_name, last_tag_type)
            self.table.setHorizontalHeaderItem(idx_end, item)

        # Adding a "Total" row and to count the scans
        self.table.insertRow(self.nb_row)
        item = QTableWidgetItem()
        item.setText('Total')

        item.setFont(self.font)

        self.table.setVerticalHeaderItem(self.nb_row, item)

    def fill_first_tags(self):
        """
        Fills the cells of the table corresponding to the (n-1) first selected tags
        """

        cell_text = []
        for col in range(len(self.values_list) - 1):
            # cell_text will contain the n-1 element to display
            cell_text.append(self.values_list[col][0])

            # Filling the last "Total" column
            item = QTableWidgetItem()
            item.setText(str(self.nb_values[col]))
            item.setFont(self.font)
            self.table.setItem(self.nb_row, col, item)

        # Filling the cells of the n-1 first tags
        for row in range(self.nb_row):

            for col in range(len(self.values_list) - 1):
                item = QTableWidgetItem()
                tag_name = self.push_buttons[col].text()
                tag_type = self.project.session.get_field(COLLECTION_CURRENT, tag_name).type
                set_item_data(item, cell_text[col], tag_type)
                self.table.setItem(row, col, item)

            # Looping from the (n-1)th tag
            col_checked = len(self.values_list) - 2
            # Flag up will be True when all values of the tag have been iterated
            flag_up = False
            while col_checked >= 0:
                if flag_up:
                    # In this case, the value of the right column has reach its last value
                    # This value has been reset to the first value
                    if cell_text[col_checked] == self.values_list[col_checked][-1]:
                        # If the value that has been displayed is the last one, the flag
                        # stays the same, the value of the column on the left has to be changed
                        cell_text[col_checked] = self.values_list[col_checked][0]
                    else:
                        # Else we iterate on the next value
                        idx = self.values_list[col_checked].index(cell_text[col_checked])
                        cell_text[col_checked] = self.values_list[col_checked][idx + 1]
                        flag_up = False

                if (col_checked > 0 and len(self.values_list) - 1 > 1) or (len(self.values_list) - 1 == 1):
                    if cell_text[col_checked] == self.values_list[col_checked][-1]:
                        # If the value that has been displayed is the last one, the flag
                        # is set to True, the value of the column on the left has to be changed
                        cell_text[col_checked] = self.values_list[col_checked][0]
                        flag_up = True
                    else:
                        # Else we iterate on the next value and reset the flag
                        idx = self.values_list[col_checked].index(cell_text[col_checked])
                        cell_text[col_checked] = self.values_list[col_checked][idx + 1]
                        flag_up = False

                    if not flag_up:
                        # If there is nothing to do, we quit the loop
                        break

                col_checked -= 1

    def fill_last_tag(self):
        """
        Fills the cells corresponding to the last selected tag
        """

        # Cells of the last tag
        for col in range(self.idx_last_tag + 1, self.nb_col):
            nb_scans_ok = 0
            # Creating a tag_list that will contain couples tag_name/tag_value that
            # will then querying the Database
            for row in range(self.nb_row):
                tag_list = []
                for idx_first_columns in range(self.idx_last_tag + 1):
                    tag_name = self.table.horizontalHeaderItem(idx_first_columns).text()
                    tag_type = self.project.session.get_field(COLLECTION_CURRENT, tag_name).type
                    value_str = self.table.item(row, idx_first_columns).data(Qt.EditRole)
                    value_database = table_to_database(value_str, tag_type)
                    tag_list.append([tag_name, value_database])
                tag_last_columns = self.push_buttons[-1].text()
                tag_last_columns_type = self.project.session.get_field(COLLECTION_CURRENT, tag_last_columns).type
                value_last_columns_str = self.table.horizontalHeaderItem(col).data(Qt.EditRole)
                value_last_columns_database = table_to_database(value_last_columns_str, tag_last_columns_type)
                tag_list.append([tag_last_columns, value_last_columns_database])

                item = QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                # Getting the list of the scans that corresponds to the couples
                # tag_name/tag_values
                generator_scans = self.project.session.filter_documents(COLLECTION_CURRENT,
                                                                        self.prepare_filter(tag_list))

                # List of scans created, given the generator
                list_scans = [getattr(scan, TAG_FILENAME) for scan in generator_scans]

                sources_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                                                  "sources_images")
                if list_scans:
                    icon = QIcon(os.path.join(sources_images_dir, 'green_v.png'))
                    length = len(list_scans)
                    nb_scans_ok += length
                    text = str(length)
                    item.setText(text)
                    tool_tip = ''
                    # Setting as tooltip all the corresponding scans
                    for tpl in list_scans:
                        tool_tip += (tpl + '\n')
                    tool_tip = tool_tip[:-1]
                    item.setToolTip(tool_tip)
                else:
                    icon = QIcon(os.path.join(sources_images_dir, 'red_cross.png'))
                item.setIcon(icon)
                self.table.setItem(row, col, item)

            item = QTableWidgetItem()
            item.setText(str(nb_scans_ok))
            item.setFont(self.font)
            self.table.setItem(self.nb_row, col, item)

    @staticmethod
    def prepare_filter(couples):
        """
        Prepares the filter in order to fill the count table

        :param couples: (tag, value) couples
        :return: Str query of the corresponding filter
        """

        query = ""

        and_to_write = False

        for couple in couples:
            tag = couple[0]
            value = couple[1]

            # No AND for the first condition
            if and_to_write:
                query += " AND "

            and_to_write = True

            query += "({" + tag + "} == \"" + str(value) + "\")"

        query = "(" + query + ")"

        return query
