##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

from datetime import datetime

# PyQt5 imports
from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QPushButton, QMessageBox

# Populse_MIA imports
from populse_mia.utils.utils import check_value_type
from populse_mia.project.project import COLLECTION_CURRENT

# Populse_db imports
from populse_db.database import FIELD_TYPE_LIST_INTEGER, FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_STRING, \
    FIELD_TYPE_LIST_DATE, FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_TIME


class ModifyTable(QDialog):
    """
    Is called when the user wants to verify precisely the scans of the project.

    Attributes:
        - project: current project in the software
        - values: list of values of the cell
        - types: value types
        - scans: scans of the rows
        - tags: tags of the columns
        - table: table widget

    Methods:
        - fill_table: fills the table
        - update_table_values: updates the table in the database
    """

    def __init__(self, project, value, types, scans, tags):
        """
        Initialization of the ModifyTable class

        :param project: Instance of project
        :param value: List of values of the cell
        :param types: Value types
        :param scans: Scans of the rows
        :param tags: Tags of the columns
        """
        super().__init__()

        self.setModal(True)

        # Variables init
        self.types = types
        self.scans = scans
        self.tags = tags
        self.project = project
        self.value = value

        # The table that will be filled
        self.table = QTableWidget()

        # Filling the table
        self.fill_table()

        # Ok button
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.update_table_values)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.h_box_final = QHBoxLayout()

        self.h_box_final.addWidget(ok_button)
        self.h_box_final.addWidget(cancel_button)

        self.v_box_final.addWidget(self.table)
        self.v_box_final.addLayout(self.h_box_final)

        self.setLayout(self.v_box_final)

    def fill_table(self):
        """
        Fills the table
        """
        # Sizes
        self.table.setColumnCount(len(self.value))
        self.table.setRowCount(1)

        # Values filled
        for i in range (0, self.table.columnCount()):
            column_elem = self.value[i]
            item = QTableWidgetItem()
            item.setText(str(column_elem))
            self.table.setItem(0, i, item)

        # Resize
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

    def update_table_values(self):
        """
        Updates the table in the database after Ok is clicked
        """
        valid = True

        # For each value, type checked
        for i in range (0, self.table.columnCount()):
            item = self.table.item(0, i)
            text = item.text()

            valid_type = True
            for tag_type in self.types:
                if not check_value_type(text, tag_type, True):
                    valid_type = False
                    type_problem = tag_type
                    break

            # Type checked
            if not valid_type:

                # Error dialog if invalid cell
                valid = False
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Invalid value")
                msg.setInformativeText("The value " + text + " is invalid with the type " + type_problem)
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()
                break

        if valid:
            # Database updated only if valid type for every cell

            for cell in range (0, len(self.scans)):
                scan = self.scans[cell]
                tag = self.tags[cell]
                tag_object = self.project.session.get_field(COLLECTION_CURRENT, tag)
                tag_type = tag_object.type

                database_value = []

                # For each value
                for i in range (0, self.table.columnCount()):
                    item = self.table.item(0, i)
                    text = item.text()

                    if tag_type == FIELD_TYPE_LIST_INTEGER:
                        database_value.append(int(text))
                    elif tag_type == FIELD_TYPE_LIST_FLOAT:
                        database_value.append(float(text))
                    elif tag_type == FIELD_TYPE_LIST_STRING:
                        database_value.append(str(text))
                    elif tag_type == FIELD_TYPE_LIST_DATE:
                        format = "%d/%m/%Y"
                        subvalue = datetime.strptime(text, format).date()
                        database_value.append(subvalue)
                    elif tag_type == FIELD_TYPE_LIST_DATETIME:
                        format = "%d/%m/%Y %H:%M"
                        subvalue = datetime.strptime(text, format)
                        database_value.append(subvalue)
                    elif tag_type == FIELD_TYPE_LIST_TIME:
                        format = "%H:%M"
                        subvalue = datetime.strptime(text, format).time()
                        database_value.append(subvalue)

                # Database updated for every cell
                self.project.session.set_value(COLLECTION_CURRENT, scan, tag, database_value)

            self.close()
