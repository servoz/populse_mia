#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from DataBase.DataBase import DataBase

if __name__ == '__main__':

    app = QApplication(sys.argv)

    database = DataBase(None, True)

    imageViewer = Main_Window(database)
    imageViewer.show()

    sys.exit(app.exec_())