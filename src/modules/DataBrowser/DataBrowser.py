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
from PopUps.Ui_Dialog_remove_tag import Ui_Dialog_remove_tag
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings
from DataBrowser.CountTable import CountTable

from SoftwareProperties import Config
from ImageViewer.MiniViewer import MiniViewer

from functools import partial
from SoftwareProperties.Config import Config
from DataBase.DataBaseModel import TAG_ORIGIN_USER, TAG_ORIGIN_RAW, TAG_TYPE_STRING, TAG_TYPE_FLOAT, TAG_TYPE_INTEGER
from DataBrowser.AdvancedSearch import AdvancedSearch
from DataBrowser.ModifyTable import ModifyTable

from Utils.utils import database_to_table, table_to_database, check_value_type

not_defined_value = "*Not Defined*" # Variable shown everywhere when no value for the tag

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
        """
        Called when switching project (new, open, and save as)
        :param database: New instance of database
        :return:
        """
        # Database updated everywhere
        self.database = database
        self.table_data.database = database
        self.viewer.database = database
        self.advanced_search.database = database

        # We hide the advanced search when switching project
        self.frame_advanced_search.setHidden(True)

        #TODO update count table database???

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
            self.table_data.nb_columns = len(self.database.getVisualizedTags())
            self.table_data.setColumnCount(self.table_data.nb_columns)
            self.table_data.initialize_headers()
            self.table_data.fill_headers()
            self.table_data.update_table()

    def count_table_pop_up(self):
        pop_up = CountTable(self.database)
        pop_up.show()

        if pop_up.exec_() == QDialog.Accepted:
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
        visualized_tags_button.clicked.connect(self.visualized_tags_pop_up)

        count_table_button = QPushButton()
        count_table_button.setText('Count table')
        count_table_button.clicked.connect(self.count_table_pop_up)

        self.menu_toolbar.addWidget(tags_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.frame_test)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(advanced_search_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(visualized_tags_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(count_table_button)

    def search_str(self, str_search):

        return_list = []

        # Returns the list of scans that have at least one not defined value in the visualized tags
        if str_search == "*Not Defined*":
        # Returns the list of scans that have a match with the search in their visible tag values
            return_list = self.database.getScansMissingTags()
        elif str_search != "":
            return_list = self.database.getScansSimpleSearch(str_search)
        # Otherwise, we take every scan
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
        """
        Called when the button advanced search is called
        """
        if(self.frame_advanced_search.isHidden()):
            # If the advanced search is hidden, we reset it and display it
            self.frame_advanced_search.setHidden(False)
            self.advanced_search.show_search()
        else:
            # If the advanced search is visible, we hide it
            self.frame_advanced_search.setHidden(True)
            # We reput all the scans in the databrowser
            return_list = []
            for scan in self.database.getScans():
                return_list.append(scan.scan)
            self.table_data.scans_to_visualize = return_list
            # The table must be updated
            self.table_data.update_table()

    def add_tag_pop_up(self):

        # We first show the add_tag pop up
        self.pop_up_add_tag = Ui_Dialog_add_tag(self.database)
        self.pop_up_add_tag.show()

        # We get the values entered by the user
        if self.pop_up_add_tag.exec_() == QDialog.Accepted:
            (new_tag_name, new_default_value, type, new_tag_description, new_tag_unit) = self.pop_up_add_tag.get_values()

            values = []

            database_value = table_to_database(new_default_value)

            # We add the tag and a value for each scan in the database
            self.database.addTag(new_tag_name, True, TAG_ORIGIN_USER, type, new_tag_unit, database_value, new_tag_description)
            for scan in self.database.getScans():
                self.database.addValue(scan.scan, new_tag_name, database_value, None)
                values.append([scan.scan, new_tag_name, database_value, None]) # For history

            # For history
            historyMaker = []
            historyMaker.append("add_tag")
            historyMaker.append(new_tag_name)
            historyMaker.append(type)
            historyMaker.append(new_tag_unit)
            historyMaker.append(database_value)
            historyMaker.append(new_tag_description)
            historyMaker.append(values)
            self.database.undos.append(historyMaker)
            self.database.redos.clear()

            # Reset of headers
            self.table_data.nb_columns = len(self.database.getVisualizedTags())
            self.table_data.setColumnCount(self.table_data.nb_columns)
            self.table_data.initialize_headers()
            self.table_data.fill_headers()

            # Updating the table
            self.table_data.update_table()

    def clone_tag_pop_up(self):

        # We first show the clone_tag pop up
        self.pop_up_clone_tag = Ui_Dialog_clone_tag(self.database)
        self.pop_up_clone_tag.show()

        # We get the informations given by the user
        if self.pop_up_clone_tag.exec_() == QDialog.Accepted:
            (tag_to_clone, new_tag_name) = self.pop_up_clone_tag.get_values()

            values = []

            # We add the new tag in the database
            self.database.addTag(new_tag_name, True, TAG_ORIGIN_USER, self.database.getTagType(tag_to_clone), self.database.getTagUnit(tag_to_clone), self.database.getTagDefault(tag_to_clone), self.database.getTagDescription(tag_to_clone))
            for scan in self.database.getScans():
                # If the tag to clone has a value, we add this value with the new tag name in the database
                if(self.database.scanHasTag(scan.scan, tag_to_clone)):
                    toCloneValue = self.database.getValue(scan.scan, tag_to_clone)
                    self.database.addValue(scan.scan, new_tag_name, toCloneValue.current_value, toCloneValue.raw_value)
                    values.append([scan.scan, new_tag_name, toCloneValue.current_value, toCloneValue.raw_value])  # For history

            # For history
            historyMaker = []
            historyMaker.append("add_tag")
            historyMaker.append(new_tag_name)
            historyMaker.append(self.database.getTagType(tag_to_clone))
            historyMaker.append(self.database.getTagUnit(tag_to_clone))
            historyMaker.append(self.database.getTagDefault(tag_to_clone))
            historyMaker.append(self.database.getTagDescription(tag_to_clone))
            historyMaker.append(values)
            self.database.undos.append(historyMaker)
            self.database.redos.clear()

            # Reset of headers
            self.table_data.nb_columns = len(self.database.getVisualizedTags())
            self.table_data.setColumnCount(self.table_data.nb_columns)
            self.table_data.initialize_headers()
            self.table_data.fill_headers()

            # Updating the table
            self.table_data.update_table()

    def remove_tag_pop_up(self):

        # We first open the remove_tag pop up
        self.pop_up_remove_tag = Ui_Dialog_remove_tag(self.database)
        self.pop_up_remove_tag.show()

        # We get the tags to remove
        if self.pop_up_remove_tag.exec_() == QDialog.Accepted:
            tag_names_to_remove = self.pop_up_remove_tag.get_values()

            # For history
            historyMaker = []
            historyMaker.append("remove_tags")
            tags_removed = []

            # Each Tag object to remove is put in the history
            for tag in tag_names_to_remove:
                tagObject = self.database.getTag(tag)
                tags_removed.append(tagObject)
            historyMaker.append(tags_removed)

            # Each Value objects of the tags to remove are stored in the history
            values_removed = []
            for tag in tag_names_to_remove:
                for value in self.database.getValuesGivenTag(tag):
                    values_removed.append(value)
            historyMaker.append(values_removed)

            self.database.undos.append(historyMaker)
            self.database.redos.clear()

            # Tags removed from the database
            for tag in tag_names_to_remove:
                self.database.removeTag(tag)

            # Reset of headers
            self.table_data.nb_columns = len(self.database.getVisualizedTags())
            self.table_data.setColumnCount(self.table_data.nb_columns)
            self.table_data.initialize_headers()
            self.table_data.fill_headers()

            # Table updated
            self.table_data.update_table()

class TableDataBrowser(QTableWidget):

    def __init__(self, database):

        self.database = database
        self.flag_first_time = 0

        super().__init__()

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # The list of scans to visualize
        self.scans_to_visualize = []
        for scan in self.database.getScans():
            self.scans_to_visualize.append(scan.scan)

        # It allows to move the columns
        self.horizontalHeader().setSectionsMovable(True)

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.context_menu_table))
        self.flag_first_time = 0
        self.hh = self.horizontalHeader()
        self.hh.sectionClicked.connect(partial(self.selectAllColumn))
        self.hh.sectionDoubleClicked.connect(partial(self.sort_items))
        self.hh.sectionMoved.connect(partial(self.section_moved))

        self.update_table()

    def section_moved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        """
        Called when the columns of the databrowser are moved
        We have to ensure FileName column stays at index 0
        :param logicalIndex:
        :param oldVisualIndex: From index
        :param newVisualIndex: To index
        """

        # We need to disconnect the sectionMoved signal, otherwise infinite call to this function
        self.hh.sectionMoved.disconnect()

        if(oldVisualIndex == 0 or newVisualIndex == 0):
            # FileName column is moved, to revert because it has to stay the first column
            self.horizontalHeader().moveSection(newVisualIndex, oldVisualIndex)

        # We reconnect the signal
        self.hh.sectionMoved.connect(partial(self.section_moved))

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

        # Scans sorted
        if(self.database.getSortedTag() != ''):
            list_tags = []
            for scan in self.scans_to_visualize:
                if(self.database.scanHasTag(scan, self.database.getSortedTag())):
                    list_tags.append(self.database.getValue(scan, self.database.getSortedTag()).current_value)
                else:
                    list_tags.append(not_defined_value)

            if self.database.getSortOrder() == "ascending":
                self.scans_to_visualize = [x for _, x in sorted(zip(list_tags, self.scans_to_visualize))]
            elif self.database.getSortOrder() == "descending":
                self.scans_to_visualize = [x for _, x in sorted(zip(list_tags, self.scans_to_visualize), reverse=True)]

        self.flag_first_time += 1

        if self.flag_first_time > 1:
            self.itemChanged.disconnect()

        self.nb_columns = len(self.database.getVisualizedTags())

        self.nb_rows = len(self.database.getScans())

        self.setRowCount(self.nb_rows)

        self.setColumnCount(self.nb_columns)

        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color:rgb(255, 255, 255); background-color:rgb(250, 250, 250);")

        _translate = QtCore.QCoreApplication.translate

        if self.flag_first_time <= 1:
            self.initialize_headers()
            self.initialize_cells()

        # Sort visual management
        self.fill_headers()

        # Cells filled
        self.fill_cells_update_table()

        # Columns and rows resized
        self.resizeColumnsToContents()

        # When the user changes one item of the table, the background will change
        self.itemChanged.connect(self.change_cell_color)

        # Auto-save
        config = Config()
        if (config.isAutoSave() == "yes" and not self.database.isTempProject):
            save_project(self.database)

    def initialize_headers(self):
        # Initializing the headers for each row and each column
        item = QtWidgets.QTableWidgetItem()
        i = 0
        while i <= self.nb_columns:
            self.setHorizontalHeaderItem(i, item)
            item = QtWidgets.QTableWidgetItem()
            i += 1

    def initialize_cells(self):
        # Initializing each cell of the table
        row = (-1)

        while row < self.nb_rows:
            row += 1
            column = 0
            while column <= self.nb_columns:
                item = QtWidgets.QTableWidgetItem()
                self.setItem(row, column, item)
                column += 1

    def fill_headers(self):
        nb = 0
        for element in self.database.getVisualizedTags():
            tag_name = element.tag
            item = self.horizontalHeaderItem(nb)
            if tag_name == self.database.getSortedTag():
                if self.database.getSortOrder() == 'ascending':
                    item.setIcon(QIcon(os.path.join('..', 'sources_images', 'down_arrow.png')))
                else:
                    item.setIcon(QIcon(os.path.join('..', 'sources_images', 'up_arrow.png')))
            item.setText(tag_name)
            item.setToolTip("Description: " + str(element.description) + "\nUnit: " + str(element.unit) + "\nType: " + str(element.type))
            self.setHorizontalHeaderItem(nb, item)
            nb += 1

    def fill_cells_update_table(self):
        row = 0
        for scan in self.database.getScans():
            self.setRowHidden(row, False)
            if scan.scan not in self.scans_to_visualize:
                for searched_row in range(len(self.database.getScans())):
                    if self.item(searched_row, 0) is not None \
                            and scan.scan == self.item(searched_row, 0).text():
                        self.setRowHidden(searched_row, True)
            else:
                column = 0
                self.setRowHidden(row, False)
                while column < len(self.horizontalHeader()):
                    item = self.horizontalHeaderItem(column)
                    current_tag = item.text()
                    # The scan has a value for the tag
                    if (self.database.scanHasTag(scan.scan, current_tag)):
                        value = self.database.getValue(scan.scan, current_tag)
                        item = QTableWidgetItem()
                        if current_tag == "FileName":
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable) # FileName not editable
                        item.setText(database_to_table(value.current_value))

                        # Font reset
                        font = item.font()
                        font.setItalic(False)
                        font.setBold(False)
                        item.setFont(font)

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
                        a = str(not_defined_value)
                        item = QTableWidgetItem()
                        item.setText(a)
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)
                    self.setItem(row, column, item)
                    column += 1

            row += 1

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

        # Signals reconnected
        self.itemChanged.connect(self.change_cell_color)

        self.update_table()

    def reset_cell(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text() # We get the FileName of the scan from the first row

            if(self.database.scanHasTag(scan_name, tag_name)):
                cell = self.database.getValue(scan_name, tag_name)
                modified_values.append([scan_name, tag_name, cell.current_value, cell.raw_value]) # For history
                self.database.resetTag(scan_name, tag_name)
                self.item(row, col).setText(cell.raw_value)

                if(self.database.getTagOrigin(tag_name) == TAG_ORIGIN_RAW):
                    color = QColor()
                    if row % 2 == 1:
                        color.setRgb(255, 255, 255)
                    else:
                        color.setRgb(250, 250, 250)
                    self.item(row, col).setData(Qt.BackgroundRole, QVariant(color))

        # For history
        historyMaker.append(modified_values)
        self.database.undos.append(historyMaker)
        self.database.redos.clear()

    def reset_column(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        for point in points:
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()

            row = 0
            while row < len(self.scans_to_visualize):
                scan = self.item(row, 0).text() # We get the FileName of the scan from the first column
                if (self.database.scanHasTag(scan, tag_name)):
                    cell = self.database.getValue(scan, tag_name) # Value object of the cell
                    modified_values.append([scan, tag_name, cell.current_value, cell.raw_value]) # For history
                    self.database.resetTag(scan, tag_name)
                    self.item(row, col).setText(cell.raw_value)
                    if self.database.getTagOrigin(tag_name) == TAG_ORIGIN_RAW:
                        color = QColor()
                        if row % 2 == 1:
                            color.setRgb(255, 255, 255)
                        else:
                            color.setRgb(250, 250, 250)
                        self.item(row, col).setData(Qt.BackgroundRole, QVariant(color))
                row += 1

        # For history
        historyMaker.append(modified_values)
        self.database.undos.append(historyMaker)
        self.database.redos.clear()

    def reset_row(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        # For each selected cell
        for point in points:
            row = point.row()
            scan_name = self.item(row, 0).text() # FileName is always the first column

            column = 0
            while column < len(self.horizontalHeader()):
                tag = self.horizontalHeaderItem(column).text() # We get the tag name from the header
                if (self.database.scanHasTag(scan_name, tag)):
                    # We reset the value only if it exists
                    cell = self.database.getValue(scan_name, tag) # Value object of the cell
                    modified_values.append([scan_name, tag, cell.current_value, cell.raw_value]) # For history
                    self.database.resetTag(scan_name, tag)
                    self.item(row, column).setText(cell.raw_value)
                    if(self.database.getTagOrigin(tag) == TAG_ORIGIN_RAW):
                        color = QColor()
                        if row % 2 == 1:
                            color.setRgb(255, 255, 255)
                        else:
                            color.setRgb(250, 250, 250)
                        self.item(row, column).setData(Qt.BackgroundRole, QVariant(color))
                column += 1

        # For history
        historyMaker.append(modified_values)
        self.database.undos.append(historyMaker)
        self.database.redos.clear()

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
            if self.database.scanHasTag(scan_path, tag_name):
                item.setText(database_to_table(self.database.getValue(scan_path, tag_name).current_value))
            else:
                a = str(not_defined_value)
                item = QTableWidgetItem()
                item.setText(a)
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

            scan_object = self.database.getScan(scan_path)
            scans_removed.append(scan_object)
            for value in self.database.getValuesGivenScan(scan_path):
                values_removed.append(value)

            self.scans_to_visualize.remove(scan_path)
            self.database.removeScan(scan_path)

        historyMaker.append(scans_removed)
        historyMaker.append(values_removed)
        self.database.undos.append(historyMaker)
        self.database.redos.clear()

    def sort_items(self, col):
        """
        Manages the sort when a column is double clicked
        :param col: Column clicked to sort
        :return:
        """

        self.clearSelection() # Remove the column selection from single click
        item = self.horizontalHeaderItem(col)
        tag_name = self.horizontalHeaderItem(col).text()

        # For history
        historyMaker = []
        historyMaker.append("modified_sort")
        # Old values
        historyMaker.append(self.database.getSortedTag())
        historyMaker.append(self.database.getSortOrder())

        # Sort values updated
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

        # For history
        # New values
        historyMaker.append(self.database.getSortedTag())
        historyMaker.append(self.database.getSortOrder())
        self.database.undos.append(historyMaker)
        self.database.redos.clear()

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
            self.nb_columns = len(self.database.getVisualizedTags())
            self.setColumnCount(self.nb_columns)
            self.initialize_headers()
            self.fill_headers()

    def mouseReleaseEvent(self, e):
        """
        Called when clicking released on cells, for table change
        :param e: event
        """

        import ast

        super(TableDataBrowser, self).mouseReleaseEvent(e)

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
                tag_type = self.database.getTagType(tag_name)
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
            else:

                if len(self.coordinates) > 1:
                    list_value = []
                    i = 0
                    while i < self.table_sizes[0]:
                        list_value.append([0])
                        i += 1
                else:
                    list_value = self.old_values[0]

                # Window to change table values displayed
                pop_up = ModifyTable(self.database, list_value, self.table_types, self.table_scans, self.table_tags)
                pop_up.show()
                if pop_up.exec_() == QDialog.Accepted:
                    pass

                # For history
                historyMaker = []
                historyMaker.append("modified_values")
                modified_values = []

                # Tables updated
                i = 0
                while i < len(self.coordinates):
                    new_item = QTableWidgetItem()
                    old_value = self.old_values[i]
                    new_value = self.database.getValue(self.table_scans[i], self.table_tags[i])
                    modified_values.append([self.table_scans[i], self.table_tags[i], old_value, new_value.current_value])
                    new_item.setText(database_to_table(new_value.current_value))
                    self.setItem(self.coordinates[i][0], self.coordinates[i][1], new_item)
                    i += 1

                # For history
                historyMaker.append(modified_values)
                self.database.undos.append(historyMaker)
                self.database.redos.clear()

            self.itemChanged.connect(self.change_cell_color)

            # Auto-save
            config = Config()
            if (config.isAutoSave() == "yes" and not self.database.isTempProject):
                save_project(self.database)

        except Exception as e:
            print(e)

    def change_cell_color(self, item_origin):
        """
        The background color of the table will change when the user changes an item
        Handles the multi-selection case
        :return:
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
            scan_path = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(col).text()
            type = self.database.getTagType(tag_name)
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

                color = QColor()

                value_database = table_to_database(text_value)

                # The scan already have a value for the tag: we update it
                if(self.database.scanHasTag(scan_path, tag_name)):
                    modified_values.append([scan_path, tag_name, self.database.getValue(scan_path, tag_name).current_value, value_database])
                    self.database.setTagValue(scan_path, tag_name, value_database)
                # The scan does not have a value for the tag yet: we add it
                else:
                    modified_values.append([scan_path, tag_name, None, value_database])
                    self.database.addValue(scan_path, tag_name, value_database, value_database)

                #Raw tag
                if(self.database.getTagOrigin(tag_name) == TAG_ORIGIN_RAW):
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

                # We only set the case if it's not the tag FileName
                if(tag_name != "FileName"):
                    item.setData(Qt.BackgroundRole, QVariant(color))
                    item.setText(text_value)

                    # Font reseted in case it was a not defined cell
                    font = item.font()
                    font.setItalic(False)
                    font.setBold(False)
                    item.setFont(font)

            # For history
            historyMaker.append(modified_values)
            self.database.undos.append(historyMaker)
            self.database.redos.clear()

            # Auto-save
            config = Config()
            if (config.isAutoSave() == "yes" and not self.database.isTempProject):
                save_project(self.database)

        self.itemChanged.connect(self.change_cell_color)


