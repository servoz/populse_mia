#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window

if __name__ == '__main__':

    app = QApplication(sys.argv)

    imageViewer = Main_Window()
    imageViewer.show()

    sys.exit(app.exec_())