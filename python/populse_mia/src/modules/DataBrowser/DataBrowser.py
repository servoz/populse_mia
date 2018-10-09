##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import ast
import os
from functools import partial

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QFrame, QToolBar, QToolButton, QAction, QMessageBox, QPushButton, \
    QProgressDialog, QDoubleSpinBox, QDateTimeEdit, QDateEdit, QTimeEdit, QApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHBoxLayout, QSplitter, QGridLayout, QItemDelegate, QAbstractItemView

from DataBrowser.RapidSearch import RapidSearch
from DataBrowser.AdvancedSearch import AdvancedSearch
from DataBrowser.CountTable import CountTable
from DataBrowser.ModifyTable import ModifyTable
from ImageViewer.MiniViewer import MiniViewer
from PopUps.Ui_Dialog_Multiple_Sort import Ui_Dialog_Multiple_Sort
from PopUps.Ui_Dialog_Settings import Ui_Dialog_Settings
from PopUps.Ui_Dialog_Show_Brick import Ui_Dialog_Show_Brick
from PopUps.Ui_Dialog_add_path import Ui_Dialog_add_path
from PopUps.Ui_Dialog_add_tag import Ui_Dialog_add_tag
from PopUps.Ui_Dialog_clone_tag import Ui_Dialog_clone_tag
from PopUps.Ui_Dialog_remove_tag import Ui_Dialog_remove_tag
from PopUps.Ui_Select_Filter import Ui_Select_Filter
import PopUps.Ui_DataBrowser_Current_Selection
from ProjectManager.Controller import save_project
from SoftwareProperties import Config
from SoftwareProperties.Config import Config
from Utils.Tools import ClickableLabel
from Utils.Utils import check_value_type, set_item_data, table_to_database
from Project.Project import COLLECTION_CURRENT, COLLECTION_INITIAL, COLLECTION_BRICK, TAG_CHECKSUM, TAG_FILENAME, \
    TAG_BRICKS, BRICK_NAME
from Project.database_mia import TAG_ORIGIN_BUILTIN, TAG_ORIGIN_USER
from populse_db.database import FIELD_TYPE_STRING, FIELD_TYPE_FLOAT, FIELD_TYPE_DATETIME, FIELD_TYPE_DATE, \
    FIELD_TYPE_TIME, FIELD_TYPE_LIST_DATE, FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_TIME, FIELD_TYPE_LIST_INTEGER, \
    FIELD_TYPE_LIST_STRING, FIELD_TYPE_LIST_FLOAT, FIELD_TYPE_LIST_BOOLEAN, LIST_TYPES

not_defined_value = "*Not Defined*"  # Variable shown everywhere when no value for the tag

class NumberFormatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        data = index.data(Qt.EditRole)
        decimals_number = str(data)[::-1].find('.')
        editor.setMaximum(10 ** 10)
        editor.setDecimals(decimals_number)
        return editor


class DateTimeFormatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QDateTimeEdit(parent)
        editor.setDisplayFormat("dd/MM/yyyy hh:mm:ss.zzz")
        return editor


class DateFormatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QDateEdit(parent)
        editor.setDisplayFormat("dd/MM/yyyy")
        return editor


class TimeFormatDelegate(QItemDelegate):
    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QTimeEdit(parent)
        editor.setDisplayFormat("hh:mm:ss.zzz")
        return editor

class DataBrowser(QWidget):

    def __init__(self, project, main_window):

        self.project = project
        self.main_window = main_window

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
        self.table_data = TableDataBrowser(project, self, self.project.session.get_visibles(), True, True)
        self.table_data.setObjectName("table_data")

        ## LAYOUTS ##

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(self.table_data)

        # Add path button under the table
        hbox_layout = QHBoxLayout()

        self.addRowLabel = ClickableLabel()
        self.addRowLabel.setObjectName('plus')
        addRowPicture = QPixmap(os.path.relpath(os.path.join("..", "sources_images", "green_plus.png")))
        addRowPicture = addRowPicture.scaledToHeight(20)
        self.addRowLabel.setPixmap(addRowPicture)
        self.addRowLabel.setFixedWidth(20)
        self.addRowLabel.clicked.connect(self.table_data.add_path)

        hbox_layout.addWidget(self.addRowLabel)

        hbox_layout.addStretch(1)

        self.send_documents_to_pipeline_button = QPushButton("Send documents to the Pipeline Manager")
        self.send_documents_to_pipeline_button.clicked.connect(self.send_documents_to_pipeline)
        hbox_layout.addWidget(self.send_documents_to_pipeline_button)

        vbox_table.addLayout(hbox_layout)

        self.frame_table_data.setLayout(vbox_table)

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

    def send_documents_to_pipeline(self):
        """
        Send the current list of scans to the Pipeline Manager
        """

        current_scans = self.table_data.get_current_filter()

        # Displays a popup with the list of scans

        self.show_selection = PopUps.Ui_DataBrowser_Current_Selection.Ui_DataBrowser_Current_Selection(self.project, self, current_scans, self.main_window)
        self.show_selection.show()

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
        self.advanced_search.project = database
        # TODO update count table database?

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
        self.save_filter_action.triggered.connect(
            lambda: self.project.save_current_filter(self.advanced_search.get_filters(False)))

        self.open_filter_action = QAction("Open filter", self, shortcut="Ctrl+O")
        self.open_filter_action.triggered.connect(self.open_filter)

    def open_filter(self):
        """
        To open a project filter saved before
        """

        self.popUp = Ui_Select_Filter(self.project, self)
        self.popUp.show()

    def open_filter_infos(self):

        filterToApply = self.project.currentFilter

        # We open the advanced search + search_bar
        old_scans = self.table_data.scans_to_visualize
        documents = self.project.session.get_documents_names(COLLECTION_CURRENT)
        self.table_data.scans_to_visualize = documents
        self.table_data.scans_to_search = documents
        self.table_data.update_visualized_rows(old_scans)

        self.search_bar.setText(filterToApply.search_bar)

        if len(filterToApply.nots) > 0:
            self.frame_advanced_search.setHidden(False)
            self.advanced_search.scans_list = self.table_data.scans_to_visualize
            self.advanced_search.show_search()
            self.advanced_search.apply_filter(filterToApply)

    def count_table_pop_up(self):
        self.count_table_pop_up = CountTable(self.project)
        self.count_table_pop_up.show()

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

        self.search_bar = RapidSearch(self)
        self.search_bar.textChanged.connect(partial(self.search_str))

        self.button_cross = QToolButton()
        self.button_cross.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.button_cross.setIcon(QIcon(os.path.join('..', 'sources_images', 'gray_cross.png')))
        self.button_cross.clicked.connect(self.reset_search_bar)

        search_bar_layout = QHBoxLayout()
        search_bar_layout.setSpacing(0)
        search_bar_layout.addWidget(self.search_bar)
        search_bar_layout.addWidget(self.button_cross)

        self.advanced_search_button = QPushButton()
        self.advanced_search_button.setText('Advanced search')
        self.advanced_search_button.clicked.connect(self.advanced_search)

        self.frame_test = QFrame()
        self.frame_test.setLayout(search_bar_layout)

        self.visualized_tags_button = QPushButton()
        self.visualized_tags_button.setText('Visualized tags')
        self.visualized_tags_button.clicked.connect(lambda: self.table_data.visualized_tags_pop_up())

        self.count_table_button = QPushButton()
        self.count_table_button.setText('Count table')
        self.count_table_button.clicked.connect(self.count_table_pop_up)

        self.menu_toolbar.addWidget(tags_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(filters_tool_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.frame_test)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.advanced_search_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.visualized_tags_button)
        self.menu_toolbar.addSeparator()
        self.menu_toolbar.addWidget(self.count_table_button)

    def search_str(self, str_search):

        old_scan_list = self.table_data.scans_to_visualize

        return_list = []

        # Every scan taken if empty search
        if str_search == "":
            return_list = self.table_data.scans_to_search
        else:
            # Scans with at least a not defined value
            if str_search == not_defined_value:
                filter = self.search_bar.prepare_not_defined_filter(self.project.session.get_visibles())
            # Scans matching the search
            else:
                filter = self.search_bar.prepare_filter(str_search, self.project.session.get_visibles(), self.table_data.scans_to_search)

            generator = self.project.session.filter_documents(COLLECTION_CURRENT, filter)

            # Creating the list of scans
            return_list = [getattr(scan, TAG_FILENAME) for scan in generator]

        self.table_data.scans_to_visualize = return_list

        # Rows updated
        self.table_data.update_visualized_rows(old_scan_list)

        self.project.currentFilter.search_bar = str_search

    def reset_search_bar(self):
        self.search_bar.setText("")

    def move_splitter(self):
        if self.splitter_vertical.sizes()[1] != self.splitter_vertical.minimumHeight():
            self.connect_viewer()

    def connect_viewer(self):

        if self.splitter_vertical.sizes()[1] == self.splitter_vertical.minimumHeight():
            self.viewer.setHidden(True)
        else:
            self.viewer.setHidden(False)
            items = self.table_data.selectedItems()

            full_names = []
            for item in items:
                row = item.row()
                full_name = self.table_data.item(row, 0).text()
                if full_name.endswith(".nii"):
                    if not os.path.isfile(os.sep + full_name):
                        full_name = os.path.relpath(os.path.join(self.project.folder, full_name))
                    else:
                        full_name = os.sep + full_name
                    if full_name not in full_names:
                        full_names.append(full_name)

            self.viewer.verify_slices(full_names)

    def advanced_search(self):
        """
        Called when the button advanced search is called
        """

        if self.frame_advanced_search.isHidden():
            # If the advanced search is hidden, we reset it and display it
            self.advanced_search.scans_list = self.table_data.scans_to_visualize
            self.frame_advanced_search.setHidden(False)
            self.advanced_search.show_search()
        else:

            old_scans_list = self.table_data.scans_to_visualize
            # If the advanced search is visible, we hide it
            self.frame_advanced_search.setHidden(True)
            self.advanced_search.rows = []
            # All the scans are reput in the DataBrowser
            self.table_data.scans_to_visualize = self.advanced_search.scans_list
            self.table_data.scans_to_search = self.project.session.get_documents_names(COLLECTION_CURRENT)
            self.project.currentFilter.nots = []
            self.project.currentFilter.values = []
            self.project.currentFilter.fields = []
            self.project.currentFilter.links = []
            self.project.currentFilter.conditions = []

            self.table_data.update_visualized_rows(old_scans_list)

    def add_tag_infos(self, new_tag_name, new_default_value, tag_type, new_tag_description,new_tag_unit):
        """
        Adds the tag after add_tag pop_up
        :param new_tag_name: New tag name
        :param new_default_value:  New default value
        :param tag_type: New tag type
        :param new_tag_description: New tag description
        :param new_tag_unit: New tag unit
        """

        values = []

        # We add the tag and a value for each scan in the Database
        self.project.session.add_field(COLLECTION_CURRENT, new_tag_name, tag_type, new_tag_description, True,
                                        TAG_ORIGIN_USER, new_tag_unit, new_default_value)
        self.project.session.add_field(COLLECTION_INITIAL, new_tag_name, tag_type, new_tag_description, True,
                                        TAG_ORIGIN_USER, new_tag_unit, new_default_value)
        for scan in self.project.session.get_documents(COLLECTION_CURRENT):
            self.project.session.add_value(COLLECTION_CURRENT, getattr(scan, TAG_FILENAME), new_tag_name,
                                           table_to_database(new_default_value, tag_type))
            self.project.session.add_value(COLLECTION_INITIAL, getattr(scan, TAG_FILENAME), new_tag_name,
                                           table_to_database(new_default_value, tag_type))
            values.append(
                [getattr(scan, TAG_FILENAME), new_tag_name, table_to_database(new_default_value, tag_type),
                 table_to_database(new_default_value, tag_type)])  # For history

        # For history
        historyMaker = []
        historyMaker.append("add_tag")
        historyMaker.append(new_tag_name)
        historyMaker.append(tag_type)
        historyMaker.append(new_tag_unit)
        historyMaker.append(new_default_value)
        historyMaker.append(new_tag_description)
        historyMaker.append(values)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        # New tag added to the table
        column = self.table_data.get_index_insertion(new_tag_name)
        self.table_data.add_column(column, new_tag_name)

    def add_tag_pop_up(self):
        """
        Displays add_tag popup
        :return:
        """

        # We first show the add_tag pop up
        self.pop_up_add_tag = Ui_Dialog_add_tag(self, self.project)
        self.pop_up_add_tag.show()

    def clone_tag_infos(self, tag_to_clone, new_tag_name):
        """
        Clones the tag after the clone_tag pop_up
        :param tag_to_clone: Tag to clone
        :param new_tag_name: New tag name
        """

        values = []

        # We add the new tag in the Database
        tagCloned = self.project.session.get_field(COLLECTION_CURRENT, tag_to_clone)
        tagClonedInit = self.project.session.get_field(COLLECTION_INITIAL, tag_to_clone)
        self.project.session.add_field(COLLECTION_CURRENT, new_tag_name, tagCloned.type, tagCloned.description, True,
                                        TAG_ORIGIN_USER, tagCloned.unit, tagCloned.default_value)
        self.project.session.add_field(COLLECTION_INITIAL, new_tag_name, tagCloned.type, tagClonedInit.description, True,
                                        TAG_ORIGIN_USER, tagCloned.unit, tagCloned.default_value)
        for scan in self.project.session.get_documents(COLLECTION_CURRENT):

            # If the tag to clone has a value, we add this value with the new tag name in the Database
            cloned_cur_value = self.project.session.get_value(COLLECTION_CURRENT, getattr(scan, TAG_FILENAME),
                                                               tag_to_clone)
            cloned_init_value = self.project.session.get_value(COLLECTION_INITIAL, getattr(scan, TAG_FILENAME),
                                                                tag_to_clone)
            if cloned_cur_value is not None or cloned_init_value is not None:
                self.project.session.add_value(COLLECTION_CURRENT, getattr(scan, TAG_FILENAME), new_tag_name,
                                               cloned_cur_value)
                self.project.session.add_value(COLLECTION_INITIAL, getattr(scan, TAG_FILENAME), new_tag_name,
                                               cloned_init_value)
                values.append(
                    [getattr(scan, TAG_FILENAME), new_tag_name, cloned_cur_value, cloned_init_value])  # For history

        # For history
        historyMaker = []
        historyMaker.append("add_tag")
        historyMaker.append(new_tag_name)
        historyMaker.append(tagCloned.type)
        historyMaker.append(tagCloned.unit)
        historyMaker.append(tagCloned.default_value)
        historyMaker.append(tagCloned.description)
        historyMaker.append(values)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        # New tag added to the table
        column = self.table_data.get_index_insertion(new_tag_name)
        self.table_data.add_column(column, new_tag_name)

    def clone_tag_pop_up(self):
        """
        Displays clone_tag popup
        """

        # We first show the clone_tag pop up
        self.pop_up_clone_tag = Ui_Dialog_clone_tag(self, self.project)
        self.pop_up_clone_tag.show()

    def remove_tag_infos(self, tag_names_to_remove):
        """
        Removes user tags after the popup
        :param tag_names_to_remove: List of tags to remove
        """

        self.table_data.itemSelectionChanged.disconnect()

        # For history
        historyMaker = []
        historyMaker.append("remove_tags")
        tags_removed = []

        # Each Tag row to remove is put in the history
        for tag in tag_names_to_remove:
            tagObject = self.project.session.get_field(COLLECTION_CURRENT, tag)
            tags_removed.append([tagObject])
        historyMaker.append(tags_removed)

        # Each value of the tags to remove are stored in the history
        values_removed = []
        for tag in tag_names_to_remove:
            for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
                current_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag)
                initial_value = self.project.session.get_value(COLLECTION_INITIAL, scan, tag)
                if current_value is not None or initial_value is not None:
                    values_removed.append([scan, tag, current_value, initial_value])
        historyMaker.append(values_removed)

        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        # Tags removed from the Database and table
        for tag in tag_names_to_remove:
            self.project.session.remove_field(COLLECTION_CURRENT, tag)
            self.project.session.remove_field(COLLECTION_INITIAL, tag)
            self.table_data.removeColumn(self.table_data.get_tag_column(tag))

        # Selection updated
        self.table_data.update_selection()

        self.table_data.itemSelectionChanged.connect(self.table_data.selection_changed)

    def remove_tag_pop_up(self):
        """
        Displays the popup to remove user tags
        """

        # We first open the remove_tag pop up
        self.pop_up_remove_tag = Ui_Dialog_remove_tag(self, self.project)
        self.pop_up_remove_tag.show()


class TableDataBrowser(QTableWidget):

    def __init__(self, project, data_browser, tags_to_display, update_values, activate_selection):

        super().__init__()

        self.project = project
        self.data_browser = data_browser
        self.tags_to_display = tags_to_display
        self.update_values = update_values
        self.activate_selection = activate_selection
        self.bricks = {}

        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # It allows to move the columns (except the first column name)
        self.horizontalHeader().setSectionsMovable(True)

        # It allows the automatic sort
        self.setSortingEnabled(True)

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        if self.activate_selection:
            self.customContextMenuRequested.connect(partial(self.context_menu_table))
        self.itemChanged.connect(self.change_cell_color)
        if activate_selection:
            self.itemSelectionChanged.connect(self.selection_changed)
        else:
            self.setSelectionMode(QAbstractItemView.NoSelection)
        self.horizontalHeader().sortIndicatorChanged.connect(partial(self.sort_updated))
        self.horizontalHeader().sectionDoubleClicked.connect(partial(self.selectAllColumn))
        self.horizontalHeader().sectionMoved.connect(partial(self.section_moved))
        self.verticalHeader().setMinimumSectionSize(30)

        self.update_table(True)

        if not self.update_values:
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add_path(self):
        """
        Green cross clicked to add a path
        """

        self.pop_up_add_path = Ui_Dialog_add_path(self.project, self.data_browser)
        self.pop_up_add_path.show()

    def add_column(self, column, tag):

        self.itemChanged.disconnect()

        self.itemSelectionChanged.disconnect()

        # Adding the column to the table
        self.insertColumn(column)
        item = QtWidgets.QTableWidgetItem()
        self.setHorizontalHeaderItem(column, item)
        tag_object = self.project.session.get_field(COLLECTION_CURRENT, tag)
        item.setText(tag)
        item.setToolTip(
            "Description: " + str(tag_object.description) + "\nUnit: " + str(tag_object.unit) + "\nType: " + str(
                tag_object.type))
        # Set column type
        if tag_object.type == FIELD_TYPE_FLOAT:
            self.setItemDelegateForColumn(column, NumberFormatDelegate(self))
        elif tag_object.type == FIELD_TYPE_DATETIME:
            self.setItemDelegateForColumn(column, DateTimeFormatDelegate(self))
        elif tag_object.type == FIELD_TYPE_DATE:
            self.setItemDelegateForColumn(column, DateFormatDelegate(self))
        elif tag_object.type == FIELD_TYPE_TIME:
            self.setItemDelegateForColumn(column, TimeFormatDelegate(self))

        for row in range(0, self.rowCount()):
            item = QtWidgets.QTableWidgetItem()
            self.setItem(row, column, item)
            scan = self.item(row, 0).text()
            cur_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag)
            if cur_value is not None:
                set_item_data(item, cur_value, tag_object.type)
            else:
                set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
                font = item.font()
                font.setItalic(True)
                font.setBold(True)
                item.setFont(font)

        self.resizeColumnsToContents()  # New column resized

        # Selection updated
        self.update_selection()

        self.update_colors()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def sort_updated(self, column, order):
        """
        Called when the sort is updated
        :param column: Column being sorted
        :param order: New order
        """

        self.itemChanged.disconnect()

        if column != -1:
            self.project.setSortOrder(int(order))
            self.project.setSortedTag(self.horizontalHeaderItem(column).text())

            self.sortItems(column, order)

            self.update_colors()
            self.resizeRowsToContents()

        self.itemChanged.connect(self.change_cell_color)

    def get_current_filter(self):
        """
        Get the current databrowser selection (list of paths)
        If there is a current selection, the list of selected scans is returned, otherwise the list of the visible paths in the databrowser is returned
        :return: The list of scans corresponding to the current selection in the databrowser
        """

        return_list = []
        if self.activate_selection and len(self.scans) > 0:
            for scan in self.scans:
                return_list.append(scan[0])
        else:
            return_list = self.scans_to_visualize
        return return_list

    def update_selection(self):
        """
        Called after searches to update the selection
        """

        # Selection updated
        self.clearSelection()

        for scan in self.scans:
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
        self.scans.clear()

        for point in self.selectedItems():
            row = point.row()
            column = point.column()
            scan_name = self.item(row, 0).text()
            tag_name = self.horizontalHeaderItem(column).text()
            scan_already_in_list = False
            for scan in self.scans:
                if scan[0] == scan_name:
                    # Scan already in the list, we append the column
                    scan[1].append(tag_name)
                    scan_already_in_list = True
                    break

            if not scan_already_in_list:
                # Scan not in the list, we add it
                self.scans.append([scan_name, [tag_name]])

        # ImageViewer updated
        self.data_browser.connect_viewer()

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

    def update_table(self, take_tags_to_update=False):
        """
        This method will fill the tables in the 'Table' tab with the project data
        Only called when switching project to completely reset the table
        """

        self.setSortingEnabled(False)

        self.clearSelection()  # Selection cleared when switching project

        # The list of scans to visualize
        self.scans_to_visualize = self.project.session.get_documents_names(COLLECTION_CURRENT)
        self.scans_to_search = self.project.session.get_documents_names(COLLECTION_CURRENT)

        # The list of selected scans
        if self.activate_selection:
            self.scans = []

        self.itemChanged.disconnect()

        self.setRowCount(len(self.scans_to_visualize))

        _translate = QtCore.QCoreApplication.translate

        # Sort visual management
        self.fill_headers(take_tags_to_update)

        # Cells filled
        self.fill_cells_update_table()

        # Saved sort applied if it exists
        self.setSortingEnabled(True)

        tag_to_sort = self.project.getSortedTag()
        column_to_sort = self.get_tag_column(tag_to_sort)
        sort_order = self.project.getSortOrder()

        self.itemChanged.connect(self.change_cell_color)

        if column_to_sort != None:
            self.horizontalHeader().setSortIndicator(column_to_sort, sort_order)
        else:
            self.horizontalHeader().setSortIndicator(0, 0)

        self.itemChanged.disconnect()

        # Columns and rows resized
        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        self.update_colors()

        # When the user changes one item of the table, the background will change
        self.itemChanged.connect(self.change_cell_color)

    def fill_headers(self, take_tags_to_update=False):
        """
        To initialize and fill the headers of the table
        """

        # Sorting the list of tags in alphabetical order, but keeping FileName first
        tags = self.project.session.get_fields_names(COLLECTION_CURRENT)
        tags.remove(TAG_CHECKSUM)
        tags.remove(TAG_FILENAME)
        tags = sorted(tags)
        tags.insert(0, TAG_FILENAME)

        self.setColumnCount(len(tags))

        column = 0
        # Filling the headers
        for tag_name in tags:
            item = QtWidgets.QTableWidgetItem()
            self.setHorizontalHeaderItem(column, item)
            item.setText(tag_name)

            element = self.project.session.get_field(COLLECTION_CURRENT, tag_name)
            if element is not None:
                item.setToolTip(
                    "Description: " + str(element.description) + "\nUnit: " + str(element.unit) + "\nType: " + str(
                        element.type))

                # Set column type
                if element.type == FIELD_TYPE_FLOAT:
                    self.setItemDelegateForColumn(column, NumberFormatDelegate(self))
                elif element.type == FIELD_TYPE_DATETIME:
                    self.setItemDelegateForColumn(column, DateTimeFormatDelegate(self))
                elif element.type == FIELD_TYPE_DATE:
                    self.setItemDelegateForColumn(column, DateFormatDelegate(self))
                elif element.type == FIELD_TYPE_TIME:
                    self.setItemDelegateForColumn(column, TimeFormatDelegate(self))

                # Hide the column if not visible
                if take_tags_to_update:
                    if tag_name in self.tags_to_display:
                        self.setColumnHidden(column, False)

                    else:
                        self.setColumnHidden(column, True)
                else:
                    if element.visibility:
                        self.setColumnHidden(column, False)

                    else:
                        self.setColumnHidden(column, True)

            self.setHorizontalHeaderItem(column, item)

            column += 1

    def fill_cells_update_table(self):
        """
        To initialize and fill the cells of the table
        """

        cells_number = len(self.scans_to_visualize) * len(self.horizontalHeader())
        self.progress = QProgressDialog("Please wait while the cells are being filled...",
                                        None, 0, cells_number)
        self.progress.setMinimumDuration(0)
        self.progress.setValue(0)
        self.progress.setWindowTitle("Filling the cells")
        self.progress.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.progress.setModal(True)
        self.progress.setAttribute(Qt.WA_DeleteOnClose, True)
        self.progress.show()

        idx = 0
        row = 0
        for scan in self.scans_to_visualize:

            for column in range(0, len(self.horizontalHeader())):

                idx += 1
                self.progress.setValue(idx)
                QApplication.processEvents()

                current_tag = self.horizontalHeaderItem(column).text()

                item = QTableWidgetItem()

                if column == 0:
                    # name tag
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # name not editable
                    set_item_data(item, scan, FIELD_TYPE_STRING)
                else:
                    # Other tags
                    current_value = self.project.session.get_value(COLLECTION_CURRENT, scan, current_tag)
                    # The scan has a value for the tag
                    if current_value is not None:

                        if current_tag != TAG_BRICKS:
                            set_item_data(item, current_value,
                                          self.project.session.get_field(COLLECTION_CURRENT, current_tag).type)
                        else:
                            # Tag bricks, display list with buttons
                            widget = QWidget()
                            widget.moveToThread(QApplication.instance().thread())
                            layout = QVBoxLayout()
                            for brick_number in range(0, len(current_value)):
                                brick_uuid = current_value[brick_number]
                                brick_name = self.project.session.get_value(COLLECTION_BRICK, brick_uuid, BRICK_NAME)
                                brick_name_button = QPushButton(brick_name)
                                brick_name_button.moveToThread(QApplication.instance().thread())
                                self.bricks[brick_name_button] = brick_uuid
                                brick_name_button.clicked.connect(self.show_brick_history)
                                layout.addWidget(brick_name_button)
                            widget.setLayout(layout)
                            self.setCellWidget(row, column, widget)

                    # The scan does not have a value for the tag
                    else:
                        if current_tag != TAG_BRICKS:
                            set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
                            font = item.font()
                            font.setItalic(True)
                            font.setBold(True)
                            item.setFont(font)
                        else:
                            set_item_data(item, "", FIELD_TYPE_STRING)
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # bricks not editable
                self.setItem(row, column, item)
            row += 1

        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        self.progress.close()

    def show_brick_history(self):
        """
        Shows brick history popup
        """

        brick_uuid = self.bricks[self.sender()]
        self.show_brick_popup = Ui_Dialog_Show_Brick(self.project, brick_uuid, self.data_browser, self.data_browser.parent)
        self.show_brick_popup.show()

    def update_colors(self):
        """ Method that changes the background of all the cells """

        # itemChanged signal is always disconnected when calling this method

        for column in range(0, self.columnCount()):
            if not self.isColumnHidden(column):
                tag = self.horizontalHeaderItem(column).text()
                row_number = 0
                for row in range(0, self.rowCount()):
                    if not self.isRowHidden(row):
                        scan = self.item(row, 0).text()

                        item = self.item(row, column)

                        color = QColor()

                        if column == 0:
                            if row_number % 2 == 0:
                                color.setRgb(255, 255, 255)  # White
                            else:
                                color.setRgb(230, 230, 230)  # Grey

                        # Raw tag
                        elif self.project.session.get_field(COLLECTION_CURRENT, tag).origin == TAG_ORIGIN_BUILTIN:
                            current_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag)
                            initial_value = self.project.session.get_value(COLLECTION_INITIAL, scan, tag)
                            if current_value != initial_value:
                                if row_number % 2 == 0:
                                    color.setRgb(200, 230, 245)  # Cyan
                                else:
                                    color.setRgb(150, 215, 230)  # Blue
                            else:
                                if row_number % 2 == 0:
                                    color.setRgb(255, 255, 255)  # White
                                else:
                                    color.setRgb(230, 230, 230)  # Grey

                        # User tag
                        else:
                            if row_number % 2 == 0:
                                color.setRgb(245, 215, 215)  # Pink
                            else:
                                color.setRgb(245, 175, 175)  # Red

                        row_number += 1

                        item.setData(Qt.BackgroundRole, QtCore.QVariant(color))

        # Auto-save
        config = Config()
        if config.isAutoSave() == "yes":
            save_project(self.project)

    def context_menu_table(self, position):

        self.itemChanged.disconnect()

        self.menu = QMenu(self)

        self.action_reset_cell = self.menu.addAction("Reset cell(s)")
        self.action_reset_column = self.menu.addAction("Reset column(s)")
        self.action_reset_row = self.menu.addAction("Reset row(s)")
        self.action_clear_cell = self.menu.addAction("Clear cell(s)")
        self.action_add_scan = self.menu.addAction("Add path")
        self.action_remove_scan = self.menu.addAction("Remove path(s)")
        self.action_sort_column = self.menu.addAction("Sort column")
        self.action_sort_column_descending = self.menu.addAction("Sort column (descending)")
        self.action_visualized_tags = self.menu.addAction("Visualized tags")
        self.action_select_column = self.menu.addAction("Select column(s)")
        self.action_multiple_sort = self.menu.addAction("Multiple sort")

        action = self.menu.exec_(self.mapToGlobal(position))
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        if action == self.action_reset_cell:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.reset_cell)
            msg.exec()
        elif action == self.action_reset_column:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.reset_column)
            msg.exec()
        elif action == self.action_reset_row:
            msg.setText("You are about to reset cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.reset_row)
            msg.exec()
        if action == self.action_clear_cell:
            msg.setText("You are about to clear cells.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.clear_cell)
            msg.exec()
        elif action == self.action_add_scan:
            self.itemChanged.connect(self.change_cell_color)
            self.add_path()
            self.itemChanged.disconnect()
        elif action == self.action_remove_scan:
            msg.setText("You are about to remove a scan from the project.")
            msg.buttonClicked.connect(msg.close)
            msg.buttons()[0].clicked.connect(self.remove_scan)
            msg.exec()
        elif action == self.action_sort_column:
            self.sort_column(0)
        elif action == self.action_sort_column_descending:
            self.sort_column(1)
        elif action == self.action_visualized_tags:
            self.visualized_tags_pop_up()
        elif action == self.action_select_column:
            self.selectAllColumns()
        elif action == self.action_multiple_sort:
            self.multiple_sort_pop_up()

        self.update_colors()

        # Signals reconnected
        self.itemChanged.connect(self.change_cell_color)

    def sort_column(self, order):
        """
        Sorts the current column
        :param order: order of sort (0 for ascending, 1 for descending)
        """

        self.itemChanged.connect(self.change_cell_color)

        self.horizontalHeader().setSortIndicator(self.currentItem().column(), order)

        self.itemChanged.disconnect()

    def get_tag_column(self, tag):
        """
        Returns the column index of the tag
        :param tag:tag name
        :return:index of the column of the tag
        """

        for column in range(0, self.columnCount()):
            item = self.horizontalHeaderItem(column)
            tag_name = item.text()
            if tag_name == tag:
                return column

    def get_scan_row(self, scan):
        """
        Returns the row index of the scan
        :param scan:Scan FileName
        :return:index of the row of the scan
        """

        for row in range(0, self.rowCount()):
            item = self.item(row, 0)
            scan_name = item.text()
            if scan_name == scan:
                return row

    def clear_cell(self):
        """
        Clears the selected cells
        """

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()
        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()  # We get the FileName of the scan from the first row
            current_value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
            modified_values.append([scan_name, tag_name, current_value, None])  # For history
            self.project.session.remove_value(COLLECTION_CURRENT, scan_name, tag_name)
            item  = self.item(row, col)
            set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
            font = item.font()
            font.setItalic(True)
            font.setBold(True)
            item.setFont(font)

        # For history
        historyMaker.append(modified_values)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

    def reset_cell(self):

        # For history
        historyMaker = []
        historyMaker.append("modified_values")
        modified_values = []

        points = self.selectedIndexes()

        has_unreset_values = False  # To know if some values do not have raw values (user tags)

        for point in points:
            row = point.row()
            col = point.column()
            tag_name = self.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()  # We get the FileName of the scan from the first row

            current_value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
            initial_value = self.project.session.get_value(COLLECTION_INITIAL, scan_name, tag_name)
            if initial_value is not None:
                try:
                    self.project.session.set_value(COLLECTION_CURRENT, scan_name, tag_name, initial_value)
                    set_item_data(self.item(row, col), initial_value,
                                  self.project.session.get_field(COLLECTION_CURRENT, tag_name).type)
                    modified_values.append([scan_name, tag_name, current_value, initial_value])  # For history
                except ValueError:
                    has_unreset_values = True
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
            tag_name = self.horizontalHeaderItem(col).text()

            for row_iter in range(0, len(self.scans_to_visualize)):
                scan = self.item(row_iter, 0).text()  # We get the FileName of the scan from the first column
                initial_value = self.project.session.get_value(COLLECTION_INITIAL, scan, tag_name)
                current_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag_name)
                if initial_value is not None:
                    try:
                        self.project.session.set_value(COLLECTION_CURRENT, scan, tag_name, initial_value)
                        set_item_data(self.item(row_iter, col), initial_value,
                                      self.project.session.get_field(COLLECTION_CURRENT, tag_name).type)
                        modified_values.append([scan, tag_name, current_value, initial_value])  # For history
                    except ValueError:
                        has_unreset_values = True
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
            scan_name = self.item(row, 0).text()  # FileName is always the first column

            for column in range(0, len(self.horizontalHeader())):
                tag = self.horizontalHeaderItem(column).text()  # We get the tag name from the header
                current_value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag)
                initial_value = self.project.session.get_value(COLLECTION_INITIAL, scan_name, tag)
                if initial_value is not None:
                    # We reset the value only if it exists

                    try:
                        self.project.session.set_value(COLLECTION_CURRENT, scan_name, tag, initial_value)
                        set_item_data(self.item(row, column), initial_value,
                                      self.project.session.get_field(COLLECTION_CURRENT, tag).type)
                        modified_values.append([scan_name, tag, current_value, initial_value])  # For history
                    except ValueError:
                        has_unreset_values = True

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

    def display_unreset_values(self):
        """
        Error message when trying to reset user tags
        """
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Warning)
        self.msg.setText("Some values do not have a raw value")
        self.msg.setInformativeText(
            "Some values have not been reset because they do not have a raw value.\nIt is the case for the user tags, FileName and the cells not defined.")
        self.msg.setWindowTitle("Warning")
        self.msg.setStandardButtons(QMessageBox.Ok)
        self.msg.buttonClicked.connect(self.msg.close)
        self.msg.show()

    def remove_scan(self):

        points = self.selectedIndexes()

        historyMaker = []
        historyMaker.append("remove_scans")
        scans_removed = []
        values_removed = []

        for point in points:
            row = point.row()
            scan_path = self.item(row, 0).text()

            scan_object = self.project.session.get_document(COLLECTION_CURRENT, scan_path)

            if scan_object is not None:
                scans_removed.append(scan_object)

                # Adding removed values to history
                for tag in self.project.session.get_fields_names(COLLECTION_CURRENT):
                    if tag != TAG_FILENAME:
                        current_value = self.project.session.get_value(COLLECTION_CURRENT, scan_path, tag)
                        initial_value = self.project.session.get_value(COLLECTION_INITIAL, scan_path, tag)
                        if current_value is not None or initial_value is not None:
                            values_removed.append([scan_path, tag, current_value, initial_value])

                self.scans_to_visualize.remove(scan_path)
                self.project.session.remove_document(COLLECTION_CURRENT, scan_path)
                self.project.session.remove_document(COLLECTION_INITIAL, scan_path)

        for scan in scans_removed:
            scan_name = getattr(scan, TAG_FILENAME)
            self.removeRow(self.get_scan_row(scan_name))

        historyMaker.append(scans_removed)
        historyMaker.append(values_removed)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        self.resizeColumnsToContents()

    def visualized_tags_pop_up(self):
        old_tags = self.project.session.get_visibles()  # Old list of columns
        self.pop_up = Ui_Dialog_Settings(self.project, self.data_browser, old_tags)
        self.pop_up.tab_widget.setCurrentIndex(0)
        screen_resolution = QApplication.instance().desktop().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.pop_up.setMinimumWidth(0.5 * width)
        self.pop_up.setMinimumHeight(0.8 * height)
        self.pop_up.show()

    def multiple_sort_infos(self, list_tags, order):

        self.itemChanged.disconnect()

        list_tags_name = list_tags
        list_tags = []
        for tag_name in list_tags_name:
            list_tags.append(self.project.session.get_field(COLLECTION_CURRENT, tag_name))
        list_sort = []
        for scan in self.scans_to_visualize:
            tags_value = []
            for tag in list_tags:
                current_value = str(self.project.session.get_value(COLLECTION_CURRENT, scan, tag.field_name))
                if current_value is not None:
                    tags_value.append(current_value)
                else:
                    tags_value.append(not_defined_value)
            list_sort.append(tags_value)

        if order == "Descending":
            self.scans_to_visualize = [x for _, x in sorted(zip(list_sort, self.scans_to_visualize), reverse=True)]
        else:
            self.scans_to_visualize = [x for _, x in sorted(zip(list_sort, self.scans_to_visualize))]

        # Table updated
        self.setSortingEnabled(False)
        for row in range(0, self.rowCount()):
            scan = self.scans_to_visualize[row]
            old_row = self.get_scan_row(scan)
            if old_row != row:
                for column in range(0, self.columnCount()):
                    item_to_move = self.takeItem(old_row, column)
                    item_wrong_row = self.takeItem(row, column)
                    self.setItem(row, column, item_to_move)
                    self.setItem(old_row, column, item_wrong_row)
        self.itemChanged.connect(self.change_cell_color)
        self.horizontalHeader().setSortIndicator(-1, 0)
        self.itemChanged.disconnect()
        self.setSortingEnabled(True)

        self.itemChanged.connect(self.change_cell_color)

    def multiple_sort_pop_up(self):
        self.pop_up = Ui_Dialog_Multiple_Sort(self.project, self)
        self.pop_up.show()

    def update_visualized_rows(self, old_scans):
        """
        Called after a search to update the list of scans in the table
        :param old_scans: Old list of scans
        """

        self.itemChanged.disconnect()

        if self.activate_selection:
            self.itemSelectionChanged.disconnect()

        # Scans that are not visible anymore are hidden
        for scan in old_scans:
            if not scan in self.scans_to_visualize:
                self.setRowHidden(self.get_scan_row(scan), True)

        # Scans that became visible must be visible
        for scan in self.scans_to_visualize:
            self.setRowHidden(self.get_scan_row(scan), False)

        self.resizeColumnsToContents()  # Columns resized

        # Selection updated
        if self.activate_selection:
            self.update_selection()

        self.update_colors()

        if self.activate_selection:
            self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def update_visualized_columns(self, old_tags, visibles):
        """
        Called to set the visualized tags in the table
        :param old_tags: Old list of visualized tags
        :param visibles: List of tags to display
        """

        self.itemChanged.disconnect()
        if self.activate_selection:
            self.itemSelectionChanged.disconnect()

        # Tags that are not visible anymore are hidden
        for tag in old_tags:
            if not tag in visibles:
                self.setColumnHidden(self.get_tag_column(tag), True)

        # Tags that became visible must be visible
        for tag in visibles:
            self.setColumnHidden(self.get_tag_column(tag), False)

        # Update the list of tags in the advanced search if it's opened
        if hasattr(self.data_browser, "frame_advanced_search") and not self.data_browser.frame_advanced_search.isHidden():
            for row in self.data_browser.advanced_search.rows:
                fields = row[2]
                fields.clear()
                for visible_tag in visibles:
                    fields.addItem(visible_tag)
                fields.model().sort(0)
                fields.addItem("All visualized tags")

        self.resizeColumnsToContents()

        self.update_colors()

        # Selection updated
        if self.activate_selection:
            self.update_selection()
            self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def add_columns(self):
        """
        To add the new tags
        """

        self.itemChanged.disconnect()

        self.itemSelectionChanged.disconnect()

        tags = self.project.session.get_fields_names(COLLECTION_CURRENT)
        tags.remove(TAG_CHECKSUM)
        tags.remove(TAG_FILENAME)
        tags = sorted(tags)
        tags.insert(0, TAG_FILENAME)

        visibles = self.project.session.get_visibles()

        # Adding missing columns

        for tag in tags:

            # Tag added only if it's not already in the table

            if self.get_tag_column(tag) is None:

                columnIndex = self.get_index_insertion(tag)
                self.insertColumn(columnIndex)

                item = QtWidgets.QTableWidgetItem()
                self.setHorizontalHeaderItem(columnIndex, item)
                item.setText(tag)
                tag_object = self.project.session.get_field(COLLECTION_CURRENT, tag)

                if tag_object is not None:
                    item.setToolTip("Description: " + str(tag_object.description) + "\nUnit: " + str(
                    tag_object.unit) + "\nType: " + str(tag_object.type))

                # Set column type

                if tag_object.type == FIELD_TYPE_FLOAT:
                    self.setItemDelegateForColumn(columnIndex, NumberFormatDelegate(self))
                elif tag_object.type == FIELD_TYPE_DATETIME:
                    self.setItemDelegateForColumn(columnIndex, DateTimeFormatDelegate(self))
                elif tag_object.type == FIELD_TYPE_DATE:
                    self.setItemDelegateForColumn(columnIndex, DateFormatDelegate(self))
                elif tag_object.type == FIELD_TYPE_TIME:
                    self.setItemDelegateForColumn(columnIndex, TimeFormatDelegate(self))

                # Hide the column if not visible

                if tag in visibles:
                    self.setColumnHidden(columnIndex, True)

                # Rows filled for the column being added

                for row in range(0, self.rowCount()):
                    item = QtWidgets.QTableWidgetItem()
                    self.setItem(row, columnIndex, item)
                    scan = self.item(row, 0).text()
                    cur_value = self.project.database.get_value(COLLECTION_CURRENT, scan, tag)

                    if cur_value is not None:
                        set_item_data(item, cur_value, tag_object.type)
                    else:
                        set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
                        font = item.font()
                        font.setItalic(True)
                        font.setBold(True)
                        item.setFont(font)

                # Removing useless columns
                tags_to_remove = []

                for column in range(0, self.columnCount()):
                    tag_name = self.horizontalHeaderItem(column).text()

                    if not tag_name in self.project.session.get_fields_names(COLLECTION_CURRENT) and tag_name != TAG_FILENAME:
                        tags_to_remove.append(tag_name)

                    for tag in tags_to_remove:
                        self.removeColumn(self.get_tag_column(tag))

        self.resizeColumnsToContents()

        # Selection updated
        self.update_selection()

        self.update_colors()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

    def add_rows(self, rows):
        """
        Inserts rows in the table if they are not already in the table
        :param rows: List of all scans
        """

        self.setSortingEnabled(False)

        self.itemSelectionChanged.disconnect()

        self.itemChanged.disconnect()

        cells_number = len(rows) * self.columnCount()
        self.progress = QProgressDialog("Please wait while the paths are being added...", None, 0, cells_number)
        self.progress.setMinimumDuration(0)
        self.progress.setValue(0)
        self.progress.setWindowTitle("Adding the paths")
        self.progress.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.progress.setModal(True)
        self.progress.setAttribute(Qt.WA_DeleteOnClose, True)
        self.progress.show()

        idx = 0
        for scan in rows:

            # Scan added only if it's not already in the table
            if self.get_scan_row(scan) is None:

                rowCount = self.rowCount()
                self.insertRow(rowCount)

                # Columns filled for the row being added
                for column in range(0, self.columnCount()):

                    idx += 1
                    self.progress.setValue(idx)
                    QApplication.processEvents()

                    item = QtWidgets.QTableWidgetItem()
                    tag = self.horizontalHeaderItem(column).text()

                    if column == 0:
                        # name tag
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # name not editable
                        set_item_data(item, scan, FIELD_TYPE_STRING)
                    else:
                        cur_value = self.project.session.get_value(COLLECTION_CURRENT, scan, tag)
                        if cur_value is not None:
                            if tag != TAG_BRICKS:
                                set_item_data(item, cur_value,
                                              self.project.session.get_field(COLLECTION_CURRENT, tag).type)
                            else:
                                # Tag bricks, display list with buttons
                                widget = QWidget()
                                widget.moveToThread(QApplication.instance().thread())
                                layout = QVBoxLayout()
                                for brick_number in range(0, len(cur_value)):
                                    brick_uuid = cur_value[brick_number]
                                    brick_name = self.project.session.get_value(COLLECTION_BRICK, brick_uuid,
                                                                                BRICK_NAME)
                                    brick_name_button = QPushButton(brick_name)
                                    brick_name_button.moveToThread(QApplication.instance().thread())
                                    self.bricks[brick_name_button] = brick_uuid
                                    brick_name_button.clicked.connect(self.show_brick_history)
                                    layout.addWidget(brick_name_button)
                                widget.setLayout(layout)
                                self.setCellWidget(rowCount, column, widget)

                        else:
                            if tag != TAG_BRICKS:
                                set_item_data(item, not_defined_value, FIELD_TYPE_STRING)
                                font = item.font()
                                font.setItalic(True)
                                font.setBold(True)
                                item.setFont(font)
                            else:
                                set_item_data(item, "", FIELD_TYPE_STRING)
                                item.setFlags(item.flags() & ~Qt.ItemIsEditable)  # bricks not editable
                    self.setItem(rowCount, column, item)

        self.setSortingEnabled(True)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        # Selection updated
        self.update_selection()

        self.update_colors()

        self.itemSelectionChanged.connect(self.selection_changed)

        self.itemChanged.connect(self.change_cell_color)

        self.progress.close()

    def get_index_insertion(self, to_insert):
        """
        To get index insertion of a new column, since it's already sorted in alphabetical order
        :param to_insert: tag to insert
        """

        for column in range(1, len(self.horizontalHeader())):
            if self.horizontalHeaderItem(column).text() > to_insert:
                return column
        return self.columnCount()

    def mouseReleaseEvent(self, e):
        """
        Called when clicking released on cells, for list values changes
        :param e: event
        """

        super(TableDataBrowser, self).mouseReleaseEvent(e)

        self.setMouseTracking(False)

        self.coordinates = []  # Coordinates of selected cells stored
        self.old_database_values = []  # Old database values stored
        self.old_table_values = []  # Old table values stored
        self.types = []  # List of types
        self.lengths = []  # List of lengths
        self.scans_list = []  # List of table scans
        self.tags = []  # List of table tags

        try:

            for item in self.selectedItems():
                column = item.column()
                row = item.row()
                self.coordinates.append([row, column])
                tag_name = self.horizontalHeaderItem(column).text()
                tag_object = self.project.session.get_field(COLLECTION_CURRENT, tag_name)
                tag_type = tag_object.type
                scan_name = self.item(row, 0).text()

                if tag_name == TAG_BRICKS:
                    self.setMouseTracking(True)
                    return

                # Scan and tag added
                self.tags.append(tag_name)
                self.scans_list.append(scan_name)

                # Type checked
                if not tag_type in self.types:
                    self.types.append(tag_type)

                if tag_type in LIST_TYPES:

                    database_value = self.project.session.get_value(COLLECTION_CURRENT, scan_name, tag_name)
                    self.old_database_values.append(database_value)

                    table_value = item.data(Qt.EditRole)
                    table_value = ast.literal_eval(table_value)
                    self.old_table_values.append(table_value)

                    size = len(database_value)
                    if size not in self.lengths:
                        self.lengths.append(size)

                else:
                    self.setMouseTracking(True)
                    return

            # Error if lists of different lengths
            if len(self.lengths) > 1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Incompatible list lengths")
                msg.setInformativeText("The lists can't have several lengths")
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()

            # Ok
            elif len(self.old_table_values) > 0:

                if len(self.coordinates) > 1:
                    value = []
                    for i in range(0, self.lengths[0]):
                        value.append(0)
                else:
                    value = self.old_table_values[0]

                # Window to change list values displayed
                pop_up = ModifyTable(self.project, value, self.types, self.scans_list, self.tags)
                pop_up.show()
                if pop_up.exec_():
                    pass

                # For history
                historyMaker = []
                historyMaker.append("modified_values")
                modified_values = []

                self.itemChanged.disconnect()

                # Lists updated
                for i in range(0, len(self.coordinates)):
                    new_item = QTableWidgetItem()
                    old_value = self.old_database_values[i]
                    new_cur_value = self.project.session.get_value(COLLECTION_CURRENT, self.scans_list[i], self.tags[i])
                    modified_values.append([self.scans_list[i], self.tags[i], old_value, new_cur_value])
                    set_item_data(new_item, new_cur_value, self.project.session.get_field(COLLECTION_CURRENT, self.tags[i]).type)
                    self.setItem(self.coordinates[i][0], self.coordinates[i][1], new_item)

                # For history
                historyMaker.append(modified_values)
                self.project.undos.append(historyMaker)
                self.project.redos.clear()

                self.update_colors()

                self.itemChanged.connect(self.change_cell_color)

            self.setMouseTracking(True)

            self.resizeColumnsToContents()  # Columns resized

        except Exception as e:
            print(e)
            self.setMouseTracking(True)

    def change_cell_color(self, item_origin):
        """
        The background color and the value of the cells will change when the user changes an item
        Handles the multi-selection case
        """

        self.itemChanged.disconnect()
        new_value = item_origin.data(Qt.EditRole)

        cells_types = []  # Will contain the type list of the selection

        # self.fill_cells_update_table()  # To reset the first cell already changed

        # For each item selected, we check the validity of the types
        for item in self.selectedItems():
            row = item.row()
            col = item.column()
            tag_name = self.horizontalHeaderItem(col).text()
            tag_object = self.project.session.get_field(COLLECTION_CURRENT, tag_name)
            tag_type = tag_object.type

            if tag_name == TAG_BRICKS or tag_name == TAG_FILENAME:
                self.update_colors()
                self.itemChanged.connect(self.change_cell_color)
                return

            # Type added to types list
            if not tag_type in cells_types:
                cells_types.append(tag_type)

        # Error if list with other types
        if FIELD_TYPE_LIST_DATE in cells_types or FIELD_TYPE_LIST_DATETIME in cells_types or FIELD_TYPE_LIST_TIME in cells_types or FIELD_TYPE_LIST_INTEGER in cells_types or FIELD_TYPE_LIST_STRING in cells_types or FIELD_TYPE_LIST_FLOAT in cells_types or FIELD_TYPE_LIST_BOOLEAN in cells_types and len(
                cells_types) > 1:
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

        # Nothing to do if list
        if FIELD_TYPE_LIST_DATE in cells_types or FIELD_TYPE_LIST_DATETIME in cells_types or FIELD_TYPE_LIST_TIME in cells_types or FIELD_TYPE_LIST_INTEGER in cells_types or FIELD_TYPE_LIST_STRING in cells_types or FIELD_TYPE_LIST_FLOAT in cells_types or FIELD_TYPE_LIST_BOOLEAN in cells_types:
            self.itemChanged.connect(self.change_cell_color)
            return

        # We check that the value is compatible with all the types
        types_compatibles = True
        for cell_type in cells_types:
            if not check_value_type(new_value, cell_type):
                types_compatibles = False
                type_problem = cell_type
                break

        # Error if invalid value
        if not types_compatibles:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Invalid value")
            msg.setInformativeText("The value " + str(new_value) + " is invalid with the type " + type_problem)
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
                database_value = table_to_database(new_value, self.project.session.get_field(COLLECTION_CURRENT, tag_name).type)

                # We only set the cell if it's not the tag name
                if (tag_name != TAG_FILENAME):

                    old_value = self.project.session.get_value(COLLECTION_CURRENT, scan_path, tag_name)
                    # The scan already has a value for the tag: we update it
                    if old_value is not None:
                        modified_values.append([scan_path, tag_name, old_value, database_value])
                        self.project.session.set_value(COLLECTION_CURRENT, scan_path, tag_name, database_value)
                    # The scan does not have a value for the tag yet: we add it
                    else:
                        modified_values.append([scan_path, tag_name, None, database_value])
                        self.project.session.add_value(COLLECTION_CURRENT, scan_path, tag_name, database_value)

                        # Font reset in case it was a not defined cell
                        font = item.font()
                        font.setItalic(False)
                        font.setBold(False)
                        item.setFont(font)

                    set_item_data(item, new_value, self.project.session.get_field(COLLECTION_CURRENT, tag_name).type)

            # For history
            historyMaker.append(modified_values)
            self.project.undos.append(historyMaker)
            self.project.redos.clear()

            self.resizeColumnsToContents()  # Columns resized

        self.update_colors()

        self.itemChanged.connect(self.change_cell_color)