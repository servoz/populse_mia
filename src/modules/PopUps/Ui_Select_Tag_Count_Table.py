from PyQt5 import QtWidgets, QtCore
from PopUps.Ui_Tag_Selection import Ui_Tag_Selection


class Ui_Select_Tag_Count_Table(Ui_Tag_Selection):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    def __init__(self, database, tag_name_checked=None):
        super(Ui_Select_Tag_Count_Table, self).__init__(database)

        # Filling the list and checking the previous selected tag
        for tag in self.database.getTags():
            item = QtWidgets.QListWidgetItem()
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if tag.tag == tag_name_checked:
                item.setCheckState(QtCore.Qt.Checked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
            self.list_widget_tags.addItem(item)
            item.setText(tag.tag)

    def ok_clicked(self):
        for idx in range(self.list_widget_tags.count()):
            item = self.list_widget_tags.item(idx)
            if item.checkState() == QtCore.Qt.Checked:
                self.selected_tag = item.text()
                break

        self.accept()
        self.close()

