#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from ProjectManager.models import *

if __name__ == '__main__':

    app = QApplication(sys.argv)

    project = Project("")
    imageViewer = Main_Window(project)
    imageViewer.show()

    sys.exit(app.exec_())