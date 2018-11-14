##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5 import QtWidgets

# Populse_MIA imports
from populse_mia.software_properties.config import Config
from populse_mia.pop_ups.pop_up_filter_selection import PopUpFilterSelection


class PopUpSelectFilter(PopUpFilterSelection):
    """
    Is called when the user wants to open a filter that has already been saved

    Attributes:
        - project: current project in the software
        - databrowser: data browser instance of the software
        - config: current config of the software

    Methods:
        - ok_clicked: saves the modifications and updates the data browser
    """

    def __init__(self, project, databrowser):
        super(PopUpSelectFilter, self).__init__(project)
        self.project = project
        self.databrowser = databrowser
        self.config = Config()
        self.setWindowTitle("Open a filter")

        # Filling the filter list
        for filter in self.project.filters:
            item = QtWidgets.QListWidgetItem()
            self.list_widget_filters.addItem(item)
            item.setText(filter.name)

    def ok_clicked(self):
        """
        Saves the modifications and updates the data browser
        """
        for item in self.list_widget_filters.selectedItems():

            # Current filter updated
            filter_name = item.text()
            filter_object = self.project.getFilter(filter_name)
            self.project.setCurrentFilter(filter_object)
            break

        self.databrowser.open_filter_infos()

        self.accept()
        self.close()
