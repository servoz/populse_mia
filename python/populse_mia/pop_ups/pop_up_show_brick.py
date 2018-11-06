##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QTableWidgetItem, QWidget, QLabel, QPushButton, \
    QApplication

# Populse_MIA imports
from populse_mia.project.project import COLLECTION_BRICK, BRICK_NAME, BRICK_EXEC, BRICK_EXEC_TIME, BRICK_INIT, BRICK_INIT_TIME, \
    BRICK_INPUTS, BRICK_OUTPUTS, COLLECTION_CURRENT


class PopUpShowBrick(QDialog):
    """
    Class to display the brick history of a document

    Attributes:
        - project: current project in the software
        - databrowser: data browser instance of the software
        - main_window: main window of the software

    Methods:
        - io_value_is_scan: checks if the I/O value is a scan
        - file_clicked: called when a file is clicked
    """

    def __init__(self, project, brick_uuid, databrowser, main_window):
        """
        Prepares the brick history popup
        :param project: project
        :param brick_uuid: brick to display
        :param databrowser; data browser that made the call
        :param main_window: main window of the software
        """

        super().__init__()

        self.setModal(True)

        self.databrowser = databrowser
        self.main_window = main_window
        self.project = project
        brick_row = project.session.get_document(COLLECTION_BRICK, brick_uuid)
        self.setWindowTitle("Brick " + getattr(brick_row, BRICK_NAME) + " history")

        layout = QVBoxLayout()

        self.table = QTableWidget()

        # Filling the table
        inputs = getattr(brick_row, BRICK_INPUTS)
        outputs = getattr(brick_row, BRICK_OUTPUTS)
        self.table.setRowCount(1)
        self.table.setColumnCount(5 + len(inputs) + len(outputs))

        # Brick name
        item = QTableWidgetItem()
        item.setText(BRICK_NAME)
        self.table.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setText(getattr(brick_row, BRICK_NAME))
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(0, 0, item)

        # Brick init
        item = QTableWidgetItem()
        item.setText(BRICK_INIT)
        self.table.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        item.setText(getattr(brick_row, BRICK_INIT))
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(0, 1, item)

        # Brick init time
        item = QTableWidgetItem()
        item.setText(BRICK_INIT_TIME)
        self.table.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        if getattr(brick_row, BRICK_INIT_TIME) is not None:
            item.setText(str(getattr(brick_row, BRICK_INIT_TIME)))
            self.table.setItem(0, 2, item)

        # Brick execution
        item = QTableWidgetItem()
        item.setText(BRICK_EXEC)
        self.table.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setText(getattr(brick_row, BRICK_EXEC))
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(0, 3, item)

        # Brick execution time
        item = QTableWidgetItem()
        item.setText(BRICK_EXEC_TIME)
        self.table.setHorizontalHeaderItem(4, item)
        item = QTableWidgetItem()
        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
        if getattr(brick_row, BRICK_EXEC_TIME) is not None:
            item.setText(str(getattr(brick_row, BRICK_EXEC_TIME)))
        self.table.setItem(0, 4, item)

        column = 5

        # Inputs
        for key, value in sorted(inputs.items()):
            item = QTableWidgetItem()
            item.setText(key)
            self.table.setHorizontalHeaderItem(column, item)
            if isinstance(value, list):
                sub_widget = QWidget()
                sub_layout = QVBoxLayout()
                for sub_value in value:
                    value_scan = self.io_value_is_scan(sub_value)
                    if value_scan is not None:
                        button = QPushButton(value_scan)
                        button.clicked.connect(self.file_clicked)
                        sub_layout.addWidget(button)
                    else:
                        label = QLabel(str(sub_value))
                        sub_layout.addWidget(label)
                sub_widget.setLayout(sub_layout)
                self.table.setCellWidget(0, column, sub_widget)
            else:
                value_scan = self.io_value_is_scan(value)
                if value_scan is not None:
                    widget = QWidget()
                    output_layout = QVBoxLayout()
                    button = QPushButton(value_scan)
                    button.clicked.connect(self.file_clicked)
                    output_layout.addWidget(button)
                    widget.setLayout(output_layout)
                    self.table.setCellWidget(0, column, widget)
                else:
                    item = QTableWidgetItem()
                    item.setText(str(value))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.table.setItem(0, column, item)
            column += 1

        # Outputs
        for key, value in sorted(outputs.items()):
            item = QTableWidgetItem()
            item.setText(key)
            self.table.setHorizontalHeaderItem(column, item)
            value = outputs[key]
            if isinstance(value, list):
                sub_widget = QWidget()
                sub_layout = QVBoxLayout()
                for sub_value in value:
                    value_scan = self.io_value_is_scan(sub_value)
                    if value_scan is not None:
                        button = QPushButton(value_scan)
                        button.clicked.connect(self.file_clicked)
                        sub_layout.addWidget(button)
                    else:
                        label = QLabel(str(sub_value))
                        sub_layout.addWidget(label)
                sub_widget.setLayout(sub_layout)
                self.table.setCellWidget(0, column, sub_widget)
            else:
                value_scan = self.io_value_is_scan(value)
                if value_scan is not None:
                    widget = QWidget()
                    output_layout = QVBoxLayout()
                    button = QPushButton(value_scan)
                    button.clicked.connect(self.file_clicked)
                    output_layout.addWidget(button)
                    widget.setLayout(output_layout)
                    self.table.setCellWidget(0, column, widget)
                else:
                    item = QTableWidgetItem()
                    item.setText(str(value))
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.table.setItem(0, column, item)
            column += 1

        self.table.verticalHeader().setMinimumSectionSize(30)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        layout.addWidget(self.table)

        self.setLayout(layout)

        screen_resolution = QApplication.instance().desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setMinimumHeight(0.5 * height)
        self.setMinimumWidth(0.8 * width)

    def io_value_is_scan(self, value):
        """
        Checks if the I/O value is a scan

        :param value: I/O value
        :return: The scan corresponding to the value if it exists, None otherwise
        """

        value_scan = None
        for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
            if scan in str(value):
                value_scan = scan
        return value_scan

    def file_clicked(self):
        """
        Called when a file is clicked
        """

        file = self.sender().text()
        self.databrowser.table_data.clearSelection()
        row_to_select = self.databrowser.table_data.get_scan_row(file)
        self.databrowser.table_data.selectRow(row_to_select)
        item_to_scroll_to = self.databrowser.table_data.item(row_to_select, 0)
        self.databrowser.table_data.scrollToItem(item_to_scroll_to)
        self.close()
