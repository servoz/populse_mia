from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QLabel, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObjectCleanupHandler
import os
from Utils.Tools import ClickableLabel

class AdvancedSearch(QWidget):

    def __init__(self, database):

        super().__init__()

        self.database = database
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

        fieldChoice = QComboBox()
        for tag in self.database.getVisualizedTags():
            fieldChoice.addItem(tag.tag)
        fieldChoice.addItem("All visualized tags")

        conditionChoice = QComboBox()
        conditionChoice.addItem("==")
        conditionChoice.addItem("!=")
        conditionChoice.addItem(">=")
        conditionChoice.addItem("<=")
        conditionChoice.addItem("<")
        conditionChoice.addItem(">")

        conditionValue = QLineEdit()

        removeRowLabel = ClickableLabel()
        removeRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        removeRowPicture = removeRowPicture.scaledToHeight(30)
        removeRowLabel.setPixmap(removeRowPicture)

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

        i = 0
        while i < len(self.rows) - 1:
            if(self.rows[i].count() == 5):
                greenPlus = self.rows[i].takeAt(self.rows[i].count() - 1)
                greenPlusWidget = greenPlus.widget()
                greenPlusWidget.deleteLater()
            i = i + 1

        if (self.rows[len(self.rows) - 1].count() == 4):
            addRowLabel = ClickableLabel()
            addRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
            addRowPicture = addRowPicture.scaledToHeight(20)
            addRowLabel.setPixmap(addRowPicture)
            addRowLabel.clicked.connect(self.add_row)
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
