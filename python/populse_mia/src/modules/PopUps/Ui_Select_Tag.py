from PyQt5 import QtWidgets, QtCore
from SoftwareProperties.Config import Config
from PopUps.Ui_Tag_Selection import Ui_Tag_Selection

class Ui_Select_Tag(Ui_Tag_Selection):
    """
    Is called when the user wants to update the tags that are visualized in the data browser
    """

    def __init__(self, project):
        super(Ui_Select_Tag, self).__init__(project)
        self.project = project
        self.config = Config()

        # Filling the list and checking the thumbnail tag
        for tag in self.project.database.get_tags_names():
            if tag != "Checksum":
                item = QtWidgets.QListWidgetItem()
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                if tag == self.config.getThumbnailTag():
                    item.setCheckState(QtCore.Qt.Checked)
                else:
                    item.setCheckState(QtCore.Qt.Unchecked)
                self.list_widget_tags.addItem(item)
                item.setText(tag)

    def ok_clicked(self):
        for idx in range(self.list_widget_tags.count()):
            item = self.list_widget_tags.item(idx)
            if item.checkState() == QtCore.Qt.Checked:
                self.config.setThumbnailTag(item.text())
                break

        self.accept()
        self.close()
