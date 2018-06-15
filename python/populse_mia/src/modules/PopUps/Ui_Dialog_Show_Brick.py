from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QTableWidgetItem

from Project.Project import COLLECTION_BRICK, BRICK_NAME, BRICK_EXEC, BRICK_EXEC_TIME, BRICK_INIT, BRICK_INIT_TIME, \
    BRICK_INPUTS, BRICK_OUTPUTS


class Ui_Dialog_Show_Brick(QDialog):
    """
    Class to display the brick history
    """

    def __init__(self, project, brick_uuid):
        """
        Prepares the brick history popup
        :param project: project
        :param brick_uuid: brick to display
        """

        super().__init__()

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
                row = 0
                for sub_value in value:
                    current_rows = table.rowCount()
                    if row >= current_rows:
                        table.setRowCount(current_rows + 1)
                    item = QTableWidgetItem()
                    item.setText(str(sub_value))
                    table.setItem(row, column, item)
                    row += 1
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
                row = 0
                for sub_value in value:
                    current_rows = table.rowCount()
                    if row >= current_rows:
                        table.setRowCount(current_rows + 1)
                    item = QTableWidgetItem()
                    item.setText(str(sub_value))
                    table.setItem(row, column, item)
                    row += 1
            else:
                item = QTableWidgetItem()
                item.setText(str(value))
                table.setItem(0, column, item)
            column += 1

        table.resizeColumnsToContents()
        layout.addWidget(table)

        self.setLayout(layout)
        self.setMinimumHeight(700)
        self.setMinimumWidth(1200)