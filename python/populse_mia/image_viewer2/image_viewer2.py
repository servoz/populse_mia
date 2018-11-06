##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QToolBar, QWidget, QVBoxLayout, \
    QTableWidget, QListWidget, QListWidgetItem


class ImageViewer2(QWidget):
    def __init__(self,textBox):
        super(ImageViewer2, self).__init__()
        
        self.textBox = textBox
        sep = QAction(self)
        sep.setSeparator(True)
       
        projAct = QAction(QIcon('images/icons-403.png'),'project',self)
        projAct.setShortcut('Ctrl+j')
        toolAct = QAction(QIcon('images/Tool_Application.png'),'Tool',self)
        toolAct.setShortcut('Ctrl+t')
        protAct = QAction(QIcon('images/Protocol_record.png'),'Protocol',self)
        protAct.setShortcut('Ctrl+p')
        creatAct = QAction(QIcon('images/create.png'),'Create ROI',self)
        creatAct.setShortcut('Ctrl+r')
        openAct = QAction(QIcon('images/open.png'),'Open ROI',self)
        openAct.setShortcut('Ctrl+o')
        plotAct = QAction(QIcon('images/plot.png'),'Plotting',self)
        plotAct.setShortcut('Ctrl+g')
        prefAct = QAction(QIcon('images/pref.png'),'Preferences',self)
        prefAct.setShortcut('Ctrl+h')
       
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(50,50))
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        toolbar.addActions((projAct,sep,toolAct,protAct,creatAct,openAct,plotAct,prefAct))
        toolbar.actionTriggered[QAction].connect(self.btnPressed)
        
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(toolbar)

        
    def btnPressed(self,act):
        self.textBox.setText(act.text())
