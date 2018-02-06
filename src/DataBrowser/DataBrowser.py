from PyQt5.QtCore import Qt, QVariant, QPoint
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QTableWidget, QHBoxLayout, QSplitter
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem, QMenu
import controller
from models import *
from pop_ups import Ui_Dialog_add_tag, Ui_Dialog_clone_tag, Ui_Dialog_Type_Problem, Ui_Dialog_remove_tag, \
    Ui_Visualized_Tags, Ui_Dialog_Preferences
from functools import partial


class DataBrowser(QWidget):
    def __init__(self, project):

        super(DataBrowser, self).__init__()

        _translate = QtCore.QCoreApplication.translate

        ################################### TABLE ###################################

        # Frame behind the table
        self.frame_table_data = QtWidgets.QFrame(self)
        self.frame_table_data.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_table_data.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_table_data.setObjectName("frame_table_data")

        # Label
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
        self.push_button_remove_tag.clicked.connect(lambda: self.remove_tag_pop_up(project))

        # Main table that will display the tags
        self.table_data = TableDataBrowser(project)
        self.table_data.setObjectName("table_data")

        ## LAYOUTS ##

        vbox_table = QVBoxLayout()
        vbox_table.addWidget(self.label_principal_table)
        vbox_table.addWidget(self.push_button_add_tag)
        vbox_table.addWidget(self.push_button_clone_tag)
        vbox_table.addWidget(self.push_button_remove_tag)
        vbox_table.setSpacing(10)
        vbox_table.addStretch(1)

        hbox_table = QHBoxLayout()
        hbox_table.addLayout(vbox_table)
        hbox_table.addWidget(self.table_data)

        self.frame_table_data.setLayout(hbox_table)

        ################################### VISUALIZATION ###################################

        # Visualization frame, label and text edit (bottom left of the screen in the application)
        self.frame_visualization = QtWidgets.QFrame(self)
        self.frame_visualization.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_visualization.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_visualization.setObjectName("frame_5")

        self.label_visualization = QtWidgets.QLabel(self.frame_visualization)
        self.label_visualization.setGeometry(QtCore.QRect(10, 10, 81, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setUnderline(True)
        self.label_visualization.setFont(font)
        self.label_visualization.setObjectName("label_10")
        self.label_visualization.setText(_translate("MainWindow", "Vizualisation:"))

        self.visualisation_path = QtWidgets.QTextEdit(self.frame_visualization)
        self.visualisation_path.setGeometry(QtCore.QRect(90, 0, 650, 31))
        self.visualisation_path.setStyleSheet("")
        self.visualisation_path.setObjectName("visualisation_path")

        ## SPLITTER AND LAYOUT ##

        splitter_vertical = QSplitter(Qt.Vertical)
        splitter_vertical.addWidget(self.frame_table_data)
        splitter_vertical.addWidget(self.frame_visualization)

        hbox_splitter = QHBoxLayout(self)
        hbox_splitter.addWidget(splitter_vertical)
        self.setLayout(hbox_splitter)

    def add_tag_pop_up(self, project):
        # Ui_Dialog_add_tag() is defined in pop_ups.py
        self.pop_up_add_tag = Ui_Dialog_add_tag()
        self.pop_up_add_tag.show()

        if self.pop_up_add_tag.exec_() == QDialog.Accepted:
            (new_tag_name, new_default_value, type) = self.pop_up_add_tag.get_values()

            list_to_add = []
            list_to_add.append(type(new_default_value))

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

        # Adding a custom context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(partial(self.context_menu_table, project))
        self.flag_first_time = 0
        if project:
            self.update_table(project)

    def update_table(self, project):
        """
        This method will fill the tables in the 'Table' tab with the project data
        """

        self.flag_first_time += 1

        if self.flag_first_time > 1:
            self.itemChanged.disconnect()

        self.nb_columns = len(project.tags_to_visualize) + 1 # Read from MIA2 preferences

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

        # Filling the header of the columns
        item = self.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", 'Path'))

        nb = 1
        for element in project.tags_to_visualize:
            element = str(element)
            item = QTableWidgetItem()
            item.setText(_translate("MainWindow", element))
            self.setHorizontalHeaderItem(nb, item)
            nb += 1

        """ Filling the first column with the path of each scan """
        nb = 0
        for i in project._get_scans():
            a = str(i.file_path)
            item = QTableWidgetItem()
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setText(a)
            self.setItem(nb, 0, item)
            nb += 1

        # Filling all the cells
        y = -1
        # Loop on the scans

        for file in project._get_scans():
            y += 1
            i = 0

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
                            txt = utils.check_tag_value(n_tag, 'value')
                            item.setText(txt)

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

        __sortingEnabled = self.isSortingEnabled()
        self.setSortingEnabled(__sortingEnabled)
        self.resizeColumnsToContents()

        # When the user changes one item of the table, the background will change
        #self.itemChanged.connect(lambda item: self.change_cell_color(item, project))
        self.itemChanged.connect(partial(self.change_cell_color, project))

    def context_menu_table(self, project, position):

        self.flag_first_time += 1

        menu = QMenu(self)

        action_reset_cell = menu.addAction("Reset cell(s)")
        action_reset_column = menu.addAction("Reset column(s)")
        action_reset_row = menu.addAction("Reset row(s)")
        action_visualized_tags = menu.addAction("Visualized tags")

        action = menu.exec_(self.mapToGlobal(position))
        if action == action_reset_cell:
            self.reset_cell(project)
        elif action == action_reset_column:
            self.reset_column(project)
        elif action == action_reset_row:
            self.reset_row(project)
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
            # tag_name = self.table_widget_main.horizontalHeaderItem(col).text()
            scan_name = self.item(row, 0).text()
            for file in project._get_scans():
                if file.file_path == scan_name:
                    for n_tag in file.getAllTags():
                        if n_tag.name in project.tags_to_visualize:
                            idx = project.tags_to_visualize.index(n_tag.name) + 1
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

    def reset_cell_with_item(self, project, item_in):
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

    def visualized_tags_pop_up(self, project):
        self.pop_up = Ui_Dialog_Preferences(project)
        self.pop_up.tab_widget.setCurrentIndex(1)

        self.pop_up.setGeometry(300, 200, 800, 600)
        self.pop_up.show()

        if self.pop_up.exec_() == QDialog.Accepted:
            self.update_table(project)


    def change_cell_color(self, project, item):
        """
        The background color of the table will change when the user changes an item
        :return:
        """
        self.itemChanged.disconnect()
        row = item.row()
        col = item.column()
        tp = str
        scan_path = self.item(row, 0).text()
        tag_name = self.horizontalHeaderItem(col).text()
        text_value = item.text()

        for scan in project._get_scans():
            if scan_path == scan.file_path:
                for tag in scan.getAllTags():
                    if tag_name == tag.name:
                        tp = type(tag.original_value[0])
        try:

            test = tp(text_value)

        except ValueError:
            # Dialog that says that it is not possible
            self.pop_up_type = Ui_Dialog_Type_Problem(tp)
            self.pop_up_type.ok_signal.connect(partial(self.reset_cell_with_item, project, item))
            self.pop_up_type.exec()

        else:
            for scan in project._get_scans():
                if scan_path == scan.file_path:
                    for tag in scan.getAllTags():
                        if tag_name == tag.name:
                            txt = utils.check_tag_value(tag, 'original_value')
                            color = QColor()
                            if tag.origin != 'custom':
                                if str(item.text()) != str(txt):
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
                            tag_origin = tag.origin
                            tag_replace = tag.replace
                            tag_value_to_add = utils.text_to_tag_value(text_value, tag)
                            new_tag = Tag(tag_name, tag_replace, tag_value_to_add, tag_origin, tag.original_value)
                            scan.replaceTag(new_tag, tag_name, str(tag_origin))

        self.itemChanged.connect(partial(self.change_cell_color, project))