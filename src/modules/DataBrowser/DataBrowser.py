from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QTableWidget, QHBoxLayout, QSplitter, QGridLayout
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QFrame, QToolBar, QToolButton, QAction,\
    QMessageBox, QPushButton
import os
from ProjectManager.controller import save_project


from PopUps.Ui_Dialog_add_tag import Ui_Dialog_add_tag
from PopUps.Ui_Dialog_clone_tag import Ui_Dialog_clone_tag
from PopUps.Ui_Dialog_Type_Problem import Ui_Dialog_Type_Problem
from PopUps.Ui_Dialog_remove_tag import Ui_Dialog_remove_tag
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings

from SoftwareProperties import Config
from ImageViewer.MiniViewer import MiniViewer

from functools import partial
import Utils.utils as utils
from SoftwareProperties.Config import Config
from DataBase.DataBaseModel import TAG_ORIGIN_USER, TAG_ORIGIN_RAW, TAG_TYPE_STRING, TAG_TYPE_FLOAT, TAG_TYPE_INTEGER, TAG_TYPE_LIST
from DataBrowser.AdvancedSearch import AdvancedSearch

class DataBrowser(QWidget):
    def __init__(self, database):

        self.database = database

        super(DataBrowser, self).__init__()

        _translate = QtCore.QCoreApplication.translate
        self.create_actions()
        self.create_toolbar_menus()

        ################################### TABLE ###################################

        # Frame behind the table
        self.frame_table_data = QtWidgets.QFrame(self)
        self.frame_table_data.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_table_data.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_table_data.setObjectName("frame_table_data")

        # Main table that will display the tags
        self.table_data = TableDataBrowser(database)
        self.table_data.setObjectName("table_data")
        self.table_data.itemSelectionChanged.connect(self.connect_viewer)

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

        self.viewer = MiniViewer(self.database)
        self.viewer.setObjectName("viewer")
        self.viewer.adjustSize()

        hbox_viewer = QHBoxLayout()
        hbox_viewer.addWidget(self.viewer)

        self.frame_visualization.setLayout(hbox_viewer)

        # ADVANCED SEARCH

        self.frame_advanced_search = QtWidgets.QFrame(self)
        self.frame_advanced_search.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_advanced_search.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_advanced_search.setObjectName("frame_search")
        self.frame_advanced_search.setHidden(True)
        self.advanced_search = AdvancedSearch(self.database, self)
        layout_search = QGridLayout()
        layout_search.addWidget(self.advanced_search)
        self.frame_advanced_search.setLayout(layout_search)

        ## SPLITTER AND LAYOUT ##

        self.splitter_vertical = QSplitter(Qt.Vertical)
        self.splitter_vertical.addWidget(self.frame_advanced_search)
        self.splitter_vertical.addWidget(self.frame_table_data)
        self.splitter_vertical.addWidget(self.frame_visualization)
        self.splitter_vertical.splitterMoved.connect(self.move_splitter)

        vbox_splitter = QVBoxLayout(self)
        vbox_splitter.addWidget(self.menu_toolbar)
        vbox_splitter.addWidget(self.splitter_vertical)

        self.setLayout(vbox_splitter)

    def update_database(self, database):
        self.database = database
        self.table_data.database = database
        self.viewer.database = database
        self.advanced_search.database = database
        self.frame_advanced_search.setHidden(True)

    def create_actions(self):
        self.add_tag_action = QAction("Add tag", self, shortcut="Ctrl+A")
        self.add_tag_action.triggered.connect(self.add_tag_pop_up)

        self.clone_tag_action = QAction("Clone tag", self)
        self.clone_tag_action.triggered.connect(self.clone_tag_pop_up)

        self.remove_tag_action = QAction("Remove tag", self, shortcut="Ctrl+R")
        self.remove_tag_action.triggered.connect(self.remove_tag_pop_up)

    def visualized_tags_pop_up(self):
        self.pop_up = Ui_Dialog_Settings(self.database)
        self.pop_up.tab_widget.setCurrentIndex(0)

        self.pop_up.setGeometry(300, 200, 800, 600)
        self.pop_up.show()

        if self.pop_up.exec_() == QDialog.Accepted:
            self.table_data.update_table()

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

        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(partial(self.search_str))

        self.button_cross = QToolButton()
        self.button_cross.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.button_cross.setIcon(QIcon(os.path.join('..', 'sources_images', 'gray_cross.png')))
        self.button_cross.clicked.connect(self.reset_search_bar)

        search_bar_layout = QHBoxLayout()
        search_bar_layout.setSpacing(0)
        search_bar_layout.addWidget(self.search_bar)
        search_bar_layout.addWidget(self.button_cross)

        advanced_search_button = QPushButton()
        advanced_search_button.setText('Advanced search')
        advanced_search_button.clicked.connect(self.advanced_search)

        self.frame_test = QFrame()
        self.frame_test.setLayout(search_bar_layout)

        visualized_tags_button = QPushButton()
        visualized_tags_button.setText('Visualized tags')
        visualized_tags_button.clicked.connect(self.visualized_tags_pop_up)

        self.menu_toolbar.addWidget(tags_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.frame_test)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(advanced_search_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(visualized_tags_button)

    def search_str(self, str_search):

        """return_list = []
        if str_search != "":
            split_list = str_search.split('*')
            for scan in self.database.getScans():
                for tag in self.database.getValuesGivenScan(scan.scan):
                    if scan.scan in return_list:
                        break
                    if self.database.getTagVisibility(tag.tag):
                        i = 0
                        for element in split_list:
                            if element.upper() in str(tag.current_value[0]).upper():
                                i += 1
                        if i == len(split_list):
                            return_list.append(scan.scan)
        else:
            for scan in self.database.getScans():
                return_list.append(scan.scan)"""

        return_list = []

        if str_search != "":
            for scan in self.database.getScansSimpleSearch(str_search):
                return_list.append(scan)
        else:
            for scan in self.database.getScans():
                return_list.append(scan.scan)

        self.table_data.scans_to_visualize = return_list
        self.table_data.update_table()

    def reset_search_bar(self):
        self.search_bar.setText("")

    def move_splitter(self):
        if self.splitter_vertical.sizes()[1] != self.splitter_vertical.minimumHeight():
            self.connect_viewer()
            """
            self.viewer.setHidden(False)
        else:
            self.viewer.setHidden(True)
            path_name = os.path.relpath(self.database.folder)
            items = self.table_data.selectedItems()
            full_names = []
            for item in items:
                row = item.row()
                file_name = self.table_data.item(row, 0).text() + ".nii"
                full_name = path_name + '/data/raw_data/' + file_name
                if not full_name in full_names:
                    full_names.append(full_name)

            self.viewer.show_slices(full_names)"""

    def connect_viewer(self):

        if self.splitter_vertical.sizes()[1] == self.splitter_vertical.minimumHeight():
            self.viewer.setHidden(True)
        else:
            self.viewer.setHidden(False)
            path_name = os.path.relpath(self.database.folder)
            items = self.table_data.selectedItems()
            full_names = []
            for item in items:
                row = item.row()
                file_name = self.table_data.item(row, 0).text() + ".nii"
                full_name = os.path.join(path_name, 'data', 'raw_data', file_name)
                if not full_name in full_names:
                    full_names.append(full_name)

            self.viewer.verify_slices(full_names)

    def advanced_search(self):
        if(self.frame_advanced_search.isHidden()):
            self.frame_advanced_search.setHidden(False)
            self.advanced_search.show_search()
        else:
            self.frame_advanced_search.setHidden(True)
            return_list = []
            for scan in self.database.getScans():
                return_list.append(scan.scan)
            self.table_data.scans_to_visualize = return_list
            self.table_data.update_table()

    def add_tag_pop_up(self):
        # Ui_Dialog_add_tag() is defined in pop_ups.py
        self.pop_up_add_tag = Ui_Dialog_add_tag(self.database)
        self.pop_up_add_tag.show()

        if self.pop_up_add_tag.exec_() == QDialog.Accepted:
            (new_tag_name, new_default_value, type, new_tag_description, new_tag_unit) = self.pop_up_add_tag.get_values()

            """if type != list:
                list_to_add = []
                list_to_add.append(type(new_default_value))
            else:
                list_to_add = utils.text_to_list(new_default_value)"""


            #new_tag = Tag(new_tag_name, "", list_to_add, "custom", list_to_add)


            # Updating the data base
            #project.add_user_tag(new_tag_name, list_to_add)
            #project.add_tag(new_tag)
            #project.tags_to_visualize.append(new_tag_name)

            # Database
            real_type = ""
            if(type == str):
                real_type = TAG_TYPE_STRING
            if (type == int):
                real_type = TAG_TYPE_INTEGER
            if (type == float):
                real_type = TAG_TYPE_FLOAT
            if (type == list):
                real_type = TAG_TYPE_LIST
            self.database.addTag(new_tag_name, True, TAG_ORIGIN_USER, real_type, new_tag_unit, new_default_value, new_tag_description)
            for scan in self.database.getScans():
                self.database.addValue(scan.scan, new_tag_name, new_default_value, new_default_value)

            historyMaker = []
            historyMaker.append("add_tag")
            historyMaker.append(new_tag_name)
            self.database.history.append(historyMaker)
            self.database.historyHead = self.database.historyHead + 1

            # Updating the table
            self.table_data.update_table()

    def clone_tag_pop_up(self):
        # Ui_Dialog_clone_tag() is defined in pop_ups.py
        self.pop_up_clone_tag = Ui_Dialog_clone_tag(self.database)
        self.pop_up_clone_tag.show()

        if self.pop_up_clone_tag.exec_() == QDialog.Accepted:
            (tag_to_clone, new_tag_name) = self.pop_up_clone_tag.get_values()

            # Updating the data base
            #project.clone_tag(tag_to_clone, new_tag_name)
            #project.tags_to_visualize.append(new_tag_name)

            self.database.addTag(new_tag_name, True, TAG_ORIGIN_USER, self.database.getTagType(tag_to_clone), self.database.getTagUnit(tag_to_clone), self.database.getTagDefault(tag_to_clone), self.database.getTagDescription(tag_to_clone))
            for scan in self.database.getScans():
                if(self.database.scanHasTag(scan.scan, tag_to_clone)):
                    self.database.addValue(scan.scan, new_tag_name, self.database.getValue(scan.scan, tag_to_clone).current_value)

            historyMaker = []
            historyMaker.append("add_tag")
            historyMaker.append(new_tag_name)
            self.database.history.append(historyMaker)
            self.database.historyHead = self.database.historyHead + 1

            # Updating the table
            self.table_data.update_table()

    def remove_tag_pop_up(self):
        # Ui_Dialog_remove_tag() is defined in pop_ups.py
        self.pop_up_clone_tag = Ui_Dialog_remove_tag(self.database)
        self.pop_up_clone_tag.show()

        if self.pop_up_clone_tag.exec_() == QDialog.Accepted:
            tag_names_to_remove = self.pop_up_clone_tag.get_values()

            #for tag_name in tag_names_to_remove:
                #project.remove_tag_by_name(tag_name)

            historyMaker = []
            historyMaker.append("remove_tags")
            tags_removed = []
            for tag in tag_names_to_remove:
                tagObject = self.database.getTag(tag)
                tags_removed.append(tagObject)
            historyMaker.append(tags_removed)
            values_removed = []
            for tag in tag_names_to_remove:
                for value in self.database.getValuesGivenTag(tag):
                    values_removed.append(value)
            historyMaker.append(values_removed)
            self.database.history.append(historyMaker)
            self.database.historyHead = self.database.historyHead + 1

            for tag in tag_names_to_remove:
                self.database.removeTag(tag)

            self.table_data.update_table()

class TableDataBrowser(QTableWidget):

    # DATABASE
    def __init__(self, database):

        self.database = database
        self.flag_first_time = 0

        super().__init__()

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # The list of scans to visualize
        self.scans_to_visualize = []
        for scan in self.database.getScans():
            self.scans_to_visualize.append(scan.scan)

        # It allows to move th  e columns
        self.horizontalHeader().setSectionsMovable(True)

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.context_menu_table))
        self.flag_first_time = 0
        self.hh = self.horizontalHeader()
        self.hh.sectionClicked.connect(partial(self.selectAllColumn))
        self.hh.sectionDoubleClicked.connect(partial(self.sort_items))

        self.update_table()

    def selectAllColumn(self, col):
        self.clearSelection()
        self.selectColumn(col)

    def selectAllColumns(self):
        self.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        points = self.selectedIndexes()
        self.clearSelection()
        for point in points:
            col = point.column()
            self.selectColumn(col)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def update_table(self):
        """
        This method will fill the tables in the 'Table' tab with the project data
        """

        if(self.database.getSortedTag() != ''):
            list_tags = []
            for scan in self.scans_to_visualize:
                if(self.database.scanHasTag(scan, self.database.getSortedTag())):
                    list_tags.append(self.database.getValue(scan, self.database.getSortedTag()).current_value)
                else:
                    list_tags.append("NaN")

            if self.database.getSortOrder() == "ascending":
                self.scans_to_visualize = [x for _, x in sorted(zip(list_tags, self.scans_to_visualize))]
            elif self.database.getSortOrder() == "descending":
                self.scans_to_visualize = [x for _, x in sorted(zip(list_tags, self.scans_to_visualize), reverse=True)]

        self.flag_first_time += 1

        if self.flag_first_time > 1:
            self.itemChanged.disconnect()

        # DATABASE
        self.nb_columns = len(self.database.getVisualizedTags())

        # PROJECT
        #self.nb_columns = len(project.tags_to_visualize) # Read from MIA2 preferences

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
        # PROJECT
        #for element in project.tags_to_visualize:
        # DATABASE
        for element in self.database.getVisualizedTags():
            # PROJECT
            #element = str(element)
            # DATABASE
            element = element.tag
            item = self.horizontalHeaderItem(nb)
            # PROJECT
            if element == self.database.getSortedTag():
                if self.database.getSortOrder() == 'ascending':
                    item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))
                else:
                    item.setIcon(QIcon(os.path.join('..', 'sources_images', 'up_arrow.png')))
            item.setText(_translate("MainWindow", element))
            item.setToolTip(self.database.getTagDescription(element))
            self.setHorizontalHeaderItem(nb, item)
            nb += 1

        # Filling all the cells
        #y = -1
        # Loop on the scans

        row = 0
        for scan in self.scans_to_visualize:
            column = 0
            while column < len(self.horizontalHeader()):
                item = self.horizontalHeaderItem(column)
                current_tag = item.text()
                # The scan has a value for the tag
                if(self.database.scanHasTag(scan, current_tag)):
                    value =  self.database.getValue(scan, current_tag)
                    item = QTableWidgetItem()
                    item.setText(value.current_value)
                    # FileName not editable
                    if current_tag == "FileName":
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    # User tag
                    if self.database.getTagOrigin(current_tag) == TAG_ORIGIN_USER:
                        color = QColor()
                        if row % 2 == 1:
                            color.setRgb(255, 240, 240)
                        else:
                            color.setRgb(255, 225, 225)
                        item.setData(Qt.BackgroundRole, QVariant(color))

                # The scan does not have a value for the tag
                else:
                    a = str('NaN')
                    item = QTableWidgetItem()
                    item.setText(a)
                self.setItem(row, column, item)
                column += 1
            row += 1

        """for file in project._get_scans():
        
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
                        self.setItem(y, i, item)"""

        ######

        self.resizeColumnsToContents()

        # When the user changes one item of the table, the background will change
        self.itemChanged.connect(self.change_cell_color)

        # Auto-save
        config = Config()
        if (config.isAutoSave() == "yes" and not self.database.isTempProject):
            save_project(self.database)

    def context_menu_table(self, position):

        self.itemChanged.disconnect()

        self.flag_first_time += 1

        menu = QMenu(self)

        action_reset_cell = menu.addAction("Reset cell(s)")
        action_reset_column = menu.addAction("Reset column(s)")
        action_reset_row = menu.addAction("Reset row(s)")
        action_remove_scan = menu.addAction("Remove scan(s)")
        action_sort_column = menu.addAction("Sort column")
        action_sort_column_descending = menu.addAction("Sort column (descending)")
        action_visualized_tags = menu.addAction("Visualized tags")
        action_select_column = menu.addAction("Select column(s)")

        action = menu.exec_(self.mapToGlobal(position))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)

        if action == action_reset_cell:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(self.reset_cell)
            msg.exec()
        elif action == action_reset_column:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(self.reset_column)
            msg.exec()
        elif action == action_reset_row:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(self.reset_row)
            msg.exec()
        elif action == action_remove_scan:
            msg.setText("You are about to remove a scan from the project.")
            msg.buttonClicked.connect(msg.close)
            msg.buttonClicked.connect(self.remove_scan)
            msg.exec()
        elif action == action_sort_column:
            self.sort_column()
        elif action == action_sort_column_descending:
            self.sort_column_descending()
        elif action == action_visualized_tags:
            self.visualized_tags_pop_up()
        elif action == action_select_column:
            self.selectAllColumns()

        # Signals reconnected
        self.itemChanged.connect(self.change_cell_color)

        self.update_table()

    def reset_cell(self):

        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()

            if(self.database.scanHasTag(scan_name, tag_name)):
                self.database.resetTag(scan_name, tag_name)
                self.item(row, col).setText(self.database.getValue(scan_name, tag_name).raw_value)

                if(self.database.getTagOrigin(tag_name) == TAG_ORIGIN_RAW):
                    color = QColor()
                    if row % 2 == 1:
                        color.setRgb(255, 255, 255)
                    else:
                        color.setRgb(250, 250, 250)
                    self.item(row, col).setData(Qt.BackgroundRole, QVariant(color))

            """for file in self.database.getScans():
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
                            n_tag.resetTag()"""

    def reset_column(self):
        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()

            scan_id = -1
            for scan in self.database.getScans():
                if (self.database.scanHasTag(scan.scan, tag_name)):
                    self.database.resetTag(scan.scan, tag_name)
                    scan_id += 1
                    self.item(scan_id, col).setText(self.database.getValue(scan.scan, tag_name).raw_value)
                    if self.database.getTagOrigin(tag_name) == TAG_ORIGIN_RAW:
                        color = QColor()
                        if row % 2 == 1:
                            color.setRgb(255, 255, 255)
                        else:
                            color.setRgb(250, 250, 250)
                        self.item(scan_id, col).setData(Qt.BackgroundRole, QVariant(color))

            """scan_id = -1
            for file in project._get_scans():

                # DATABASE
                self.database.resetTag(file.file_path, tag_name)

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
                        n_tag.resetTag()"""

    def reset_row(self):
        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            scan_name = self.item(row, 0).text()

            idx = -1
            for tag in self.database.getVisualizedTags():
                idx += 1
                if (self.database.scanHasTag(scan_name, tag.tag)):
                    self.database.resetTag(scan_name, tag.tag)
                    self.item(row, idx).setText(self.database.getValue(scan_name, tag.tag).raw_value)
                    if(self.database.getTagOrigin(tag.tag) == TAG_ORIGIN_RAW):
                        color = QColor()
                        if row % 2 == 1:
                            color.setRgb(255, 255, 255)
                        else:
                            color.setRgb(250, 250, 250)
                        self.item(row, idx).setData(Qt.BackgroundRole, QVariant(color))

            """for file in project._get_scans():
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

                        # DATABASE
                        self.database.resetTag(scan_name, n_tag.name)"""

    def reset_cells_with_item(self, items_in):

        for item_in in items_in:
            row = item_in.row()
            col = item_in.column()

            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()

            item = QTableWidgetItem()
            if self.database.getTagOrigin(tag_name) == TAG_ORIGIN_USER:
                color = QColor()
                if row % 2 == 1:
                    color.setRgb(255, 240, 240)
                else:
                    color.setRgb(255, 225, 225)
                item.setData(Qt.BackgroundRole, QVariant(color))
            item.setText(self.database.getValue(scan_path, tag_name).current_value)
            self.setItem(row, col, item)

            """for scan in project._get_scans():
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
                            self.setItem(row, col, item)"""

    def remove_scan(self):
        points = self.selectedIndexes()

        historyMaker = []
        historyMaker.append("remove_scans")
        scans_removed = []
        values_removed = []

        for point in points:
            row = point.row()
            scan_path = self.item(row, 0).text()

            """for scan in project._get_scans():
                if scan_path == scan.file_path:
                    project.remove_scan(scan_path)"""

            scan_object = self.database.getScan(scan_path)
            scans_removed.append(scan_object)
            for value in self.database.getValuesGivenScan(scan_path):
                values_removed.append(value)

            self.scans_to_visualize.remove(scan_path)
            self.database.removeScan(scan_path)

        historyMaker.append(scans_removed)
        historyMaker.append(values_removed)
        self.database.history.append(historyMaker)
        self.database.historyHead = self.database.historyHead + 1

    def sort_items(self, col):
        self.clearSelection() # Remove the column selection from single click
        item = self.horizontalHeaderItem(col)
        tag_name = self.horizontalHeaderItem(col).text()
        if tag_name == self.database.getSortedTag():
            if self.database.getSortOrder() == 'ascending':
                self.database.setSortOrder('descending')
                item.setIcon(QIcon(os.path.join('..', 'sources_images', 'up_arrow.png')))
            else:
                self.database.setSortOrder('ascending')
                item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))
        else:
            self.database.setSortOrder('ascending')
            item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))

        self.database.setSortedTag(tag_name)
        self.update_table()

    def sort_column(self):
        points = self.selectedItems()

        self.database.setSortOrder('ascending')
        self.database.setSortedTag('')

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            self.database.setSortedTag(tag_name)

    def sort_column_descending(self):
        points = self.selectedItems()

        self.database.setSortOrder('descending')
        self.database.setSortedTag('')

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            self.database.setSortedTag(tag_name)

    def visualized_tags_pop_up(self):
        self.pop_up = Ui_Dialog_Settings(self.database)
        self.pop_up.tab_widget.setCurrentIndex(0)

        self.pop_up.setGeometry(300, 200, 800, 600)

        if self.pop_up.exec_() == QDialog.Accepted:
            pass


    def change_cell_color(self, item_origin):
        """
        The background color of the table will change when the user changes an item
        Handles the multi-selection case
        :return:
        """

        self.itemChanged.disconnect()
        text_value = item_origin.text()

        """is_error = False
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
                # TODO: THIS HAVE TO BE IMPROVE (CHECK EACH VALUE OF THE WRITTEN LIST)
                if tp == list and (text_value[0] != '[' or text_value[-1] != ']'):
                    is_error = True
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
        else:"""

        is_error = False
        for item in self.selectedItems():
            if is_error:
                break
            row = item.row()
            col = item.column()
            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()
            # Default type is string if we don't find the real one
            if(tag_name != ""):
                tp = self.database.getTagType(tag_name)
            else:
                tp = TAG_TYPE_STRING
            if(tp == ""):
                tp = TAG_TYPE_STRING
            if(tp == TAG_TYPE_INTEGER):
                try:
                    int(text_value)
                except ValueError:
                    is_error = True
            elif (tp == TAG_TYPE_FLOAT):
                try:
                    float(text_value)
                except ValueError:
                    is_error = True
            elif (tp == TAG_TYPE_STRING):
                try:
                    str(text_value)
                except ValueError:
                    is_error = True
            elif (tp == TAG_TYPE_LIST):
                try:
                    text_value.split(",")

                except ValueError:
                    is_error = True

        if is_error:
            items = self.selectedItems()

            # Dialog that says that it is not possible
            self.pop_up_type = Ui_Dialog_Type_Problem(str(tp))
            # Resetting the cells
            self.pop_up_type.ok_signal.connect(partial(self.reset_cells_with_item, items))
            self.pop_up_type.exec()

        else:
            for item in self.selectedItems():
                row = item.row()
                col = item.column()
                scan_path = self.item(row, 0).text()
                tag_name = self.horizontalHeaderItem(col).text()

                color = QColor()

                # The scan already have a value for the tag
                if(self.database.scanHasTag(scan_path, tag_name)):
                    self.database.setTagValue(scan_path, tag_name, text_value)
                # The scan does not have a value for the tag yet
                else:
                    self.database.addValue(scan_path, tag_name, text_value)

                #User tag
                if(tag_name != "" and self.database.getTagOrigin(tag_name) == TAG_ORIGIN_RAW):
                    if str(text_value) != self.database.getValue(scan_path, tag_name).raw_value:
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

                """for scan in project._get_scans():
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
                                scan.replaceTag(new_tag, tag_name, str(tag_origin))"""

        self.itemChanged.connect(self.change_cell_color)

        #Auto-save
        config = Config()
        if (config.isAutoSave() == "yes" and not self.database.isTempProject):
            save_project(self.database)
