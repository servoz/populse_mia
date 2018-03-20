from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QPushButton, QMessageBox
from Utils.utils import check_value_type
from DataBase.DataBaseModel import TAG_TYPE_FLOAT, TAG_TYPE_INTEGER

class ModifyTable(QDialog):
    """
    Is called when the user wants to verify precisely the scans of the project.
    """

    def __init__(self, database, list_value, types, scans, tags):
        """
        ModifyTable init
        :param database: Instance of database
        :param list_value: List of values of the cell
        :param types: Value types
        :param scans: Scans of the rows
        :param tags: Tags of the columns
        """
        super().__init__()

        # Variables init
        self.types = types
        self.scans = scans
        self.tags = tags
        self.database = database
        self.value = list_value

        # The table that will be filled
        self.table = QTableWidget()

        # Fill the table
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
        i = 0
        while i < self.table.columnCount():
            column_elem = self.value[i]
            if len(column_elem) == 1:
                item = QTableWidgetItem()
                item.setText(str(column_elem[0]))
                self.table.setItem(0, i, item)
            i += 1

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
        To update the table in the database after Ok is clicked
        """
        valid = True

        # For each value, type checked
        i = 0
        while i < self.table.columnCount():
            item = self.table.item(0, i)
            text = item.text()

            valid_type = True
            for type in self.types:
                if not check_value_type(text, type):
                    valid_type = False
                    type_problem = type
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

            i += 1

        if valid:
            # Database updated only if valid type for every cell

            cell = 0
            while cell < len(self.scans):
                scan = self.scans[cell]
                tag = self.tags[cell]
                type = self.database.getTagType(tag)

                database_value = []

                # For each value
                i = 0
                while i < self.table.columnCount():
                    item = self.table.item(0, i)
                    text = item.text()

                    if type == TAG_TYPE_INTEGER:
                        database_value.append([int(text)])
                    elif type == TAG_TYPE_FLOAT:
                        database_value.append([float(text)])
                    else:
                        database_value.append([str(text)])
                    i += 1

                # Database updated for every cell
                self.database.setTagValue(scan, tag, str(database_value))

                cell += 1

            self.close()