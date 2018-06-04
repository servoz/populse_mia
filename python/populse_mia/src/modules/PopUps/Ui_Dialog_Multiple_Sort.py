from PyQt5.QtWidgets import QHBoxLayout, QDialog, QPushButton, QLabel, QComboBox, QVBoxLayout
from PyQt5.QtGui import QPixmap
import os
from PopUps.Ui_Select_Tag_Count_Table import Ui_Select_Tag_Count_Table
from Utils.Tools import ClickableLabel

class Ui_Dialog_Multiple_Sort(QDialog):
    def __init__(self, project=None):
        super().__init__()
        self.project = project

        # values_list will contain the different values of each selected tag
        self.values_list = [[], []]
        self.list_tags = []

        self.label_tags = QLabel('Tags: ')

        # Each push button will allow the user to add a tag to the count table
        push_button_tag_1 = QPushButton()
        push_button_tag_1.setText("Tag n°1")
        push_button_tag_1.clicked.connect(lambda: self.select_tag(0))

        push_button_tag_2 = QPushButton()
        push_button_tag_2.setText("Tag n°2")
        push_button_tag_2.clicked.connect(lambda: self.select_tag(1))

        # The list of all the push buttons (the user can add as many as he or she wants)
        self.push_buttons = []
        self.push_buttons.insert(0, push_button_tag_1)
        self.push_buttons.insert(1, push_button_tag_2)

        # Labels to add/remove a tag (a push button)
        self.remove_tag_label = ClickableLabel()
        remove_tag_picture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "red_minus.png")))
        remove_tag_picture = remove_tag_picture.scaledToHeight(20)
        self.remove_tag_label.setPixmap(remove_tag_picture)
        self.remove_tag_label.clicked.connect(self.remove_tag)

        self.add_tag_label = ClickableLabel()
        self.add_tag_label.setObjectName('plus')
        add_tag_picture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        add_tag_picture = add_tag_picture.scaledToHeight(15)
        self.add_tag_label.setPixmap(add_tag_picture)
        self.add_tag_label.clicked.connect(self.add_tag)

        # Combobox to choose if the sort order is ascending or descending
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Ascending", "Descending"])

        # Push button that is pressed to launch the computations
        self.push_button_sort = QPushButton()
        self.push_button_sort.setText('Sort scans')
        self.push_button_sort.clicked.connect(self.sort_scans)

        # Layouts
        self.v_box_final = QVBoxLayout()
        self.setLayout(self.v_box_final)
        self.refresh_layout()

    def refresh_layout(self):
        """ Methods that update the layouts (especially when a tag push button
        is added or removed. """
        self.h_box_top = QHBoxLayout()
        self.h_box_top.setSpacing(10)
        self.h_box_top.addWidget(self.label_tags)

        for tag_label in self.push_buttons:
            self.h_box_top.addWidget(tag_label)

        self.h_box_top.addWidget(self.add_tag_label)
        self.h_box_top.addWidget(self.remove_tag_label)
        self.h_box_top.addWidget(self.combo_box)
        self.h_box_top.addWidget(self.push_button_sort)
        self.h_box_top.addStretch(1)

        self.v_box_final.addLayout(self.h_box_top)

    def add_tag(self):
        """ Method that adds a push button. """
        push_button = QPushButton()
        push_button.setText('Tag n°' + str(len(self.push_buttons) + 1))
        push_button.clicked.connect(lambda: self.select_tag(len(self.push_buttons) - 1))
        self.push_buttons.insert(len(self.push_buttons), push_button)
        self.refresh_layout()

    def remove_tag(self):
        """ Method that removes a push buttons and makes the changes
        in the list of values. """
        push_button = self.push_buttons[-1]
        push_button.deleteLater()
        push_button = None
        del self.push_buttons[-1]
        del self.values_list[-1]
        self.refresh_layout()

    def select_tag(self, idx):
        """ Method that calls a pop-up to choose a tag. """
        popUp = Ui_Select_Tag_Count_Table(self.project, self.push_buttons[idx].text(), visualized_tags_only=True)
        if popUp.exec_():
            self.push_buttons[idx].setText(popUp.selected_tag)
            self.fill_values(idx)

    def fill_values(self, idx):
        """ Method that fills the values list when a tag is added
        or removed. """
        tag_name = self.push_buttons[idx].text()
        if len(self.values_list) <= idx:
            self.values_list.insert(idx, [])
        if self.values_list[idx] is not None:
            self.values_list[idx] = []
        for scan in self.project.database.get_fields_names():
            current_value = self.project.database.get_value(scan, tag_name)
            if current_value not in self.values_list[idx]:
                self.values_list[idx].append(current_value)

    def sort_scans(self):
        self.order = self.combo_box.itemText(self.combo_box.currentIndex())
        for push_button in self.push_buttons:
            self.list_tags.append(push_button.text())
        self.accept()
