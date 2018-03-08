#! /usr/bin/python3
# -*- coding: utf-8 -*- # Character encoding, recommended

import sys
import os
from PyQt5.QtWidgets import QApplication
from MainWindow.Main_Window import Main_Window
from DataBase.DataBase import DataBase



# Capsul import
from capsul.api import Process

# Trait import
from traits.api import Float

class Addition(Process):
    add_in_1 = Float(output=False)

    def __init__(self):
        super(Addition, self).__init__()
        self.add_trait("add_in_2", Float(output=False))
        self.add_trait("add_out", Float(output=True))

    def _run_process(self):
        self.add_out = self.add_in_1 + self.add_in_2
        print('Addition\n...\nInputs: {', self.add_in_1, ', ',
              self.add_in_2, '}\nOutput: ', self.add_out, '\n...\n')

class Substraction(Process):
    sub_in_1 = Float(output=False)

    def __init__(self):
        super(Substraction, self).__init__()
        self.add_trait("sub_in_2", Float(output=False))
        self.add_trait("sub_out", Float(output=True))

    def _run_process(self):
        self.sub_out = self.sub_in_1 - self.sub_in_2
        print('Substraction\n...\nInputs: {', self.sub_in_1, ', ',
              self.sub_in_2, '}\nOutput: ', self.sub_out, '\n...\n')

if __name__ == '__main__':
    # Working from the scripts directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    app = QApplication(sys.argv)

    database = DataBase(None, True)

    imageViewer = Main_Window(database)
    imageViewer.show()

    sys.exit(app.exec_())