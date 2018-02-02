'''
Created on 20 déc. 2017

@author: omonti
'''
from PyQt5.QtWidgets import QMessageBox


class AboutSoft(QMessageBox):
    def __init__(self,parent=None):
        QMessageBox.__init__(self, parent)
        self.about(self, "About MRI Image Viewer",
                "<b>MRI Image Viewer</b> developped by :"
                "<br>IRMaGe - INSERM US17 "
                "<br>Bât. Edmond J. Safra "
                "<br>University Grenoble Alpes - Site Santé "
                "<br>BP170 "
				"<br>38042 GRENOBLE Cedex - France "
                ""
				"<p>olivier.montigon@univ-grenoble-alpes.fr</p>")