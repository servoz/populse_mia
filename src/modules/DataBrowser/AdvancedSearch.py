from PyQt5.QtWidgets import QWidget, QGridLayout, QComboBox, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObjectCleanupHandler
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

        rowLayout = []

        notChoice = QComboBox()
        notChoice.setObjectName('not')
        notChoice.addItem("")
        notChoice.addItem("NOT")

        fieldChoice = QComboBox()
        fieldChoice.setObjectName('field')
        for tag in self.database.getVisualizedTags():
            fieldChoice.addItem(tag.tag)
        fieldChoice.addItem("All visualized tags")

        conditionValue = QLineEdit()
        conditionValue.setObjectName('value')

        conditionChoice = QComboBox()
        conditionChoice.setObjectName('condition')
        conditionChoice.addItem("=")
        conditionChoice.addItem("!=")
        conditionChoice.addItem(">=")
        conditionChoice.addItem("<=")
        conditionChoice.addItem(">")
        conditionChoice.addItem("<")
        conditionChoice.addItem("BETWEEN")
        conditionChoice.addItem("IN")
        conditionChoice.addItem("CONTAINS")
        conditionChoice.currentTextChanged.connect(lambda : self.displayValueRules(conditionChoice, conditionValue))



        removeRowLabel = ClickableLabel()
        removeRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        removeRowPicture = removeRowPicture.scaledToHeight(30)
        removeRowLabel.setPixmap(removeRowPicture)

        rowLayout.append(None)
        rowLayout.append(notChoice)
        rowLayout.append(fieldChoice)
        rowLayout.append(conditionChoice)
        rowLayout.append(conditionValue)
        rowLayout.append(removeRowLabel)
        rowLayout.append(None)

        removeRowLabel.clicked.connect(lambda: self.remove_row(rowLayout))

        self.rows.append(rowLayout)

        self.refresh_search()

    def displayValueRules(self, choice, value):
        if(choice.currentText() == "BETWEEN"):
            value.setPlaceholderText("Please separate the two inclusive borders of the range by a comma and a space")
        elif (choice.currentText() == "IN"):
            value.setPlaceholderText("Please separate each list item by a comma and a space")
        else:
            value.setPlaceholderText("")

    def refresh_search(self):

        self.clearLayout(self.layout())
        QObjectCleanupHandler().add(self.layout())

        i = 0
        while i < len(self.rows):
            # Plus removed from every row
            if(self.rows[i][6] != None):
                self.rows[i][6].setParent(None)
                self.rows[i][6].deleteLater()
                self.rows[i][6] = None
            # Link removed from every row
            if (self.rows[i][0] != None):
                self.rows[i][0].setParent(None)
                self.rows[i][0].deleteLater()
                self.rows[i][0] = None
            i = i + 1

        #Plus added to the last row
        addRowLabel = ClickableLabel()
        addRowLabel.setObjectName('plus')
        addRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        addRowPicture = addRowPicture.scaledToHeight(20)
        addRowLabel.setPixmap(addRowPicture)
        addRowLabel.clicked.connect(self.add_row)
        self.rows[len(self.rows) - 1][6] = addRowLabel

        i = 1
        while i < len(self.rows):
            row = self.rows[i]
            linkChoice = QComboBox()
            linkChoice.setObjectName('link')
            linkChoice.addItem("AND")
            linkChoice.addItem("OR")
            row[0] = linkChoice
            i = i + 1

        master_layout = QVBoxLayout()
        main_layout = QGridLayout()

        i = 0
        while i < len(self.rows):
            j = 0
            while j < 7:
                widget = self.rows[i][j]
                if(widget != None):
                    main_layout.addWidget(widget, i, j)
                j = j + 1
            i = i + 1

        #Search button added at the end
        searchLayout = QHBoxLayout(None)
        searchLayout.setObjectName("search layout")
        search = QPushButton("Search")
        search.setFixedWidth(100)
        search.clicked.connect(self.launch_search)
        searchLayout.addWidget(search)
        searchLayout.setParent(None)

        master_layout.addLayout(main_layout)
        master_layout.addLayout(searchLayout)

        self.setLayout(master_layout)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None and not self.rowsContainsWidget(widget):
                    pass
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def rowsContainsWidget(self, widget):
        for row in self.rows:
            if(widget in row):
                return True
        return False

    def launch_search(self):
        fields = []
        conditions = []
        values = []
        links = []
        nots = []
        for row in self.rows:
            for widget in row:
                if widget != None:
                    child = widget
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
        result = self.database.getScansAdvancedSearch(links, fields, conditions, values, nots)
        self.dataBrowser.table_data.scans_to_visualize = result
        self.dataBrowser.table_data.update_table()