import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QTableWidget, QFrame, \
    QVBoxLayout, QTableWidgetItem
from PyQt5.QtGui import QIcon, QPixmap, QFont
import os
from PopUps.Ui_Select_Tag_Count_Table import Ui_Select_Tag_Count_Table
from Utils.Tools import ClickableLabel

from functools import reduce # Valid in Python 2.6+, required in Python 3
import operator


class CountTable(QDialog):
    """
    Is called when the user wants to verify precisely the scans of the project.
    """

    def __init__(self, project=None):
        super().__init__()

        self.project = project

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
        """ Methods that update the layouts (especially when a tag push button
        is added or removed. """
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
        """ Method that adds a push button. """
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.push_buttons) + 1))
        push_button.clicked.connect(lambda: self.select_tag(len(self.push_buttons) - 1))
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

    def select_tag(self, idx):
        """ Method that calls a pop-up to choose a tag. """
        popUp = Ui_Select_Tag_Count_Table(self.project, self.push_buttons[idx].text())
        if popUp.exec_():
            self.push_buttons[idx].setText(popUp.selected_tag)
            self.fill_values(idx)
            print("idx: ", idx)

    def fill_values(self, idx):
        """ Method that fills the values list when a tag is added
        or removed. """
        tag_name = self.push_buttons[idx].text()
        values = []
        for scan in self.project.database.get_paths_names():
            current_value = self.project.database.get_current_value(scan, tag_name)
            initial_value = self.project.database.get_initial_value(scan, tag_name)
            if current_value is not None or initial_value is not None:
                values.append([scan, tag_name, current_value, initial_value])
        if len(self.values_list) <= idx:
            self.values_list.insert(idx, [])
        if self.values_list[idx] is not None:
            self.values_list[idx] = []
        for value in values:
            if str(value[3]) not in self.values_list[idx]:
                self.values_list[idx].append(str(value[3]))

    def count_scans(self):
        """ Method that counts the number of scans depending on the
        selected tags and displays the result in the table"""

        # Clearing the table
        self.table.clear()

        # Font
        self.font = QFont()
        self.font.setBold(True)

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
        """ Method that fills the headers of the table depending on
        the selected tags. """
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

        for header_name in self.values_list[-1]:
            idx_end += 1
            item = QTableWidgetItem()
            item.setText(header_name)
            self.table.setHorizontalHeaderItem(idx_end, item)

        # Adding a "Total" row and to count the scans
        self.table.insertRow(self.nb_row)
        item = QTableWidgetItem()
        item.setText('Total')

        item.setFont(self.font)

        self.table.setVerticalHeaderItem(self.nb_row, item)

    def fill_first_tags(self):
        """ Method that fills the cells of the table corresponding to
        the (n-1) first selected tags. """
        cell_text = []
        print(self.values_list)
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
                item.setText(cell_text[col])
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

                if col_checked > 0:
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
        """ Method that fills the cells corresponding to the last selected tag. """

        # Cells of the last tag
        for col in range(self.idx_last_tag + 1, self.nb_col):
            nb_scans_ok = 0
            # Creating a tag_list that will contain couples tag_name/tag_value that
            # will then querying the Database
            for row in range(self.nb_row):
                tag_list = []
                for idx_first_columns in range(self.idx_last_tag + 1):
                    value = self.table.item(row, idx_first_columns).text()
                    tag_name = self.table.horizontalHeaderItem(idx_first_columns).text()
                    tag_list.append([tag_name, value])
                value_last_columns = self.table.horizontalHeaderItem(col).text()
                tag_last_columns = self.push_buttons[-1].text()
                tag_list.append([tag_last_columns, value_last_columns])

                item = QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                # Getting the list of the scans that corresponds to the couples
                # tag_name/tag_values
                list_scans = self.project.database.get_paths_matching_tag_value_couples(tag_list)

                if list_scans:
                    icon = QIcon(os.path.join('..', 'sources_images', 'green_v.png'))
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
                    icon = QIcon(os.path.join('..', 'sources_images', 'red_cross.png'))
                item.setIcon(icon)
                self.table.setItem(row, col, item)

            item = QTableWidgetItem()
            item.setText(str(nb_scans_ok))
            item.setFont(self.font)
            self.table.setItem(self.nb_row, col, item)