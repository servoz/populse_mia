from PyQt5 import QtWidgets, QtCore
from PopUps.Ui_Tag_Selection import Ui_Tag_Selection

from Project.Project import TAG_CHECKSUM, COLLECTION_CURRENT


class Ui_Select_Tag_Count_Table(Ui_Tag_Selection):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    def __init__(self, project, tags_to_display, tag_name_checked=None):
        super(Ui_Select_Tag_Count_Table, self).__init__(project)

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
        self.selected_tag = None
        for idx in range(self.list_widget_tags.count()):
            item = self.list_widget_tags.item(idx)
            if item.checkState() == QtCore.Qt.Checked:
                self.selected_tag = item.text()
                break

        self.accept()
        self.close()

