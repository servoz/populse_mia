from PyQt5 import QtWidgets, QtCore
from PopUps.Ui_Tag_Selection import Ui_Tag_Selection

from Project.Project import TAG_CHECKSUM, COLLECTION_CURRENT

class Ui_Select_Tag_Count_Table(Ui_Tag_Selection):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    def __init__(self, project, tag_name_checked=None, visualized_tags_only=False):
        super(Ui_Select_Tag_Count_Table, self).__init__(project)

        if visualized_tags_only:
            for tag in self.project.getVisibles():
                item = QtWidgets.QListWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                if tag == tag_name_checked:
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                self.list_widget_tags.addItem(item)
                item.setText(tag)

        else:
            # Filling the list and checking the previous selected tag
            tags = self.project.database.get_fields_names(COLLECTION_CURRENT)
            tags.remove(TAG_CHECKSUM)
            for tag in tags:
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
        for idx in range(self.list_widget_tags.count()):
            item = self.list_widget_tags.item(idx)
            if item.checkState() == QtCore.Qt.Checked:
                self.selected_tag = item.text()
                break

        self.accept()
        self.close()

