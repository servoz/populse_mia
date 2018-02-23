from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QTableWidget, QHBoxLayout, QSplitter
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QLabel, QScrollArea, QFrame, QToolBar, QToolButton, QAction,\
    QMessageBox, QSlider, QLineEdit, QSizePolicy, QCheckBox, QPushButton
import os
from ProjectManager.controller import save_project
from ProjectManager.models import *

from PopUps.Ui_Dialog_add_tag import Ui_Dialog_add_tag
from PopUps.Ui_Dialog_clone_tag import Ui_Dialog_clone_tag
from PopUps.Ui_Dialog_Type_Problem import Ui_Dialog_Type_Problem
from PopUps.Ui_Dialog_remove_tag import Ui_Dialog_remove_tag
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings

from SoftwareProperties import Config
import scipy.misc as misc

from functools import partial
import nibabel as nib
from scipy.ndimage import rotate  # to work with NumPy arrays
import numpy as np  # a N-dimensional array object
import Utils.utils as utils
from SoftwareProperties.Config import Config

class DataBrowser(QWidget):
    def __init__(self, project):

        super(DataBrowser, self).__init__()

        _translate = QtCore.QCoreApplication.translate
        self.create_actions(project)
        self.create_toolbar_menus(project)

        ################################### TABLE ###################################

        # Frame behind the table
        self.frame_table_data = QtWidgets.QFrame(self)
        self.frame_table_data.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_table_data.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_table_data.setObjectName("frame_table_data")

        # Main table that will display the tags
        self.table_data = TableDataBrowser(project)
        self.table_data.setObjectName("table_data")
        self.table_data.cellClicked.connect(partial(self.connect_viewer, project))

        ## LAYOUTS ##

        hbox_table = QHBoxLayout()
        hbox_table.addWidget(self.table_data)

        self.frame_table_data.setLayout(hbox_table)

        ################################### VISUALIZATION ###################################

        # Visualization frame, label and text edit (bottom left of the screen in the application)
        self.frame_visualization = QtWidgets.QFrame(self)
        self.frame_visualization.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_visualization.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_visualization.setObjectName("frame_5")

        self.viewer = MiniViewer(project)
        self.viewer.setObjectName("viewer")
        self.viewer.adjustSize()

        hbox_viewer = QHBoxLayout()
        hbox_viewer.addWidget(self.viewer)

        self.frame_visualization.setLayout(hbox_viewer)

        ## SPLITTER AND LAYOUT ##

        splitter_vertical = QSplitter(Qt.Vertical)
        splitter_vertical.addWidget(self.frame_table_data)
        splitter_vertical.addWidget(self.frame_visualization)

        vbox_splitter = QVBoxLayout(self)
        vbox_splitter.addWidget(self.menu_toolbar)
        vbox_splitter.addWidget(splitter_vertical)

        self.setLayout(vbox_splitter)

    def create_actions(self, project):
        self.add_tag_action = QAction("Add tag", self, shortcut="Ctrl+A")
        self.add_tag_action.triggered.connect(lambda: self.add_tag_pop_up(project))

        self.clone_tag_action = QAction("Clone tag", self)
        self.clone_tag_action.triggered.connect(lambda: self.clone_tag_pop_up(project))

        self.remove_tag_action = QAction("Remove tag", self, shortcut="Ctrl+R")
        self.remove_tag_action.triggered.connect(lambda: self.remove_tag_pop_up(project))

    def visualized_tags_pop_up(self, project):
        self.pop_up = Ui_Dialog_Settings(project)
        self.pop_up.tab_widget.setCurrentIndex(0)

        self.pop_up.setGeometry(300, 200, 800, 600)
        self.pop_up.show()

        if self.pop_up.exec_() == QDialog.Accepted:
            self.table_data.update_table(project)

    def create_toolbar_menus(self, project):
        self.menu_toolbar = QToolBar()

        tags_tool_button = QToolButton()
        tags_tool_button.setText('Tags')
        tags_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        tags_menu = QMenu()
        tags_menu.addAction(self.add_tag_action)
        tags_menu.addAction(self.clone_tag_action)
        tags_menu.addAction(self.remove_tag_action)
        tags_tool_button.setMenu(tags_menu)

        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(partial(self.search_str, project))

        self.button_cross = QToolButton()
        self.button_cross.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.button_cross.setIcon(QIcon(os.path.join('..', 'sources_images', 'gray_cross.png')))
        self.button_cross.clicked.connect(self.reset_search_bar)

        search_bar_layout = QHBoxLayout()
        search_bar_layout.setSpacing(0)
        search_bar_layout.addWidget(self.search_bar)
        search_bar_layout.addWidget(self.button_cross)

        self.frame_test = QFrame()
        self.frame_test.setLayout(search_bar_layout)

        visualized_tags_button = QPushButton()
        visualized_tags_button.setText('Visualized tags')
        visualized_tags_button.clicked.connect(lambda: self.visualized_tags_pop_up(project))

        self.menu_toolbar.addWidget(tags_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.frame_test)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(visualized_tags_button)

    def search_str(self, project, str_search):
        return_list = []
        if str_search != "":
            split_list = str_search.split('*')
            for scan in project._get_scans():
                for tag in scan.getAllTags():
                    if scan.file_path in return_list:
                        break
                    if tag.name in project.tags_to_visualize:
                        i = 0
                        for element in split_list:
                            if element.upper() in str(tag.value[0]).upper():
                                i += 1
                        if i == len(split_list):
                            return_list.append(scan.file_path)
        else:
            for scan in project._get_scans():
                return_list.append(scan.file_path)


        self.table_data.scans_to_visualize = return_list
        self.table_data.update_table(project)

    def reset_search_bar(self):
        self.search_bar.setText("")

    def connect_viewer(self, project, row, col):
        path_name = os.path.abspath(project.folder)
        file_name = self.table_data.item(row, 0).text() + ".nii"
        full_name = path_name + '/data/raw_data/' + file_name
        self.viewer.show_slices(full_name)

    def add_tag_pop_up(self, project):
        # Ui_Dialog_add_tag() is defined in pop_ups.py
        self.pop_up_add_tag = Ui_Dialog_add_tag(project)
        self.pop_up_add_tag.show()

        if self.pop_up_add_tag.exec_() == QDialog.Accepted:
            (new_tag_name, new_default_value, type) = self.pop_up_add_tag.get_values()

            if type != list:
                list_to_add = []
                list_to_add.append(type(new_default_value))
            else:
                list_to_add = utils.text_to_list(new_default_value)

            new_tag = Tag(new_tag_name, "", list_to_add, "custom", list_to_add)

            # Updating the data base
            project.add_user_tag(new_tag_name, list_to_add)
            project.add_tag(new_tag)
            project.tags_to_visualize.append(new_tag_name)

            # Updating the table
            self.table_data.update_table(project)

    def clone_tag_pop_up(self, project):
        # Ui_Dialog_clone_tag() is defined in pop_ups.py
        self.pop_up_clone_tag = Ui_Dialog_clone_tag(project)
        self.pop_up_clone_tag.show()

        if self.pop_up_clone_tag.exec_() == QDialog.Accepted:
            (tag_to_clone, new_tag_name) = self.pop_up_clone_tag.get_values()

            # Updating the data base
            project.clone_tag(tag_to_clone, new_tag_name)
            project.tags_to_visualize.append(new_tag_name)

            # Updating the table
            self.table_data.update_table(project)

    def remove_tag_pop_up(self, project):
        # Ui_Dialog_remove_tag() is defined in pop_ups.py
        self.pop_up_clone_tag = Ui_Dialog_remove_tag(project)
        self.pop_up_clone_tag.show()

        if self.pop_up_clone_tag.exec_() == QDialog.Accepted:
            tag_names_to_remove = self.pop_up_clone_tag.get_values()

            for tag_name in tag_names_to_remove:
                project.remove_tag_by_name(tag_name)

            self.table_data.update_table(project)


class TableDataBrowser(QTableWidget):

    def __init__(self, project):
        super().__init__()

        # The list of scans to visualize
        self.scans_to_visualize = []
        for scan in project._get_scans():
            self.scans_to_visualize.append(scan.file_path)

        # It allows to move the columns
        self.horizontalHeader().setSectionsMovable(True)

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.context_menu_table, project))
        self.flag_first_time = 0
        self.hh = self.horizontalHeader()
        self.hh.sectionClicked.connect(partial(self.selectAllColumn))
        self.hh.sectionDoubleClicked.connect(partial(self.sort_items, project))

        if project:
            self.update_table(project)

    def selectAllColumn(self, col):
        self.selectColumn(col)

    def update_table(self, project):
        """
        This method will fill the tables in the 'Table' tab with the project data
        """

        project.sort_by_tags()
        self.flag_first_time += 1

        if self.flag_first_time > 1:
            self.itemChanged.disconnect()

        self.nb_columns = len(project.tags_to_visualize) # Read from MIA2 preferences

        self.nb_rows = len(self.scans_to_visualize)
        self.setRowCount(self.nb_rows)

        self.setColumnCount(self.nb_columns)

        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color:rgb(255, 255, 255); background-color:rgb(250, 250, 250);")

        _translate = QtCore.QCoreApplication.translate

        # Initializing the headers for each row and each column
        item = QtWidgets.QTableWidgetItem()
        i = 0
        while i <= self.nb_columns:
            self.setHorizontalHeaderItem(i, item)
            item = QtWidgets.QTableWidgetItem()
            i += 1

        # Initializing each cell of the table
        row = (-1)

        while row < self.nb_rows:
            row += 1
            column = 0
            while column <= self.nb_columns:
                item = QtWidgets.QTableWidgetItem()
                self.setItem(row, column, item)
                column += 1

        nb = 0
        for element in project.tags_to_visualize:
            element = str(element)
            item = self.horizontalHeaderItem(nb)
            if element == project.sort_tags[0]:
                if project.sort_order == 'ascending':
                    item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))
                else:
                    item.setIcon(QIcon(os.path.join('..', 'sources_images', 'up_arrow.png')))
            item.setText(_translate("MainWindow", element))
            self.setHorizontalHeaderItem(nb, item)
            nb += 1

        # Filling all the cells
        y = -1
        # Loop on the scans

        for file in project._get_scans():

            if file.file_path in self.scans_to_visualize:

                y += 1
                i = -1

                # Loop on the selected tags
                for tag_name in project.tags_to_visualize:
                    i += 1
                    # If the tag belong to the tags of the project (of course it does...)
                    if tag_name in file.getAllTagsNames():
                        # Loop on the project tags
                        for n_tag in file._get_tags():
                            # If a project tag name matches our tag
                            if n_tag.name == tag_name:
                                # It is put in the table
                                item = QTableWidgetItem()
                                txt = utils.check_tag_value(n_tag, 'value')
                                item.setText(txt)

                                if tag_name == "FileName":
                                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                                # If this tag has been added by the user
                                if n_tag.origin == "custom":
                                    color = QColor()
                                    if y % 2 == 1:
                                        color.setRgb(255, 240, 240)
                                    else:
                                        color.setRgb(255, 225, 225)
                                    item.setData(Qt.BackgroundRole, QVariant(color))
                                else:
                                    if utils.compare_values(n_tag) == False:
                                        txt = utils.check_tag_value(n_tag, 'original_value')
                                        item.setToolTip("Original value: " + txt)
                                        color = QColor()
                                        if y % 2 == 1:
                                            color.setRgb(240, 240, 255)
                                        else:
                                            color.setRgb(225, 225, 255)
                                        item.setData(Qt.BackgroundRole, QVariant(color))
                                self.setItem(y, i, item)
                    else:
                        a = str('NaN')
                        item = QTableWidgetItem()
                        item.setText(a)
                        self.setItem(y, i, item)



        ######

        self.resizeColumnsToContents()

        # When the user changes one item of the table, the background will change
        self.itemChanged.connect(partial(self.change_cell_color, project))

        config = Config()
        if (config.isAutoSave() == "yes" and not project.name == ""):
            save_project(project)

    def context_menu_table(self, project, position):

        self.hh.disconnect()

        self.flag_first_time += 1

        menu = QMenu(self)

        action_reset_cell = menu.addAction("Reset cell(s)")
        action_reset_column = menu.addAction("Reset column(s)")
        action_reset_row = menu.addAction("Reset row(s)")
        action_remove_scan = menu.addAction("Remove scan")
        action_sort_column = menu.addAction("Sort column")
        action_sort_column_descending = menu.addAction("Sort column (descending)")
        action_visualized_tags = menu.addAction("Visualized tags")

        action = menu.exec_(self.mapToGlobal(position))
        nb_cells = len(self.selectedIndexes())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)

        if action == action_reset_cell:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.reset_cell(project))
            msg.exec()
            self.reset_cell(project)
        elif action == action_reset_column:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.reset_column(project))
            msg.exec()
        elif action == action_reset_row:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.reset_row(project))
            msg.exec()
        elif action == action_remove_scan:
            msg.setText("You are about to remove a scan from the project.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.remove_scan(project))
            msg.exec()
        elif action == action_sort_column:
            self.sort_column(project)
        elif action == action_sort_column_descending:
            self.sort_column_descending(project)
        elif action == action_visualized_tags:
            self.visualized_tags_pop_up(project)

        self.update_table(project)
        self.hh.sectionClicked.connect(partial(self.sort_items, project))

    def reset_cell(self, project):
        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()
            for file in project._get_scans():
                if file.file_path == scan_name:
                    for n_tag in file._get_tags():
                        if n_tag.name == tag_name:
                            txt = utils.check_tag_value(n_tag, 'original_value')
                            self.item(row, col).setText(txt)
                            if n_tag.origin != "custom":
                                color = QColor()
                                if row % 2 == 1:
                                    color.setRgb(255, 255, 255)
                                else:
                                    color.setRgb(250, 250, 250)
                                self.item(row, col).setData(Qt.BackgroundRole, QVariant(color))
                            n_tag.resetTag()

    def reset_column(self, project):
        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_id = -1
            for file in project._get_scans():
                scan_id += 1
                for n_tag in file._get_tags():
                    if n_tag.name == tag_name:
                        txt = utils.check_tag_value(n_tag, 'original_value')
                        self.item(scan_id, col).setText(txt)
                        if n_tag.origin != "custom":
                            color = QColor()
                            if row % 2 == 1:
                                color.setRgb(255, 255, 255)
                            else:
                                color.setRgb(250, 250, 250)
                            self.item(scan_id, col).setData(Qt.BackgroundRole, QVariant(color))
                        n_tag.resetTag()

    def reset_row(self, project):
        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            scan_name = self.item(row, 0).text()
            for file in project._get_scans():
                if file.file_path == scan_name:
                    for n_tag in file.getAllTags():
                        if n_tag.name in project.tags_to_visualize:
                            idx = project.tags_to_visualize.index(n_tag.name)
                            txt = utils.check_tag_value(n_tag, 'original_value')
                            self.item(row, idx).setText(txt)
                            if n_tag.origin != "custom":
                                color = QColor()
                                if row % 2 == 1:
                                    color.setRgb(255, 255, 255)
                                else:
                                    color.setRgb(250, 250, 250)
                                self.item(row, idx).setData(Qt.BackgroundRole, QVariant(color))
                            n_tag.resetTag()

    def reset_cells_with_item(self, project, items_in):
        for item_in in items_in:
            row = item_in.row()
            col = item_in.column()

            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()

            for scan in project._get_scans():
                if scan_path == scan.file_path:
                    for tag in scan.getAllTags():
                        if tag_name == tag.name:
                            # It is put in the table
                            item = QTableWidgetItem()
                            txt = utils.check_tag_value(tag, 'value')
                            if tag.origin == 'custom':
                                color = QColor()
                                if row % 2 == 1:
                                    color.setRgb(255, 240, 240)
                                else:
                                    color.setRgb(255, 225, 225)
                                item.setData(Qt.BackgroundRole, QVariant(color))
                            item.setText(txt)
                            self.setItem(row, col, item)

    def remove_scan(self, project):
        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            scan_path = self.item(row, 0).text()
            for scan in project._get_scans():
                if scan_path == scan.file_path:
                    project.remove_scan(scan_path)

    def sort_items(self, project, col):
        item = self.horizontalHeaderItem(col)
        tag_name = self.horizontalHeaderItem(col).text()
        if tag_name == project.sort_tags[0]:
            if project.sort_order == 'ascending':
                project.sort_order = 'descending'
                item.setIcon(QIcon(os.path.join('..', 'sources_images', 'up_arrow.png')))
            else:
                project.sort_order = 'ascending'
                item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))
        else:
            project.sort_order = 'ascending'
            item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))

        project.reset_sort_tags()
        project.add_sort_tag(tag_name)
        self.update_table(project)

    def sort_column(self, project):
        points = self.selectedItems()

        project.sort_order = "ascending"
        project.reset_sort_tags()

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            project.add_sort_tag(tag_name)

    def sort_column_descending(self, project):
        points = self.selectedItems()

        project.sort_order = "descending"
        project.reset_sort_tags()

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            project.add_sort_tag(tag_name)

    def visualized_tags_pop_up(self, project):
        self.pop_up = Ui_Dialog_Settings(project)
        self.pop_up.tab_widget.setCurrentIndex(0)

        self.pop_up.setGeometry(300, 200, 800, 600)
        self.pop_up.show()

        if self.pop_up.exec_() == QDialog.Accepted:
            self.update_table(project)

    def change_cell_color(self, project, item_origin):
        """
        The background color of the table will change when the user changes an item
        Handles the multi-selection case
        :return:
        """

        self.itemChanged.disconnect()
        text_value = item_origin.text()
        is_error = False
        for item in self.selectedItems():
            if is_error:
                break
            row = item.row()
            col = item.column()
            tp = str
            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()

            for scan in project._get_scans():
                if scan_path == scan.file_path:
                    for tag in scan.getAllTags():
                        if tag_name == tag.name:
                            tp = type(tag.original_value[0])
            try:
                """# TODO: THIS HAVE TO BE IMPROVE (CHECK EACH VALUE OF THE WRITTEN LIST)
                if tp == list and (text_value[0] != '[' or text_value[-1] != ']'):
                    is_error = True"""
                test = tp(text_value)

            except ValueError:
                is_error = True

        if is_error:
            items = self.selectedItems()

            # Dialog that says that it is not possible
            self.pop_up_type = Ui_Dialog_Type_Problem(tp)
            # Resetting the cells
            self.pop_up_type.ok_signal.connect(partial(self.reset_cells_with_item, project, items))
            self.pop_up_type.exec()
        else:
            for item in self.selectedItems():
                row = item.row()
                col = item.column()
                scan_path = self.item(row, 0).text()
                tag_name = self.horizontalHeaderItem(col).text()
                for scan in project._get_scans():
                    if scan_path == scan.file_path:
                        for tag in scan.getAllTags():
                            if tag_name == tag.name:
                                tp = type(tag.original_value[0])
                                txt = utils.check_tag_value(tag, 'original_value')
                                color = QColor()
                                if tag.origin != 'custom':
                                    if str(text_value) != str(txt):
                                        if row % 2 == 1:
                                            color.setRgb(240, 240, 255)
                                        else:
                                            color.setRgb(225, 225, 255)
                                    else:
                                        if row % 2 == 1:
                                            color.setRgb(255, 255, 255)
                                        else:
                                            color.setRgb(250, 250, 250)

                                else:
                                    if row % 2 == 1:
                                        color.setRgb(255, 240, 240)
                                    else:
                                        color.setRgb(255, 225, 225)

                                item.setData(Qt.BackgroundRole, QVariant(color))
                                item.setText(text_value)
                                tag_origin = tag.origin
                                tag_replace = tag.replace
                                if tp == list:
                                    tag_value_to_add = utils.text_to_list(text_value)
                                else:
                                    tag_value_to_add = utils.text_to_tag_value(text_value, tag)
                                new_tag = Tag(tag_name, tag_replace, tag_value_to_add, tag_origin, tag.original_value)
                                scan.replaceTag(new_tag, tag_name, str(tag_origin))

        self.itemChanged.connect(partial(self.change_cell_color, project))

        config = Config()
        if (config.isAutoSave() == "yes" and not project.name == ""):
            save_project(project)


class MiniViewer(QWidget):
    #TODO: IF THE CHECKBOX TO SHOW ALL SLICES IS CHECKED OR UNCHECKED IN THE PREFERENCES POP-UP, IT DOES NOT UPDATE THE
    #TODO: CHECKBOX OF THE MINIVIEWER : EVEN WITH SIGNALS IT DOES NOT WORK BECAUSE WE NEED TO CREATE TWO SEVERAL OBJECTS

    #TODO: HANDLE THE MULTI SELECTION

    def __init__(self, project):
        super().__init__()

        self.setHidden(True)
        self.nb_labels = 6

        self.config = Config()
        # Updating the check_box if the preferences are changed

        self.labels = QWidget()
        self.scroll_area = QScrollArea()
        self.frame = QFrame()
        self.scroll_area.setWidget(self.frame)
        self.frame_final = QFrame()

        self.createLayouts()

        self.setLayout(self.v_box_final)

        self.check_box = QCheckBox('Show all slices (no cursors)')

        if self.config.getShowAllSlices() == 'yes':
            self.check_box.setCheckState(Qt.Checked)
        else:
            self.check_box.setCheckState(Qt.Unchecked)

        self.check_box.stateChanged.connect(self.check_box_state_changed)
        self.file_path = ""

    def check_box_state_changed(self):
        if self.check_box.checkState() == Qt.Checked:
            self.config.setShowAllSlices('yes')
        elif self.check_box.checkState() == Qt.Unchecked:
            self.config.setShowAllSlices('no')
        self.show_slices(self.file_path)

    def show_slices(self, file_path):
        self.file_path = file_path
        self.setMinimumHeight(180)

        if self.isHidden():
            self.setHidden(False)

        self.clearLayouts()

        self.frame = QFrame(self)
        self.frame_final = QFrame(self)
        self.img = nib.load(self.file_path)

        if self.check_box.checkState() == Qt.Unchecked:

            self.boxSlider()
            self.enableSliders()

            sl1 = self.a1.value()
            sl2 = self.a2.value()
            sl3 = self.a3.value()

            if (len(self.img.shape) == 3):
                self.im_2D = self.img.get_data()[:, :, sl1].copy()
                self.a1.setMaximum(self.img.shape[2] - 1)
                self.a2.setMaximum(0)
                self.a3.setMaximum(0)
            if (len(self.img.shape) == 4):
                self.im_2D = self.img.get_data()[:, :, sl1, sl2].copy()
                self.a1.setMaximum(self.img.shape[2] - 1)
                self.a2.setMaximum(self.img.shape[3] - 1)
                self.a3.setMaximum(0)
            if (len(self.img.shape) == 5):
                self.im_2D = self.img.get_data()[:, :, sl1, sl2, sl3].copy()
                self.a1.setMaximum(self.img.shape[2] - 1)
                self.a2.setMaximum(self.img.shape[3] - 1)
                self.a3.setMaximum(self.img.shape[4] - 1)

            self.im_2D = rotate(self.im_2D, -90, reshape=False)
            self.im_2D = np.uint8((self.im_2D - self.im_2D.min()) / self.im_2D.ptp() * 255.0)
            self.im_2D = misc.imresize(self.im_2D, (128, 128))

            self.displayPosValue()

            w, h = self.im_2D.shape

            im_Qt = QImage(self.im_2D.data, w, h, QImage.Format_Indexed8)
            pixm = QPixmap.fromImage(im_Qt)

            self.imageLabel = QLabel(self)
            self.imageLabel.setPixmap(pixm)
            self.imageLabel.setToolTip(os.path.basename(self.file_path))

            self.h_box_slider_1 = QHBoxLayout()
            self.h_box_slider_1.addWidget(self.txta1)
            self.h_box_slider_1.addWidget(self.a1)

            self.h_box_slider_2 = QHBoxLayout()
            self.h_box_slider_2.addWidget(self.txta2)
            self.h_box_slider_2.addWidget(self.a2)

            self.h_box_slider_3 = QHBoxLayout()
            self.h_box_slider_3.addWidget(self.txta3)
            self.h_box_slider_3.addWidget(self.a3)

            self.v_box_sliders = QVBoxLayout()
            self.v_box_sliders.addLayout(self.h_box_slider_1)
            self.v_box_sliders.addLayout(self.h_box_slider_2)
            self.v_box_sliders.addLayout(self.h_box_slider_3)

            self.h_box = QHBoxLayout()
            self.h_box.addWidget(self.imageLabel)
            self.h_box.addLayout(self.v_box_sliders)
            self.h_box.addStretch(1)

            self.frame.setLayout(self.h_box)

        else:

            self.h_box_images = QHBoxLayout()
            self.h_box_images.setSpacing(10)

            if len(self.img.shape) == 3:
                nb_slices = self.img.shape[2]
                txt = "Slice n°"
            elif len(self.img.shape) == 4:
                nb_slices = self.img.shape[3]
                txt = "Time n°"
            elif len(self.img.shape) == 5:
                nb_slices = self.img.shape[4]
                txt = "Study n°"
            else:
                nb_slices = 0

            for i in range(nb_slices):
                pixm = self.image_to_pixmap(self.img, i)

                self.v_box = QVBoxLayout()

                label = QLabel(self)
                label.setPixmap(pixm)

                label_info = QLabel()
                label_info.setText(txt + str(i + 1))
                label_info.setAlignment(QtCore.Qt.AlignCenter)

                self.v_box.addWidget(label)
                self.v_box.addWidget(label_info)

                self.h_box_images.addLayout(self.v_box)
            self.frame.setLayout(self.h_box_images)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.frame)

        self.h_box_check_box = QHBoxLayout()
        self.h_box_check_box.addStretch(1)
        self.h_box_check_box.addWidget(self.check_box)

        self.v_box_final.addLayout(self.h_box_check_box)
        self.v_box_final.addWidget(self.scroll_area)

    def clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()

    def clearLayouts(self):

        for i in reversed(range(self.v_box_final.count())):
            if self.v_box_final.itemAt(i).widget() is not None:
                self.v_box_final.itemAt(i).widget().setParent(None)

        """try:
            self.clear_layout(self.h_box_images)
        except:
            pass
        else:
            self.clear_layout(self.h_box_images)

        try:
            self.clear_layout(self.v_box)
        except:
            pass
        else:
            self.clear_layout(self.v_box)

        try:
            self.clear_layout(self.v_box_final)
        except:
            pass
        else:
            self.clear_layout(self.v_box_final)

        try:
            self.clear_layout(self.h_box_slider_1)
        except:
            pass
        else:
            self.clear_layout(self.h_box_slider_1)

        try:
            self.clear_layout(self.h_box_slider_2)
        except:
            pass
        else:
            self.clear_layout(self.h_box_slider_2)

        try:
            self.clear_layout(self.h_box_slider_3)
        except:
            pass
        else:
            self.clear_layout(self.h_box_slider_3)

        try:
            self.clear_layout(self.v_box_sliders)
        except:
            pass
        else:
            self.clear_layout(self.v_box_sliders)

        try:
            self.clear_layout(self.h_box)
        except:
            pass
        else:
            self.clear_layout(self.h_box)

        try:
            self.clear_layout(self.h_box_check_box)
        except:
            pass
        else:
            self.clear_layout(self.h_box_check_box)"""


    def createLayouts(self):

        self.h_box_images = QHBoxLayout()
        self.h_box_images.setSpacing(10)
        self.v_box = QVBoxLayout()
        self.v_box_final = QVBoxLayout()
        self.h_box_slider_1 = QHBoxLayout()
        self.h_box_slider_2 = QHBoxLayout()
        self.h_box_slider_3 = QHBoxLayout()
        self.v_box_sliders = QVBoxLayout()
        self.h_box = QHBoxLayout()
        self.h_box_check_box = QHBoxLayout()


    def image_to_pixmap(self, im, i):
        # The image to show depends on the dimension of the image
        if len(im.shape) == 3:
            self.im_2D = im.get_data()[:, :, i].copy()

        elif len(im.shape) == 4:
            im_3D = im.get_data()[:, :, :, i].copy()
            middle_slice = int(im_3D.shape[2] / 2)
            self.im_2D = im_3D[:, :, middle_slice]

        elif len(im.shape) == 5:
            im_4D = im.get_data()[:, :, :, :, i].copy()
            im_3D = im_4D[:, :, :, 1]
            middle_slice = int(im_3D.shape[2] / 2)
            self.im_2D = im_3D[:, :, middle_slice]

        else:
            self.im_2D = [0]

        self.im_2D = rotate(self.im_2D, -90, reshape=False)
        self.im_2D = np.uint8((self.im_2D - self.im_2D.min()) / self.im_2D.ptp() * 255.0)
        self.im_2D = misc.imresize(self.im_2D, (128, 128))

        w, h = self.im_2D.shape

        im_Qt = QImage(self.im_2D.data, w, h, QImage.Format_Indexed8)
        pixm = QPixmap.fromImage(im_Qt)

        return pixm

    def createSlider(self,maxm=0,minm=0,pos=0):
        slider = QSlider(Qt.Horizontal)
        slider.setFocusPolicy(Qt.StrongFocus)
        #slider.setTickPosition(QSlider.TicksBothSides)
        slider.setTickInterval(1)
        #slider.setSingleStep(1)
        slider.setMaximum(maxm)
        slider.setMinimum(minm)
        slider.setValue(pos)
        slider.setEnabled(False)
        return slider

    def enableSliders(self):
        self.a1.setEnabled(True)
        self.a2.setEnabled(True)
        self.a3.setEnabled(True)

    def boxSlider(self):
        self.a1 = self.createSlider(0, 0, 0)
        self.a2 = self.createSlider(0, 0, 0)
        self.a3 = self.createSlider(0, 0, 0)

        self.a1.valueChanged.connect(self.changePosValue)
        self.a2.valueChanged.connect(self.changePosValue)
        self.a3.valueChanged.connect(self.changePosValue)

        self.txta1 = self.createFieldValue()
        self.txta2 = self.createFieldValue()
        self.txta3 = self.createFieldValue()

    def displayPosValue(self):
        self.txta1.setText(str(self.a1.value()+1)+' / '+str(self.a1.maximum()+1))
        self.txta2.setText(str(self.a2.value()+1)+' / '+str(self.a2.maximum()+1))
        self.txta3.setText(str(self.a3.value()+1)+' / '+str(self.a3.maximum()+1))

    def createFieldValue(self):
        fieldValue = QLineEdit()
        fieldValue.setEnabled(False)
        fieldValue.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        return fieldValue

    def changePosValue(self):
        self.navigImage()

    def navigImage(self):
        self.indexImage()
        self.displayPosValue()

        self.im_2D = rotate(self.im_2D, -90, reshape=False)
        self.im_2D = np.uint8((self.im_2D - self.im_2D.min()) / self.im_2D.ptp() * 255.0)
        self.im_2D = misc.imresize(self.im_2D, (128, 128))

        w, h = self.im_2D.shape

        image = QImage(self.im_2D.data,w,h,QImage.Format_Indexed8)
        self.pixm = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(self.pixm)

    def indexImage(self):
        sl1=self.a1.value()
        sl2=self.a2.value()
        sl3=self.a3.value()
        if (len(self.img.shape)==3):
            self.im_2D = self.img.get_data()[:,:,sl1].copy()
            self.a1.setMaximum(self.img.shape[2]-1)
            self.a2.setMaximum(0)
            self.a3.setMaximum(0)
        if (len(self.img.shape)==4):
            self.im_2D = self.img.get_data()[:,:,sl1,sl2].copy()
            self.a1.setMaximum(self.img.shape[2]-1)
            self.a2.setMaximum(self.img.shape[3]-1)
            self.a3.setMaximum(0)
        if (len(self.img.shape)==5):
            self.im_2D = self.img.get_data()[:,:,sl1,sl2,sl3].copy()
            self.a1.setMaximum(self.img.shape[2]-1)
            self.a2.setMaximum(self.img.shape[3]-1)
            self.a3.setMaximum(self.img.shape[4]-1)
