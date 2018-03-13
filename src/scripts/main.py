#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
import os
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from DataBase.DataBase import DataBase
from NodeEditor.Processes.processes import *
from SoftwareProperties.Config import Config

if __name__ == '__main__':
    # Working from the scripts directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    app = QApplication(sys.argv)

    # We make sure that FileName is in the default tags
    config = Config()
    tags = config.getDefaultTags()
    if not "FileName" in config.getDefaultTags():
        tags.insert(0, "FileName")
        config.setDefaultTags(tags)

    database = DataBase(None, True)

    imageViewer = Main_Window(database)
    imageViewer.show()

    sys.exit(app.exec_())