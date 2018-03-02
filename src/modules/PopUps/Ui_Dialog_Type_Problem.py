from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QPushButton, QLabel


class Ui_Dialog_Type_Problem(QDialog):
    """
    Is called when the user changes a value that is not in the right type
    """
    ok_signal = pyqtSignal()

    def __init__(self, tp):
        super().__init__()

        self.setWindowTitle("Type error")

        label = QLabel(self)
        label.setText('This value should be of type ' + tp)

        push_button_ok = QPushButton("OK", self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(push_button_ok)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        push_button_ok.clicked.connect(self.ok_clicked)

    def ok_clicked(self):
        self.ok_signal.emit()
        self.close()


