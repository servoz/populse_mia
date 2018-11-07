##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5 import QtWidgets, QtCore

# Populse_MIA imports
from populse_mia.software_properties.config import Config
from populse_mia.pop_ups.pop_up_tag_selection import PopUpTagSelection
from populse_mia.project.project import COLLECTION_CURRENT, TAG_CHECKSUM


class PopUpSelectTag(PopUpTagSelection):
    """
    Is called when the user wants to update the tag to display in the mini viewer

    Attributes:
        - project: current project in the software
        - config: current config of the software

    Methods:
        - ok_clicked: saves the modifications and updates the mini viewer
    """

    def __init__(self, project):
        super(PopUpSelectTag, self).__init__(project)
        self.project = project
        self.config = Config()

        # Filling the list and checking the thumbnail tag
        for tag in self.project.session.get_fields_names(COLLECTION_CURRENT):
            if tag != TAG_CHECKSUM:
                item = QtWidgets.QListWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                if tag == self.config.getThumbnailTag():
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                self.list_widget_tags.addItem(item)
                item.setText(tag)
        self.list_widget_tags.sortItems()

    def ok_clicked(self):
        """
        Saves the modifications and updates the mini viewer
        """
        for idx in range(self.list_widget_tags.count()):
            item = self.list_widget_tags.item(idx)
            if item.checkState() == QtCore.Qt.Checked:
                self.config.setThumbnailTag(item.text())
                break

        self.accept()
        self.close()
