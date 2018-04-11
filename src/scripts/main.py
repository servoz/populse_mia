#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
import os
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from Project.Project import Project
from SoftwareProperties.Config import Config

if __name__ == '__main__':
    # Working from the scripts directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    app = QApplication(sys.argv)

    # We make sure that FileName is in the default tags and in first position
    config = Config()
    tags = config.getDefaultTags()
    if not "FileName" in tags:
        tags.insert(0, "FileName")
    fileNameIndex = tags.index("FileName")
    if fileNameIndex != 0:
        tags[0], tags[fileNameIndex] = tags[fileNameIndex], tags[0]
    config.setDefaultTags(tags)

    project = Project(None, True)

    imageViewer = Main_Window(project)
    imageViewer.show()

    sys.exit(app.exec_())