#!/usr/bin/python

import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QByteArray, Qt, QStringListModel, QLineF, QPointF, \
    QRectF, QSize
from PyQt5.QtGui import QStandardItemModel, QPixmap, QPainter, QPainterPath, \
    QCursor, QBrush, QStandardItem, QIcon
from PyQt5.QtWidgets import QMenuBar, QMenu, qApp, QGraphicsScene, QGraphicsView, \
    QTextEdit, QGraphicsLineItem, QGraphicsRectItem, QGraphicsTextItem, \
    QGraphicsEllipseItem, QDialog, QPushButton, QVBoxLayout, QListView, QWidget, \
    QSplitter, QApplication, QToolBar, QAction, QHBoxLayout
from matplotlib.backends.qt_compat import QtWidgets
import sip
import os
import six
from capsul.pipeline import pipeline_tools
from capsul.api import get_process_instance

from NodeEditor.callStudent import callStudent
from capsul.qt_gui.widgets import PipelineDevelopperView

if sys.version_info[0] >= 3:
    unicode = str
    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()



class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        QMenuBar.__init__(self, parent)
        
        self.menu1 = QMenu('File')
        mp11=self.menu1.addAction('Open Project')
        mp12=self.menu1.addAction('New Project')
        mp13=self.menu1.addAction('quit')
        mp11.triggered.connect(self.actionsMenu11)
        mp12.triggered.connect(self.actionsMenu12)
        mp13.triggered.connect(qApp.exit)
        self.addMenu(self.menu1)
        
        self.menu2 = QMenu('Project')
        mp21=self.menu2.addAction('Detail project')
        mp21.triggered.connect(self.actionsMenu21)
        self.addMenu(self.menu2)
        
        self.menu3 = QMenu('Run')
        mp31=self.menu3.addAction('Run project')
        mp32=self.menu3.addAction('stop project')
        mp31.triggered.connect(self.actionsMenu31)
        mp32.triggered.connect(self.actionsMenu32)
        self.addMenu(self.menu3)
    def actionsMenu11(self):
        print('Open Project')
    def actionsMenu12(self):
        print('New Project')
    def actionsMenu21(self):
        print('Detail project')
    def actionsMenu31(self):
        print('Run project')
    def actionsMenu32(self):
        print('stop project')

class ToolBar(QToolBar):
    def __init__(self, parent=None):
        QToolBar.__init__(self, parent)

        sep = QAction(self)
        sep.setSeparator(True)
       
        projAct = QAction(QIcon(os.path.join('..', 'sources_images', 'icons-403.png')),'Project',self)
        projAct.setShortcut('Ctrl+j')
        toolAct = QAction(QIcon(os.path.join('..', 'sources_images', 'Tool_Application.png')),'Tool',self)
        toolAct.setShortcut('Ctrl+t')
        protAct = QAction(QIcon(os.path.join('..', 'sources_images', 'Protocol_record.png')),'Protocol',self)
        protAct.setShortcut('Ctrl+p')
        creatAct = QAction(QIcon(os.path.join('..', 'sources_images', 'create.png')),'Create ROI',self)
        creatAct.setShortcut('Ctrl+r')
        openAct = QAction(QIcon(os.path.join('..', 'sources_images', 'open.png')) ,'Open ROI',self)
        openAct.setShortcut('Ctrl+o')
        plotAct = QAction(QIcon(os.path.join('..', 'sources_images', 'plot.png')),'Plotting',self)
        plotAct.setShortcut('Ctrl+g')
        prefAct = QAction(QIcon(os.path.join('..', 'sources_images', 'pref.png')),'Preferences',self)
        prefAct.setShortcut('Ctrl+h')

        self.setIconSize(QSize(50,50))
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.addActions((projAct,sep,toolAct,protAct,creatAct,openAct,plotAct,prefAct))
        self.actionTriggered[QAction].connect(self.btnPressed)
        
    def btnPressed(self,act):
        textInf.setText(act.text())


class LibraryModel(QStandardItemModel):
    def __init__(self, parent=None):
        QStandardItemModel.__init__(self, parent)
    def mimeTypes(self):
        return ['component/name']
    def mimeData(self, idxs):
        mimedata = QtCore.QMimeData()
        for idx in idxs:
            if idx.isValid():
                txt = self.data(idx, Qt.DisplayRole)
                mimedata.setData('component/name', QByteArray(txt.encode()))
        return mimedata

class LibItem(QPixmap):
    def __init__(self, parent=None):
        QPixmap.__init__(self, 110,100)
        self.fill()
        painter = QPainter(self)
        painter.setPen(Qt.yellow)
        painter.fillRect(5, 5, 100, 100, Qt.gray)
        painter.setBrush(Qt.red)
        painter.drawRect(90, 40, 20, 20)
        painter.setBrush(Qt.green)
        painter.drawRect(0, 40, 20, 20)
        painter.end()

class DiagramScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(DiagramScene, self).__init__(parent)
    def mouseMoveEvent(self, mouseEvent):
        editor.sceneMouseMoveEvent(mouseEvent)
        super(DiagramScene, self).mouseMoveEvent(mouseEvent)
    def mouseReleaseEvent(self, mouseEvent):
        editor.sceneMouseReleaseEvent(mouseEvent)
        super(DiagramScene, self).mouseReleaseEvent(mouseEvent)

"""class EditorGraphicsView(QGraphicsView): # ORIGINAL CLASS
    def __init__(self, scene, parent=None):
        QGraphicsView.__init__(self, scene, parent)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            event.accept()
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            event.accept()
            
    def dropEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            name = str(event.mimeData().data('component/name'))
            nIn = int(name[name.index('(')+1:name.index(',')])
            nOut= int(name[name.index(',')+1:name.index(')')])
            self.b1 = BlockItem(name, nIn , nOut)
            self.b1.setPos(self.mapToScene(event.pos()))
            self.scene().addItem(self.b1)"""


class EditorGraphicsView(PipelineDevelopperView):
    def __init__(self, scene, parent=None):
        PipelineDevelopperView.__init__(self, pipeline=None, allow_open_controller=True,
                                        show_sub_pipelines=True, enable_edition=True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            #name = str(event.mimeData().data('component/name'))
            #nIn = int(name[name.index('(')+1:name.index(',')])
            #nOut= int(name[name.index(',')+1:name.index(')')])
            #self.b1 = BlockItem(name, nIn , nOut)
            #self.b1.setPos(self.mapToScene(event.pos()))
            self.click_pos = QtGui.QCursor.pos()
            self.add_process()
            #self.scene().addItem(self.b1)


    #============================================================================
    # def mousePressEvent(self, event):
    #     print(event)      
    #============================================================================
class TextEditor(QTextEdit):
    def __init__(self,parent=None):
        super(TextEditor,self).__init__(parent)
        self.text=''
        def append(self, txt):
            txt.append(txt)
            txt._text+=str(txt) if isinstance(txt, QStringListModel) else txt
        def text(self):
            return self.document().toPlainText()

class Connection:
    def __init__(self, fromPort, toPort):
        self.fromPort = fromPort
        self.pos1 = None
        self.pos2 = None
        if fromPort:
            self.pos1 = fromPort.scenePos()
            fromPort.posCallbacks.append(self.setBeginPos)
        self.toPort = toPort
        # Create arrow item:
        self.arrow = ArrowItem()
        editor.diagramScene.addItem(self.arrow)
        #print(editor.diagramScene.items()[0])
    def setFromPort(self, fromPort):
        self.fromPort = fromPort
        if self.fromPort:
            self.pos1 = fromPort.scenePos()
            self.fromPort.posCallbacks.append(self.setBeginPos)
         
    def setToPort(self, toPort):
        self.toPort = toPort
        if self.toPort:
            self.pos2 = toPort.scenePos()
            self.toPort.posCallbacks.append(self.setEndPos)
    def setEndPos(self, endpos):
        self.pos2 = endpos
        self.arrow.setLine(QLineF(self.pos1, self.pos2))
    def setBeginPos(self, pos1):
        self.pos1 = pos1
        self.arrow.setLine(QLineF(self.pos1, self.pos2))
    def delete(self):
        editor.diagramScene.removeItem(self.arrow)


class ArrowItem(QGraphicsLineItem):
    def __init__(self, name='Untitled'):
        super(ArrowItem, self).__init__(None)
        self.setPen(QtGui.QPen(QtCore.Qt.blue,2))
        self.setFlag(self.ItemIsSelectable, True)
        self.setFlag(self.ItemIsFocusable, True)
  
    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Delete:
            editor.diagramScene.removeItem(self)
           
    def mousePressEvent(self, event):
        print()
      
class ArrowItem2(QPainter):
    def __init__(self, name='Untitled'):
        super(ArrowItem2,self).__init__(None)
        self.begin(self)
        self.setRenderHint(QPainter.Antialiasing)
        #self.drawBezierCurve(self)
        #self.end()
    def drawBezierCurve(self, qp):
        path = QPainterPath()
        path.moveTo(30, 30)
        path.cubicTo(30, 30, 200, 350, 350, 30)
        qp.drawPath(path)

class BlockItem(QGraphicsRectItem):
    def __init__(self, name='Untitled', *inout, parent=None):
        super(BlockItem, self).__init__(parent)
        self.name=name
        self.inout=inout
        self.editBlock()
      
    def editBlock(self):
        # Properties of the rectangle:
        w = 150.0
        h = 80.0
        self.setPen(QtGui.QPen(QtCore.Qt.yellow, 2))
        self.setBrush(QtGui.QBrush(QtCore.Qt.lightGray))
        self.setFlags(self.ItemIsSelectable | self.ItemIsMovable)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        # Label:
        self.label = QGraphicsTextItem(self.name, self)
        # Create corner for resize:
        self.sizer = HandleItem(self)
        self.sizer.setPos(w, h)
        self.sizer.posChangeCallbacks.append(self.changeSize) # Connect the callback
        #self.sizer.setVisible(False)
        self.sizer.setFlag(self.sizer.ItemIsSelectable, True)
        self.setFlag(self.ItemIsFocusable, True)
        # Inputs and outputs of the block:
        self.inputs = []
        for i in range (0,int(self.inout[0])):
            self.inputs.append( PortItem(i, Qt.red,5,'in',self) )
        self.outputs = []
        for i in range (0,int(self.inout[1])):
            self.outputs.append( PortItem(i, Qt.green,-40,'out',self) )
        self.changeSize(w, h)
   
    def editParameters(self):
       
        if len(tagEditor.children()) > 0 :
            self.clearLayout(tagEditor)

        cl = callStudent(self.name)
        tagEditor.setLayout(cl.getWidgets())
        #tagEditor.update()
     
    def clearLayout(self,layout):
        for i in reversed(range(len(layout.children()))):
            if type(layout.layout().itemAt(i))==QtWidgets.QWidgetItem:
                layout.layout().itemAt(i).widget().setParent(None)
            if type(layout.layout().itemAt(i))==QtWidgets.QHBoxLayout or type(layout.layout().itemAt(i))==QtWidgets.QVBoxLayout:
                layout.layout().itemAt(i).deleteLater()
                for j in reversed(range(len(layout.layout().itemAt(i)))):
                    layout.layout().itemAt(i).itemAt(j).widget().setParent(None)
        
        if layout.layout() is not None:
            sip.delete(layout.layout())
            #layout.layout().deleteLater()

    def contextMenuEvent(self, event):
        menu = QMenu()
        menu.addAction('Delete')
        pa = menu.addAction('Parameters')
        pa.triggered.connect(self.editParameters)
        menu.exec_(event.screenPos())
   
    def changeSize(self, w, h):
        # Limit the block size:
        if h < 80:
            h = 800
        if w < 150:
            w = 150
        self.setRect(0.0, 0.0, w, h)
        # center label:
        rect = self.label.boundingRect()
        lw, lh = rect.width(), rect.height()
        lx = (w - lw) / 2
        ly = (h - lh) / 2
        self.label.setPos(lx, ly)
        # Update port positions:
        if len(self.inputs) == 1:
            self.inputs[0].setPos(-4, h / 2)
        elif len(self.inputs) > 1:
            y = 5
            dy = (h - 10) / (len(self.inputs) - 1)
            for inp in self.inputs:
                inp.setPos(-4, y)
                y += dy
        if len(self.outputs) == 1:
            self.outputs[0].setPos(w+4, h / 2)
        elif len(self.outputs) > 1:
            y = 5
            dy = (h - 10) / (len(self.outputs) + 0)
            for outp in self.outputs:
                outp.setPos(w+4, y)
                y += dy
        return w, h
  
    def mousePressEvent(self, event):
        if event.button()==QtCore.Qt.LeftButton:
            textedit.append(self.name)
            self.editParameters()

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Delete:
            editor.diagramScene.removeItem(self)
 
class HandleItem(QGraphicsEllipseItem):
    """ A handle that can be moved by the mouse """
    def __init__(self, parent=None):
        super(HandleItem, self).__init__(QRectF(-4.0,-4.0,8.0,8.0), parent)
        self.posChangeCallbacks = []
        self.setBrush(QtGui.QBrush(Qt.white))
        self.setFlag(self.ItemIsMovable, True)
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        self.setCursor(QtGui.QCursor(Qt.SizeFDiagCursor))

    def itemChange(self, change, value):
        if change == self.ItemPositionChange:
            x, y = value.x(), value.y()
            # TODO: make this a signal?
            # This cannot be a signal because this is not a QObject
            for cb in self.posChangeCallbacks:
                res = cb(x, y)
                if res:
                    x, y = res
                    value = QPointF(x, y)
            return value
        # Call superclass method:
        return super(HandleItem, self).itemChange(change, value)

class PortItem(QGraphicsRectItem):
    def __init__(self, name, color , posn, nameItem,parent=None):
        QGraphicsRectItem.__init__(self, QRectF(-6,-6,10.0,10.0), parent)
        self.setCursor(QCursor(QtCore.Qt.CrossCursor))
        # Properties:
        self.setBrush(QBrush(color))
        # Name:
        self.name = name
        self.posCallbacks = []
        self.setFlag(self.ItemSendsScenePositionChanges, True)
        
        self.label = QGraphicsTextItem(nameItem+str(name),self)
        self.label.setPos(posn,-12)
   
    def itemChange(self, change, value):
        if change == self.ItemScenePositionHasChanged:
            for cb in self.posCallbacks:
                cb(value)
            return value
        return super(PortItem, self).itemChange(change, value)
  
    def mousePressEvent(self, event):
        editor.startConnection(self)

class ParameterDialog(QDialog):
    def __init__(self,title,parent=None):
        super(ParameterDialog, self).__init__(parent)
        self.title=title
        self.setWindowTitle(self.tr(self.title))
        self.button = QPushButton('Ok', self)
        l = QVBoxLayout(self)
        l.addWidget(self.button)
        self.button.clicked.connect(self.OK)
 
    def OK(self):
        self.close()
      
    def getWidget(self):
        return self.layout() 

class ProjectEditor(QWidget):
    def __init__(self,textInfo):
        global textedit, tagEditor, editor, textInf
        
        editor=self
        textInf=textInfo
        
        QWidget.__init__(self)
        self.setWindowTitle("Diagram editor")
        
        #menub = MenuBar(self)
        menub = ToolBar(self)
       
        self.verticalLayout = QVBoxLayout(self)
             
        self.libraryBrowserView = QListView(self)
        self.libraryModel = LibraryModel(self)
        self.libraryModel.setColumnCount(1)
    
        pxm = LibItem(self)
    
        self.libItems = []
        self.libItems.append( QStandardItem(QIcon(pxm), 'Source (0,2)') )
        self.libItems.append( QStandardItem(QIcon(pxm), 'Unit 1 (1,2)') )
        self.libItems.append( QStandardItem(QIcon(pxm), 'Unit 2 (3,3)') )
        self.libItems.append( QStandardItem(QIcon(pxm), 'Display (1,0)') )
        self.libItems.append( QStandardItem(QIcon(pxm), 'Student (3,2)') )
        self.libItems.append( QStandardItem(QIcon(pxm), 'Study (2,2)') )
    
        for i in self.libItems:
            self.libraryModel.appendRow(i)
        self.libraryBrowserView.setModel(self.libraryModel)
        self.libraryBrowserView.setViewMode(self.libraryBrowserView.IconMode)
        self.libraryBrowserView.setDragDropMode(self.libraryBrowserView.DragOnly)
    
        self.diagramScene = DiagramScene(self)
        self.diagramView = EditorGraphicsView(self.diagramScene, self)

        self.textedit = TextEditor(self)
        self.textedit.setStyleSheet("background-color : lightgray")
        redText = "<span style=\" font-size:12pt; font-weight:600; color:#ff0000;\" >"
        redText = redText + ("Code of the box")
        redText = redText + ("</span>")
        self.textedit.append(redText)
        
        tagEditor = QWidget(self)

        self.runButton = QPushButton('Run pipeline', self)
        self.runButton.clicked.connect(self.runPipeline)

        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(menub)
        self.hLayout.addWidget(self.runButton)
        self.hLayout.addStretch(1)
    
        self.splitter0 = QSplitter(Qt.Horizontal)
        self.splitter0.addWidget(self.diagramView)
        self.splitter0.addWidget(tagEditor)
        
        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.libraryBrowserView)
        self.splitter1.addWidget(self.diagramView)
        self.splitter1.addWidget(tagEditor)
        self.splitter1.setSizes([100,400,200])
    
        self.splitter2 = QSplitter(Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.textedit)
        self.splitter2.setSizes([400,200])
           
        self.verticalLayout.addLayout(self.hLayout)
        self.verticalLayout.addWidget(self.splitter2)
    
        self.startedConnection = None

    def runPipeline(self):
        '''# Saving the pipeline
        pipeline = self.diagramView.scene.pipeline
        filename = '/tmp/pipeline.py'
        posdict = dict([(key, (value.x(), value.y())) \
                        for key, value in six.iteritems(self.scene.pos)])
        old_pos = pipeline.node_position
        pipeline.node_position = posdict
        pipeline_tools.save_pipeline(pipeline, filename)
        self._pipeline_filename = unicode(filename)
        pipeline.node_position = old_pos'''

        pipeline = get_process_instance(self.diagramView.scene.pipeline)
        with open('/tmp/tmp_pipeline.txt', 'w') as f:
            sys.stdout = f
            f.write('Pipeline execution\n...\n\n')
            pipeline()

        with open('/tmp/tmp_pipeline.txt', 'r') as f:
            self.textedit.setText(f.read())

    def startConnection(self, port):
        self.startedConnection = Connection(port, None)
     
    def sceneMouseMoveEvent(self, event):
        if self.startedConnection:
            pos = event.scenePos()
            self.startedConnection.setEndPos(pos)
     
    def sceneMouseReleaseEvent(self, event):
        # Clear the actual connection:
        if self.startedConnection:
            pos = event.scenePos()
            items = self.diagramScene.items(pos)
            for item in items:
                if type(item) is PortItem:
                    self.startedConnection.setToPort(item)
            if self.startedConnection.toPort == None:
                self.startedConnection.delete()
            self.startedConnection = None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    global editor
    editor = ProjectEditor()
    editor.show()
    editor.resize(700, 800)
    app.exec_()