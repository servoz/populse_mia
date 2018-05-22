from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal

class ClickableLabel(QLabel):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    # Signal that will be emitted at the end to tell that the project has been created
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        self.clicked.emit()