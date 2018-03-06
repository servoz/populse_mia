#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
import os
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from DataBase.DataBase import DataBase

if __name__ == '__main__':
    # Working from the scripts directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    app = QApplication(sys.argv)

    database = DataBase(None, True)

    imageViewer = Main_Window(database)
    imageViewer.show()

    sys.exit(app.exec_())