from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QTableWidgetItem, QWidget, QLabel, QPushButton, \
    QApplication

from Project.Project import COLLECTION_BRICK, BRICK_NAME, BRICK_EXEC, BRICK_EXEC_TIME, BRICK_INIT, BRICK_INIT_TIME, \
    BRICK_INPUTS, BRICK_OUTPUTS, COLLECTION_CURRENT


class Ui_Dialog_Show_Brick(QDialog):
    """
    Class to display the brick history
    """

    def __init__(self, project, brick_uuid, databrowser, imageViewer):
        """
        Prepares the brick history popup
        :param project: project
        :param brick_uuid: brick to display
        :param databrowser; databrowser that made the call
        :param imageViewer: main window
        """

        super().__init__()

        self.databrowser = databrowser
        self.imageViewer = imageViewer
        project = project
        brick_row = project.session.get_document(COLLECTION_BRICK, brick_uuid)
        self.setWindowTitle("Brick " + getattr(brick_row, BRICK_NAME) + " history")

        layout = QVBoxLayout()

        table = QTableWidget()

        # Filling the table
        inputs = getattr(brick_row, BRICK_INPUTS)
        outputs = getattr(brick_row, BRICK_OUTPUTS)
        table.setRowCount(1)
        table.setColumnCount(5 + len(inputs) + len(outputs))

        # Brick name
        item = QTableWidgetItem()
        item.setText(BRICK_NAME)
        table.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        item.setText(getattr(brick_row, BRICK_NAME))
        table.setItem(0, 0, item)

        # Brick init
        item = QTableWidgetItem()
        item.setText(BRICK_INIT)
        table.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        item.setText(getattr(brick_row, BRICK_INIT))
        table.setItem(0, 1, item)

        # Brick init time
        item = QTableWidgetItem()
        item.setText(BRICK_INIT_TIME)
        table.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        if getattr(brick_row, BRICK_INIT_TIME) is not None:
            item.setText(str(getattr(brick_row, BRICK_INIT_TIME)))
        table.setItem(0, 2, item)

        # Brick execution
        item = QTableWidgetItem()
        item.setText(BRICK_EXEC)
        table.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setText(getattr(brick_row, BRICK_EXEC))
        table.setItem(0, 3, item)

        # Brick execution time
        item = QTableWidgetItem()
        item.setText(BRICK_EXEC_TIME)
        table.setHorizontalHeaderItem(4, item)
        item = QTableWidgetItem()
        if getattr(brick_row, BRICK_EXEC_TIME) is not None:
            item.setText(str(getattr(brick_row, BRICK_EXEC_TIME)))
        table.setItem(0, 4, item)

        column = 5

        # Inputs
        for name in inputs:
            item = QTableWidgetItem()
            item.setText(name)
            table.setHorizontalHeaderItem(column, item)
            value = inputs[name]
            if isinstance(value, list):
                widget = QWidget()
                sub_layout = QVBoxLayout()
                for sub_value in value:
                    value_scan = None
                    for scan in project.session.get_documents_names(COLLECTION_CURRENT):
                        if scan in str(sub_value):
                            value_scan = scan
                    if value_scan is not None:
                        button = QPushButton(value_scan)
                        button.clicked.connect(self.file_clicked)
                        sub_layout.addWidget(button)
                    else:
                        label = QLabel(str(sub_value))
                        sub_layout.addWidget(label)
                widget.setLayout(sub_layout)
                table.setCellWidget(0, column, widget)
            else:
                item = QTableWidgetItem()
                item.setText(str(value))
                table.setItem(0, column, item)
            column += 1

        # Outputs
        for name in outputs:
            item = QTableWidgetItem()
            item.setText(name)
            table.setHorizontalHeaderItem(column, item)
            value = outputs[name]
            if isinstance(value, list):
                widget = QWidget()
                sub_layout = QVBoxLayout()
                for sub_value in value:
                    value_scan = None
                    for scan in project.session.get_documents_names(COLLECTION_CURRENT):
                        if scan in str(sub_value):
                            value_scan = scan
                    if value_scan is not None:
                        button = QPushButton(value_scan)
                        button.clicked.connect(self.file_clicked)
                        sub_layout.addWidget(button)
                    else:
                        label = QLabel(str(sub_value))
                        sub_layout.addWidget(label)
                widget.setLayout(sub_layout)
                table.setCellWidget(0, column, widget)
            else:
                item = QTableWidgetItem()
                item.setText(str(value))
                table.setItem(0, column, item)
            column += 1

        table.verticalHeader().setMinimumSectionSize(30)
        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        layout.addWidget(table)

        self.setLayout(layout)

        screen_resolution = QApplication.instance().desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setMinimumHeight(0.5 * height)
        self.setMinimumWidth(0.8 * width)

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