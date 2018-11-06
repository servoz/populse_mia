##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5.QtWidgets import QVBoxLayout, QDialogButtonBox, QDialog, QApplication

# Populse_MIA imports
from populse_mia.data_browser import data_browser
from populse_mia.project.project import TAG_FILENAME


class PopUpDataBrowserCurrentSelection(QDialog):
    """
    Is called to display the current data_browser selection

    Attributes:
        - project: current project in the software
        - databrowser: data browser instance of the software
        - filter: list of the current documents in the data browser
        - main_window: main window of the software

    Methods:
        - ok_clicked: updates the "scan_list" attribute of several widgets
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
        databrowser_table = data_browser.TableDataBrowser(self.project, self.databrowser,
                                                                       [TAG_FILENAME], False, False)
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
        Updates the "scan_list" attribute of several widgets
        """

        self.main_window.pipeline_manager.scan_list = self.filter
        self.main_window.pipeline_manager.nodeController.scan_list = self.filter
        self.main_window.pipeline_manager.pipelineEditorTabs.scan_list = self.filter
        self.close()
