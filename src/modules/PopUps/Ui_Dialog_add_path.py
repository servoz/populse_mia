from PyQt5.QtWidgets import QDialog

class Ui_Dialog_add_path(QDialog):
    """
    Is called when the user wants to add a path to the project
    """

    def __init__(self, project):
        super().__init__()
        self.project = project
        self.setWindowTitle("Add a path")