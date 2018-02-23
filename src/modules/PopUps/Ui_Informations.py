from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout


class Ui_Informations(QWidget):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_preferences_change = pyqtSignal()

    def __init__(self, project, database):
        super().__init__()
        self.retranslate_Ui(project, database)

    def retranslate_Ui(self, project, database):
        _translate = QtCore.QCoreApplication.translate

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(3)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Property', 'Value'))

        item = QTableWidgetItem("Name")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem(project.name)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(0, 1, item)

        item = QTableWidgetItem("Folder")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem(database.folder)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(1, 1, item)

        item = QTableWidgetItem("Date of creation")
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(2, 0, item)

        item = QTableWidgetItem(project.date)
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.tableWidget.setItem(2, 1, item)

        self.tableWidget.resizeRowsToContents()
        self.tableWidget.resizeColumnsToContents()

        box = QVBoxLayout()
        box.addWidget(self.tableWidget)

        self.setLayout(box)
