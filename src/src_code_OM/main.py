'''
Created on 11 janv. 2018

@author: omonti

'''
import subprocess

from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QTabWidget, QApplication, QVBoxLayout, \
    QMenuBar, QAction, qApp, QLineEdit, QMainWindow

from Config import Config
from DataBrowser.DataBrowser import DataBrowser   
from ImageViewer.ImageViewer import ImageViewer
from NodeEditor.PipeLine_Irmage import ProjectEditor  


class Project_Irmage(QMainWindow):
    def __init__(self):
        
        ############### Main Window ################################################################
        super(Project_Irmage,self).__init__()
        
        ############### initial setting ############################################################
        config=Config()
        self.currentRep = config.getPathData()
            
        ################ Create Menus ##############################################################
        project = self.menuBar().addMenu('File')
        project.addAction('Open Project')
        project.addAction('Save Project')
        project.addAction('Save Project as')
        project.addAction('Project Properties')
        project.addAction('MIA Preferences')
        
        importAct = QAction(QIcon('sources_images/Blue.png'),'Import Data',self)
        importAct.triggered.connect(self.impData)
        project.addAction(importAct)
       
        exitAct = QAction(QIcon('sources_images/exit.png'), 'Exit', self)
        exitAct.triggered.connect(qApp.quit)
        project.addAction(exitAct)
        
        mhelp = self.menuBar().addMenu('About')
        mhelp.addAction('Documentations')
        mhelp.addAction('Credits')
        
        ################ Create Tabs ###############################################################
        self.setCentralWidget(createTabs())
        
        ################ Window Main ###############################################################
        self.setWindowTitle("MRImage Viewer (IRMaGe)")
        self.resize(800,600)
        self.statusBar().showMessage('Ready')
    
    def impData(self):
        subprocess.call(['java','-Xmx4096M','-jar','MRIManagerJ8.jar','[ExportNifti]' + self.currentRep,'[ExportToMIA] PatientName-StudyName-CreationDate-SeqNumber-Protocol-SequenceName-AcquisitionTime'])
       
   
class createTabs(QWidget):
    def __init__(self):
        super(createTabs,self).__init__()

        self.config=Config()
        self.currentRep = self.config.getPathData()
               
        self.tabs = QTabWidget()
        self.tabs.setAutoFillBackground(False)
        self.tabs.setStyleSheet('QTabBar{font-size:14pt;font-family:Times;text-align: center;color:blue;}')
        self.tabs.setMovable(True)
        
        self.textInfo = QLineEdit(self)
        self.textInfo.resize(500,40)
        #self.textInfo.setEnabled(False)
        self.textInfo.setText('Welcome to Irmage')
                        
        self.tabs.addTab(DataBrowser(self.textInfo),"Data Browser")
        self.tabs.addTab(ProjectEditor(self.textInfo),"PipeLine Manager")
               
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.tabs)
        self.verticalLayout.addWidget(self.textInfo)
   
          
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    imageViewer = Project_Irmage()
    imageViewer.show()

    sys.exit(app.exec_())