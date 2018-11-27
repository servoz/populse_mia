##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import datetime
import os
import sys
import uuid
import six
from time import sleep
from collections import OrderedDict

from PyQt5 import QtCore
from matplotlib.backends.qt_compat import QtWidgets
from traits.trait_errors import TraitError
from traits.api import TraitListObject, Undefined

from nipype.interfaces.base import traits    ### Test for matlab launch

# PyQt5 imports
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF
from PyQt5.QtWidgets import QMenu, QVBoxLayout, QWidget, \
    QSplitter, QApplication, QToolBar, QAction, QHBoxLayout, QScrollArea, QMessageBox, QProgressDialog, QGraphicsScene, \
    QGraphicsView

# Capsul imports
from capsul.api import get_process_instance, StudyConfig, PipelineNode, Switch, NipypeProcess, Pipeline

# Populse_MIA imports
from populse_mia.pipeline_manager.process_mia import ProcessMIA
from populse_mia.pop_ups.pop_up_select_iteration import PopUpSelectIteration
from populse_mia.pipeline_manager.iteration_table import IterationTable
from populse_mia.pipeline_manager.capsul_files.pipeline_developper_view import PipelineDevelopperView
from populse_mia.project.project import COLLECTION_CURRENT, COLLECTION_INITIAL, COLLECTION_BRICK, BRICK_NAME, \
    BRICK_OUTPUTS, BRICK_INPUTS, TAG_BRICKS, BRICK_INIT, BRICK_INIT_TIME, TAG_TYPE, TAG_EXP_TYPE, TAG_FILENAME, \
    TAG_CHECKSUM, TYPE_NII, TYPE_MAT
from populse_mia.pipeline_manager.node_controller import NodeController
from populse_mia.pipeline_manager.pipeline_editor import PipelineEditorTabs
from populse_mia.pipeline_manager.process_library import ProcessLibraryWidget
from populse_mia.software_properties.config import Config

if sys.version_info[0] >= 3:
    unicode = str

    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()


class PipelineManagerTab(QWidget):
    """
    Widget that handles the Pipeline Manager tab.

    Attributes:
        - processLibrary: library of processes to drag & drop to a pipeline editor
        - pipelineEditorTabs: graphical pipeline editor composed of several tabs
        - nodeController: controller that displays parameters when a node is clicked
        - iterationTable: widgets that handles pipeline iteration
        - project: current project in the software
        - scan_list: list of the selected database files
        - iteration_table_scans_list: list of the scans contained in the iteration table
        - main_window: main window of the software

    Methods:
        - undo: undo the last action made on the current pipeline editor
        - redo: redo the last undone action on the current pipeline editor
        - update_clinical_mode: updates the visibility of widgets/actions depending of the chosen mode
        - update_scans_list: updates the user-selected list of scans
        - update_project: updates the project attribute of several objects
        - controller_value_changed: updates history when a pipeline node is changed
        - updateProcessLibrary: updates the library of processes when a pipeline is saved
        - loadPipeline: loads a pipeline to the pipeline editor
        - savePipeline: saves the current pipeline of the pipeline editor
        - savePipelineAs: saves the current pipeline of the pipeline editor under another name
        - loadParameters: loads pipeline parameters to the current pipeline of the pipeline editor
        - saveParameters: save the pipeline parameters of the the current pipeline of the pipeline editor
        - initPipeline: initializes the current pipeline of the pipeline editor
        - init_pipeline: initializes the current pipeline of the pipeline editor (without progress bar)
        - runPipeline: runs the current pipeline of the pipeline editor
        - displayNodeParameters: displays the node controller when a node is clicked
    """

    item_library_clicked = QtCore.Signal(str)

    def __init__(self, project, scan_list, main_window):
        """
        Initialization of the Pipeline Manager tab

        :param project: current project in the software
        :param scan_list: list of the selected database files
        :param main_window: main window of the software
        """

        config = Config()
        ProcessMIA.project = project
        self.project = project
        if not scan_list:
            self.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)
        else:
            self.scan_list = scan_list
        self.main_window = main_window
        self.disable_progress_bar = False

        # This list is the list of scans contained in the iteration table
        # If it is empty, the scan list in the Pipeline Manager is the scan list from the data_browser
        self.iteration_table_scans_list = []

        QWidget.__init__(self)
        self.setWindowTitle("Diagram editor")

        self.verticalLayout = QVBoxLayout(self)

        self.processLibrary = ProcessLibraryWidget(self.main_window)

        self.processLibrary.process_library.item_library_clicked.connect(self.item_library_clicked)
        self.item_library_clicked.connect(self._show_preview)

        # self.diagramScene = DiagramScene(self)
        self.pipelineEditorTabs = PipelineEditorTabs(self.project, self.scan_list, self.main_window)
        self.pipelineEditorTabs.node_clicked.connect(self.displayNodeParameters)
        self.pipelineEditorTabs.switch_clicked.connect(self.displayNodeParameters)
        self.pipelineEditorTabs.pipeline_saved.connect(self.updateProcessLibrary)

        self.nodeController = NodeController(self.project, self.scan_list, self, self.main_window)
        self.nodeController.visibles_tags = self.project.session.get_visibles()

        self.iterationTable = IterationTable(self.project, self.scan_list, self.main_window)
        self.iterationTable.iteration_table_updated.connect(self.update_scans_list)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.nodeController)

        # Actions
        self.load_pipeline_action = QAction("Load pipeline", self)
        self.load_pipeline_action.triggered.connect(self.loadPipeline)

        self.save_pipeline_action = QAction("Save pipeline", self)
        self.save_pipeline_action.triggered.connect(self.savePipeline)

        self.save_pipeline_as_action = QAction("Save pipeline as", self)
        self.save_pipeline_as_action.triggered.connect(self.savePipelineAs)

        self.load_pipeline_parameters_action = QAction("Load pipeline parameters", self)
        self.load_pipeline_parameters_action.triggered.connect(self.loadParameters)

        self.save_pipeline_parameters_action = QAction("Save pipeline parameters", self)
        self.save_pipeline_parameters_action.triggered.connect(self.saveParameters)

        self.init_pipeline_action = QAction("Initialize pipeline", self)
        self.init_pipeline_action.triggered.connect(self.initPipeline)

        self.run_pipeline_action = QAction("Run pipeline", self)
        self.run_pipeline_action.triggered.connect(self.runPipeline)

        # Toolbar
        self.menu_toolbar = QToolBar()

        self.tags_menu = QMenu()
        self.tags_menu.addAction(self.load_pipeline_action)
        self.tags_menu.addAction(self.save_pipeline_action)
        self.tags_menu.addAction(self.save_pipeline_as_action)
        self.tags_menu.addSeparator()
        self.tags_menu.addAction(self.load_pipeline_parameters_action)
        self.tags_menu.addAction(self.save_pipeline_parameters_action)
        self.tags_menu.addSeparator()
        self.tags_menu.addAction(self.init_pipeline_action)
        self.tags_menu.addAction(self.run_pipeline_action)

        if config.get_clinical_mode() == 'yes':
            self.save_pipeline_action.setDisabled(True)
            self.save_pipeline_as_action.setDisabled(True)

        self.tags_tool_button = QtWidgets.QToolButton()
        self.tags_tool_button.setText('Pipeline')
        self.tags_tool_button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.tags_tool_button.setMenu(self.tags_menu)

        # Layouts
        self.hLayout = QHBoxLayout()
        self.hLayout.addWidget(self.tags_tool_button)
        self.hLayout.addStretch(1)

        self.splitterRight = QSplitter(Qt.Vertical)
        self.splitterRight.addWidget(self.iterationTable)
        self.splitterRight.addWidget(self.scrollArea)
        self.splitterRight.setSizes([400, 400])

        # previewScene = QGraphicsScene()
        # previewScene.setSceneRect(QtCore.QRectF())
        # self.previewDiagram = QGraphicsView()
        # self.previewDiagram.setEnabled(False)

        self.previewBlock = PipelineDevelopperView(pipeline=None, allow_open_controller=False,
                                                   show_sub_pipelines=True, enable_edition=False)

        self.splitter0 = QSplitter(Qt.Vertical)
        self.splitter0.addWidget(self.processLibrary)
        self.splitter0.addWidget(self.previewBlock)

        self.splitter1 = QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(self.splitter0)
        self.splitter1.addWidget(self.pipelineEditorTabs)
        self.splitter1.addWidget(self.splitterRight)
        self.splitter1.setSizes([200, 800, 200])

        if config.get_clinical_mode() == 'yes':
            self.processLibrary.setHidden(True)
            self.previewBlock.setHidden(True)

        # self.splitter2 = QSplitter(Qt.Vertical)
        # self.splitter2.addWidget(self.splitter1)
        # self.splitter2.setSizes([800, 100])

        self.verticalLayout.addLayout(self.hLayout)
        self.verticalLayout.addWidget(self.splitter1)

        self.startedConnection = None

        # To undo/redo
        self.nodeController.value_changed.connect(self.controller_value_changed)

    def _show_preview(self, name_item):
        for elem in self.previewBlock.scene.items():
            self.previewBlock.scene.removeItem(elem)
        self.previewBlock.centerOn(0, 0)
        self.find_process(name_item)

    def find_process(self, path):
        """
        Finds the dropped process in the system's paths

        :param path: class's path (e.g. "nipype.interfaces.spm.Smooth") (str)
        """
        package_name, process_name = os.path.splitext(path)
        process_name = process_name[1:]
        __import__(package_name)
        pkg = sys.modules[package_name]
        for name, instance in sorted(list(pkg.__dict__.items())):
            if name == process_name:
                try:
                    process = get_process_instance(instance)
                except Exception as e:
                    print(e)
                    return
                else:
                    node, node_name = self.add_process_to_preview(instance)
                    gnode = self.previewBlock.scene.add_node(node_name, node)
                    gnode.setPos(0,0)
                    gnode.updateInfoActived(True)
                    # gnode.active = True
                    # gnode.update_node()
                    rect=gnode.sceneBoundingRect()
                    self.previewBlock.scene.setSceneRect(rect)
                    self.previewBlock.fitInView(rect.x(), rect.y(), rect.width() * 1.2,
                                                rect.height() * 1.2, Qt.KeepAspectRatio)
                    self.previewBlock.setAlignment(Qt.AlignCenter)

    def add_process_to_preview(self, class_process, node_name=None):
        """
        Adds a process to the pipeline

        :param class_process: process class's name (str)
        :param node_name: name of the corresponding node (using when undo/redo) (str)
        """
        pipeline = self.previewBlock.scene.pipeline
        if not node_name:
            class_name = class_process.__name__
            i = 1

            node_name = class_name.lower() + str(i)

            while node_name in pipeline.nodes and i < 100:
                i += 1
                node_name = class_name.lower() + str(i)

            process_to_use = class_process()

        else:
            process_to_use = class_process

        try:
            process = get_process_instance(
                process_to_use)
        except Exception as e:
            print(e)
            return

        pipeline.add_process(node_name, process)

        # Capsul update
        node = pipeline.nodes[node_name]
        # gnode = self.scene.add_node(node_name, node)

        return node, node_name

    def undo(self):
        """
        Undo the last action made on the current pipeline editor

        Actions that can be undone:
            - add_process
            - delete_process
            - export_plug
            - export_plugs
            - remove_plug
            - update_node_name
            - update_plug_value
            - add_link
            - delete_link

        """
        c_e = self.pipelineEditorTabs.get_current_editor()

        # We can undo if we have an action to revert
        if len(self.pipelineEditorTabs.undos[c_e]) > 0:
            to_undo = self.pipelineEditorTabs.undos[c_e].pop()
            # The first element of the list is the type of action made by the user
            action = to_undo[0]

            if action == "add_process":
                node_name = to_undo[1]
                c_e.del_node(node_name, from_undo=True)

            elif action == "delete_process":
                node_name = to_undo[1]
                class_name = to_undo[2]
                links = to_undo[3]
                c_e.add_process(class_name, node_name, from_undo=True, links=links)

            elif action == "export_plug":
                temp_plug_name = to_undo[1]
                c_e._remove_plug(_temp_plug_name=temp_plug_name, from_undo=True)

            elif action == "export_plugs":
                parameter_list = to_undo[1]
                node_name = to_undo[2]
                for parameter in parameter_list:
                    temp_plug_name = ('inputs', parameter)
                    c_e._remove_plug(_temp_plug_name=temp_plug_name, from_undo=True, from_export_plugs=True)
                self.main_window.statusBar().showMessage("Plugs {0} have been removed.".format(str(parameter_list)))

            elif action == "remove_plug":
                temp_plug_name = to_undo[1]
                new_temp_plugs = to_undo[2]
                optional = to_undo[3]
                c_e._export_plug(temp_plug_name=new_temp_plugs[0], weak_link=False,
                                 optional=optional, from_undo=True,
                                 pipeline_parameter=temp_plug_name[1])

                # Connecting all the plugs that were connected to the original plugs
                for plug_tuple in new_temp_plugs:
                    # Checking if the original plug is a pipeline input or output to adapt
                    # the links to add.
                    if temp_plug_name[0] == 'inputs':
                        source = ('', temp_plug_name[1])
                        dest = plug_tuple
                    else:
                        source = plug_tuple
                        dest = ('', temp_plug_name[1])

                    c_e.scene.add_link(source, dest, active=True, weak=False)

                    # Writing a string to represent the link
                    source_parameters = ".".join(source)
                    dest_parameters = ".".join(dest)
                    link = "->".join((source_parameters, dest_parameters))

                    c_e.scene.pipeline.add_link(link)
                    c_e.scene.update_pipeline()

            elif action == "update_node_name":
                node = to_undo[1]
                new_node_name = to_undo[2]
                old_node_name = to_undo[3]
                c_e.update_node_name(node, new_node_name, old_node_name, from_undo=True)

            elif action == "update_plug_value":
                node_name = to_undo[1]
                old_value = to_undo[2]
                plug_name = to_undo[3]
                value_type = to_undo[4]
                c_e.update_plug_value(node_name, old_value, plug_name, value_type, from_undo=True)

            elif action == "add_link":
                link = to_undo[1]
                c_e._del_link(link, from_undo=True)

            elif action == "delete_link":
                source = to_undo[1]
                dest = to_undo[2]
                active = to_undo[3]
                weak = to_undo[4]
                c_e.add_link(source, dest, active, weak, from_undo=True)
                link = source[0] + "." + source[1] + "->" + dest[0] + "." + dest[1]

            c_e.scene.pipeline.update_nodes_and_plugs_activation()
            self.nodeController.update_parameters()

    def redo(self):
        """
        Redo the last undone action on the current pipeline editor

        Actions that can be redone:
            - add_process
            - delete_process
            - export_plug
            - export_plugs
            - remove_plug
            - update_node_name
            - update_plug_value
            - add_link
            - delete_link

        """
        c_e = self.pipelineEditorTabs.get_current_editor()

        # We can redo if we have an action to make again
        if len(self.pipelineEditorTabs.redos[c_e]) > 0:
            to_redo = self.pipelineEditorTabs.redos[c_e].pop()
            # The first element of the list is the type of action made by the user
            action = to_redo[0]

            if action == "delete_process":
                node_name = to_redo[1]
                class_process = to_redo[2]
                links = to_redo[3]
                c_e.add_process(class_process, node_name, from_redo=True, links=links)

            elif action == "add_process":
                node_name = to_redo[1]
                c_e.del_node(node_name, from_redo=True)

            elif action == "export_plug":
                temp_plug_name = to_redo[1]
                c_e._remove_plug(_temp_plug_name=temp_plug_name, from_redo=True)

            elif action == "export_plugs":
                # No redo possible
                pass

            elif action == "remove_plug":
                temp_plug_name = to_redo[1]
                new_temp_plugs = to_redo[2]
                optional = to_redo[3]
                c_e._export_plug(temp_plug_name=new_temp_plugs[0], weak_link=False,
                                 optional=optional, from_redo=True,
                                 pipeline_parameter=temp_plug_name[1])

                # Connecting all the plugs that were connected to the original plugs
                for plug_tuple in new_temp_plugs:
                    # Checking if the original plug is a pipeline input or output to adapt
                    # the links to add.
                    if temp_plug_name[0] == 'inputs':
                        source = ('', temp_plug_name[1])
                        dest = plug_tuple
                    else:
                        source = plug_tuple
                        dest = ('', temp_plug_name[1])

                    c_e.scene.add_link(source, dest, active=True, weak=False)

                    # Writing a string to represent the link
                    source_parameters = ".".join(source)
                    dest_parameters = ".".join(dest)
                    link = "->".join((source_parameters, dest_parameters))

                    c_e.scene.pipeline.add_link(link)
                    c_e.scene.update_pipeline()

            elif action == "update_node_name":
                node = to_redo[1]
                new_node_name = to_redo[2]
                old_node_name = to_redo[3]
                c_e.update_node_name(node, new_node_name, old_node_name, from_redo=True)

            elif action == "update_plug_value":
                node_name = to_redo[1]
                new_value = to_redo[2]
                plug_name = to_redo[3]
                value_type = to_redo[4]
                c_e.update_plug_value(node_name, new_value, plug_name, value_type, from_redo=True)

            elif action == "add_link":
                link = to_redo[1]
                c_e._del_link(link, from_redo=True)

            elif action == "delete_link":
                source = to_redo[1]
                dest = to_redo[2]
                active = to_redo[3]
                weak = to_redo[4]
                c_e.add_link(source, dest, active, weak, from_redo=True)
                link = source[0] + "." + source[1] + "->" + dest[0] + "." + dest[1]

            c_e.scene.pipeline.update_nodes_and_plugs_activation()
            self.nodeController.update_parameters()

    def update_clinical_mode(self):
        """
        Updates the visibility of widgets/actions depending of the chosen mode

        """
        config = Config()

        # If the clinical mode is chosen, the process library is not available
        # and the user cannot save a pipeline
        if config.get_clinical_mode() == 'yes':
            self.processLibrary.setHidden(True)
            self.previewBlock.setHidden(True)
            self.save_pipeline_action.setDisabled(True)
            self.save_pipeline_as_action.setDisabled(True)
        else:
            self.processLibrary.setHidden(False)
            self.previewBlock.setHidden(False)
            self.save_pipeline_action.setDisabled(False)
            self.save_pipeline_as_action.setDisabled(False)

    def update_scans_list(self, iteration_list):
        """
        Updates the user-selected list of scans

        :param iteration_list: current list of scans in the iteration table
        """
        if self.iterationTable.check_box_iterate.isChecked():
            self.iteration_table_scans_list = iteration_list
            self.pipelineEditorTabs.scan_list = iteration_list
        else:
            self.iteration_table_scans_list = []
            self.pipelineEditorTabs.scan_list = self.scan_list
        if not self.pipelineEditorTabs.scan_list:
            self.pipelineEditorTabs.scan_list = self.project.session.get_documents_names(COLLECTION_CURRENT)
        self.pipelineEditorTabs.update_scans_list()

    def update_project(self, project):
        """
        Updates the project attribute of several objects

        :param project: current project in the software
        """
        self.project = project
        self.nodeController.project = project
        self.pipelineEditorTabs.project = project
        self.nodeController.visibles_tags = self.project.session.get_visibles()
        self.iterationTable.project = project
        ProcessMIA.project = project

    def controller_value_changed(self, signal_list):
        """
        Updates history when a pipeline node is changed

        :param signal_list: list of the needed parameters to update history
        """
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

        self.pipelineEditorTabs.undos[self.pipelineEditorTabs.get_current_editor()].append(history_maker)
        self.pipelineEditorTabs.redos[self.pipelineEditorTabs.get_current_editor()].clear()

        if case == "plug_value":
            node_name = signal_list[0]
            if node_name in ['inputs', 'outputs']:
                node_name = ''

        if case == "node_name":
            node_name = signal_list[1]

        self.nodeController.update_parameters(self.pipelineEditorTabs.get_current_pipeline().nodes[node_name].process)

    def updateProcessLibrary(self, filename):
        """
        Updates the library of processes when a pipeline is saved

        :param filename: file name of the pipeline that has been saved
        """
        filename_folder, file_name = os.path.split(filename)
        module_name = os.path.splitext(file_name)[0]
        class_name = module_name.capitalize()

        tmp_file = os.path.join(filename_folder, module_name + '_tmp')

        # Changing the "Pipeline" class name to the name of file
        with open(filename, 'r') as f:
            with open(tmp_file, 'w') as tmp:
                for line in f:
                    line = line.strip('\r\n')
                    if 'class ' in line:
                        line = 'class {0}(Pipeline):'.format(class_name)
                    tmp.write(line + '\n')

        with open(tmp_file, 'r') as tmp:
            with open(filename, 'w') as f:
                for line in tmp:
                    f.write(line)

        os.remove(tmp_file)
        config = Config()

        if os.path.relpath(filename_folder) != \
                os.path.relpath(os.path.join(config.get_mia_path(), 'processes', 'User_processes')):
            return

        # Updating __init__.py
        init_file = os.path.join(config.get_mia_path(), 'processes', 'User_processes', '__init__.py')

        # Checking that import line is not already in the file
        pattern = 'from .{0} import {1}\n'.format(module_name, class_name)
        file = open(init_file, 'r')
        flines = file.readlines()
        file.close()
        if pattern not in flines:
            with open(init_file, 'a') as f:
                print('from .{0} import {1}'.format(module_name, class_name), file=f)

        package = 'User_processes'
        path = os.path.relpath(os.path.join(filename_folder, '..'))

        # If the pipeline has already been saved
        if 'User_processes.' + module_name in sys.modules.keys():
            del sys.modules['User_processes.' + module_name]  # removing the previous version of the module
            __import__('User_processes')  # this adds the new module version to the sys.modules dictionary

        # Adding the module path to the system path
        if path not in sys.path:
            sys.path.insert(0, path)

        self.processLibrary.pkg_library.add_package(package, class_name)
        if os.path.relpath(path) not in self.processLibrary.pkg_library.paths:
            self.processLibrary.pkg_library.paths.append(os.path.relpath(path))
        self.processLibrary.pkg_library.save()

    def loadPipeline(self):
        """
        Loads a pipeline to the pipeline editor

        """
        self.pipelineEditorTabs.load_pipeline()

    def savePipeline(self):
        """
        Saves the current pipeline of the pipeline editor

        """
        filename = self.pipelineEditorTabs.get_current_filename()
        if filename:
            self.pipelineEditorTabs.save_pipeline(new_file_name=filename)
        else:
            self.pipelineEditorTabs.save_pipeline()

    def savePipelineAs(self):
        """
        Saves the current pipeline of the pipeline editor under another name

        """
        self.pipelineEditorTabs.save_pipeline()

    def loadParameters(self):
        """
        Loads pipeline parameters to the current pipeline of the pipeline editor

        """
        self.pipelineEditorTabs.load_pipeline_parameters()

        self.nodeController.update_parameters()

    def saveParameters(self):
        """
        Save the pipeline parameters of the the current pipeline of the pipeline editor

        """
        self.pipelineEditorTabs.save_pipeline_parameters()

    def initPipeline(self, pipeline=None):
        """
        Initializes the current pipeline of the pipeline editor

        During the initialization, the every output file is created empty depending on
        the inputs and are stored in the database.

        :param pipeline: used to initialize a sub-pipeline
        """

        # TODO: TO REMOVE
        """import shutil
        data_folder = os.path.join(self.project.folder, 'data', 'raw_data')
        spm_mat_file = os.path.join('..', '..', 'ressources', 'SPM.mat')
        shutil.copy2(spm_mat_file, data_folder)"""

        self.disable_progress_bar = True  # Should we add a progress bar for the initialization?
        if self.disable_progress_bar:
            name = os.path.basename(self.pipelineEditorTabs.get_current_filename())
            self.main_window.statusBar().showMessage('Pipeline "{0}" is getting initialized. Please wait.'.format(name))
            QApplication.processEvents()
            self.init_pipeline()
            self.main_window.statusBar().showMessage(
                'Pipeline "{0}" has been initialized.'.format(name))
        else:
            self.progress = InitProgress(self.project, self.pipelineEditorTabs, pipeline)
            self.progress.show()
            self.progress.exec()

    def add_plug_value_to_database(self, p_value, brick):
        """
        Adds the plug value to the database.

        :param p_value: plug value, a file name or a list of file names
        :param brick: brick of the value
        """

        if type(p_value) in [list, TraitListObject]:
            for elt in p_value:
                self.add_plug_value_to_database(elt, brick)
            return

        # This means that the value is not a filename
        if p_value in ["<undefined>", Undefined] or not os.path.isdir(os.path.split(p_value)[0]):
            return
        try:
            open(p_value, 'a').close()
        except IOError:
            raise IOError('Could not open {0} file.'.format(p_value))
        else:
            # Deleting the project's folder in the file name so it can
            # fit to the database's syntax
            old_value = p_value
            p_value = p_value.replace(self.project.folder, "")
            p_value = p_value.replace(os.path.abspath(self.project.folder), "")
            if p_value[0] in ["\\", "/"]:
                p_value = p_value[1:]

            # If the file name is already in the database, no exception is raised
            # but the user is warned
            if self.project.session.get_document(COLLECTION_CURRENT, p_value):
                print("Path {0} already in database.".format(p_value))
            else:
                self.project.session.add_document(COLLECTION_CURRENT, p_value)
                self.project.session.add_document(COLLECTION_INITIAL, p_value)

            # Adding the new brick to the output files
            bricks = self.project.session.get_value(COLLECTION_CURRENT, p_value, TAG_BRICKS)
            if bricks is None:
                bricks = []
            bricks.append(self.brick_id)
            self.project.session.set_value(COLLECTION_CURRENT, p_value, TAG_BRICKS, bricks)
            self.project.session.set_value(COLLECTION_INITIAL, p_value, TAG_BRICKS, bricks)

            # Type tag
            filename, file_extension = os.path.splitext(p_value)
            if file_extension == ".nii":
                self.project.session.set_value(COLLECTION_CURRENT, p_value, TAG_TYPE, TYPE_NII)
                self.project.session.set_value(COLLECTION_INITIAL, p_value, TAG_TYPE, TYPE_NII)
            elif file_extension == ".mat":
                self.project.session.set_value(COLLECTION_CURRENT, p_value, TAG_TYPE, TYPE_MAT)
                self.project.session.set_value(COLLECTION_INITIAL, p_value, TAG_TYPE, TYPE_MAT)

            # Adding inherited tags
            if self.inheritance_dict:
                parent_file = self.inheritance_dict[old_value]
                for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
                    if scan in str(parent_file):
                        database_parent_file = scan
                banished_tags = [TAG_TYPE, TAG_EXP_TYPE, TAG_BRICKS, TAG_CHECKSUM, TAG_FILENAME]
                for tag in self.project.session.get_fields_names(COLLECTION_CURRENT):
                    if not tag in banished_tags:
                        parent_current_value = self.project.session.get_value(COLLECTION_CURRENT, database_parent_file,
                                                                              tag)
                        self.project.session.set_value(COLLECTION_CURRENT, p_value, tag, parent_current_value)
                        parent_initial_value = self.project.session.get_value(COLLECTION_INITIAL, database_parent_file,
                                                                              tag)
                        self.project.session.set_value(COLLECTION_INITIAL, p_value, tag, parent_initial_value)

            self.project.saveModifications()

    def init_pipeline(self, pipeline=None):
        """
        Initializes the current pipeline of the pipeline editor

        :param pipeline: not None if this method is called from a sub-pipeline
        """

        config = Config()
        main_pipeline = False

        # If the initialisation is launch for the main pipeline
        if not pipeline:
            pipeline = get_process_instance(self.pipelineEditorTabs.get_current_pipeline())
            main_pipeline = True

        # Test, if it works, comment.
        if hasattr(pipeline, 'pipeline_steps'):
            pipeline.pipeline_steps.on_trait_change(
                self.pipelineEditorTabs.get_current_editor()._reset_pipeline, remove=True)
        pipeline.on_trait_change(self.pipelineEditorTabs.get_current_editor()._reset_pipeline,
                                 'selection_changed', remove=True)
        pipeline.on_trait_change(self.pipelineEditorTabs.get_current_editor()._reset_pipeline,
                                 'user_traits_changed', remove=True)

        # nodes_to_check contains the node names that need to be update
        nodes_to_check = []

        # nodes_inputs_ratio is a dictionary whose keys are the node names
        # and whose values are a list of two elements: the first one being
        # the number of activated mandatory input plugs, the second one being
        # the total number of mandatory input plugs of the corresponding node
        nodes_inputs_ratio = {}

        # nodes_inputs_ratio_list contains the ratio between the number of
        # activated mandatory input plugs and the total number of mandatory
        # input plugs of the corresponding node (the order is the same as nodes_to_check)
        nodes_inputs_ratio_list = []

        for node_name, node in pipeline.nodes.items():

            # Updating the project attribute of the processes
            if hasattr(node, 'process'):
                process = node.process
                if hasattr(process, 'use_project') and process.use_project:
                    process.project = self.project

            nb_plugs_from_in = 0
            nb_plugs = 0

            for plug_name, plug in node.plugs.items():
                if plug.links_from and not plug.output and not plug.optional:
                    nb_plugs += 1
                    # If the link come from the pipeline "global" inputs, it is
                    # added to compute the ratio
                    if list(plug.links_from)[0][0] == "":
                        nb_plugs_from_in += 1

            if nb_plugs == 0:
                ratio = 0
            else:
                ratio = nb_plugs_from_in / nb_plugs

            nodes_to_check.append(node_name)
            nodes_inputs_ratio[node_name] = [nb_plugs_from_in, nb_plugs]
            nodes_inputs_ratio_list.append(ratio)

        # Sorting the nodes_to_check list as the order (the nodes having the highest ratio
        # being at the end of the list)
        nodes_to_check = [x for _, x in sorted(zip(nodes_inputs_ratio_list, nodes_to_check))]

        while nodes_to_check:
            # Finding one node that has a ratio of 1, which means that all of its mandatory
            # inputs are "connected"
            key_name = [key for key, value in nodes_inputs_ratio.items() if value[0] == value[1]]
            if key_name:

                # This node can be initialized so it is placed at the end of the nodes_to_check list
                nodes_to_check.append(key_name[0])

                # It can also be removed from the dictionary
                del nodes_inputs_ratio[key_name[0]]

            # Reversing the list so that the node to be initialized is at the first place
            # Using OrderedDict allows to remove the duplicate in the list without losing the
            # order. So if key_name[0] appears twice, it will stay at the first place
            nodes_to_check = list(OrderedDict((x, True) for x in nodes_to_check[::-1]).keys())

            node_name = nodes_to_check.pop(0)

            nodes_to_check = nodes_to_check[::-1]

            # Inputs/Outputs nodes will be automatically updated with
            # the method update_nodes_and_plugs_activation of the pipeline object
            if node_name in ['', 'inputs', 'outputs']:
                continue

            # If the node is a pipeline node, each of its nodes has to be initialised
            node = pipeline.nodes[node_name]
            if isinstance(node, PipelineNode):
                sub_pipeline = node.process
                self.init_pipeline(sub_pipeline)
                for plug_name in node.plugs.keys():
                    if hasattr(node.plugs[plug_name], 'links_to'):  # If the plug is an output and is
                        # connected to another one
                        list_info_link = list(node.plugs[plug_name].links_to)
                        for info_link in list_info_link:
                            if info_link[2] in pipeline.nodes.values():  # The third element of info_link contains the
                                # destination node object
                                dest_node_name = info_link[0]
                                if dest_node_name:
                                    # Adding the destination node name and incrementing
                                    # the input counter of the latter if it is not the
                                    # pipeline "global" outputs ('')
                                    nodes_to_check.append(dest_node_name)
                                    nodes_inputs_ratio[dest_node_name][0] += 1

                pipeline.update_nodes_and_plugs_activation()
                continue

            # Adding the brick to the bricks history
            self.brick_id = str(uuid.uuid4())
            self.project.session.add_document(COLLECTION_BRICK, self.brick_id)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_NAME, node_name)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INIT_TIME, datetime.datetime.now())
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INIT, "Not Done")
            self.project.saveModifications()

            process = node.process

            if 'IRMaGe_processes' in str(process.__class__):  # update launching parameters for IRMaGe_processes bricks   ### Test for matlab launch
                print('\nUpdating the launching parameters for IRMaGe process node: {0} ...\n'.format(node_name))  ### Test for matlab launch
                    
                if config.get_use_spm_standalone() == 'yes':  ### Test for matlab launch
                    pipeline.nodes[node_name].process.use_mcr = True
                    pipeline.nodes[node_name].process.paths = config.get_spm_standalone_path().split()
                    pipeline.nodes[node_name].process.matlab_cmd = config.get_matlab_command()
                        
                elif config.get_use_spm() == 'yes':
                    pipeline.nodes[node_name].process.use_mcr = False
                    pipeline.nodes[node_name].process.paths = config.get_spm_path().split()
                    pipeline.nodes[node_name].process.matlab_cmd = config.get_matlab_command()

                if not os.path.isdir(os.path.abspath(self.project.folder + os.sep + 'scripts')):  ### Test for matlab launch
                    os.mkdir(os.path.abspath(self.project.folder + os.sep + 'scripts'))  ### Test for matlab launch

                pipeline.nodes[node_name].process.output_directory = os.path.abspath(self.project.folder +
                                                                                         os.sep + 'scripts')
                pipeline.nodes[node_name].process.mfile = True

            # Getting the list of the outputs of the node according to its inputs
            try:
                self.inheritance_dict = None
                (process_outputs, self.inheritance_dict) = process.list_outputs()
            except TraitError:
                print("TRAIT ERROR for node {0}".format(node_name))
            except ValueError:
                process_outputs = process.list_outputs()
                print("No inheritance dict for the process {0}.".format(node_name))
            except AttributeError:  # If the process has no "list_outputs" method, which is the case for Nipype's
                # interfaces
                try:
                    process_outputs = process._nipype_interface._list_outputs()
                    # The Nipype Process outputs are always "private" for Capsul
                    tmp_dict = {}
                    for key, value in process_outputs.items():
                        tmp_dict['_' + key] = process_outputs[key]
                    process_outputs = tmp_dict
                except:  # TODO: test which kind of error can generate a Nipype interface
                    print("No output list method for the process {0}.".format(node_name))
                    process_outputs = {}

            # Adding I/O to database history
            inputs = process.get_inputs()
            keys2consider = ['use_mcr', 'paths', 'matlab_cmd', 'output_directory'] # plugs to be filled automatically
            
            for key in inputs:
                
                if inputs[key] is Undefined:
                    inputs[key] = "<undefined>"

#Could be cleaner to do some tests with warning pop up if necessary (ex. if config.get_spm_standalone_path() is None, etc ...)
                    
#                if (isinstance(process, NipypeProcess)) and (key in keys2consider) and (inputs[key] == "<undefined>"):
                if 'NipypeProcess' in str(process.__class__):                                   # update launching parameters for IRMaGe_processes bricks ### Test for matlab launch
                    print('\nUpdating the launching parameters for NipypeProcess node: {0} ...'.format(node_name))                                     ### Test for matlab launch
                    keys2consider = ['use_mcr', 'paths', 'matlab_cmd', 'output_directory']      # plugs to be filled automatically                     ### Test for matlab launch
                    
                    if (key == keys2consider[0]) and (config.get_use_spm_standalone() == 'yes'):  # use_mcr parameter                                  ### Test for matlab launch
                        inputs[key] = True                                                                                                             ### Test for matlab launch
                    elif (key == keys2consider[0]) and (config.get_use_spm_standalone() == 'no'):                                                      ### Test for matlab launch
                        inputs[key] = False                                                                                                            ### Test for matlab launch
                            
                    if (key == keys2consider[1]) and (config.get_use_spm_standalone() == 'yes'):  # paths  parameter                                   ### Test for matlab launch
                        inputs[key] = config.get_spm_standalone_path().split()                                                                         ### Test for matlab launch
                    elif (key == keys2consider[1]) and (config.get_use_spm() == 'yes'):                                                                ### Test for matlab launch
                        inputs[key] = config.get_spm_path().split()                                                                                    ### Test for matlab launch

                    if (key == keys2consider[2]) and (config.get_use_spm_standalone() == 'yes'):  # matlab_cmd parameter                               ### Test for matlab launch
                        inputs[key] = (config.get_spm_standalone_path() + '/run_spm12.sh ' +                                                           ### Test for matlab launch
                                       config.get_matlab_standalone_path() + ' script')                                                                ### Test for matlab launch
                    elif (key == keys2consider[2]) and (config.get_use_spm_standalone() == 'no'):                                                      ### Test for matlab launch
                        inputs[key] = config.get_matlab_path()                                                                                         ### Test for matlab launch

                    if (key == keys2consider[3]):                                                 # output_directory parameter                         ### Test for matlab launch

                        if not os.path.isdir(os.path.abspath(self.project.folder + '/scripts')):                                                       ### Test for matlab launch
                            os.mkdir(os.path.abspath(self.project.folder + '/scripts'))                                                                ### Test for matlab launch

                        inputs[key] =  os.path.abspath(self.project.folder + '/scripts')                                                               ### Test for matlab launch
   
                    try:                                                                                                                               ### Test for matlab launch
                        pipeline.nodes[node_name].set_plug_value(key, inputs[key])                                                                     ### Test for matlab launch
                    
                    except TraitError:                                                                                                                 ### Test for matlab launch
                    
                        if isinstance(inputs[key], list) and len(inputs[key]) == 1:                                                                    ### Test for matlab launch
                        
                            try:                                                                                                                       ### Test for matlab launch
                                pipeline.nodes[key].set_plug_value(key, inputs[key][0])                                                                ### Test for matlab launch
                            
                            except TraitError:                                                                                                         ### Test for matlab launch
                                print("Trait error for {0} plug of {1} node".format(key, inputs[key]))                                                 ### Test for matlab launch

            outputs = process.get_outputs()
            for key in outputs:
                value = outputs[key]
                if value is Undefined:
                    outputs[key] = "<undefined>"
            self.project.saveModifications()
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INPUTS, inputs)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_OUTPUTS, outputs)

            if process_outputs:
                for plug_name, plug_value in process_outputs.items():
                    node = pipeline.nodes[node_name]
                    if plug_name not in node.plugs.keys():
                        continue
                    if plug_value not in ["<undefined>", Undefined]:
                        self.add_plug_value_to_database(plug_value, self.brick_id)

                    list_info_link = list(node.plugs[plug_name].links_to)

                    # If the output is connected to another node,
                    # the latter is added to nodes_to_check
                    for info_link in list_info_link:
                        dest_node_name = info_link[0]
                        if dest_node_name:
                            # Adding the destination node name and incrementing
                            # the input counter of the latter
                            nodes_to_check.append(dest_node_name)
                            nodes_inputs_ratio[dest_node_name][0] += 1

                    try:
                        pipeline.nodes[node_name].set_plug_value(plug_name, plug_value)
                    except TraitError:
                        if type(plug_value) is list and len(plug_value) == 1:
                            try:
                                pipeline.nodes[node_name].set_plug_value(plug_name, plug_value[0])
                            except TraitError:
                                print("Trait error for {0} plug of {1} node".format(plug_name, node_name))
                                pass

                    pipeline.update_nodes_and_plugs_activation()

            # Adding I/O to database history again to update outputs
            inputs = process.get_inputs()
            for key in inputs:
                value = inputs[key]
                if value is Undefined:
                    inputs[key] = "<undefined>"
            outputs = process.get_outputs()
            for key in outputs:
                value = outputs[key]
                if value is Undefined:
                    outputs[key] = "<undefined>"
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INPUTS, inputs)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_OUTPUTS, outputs)

            # Setting brick init state if init finished correctly
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INIT, "Done")
            self.project.saveModifications()

        # Test, if it works, comment.
        pipeline.on_trait_change(self.pipelineEditorTabs.get_current_editor()._reset_pipeline, 'selection_changed',
                                 dispatch='ui')
        pipeline.on_trait_change(self.pipelineEditorTabs.get_current_editor()._reset_pipeline, 'user_traits_changed',
                                 dispatch='ui')
        if hasattr(pipeline, 'pipeline_steps'):
            pipeline.pipeline_steps.on_trait_change(
                self.pipelineEditorTabs.get_current_editor()._reset_pipeline, dispatch='ui')

        # Updating the node controller
        if main_pipeline:
            node_controller_node_name = self.nodeController.node_name
            if node_controller_node_name in ['inputs', 'outputs']:
                node_controller_node_name = ''
            self.nodeController.display_parameters(self.nodeController.node_name,
                                                   pipeline.nodes[node_controller_node_name].process,
                                                   pipeline)
        
    def runPipeline(self):
        """
        Runs the current pipeline of the pipeline editor

        """
        name = os.path.basename(self.pipelineEditorTabs.get_current_filename())
        self.main_window.statusBar().showMessage('Pipeline "{0}" is getting run. Please wait.'.format(name))
        QApplication.processEvents()

        if self.iterationTable.check_box_iterate.isChecked():
            iterated_tag = self.iterationTable.iterated_tag
            tag_values = self.iterationTable.tag_values_list
            ui_iteration = PopUpSelectIteration(iterated_tag, tag_values)
            if ui_iteration.exec():
                tag_values = ui_iteration.final_values
                for tag_value in tag_values:

                    # Status bar update
                    self.main_window.statusBar().showMessage(
                        'Pipeline "{0}" is getting run for {1} {2}. Please wait.'.format(name, iterated_tag,
                                                                                          tag_value))
                    QApplication.processEvents()

                    idx_combo_box = self.iterationTable.combo_box.findText(tag_value)
                    self.iterationTable.combo_box.setCurrentIndex(idx_combo_box)
                    self.iterationTable.update_table()

                    self.progress = InitProgress(self.project, self.pipelineEditorTabs, None)
                    self.progress.show()
                    self.progress.exec()

                    self.progress = RunProgress(self.pipelineEditorTabs)
                    self.progress.show()
                    self.progress.exec()

            self.main_window.statusBar().showMessage(
                'Pipeline "{0}" has been run for {1} {2}. Please wait.'.format(name, iterated_tag, tag_values))
        else:
            try:
                self.progress = RunProgress(self.pipelineEditorTabs)
                self.progress.show()
                self.progress.exec()
            except:
                self.main_window.statusBar().showMessage(
                    'Pipeline "{0}" has not been correctly run.'.format(name))
            else:
                self.main_window.statusBar().showMessage(
                    'Pipeline "{0}" has been correctly run.'.format(name))

    def displayNodeParameters(self, node_name, process):
        """
        Displays the node controller when a node is clicked

        :param node_name: name of the node to display parameters
        :param process: process instance of the corresponding node
        :return:
        """
        if isinstance(process, Switch):
            pass
        else:
            self.nodeController.display_parameters(node_name, process, self.pipelineEditorTabs.get_current_pipeline())
            self.scrollArea.setWidget(self.nodeController)


class InitProgress(QProgressDialog):
    """
    Init progress bar
    """

    def __init__(self, project, diagram_view, pipeline):

        super(InitProgress, self).__init__("Please wait while the pipeline is being initialized...", None, 0, 0)

        if not pipeline:
            nodes_to_check = []
            for node_name in diagram_view.get_current_pipeline().nodes.keys():
                nodes_to_check.append(node_name)
            bricks_number = self.get_bricks_number(diagram_view.get_current_pipeline())
        else:
            bricks_number = self.get_bricks_number(pipeline)
        self.setMaximum(bricks_number)
        self.setWindowTitle("Pipeline initialization")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(False)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.project = project
        self.diagramView = diagram_view
        self.pipeline = pipeline

        self.setMinimumDuration(0)
        self.setValue(0)

        self.worker = InitWorker(self.project, self.diagramView, self.pipeline, self)
        self.worker.finished.connect(self.close)
        self.worker.notifyProgress.connect(self.onProgress)
        self.worker.start()

    def onProgress(self, i):
        """
        Signal to set the pipeline initialization progressbar value
        """

        self.setValue(i)

    def get_bricks_number(self, pipeline):
        """
        Gives the number of bricks in the current pipeline
        :return: The number of bricks to initialize in the current pipeline
        """

        number_of_bricks = 0
        for node_name in pipeline.nodes.keys():
            if node_name in ['', 'inputs', 'outputs']:
                continue
            node = pipeline.nodes[node_name]
            if isinstance(node, PipelineNode):
                sub_pipeline = node.process
                number_of_bricks += self.get_bricks_number(sub_pipeline)
                continue
            else:
                number_of_bricks += 1
        return number_of_bricks + 1


class InitWorker(QThread):
    """
    Thread doing the pipeline initialization
    """

    notifyProgress = pyqtSignal(int)

    def __init__(self, project, diagram_view, pipeline, progress):
        super().__init__()
        self.project = project
        self.diagramView = diagram_view
        self.pipeline = pipeline
        self.progress = progress

    def add_plug_value_to_database(self, p_value, brick):
        """
        Adds the plug value to the database.
        :param p_value: plug value, a file name or a list of file names
        :param brick: brick of the value
        """

        if type(p_value) in [list, TraitListObject]:
            for elt in p_value:
                self.add_plug_value_to_database(elt, brick)
            return

        # This means that the value is not a filename
        if p_value in ["<undefined>", Undefined] or not os.path.isdir(os.path.split(p_value)[0]):
            return
        try:
            open(p_value, 'a').close()
        except IOError:
            raise IOError('Could not open {0} file.'.format(p_value))
        else:
            # Deleting the project's folder in the file name so it can
            # fit to the database's syntax
            old_value = p_value
            p_value = p_value.replace(self.project.folder, "")
            if p_value[0] in ["\\", "/"]:
                p_value = p_value[1:]

            # If the file name is already in the database, no exception is raised
            # but the user is warned
            if self.project.session.get_document(COLLECTION_CURRENT, p_value):
                print("Path {0} already in database.".format(p_value))
            else:
                self.project.session.add_document(COLLECTION_CURRENT, p_value)
                self.project.session.add_document(COLLECTION_INITIAL, p_value)

            # Adding the new brick to the output files
            bricks = self.project.session.get_value(COLLECTION_CURRENT, p_value, TAG_BRICKS)
            if bricks is None:
                bricks = []
            bricks.append(self.brick_id)
            self.project.session.set_value(COLLECTION_CURRENT, p_value, TAG_BRICKS, bricks)
            self.project.session.set_value(COLLECTION_INITIAL, p_value, TAG_BRICKS, bricks)

            # Type tag
            filename, file_extension = os.path.splitext(p_value)
            if file_extension == ".nii":
                self.project.session.set_value(COLLECTION_CURRENT, p_value, TAG_TYPE, TYPE_NII)
                self.project.session.set_value(COLLECTION_INITIAL, p_value, TAG_TYPE, TYPE_NII)
            elif file_extension == ".mat":
                self.project.session.set_value(COLLECTION_CURRENT, p_value, TAG_TYPE, TYPE_MAT)
                self.project.session.set_value(COLLECTION_INITIAL, p_value, TAG_TYPE, TYPE_MAT)

            # Adding inherited tags
            if self.inheritance_dict:
                parent_file = self.inheritance_dict[old_value]
                for scan in self.project.session.get_documents_names(COLLECTION_CURRENT):
                    if scan in str(parent_file):
                        database_parent_file = scan
                banished_tags = [TAG_TYPE, TAG_EXP_TYPE, TAG_BRICKS, TAG_CHECKSUM, TAG_FILENAME]
                for tag in self.project.session.get_fields_names(COLLECTION_CURRENT):
                    if not tag in banished_tags:
                        parent_current_value = self.project.session.get_value(COLLECTION_CURRENT, database_parent_file,
                                                                              tag)
                        self.project.session.set_value(COLLECTION_CURRENT, p_value, tag, parent_current_value)
                        parent_initial_value = self.project.session.get_value(COLLECTION_INITIAL, database_parent_file,
                                                                              tag)
                        self.project.session.set_value(COLLECTION_INITIAL, p_value, tag, parent_initial_value)

            self.project.saveModifications()

    def init_pipeline(self, pipeline):

        main_pipeline = False

        # If the initialisation is launch for the main pipeline
        if not pipeline:
            pipeline = get_process_instance(self.diagramView.get_current_pipeline())
            main_pipeline = True

        # Test, if it works, comment.
        if hasattr(pipeline, 'pipeline_steps'):
            pipeline.pipeline_steps.on_trait_change(
                self.diagramView.get_current_editor()._reset_pipeline, remove=True)
        pipeline.on_trait_change(self.diagramView.get_current_editor()._reset_pipeline,
                                 'selection_changed', remove=True)
        pipeline.on_trait_change(self.diagramView.get_current_editor()._reset_pipeline,
                                 'user_traits_changed', remove=True)

        # nodes_to_check contains the node names that need to be update
        nodes_to_check = []

        # nodes_inputs_ratio is a dictionary whose keys are the node names
        # and whose values are a list of two elements: the first one being
        # the number of activated mandatory input plugs, the second one being
        # the total number of mandatory input plugs of the corresponding node
        nodes_inputs_ratio = {}

        # nodes_inputs_ratio_list contains the ratio between the number of
        # activated mandatory input plugs and the total number of mandatory
        # input plugs of the corresponding node (the order is the same as nodes_to_check)
        nodes_inputs_ratio_list = []

        for node_name, node in pipeline.nodes.items():
            nb_plugs_from_in = 0
            nb_plugs = 0

            for plug_name, plug in node.plugs.items():
                if plug.links_from and not plug.output and not plug.optional:
                    nb_plugs += 1
                    # If the link come from the pipeline "global" inputs, it is
                    # added to compute the ratio
                    if list(plug.links_from)[0][0] == "":
                        nb_plugs_from_in += 1

            if nb_plugs == 0:
                ratio = 0
            else:
                ratio = nb_plugs_from_in / nb_plugs

            nodes_to_check.append(node_name)
            nodes_inputs_ratio[node_name] = [nb_plugs_from_in, nb_plugs]
            nodes_inputs_ratio_list.append(ratio)

        # Sorting the nodes_to_check list as the order (the nodes having the highest ratio
        # being at the end of the list)
        nodes_to_check = [x for _, x in sorted(zip(nodes_inputs_ratio_list, nodes_to_check))]

        idx = self.progress.value()

        while nodes_to_check:
            # Finding one node that has a ratio of 1, which means that all of its mandatory
            # inputs are "connected"
            key_name = [key for key, value in nodes_inputs_ratio.items() if value[0] == value[1]]
            if key_name:

                # This node can be initialized so it is placed at the end of the nodes_to_check list
                nodes_to_check.append(key_name[0])

                # It can also be removed from the dictionary
                del nodes_inputs_ratio[key_name[0]]

            # Reversing the list so that the node to be initialized is at the first place
            # Using OrderedDict allows to remove the duplicate in the list without losing the
            # order. So if key_name[0] appears twice, it will stay at the first place
            nodes_to_check = list(OrderedDict((x, True) for x in nodes_to_check[::-1]).keys())

            node_name = nodes_to_check.pop(0)

            nodes_to_check = nodes_to_check[::-1]

            # Inputs/Outputs nodes will be automatically updated with
            # the method update_nodes_and_plugs_activation of the pipeline object
            if node_name in ['', 'inputs', 'outputs']:
                continue

            # progressbar
            idx += 1
            self.notifyProgress.emit(idx)
            sleep(0.1)

            # If the node is a pipeline node, each of its nodes has to be initialised
            node = pipeline.nodes[node_name]
            if isinstance(node, PipelineNode):
                sub_pipeline = node.process
                self.init_pipeline(sub_pipeline)
                for plug_name in node.plugs.keys():
                    if hasattr(node.plugs[plug_name], 'links_to'):  # If the plug is an output and is
                        # connected to another one
                        list_info_link = list(node.plugs[plug_name].links_to)
                        for info_link in list_info_link:
                            if info_link[2] in pipeline.nodes.values():  # The third element of info_link contains the
                                # destination node object
                                dest_node_name = info_link[0]
                                if dest_node_name:
                                    # Adding the destination node name and incrementing
                                    # the input counter of the latter if it is not the
                                    # pipeline "global" outputs ('')
                                    nodes_to_check.append(dest_node_name)
                                    nodes_inputs_ratio[dest_node_name][0] += 1

                pipeline.update_nodes_and_plugs_activation()
                continue

            # Adding the brick to the bricks history
            self.brick_id = str(uuid.uuid4())
            self.project.session.add_document(COLLECTION_BRICK, self.brick_id)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_NAME, node_name)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INIT_TIME, datetime.datetime.now())
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INIT, "Not Done")
            self.project.saveModifications()

            process = node.process

            # Getting the list of the outputs of the node according to its inputs
            try:
                self.inheritance_dict = None
                (process_outputs, self.inheritance_dict) = process.list_outputs()
            except TraitError:
                print("TRAIT ERROR for node {0}".format(node_name))
            except ValueError:
                process_outputs = process.list_outputs()
                print("No inheritance dict for the process {0}.".format(node_name))
            except AttributeError:  # If the process has no "list_outputs" method, which is the case for Nipype's
                # interfaces
                try:
                    process_outputs = process._nipype_interface._list_outputs()
                    # The Nipype Process outputs are always "private" for Capsul
                    tmp_dict = {}
                    for key, value in process_outputs.items():
                        tmp_dict['_' + key] = process_outputs[key]
                    process_outputs = tmp_dict
                except:  # TODO: test which kind of error can generate a Nipype interface
                    print("No output list method for the process {0}.".format(node_name))
                    process_outputs = {}

            # Adding I/O to database history
            inputs = process.get_inputs()
            for key in inputs:
                value = inputs[key]
                if value is Undefined:
                    inputs[key] = "<undefined>"
            outputs = process.get_outputs()
            for key in outputs:
                value = outputs[key]
                if value is Undefined:
                    outputs[key] = "<undefined>"
            self.project.saveModifications()
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INPUTS, inputs)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_OUTPUTS, outputs)

            if process_outputs:
                for plug_name, plug_value in process_outputs.items():
                    node = pipeline.nodes[node_name]
                    if plug_name not in node.plugs.keys():
                        continue
                    if plug_value not in ["<undefined>", Undefined]:
                        self.add_plug_value_to_database(plug_value, self.brick_id)

                    list_info_link = list(node.plugs[plug_name].links_to)

                    # If the output is connected to another node,
                    # the latter is added to nodes_to_check
                    for info_link in list_info_link:
                        dest_node_name = info_link[0]
                        if dest_node_name:
                            # Adding the destination node name and incrementing
                            # the input counter of the latter
                            nodes_to_check.append(dest_node_name)
                            nodes_inputs_ratio[dest_node_name][0] += 1

                    try:
                        pipeline.nodes[node_name].set_plug_value(plug_name, plug_value)
                    except TraitError:
                        if type(plug_value) is list and len(plug_value) == 1:
                            try:
                                pipeline.nodes[node_name].set_plug_value(plug_name, plug_value[0])
                            except TraitError:
                                print("Trait error for {0} plug of {1} node".format(plug_name, node_name))
                                pass

                    pipeline.update_nodes_and_plugs_activation()

            # Adding I/O to database history again to update outputs
            inputs = process.get_inputs()
            for key in inputs:
                value = inputs[key]
                if value is Undefined:
                    inputs[key] = "<undefined>"
            outputs = process.get_outputs()
            for key in outputs:
                value = outputs[key]
                if value is Undefined:
                    outputs[key] = "<undefined>"
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INPUTS, inputs)
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_OUTPUTS, outputs)

            # Setting brick init state if init finished correctly
            self.project.session.set_value(COLLECTION_BRICK, self.brick_id, BRICK_INIT, "Done")
            self.project.saveModifications()

        # Test, if it works, comment.
        pipeline.on_trait_change(self.diagramView.get_current_editor()._reset_pipeline, 'selection_changed',
                                 dispatch='ui')
        pipeline.on_trait_change(self.diagramView.get_current_editor()._reset_pipeline, 'user_traits_changed',
                                 dispatch='ui')
        if hasattr(pipeline, 'pipeline_steps'):
            pipeline.pipeline_steps.on_trait_change(
                self.diagramView.get_current_editor()._reset_pipeline, dispatch='ui')

        # Updating the node controller
        if main_pipeline:
            node_controller_node_name = self.nodeController.node_name
            if node_controller_node_name in ['inputs', 'outputs']:
                node_controller_node_name = ''
            self.nodeController.display_parameters(self.nodeController.node_name,
                                                   pipeline.nodes[node_controller_node_name].process,
                                                   pipeline)

    def run(self):
        self.init_pipeline(self.pipeline)
        idx = self.progress.value()
        idx += 1
        self.progress.setValue(idx)
        QApplication.processEvents()


class RunProgress(QProgressDialog):
    """
    Run progress bar
    """

    def __init__(self, diagram_view):

        super(RunProgress, self).__init__("Please wait while the pipeline is being run...", None, 0, 0)

        self.setWindowTitle("Pipeline run")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True)

        self.diagramView = diagram_view

        self.setMinimumDuration(0)
        self.setValue(0)

        self.worker = RunWorker(self.diagramView)
        self.worker.finished.connect(self.close)
        self.worker.start()


class RunWorker(QThread):
    """
    Thread doing the pipeline run
    """

    def __init__(self, diagram_view):
        super().__init__()
        self.diagramView = diagram_view

    def run(self):

        def _check_nipype_processes(pplne):
            for node_name, node in pplne.nodes.items():
                if isinstance(node.process, Pipeline):
                    if node_name != "":
                        _check_nipype_processes(node.process)
                elif isinstance(node.process, NipypeProcess):
                    node.process.activate_copy = False

        _check_nipype_processes(self.diagramView.get_current_pipeline())

        pipeline = get_process_instance(self.diagramView.get_current_pipeline())

        # Reading config
        config = Config()
        spm_standalone_path = config.get_spm_standalone_path()
        spm_path = config.get_spm_path()
        matlab_path = config.get_matlab_path()
        matlab_standalone_path = config.get_matlab_standalone_path()
        use_spm = config.get_use_spm()
        use_spm_standalone = config.get_use_spm_standalone()
        use_matlab = config.get_use_matlab()

        if use_spm_standalone == "yes" and os.path.exists(spm_standalone_path) \
                and os.path.exists(matlab_standalone_path):

            # WILL BE REMOVED WHEN ISSUE #27 WILL BE RESOLVED

            # Setting environment variables to run SPM12 standalone correctly
            # print("force_spmmcr", os.environ["FORCE_SPMMCR"])
            # print("spmmcrcmd", os.environ["SPMMCRCMD"])

            """# OS.ENVIRON TEST
            print("FORCE_SPMMCR in environ", "FORCE_SPMMCR" in os.environ.keys())
            _environ = os.environ.copy()
            try:
                _environ["FORCE_SPMMCR"] = '1'
                _environ["SPMMCRCMD"] = os.path.join(spm_standalone_path, 'run_spm12.sh') + ' ' + \
                                        matlab_standalone_path + os.sep + " script"
            finally:
                os.environ.clear()
                os.environ.update(_environ)"""

            '''# SUBPROCESS TEST: DOES NOT WORK
            import subprocess
            subprocess.run(["export FORCE_SPMMCR=1"])
            subprocess.run(["export SPMMCRCMD='" + os.path.join(spm_standalone_path, 'run_spm12.sh') + ' ' +
                            matlab_standalone_path + os.sep + " script'"])'''

            '''# putenv test
            os.putenv("FORCE_SPMMCR", '1')
            os.putenv("SPMMCRCMD", os.path.join(spm_standalone_path, 'run_spm12.sh') + ' ' +
                      matlab_standalone_path + os.sep + ' script')'''

            # print("os.environ", os.environ)
            # os.environ["FORCE_SPMMCR"] = '1'
            # os.environ["SPMMCRCMD"] = os.path.join(spm_standalone_path, 'run_spm12.sh') + ' ' + matlab_standalone_path \
            #                          + os.sep + ' script'
            #
            # print("force_spmmcr", os.environ["FORCE_SPMMCR"])
            # print("spmmcrcmd", os.environ["SPMMCRCMD"])

            if os.path.exists(matlab_path):
                study_config = StudyConfig(use_spm=True, spm_directory=spm_standalone_path,
                                           spm_exec=matlab_standalone_path, matlab_exec=matlab_path,
                                           output_directory=spm_standalone_path, spm_standalone=True)
            else:
                study_config = StudyConfig(use_spm=True, spm_directory=spm_standalone_path,
                                           spm_exec=matlab_standalone_path,
                                           output_directory=spm_standalone_path, spm_standalone=True)

        elif use_spm == "yes" and use_matlab == "yes":  # Using without SPM standalone
            study_config = StudyConfig(use_spm=True, matlab_exec=matlab_path, spm_directory=spm_path,
                                       spm_standalone=False, use_matlab=True, output_directory=spm_path)
        else:
            study_config = StudyConfig(use_spm=False)

        study_config.reset_process_counter()

        try:
            study_config.run(pipeline, verbose=1)
        except OSError as e:
            self.msg = QMessageBox()
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText("SPM standalone is not set")
            self.msg.setInformativeText(
                "SPM processes cannot be run with SPM standalone not set.\nYou can activate it and set the paths in MIA preferences.")
            self.msg.setWindowTitle("Error")
            self.msg.setStandardButtons(QMessageBox.Ok)
            self.msg.buttonClicked.connect(self.msg.close)
            self.msg.show()
