#!/usr/bin/python3

import sys
import sip
import os

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QByteArray, Qt, QStringListModel, QLineF, QPointF, \
    QRectF, QSize
from PyQt5.QtGui import QStandardItemModel, QPixmap, QPainter, QPainterPath, \
    QCursor, QBrush, QIcon
from PyQt5.QtWidgets import QMenuBar, QMenu, qApp, QGraphicsScene, \
    QTextEdit, QGraphicsLineItem, QGraphicsRectItem, QGraphicsTextItem, \
    QGraphicsEllipseItem, QDialog, QPushButton, QVBoxLayout, QWidget, \
    QSplitter, QApplication, QToolBar, QAction, QHBoxLayout, QScrollArea
from matplotlib.backends.qt_compat import QtWidgets
from traits.trait_errors import TraitError

from traits.api import TraitListObject
from capsul.api import get_process_instance, StudyConfig
from .process_library import ProcessLibraryWidget

from PipelineManager.callStudent import callStudent
from .NodeController import NodeController
from .PipelineEditor import PipelineEditor

if sys.version_info[0] >= 3:
    unicode = str

    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()


class PipelineManagerTab(QWidget):
    def __init__(self, project, scan_list):
        global textedit, tagEditor, editor

        editor = self
        self.project = project
        self.scan_list = scan_list

        QWidget.__init__(self)
        self.setWindowTitle("Diagram editor")

        menub = ToolBar(self)

        self.verticalLayout = QVBoxLayout(self)

        self.processLibrary = ProcessLibraryWidget()

        self.diagramScene = DiagramScene(self)
        self.diagramView = PipelineEditor(self.project)
        self.diagramView.node_clicked.connect(self.displayNodeParameters)

        self.textedit = TextEditor(self)
        self.textedit.setStyleSheet("background-color : lightgray")

        self.nodeController = NodeController(self.project, self.scan_list)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.nodeController)

        self.loadButton = QPushButton('Load pipeline', self)
        self.loadButton.clicked.connect(self.loadPipeline)

        self.saveButton = QPushButton('Save pipeline', self)
        self.saveButton.clicked.connect(self.savePipeline)

        self.initButton = QPushButton('Initialize pipeline', self)
        self.initButton.clicked.connect(self.initPipeline)

        self.runButton = QPushButton('Run pipeline', self)
        self.runButton.clicked.connect(self.runPipeline)

        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(menub)
        self.hLayout.addWidget(self.saveButton)
        self.hLayout.addWidget(self.loadButton)
        self.hLayout.addWidget(self.initButton)
        self.hLayout.addWidget(self.runButton)
        self.hLayout.addStretch(1)

        self.splitter0 = QSplitter(Qt.Horizontal)
        self.splitter0.addWidget(self.diagramView)
        self.splitter0.addWidget(self.scrollArea)

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.processLibrary)
        self.splitter1.addWidget(self.diagramView)
        self.splitter1.addWidget(self.scrollArea)
        self.splitter1.setSizes([100, 400, 200])

        self.splitter2 = QSplitter(Qt.Vertical)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.addWidget(self.textedit)
        self.splitter2.setSizes([800, 100])

        self.verticalLayout.addLayout(self.hLayout)
        self.verticalLayout.addWidget(self.splitter2)

        self.startedConnection = None

        # To undo/redo
        self.nodeController.value_changed.connect(self.controller_value_changed)

    def undo(self):
        #TODO: it is not totally finished
        # We can undo if we have an action to revert
        if len(self.diagramView.undos) > 0:
            to_undo = self.diagramView.undos.pop()
            # The first element of the list is the type of action made by the user
            action = to_undo[0]

            if action == "add_process":
                node_name = to_undo[1]
                self.diagramView.del_node(node_name, from_undo=True)

            elif action == "delete_process":
                node_name = to_undo[1]
                class_name = to_undo[2]
                links = to_undo[3]
                self.diagramView.add_process(class_name, node_name, from_undo=True, links=links)

            elif action == "export_plugs":
                pass

            elif action == "update_node_name":
                node = to_undo[1]
                new_node_name = to_undo[2]
                old_node_name = to_undo[3]
                self.diagramView.update_node_name(node, new_node_name, old_node_name, from_undo=True)

            elif action == "update_plug_value":
                node_name = to_undo[1]
                old_value = to_undo[2]
                plug_name = to_undo[3]
                value_type = to_undo[4]
                self.diagramView.update_plug_value(node_name, old_value, plug_name, value_type, from_undo=True)

            elif action == "add_link":
                link = to_undo[1]
                self.diagramView._del_link(link, from_undo=True)

            elif action == "delete_link":
                source = to_undo[1]
                dest = to_undo[2]
                active = to_undo[3]
                weak = to_undo[4]
                self.diagramView.add_link(source, dest, active, weak, from_undo=True)
            # TODO: ADD "MOVE PROCESS ?"

            self.diagramView.scene.pipeline.update_nodes_and_plugs_activation()
        print("REDOS IN UNDO")
        print(self.diagramView.redos)
        print("UNDOS IN UNDO")
        print(self.diagramView.undos)

    def redo(self):
        print("REDO IN REDO")
        print(self.diagramView.redos)
        print("UNDO IN REDO")
        print(self.diagramView.undos)

        # We can redo if we have an action to make again
        if len(self.diagramView.redos) > 0:
            to_redo = self.diagramView.redos.pop()
            # The first element of the list is the type of action made by the user
            action = to_redo[0]

            if action == "delete_process":
                node_name = to_redo[1]
                class_process = to_redo[2]
                links = to_redo[3]
                self.diagramView.add_process(class_process, node_name, from_redo=True, links=links)

            elif action == "add_process":
                node_name = to_redo[1]
                self.diagramView.del_node(node_name, from_redo=True)

            elif action == "export_plugs":
                pass

            elif action == "update_node_name":
                node = to_redo[1]
                new_node_name = to_redo[2]
                old_node_name = to_redo[3]
                self.diagramView.update_node_name(node, new_node_name, old_node_name, from_redo=True)

            elif action == "update_plug_value":
                node_name = to_redo[1]
                new_value = to_redo[2]
                plug_name = to_redo[3]
                value_type = to_redo[4]
                self.diagramView.update_plug_value(node_name, new_value, plug_name, value_type, from_redo=True)

            elif action == "add_link":
                link = to_redo[1]
                self.diagramView._del_link(link, from_redo=True)

            elif action == "delete_link":
                source = to_redo[1]
                dest = to_redo[2]
                active = to_redo[3]
                weak = to_redo[4]
                self.diagramView.add_link(source, dest, active, weak, from_redo=True)

            self.diagramView.scene.pipeline.update_nodes_and_plugs_activation()
            # TODO: ADD "MOVE NODE ?"

    def update_project(self, project):
        self.project = project
        self.nodeController.project = project
        self.diagramView.project = project

    def controller_value_changed(self, signal_list):
        case = signal_list.pop(0)

        # For history
        history_maker = []

        if case == "node_name":
            history_maker.append("update_node_name")
            for element in signal_list:
                history_maker.append(element)

        elif case == "plug_value":
            history_maker.append("update_plug_value")
            for element in signal_list:
                history_maker.append(element)

        self.diagramView.undos.append(history_maker)
        self.diagramView.redos.clear()

    def loadPipeline(self):
        self.diagramView.load_pipeline()

    def savePipeline(self):
        self.diagramView.save_pipeline()

    def initPipeline(self):
        """ Method that generates the output names of each pipeline node. """

        def add_plug_value_to_database(p_value):
            """
            Adds the plug value to the database.
            :param p_value: plug value, a file name or a list of file names
            :return:
            """
            if type(p_value) in [list, TraitListObject]:
                for elt in p_value:
                    add_plug_value_to_database(elt)
                return

            try:
                open(p_value, 'a').close()
            except IOError:
                raise IOError('Could not open {0} file.'.format(p_value))
            else:
                # Deleting the project's folder in the file name so it can
                # fit to the database's syntax
                p_value = p_value.replace(self.project.folder, "")
                if p_value[0] in ["\\", "/"]:
                    p_value = p_value[1:]

                # If the file name is already in the database, no exception is raised
                # but the user is warned
                if self.project.database.get_document(p_value):
                    print("Path {0} already in database.".format(p_value))
                else:
                    self.project.database.add_document(p_value)

        pipeline_scene = self.diagramView.scene

        # nodes_to_check contains the node names that need to be update
        nodes_to_check = []

        # This list is initialized with all node names
        for node_name in pipeline_scene.gnodes.keys():
            nodes_to_check.append(node_name)

        while nodes_to_check:
            # Verifying if any element of nodes_to_check is unique
            nodes_to_check = list(set(nodes_to_check))

            node_name = nodes_to_check.pop()

            # Inputs/Outputs nodes will be automatically updated with
            # the method update_nodes_and_plugs_activation of the pipeline object
            if node_name in ['', 'inputs', 'outputs']:
                continue

            gnode = pipeline_scene.gnodes[node_name]
            process = gnode.process

            # Getting the list of the outputs of the node according to its inputs
            try:
                process_outputs = process.list_outputs()
            except TraitError:
                print("TRAIT ERROR for node {0}".format(node_name))
                # The node should be checked again but it can lead to an
                # infinite loop, so this line is commented until a better
                # solution is found.
                # nodes_to_check.insert(0, node_name)
                continue

            if process_outputs:
                for plug_name, plug_value in process_outputs.items():
                    node = pipeline_scene.pipeline.nodes[node_name]
                    if plug_name not in node.plugs.keys():
                        continue
                    """if type(plug_value) in [list, TraitListObject]:
                        for element in plug_value:
                            add_plug_value_to_database(element)
                    else:"""
                    add_plug_value_to_database(plug_value)

                    list_info_link = list(node.plugs[plug_name].links_to)

                    # If the output is connected to another node,
                    # the latter is added to nodes_to_check
                    for info_link in list_info_link:
                        dest_node_name = info_link[0]
                        nodes_to_check.append(dest_node_name)

                    if plug_name == "native_class_images":
                        print("NATIVE CLASS IMAGE VALUE: ", plug_value)

                    try:
                        pipeline_scene.pipeline.nodes[node_name].set_plug_value(plug_name, plug_value)
                    except TraitError:
                        if type(plug_value) is list and len(plug_value) == 1:
                            try:
                                pipeline_scene.pipeline.nodes[node_name].set_plug_value(plug_name, plug_value[0])
                            except TraitError:
                                pass

                    pipeline_scene.pipeline.update_nodes_and_plugs_activation()

    def runPipeline(self):
        pipeline = get_process_instance(self.diagramView.scene.pipeline)
        # Now
        study_config = StudyConfig(modules=StudyConfig.default_modules + ['NipypeConfig', 'SPMConfig', 'FSLConfig'])

        # Modifying the study_config to use SPM 12 Standalone
        setattr(study_config, 'spm_exec', '/home/david/spm12/run_spm12.sh')
        setattr(study_config, 'spm_standalone', True)
        setattr(study_config, 'spm_directory', '/home/david/spm12')
        setattr(study_config, 'use_spm', True)
        setattr(study_config, 'spm_version', '12')
        setattr(study_config, 'output_directory', '/home/david/spm12/spm12_mcr/spm/spm12/')

        # inspect config options
        for k in study_config.user_traits().keys(): print(k, ':  ', getattr(study_config, k))

        """with open('/tmp/tmp_pipeline.txt', 'w') as f:
            sys.stdout = f
            f.write('Pipeline execution\n...\n\n')
            # Before
            #pipeline()

            study_config.reset_process_counter()
            study_config.run(pipeline, verbose=1)

        with open('/tmp/tmp_pipeline.txt', 'r') as f:
            self.textedit.setText(f.read())"""

        study_config.reset_process_counter()
        study_config.run(pipeline, verbose=1)


    def displayNodeParameters(self, node_name, process):
        self.nodeController.display_parameters(node_name, process, self.diagramView.scene.pipeline)
        self.scrollArea.setWidget(self.nodeController)

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
            if self.startedConnection.toPort is None:
                self.startedConnection.delete()
            self.startedConnection = None


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
        #self.actionTriggered[QAction].connect(self.btnPressed)


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
        if event.key() == QtCore.Qt.Key_Delete:
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
            if type(layout.layout().itemAt(i)) == QtWidgets.QWidgetItem:
                layout.layout().itemAt(i).widget().setParent(None)
            if type(layout.layout().itemAt(i)) == QtWidgets.QHBoxLayout \
                    or type(layout.layout().itemAt(i)) == QtWidgets.QVBoxLayout:
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
        if event.button() == QtCore.Qt.LeftButton:
            textedit.append(self.name)
            self.editParameters()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    global editor
    editor = PipelineManagerTab()
    editor.show()
    editor.resize(700, 800)
    app.exec_()
