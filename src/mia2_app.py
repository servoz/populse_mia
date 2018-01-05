import sys
import os
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QDialog, \
    QVBoxLayout, QLabel, QListWidgetItem
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem
import controller, utils
from models import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.createUI()

    def createUI(self):

        # Menubar
        menu_file = self.menuBar().addMenu('File')
        menu_help = self.menuBar().addMenu('Help')
        # TODO: ADD MORE MENUS ?

        # Actions in the "File" menu
        action_create = menu_file.addAction('Create project')
        action_open = menu_file.addAction('Open project')
        action_edit = menu_file.addAction('Edit project')
        action_save = menu_file.addAction('Save project')
        action_settings = menu_file.addAction('Setting')
        action_exit = menu_file.addAction('Exit')
        # TODO: ADD SHORTCUTS ?
        # TODO: ADD MORE ACTIONS ?

        # Connection of the several triggered signals of the actions to some other methods
        action_create.triggered.connect(self.create_project_pop_up)
        action_open.triggered.connect(self.open_project_pop_up)
        action_exit.triggered.connect(self.close)

        self.setWindowTitle('MIA II')
        self.setGeometry(50, 50, 1500, 900)
        self.show()
        return self

    def create_project_pop_up(self):
        # Ui_Dialog() is defined at the end of this script
        self.exPopup = Ui_Dialog()

        # Once the user has selected his project, the 'signal_create_project" signal is emitted
        # Which will be connected to the modify_ui method that controls the following processes
        self.exPopup.signal_create_project.connect(self.modify_ui)
        self.exPopup.setGeometry(475, 275, 400, 300)
        self.exPopup.show()

    def open_project_pop_up(self):
        # Ui_Dialog() is defined at the end of this script
        self.exPopup = Ui_Dialog_Open()

        # Once the user has selected his project, the 'signal_create_project" signal is emitted
        # Which will be connected to the modify_ui method that controls the following processes
        self.exPopup.signal_create_project.connect(self.modify_ui)
        self.exPopup.setGeometry(475, 275, 400, 300)
        self.exPopup.show()

    @pyqtSlot()
    def modify_ui(self):
        """
        This method will only "allocate" the several tables and lists of the application
        """
        # This list will later contain all the tags in the project
        self.list_selected_tags = []
        #print(self.liste)
        # We get the name and the path of the current project to open it
        name = self.exPopup.name
        path = self.exPopup.new_path
        data_path = os.path.join(path, 'data')
        raw_data = os.path.join(data_path, 'raw_data')
        self.project = controller.open_project(name, path)

        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setObjectName("centralwidget")

        # Creating the widget that will contain the several tabs
        self.tab_widget = QtWidgets.QTabWidget(self.central_widget)
        self.tab_widget.setEnabled(True)
        self.tab_widget.setGeometry(QtCore.QRect(0, 0, 1500, 875))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.tab_widget.sizePolicy().hasHeightForWidth())
        self.tab_widget.setSizePolicy(size_policy)
        self.tab_widget.setStyleSheet("")
        self.tab_widget.setObjectName("tabWidget")

        ################################################################################################################
        # 'List' tab
        ################################################################################################################

        # Initializing the "List" tab
        self.tab_list = QtWidgets.QWidget()
        self.tab_list.setObjectName("tab")

        # List of the scans contained in the project
        self.list_widget_scans = QtWidgets.QListWidget(self.tab_list)
        self.list_widget_scans.setGeometry(QtCore.QRect(100, 200, 408, 485))
        self.list_widget_scans.setObjectName("listWidget_1")
        self.list_widget_scans.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        nb = 0
        while nb < len(self.project._get_scans()):
            item = QtWidgets.QListWidgetItem()
            self.list_widget_scans.addItem(item)
            nb += 1

        # List of all the tags contained in the project
        list_tag = Project.getAllTagsNames(self.project)
        self.list_widget_tags = QtWidgets.QListWidget(self.tab_list)
        self.list_widget_tags.setGeometry(QtCore.QRect(700, 200, 279, 485))
        self.list_widget_tags.setObjectName("listWidget")
        self.list_widget_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        nb = 1
        while nb <= len(list_tag):
            item = QtWidgets.QListWidgetItem()
            self.list_widget_tags.addItem(item)
            nb += 1

        # List of the tags selected by the user
        self.list_widget_selected_tags = QtWidgets.QListWidget(self.tab_list)
        self.list_widget_selected_tags.setGeometry(QtCore.QRect(1100, 200, 279, 485))
        self.list_widget_selected_tags.setObjectName("listWidget_2")
        self.list_widget_selected_tags.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        # Parent folder of the raw data
        self.label_parent_folder = QtWidgets.QLabel(self.tab_list)
        self.label_parent_folder.setGeometry(QtCore.QRect(10, 15, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Arial Unicode MS")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label_parent_folder.setFont(font)
        self.label_parent_folder.setObjectName("label")
        self.parent_folder = QtWidgets.QLabel(self.tab_list)
        self.parent_folder.setGeometry(QtCore.QRect(100, 15, 1400, 21))
        self.parent_folder.setObjectName("parent_folder")
        self.parent_folder.setText(raw_data)

        # "OK" button to pass to the 'Table' tab
        self.push_button_to_table = QtWidgets.QPushButton(self.tab_list)
        self.push_button_to_table.setGeometry(QtCore.QRect(1400, 800, 41, 20))
        self.push_button_to_table.setStyleSheet("background-color: rgb(129, 255, 110);")
        self.push_button_to_table.setObjectName("pushButton")
        self.push_button_to_table.clicked.connect(self.table_tab)

        # Title of the three list widgets
        self.label_file_paths = QtWidgets.QLabel(self.tab_list)
        self.label_file_paths.setGeometry(QtCore.QRect(280, 150, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_file_paths.setFont(font)
        self.label_file_paths.setObjectName("label_2")

        self.label_tags_with_files = QtWidgets.QLabel(self.tab_list)
        self.label_tags_with_files.setGeometry(QtCore.QRect(800, 150, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_tags_with_files.setFont(font)
        self.label_tags_with_files.setObjectName("label_3")

        self.label_selected_tags = QtWidgets.QLabel(self.tab_list)
        self.label_selected_tags.setGeometry(QtCore.QRect(1200, 150, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_selected_tags.setFont(font)
        self.label_selected_tags.setObjectName("label_4")

        # Frames and labels that display the number of scans (files)/tags/selected tags
        self.frame_nb_files = QtWidgets.QFrame(self.tab_list)
        self.frame_nb_files.setGeometry(QtCore.QRect(100, 685, 408, 41))
        self.frame_nb_files.setStyleSheet("background-color: rgb(195, 255, 190);")
        self.frame_nb_files.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_nb_files.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_nb_files.setObjectName("frame")

        self.label_nb_files = QtWidgets.QLabel(self.frame_nb_files)
        self.label_nb_files.setGeometry(QtCore.QRect(40, 10, 81, 16))
        self.label_nb_files.setObjectName("label_5")

        self.nb_files = QtWidgets.QLabel(self.frame_nb_files)
        self.nb_files.setGeometry(QtCore.QRect(130, 10, 47, 21))
        self.nb_files.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.nb_files.setText(str(self.list_widget_scans.count()))
        self.nb_files.setObjectName("number_file")

        self.frame_nb_tags = QtWidgets.QFrame(self.tab_list)
        self.frame_nb_tags.setGeometry(QtCore.QRect(700, 685, 279, 41))
        self.frame_nb_tags.setStyleSheet("background-color: rgb(195, 255, 190);")
        self.frame_nb_tags.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_nb_tags.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_nb_tags.setObjectName("frame_2")

        self.label_nb_tags = QtWidgets.QLabel(self.frame_nb_tags)
        self.label_nb_tags.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.label_nb_tags.setObjectName("label_6")

        self.nb_tags = QtWidgets.QLabel(self.frame_nb_tags)
        self.nb_tags.setGeometry(QtCore.QRect(100, 10, 47, 21))
        self.nb_tags.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.nb_tags.setText(str(self.list_widget_tags.count()))
        self.nb_tags.setObjectName("number_tag")

        self.frame_selected_tags = QtWidgets.QFrame(self.tab_list)
        self.frame_selected_tags.setGeometry(QtCore.QRect(1100, 685, 279, 41))
        self.frame_selected_tags.setStyleSheet("background-color: rgb(195, 255, 190);")
        self.frame_selected_tags.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_selected_tags.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_selected_tags.setObjectName("frame_3")

        self.label_nb_selected_tags = QtWidgets.QLabel(self.frame_selected_tags)
        self.label_nb_selected_tags.setGeometry(QtCore.QRect(5, 10, 121, 16))
        self.label_nb_selected_tags.setObjectName("label_8")

        self.nb_selected_tags = QtWidgets.QLabel(self.frame_selected_tags)
        self.nb_selected_tags.setGeometry(QtCore.QRect(140, 10, 31, 21))
        self.nb_selected_tags.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.nb_selected_tags.setText(str(self.list_widget_selected_tags.count()))
        self.nb_selected_tags.setObjectName("number_file_2")

        # Button to launch the conversion software "MRI Manager File"
        self.push_button_conversion = QtWidgets.QPushButton(self.tab_list)
        self.push_button_conversion.setGeometry(QtCore.QRect(15, 70, 91, 31))
        self.push_button_conversion.setStyleSheet("background-color: rgb(93, 255, 24);")
        self.push_button_conversion.setObjectName("pushButton_2")
        self.push_button_conversion.clicked.connect(self.conversion_software)

        # Two buttons to select of unselect tags
        self.push_button_select_tag = QtWidgets.QPushButton(self.tab_list)
        self.push_button_select_tag.setGeometry(QtCore.QRect(1010, 385, 51, 21))
        self.push_button_select_tag.setObjectName("pushButton_3")
        self.push_button_select_tag.clicked.connect(self.click_select_tag)

        self.push_button_unselect_tag = QtWidgets.QPushButton(self.tab_list)
        self.push_button_unselect_tag.setGeometry(QtCore.QRect(1010, 440, 51, 21))
        self.push_button_unselect_tag.setObjectName("pushButton_4")
        self.push_button_unselect_tag.clicked.connect(self.click_unselect_tag)


        ################################################################################################################
        # 'Table' tab
        ################################################################################################################

        self.tab_widget.addTab(self.tab_list, "")
        self.tab_table = QtWidgets.QWidget()
        self.tab_table.setObjectName("tab_2")

        # Frame of the tag table will be display
        self.frame_principal_table = QtWidgets.QFrame(self.tab_table)
        self.frame_principal_table.setGeometry(QtCore.QRect(0, 0, 1500, 437))
        self.frame_principal_table.setStyleSheet("background-color: rgb(228, 237, 255);\n"
                                   "border-color: rgb(0, 0, 127);\n"
                                   "\n"
                                   "")
        self.frame_principal_table.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_principal_table.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_principal_table.setObjectName("frame_4")
        self.label_principal_table = QtWidgets.QLabel(self.frame_principal_table)
        self.label_principal_table.setGeometry(QtCore.QRect(10, 10, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setUnderline(True)
        self.label_principal_table.setFont(font)
        self.label_principal_table.setObjectName("label_9")

        # Main table that will contain all the tags
        self.table_widget_main = QtWidgets.QTableWidget(self.frame_principal_table)
        self.table_widget_main.setGeometry(QtCore.QRect(110, 40, 1200, 380))
        self.table_widget_main.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.table_widget_main.setObjectName("tableWidget")

        self.nb_columns = int(self.list_widget_selected_tags.count())
        self.table_widget_main.setColumnCount(self.nb_columns + 1)

        nb_rows = len(self.project._get_scans())
        self.table_widget_main.setRowCount(nb_rows)

        # It allows to move the columns
        self.table_widget_main.horizontalHeader().setSectionsMovable(True)

        # Initializing the headers for each row and each column
        item = QtWidgets.QTableWidgetItem()
        j = 0
        while j < nb_rows:
            self.table_widget_main.setVerticalHeaderItem(j, item)
            item = QtWidgets.QTableWidgetItem()
            j += 1

        i = 0
        while i <= self.nb_columns+1:
            self.table_widget_main.setHorizontalHeaderItem(i, item)
            item = QtWidgets.QTableWidgetItem()
            i += 1

        # Initializing each cell of the table
        row = (-1)
        while row < nb_rows:
            row += 1
            column = 0
            while column <= self.nb_columns+1:
                self.table_widget_main.setItem(row, column, item)
                item = QtWidgets.QTableWidgetItem()
                column += 1

        # Push button to add a tag (not functional yet)
        self.push_button_add_tag = QtWidgets.QPushButton(self.frame_principal_table)
        self.push_button_add_tag.setGeometry(QtCore.QRect(1370, 300, 75, 23))
        self.push_button_add_tag.setStyleSheet("background-color: rgb(117, 177, 255);")
        self.push_button_add_tag.setObjectName("pushButton_5")

        # Push button to show all tag (not functional yet, maybe have to delete it)
        self.push_button_show_all = QtWidgets.QPushButton(self.frame_principal_table)
        self.push_button_show_all.setGeometry(QtCore.QRect(10, 50, 75, 23))
        self.push_button_show_all.setStyleSheet("background-color: rgb(117, 177, 255);")
        self.push_button_show_all.setObjectName("pushButton_6")

        # Visualization frame, label and text edit (bottom left of the screen in the application)
        self.frame_visualization = QtWidgets.QFrame(self.tab_table)
        self.frame_visualization.setGeometry(QtCore.QRect(0, 438, 750, 437))
        self.frame_visualization.setStyleSheet("background-color: rgb(234, 237, 255);")
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

        self.visualisation_path = QtWidgets.QTextEdit(self.frame_visualization)
        self.visualisation_path.setGeometry(QtCore.QRect(90, 0, 650, 31))
        self.visualisation_path.setStyleSheet("")
        self.visualisation_path.setObjectName("visualisation_path")

        # Countable table frame, label and text edit (bottom right of the screen in the application)
        self.frame_countable_table = QtWidgets.QFrame(self.tab_table)
        self.frame_countable_table.setGeometry(QtCore.QRect(751, 438, 749, 437))
        self.frame_countable_table.setStyleSheet("background-color: rgb(229, 237, 255);")
        self.frame_countable_table.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_countable_table.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_countable_table.setObjectName("frame_6")

        self.label_countable_table = QtWidgets.QLabel(self.frame_countable_table)
        self.label_countable_table.setGeometry(QtCore.QRect(10, 10, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setUnderline(True)
        self.label_countable_table.setFont(font)
        self.label_countable_table.setObjectName("label_11")

        self.comptable_path = QtWidgets.QTextEdit(self.frame_countable_table)
        self.comptable_path.setGeometry(QtCore.QRect(100, 0, 600, 31))
        self.comptable_path.setObjectName("comptable_path")

        # The table called 'Countable table' (should be deleted)
        self.table_widget_count_table = QtWidgets.QTableWidget(self.frame_countable_table)
        self.table_widget_count_table.setGeometry(QtCore.QRect(20, 50, 371, 171))
        self.table_widget_count_table.setObjectName("tableWidget_2")
        self.table_widget_count_table.setColumnCount(5)
        self.table_widget_count_table.setRowCount(4)

        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(0, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(1, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(1, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(2, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(2, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(2, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(3, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(3, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(3, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget_count_table.setItem(3, 4, item)
        self.tab_widget.addTab(self.tab_table, "")
        self.tab_process = QtWidgets.QWidget()
        self.tab_process.setObjectName("tab_3")
        self.tab_widget.addTab(self.tab_process, "")

        self.setCentralWidget(self.central_widget)
        # Calling retranslateUi that will fill all the tables, lists etc. with the project data
        self.retranslateUi(self.project)
        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)


    def retranslateUi(self, project):
        """
        This method will fill the tables, lists, labels etc. of the application with the data of the project
        :param project:
        :return:
        """
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # The 'list_file' list will contain the paths of the scans of the project
        __sortingEnabled = self.list_widget_scans.isSortingEnabled()
        self.list_widget_scans.setSortingEnabled(False)
        nb = 0
        list_file = []
        for p_scan in project._get_scans():
            list_file.append(p_scan.file_path)
            item = self.list_widget_scans.item(nb)
            item.setText(_translate("Dialog", p_scan.file_path))
            nb += 1
        self.list_widget_scans.setSortingEnabled(__sortingEnabled)

        # The 'list_tag' list will contain the paths of the tags of the project
        __sortingEnabled = self.list_widget_tags.isSortingEnabled()
        self.list_widget_tags.setSortingEnabled(False)
        list_tag = Project.getAllTagsNames(project)
        nb = 0
        for i in list_tag:
            item = self.list_widget_tags.item(nb)
            item.setText(_translate("Dialog", i))
            nb += 1
        self.list_widget_tags.setSortingEnabled(__sortingEnabled)

        # Setting the texts of the several labels and buttons
        self.label_parent_folder.setText(_translate("MainWindow", "Parent folder:"))
        self.push_button_to_table.setText(_translate("MainWindow", "OK"))
        self.label_file_paths.setText(_translate("MainWindow", "File paths"))
        self.label_tags_with_files.setText(_translate("MainWindow", "Tags with files"))
        self.label_selected_tags.setText(_translate("MainWindow", "Selected Tags"))
        self.label_nb_files.setText(_translate("MainWindow", "Number of files:"))
        self.label_nb_tags.setText(_translate("MainWindow", "Number of tags:"))
        self.label_nb_selected_tags.setText(_translate("MainWindow", "Number of selected tags:"))
        self.push_button_conversion.setText(_translate("MainWindow", "Load Files"))
        self.push_button_select_tag.setText(_translate("MainWindow", "-->"))
        self.push_button_unselect_tag.setText(_translate("MainWindow", "<--"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_list), _translate("MainWindow", "List"))


        ################################################################################################################
        # 'Table' tab
        ################################################################################################################

        self.label_principal_table.setText(_translate("MainWindow", "Principal Table"))

        # Principal table
        """ Rows legend: 1 to the number of scans """
        nb = 0
        while nb < len(project._get_scans()):
            item = self.table_widget_main.verticalHeaderItem(nb)
            i = str(nb+1)
            item.setText(_translate("MainWindow", i))
            nb += 1

        """ First column legend """
        item = self.table_widget_main.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Path"))

        """ Filling the first column with the path of each scan """
        nb = 0
        for i in project._get_scans():
            a = str(i.file_path)
            item = QTableWidgetItem()
            item.setText(a)
            self.table_widget_main.setItem(nb, 0, item)
            nb += 1

        self.table_widget_main.setSortingEnabled(__sortingEnabled)

        self.push_button_add_tag.setText(_translate("MainWindow", "Add tag"))
        self.push_button_show_all.setText(_translate("MainWindow", "Show all"))

        # Visualization part
        self.label_visualization.setText(_translate("MainWindow", "Vizualisation:"))

        # Countable table
        self.label_countable_table.setText(_translate("MainWindow", "Countable table:"))
        item = self.table_widget_count_table.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "ef"))
        item = self.table_widget_count_table.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "ab"))
        item = self.table_widget_count_table.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "cd"))
        item = self.table_widget_count_table.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "total"))
        item = self.table_widget_count_table.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "4"))
        item = self.table_widget_count_table.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "1"))
        item = self.table_widget_count_table.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "2"))
        item = self.table_widget_count_table.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "3"))
        item = self.table_widget_count_table.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "total"))
        __sortingEnabled = self.table_widget_count_table.isSortingEnabled()
        self.table_widget_count_table.setSortingEnabled(False)
        item = self.table_widget_count_table.item(0, 0)
        item.setText(_translate("MainWindow", "0"))
        item = self.table_widget_count_table.item(0, 1)
        item.setText(_translate("MainWindow", "0"))
        item = self.table_widget_count_table.item(0, 2)
        item.setText(_translate("MainWindow", "1"))
        item = self.table_widget_count_table.item(0, 3)
        item.setText(_translate("MainWindow", "2"))
        item = self.table_widget_count_table.item(0, 4)
        item.setText(_translate("MainWindow", "3"))
        item = self.table_widget_count_table.item(1, 0)
        item.setText(_translate("MainWindow", "0"))
        item = self.table_widget_count_table.item(1, 1)
        item.setText(_translate("MainWindow", "4"))
        item = self.table_widget_count_table.item(1, 2)
        item.setText(_translate("MainWindow", "0"))
        item = self.table_widget_count_table.item(1, 3)
        item.setText(_translate("MainWindow", "0"))
        item = self.table_widget_count_table.item(1, 4)
        item.setText(_translate("MainWindow", "4"))
        item = self.table_widget_count_table.item(2, 0)
        item.setText(_translate("MainWindow", "3"))
        item = self.table_widget_count_table.item(2, 1)
        item.setText(_translate("MainWindow", "1"))
        item = self.table_widget_count_table.item(2, 2)
        item.setText(_translate("MainWindow", "6"))
        item = self.table_widget_count_table.item(2, 3)
        item.setText(_translate("MainWindow", "0"))
        item = self.table_widget_count_table.item(2, 4)
        item.setText(_translate("MainWindow", "10"))
        item = self.table_widget_count_table.item(3, 0)
        item.setText(_translate("MainWindow", "3"))
        item = self.table_widget_count_table.item(3, 1)
        item.setText(_translate("MainWindow", "5"))
        item = self.table_widget_count_table.item(3, 2)
        item.setText(_translate("MainWindow", "7"))
        item = self.table_widget_count_table.item(3, 3)
        item.setText(_translate("MainWindow", "2"))
        item = self.table_widget_count_table.item(3, 4)
        item.setText(_translate("MainWindow", "17"))

        self.table_widget_count_table.setSortingEnabled(__sortingEnabled)
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_table), _translate("MainWindow", "Table"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_process), _translate("MainWindow", "Process"))

    def conversion_software(self):
        # Opens the conversion software to convert the MRI files in Nifti/Json
        import subprocess
        subprocess.call(['java', '-jar', 'MRIManagerFinal.jar', '[ExportNifti] C:\\Users\\omonti\\Desktop\\tmpNifti',
                         '[Info] Traitement IRMaGe'])

    def click_select_tag(self):
        # Put the selected tags in the "selected tag" table
        rows = sorted([index.row() for index in self.list_widget_tags.selectedIndexes()],
                      reverse=True)
        for row in rows:
            # assuming the other listWidget is called listWidget_2
            self.list_widget_selected_tags.addItem(self.list_widget_tags.takeItem(row))
        self.nb_tags.setText(str(self.list_widget_tags.count()))
        self.nb_selected_tags.setText(str(self.list_widget_selected_tags.count()))

    def click_unselect_tag(self):
        # Remove the unselected tags from the "selected tag" table
        rows = sorted([index.row() for index in self.list_widget_selected_tags.selectedIndexes()],
                      reverse=True)
        for row in rows:
            self.list_widget_tags.addItem(self.list_widget_selected_tags.takeItem(row))
        self.nb_tags.setText(str(self.list_widget_tags.count()))
        self.nb_selected_tags.setText(str(self.list_widget_selected_tags.count()))

    def table_tab(self):
        """
        This method will fill the tables in the 'Table' tab with the project data
        """

        self.tab_widget.setCurrentIndex(1)
        self.nb_columns = self.list_widget_selected_tags.count()
        self.table_widget_main.setColumnCount(self.nb_columns + 1)

        # This list will contain all the selected tags
        self.list_selected_tags = []

        item = QtWidgets.QTableWidgetItem()
        i = 0
        # Already done at line 310
        while i <= self.nb_columns + 1:
            self.table_widget_main.setHorizontalHeaderItem(i, item)
            item = QtWidgets.QTableWidgetItem()
            i += 1

        # Filling 'list_selected_tags' with the selected tags
        nb_sel_tags = self.list_widget_selected_tags.count()
        i = 0
        while i < nb_sel_tags:
            dirname = self.list_widget_selected_tags.item(i).text()
            self.list_selected_tags.append(dirname)
            i += 1

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # Filling the header of the columns
        item = self.table_widget_main.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", 'Path'))
        nb = 1
        for element in self.list_selected_tags:
            item = self.table_widget_main.horizontalHeaderItem(nb)
            element = str(element)
            item.setText(_translate("MainWindow", element))
            nb += 1

        # Filling all the cells
        y = -1
        # Loop on the scans
        for file in self.project._get_scans():
            y += 1
            i = 0
            # Loop on the selected tags
            for tag in self.list_selected_tags:
                i += 1
                # If the tag belong to the tags of the project (of course it does...)
                if tag in controller.getAllTagsFile(file.file_path, self.project):
                    # Loop on the project tags
                    for n_tag in file._get_tags():
                        # If a project tag name matches our tag
                        if n_tag.name == tag:
                            # He is put in the table
                            a = str(n_tag.value)
                            item = QTableWidgetItem()
                            item.setText(a)
                            self.table_widget_main.setItem(y, i, item)
                else:
                    a = str('NaN')
                    item = QTableWidgetItem()
                    item.setText(a)
                    self.table_widget_main.setItem(y, i, item)



        return self.list_selected_tags



class Ui_Dialog(QDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self1):
        super().__init__()
        self1.pop_up()

    def pop_up(self1):
        self1.setObjectName("Dialog")
        self1.setStyleSheet("background-color: rgb(129, 173, 200);")

        # The 'OK' push button
        self1.push_button_ok = QtWidgets.QPushButton(self1)
        self1.push_button_ok.setGeometry(QtCore.QRect(350, 260, 31, 20))
        self1.push_button_ok.setStyleSheet("color: rgb(6, 6, 6); background-color: rgb(221, 221, 221);")
        self1.push_button_ok.setObjectName("pushButton")

        # The 'Project name' label
        self1.label_project_name = QtWidgets.QLabel(self1)
        self1.label_project_name.setGeometry(QtCore.QRect(50, 80, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self1.label_project_name.setFont(font)
        self1.label_project_name.setTextFormat(QtCore.Qt.AutoText)
        self1.label_project_name.setObjectName("label")

        # The 'Parent folder' label
        self1.label_parent_folder = QtWidgets.QLabel(self1)
        self1.label_parent_folder.setGeometry(QtCore.QRect(50, 170, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self1.label_parent_folder.setFont(font)
        self1.label_parent_folder.setTextFormat(QtCore.Qt.AutoText)
        self1.label_parent_folder.setObjectName("label_2")

        # A label to display if the chosen project name already exists
        self1.label_name_already_exists = QtWidgets.QLabel(self1)
        self1.label_name_already_exists.setGeometry(QtCore.QRect(50, 20, 350, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setWeight(75)
        self1.label_name_already_exists.setStyleSheet("color: rgb(255, 0, 0);")
        self1.label_name_already_exists.setFont(font)
        self1.label_name_already_exists.setTextFormat(QtCore.Qt.AutoText)
        self1.label_name_already_exists.setObjectName("label")

        # The 'File name' text edit
        self1.text_edit_file_name = QtWidgets.QTextEdit(self1)
        self1.text_edit_file_name.setGeometry(QtCore.QRect(160, 80, 151, 31))
        self1.text_edit_file_name.setStyleSheet("background-color: rgb(255, 255, 255);")
        self1.text_edit_file_name.setObjectName("textEdit")

        # The 'Path name' text edit
        self1.text_edit_path_name = QtWidgets.QTextEdit(self1)
        self1.text_edit_path_name.setGeometry(QtCore.QRect(160, 170, 151, 31))
        self1.text_edit_path_name.setStyleSheet("background-color: rgb(255, 255, 255);")
        self1.text_edit_path_name.setObjectName("textEdit_2")

        # The 'Browse' push button to search the folder
        self1.push_button_browse = QtWidgets.QPushButton(self1)
        self1.push_button_browse.setGeometry(QtCore.QRect(320, 180, 51, 20))
        font = QtGui.QFont()
        font.setItalic(True)
        self1.push_button_browse.setFont(font)
        self1.push_button_browse.setStyleSheet("background-color: rgb(163, 163, 163);")
        self1.push_button_browse.setObjectName("pushButton_2")

        # Filling the title of the labels and push buttons
        _translate = QtCore.QCoreApplication.translate
        self1.setWindowTitle(_translate("Dialog", "Create project"))
        self1.push_button_ok.setText(_translate("Dialog", "OK"))
        self1.label_project_name.setText(_translate("Dialog", "Project name :"))
        self1.label_parent_folder.setText(_translate("Dialog", "Parent folder :"))
        self1.push_button_browse.setText(_translate("Dialog", "browse"))

        # Connecting the push buttons
        self1.push_button_browse.clicked.connect(self1.folderExploratorCreate)
        self1.push_button_ok.clicked.connect(self1.create_project)

    def folderExploratorCreate(self1):
        # To search the folder
        from PyQt5.QtWidgets import QFileDialog
        fileName = QFileDialog.getExistingDirectory(self1, "Selected directory2")
        if fileName:
            self1.text_edit_path_name.setText(fileName)

    def create_project(self1):
        # When the 'OK' button is clicked
        name = self1.text_edit_file_name.toPlainText()
        self1.name = name
        recorded_path = self1.text_edit_path_name.toPlainText()
        recorded_path = os.path.abspath(recorded_path)
        new_path = os.path.join(recorded_path, name)
        self1.new_path = new_path

        # If the file name does not exists
        if not os.path.exists(new_path):
            controller.createProject(name, 'D :\data_nifti_json', recorded_path)
            self1.close()
            # A signal is emitted to tell that the project has been created
            self1.signal_create_project.emit()
        else:
            _translate = QtCore.QCoreApplication.translate
            self1.label_name_already_exists.setText(_translate("Dialog", "This name already exists in this parent folder"))


class Ui_Dialog_Open(QDialog):
    """
    Is called when the user wants to create a new project
    """

    # Signal that will be emitted at the end to tell that the project has been created
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pop_up()

    def pop_up(self):
        self.setObjectName("Dialog")
        self.setStyleSheet("background-color: rgb(129, 173, 200);")

        # The 'OK' push button
        self.push_button_ok = QtWidgets.QPushButton(self)
        self.push_button_ok.setGeometry(QtCore.QRect(350, 260, 31, 20))
        self.push_button_ok.setStyleSheet("color: rgb(6, 6, 6); background-color: rgb(221, 221, 221);")
        self.push_button_ok.setObjectName("pushButton")

        # The 'Project name' label
        self.label_project_name = QtWidgets.QLabel(self)
        self.label_project_name.setGeometry(QtCore.QRect(50, 80, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_project_name.setFont(font)
        self.label_project_name.setTextFormat(QtCore.Qt.AutoText)
        self.label_project_name.setObjectName("label")

        # The 'Parent folder' label
        self.label_parent_folder = QtWidgets.QLabel(self)
        self.label_parent_folder.setGeometry(QtCore.QRect(50, 170, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_parent_folder.setFont(font)
        self.label_parent_folder.setTextFormat(QtCore.Qt.AutoText)
        self.label_parent_folder.setObjectName("label_2")

        # A label to display if the chosen project name already exists
        self.label_name_does_not_exist = QtWidgets.QLabel(self)
        self.label_name_does_not_exist.setGeometry(QtCore.QRect(50, 20, 350, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setWeight(75)
        self.label_name_does_not_exist.setStyleSheet("color: rgb(255, 0, 0);")
        self.label_name_does_not_exist.setFont(font)
        self.label_name_does_not_exist.setTextFormat(QtCore.Qt.AutoText)
        self.label_name_does_not_exist.setObjectName("label")

        # The 'File name' text edit
        self.text_edit_file_name = QtWidgets.QTextEdit(self)
        self.text_edit_file_name.setGeometry(QtCore.QRect(160, 80, 151, 31))
        self.text_edit_file_name.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.text_edit_file_name.setObjectName("textEdit")

        # The 'Path name' text edit
        self.text_edit_path_name = QtWidgets.QTextEdit(self)
        self.text_edit_path_name.setGeometry(QtCore.QRect(160, 170, 151, 31))
        self.text_edit_path_name.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.text_edit_path_name.setObjectName("textEdit_2")

        # The 'Browse' push button to search the folder
        self.push_button_browse = QtWidgets.QPushButton(self)
        self.push_button_browse.setGeometry(QtCore.QRect(320, 180, 51, 20))
        font = QtGui.QFont()
        font.setItalic(True)
        self.push_button_browse.setFont(font)
        self.push_button_browse.setStyleSheet("background-color: rgb(163, 163, 163);")
        self.push_button_browse.setObjectName("pushButton_2")

        # Filling the title of the labels and push buttons
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Open project"))
        self.push_button_ok.setText(_translate("Dialog", "OK"))
        self.label_project_name.setText(_translate("Dialog", "Project name :"))
        self.label_parent_folder.setText(_translate("Dialog", "Parent folder :"))
        self.push_button_browse.setText(_translate("Dialog", "browse"))

        # Connecting the push buttons
        self.push_button_browse.clicked.connect(self.folderExplorator)
        self.push_button_ok.clicked.connect(self.open_project)

    def folderExplorator(self):
        # To search the folder
        from PyQt5.QtWidgets import QFileDialog
        fileName = QFileDialog.getExistingDirectory(self, "Selected directory")
        if fileName:
            self.text_edit_path_name.setText(fileName)

    def open_project(self):
        # When the 'OK' button is clicked
        name = self.text_edit_file_name.toPlainText()
        self.name = name
        new_path = self.text_edit_path_name.toPlainText()
        new_path = os.path.abspath(new_path)
        self.new_path = new_path

        # If the file exists
        if os.path.exists(new_path):
            controller.open_project(name, new_path)
            self.close()
            # A signal is emitted to tell that the project has been created
            self.signal_create_project.emit()
        else:
            _translate = QtCore.QCoreApplication.translate
            self.label_name_does_not_exist.setText(_translate("Dialog", "This name doesn't exist in this parent folder"))


    def project_name(self):
        name = Ui_Dialog_Open.open_project(self)
        return name



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
