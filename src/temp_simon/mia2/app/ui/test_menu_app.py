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
        self.setWindowTitle('MIA II')
        menu = self.menuBar().addMenu('File')
        menu2 = self.menuBar().addMenu('Help')
        action = menu.addAction('Create project')
        action2 = menu.addAction('Open project')
        action3 = menu.addAction('Edit project')
        action4 = menu.addAction('Save project')
        action5 = menu.addAction('Setting')
        action6 = menu.addAction('Exit')
        action.triggered.connect(self.create_project_pop_up)
        action2.triggered.connect(self.open_project_pop_up)
        action6.triggered.connect(self.close)
        self.setGeometry(50, 50, 1500, 900)
        self.show()
        return self

    def create_project_pop_up(self):
        self.exPopup = Ui_Dialog()
        self.exPopup.signal_create_project.connect(self.modify_ui)
        self.exPopup.setGeometry(475, 275, 400, 300)
        self.exPopup.show()

    def open_project_pop_up(self):
        self.exPopup = Ui_Dialog_Open()
        self.exPopup.signal_create_project.connect(self.modify_ui)
        self.exPopup.setGeometry(475, 275, 400, 300)
        self.exPopup.show()

    @pyqtSlot()
    def modify_ui(self):

        name = self.exPopup.name
        path = self.exPopup.new_path
        data_path = os.path.join(path, 'data')
        raw_data = os.path.join(data_path, 'raw_data')
        project = controller.open_project(name, path)

        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setObjectName("centralwidget")

        ################################################################################################################
        # Onglet "Table"
        ################################################################################################################
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 1500, 875))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setStyleSheet("")
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")

        #liste des scans présent dans le projet
        self.listWidget_1 = QtWidgets.QListWidget(self.tab)
        self.listWidget_1.setGeometry(QtCore.QRect(100, 200, 408, 485))
        self.listWidget_1.setObjectName("listWidget_1")
        self.listWidget_1.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        nombre = 0
        while nombre < len(project._get_scans()):
            item = QtWidgets.QListWidgetItem()
            self.listWidget_1.addItem(item)
            nombre += 1
        print('test === ', self.listWidget_1.count())
        #liste de l'ensemble des tags présent dans le projet
        list_tag = Project.getAllTagsNames(project)
        self.listWidget = QtWidgets.QListWidget(self.tab)
        self.listWidget.setGeometry(QtCore.QRect(700, 200, 279, 485))
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        number = 1
        while number <= len(list_tag):
            item = QtWidgets.QListWidgetItem()
            self.listWidget.addItem(item)
            number += 1

        #liste des tags sélectionnés pour la suite de l'affichage
        self.listWidget_2 = QtWidgets.QListWidget(self.tab)
        self.listWidget_2.setGeometry(QtCore.QRect(1100, 200, 279, 485))
        self.listWidget_2.setObjectName("listWidget_2")
        self.listWidget_2.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)

        #repertoire parent des données brutes
        self.label = QtWidgets.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(10, 15, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Arial Unicode MS")
        font.setPointSize(10)
        font.setUnderline(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.parent_folder = QtWidgets.QLabel(self.tab)
        self.parent_folder.setGeometry(QtCore.QRect(100, 15, 1400, 21))
        self.parent_folder.setObjectName("parent_folder")
        self.parent_folder.setText(raw_data)

        #boutton OK pour passer à l'onglet "Table"
        self.pushButton = QtWidgets.QPushButton(self.tab)
        self.pushButton.setGeometry(QtCore.QRect(1400, 800, 41, 20))
        self.pushButton.setStyleSheet("background-color: rgb(129, 255, 110);")
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.test)

        #Titre des 3 QListWidgets
        self.label_2 = QtWidgets.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(280, 150, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(1200, 150, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(800, 150, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")

        # Frame + Label + Nombre ; compte des 3 QListWidget
        self.frame = QtWidgets.QFrame(self.tab)
        self.frame.setGeometry(QtCore.QRect(100, 685, 408, 41))
        self.frame.setStyleSheet("background-color: rgb(195, 255, 190);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_5 = QtWidgets.QLabel(self.frame)
        self.label_5.setGeometry(QtCore.QRect(40, 10, 81, 16))
        self.label_5.setObjectName("label_5")
        self.number_file = QtWidgets.QLabel(self.frame)
        self.number_file.setGeometry(QtCore.QRect(130, 10, 47, 21))
        self.number_file.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.number_file.setText(str(self.listWidget_1.count()))
        self.number_file.setObjectName("number_file")
        self.frame_2 = QtWidgets.QFrame(self.tab)
        self.frame_2.setGeometry(QtCore.QRect(700, 685, 279, 41))
        self.frame_2.setStyleSheet("background-color: rgb(195, 255, 190);")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label_6 = QtWidgets.QLabel(self.frame_2)
        self.label_6.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.label_6.setObjectName("label_6")
        self.number_tag = QtWidgets.QLabel(self.frame_2)
        self.number_tag.setGeometry(QtCore.QRect(100, 10, 47, 21))
        self.number_tag.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.number_tag.setText(str(self.listWidget.count()))
        self.number_tag.setObjectName("number_tag")
        self.label_7 = QtWidgets.QLabel(self.frame_2)
        self.label_7.setGeometry(QtCore.QRect(100, 40, 81, 16))
        self.label_7.setObjectName("label_7")
        self.frame_3 = QtWidgets.QFrame(self.tab)
        self.frame_3.setGeometry(QtCore.QRect(1100, 685, 279, 41))
        self.frame_3.setStyleSheet("background-color: rgb(195, 255, 190);")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.label_8 = QtWidgets.QLabel(self.frame_3)
        self.label_8.setGeometry(QtCore.QRect(5, 10, 121, 16))
        self.label_8.setObjectName("label_8")
        self.number_file_2 = QtWidgets.QLabel(self.frame_3)
        self.number_file_2.setGeometry(QtCore.QRect(140, 10, 31, 21))
        self.number_file_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.number_file_2.setText(str(self.listWidget_2.count()))
        self.number_file_2.setObjectName("number_file_2")

        #bouton de lancement du logiciel de conversion
        self.pushButton_2 = QtWidgets.QPushButton(self.tab)
        self.pushButton_2.setGeometry(QtCore.QRect(15, 70, 91, 31))
        self.pushButton_2.setStyleSheet("background-color: rgb(93, 255, 24);")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.logicielConversion)

        #2 Boutons pour basculer les tags d'une liste à l'autre
        self.pushButton_3 = QtWidgets.QPushButton(self.tab)
        self.pushButton_3.setGeometry(QtCore.QRect(1010, 385, 51, 21))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.click_pushButton)
        self.pushButton_4 = QtWidgets.QPushButton(self.tab)
        self.pushButton_4.setGeometry(QtCore.QRect(1010, 440, 51, 21))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.click_pushButton_return)


        ################################################################################################################
        # Onglet "Table"
        ################################################################################################################
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.frame_4 = QtWidgets.QFrame(self.tab_2)
        self.frame_4.setGeometry(QtCore.QRect(0, 0, 1500, 437))
        self.frame_4.setStyleSheet("background-color: rgb(228, 237, 255);\n"
                                   "border-color: rgb(0, 0, 127);\n"
                                   "\n"
                                   "")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.label_9 = QtWidgets.QLabel(self.frame_4)
        self.label_9.setGeometry(QtCore.QRect(10, 10, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setUnderline(True)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")

        #Tableau principal
        self.tableWidget = QtWidgets.QTableWidget(self.frame_4)
        self.tableWidget.setGeometry(QtCore.QRect(110, 40, 1200, 380))
        self.tableWidget.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.tableWidget.setObjectName("tableWidget")
        self.column = int(self.listWidget_2.count())
        print('BBB ===', self.column)
        row = len(project._get_scans())
        self.tableWidget.setColumnCount(self.column+1)
        self.tableWidget.setRowCount(row)
        item = QtWidgets.QTableWidgetItem()

        print(row)
        j = 0
        while j < row:
            self.tableWidget.setVerticalHeaderItem(j, item)
            item = QtWidgets.QTableWidgetItem()
            j += 1
        i = 0
        while i <= self.column+1:
            self.tableWidget.setHorizontalHeaderItem(i, item)
            item = QtWidgets.QTableWidgetItem()
            i += 1

        ligne = (-1)
        while ligne < row:
            ligne += 1
            colonne = 0
            while colonne <= self.column+1:
                self.tableWidget.setItem(ligne, colonne, item)
                item = QtWidgets.QTableWidgetItem()
                colonne += 1

        """self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(3)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(2, 2, item)"""


        self.pushButton_5 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_5.setGeometry(QtCore.QRect(1370, 300, 75, 23))
        self.pushButton_5.setStyleSheet("background-color: rgb(117, 177, 255);")
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_4)
        self.pushButton_6.setGeometry(QtCore.QRect(10, 50, 75, 23))
        self.pushButton_6.setStyleSheet("background-color: rgb(117, 177, 255);")
        self.pushButton_6.setObjectName("pushButton_6")
        self.frame_5 = QtWidgets.QFrame(self.tab_2)
        self.frame_5.setGeometry(QtCore.QRect(0, 438, 750, 437))
        self.frame_5.setStyleSheet("background-color: rgb(234, 237, 255);")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.label_10 = QtWidgets.QLabel(self.frame_5)
        self.label_10.setGeometry(QtCore.QRect(10, 10, 81, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setUnderline(True)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.visualisation_path = QtWidgets.QTextEdit(self.frame_5)
        self.visualisation_path.setGeometry(QtCore.QRect(90, 0, 650, 31))
        self.visualisation_path.setStyleSheet("")
        self.visualisation_path.setObjectName("visualisation_path")
        self.frame_6 = QtWidgets.QFrame(self.tab_2)
        self.frame_6.setGeometry(QtCore.QRect(751, 438, 749, 437))
        self.frame_6.setStyleSheet("background-color: rgb(229, 237, 255);")
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.label_11 = QtWidgets.QLabel(self.frame_6)
        self.label_11.setGeometry(QtCore.QRect(10, 10, 91, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setUnderline(True)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.comptable_path = QtWidgets.QTextEdit(self.frame_6)
        self.comptable_path.setGeometry(QtCore.QRect(100, 0, 600, 31))
        self.comptable_path.setObjectName("comptable_path")
        self.tableWidget_2 = QtWidgets.QTableWidget(self.frame_6)
        self.tableWidget_2.setGeometry(QtCore.QRect(20, 50, 371, 171))
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.tableWidget_2.setColumnCount(5)
        self.tableWidget_2.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(0, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(1, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(1, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(1, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(2, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(2, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(2, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(2, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(2, 4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(3, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(3, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(3, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(3, 3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_2.setItem(3, 4, item)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")

        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(project)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)


    def retranslateUi(self, project):

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))

        #Liste des scans présent dans le projet
        __sortingEnabled = self.listWidget_1.isSortingEnabled()
        self.listWidget_1.setSortingEnabled(False)
        numero = 0
        list_file = []
        for p_scan in project._get_scans():
            list_file.append(p_scan.file_path)
            item = self.listWidget_1.item(numero)
            item.setText(_translate("Dialog", p_scan.file_path))
            numero += 1
        self.listWidget_1.setSortingEnabled(__sortingEnabled)

        #liste des tags présent dans le projet
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        list_tag = Project.getAllTagsNames(project)
        numero = 0
        for i in list_tag:
            item = self.listWidget.item(numero)
            item.setText(_translate("Dialog", i))
            numero += 1
        self.listWidget.setSortingEnabled(__sortingEnabled)

        self.label.setText(_translate("MainWindow", "Parent folder:"))
        self.pushButton.setText(_translate("MainWindow", "OK"))
        self.label_2.setText(_translate("MainWindow", "File paths"))
        self.label_3.setText(_translate("MainWindow", "Tags with files"))
        self.label_4.setText(_translate("MainWindow", "Selected Tags"))
        self.label_5.setText(_translate("MainWindow", "Number of files:"))
        self.label_6.setText(_translate("MainWindow", "Number of tags:"))
        self.label_7.setText(_translate("MainWindow", "Number of tags:"))
        self.label_8.setText(_translate("MainWindow", "Number of selected tags:"))
        self.pushButton_2.setText(_translate("MainWindow", "Load Files"))
        self.pushButton_3.setText(_translate("MainWindow", "-->"))
        self.pushButton_4.setText(_translate("MainWindow", "<--"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "List"))
        self.label_9.setText(_translate("MainWindow", "Principal Table"))

        #tableau principal
        """ Légende des lignes"""
        numero = 0
        print(len(project._get_scans()))
        while numero < len(project._get_scans()):
            item = self.tableWidget.verticalHeaderItem(numero)
            i = str(numero+1)
            item.setText(_translate("MainWindow", i))
            numero += 1

        """ Légende des colonnes """
        """item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Path"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Nom"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Adresse"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)"""

        """remplissage de la première colonne avec les path de chaque scan"""
        """numero = 0
        for i in project._get_scans():
            a = str(i.file_path)
            item = QTableWidgetItem()
            item.setText(a)
            self.tableWidget.setItem(numero, 0, item)
            numero += 1"""


        """item = self.tableWidget.item(0, 1)
        item.setText(_translate("MainWindow", "b"))
        item = self.tableWidget.item(0, 2)
        item.setText(_translate("MainWindow", "c"))
        item = self.tableWidget.item(1, 1)
        item.setText(_translate("MainWindow", "e"))
        item = self.tableWidget.item(1, 2)
        item.setText(_translate("MainWindow", "f"))
        item = self.tableWidget.item(2, 1)
        item.setText(_translate("MainWindow", "h"))
        item = self.tableWidget.item(2, 2)
        item.setText(_translate("MainWindow", "i"))"""

        self.tableWidget.setSortingEnabled(__sortingEnabled)


        self.pushButton_5.setText(_translate("MainWindow", "Add tag"))
        self.pushButton_6.setText(_translate("MainWindow", "Show all"))
        self.label_10.setText(_translate("MainWindow", "Vizualisation:"))
        self.label_11.setText(_translate("MainWindow", "Countable table:"))
        item = self.tableWidget_2.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "ef"))
        item = self.tableWidget_2.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "ab"))
        item = self.tableWidget_2.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "cd"))
        item = self.tableWidget_2.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "total"))
        item = self.tableWidget_2.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "4"))
        item = self.tableWidget_2.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "1"))
        item = self.tableWidget_2.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "2"))
        item = self.tableWidget_2.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "3"))
        item = self.tableWidget_2.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "total"))
        __sortingEnabled = self.tableWidget_2.isSortingEnabled()
        self.tableWidget_2.setSortingEnabled(False)
        item = self.tableWidget_2.item(0, 0)
        item.setText(_translate("MainWindow", "0"))
        item = self.tableWidget_2.item(0, 1)
        item.setText(_translate("MainWindow", "0"))
        item = self.tableWidget_2.item(0, 2)
        item.setText(_translate("MainWindow", "1"))
        item = self.tableWidget_2.item(0, 3)
        item.setText(_translate("MainWindow", "2"))
        item = self.tableWidget_2.item(0, 4)
        item.setText(_translate("MainWindow", "3"))
        item = self.tableWidget_2.item(1, 0)
        item.setText(_translate("MainWindow", "0"))
        item = self.tableWidget_2.item(1, 1)
        item.setText(_translate("MainWindow", "4"))
        item = self.tableWidget_2.item(1, 2)
        item.setText(_translate("MainWindow", "0"))
        item = self.tableWidget_2.item(1, 3)
        item.setText(_translate("MainWindow", "0"))
        item = self.tableWidget_2.item(1, 4)
        item.setText(_translate("MainWindow", "4"))
        item = self.tableWidget_2.item(2, 0)
        item.setText(_translate("MainWindow", "3"))
        item = self.tableWidget_2.item(2, 1)
        item.setText(_translate("MainWindow", "1"))
        item = self.tableWidget_2.item(2, 2)
        item.setText(_translate("MainWindow", "6"))
        item = self.tableWidget_2.item(2, 3)
        item.setText(_translate("MainWindow", "0"))
        item = self.tableWidget_2.item(2, 4)
        item.setText(_translate("MainWindow", "10"))
        item = self.tableWidget_2.item(3, 0)
        item.setText(_translate("MainWindow", "3"))
        item = self.tableWidget_2.item(3, 1)
        item.setText(_translate("MainWindow", "5"))
        item = self.tableWidget_2.item(3, 2)
        item.setText(_translate("MainWindow", "7"))
        item = self.tableWidget_2.item(3, 3)
        item.setText(_translate("MainWindow", "2"))
        item = self.tableWidget_2.item(3, 4)
        item.setText(_translate("MainWindow", "17"))

        self.tableWidget_2.setSortingEnabled(__sortingEnabled)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Table"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "Process"))

    def logicielConversion(self):
        #ouvre le logiciel de conversion pour convertir les IRM en Nifti + Json
        import subprocess
        subprocess.call(['java', '-jar', 'MRIManagerFinal.jar', '[ExportNifti] C:\\Users\\omonti\\Desktop\\tmpNifti',
                         '[Info] Traitement IRMaGe'])

    def click_pushButton(self):
        # balance les items sélectionnés dans la liste des des items à afficher
        rows = sorted([index.row() for index in self.listWidget.selectedIndexes()],
                      reverse=True)
        for row in rows:
            # assuming the other listWidget is called listWidget_2
            self.listWidget_2.addItem(self.listWidget.takeItem(row))
        self.number_tag.setText(str(self.listWidget.count()))
        self.number_file_2.setText(str(self.listWidget_2.count()))

    def click_pushButton_return(self):
        # envoie les items sélectionnés dans la liste des items à ne pas afficher
        rows = sorted([index.row() for index in self.listWidget_2.selectedIndexes()],
                      reverse=True)
        for row in rows:
            # assuming the other listWidget is called listWidget_2
            self.listWidget.addItem(self.listWidget_2.takeItem(row))
        self.number_tag.setText(str(self.listWidget.count()))
        self.number_file_2.setText(str(self.listWidget_2.count()))

    def test(self):
        self.tabWidget.setCurrentIndex(1)
        self.column = self.listWidget_2.count()
        print('CCC ===', self.column)
        self.modify_ui.column = self.column
        return self.column



class Ui_Dialog(QDialog):

    signal_create_project = pyqtSignal()

    def __init__(self1):
        super().__init__()
        self1.pop_up()

    def pop_up(self1):
        self1.setObjectName("Dialog")
        self1.setStyleSheet("background-color: rgb(129, 173, 200);")
        self1.pushButton = QtWidgets.QPushButton(self1)
        self1.pushButton.setGeometry(QtCore.QRect(350, 260, 31, 20))
        self1.pushButton.setStyleSheet("color: rgb(6, 6, 6); background-color: rgb(221, 221, 221);")
        self1.pushButton.setObjectName("pushButton")

        self1.label = QtWidgets.QLabel(self1)
        self1.label.setGeometry(QtCore.QRect(50, 80, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self1.label.setFont(font)
        self1.label.setTextFormat(QtCore.Qt.AutoText)
        self1.label.setObjectName("label")
        self1.label_2 = QtWidgets.QLabel(self1)
        self1.label_2.setGeometry(QtCore.QRect(50, 170, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self1.label_2.setFont(font)
        self1.label_2.setTextFormat(QtCore.Qt.AutoText)
        self1.label_2.setObjectName("label_2")
        self1.label_3 = QtWidgets.QLabel(self1)
        self1.label_3.setGeometry(QtCore.QRect(50, 20, 350, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setWeight(75)
        self1.label_3.setStyleSheet("color: rgb(255, 0, 0);")
        self1.label_3.setFont(font)
        self1.label_3.setTextFormat(QtCore.Qt.AutoText)
        self1.label_3.setObjectName("label")
        self1.textEdit = QtWidgets.QTextEdit(self1)
        self1.textEdit.setGeometry(QtCore.QRect(160, 80, 151, 31))
        self1.textEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self1.textEdit.setObjectName("textEdit")

        self1.textEdit_2 = QtWidgets.QTextEdit(self1)
        self1.textEdit_2.setGeometry(QtCore.QRect(160, 170, 151, 31))
        self1.textEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self1.textEdit_2.setObjectName("textEdit_2")
        self1.pushButton_2 = QtWidgets.QPushButton(self1)
        self1.pushButton_2.setGeometry(QtCore.QRect(320, 180, 51, 20))
        font = QtGui.QFont()
        font.setItalic(True)
        self1.pushButton_2.setFont(font)
        self1.pushButton_2.setStyleSheet("background-color: rgb(163, 163, 163);")
        self1.pushButton_2.setObjectName("pushButton_2")
        self1.pushButton_2.clicked.connect(self1.SingleBrowse)
        _translate = QtCore.QCoreApplication.translate

        self1.setWindowTitle(_translate("Dialog", "Create project"))
        self1.pushButton.setText(_translate("Dialog", "OK"))
        self1.label.setText(_translate("Dialog", "Project name :"))
        self1.label_2.setText(_translate("Dialog", "Parent folder :"))
        self1.pushButton_2.setText(_translate("Dialog", "browse"))
        self1.pushButton.clicked.connect(self1.create_project)

    def SingleBrowse(self):
        parentFolder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Directory')
        self.parentFolder = parentFolder

    def create_project(self1):
        name = self1.textEdit.toPlainText()

        self1.name = name
        recorded_path = self1.textEdit_2.toPlainText()
        recorded_path = os.path.abspath(recorded_path)
        new_path = os.path.join(recorded_path, name)
        self1.new_path = new_path
        if not os.path.exists(new_path):
            controller.createProject(name, 'D :\data_nifti_json', recorded_path)
            self1.close()
            self1.signal_create_project.emit()
        else:
            _translate = QtCore.QCoreApplication.translate
            self1.label_3.setText(_translate("Dialog", "This name already exists in this parent folder"))


class Ui_Dialog_Open(QDialog):
    signal_create_project = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.pop_up()

    def pop_up(self):
        self.setObjectName("Dialog")
        self.setStyleSheet("background-color: rgb(129, 173, 200);")
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(350, 260, 31, 20))
        self.pushButton.setStyleSheet("color: rgb(6, 6, 6); background-color: rgb(221, 221, 221);")
        self.pushButton.setObjectName("pushButton")

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(50, 80, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(50, 170, 121, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setGeometry(QtCore.QRect(50, 20, 350, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setWeight(75)
        self.label_3.setStyleSheet("color: rgb(255, 0, 0);")
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.AutoText)
        self.label_3.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(160, 80, 151, 31))
        self.textEdit.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textEdit.setObjectName("textEdit")

        self.textEdit_2 = QtWidgets.QTextEdit(self)
        self.textEdit_2.setGeometry(QtCore.QRect(160, 170, 151, 31))
        self.textEdit_2.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.textEdit_2.setObjectName("textEdit_2")
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(320, 180, 51, 20))
        font = QtGui.QFont()
        font.setItalic(True)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("background-color: rgb(163, 163, 163);")
        self.pushButton_2.setObjectName("pushButton_2")
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Open project"))
        self.pushButton.setText(_translate("Dialog", "OK"))
        self.label.setText(_translate("Dialog", "Project name :"))
        self.label_2.setText(_translate("Dialog", "Parent folder :"))
        self.pushButton_2.setText(_translate("Dialog", "browse"))
        self.pushButton.clicked.connect(self.open_project)

    def open_project(self):
        name = self.textEdit.toPlainText()
        self.name = name
        #recorded_path = utils.findPath("controller")
        """recorded_path = self.textEdit_2.toPlainText()
        recorded_path = os.path.abspath(recorded_path)
        print(recorded_path)"""
        new_path = self.textEdit_2.toPlainText()
        new_path = os.path.abspath(new_path)
        self.new_path = new_path
        if os.path.exists(new_path):
            controller.open_project(name, new_path)

            self.close()

            self.signal_create_project.emit()
            print('AAA')
            print(new_path)


        else:
            _translate = QtCore.QCoreApplication.translate
            self.label_3.setText(_translate("Dialog", "This name doesn't exist in this parent folder"))


    def project_name(self):
        name = Ui_Dialog_Open.open_project(self)
        print('TESST =========', name)
        return name



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
