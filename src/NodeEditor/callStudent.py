from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog, QLabel, QLineEdit, \
    QPushButton

from NodeEditor.get_set_Value import get_set_Value


class callStudent(QDialog):
    def __init__(self,nameBlock,parent=None):
        super(callStudent, self).__init__(parent)

        nIn=int(nameBlock[nameBlock.index('(')+1:nameBlock.index(',')])
        #nOut=int(nameBlock[nameBlock.index(',')+1:nameBlock.index(')')])

        self.vbox = QVBoxLayout(self)

        hbox = QHBoxLayout(self)
        label=QLabel("Block Name : ")
        hbox.addWidget(label)
        label=QLineEdit(nameBlock)
        label.setDisabled(True)
        label.setAlignment(QtCore.Qt.AlignCenter)
        hbox.addWidget(label)
        self.vbox.addLayout(hbox)

        self.zoneline=[]
        for i in range(nIn):
            hbox=QHBoxLayout(self)
            label=QLabel('in'+str(i))
            self.zoneline.append(QLineEdit())
            hbox.addWidget(label)
            hbox.addWidget(self.zoneline[i])
            self.vbox.addLayout(hbox)

        button = QPushButton('Ok', self)
        self.vbox.addWidget(button)

        button.clicked.connect(self.OK)

    def OK(self):
        fr = get_set_Value()
        fr.setVar(self.zoneline[0].text(), self.zoneline[1].text() ,self.zoneline[2].text())
        fr.main()
        print(fr.getResult().affich())
        print(fr.getResult().agegroup())
        self.close()

    def getWidgets(self):
        return self.layout()


#===============================================================================
# if __name__ == '__main__':
#     print("callStudent")
#     dc = callStudent()
#     dc.exec_()
#===============================================================================


