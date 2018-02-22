#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from ProjectManager.models import *
from DataBase.DataBase import DataBase
from DataBase.DataBaseModel import createDatabase
import os

if __name__ == '__main__':

    app = QApplication(sys.argv)

    project = Project("")
    database = DataBase(None)
    project.folder = database.folder # TODO To remove once the Project class is useless

    imageViewer = Main_Window(project, database)
    imageViewer.show()

    sys.exit(app.exec_())