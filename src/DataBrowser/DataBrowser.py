from PyQt5.QtCore import Qt, QVariant, QPoint
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QTableWidget, QHBoxLayout, QSplitter
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor, QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QLabel, QScrollArea, QFrame, QToolBar, QToolButton, QAction,\
    QMessageBox, QHeaderView
import controller
import os
from models import *
from pop_ups import Ui_Dialog_add_tag, Ui_Dialog_clone_tag, Ui_Dialog_Type_Problem, Ui_Dialog_remove_tag, \
    Ui_Visualized_Tags, Ui_Dialog_Preferences, Ui_Dialog_Settings
from functools import partial
import nibabel as nib
from scipy.ndimage import rotate  # to work with NumPy arrays
import numpy as np  # a N-dimensional array object
import sip


class DataBrowser(QWidget):
    def __init__(self, project):

        super(DataBrowser, self).__init__()

        _translate = QtCore.QCoreApplication.translate
        self.create_actions(project)
        self.create_toolbar_menus()

        ################################### TABLE ###################################

        # Frame behind the table
        self.frame_table_data = QtWidgets.QFrame(self)
        self.frame_table_data.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_table_data.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_table_data.setObjectName("frame_table_data")

        """'# Label
        self.label_principal_table = QtWidgets.QLabel(self.frame_table_data)
        self.label_principal_table.setText(_translate("MainWindow", "Principal Table"))

        # "Add tag" button
        self.push_button_add_tag = QtWidgets.QPushButton(self.frame_table_data)
        self.push_button_add_tag.setText(_translate("MainWindow", "Add tag"))
        self.push_button_add_tag.setObjectName("pushButton_add_tag")
        self.push_button_add_tag.clicked.connect(lambda: self.add_tag_pop_up(project))

        # "Clone tag" button
        self.push_button_clone_tag = QtWidgets.QPushButton(self.frame_table_data)
        self.push_button_clone_tag.setText(_translate("MainWindow", "Clone tag"))
        self.push_button_clone_tag.setObjectName("pushButton_clone_tag")
        self.push_button_clone_tag.clicked.connect(lambda: self.clone_tag_pop_up(project))

        # "Remove tag" button
        self.push_button_remove_tag = QtWidgets.QPushButton(self.frame_table_data)
        self.push_button_remove_tag.setText(_translate("MainWindow", "Remove tag"))
        self.push_button_remove_tag.setObjectName("pushButton_remove_tag")
        self.push_button_remove_tag.clicked.connect(lambda: self.remove_tag_pop_up(project))"""

        # Main table that will display the tags
        self.table_data = TableDataBrowser(project)
        self.table_data.setObjectName("table_data")
        self.table_data.cellClicked.connect(partial(self.connect_viewer, project))

        ## LAYOUTS ##

        """vbox_table = QVBoxLayout()
        vbox_table.addWidget(self.label_principal_table)
        vbox_table.addWidget(self.push_button_add_tag)
        vbox_table.addWidget(self.push_button_clone_tag)
        vbox_table.addWidget(self.push_button_remove_tag)
        vbox_table.setSpacing(10)
        vbox_table.addStretch(1)"""

        hbox_table = QHBoxLayout()
        # hbox_table.addLayout(vbox_table)
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

        """vbox = QVBoxLayout()
        vbox.addWidget(self.menu_toolbar)
        vbox.addLayout(hbox_splitter)
        self.setLayout(vbox)"""

    def create_actions(self, project):
        self.add_tag_action = QAction("Add tag", self, shortcut="Ctrl+A")
        self.add_tag_action.triggered.connect(lambda: self.add_tag_pop_up(project))

        self.clone_tag_action = QAction("Clone tag", self)
        self.clone_tag_action.triggered.connect(lambda: self.clone_tag_pop_up(project))

        self.remove_tag_action = QAction("Remove tag", self, shortcut="Ctrl+R")
        self.remove_tag_action.triggered.connect(lambda: self.remove_tag_pop_up(project))

    def create_toolbar_menus(self):
        self.menu_toolbar = QToolBar()

        tags_tool_button = QToolButton()
        tags_tool_button.setText('Tags')
        tags_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        tags_menu = QMenu()
        tags_menu.addAction(self.add_tag_action)
        tags_menu.addAction(self.clone_tag_action)
        tags_menu.addAction(self.remove_tag_action)
        tags_tool_button.setMenu(tags_menu)

        self.menu_toolbar.addWidget(tags_tool_button)

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

        # It allows to move the columns
        self.horizontalHeader().setSectionsMovable(True)
        #self.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        #self.setSelectionMode(QAbstractItemView.MultiSelection)

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.context_menu_table, project))
        self.flag_first_time = 0
        hh = self.horizontalHeader()
        hh.sectionClicked.connect(partial(self.sort_items, project))
        #self.horizontalHeader.sectionClicked().connect(lambda: self.sort_items(project))
        if project:
            self.update_table(project)

    def update_table(self, project):
        """
        This method will fill the tables in the 'Table' tab with the project data
        """

        project.sort_by_tags()
        self.flag_first_time += 1

        if self.flag_first_time > 1:
            self.itemChanged.disconnect()

        self.nb_columns = len(project.tags_to_visualize) # Read from MIA2 preferences

        self.nb_rows = len(project._get_scans())
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

        """# Filling the header of the columns
        item = self.horizontalHeaderItem(0)
        item.setIcon(QIcon(os.path.join('sources_images', 'down_arrow.png')))
        item.setText('FileName')"""

        nb = 0
        for element in project.tags_to_visualize:
            element = str(element)
            #item = QTableWidgetItem()
            item = self.horizontalHeaderItem(nb)
            if element == project.sort_tags[0]:
                if project.sort_order == 'ascending':
                    item.setIcon(QIcon(os.path.join('sources_images', 'down_arrow.png')))
                else:
                    item.setIcon(QIcon(os.path.join('sources_images', 'up_arrow.png')))
            item.setText(_translate("MainWindow", element))
            self.setHorizontalHeaderItem(nb, item)
            nb += 1

        """ Filling the first column with the path of each scan """
        """nb = 0
        for i in project._get_scans():
            a = str(i.file_path)
            item = QTableWidgetItem()
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setText(a)
            self.setItem(nb, 0, item)
            nb += 1"""

        # Filling all the cells
        y = -1
        # Loop on the scans

        for file in project._get_scans():
            y += 1
            i = -1

            # Loop on the selected tags
            for tag_name in project.tags_to_visualize:
                i += 1
                # If the tag belong to the tags of the project (of course it does...)
                if tag_name in controller.getAllTagsFile(file.file_path, project):
                    # Loop on the project tags
                    for n_tag in file._get_tags():
                        # If a project tag name matches our tag
                        if n_tag.name == tag_name:
                            # It is put in the table
                            item = QTableWidgetItem()
                            txt = utils.check_tag_value_2(n_tag, 'value')
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
                                    txt = utils.check_tag_value_2(n_tag, 'original_value')
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

        #__sortingEnabled = self.isSortingEnabled()
        #self.setSortingEnabled(__sortingEnabled)
        self.resizeColumnsToContents()

        # When the user changes one item of the table, the background will change
        #self.itemChanged.connect(lambda item: self.change_cell_color(item, project))
        self.itemChanged.connect(partial(self.change_cell_color, project))
        """self.itemDoubleClicked.connect(self.sort_column)"""

    def context_menu_table(self, project, position):

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
        """nb_cells = len(self.selectedIndexes())
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setText("You are about to reset cells.")
        msg.setStandardButtons(QMessageBox.Ok)"""

        if action == action_reset_cell:

            """msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.reset_cell(project))
            msg.exec()"""
            self.reset_cell(project)
        elif action == action_reset_column:
            """#msg.setText("You are about to reset " + str(nb_cells * self.rowCount()) + " cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.reset_column(project))
            msg.exec()"""
            self.reset_column(project)
        elif action == action_reset_row:
            """#msg.setText("You are about to reset " + str(nb_cells * self.columnCount()) + " cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(lambda: self.reset_row(project))
            msg.exec()"""
            self.reset_row(project)
        elif action == action_remove_scan:
            self.remove_scan(project)
        elif action == action_sort_column:
            self.sort_column(project)
        elif action == action_sort_column_descending:
            self.sort_column_descending(project)
        elif action == action_visualized_tags:
            self.visualized_tags_pop_up(project)

        self.update_table(project)

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
                            txt = utils.check_tag_value_2(n_tag, 'original_value')
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
                        txt = utils.check_tag_value_2(n_tag, 'original_value')
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
            # tag_name = self.table_widget_main.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()
            for file in project._get_scans():
                if file.file_path == scan_name:
                    for n_tag in file.getAllTags():
                        if n_tag.name in project.tags_to_visualize:
                            idx = project.tags_to_visualize.index(n_tag.name) + 1
                            txt = utils.check_tag_value_2(n_tag, 'original_value')
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
                            txt = utils.check_tag_value_2(tag, 'value')
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
                item.setIcon(QIcon(os.path.join('sources_images', 'up_arrow.png')))
            else:
                project.sort_order = 'ascending'
                item.setIcon(QIcon(os.path.join('sources_images', 'down_arrow.png')))
        else:
            project.sort_order = 'ascending'
            item.setIcon(QIcon(os.path.join('sources_images', 'down_arrow.png')))

        project.reset_sort_tags()
        project.add_sort_tag(tag_name)
        self.update_table(project)

    def sort_column(self, project):
        points = self.selectedItems()

        project.sort_order = "ascending"
        #self.setSortingEnabled(True)
        project.reset_sort_tags()

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            project.add_sort_tag(tag_name)

    def sort_column_descending(self, project):
        points = self.selectedItems()

        project.sort_order = "descending"
        #self.setSortingEnabled(True)
        project.reset_sort_tags()

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            project.add_sort_tag(tag_name)

    def visualized_tags_pop_up(self, project):
        self.pop_up = Ui_Dialog_Settings(project)
        self.pop_up.tab_widget.setCurrentIndex(1)

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
                                txt = utils.check_tag_value_2(tag, 'original_value')
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


class MiniViewer(QScrollArea):

    def __init__(self, project):
        super().__init__()

        self.setHidden(True)
        self.nb_labels = 6

        self.labels = QWidget()
        self.frame = QFrame()
        self.h_box_images = QHBoxLayout()
        self.h_box_images.setSpacing(10)
        self.v_box = QVBoxLayout()

    def show_slices(self, file_path):
        self.setMinimumHeight(180)

        if self.isHidden():
            self.setHidden(False)

        self.clear_layout(self.h_box_images)
        self.clear_layout(self.v_box)
        self.frame = QFrame()
        im = nib.load(file_path)

        if len(im.shape) == 3:
            nb_slices = im.shape[2]
            txt = "Slice n°"
        elif len(im.shape) == 4:
            nb_slices = im.shape[3]
            txt = "Time n°"
        elif len(im.shape) == 5:
            nb_slices = im.shape[4]
            txt = "Study n°"
        else:
            nb_slices = 0

        for i in range(nb_slices):
            pixm = self.image_to_pixmap(im, i)

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
        self.setWidget(self.frame)

    def clear_layout(self, layout):
        while layout.count() > 0:
            item = layout.takeAt(0)
            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()

    def image_to_pixmap(self, im, i):
        # The image to show depends on the dimension of the image
        if len(im.shape) == 3:
            im_2D = im.get_data()[:, :, i].copy()

        elif len(im.shape) == 4:
            im_3D = im.get_data()[:, :, :, i].copy()
            middle_slice = int(im_3D.shape[2] / 2)
            im_2D = im_3D[:, :, middle_slice]

        elif len(im.shape) == 5:
            im_4D = im.get_data()[:, :, :, :, i].copy()
            im_3D = im_4D[:, :, :, 1]
            middle_slice = int(im_3D.shape[2] / 2)
            im_2D = im_3D[:, :, middle_slice]

        else:
            im_2D = [0]

        import scipy.misc as misc

        im_2D = rotate(im_2D, -90, reshape=False)
        im_2D = np.uint8((im_2D - im_2D.min()) / im_2D.ptp() * 255.0)
        im_2D = misc.imresize(im_2D, (128, 128))

        w, h = im_2D.shape

        im_Qt = QImage(im_2D.data, w, h, QImage.Format_Indexed8)
        pixm = QPixmap.fromImage(im_Qt)

        return pixm
