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
from populse_mia.pop_ups.pop_up_tag_selection import PopUpTagSelection
from populse_mia.project.project import TAG_CHECKSUM


class PopUpSelectTagCountTable(PopUpTagSelection):
    """
    Is called when the user wants to update a visualized tag of the count table

    Attributes:
        - selected_tag: the selected tag

    Methods:
        - ok_clicked: updates the selected tag and closes the pop-up
    """

    def __init__(self, project, tags_to_display, tag_name_checked=None):
        super(PopUpSelectTagCountTable, self).__init__(project)

        self.selected_tag = None
        for tag in tags_to_display:
            if tag != TAG_CHECKSUM:
                item = QtWidgets.QListWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                if tag == tag_name_checked:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                self.list_widget_tags.addItem(item)
                item.setText(tag)
        self.list_widget_tags.sortItems()

    def ok_clicked(self):
        """
        Updates the selected tag and closes the pop-up
        """
        for idx in range(self.list_widget_tags.count()):
            item = self.list_widget_tags.item(idx)
            if item.checkState() == QtCore.Qt.Checked:
                self.selected_tag = item.text()
                break

        self.accept()
        self.close()

