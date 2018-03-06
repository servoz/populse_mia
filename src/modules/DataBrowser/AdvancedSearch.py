from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
import os

class AdvancedSearch(QWidget):

    def __init__(self, database):

        super().__init__()

        self.database = database

        self.vLayout = QVBoxLayout()
        self.setLayout(self.vLayout)

        #First row
        self.hLayout = QHBoxLayout()

        self.fieldChoice = QComboBox()
        for tag in self.database.getVisualizedTags():
            self.fieldChoice.addItem(tag.tag)
        self.fieldChoice.addItem("All visualized tags")

        self.conditionChoice = QComboBox()
        self.conditionChoice.addItem("==")
        self.conditionChoice.addItem("!=")
        self.conditionChoice.addItem(">=")
        self.conditionChoice.addItem("<=")
        self.conditionChoice.addItem("<")
        self.conditionChoice.addItem(">")
        self.conditionValue = QLineEdit()

        self.removeRowLabel = QLabel()
        self.removeRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        self.removeRowPicture = self.removeRowPicture.scaledToHeight(30)
        self.removeRowLabel.setPixmap(self.removeRowPicture)

        self.addRowLabel = QLabel()
        self.addRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        self.addRowPicture = self.addRowPicture.scaledToHeight(20)
        self.addRowLabel.setPixmap(self.addRowPicture)

        self.hLayout.addWidget(self.fieldChoice)
        self.hLayout.addWidget(self.conditionChoice)
        self.hLayout.addWidget(self.conditionValue)
        self.hLayout.addWidget(self.removeRowLabel)
        self.hLayout.addWidget(self.addRowLabel)

        self.vLayout.addLayout(self.hLayout)

        self.search = QPushButton("Search")
        self.search.setFixedWidth(100)
        self.vLayout.addWidget(self.search)

