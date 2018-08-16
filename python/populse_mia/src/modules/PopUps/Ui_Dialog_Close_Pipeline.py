from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QPushButton, QLabel


class Ui_Dialog_Close_Pipeline(QDialog):
    """
    Is called when the user closes a pipeline and it has been modified
    """

    save_as_signal = pyqtSignal()
    do_not_save_signal = pyqtSignal()
    cancel_signal = pyqtSignal()

    def __init__(self, pipeline_name):
        super().__init__()

        #self.setModal(True)

        self.pipeline_name = pipeline_name

        self.bool_exit = False
        self.bool_save_as = False

        self.setWindowTitle("Confirm pipeline closing")

        label = QLabel(self)
        label.setText('Do you want to close the pipeline without saving ' + self.pipeline_name + '?')

        self.push_button_save_as = QPushButton("Save", self)
        self.push_button_do_not_save = QPushButton("Do not save", self)
        self.push_button_cancel = QPushButton("Cancel", self)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.push_button_save_as)
        hbox.addWidget(self.push_button_do_not_save)
        hbox.addWidget(self.push_button_cancel)
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.push_button_save_as.clicked.connect(self.save_as_clicked)
        self.push_button_do_not_save.clicked.connect(self.do_not_save_clicked)
        self.push_button_cancel.clicked.connect(self.cancel_clicked)

    def save_as_clicked(self):
        self.save_as_signal.emit()
        self.bool_save_as = True
        self.bool_exit = True
        self.close()

    def do_not_save_clicked(self):
        self.bool_exit = True
        self.close()

    def cancel_clicked(self):
        self.bool_exit = False
        self.close()

    def can_exit(self):
        return self.bool_exit
