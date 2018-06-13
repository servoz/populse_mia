from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog
import DataBrowser.DataBrowser

class Ui_DataBrowser_Current_Selection(QDialog):
    """
    Is called to display the current DataBrowser selection
    """

    def __init__(self, project, databrowser, filter):

        super().__init__()
        self.project = project
        self.databrowser = databrowser
        self.filter = filter
        self.setWindowTitle("Confirm the selection")

        vbox_layout = QVBoxLayout()

        # Adding databrowser table
        databrowser_table = DataBrowser.DataBrowser.TableDataBrowser(self.project, self.databrowser, False, False)
        old_scan_list = databrowser_table.scans_to_visualize
        databrowser_table.scans_to_visualize = self.filter
        databrowser_table.update_visualized_rows(old_scan_list)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox_layout.addWidget(databrowser_table)
        vbox_layout.addWidget(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.setLayout(vbox_layout)

        self.setMinimumWidth(1000)
        self.setMinimumHeight(1000)