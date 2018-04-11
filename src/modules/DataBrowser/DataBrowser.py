from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QTableWidget, QHBoxLayout, QSplitter, QGridLayout
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QFrame, QToolBar, QToolButton, QAction,\
    QMessageBox, QPushButton, QProgressDialog
import os
from ProjectManager.Controller import save_project

from PopUps.Ui_Dialog_add_tag import Ui_Dialog_add_tag
from PopUps.Ui_Dialog_clone_tag import Ui_Dialog_clone_tag
from PopUps.Ui_Dialog_remove_tag import Ui_Dialog_remove_tag
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings
from PopUps.Ui_Select_Filter import Ui_Select_Filter
from PopUps.Ui_Dialog_Multiple_Sort import Ui_Dialog_Multiple_Sort
from DataBrowser.CountTable import CountTable

from SoftwareProperties import Config
from ImageViewer.MiniViewer import MiniViewer

from functools import partial
from SoftwareProperties.Config import Config
from Project.Project import Project
from populse_db.DatabaseModel import TAG_ORIGIN_USER, TAG_ORIGIN_RAW, TAG_TYPE_STRING, TAG_TYPE_FLOAT, TAG_TYPE_INTEGER
from DataBrowser.AdvancedSearch import AdvancedSearch
from DataBrowser.ModifyTable import ModifyTable

from Utils.Utils import check_value_type

from threading import Thread

import json

not_defined_value = "*Not Defined*" # Variable shown everywhere when no value for the tag

class DataBrowser(QWidget):

    def __init__(self, project):

        self.project = project

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
        self.table_data = TableDataBrowser(project, self)
        self.table_data.setObjectName("table_data")

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

        self.viewer = MiniViewer(self.project)
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
        self.advanced_search = AdvancedSearch(self.project, self)
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

        # Image viewer updated
        self.connect_viewer()

    def update_database(self, database):
        """
        Called when switching project (new, open, and save as)
        :param database: New instance of Database
        :return:
        """
        # Database updated everywhere
        self.project = database
        self.table_data.project = database
        self.viewer.project = database
        self.advanced_search.database = database
        # Update count table database?

        # We hide the advanced search when switching project
        self.frame_advanced_search.setHidden(True)

    def create_actions(self):
        self.add_tag_action = QAction("Add tag", self, shortcut="Ctrl+A")
        self.add_tag_action.triggered.connect(self.add_tag_pop_up)

        self.clone_tag_action = QAction("Clone tag", self)
        self.clone_tag_action.triggered.connect(self.clone_tag_pop_up)

        self.remove_tag_action = QAction("Remove tag", self, shortcut="Ctrl+R")
        self.remove_tag_action.triggered.connect(self.remove_tag_pop_up)

        self.save_filter_action = QAction("Save current filter", self)
        self.save_filter_action.triggered.connect(lambda : self.project.save_current_filter(self.advanced_search.get_filters()))

        self.open_filter_action = QAction("Open filter", self, shortcut="Ctrl+O")
        self.open_filter_action.triggered.connect(self.open_filter)

    def open_filter(self):
        """
        To open a project filter saved before
        """

        oldFilter = self.project.currentFilter

        self.popUp = Ui_Select_Filter(self.project)
        if self.popUp.exec_():
            pass

        filterToApply = self.project.currentFilter

        if oldFilter != filterToApply:

            self.search_bar.setText(filterToApply.search_bar)

            # We open the advanced search
            self.frame_advanced_search.setHidden(False)
            self.advanced_search.show_search()
            self.advanced_search.apply_filter(filterToApply)

    def count_table_pop_up(self):
        pop_up = CountTable(self.project)
        pop_up.show()

        if pop_up.exec_():
            pass

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

        filters_tool_button = QToolButton()
        filters_tool_button.setText('Filters')
        filters_tool_button.setPopupMode(QToolButton.MenuButtonPopup)
        filters_menu = QMenu()
        filters_menu.addAction(self.save_filter_action)
        filters_menu.addAction(self.open_filter_action)
        filters_tool_button.setMenu(filters_menu)

        self.search_bar = QtWidgets.QLineEdit(self)
        self.search_bar.setObjectName("lineEdit_search_bar")
        self.search_bar.setPlaceholderText("Rapid search, enter % to replace any string, _ to replace any character, *Not Defined* for the scans with missing value(s)")
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
        visualized_tags_button.clicked.connect(lambda : self.table_data.visualized_tags_pop_up())

        count_table_button = QPushButton()
        count_table_button.setText('Count table')
        count_table_button.clicked.connect(self.count_table_pop_up)

        self.menu_toolbar.addWidget(tags_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(filters_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.frame_test)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(advanced_search_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(visualized_tags_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(count_table_button)

    def search_str(self, str_search):

        old_scan_list = self.table_data.scans_to_visualize

        return_list = []

        # Returns the list of scans that have at least one not defined value in the visualized tags
        if str_search == "*Not Defined*":
        # Returns the list of scans that have a match with the search in their visible tag values
            return_list = self.project.getScansMissingTags()
        elif str_search != "":
            return_list = self.project.getScansSimpleSearch(str_search)
        # Otherwise, we take every scan
        else:
            return_list = self.project.getScansNames()

        self.table_data.scans_to_visualize = return_list

        # Rows updated
        self.table_data.update_visualized_rows(old_scan_list)

        self.project.currentFilter.search_bar = str_search

    def reset_search_bar(self):
        self.search_bar.setText("")

    def move_splitter(self):
        if self.splitter_vertical.sizes()[1] != self.splitter_vertical.minimumHeight():
            self.connect_viewer()
            """
            self.viewer.setHidden(False)
        else:
            self.viewer.setHidden(True)
            path_name = os.path.relpath(self.Database.folder)
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
            path_name = os.path.relpath(self.project.folder)
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
        """
        Called when the button advanced search is called
        """

        if(self.frame_advanced_search.isHidden()):
            # If the advanced search is hidden, we reset it and display it
            self.frame_advanced_search.setHidden(False)
            self.advanced_search.show_search()
        else:

            old_scans_list = self.table_data.scans_to_visualize
            # If the advanced search is visible, we hide it
            self.frame_advanced_search.setHidden(True)
            self.advanced_search.rows = []
            # We reput all the scans in the DataBrowser
            return_list = []
            for scan in self.project.getScans():
                return_list.append(scan.scan)
            self.table_data.scans_to_visualize = return_list

            self.table_data.update_visualized_rows(old_scans_list)


    def add_tag_pop_up(self):

        # We first show the add_tag pop up
        self.pop_up_add_tag = Ui_Dialog_add_tag(self.project)
        self.pop_up_add_tag.show()

        # We get the values entered by the user
        if self.pop_up_add_tag.exec_():

            (new_tag_name, new_default_value, tag_type, new_tag_description, new_tag_unit) = self.pop_up_add_tag.get_values()

            values = []

            database_value = table_to_database(new_default_value, tag_type)

            # We add the tag and a value for each scan in the Database
            self.project.addTag(new_tag_name, True, TAG_ORIGIN_USER, tag_type, new_tag_unit, database_value, new_tag_description)
            for scan in self.project.getScans():
                self.project.addValue(scan.scan, new_tag_name, database_value, None)
                values.append([scan.scan, new_tag_name, database_value, None]) # For history

            # For history
            historyMaker = []
            historyMaker.append("add_tag")
            historyMaker.append(new_tag_name)
            historyMaker.append(tag_type)
            historyMaker.append(new_tag_unit)
            historyMaker.append(database_value)
            historyMaker.append(new_tag_description)
            historyMaker.append(values)
            self.project.undos.append(historyMaker)
            self.project.redos.clear()

            # New tag added to the table
            column = self.table_data.get_index_insertion(new_tag_name)
            self.table_data.add_column(column, new_tag_name)

    def clone_tag_pop_up(self):

        # We first show the clone_tag pop up
        self.pop_up_clone_tag = Ui_Dialog_clone_tag(self.project)
        self.pop_up_clone_tag.show()

        # We get the informations given by the user
        if self.pop_up_clone_tag.exec_():

            (tag_to_clone, new_tag_name) = self.pop_up_clone_tag.get_values()

            values = []

            # We add the new tag in the Database
            tagCloned = self.project.getTag(tag_to_clone)
            self.project.addTag(new_tag_name, True, TAG_ORIGIN_USER, tagCloned.type, tagCloned.unit, tagCloned.default, tagCloned.description)
            for scan in self.project.getScans():
                # If the tag to clone has a value, we add this value with the new tag name in the Database
                if(self.project.scanHasTag(scan.scan, tag_to_clone)):
                    toCloneValue = self.project.getValue(scan.scan, tag_to_clone)
                    self.project.addValue(scan.scan, new_tag_name, toCloneValue.current_value, toCloneValue.raw_value)
                    values.append([scan.scan, new_tag_name, toCloneValue.current_value, toCloneValue.raw_value])  # For history

            # For history
            historyMaker = []
            historyMaker.append("add_tag")
            historyMaker.append(new_tag_name)
            historyMaker.append(tagCloned.type)
            historyMaker.append(tagCloned.unit)
            historyMaker.append(tagCloned.default)
            historyMaker.append(tagCloned.description)
            historyMaker.append(values)
            self.project.undos.append(historyMaker)
            self.project.redos.clear()

            # New tag added to the table
            column = self.table_data.get_index_insertion(new_tag_name)
            self.table_data.add_column(column, new_tag_name)

    def remove_tag_pop_up(self):

        # We first open the remove_tag pop up
        self.pop_up_remove_tag = Ui_Dialog_remove_tag(self.project)
        self.pop_up_remove_tag.show()

        # We get the tags to remove
        if self.pop_up_remove_tag.exec_():

            self.table_data.itemSelectionChanged.disconnect()

            tag_names_to_remove = self.pop_up_remove_tag.get_values()

            # For history
            historyMaker = []
            historyMaker.append("remove_tags")
            tags_removed = []

            # Each Tag object to remove is put in the history
            for tag in tag_names_to_remove:
                tagObject = self.project.database.get_tag(tag)
                tags_removed.append(tagObject)
            historyMaker.append(tags_removed)

            # Each Value objects of the tags to remove are stored in the history
            values_removed = []
            for tag in tag_names_to_remove:
                for value in self.project.getValuesGivenTag(tag):
                    values_removed.append(value)
            historyMaker.append(values_removed)

            self.project.undos.append(historyMaker)
            self.project.redos.clear()

            # Tags removed from the Database and table
            for tag in tag_names_to_remove:
                self.project.removeTag(tag)
                self.table_data.removeColumn(self.table_data.get_tag_column(tag))

            # Selection updated
            self.table_data.update_selection()

            self.table_data.itemSelectionChanged.connect(self.table_data.selection_changed)

class TableDataBrowser(QTableWidget):

    def __init__(self, project, parent):

        self.project = project
        self.parent = parent

        super().__init__()

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # It allows to move the columns (except FileName)
        self.horizontalHeader().setSectionsMovable(True)

        # It allows the automatic sort
        self.setSortingEnabled(True)

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.context_menu_table))
        self.horizontalHeader().sortIndicatorChanged.connect(partial(self.sort_updated))
        self.horizontalHeader().sectionDoubleClicked.connect(partial(self.selectAllColumn))
        self.horizontalHeader().sectionMoved.connect(partial(self.section_moved))
        self.itemChanged.connect(self.change_cell_color)
        self.itemSelectionChanged.connect(self.selection_changed)

        self.update_table()

    def add_column(self, column, tag):

        self.itemChanged.disconnect()

        self.itemSelectionChanged.disconnect()

        # Adding the column to the table
        self.insertColumn(column)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(column, item)
        tag_object = self.project.getTag(tag)
        item.setText(tag)
        item.setToolTip(
            "Description: " + str(tag_object.description) + "\nUnit: " + str(tag_object.unit) + "\nType: " + str(
                tag_object.type))
        row = 0
        while row < self.rowCount():
            item = QtWidgets.QTableWidgetItem()
            self.setItem(row, column, item)
            scan = self.item(row, 0).text()
            self.update_color(scan, tag, item, row)
            if self.project.scanHasTag(scan, tag):
                item.setData(QtCore.Qt.EditRole, QtCore.QVariant(
                    database_to_table(self.project.getValue(scan, tag).current_value)))
            else:
                item.setData(QtCore.Qt.EditRole, QtCore.QVariant(not_defined_value))
                font = item.font()
                font.setItalic(True)
                font.setBold(True)
                item.setFont(font)
            row += 1

        self.resizeColumnsToContents()  # New column resized

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def sort_updated(self, column, order):
        """
        Called when the sort is updated
        :param column: Column being sorted
        :param order: New order
        """

        # Auto-save
        config = Config()

        if column != -1:
            self.project.setSortOrder(int(order))
            self.project.setSortedTag(self.horizontalHeaderItem(column).text())

            if config.isAutoSave() == "yes" and not self.project.isTempProject:
                save_project(self.project)

    def update_selection(self):
        """
        Called after searches to update the selection
        """

        # Selection updated
        self.clearSelection()

        for scan in self.selected_scans:
            scan_selected = scan[0]
            row = self.get_scan_row(scan_selected)
            # We select the columns of the row if it was selected
            tags = scan[1]
            for tag in tags:
                if self.get_tag_column(tag) != None:
                    item_to_select = self.item(row, self.get_tag_column(tag))
                    item_to_select.setSelected(True)

    def selection_changed(self):
        """
        Called when the selection is changed
        """

        # List of selected scans updated
        self.selected_scans.clear()

        for point in self.selectedItems():
            row = point.row()
            column = point.column()
            scan_name = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(column).text()
            scan_already_in_list = False
            for scan in self.selected_scans:
                if scan[0] == scan_name:
                    # Scan already in the list, we append the column
                    scan[1].append(tag_name)
                    scan_already_in_list = True
                    break

            if not scan_already_in_list:
                # Scan not in the list, we add it
                self.selected_scans.append([scan_name, [tag_name]])

        # ImageViewer updated
        self.parent.connect_viewer()

    def section_moved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        """
        Called when the columns of the DataBrowser are moved
        We have to ensure FileName column stays at index 0
        :param logicalIndex:
        :param oldVisualIndex: From index
        :param newVisualIndex: To index
        """

        self.itemSelectionChanged.disconnect()

        # We need to disconnect the sectionMoved signal, otherwise infinite call to this function
        self.horizontalHeader().sectionMoved.disconnect()

        if oldVisualIndex == 0 or newVisualIndex == 0:
            # FileName column is moved, to revert because it has to stay the first column
            self.horizontalHeader().moveSection(newVisualIndex, oldVisualIndex)

        # We reconnect the signal
        self.horizontalHeader().sectionMoved.connect(partial(self.section_moved))

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.update()

    def selectAllColumn(self, col):
        """
        Called when single clicking on the column header to select the whole column
        :param col: Column to select
        """

        self.clearSelection()
        self.selectColumn(col)

    def selectAllColumns(self):
        """
        Called from context menu to select the columns
        """

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
        Only called when switching project to completely reset the table
        """

        self.setSortingEnabled(False)

        self.clearSelection() # Selection cleared when switching project

        # The list of scans to visualize
        self.scans_to_visualize = self.project.database.get_scans_names()

        # The list of selected scans
        self.selected_scans = []

        self.itemChanged.disconnect()

        self.setRowCount(len(self.scans_to_visualize))

        self.setColumnCount(len(self.project.database.get_tags_names()))

        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color:rgb(255, 255, 255); background-color:rgb(250, 250, 250);")

        _translate = QtCore.QCoreApplication.translate

        # Sort visual management
        self.fill_headers()

        # Cells filled
        self.fill_cells_update_table()

        # Saved sort applied if it exists
        self.setSortingEnabled(True)
        tag_to_sort = self.project.getSortedTag()
        column_to_sort = self.get_tag_column(tag_to_sort)
        sort_order = self.project.getSortOrder()

        if column_to_sort != None:
            self.horizontalHeader().setSortIndicator(column_to_sort, sort_order)
        else:
            self.horizontalHeader().setSortIndicator(0, 0)

        # Columns and rows resized
        self.resizeColumnsToContents()

        # When the user changes one item of the table, the background will change
        self.itemChanged.connect(self.change_cell_color)

    def fill_headers(self):
        """
        To initialize and fill the headers of the table
        """

        # Sorting the list of tags in alphabetical order, but keeping FileName first
        tags = self.project.database.get_tags_names()
        tags.remove("FileName")
        tags = sorted(tags)
        tags.insert(0, "FileName")

        column = 0
        # Filling the headers
        for tag_name in tags:
            element = self.project.database.get_tag(tag_name)
            item = QtWidgets.QTableWidgetItem()
            self.setHorizontalHeaderItem(column, item)
            item.setText(tag_name)
            item.setToolTip("Description: " + str(element.description) + "\nUnit: " + str(element.unit) + "\nType: " + str(element.type))
            self.setHorizontalHeaderItem(column, item)

            # Hide the column if not visible
            if element.visible == False:
                self.setColumnHidden(column, True)

            else:
                self.setColumnHidden(column, False)

            column += 1

    def fill_cells_update_table(self):
        """
        To initialize and fill the cells of the table
        """

        # Progressbar
        len_scans = len(self.scans_to_visualize)
        ui_progressbar = QProgressDialog("Filling the table", "Cancel", 0, len_scans)
        ui_progressbar.setWindowModality(Qt.WindowModal)
        ui_progressbar.setWindowTitle("")
        idx = 0

        row = 0
        for scan in self.scans_to_visualize:

            # Progressbar
            idx += 1
            ui_progressbar.setValue(idx)
            column = 0

            while column < len(self.horizontalHeader()):
                current_tag = self.horizontalHeaderItem(column).text()

                item = QTableWidgetItem()

                # The scan has a value for the tag
                if self.project.scanHasTag(scan, current_tag):
                    value = self.project.getValue(scan, current_tag)
                    if current_tag == "FileName":
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # FileName not editable
                    else:
                        self.update_color(scan, current_tag, item, row)
                    item.setData(QtCore.Qt.EditRole,QtCore.QVariant(database_to_table(value.current_value)))

                # The scan does not have a value for the tag
                else:
                    item.setData(QtCore.Qt.EditRole, QtCore.QVariant(not_defined_value))
                    font = item.font()
                    font.setItalic(True)
                    font.setBold(True)
                    item.setFont(font)
                self.setItem(row, column, item)
                column += 1
            row += 1

        ui_progressbar.close()

    def update_color(self, scan, tag, item, row):
        """ Method that changes the background of a cell depending on
        its row and its tag value. """

        color = QColor()
        # Raw tag
        if self.project.database.get_tag(tag).origin == TAG_ORIGIN_RAW:
            if self.project.database.is_value_modified(scan, tag):
                if row % 2 == 1:
                    color.setRgb(240, 240, 255)
                else:
                    color.setRgb(225, 225, 255)
            else:
                if row % 2 == 1:
                    color.setRgb(255, 255, 255)
                else:
                    color.setRgb(250, 250, 250)

        # User tag
        elif self.project.database.get_tag(tag).origin == TAG_ORIGIN_USER:
            if row % 2 == 1:
                color.setRgb(255, 240, 240)
            else:
                color.setRgb(255, 225, 225)

        else:
            if row % 2 == 1:
                color.setRgb(255, 255, 255)
            else:
                color.setRgb(250, 250, 250)

        item.setData(Qt.BackgroundRole, QtCore.QVariant(color))

    def context_menu_table(self, position):

        self.itemChanged.disconnect()

        menu = QMenu(self)

        action_reset_cell = menu.addAction("Reset cell(s)")
        action_reset_column = menu.addAction("Reset column(s)")
        action_reset_row = menu.addAction("Reset row(s)")
        action_remove_scan = menu.addAction("Remove scan(s)")
        action_sort_column = menu.addAction("Sort column")
        action_sort_column_descending = menu.addAction("Sort column (descending)")
        action_visualized_tags = menu.addAction("Visualized tags")
        action_select_column = menu.addAction("Select column(s)")
        action_multiple_sort = menu.addAction("Multiple sort")

        action = menu.exec_(self.mapToGlobal(position))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if action == action_reset_cell:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.reset_cell)
            msg.exec()
        elif action == action_reset_column:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.reset_column)
            msg.exec()
        elif action == action_reset_row:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.reset_row)
            msg.exec()
        elif action == action_remove_scan:
            msg.setText("You are about to remove a scan from the project.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.remove_scan)
            msg.exec()
        elif action == action_sort_column:
            self.sort_column()
        elif action == action_sort_column_descending:
            self.sort_column_descending()
        elif action == action_visualized_tags:
            self.visualized_tags_pop_up()
        elif action == action_select_column:
            self.selectAllColumns()
        elif action == action_multiple_sort:
            self.multiple_sort_pop_up()

        # Signals reconnected
        self.itemChanged.connect(self.change_cell_color)

    def sort_column(self):
        """
        Sorts the current column in ascending order
        """

        self.itemSelectionChanged.disconnect()

        self.horizontalHeader().setSortIndicator(self.currentItem().column(), 0)

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

    def sort_column_descending(self):
        """
        Sorts the current column in descending order
        """

        self.itemSelectionChanged.disconnect()

        self.horizontalHeader().setSortIndicator(self.currentItem().column(), 1)

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

    def get_tag_column(self, tag):
        """
        Returns the column index of the tag
        :param tag:tag name
        :return:index of the column of the tag
        """

        column = 0
        while column < self.columnCount():
            item = self.horizontalHeaderItem(column)
            tag_name = item.text()
            if tag_name == tag:
                return column
            column += 1

    def get_scan_row(self, scan):
        """
        Returns the row index of the scan
        :param scan:Scan FileName
        :return:index of the row of the scan
        """

        row = 0
        while row < self.rowCount():
            item = self.item(row, 0)
            scan_name = item.text()
            if scan_name == scan:
                return row
            row += 1

    def reset_cell(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        has_unreset_values = False # To know if some values do not have raw values (user tags)

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text() # We get the FileName of the scan from the first row

            current_value = self.project.database.get_current_value(scan_name, tag_name)
            initial_value = self.project.database.get_initial_value(scan_name, tag_name)
            if initial_value is not None:
                modified_values.append([scan_name, tag_name, current_value, initial_value]) # For history
                self.project.database.reset_value(scan_name, tag_name)
                # has_unreset_values = True TODO if value not reset
                self.update_color(scan_name, tag_name, self.item(row, col), row)
                self.item(row, col).setData(QtCore.Qt.EditRole, QtCore.QVariant(str(initial_value)))
            else:
                has_unreset_values = True

        # For history
        historyMaker.append(modified_values)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        # Warning message if unreset values
        if has_unreset_values:
            self.display_unreset_values()

        self.resizeColumnsToContents()

    def reset_column(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        has_unreset_values = False  # To know if some values do not have raw values (user tags)

        for point in points:
            col = point.column()
            row = point.row()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()  # We get the FileName of the scan from the first row

            row = 0
            while row < len(self.scans_to_visualize):
                scan = self.item(row, 0).text() # We get the FileName of the scan from the first column
                initial_value = self.project.database.get_initial_value(scan, tag_name)
                current_value = self.project.database.get_current_value(scan, tag_name)
                if initial_value is not None:
                    modified_values.append([scan, tag_name, current_value, initial_value]) # For history
                    self.project.database.reset_value(scan, tag_name)
                    # has_unreset_values = True TODO if not reset
                    self.item(row, col).setData(QtCore.Qt.EditRole, QtCore.QVariant(str(initial_value)))
                    self.update_color(scan, tag_name, self.item(row, col), row)
                else:
                    has_unreset_values = True
                row += 1

        # For history
        historyMaker.append(modified_values)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        # Warning message if unreset values
        if has_unreset_values:
            self.display_unreset_values()

        self.resizeColumnsToContents()

    def reset_row(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        has_unreset_values = False  # To know if some values do not have raw values (user tags)

        # For each selected cell
        for point in points:
            row = point.row()
            scan_name = self.item(row, 0).text() # FileName is always the first column

            column = 0
            while column < len(self.horizontalHeader()):
                tag = self.horizontalHeaderItem(column).text() # We get the tag name from the header
                current_value = self.project.database.get_initial_value(scan_name, tag)
                initial_value = self.project.database.get_current_value(scan_name, tag)
                if initial_value is not None:
                    # We reset the value only if it exists
                    modified_values.append([scan_name, tag, current_value, initial_value]) # For history
                    self.project.database.reset_value(scan_name, tag)
                    #has_unreset_values = True TODO if not reset
                    self.item(row, column).setData(QtCore.Qt.EditRole, QtCore.QVariant(str(initial_value)))
                    self.update_color(scan_name, tag, self.item(row, column), row)
                else:
                    has_unreset_values = True
                column += 1

        # For history
        historyMaker.append(modified_values)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        # Warning message if unreset values
        if has_unreset_values:
            self.display_unreset_values()

        self.resizeColumnsToContents()

    def display_unreset_values(self):
        """
        Error message when trying to reset user tags
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Some values do not have a raw value")
        msg.setInformativeText(
            "Some values have not been reset because they do not have a raw value.\nIt is the case for the user tags, FileName and the cells not defined.")
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(msg.close)
        msg.exec()

    def reset_cells_with_item(self, items_in):

        for item_in in items_in:
            row = item_in.row()
            col = item_in.column()

            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()

            item = QTableWidgetItem()
            value = self.project.database.get_current_value(scan_path, tag_name)
            if value is not None:
                item.setData(QtCore.Qt.EditRole, QtCore.QVariant(str(value)))
            else:
                item = QTableWidgetItem()
                item.setData(QtCore.Qt.EditRole, QtCore.QVariant(not_defined_value))
                font = item.font()
                font.setItalic(True)
                font.setBold(True)
                item.setFont(font)
            self.setItem(row, col, item)

    def remove_scan(self):

        points = self.selectedIndexes()

        historyMaker = []
        historyMaker.append("remove_scans")
        scans_removed = []
        values_removed = []

        for point in points:
            row = point.row()
            scan_path = self.item(row, 0).text()

            scan_object = self.project.getScan(scan_path)
            scans_removed.append(scan_object)
            for value in self.project.getValuesGivenScan(scan_path):
                values_removed.append(value)

            self.scans_to_visualize.remove(scan_path)
            self.project.removeScan(scan_path)

        for scan in scans_removed:
            scan_name = scan.scan
            self.removeRow(self.get_scan_row(scan_name))

        historyMaker.append(scans_removed)
        historyMaker.append(values_removed)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        self.resizeColumnsToContents()

    def visualized_tags_pop_up(self):
        old_tags = self.project.database.get_visualized_tags() # Old list of columns
        self.pop_up = Ui_Dialog_Settings(self.project)
        self.pop_up.tab_widget.setCurrentIndex(0)

        self.pop_up.setGeometry(300, 200, 800, 600)

        if self.pop_up.exec_():

            self.update_visualized_columns(old_tags) # Columns updated

    def multiple_sort_pop_up(self):
        pop_up = Ui_Dialog_Multiple_Sort(self.project)
        if pop_up.exec_():

            self.itemSelectionChanged.disconnect()

            list_tags_name = pop_up.list_tags
            list_tags = []
            for tag_name in list_tags_name:
                list_tags.append(self.project.getTag(tag_name))
            list_sort = []
            for scan in self.scans_to_visualize:
                tags_value = []
                for tag in list_tags:
                    if self.project.scanHasTag(scan, tag.tag):
                        tags_value.append(self.project.getValue(scan, tag.tag).current_value)
                    else:
                        tags_value.append(not_defined_value)
                list_sort.append(tags_value)

            if pop_up.order == "Descending":
                self.scans_to_visualize = [x for _, x in sorted(zip(list_sort, self.scans_to_visualize), reverse=True)]
            else:
                self.scans_to_visualize = [x for _, x in sorted(zip(list_sort, self.scans_to_visualize))]


            # Table updated
            self.setSortingEnabled(False)
            row = 0
            while row < self.rowCount():
                scan = self.scans_to_visualize[row]
                old_row = self.get_scan_row(scan)
                if old_row != row:
                    column = 0
                    while column < self.columnCount():
                        item_to_move = self.takeItem(old_row, column)
                        item_wrong_row = self.takeItem(row, column)
                        self.setItem(row, column, item_to_move)
                        self.setItem(old_row, column, item_wrong_row)
                        column += 1
                row += 1
            self.horizontalHeader().setSortIndicator(-1, 0)
            self.setSortingEnabled(True)

            # Selection updated
            self.update_selection()

            self.itemSelectionChanged.connect(self.selection_changed)

    def update_visualized_rows(self, old_scans):
        """
        Called after a search to update the list of scans in the table
        :param old_scans: Old list of scans
        """

        self.itemSelectionChanged.disconnect()

        # Scans that are not visible anymore are hidden
        for scan in old_scans:
            if not scan in self.scans_to_visualize:
                self.setRowHidden(self.get_scan_row(scan), True)

        # Scans that became visible must be visible
        for scan in self.scans_to_visualize:
            self.setRowHidden(self.get_scan_row(scan), False)

        self.resizeColumnsToContents() # Columns resized

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

    def update_visualized_columns(self, old_tags):
        """
        Called to set the visualized tags in the table
        :param old_tags: Old list of visualized tags
        """

        self.itemSelectionChanged.disconnect()

        # Tags that are not visible anymore are hidden
        for tag in old_tags:
            if not self.project.database.get_tag(tag).visible:
                self.setColumnHidden(self.get_tag_column(tag), True)

        # Tags that became visible must be visible
        for tag in self.project.database.get_visualized_tags():
            self.setColumnHidden(self.get_tag_column(tag), False)

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.resizeColumnsToContents()

    def add_rows(self, rows):
        """
        Inserts rows in the table if they are not already in the table
        :param rows: List of all scans
        """

        self.setSortingEnabled(False)

        self.itemSelectionChanged.disconnect()

        self.itemChanged.disconnect()

        # Progressbar
        len_rows = len(rows)
        ui_progressbar = QProgressDialog("Reading exported files", "Cancel", 0, len_rows)
        ui_progressbar.setWindowTitle("")
        ui_progressbar.setWindowModality(Qt.WindowModal)
        idx = 0

        for scan in rows:

            # Progressbar
            idx += 1
            ui_progressbar.setValue(idx)
            if ui_progressbar.wasCanceled():
                break

            # Scan added only if it's not already in the table
            if self.get_scan_row(scan) is None:
                rowCount = self.rowCount()
                self.insertRow(rowCount)

                # Columns filled for the row being added
                column = 0
                while column < self.columnCount():
                    item = QtWidgets.QTableWidgetItem()
                    tag = self.horizontalHeaderItem(column).text()
                    if self.project.database.get_current_value(scan, tag) is not None:
                        item.setData(QtCore.Qt.EditRole, QtCore.QVariant(str(self.project.database.get_current_value(scan, tag))))
                    else:
                        item.setData(QtCore.Qt.EditRole, QtCore.QVariant(not_defined_value))
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)
                    if column != 0:
                        self.update_color(scan, tag, item, rowCount)
                    self.setItem(rowCount, column, item)
                    column += 1

        ui_progressbar.close()

        self.setSortingEnabled(True)

        self.resizeColumnsToContents()

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def get_index_insertion(self, to_insert):
        """
        To get index insertion of a new column, since it's already sorted in alphabetical order
        :param to_insert: tag to insert
        """

        i = 1
        while i < len(self.horizontalHeader()):
            if self.horizontalHeaderItem(i).text() > to_insert:
                return i
            i +=1
        return self.columnCount()

    def add_columns(self):
        """
        To add the new tags
        """

        self.itemChanged.disconnect()

        self.itemSelectionChanged.disconnect()

        # Adding missing columns
        for tag in self.project.database.get_tags():

            # Tag added only if it's not already in the table
            if self.get_tag_column(tag.name) is None:

                columnIndex = self.get_index_insertion(tag.name)
                self.insertColumn(columnIndex)

                item = QtWidgets.QTableWidgetItem()
                self.setHorizontalHeaderItem(columnIndex, item)
                item.setText(tag.name)
                item.setToolTip("Description: " + str(tag.description) + "\nUnit: " + str(tag.unit) + "\nType: " + str(tag.type))

                # Rows filled for the column being added
                row = 0
                while row < self.rowCount():
                    item = QtWidgets.QTableWidgetItem()
                    self.setItem(row, columnIndex, item)
                    scan = self.item(row, 0).text()
                    if self.project.database.get_current_value(scan, tag.name) is not None:
                        item.setData(QtCore.Qt.EditRole, QtCore.QVariant(self.project.get_current_value(scan, tag.name)))
                    else:
                        item.setData(QtCore.Qt.EditRole, QtCore.QVariant(not_defined_value))
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)
                    row += 1

                # Hide the column if not visible
                if tag.visible == False:
                    self.setColumnHidden(columnIndex, True)

        # Removing useless columns
        column = 0
        tags_to_remove = []
        while column < self.columnCount():
            tag_name = self.horizontalHeaderItem(column).text()
            if not tag_name in self.project.database.get_tags_names():
                tags_to_remove.append(tag_name)
            column += 1

        for tag in tags_to_remove:
            self.removeColumn(self.get_tag_column(tag))

        self.resizeColumnsToContents()

        # Selection updated
        self.update_selection()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def mouseReleaseEvent(self, e):
        """
        Called when clicking released on cells, for table changes
        :param e: event
        """

        import ast

        super(TableDataBrowser, self).mouseReleaseEvent(e)

        self.setMouseTracking(False)

        self.coordinates = [] # Coordinates of selected cells stored
        self.old_values = [] # Old values stored
        self.table_types = []  # List of types
        self.table_sizes = []  # List of lengths
        self.table_scans = []  # List of table scans
        self.table_tags = []  # List of table tags

        try:

            for item in self.selectedItems():
                column = item.column()
                row = item.row()
                self.coordinates.append([row, column])
                tag_name = self.horizontalHeaderItem(column).text()
                tag_type = self.project.getTagType(tag_name)
                scan_name = self.item(row, 0).text()

                # Scan and tag added
                self.table_tags.append(tag_name)
                self.table_scans.append(scan_name)

                # Type checked
                if not tag_type in self.table_types:
                    self.table_types.append(tag_type)

                # Length checked
                text = item.text()

                list_value = ast.literal_eval(text)
                if isinstance(list_value, list):

                    self.old_values.append(list_value)

                    size = len(list_value)
                    if size not in self.table_sizes:
                        self.table_sizes.append(size)

                else:
                    self.setMouseTracking(True)
                    return

            # Error if tables of different sizes
            if len(self.table_sizes) > 1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Incompatible table sizes")
                msg.setInformativeText("The tables can't have different sizes")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()

            # Ok
            elif len(self.old_values) > 0:

                if len(self.coordinates) > 1:
                    list_value = []
                    i = 0
                    while i < self.table_sizes[0]:
                        list_value.append([0])
                        i += 1
                else:
                    list_value = self.old_values[0]

                # Window to change table values displayed
                pop_up = ModifyTable(self.project, list_value, self.table_types, self.table_scans, self.table_tags)
                pop_up.show()
                if pop_up.exec_():
                    pass

                # For history
                historyMaker = []
                historyMaker.append("modified_values")
                modified_values = []

                self.itemChanged.disconnect()

                # Tables updated
                i = 0
                while i < len(self.coordinates):
                    new_item = QTableWidgetItem()
                    old_value = self.old_values[i]
                    new_value = self.project.getValue(self.table_scans[i], self.table_tags[i])
                    modified_values.append([self.table_scans[i], self.table_tags[i], old_value, new_value.current_value])
                    new_item.setData(QtCore.Qt.EditRole, QtCore.QVariant(database_to_table(new_value.current_value)))
                    self.setItem(self.coordinates[i][0], self.coordinates[i][1], new_item)
                    i += 1

                # For history
                historyMaker.append(modified_values)
                self.project.undos.append(historyMaker)
                self.project.redos.clear()

                self.itemChanged.connect(self.change_cell_color)

            self.setMouseTracking(True)

            # Auto-save
            config = Config()
            if config.isAutoSave() == "yes" and not self.project.isTempProject:
                save_project(self.project)

            self.resizeColumnsToContents()  # Columns resized

        except Exception as e:
            self.setMouseTracking(True)

    def change_cell_color(self, item_origin):
        """
        The background color and the value of the cells will change when the user changes an item
        Handles the multi-selection case
        """

        import ast

        self.itemChanged.disconnect()
        text_value = item_origin.text()

        cells_types = [] # Will contain the type list of the selection

        self.reset_cells_with_item(self.selectedItems()) # To reset the first cell already changed

        # For each item selected, we check the validity of the types
        for item in self.selectedItems():
            row = item.row()
            col = item.column()
            color = QColor()
            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()
            type = self.project.database.get_tag(tag_name).type
            old_value = item.text()

            # Type check
            try:
                list_value = ast.literal_eval(old_value)
                if isinstance(list_value, list):
                    if not "table" in cells_types:
                        cells_types.append("table")
                else:
                    if not type in cells_types:
                        cells_types.append(type)
            except:
                if not type in cells_types:
                    cells_types.append(type)

        # Error if table with other types
        if "table" in cells_types and len(cells_types) > 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Incompatible types")
            msg.setInformativeText("The following types in the selection are not compatible: " + str(cells_types))
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            self.itemChanged.connect(self.change_cell_color)
            return

        # Nothing to do if table
        if "table" in cells_types:
            self.itemChanged.connect(self.change_cell_color)
            return

        # We check that the value is compatible with all the types
        types_compatibles = True
        for cell_type in cells_types:
            if not check_value_type(text_value, cell_type):
                types_compatibles = False
                type_problem = cell_type
                break

        # Error if invalid value
        if not types_compatibles:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Invalid value")
            msg.setInformativeText("The value " + text_value + " is invalid with the type " + type_problem)
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()

        # Otherwise we update the values
        else:

            # For history
            historyMaker = []
            historyMaker.append("modified_values")
            modified_values = []

            for item in self.selectedItems():
                row = item.row()
                col = item.column()
                scan_path = self.item(row, 0).text()
                tag_name = self.horizontalHeaderItem(col).text()

                # We only set the case if it's not the tag FileName
                if (tag_name != "FileName"):

                    old_value = self.project.database.get_current_value(scan_path, tag_name)
                    # The scan already has a value for the tag: we update it
                    if old_value is not  None:
                        modified_values.append([scan_path, tag_name, old_value, text_value])
                        self.project.database.set_value(scan_path, tag_name, text_value)
                    # The scan does not have a value for the tag yet: we add it
                    else:
                        modified_values.append([scan_path, tag_name, None, text_value])
                        self.project.database.add_value(scan_path, tag_name, text_value, text_value)

                        # Font reset in case it was a not defined cell
                        font = item.font()
                        font.setItalic(False)
                        font.setBold(False)
                        item.setFont(font)

                    self.update_color(scan_path, tag_name, item, row)

                    item.setData(QtCore.Qt.EditRole, QtCore.QVariant(str(text_value)))

            # For history
            historyMaker.append(modified_values)
            self.project.undos.append(historyMaker)
            self.project.redos.clear()

            # Auto-save
            config = Config()
            if config.isAutoSave() == "yes" and not self.project.isTempProject:
                save_project(self.project)

            self.resizeColumnsToContents() # Columns resized

        self.itemChanged.connect(self.change_cell_color)


