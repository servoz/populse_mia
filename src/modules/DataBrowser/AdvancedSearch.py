from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObjectCleanupHandler, QObject
import os
from Utils.Tools import ClickableLabel

class AdvancedSearch(QWidget):

    def __init__(self, database, dataBrowser):

        super().__init__()

        self.database = database
        self.dataBrowser = dataBrowser
        self.rows = []

    def show_search(self):

        self.rows = []
        self.add_row()

    def remove_row(self, rowLayout):

        if(len(self.rows) > 1):
            self.rows.remove(rowLayout)

        self.refresh_search()

    def add_row(self):

        rowLayout = QHBoxLayout(None)
        rowLayout.setObjectName("row layout")

        notChoice = QComboBox()
        notChoice.setObjectName('not')
        notChoice.addItem("")
        notChoice.addItem("NOT")

        fieldChoice = QComboBox()
        fieldChoice.setObjectName('field')
        for tag in self.database.getVisualizedTags():
            fieldChoice.addItem(tag.tag)
        fieldChoice.addItem("All visualized tags")

        conditionChoice = QComboBox()
        conditionChoice.setObjectName('condition')
        conditionChoice.addItem("=")
        conditionChoice.addItem("!=")
        conditionChoice.addItem(">=")
        conditionChoice.addItem("<=")
        conditionChoice.addItem("<")
        conditionChoice.addItem(">")
        conditionChoice.addItem("BETWEEN")
        conditionChoice.addItem("IN")
        conditionChoice.addItem("CONTAINS")

        conditionValue = QLineEdit()
        conditionValue.setObjectName('value')

        removeRowLabel = ClickableLabel()
        removeRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        removeRowPicture = removeRowPicture.scaledToHeight(30)
        removeRowLabel.setPixmap(removeRowPicture)

        rowLayout.addWidget(notChoice)
        rowLayout.addWidget(fieldChoice)
        rowLayout.addWidget(conditionChoice)
        rowLayout.addWidget(conditionValue)
        rowLayout.addWidget(removeRowLabel)

        removeRowLabel.clicked.connect(lambda: self.remove_row(rowLayout))

        self.rows.append(rowLayout)

        self.refresh_search()

    def refresh_search(self):

        self.clearLayout(self.layout())
        QObjectCleanupHandler().add(self.layout())

        for row in self.rows:
            # Plus removed from every row
            lastRowWidget = row.itemAt(row.count() - 1).widget()
            lastRowWidgetName = lastRowWidget.objectName()
            if(lastRowWidgetName == "plus"):
                lastRowWidget.deleteLater()
            # Link removed from every row
            firstRowWidget = row.itemAt(0).widget()
            firstRowWidgetName = firstRowWidget.objectName()
            if (firstRowWidgetName == "link"):
                firstRowWidget.deleteLater()

        #Plus added to the last row
        addRowLabel = ClickableLabel()
        addRowLabel.setObjectName('plus')
        addRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        addRowPicture = addRowPicture.scaledToHeight(20)
        addRowLabel.setPixmap(addRowPicture)
        addRowLabel.clicked.connect(self.add_row)

        i = 1
        while i < len(self.rows):
            row = self.rows[i]
            linkChoice = QComboBox()
            linkChoice.setObjectName('link')
            linkChoice.addItem("AND")
            linkChoice.addItem("OR")
            row.insertWidget(0, linkChoice)
            i = i + 1

        self.rows[len(self.rows) - 1].addWidget(addRowLabel)

        main_layout = QVBoxLayout()
        main_layout.setObjectName("main layout")

        i = 0
        for row in self.rows:
            main_layout.insertLayout(i, row)
            row.setParent(main_layout)
            i = i + 1

        #Search button added at the end
        searchLayout = QHBoxLayout(None)
        searchLayout.setObjectName("search layout")
        search = QPushButton("Search")
        search.setFixedWidth(100)
        search.clicked.connect(self.launch_search)
        searchLayout.addWidget(search)
        searchLayout.setParent(None)
        main_layout.insertLayout(i, searchLayout)

        self.setLayout(main_layout)

    def clearLayout(self, layout):
        if layout is not None and not layout in self.rows:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    pass
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def launch_search(self):
        fields = []
        conditions = []
        values = []
        links = []
        nots = []
        for row in self.rows:
            i = 0
            while i < row.count():
                child = row.itemAt(i).widget()
                childName = child.objectName()
                if(childName == 'link'):
                    links.append(child.currentText())
                elif(childName == 'condition'):
                    conditions.append(child.currentText())
                elif (childName == 'field'):
                    fields.append(child.currentText())
                elif (childName == 'value'):
                    values.append(child.displayText())
                elif (childName == 'not'):
                    nots.append(child.currentText())
                i = i + 1
        result = self.database.getScansAdvancedSearch(links, fields, conditions, values, nots)
        self.dataBrowser.table_data.scans_to_visualize = result
        self.dataBrowser.table_data.update_table()