##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

# PyQt5 imports
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class ClickableLabel(QLabel):
    """
    QLabel with a clicked signal

    Attributes:
        - clicked: signal to emit when the label is clicked

    Methods:
        - mousePressEvent: overrides the mousePressEvent method by emitting the clicked signal
    """

    # Signal that will be emitted when the widget is clicked
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        """
        Overrides the mousePressEvent method by emitting the clicked signal

        :param event: clicked event
        """
        self.clicked.emit()
