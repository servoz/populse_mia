from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog, QApplication
import DataBrowser.DataBrowser
from Project.Project import TAG_FILENAME


class Ui_DataBrowser_Current_Selection(QDialog):
    """
    Is called to display the current DataBrowser selection
    """

    def __init__(self, project, databrowser, filter, main_window):

        super().__init__()
        self.project = project
        self.databrowser = databrowser
        self.filter = filter
        self.main_window = main_window
        self.setWindowTitle("Confirm the selection")
        self.setModal(True)

        vbox_layout = QVBoxLayout()

        # Adding databrowser table
        databrowser_table = DataBrowser.DataBrowser.TableDataBrowser(self.project, self.databrowser, [TAG_FILENAME], False, False)
        old_scan_list = databrowser_table.scans_to_visualize
        databrowser_table.scans_to_visualize = self.filter
        databrowser_table.update_visualized_rows(old_scan_list)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        vbox_layout.addWidget(databrowser_table)
        vbox_layout.addWidget(buttons)
        buttons.accepted.connect(self.ok_clicked)
        buttons.rejected.connect(self.close)
        self.setLayout(vbox_layout)
        screen_resolution = QApplication.instance().desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setMinimumWidth(0.5 * width)
        self.setMinimumHeight(0.8 * height)

    def ok_clicked(self):
        """
        Called when ok is clicked
        """

        self.main_window.pipeline_manager.scan_list = self.filter
        self.main_window.pipeline_manager.nodeController.scan_list = self.filter
        self.main_window.pipeline_manager.pipelineEditorTabs.scan_list = self.filter
        self.close()