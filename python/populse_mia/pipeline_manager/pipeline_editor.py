##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import sys
import six
import yaml
from traits.api import TraitError

# PyQt5 imports
from PyQt5 import QtGui, QtWidgets, QtCore

# Capsul imports
from capsul.api import get_process_instance, Process, PipelineNode, Switch

# soma-base imports
from soma.utils.weak_proxy import weak_proxy

# Populse_MIA imports
from populse_mia.pipeline_manager.capsul_files.pipeline_developper_view import PipelineDevelopperView, NodeGWidget
from populse_mia.pipeline_manager.node_controller import FilterWidget
from populse_mia.pop_ups.pop_up_close_pipeline import PopUpClosePipeline
from populse_mia.software_properties.config import Config

if sys.version_info[0] >= 3:
    unicode = str

    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()


class PipelineEditorTabs(QtWidgets.QTabWidget):
    """
    Tab widget that contains pipeline editors

    Attributes:
        - project: current project in the software
        - scan_list: list of the selected database files
        - main_window: main window of the software
        - undos: dictionary containing as values the undo list and as keys the pipeline in the corresponding tab
        - redos: dictionary containing as values the redo list and as keys the name of the corresponding tab

    Methods:
        - new_tab: creates a new tab and a new editor
        - close_tab: closes the selected tab and editor
        - set_current_editor_by_tab_name: sets the current editor
        - get_current_editor: gets the instance of the current editor
        - get_tab_name_by_index: gets the tab title from its index in the editors
        - get_filename_by_index: gets the pipeline filename from its index in the editors
        - get_index_by_tab_name: gets the index of the editor corresponding to the given tab name
        - get_index_by_filename: gets the index of the editor corresponding to the given pipeline filename
        - get_current_tab_name: gets the tab title of the current editor
        - get_current_filename: gets the file name of the current pipeline
        - get_current_pipeline: gets the instance of the current pipeline
        - save_pipeline: saves the pipeline of the current editor
        - load_pipeline: loads a new pipeline
        - save_pipeline_parameters: saves the pipeline parameters of the current editor
        - load_pipeline_parameters: loads parameters to the pipeline of the current editor
        - emit_node_clicked: emits a signal when a node is clicked
        - emit_switch_clicked: emits a signal when a switch is clicked
        - emit_pipeline_saved: emits a signal when a pipeline is saved
        - update_pipeline_editors: updates editors
        - update_history: updates undo/redo history of an editor
        - reset_pipeline: resets the pipeline of the current editor
        - update_scans_list: updates the list of database scans in every editor
        - open_sub_pipeline: opens a sub-pipeline in a new tab
        - open_filter: opens a filter widget
        - export_to_db_scans: exports the input of a filter to "database_scans"
        - check_modifications: checks if the nodes of the current pipeline have been modified
        - has_pipeline_nodes: checks if any of the pipelines in the editor tabs have pipeline nodes

    """

    pipeline_saved = QtCore.pyqtSignal(str)
    node_clicked = QtCore.pyqtSignal(str, Process)
    switch_clicked = QtCore.pyqtSignal(str, Switch)

    def __init__(self, project, scan_list, main_window):
        """
        Initialization of the Pipeline Editor tabs

        :param project: current project in the software
        :param scan_list: list of the selected database files
        :param main_window: main window of the software
        """
        super(PipelineEditorTabs, self).__init__()

        self.project = project
        self.main_window = main_window
        self.setStyleSheet('QTabBar{font-size:12pt;font-family:Arial;text-align: center;color:black;}')
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.scan_list = scan_list

        self.undos = {}
        self.redos = {}

        p_e = PipelineEditor(self.project, self.main_window)
        p_e.node_clicked.connect(self.emit_node_clicked)
        p_e.switch_clicked.connect(self.emit_switch_clicked)
        p_e.pipeline_saved.connect(self.emit_pipeline_saved)
        p_e.pipeline_modified.connect(self.update_pipeline_editors)
        p_e.edit_sub_pipeline.connect(self.open_sub_pipeline)
        p_e.open_filter.connect(self.open_filter)
        p_e.export_to_db_scans.connect(self.export_to_db_scans)

        # Setting a default editor called "New Pipeline"
        self.addTab(p_e, "New Pipeline")
        self.undos[p_e] = []
        self.redos[p_e] = []

        # Tool button to add a tab
        tb = QtWidgets.QToolButton()
        tb.setText('+')
        tb.clicked.connect(self.new_tab)

        self.addTab(QtWidgets.QLabel('Add tabs by pressing "+"'), str())
        self.setTabEnabled(1, False)
        self.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, tb)

        # Checking if the pipeline nodes have been modified
        self.tabBarClicked.connect(self.check_modifications)

    def new_tab(self):
        """
        Creates a new tab and a new editor and makes the new tab current

        """

        # Creating a new editor
        p_e = PipelineEditor(self.project, self.main_window)
        p_e.node_clicked.connect(self.emit_node_clicked)
        p_e.switch_clicked.connect(self.emit_switch_clicked)
        p_e.pipeline_saved.connect(self.emit_pipeline_saved)
        p_e.pipeline_modified.connect(self.update_pipeline_editors)
        p_e.edit_sub_pipeline.connect(self.open_sub_pipeline)
        p_e.open_filter.connect(self.open_filter)
        p_e.export_to_db_scans.connect(self.export_to_db_scans)

        # A unique editor name has to be automatically generated
        idx = 1
        while True and idx < 50:
            name = "New Pipeline {0}".format(idx)
            if self.get_index_by_tab_name(name):
                idx += 1
                continue
            else:
                break
        if name is not None:
            self.undos[p_e] = []
            self.redos[p_e] = []
        else:
            print('Too many tabs in the Pipeline Editor')
            return

        self.insertTab(self.count()-1, p_e, name)
        self.setCurrentIndex(self.count()-2)

    def close_tab(self, idx):
        """
        Closes the selected tab and editor

        :param idx: index of the tab to close
        """

        filename = os.path.basename(self.get_filename_by_index(idx))
        editor = self.get_editor_by_index(idx)

        # If the pipeline has been modified and not saved
        if self.tabText(idx)[-2:] == " *":
            self.pop_up_close = PopUpClosePipeline(filename)
            self.pop_up_close.save_as_signal.connect(self.save_pipeline)
            self.pop_up_close.exec()

            can_exit = self.pop_up_close.can_exit()

            if self.pop_up_close.bool_save_as:
                if idx == self.currentIndex():
                    self.setCurrentIndex(max(0, self.currentIndex() - 1))
                self.removeTab(idx)
                return

        else:
            can_exit = True

        if not can_exit:
            return

        del self.undos[editor]
        del self.redos[editor]

        if idx == self.currentIndex():
            self.setCurrentIndex(max(0, self.currentIndex()-1))
        self.removeTab(idx)

        # If there is no more editor, adding one
        if self.count() == 1:
            p_e = PipelineEditor(self.project, self.main_window)
            p_e.node_clicked.connect(self.emit_node_clicked)
            p_e.switch_clicked.connect(self.emit_switch_clicked)
            p_e.pipeline_saved.connect(self.emit_pipeline_saved)
            p_e.pipeline_modified.connect(self.update_pipeline_editors)
            p_e.edit_sub_pipeline.connect(self.open_sub_pipeline)
            p_e.open_filter.connect(self.open_filter)
            p_e.export_to_db_scans.connect(self.export_to_db_scans)

            # Setting a default editor called "New Pipeline"
            self.insertTab(0, p_e, "New Pipeline")
            self.setCurrentIndex(0)
            self.undos[p_e] = []
            self.redos[p_e] = []

    def set_current_editor_by_tab_name(self, tab_name):
        """
        Sets the current editor

        :param tab_name: name of the tab
        """

        self.setCurrentIndex(self.get_index_by_tab_name(tab_name))

    def set_current_editor_by_file_name(self, file_name):
        """
        Sets the current editor

        :param file_name: name of the file the pipeline was last saved to
        """

        self.setCurrentIndex(self.get_index_by_filename(file_name))

    def set_current_editor_by_editor(self, editor):
        """
        Sets the current editor

        :param editor: editor in the tab that should be made current
        """

        self.setCurrentIndex(self.get_index_by_editor(editor))

    def get_editor_by_index(self, idx):
        """
        Gets the instance of an editor from its index in the editors

        :param idx: index of the editor
        :return: the editor corresponding to the index
        """

        if idx in range(self.count()-1):  # last tab has "add tab" button, no editor
            return self.widget(idx)

    def get_current_editor(self):
        """
        Gets the instance of the current editor

        :return: the current editor
        """

        return self.get_editor_by_index(self.currentIndex())

    def get_editor_by_tab_name(self, tab_name):
        """
        Gets the instance of an editor from its tab name

        :param tab_name: name of the tab
        :return: the editor corresponding to the tab name
        """

        return self.get_editor_by_index(self.get_index_by_tab_name(tab_name))

    def get_editor_by_file_name(self, file_name):
        """
        Gets the instance of an editor from its file name

        :param file_name: name of the file the pipeline was last saved to
        :return: the editor corresponding to the file name
        """

        return self.get_editor_by_index(self.get_index_by_filename(file_name))

    def get_tab_name_by_index(self, idx):
        """
        Gets the tab name of the editor at the given index.
        Trailing " *" and ampersand ("&") characters are removed.

        :param idx: index of the editor
        :return: the tab name corresponding to the index
        """

        if idx in range(self.count()-1):  # last tab has "add tab" button, no tab name
            tab_name = self.tabText(idx).replace("&", "", 1)  # remove Qt keyboard shortcut indicator
            if tab_name[-2:] == " *":
                tab_name = tab_name[:-2]

            return tab_name

    def get_current_tab_name(self):
        """
        Gets the tab name of the editor in the current tab.
        Trailing " *" and ampersand ("&") characters are removed.

        :return: the current tab name
        """

        return self.get_tab_name_by_index(self.currentIndex())

    def get_filename_by_index(self, idx):
        """
        Gets the relative path to the file the pipeline in the editor at the given index has been last saved to.
        If the pipeline has never been saved, returns the title of the tab.

        :param idx: index of the editor
        :return: the file name corresponding to the index
        """

        editor = self.get_editor_by_index(idx)
        if editor is not None:
            return editor.get_current_filename()

    def get_current_filename(self):
        """
        Gets the relative path to the file the pipeline in the current editor has been last saved to.
        If the pipeline has never been saved, returns the title of the tab.

        :return: the filename of the current editor
        """

        return self.get_filename_by_index(self.currentIndex())

    def get_index_by_tab_name(self, tab_name):
        """
        Gets the index of the editor corresponding to the given tab name

        :param tab_name: name of the tab with the searched pipeline
        :return: the index corresponding to the tab name
        """

        for idx in range(self.count()-1):
            if self.get_tab_name_by_index(idx) == tab_name:
                return idx

    def get_index_by_filename(self, filename):
        """
        Gets the index of the first editor corresponding to the given pipeline filename

        :param filename: filename of the searched pipeline
        :return: the index corresponding to the file name
        """

        if filename:
            filename = os.path.relpath(filename)  # we always store file names as relative paths

            for idx in range(self.count()-1):
                if self.get_filename_by_index(idx) == filename:
                    return idx

    def get_index_by_editor(self, editor):
        """
        Gets the index of the editor corresponding to the given editor

        :param editor: searched pipeline editor
        :return: the index corresponding to the editor
        """

        for idx in range(self.count()-1):
            if self.get_editor_by_index(idx) == editor:
                return idx

    def get_current_pipeline(self):
        """
        Gets the instance of the current pipeline

        :return: the pipeline of the current editor
        """

        return self.get_current_editor().scene.pipeline

    def save_pipeline(self, new_file_name=None):
        """
        Saves the pipeline of the current editor

        """

        if new_file_name is None:
            # Doing a "Save as" action
            new_file_name = os.path.basename(self.get_current_editor().save_pipeline())

            if new_file_name and os.path.basename(self.get_current_filename()) != new_file_name:
                self.setTabText(self.currentIndex(), new_file_name)
        else:
            # Saving the current pipeline
            pipeline = self.get_current_pipeline()
            posdict = dict([(key, (value.x(), value.y())) \
                            for key, value in six.iteritems(self.get_current_editor().scene.pos)])
            old_pos = pipeline.node_position
            pipeline.node_position = posdict
            save_pipeline(pipeline, new_file_name)
            self.get_current_editor()._pipeline_filename = unicode(new_file_name)
            pipeline.node_position = old_pos

            self.pipeline_saved.emit(new_file_name)
            self.setTabText(self.currentIndex(), os.path.basename(new_file_name))

    def load_pipeline(self, filename=None):
        """
        Loads a new pipeline

        :param filename: not None only when this method is called from "open_sub_pipeline"
        """

        current_tab_not_empty = len(self.get_current_editor().scene.pipeline.nodes.keys()) > 1
        new_tab_opened = False

        if filename is None:
            # Open new tab if the current PipelineEditor is not empty
            if current_tab_not_empty:
                self.new_tab()  # create new tab with new editor and make it current
                working_index = self.currentIndex()
                new_tab_opened = True

            filename = self.get_current_editor().load_pipeline('', False)  # get only the file name to load

        if filename:
            # Check if this pipeline is already open
            existing_pipeline_tab = self.get_index_by_filename(filename)

            if existing_pipeline_tab is not None:
                self.setCurrentIndex(existing_pipeline_tab)
            else:  # we need to actually load the pipeline
                if current_tab_not_empty and not new_tab_opened:
                    self.new_tab()
                    new_tab_opened = True

                working_index = self.currentIndex()
                editor = self.get_editor_by_index(working_index)
                filename = editor.load_pipeline(filename)  # actually load the pipeline
                if filename:
                    self.setTabText(working_index, os.path.basename(filename))
                    self.update_scans_list()
                    return  # success

        if new_tab_opened:  # if we're still here, something went wrong. clean up.
            self.close_tab(working_index)

    def save_pipeline_parameters(self):
        """
        Saves the pipeline parameters of the current editor

        """

        self.get_current_editor().save_pipeline_parameters()

    def load_pipeline_parameters(self):
        """
        Loads parameters to the pipeline of the current editor

        """

        self.get_current_editor().load_pipeline_parameters()

    def emit_node_clicked(self, node_name, process):
        """
        Emits a signal when a node is clicked

        :param node_name: node name
        :param process: process of the corresponding node
        """

        self.node_clicked.emit(node_name, process)

    def emit_switch_clicked(self, node_name, switch):
        """
        Emits a signal when a switch is clicked

        :param node_name: node name
        :param switch: process of the corresponding node
        """

        self.switch_clicked.emit(node_name, switch)

    def emit_pipeline_saved(self, filename):
        """
        Emits a signal when a pipeline is saved

        :param filename: file name of the pipeline
        """

        self.setTabText(self.currentIndex(), os.path.basename(filename))
        self.pipeline_saved.emit(filename)

    def update_pipeline_editors(self, editor):
        """
        Update editors

        :param editor: editor
        """

        self.update_history(editor)
        self.update_scans_list()

    def update_history(self, editor):
        """
        Updates undo/redo history of an editor

        :param editor: editor
        """

        self.undos[editor] = editor.undos
        self.redos[editor] = editor.redos
        self.setTabText(self.currentIndex(), self.get_current_tab_name() + " *")  # make sure the " *" is there

    def reset_pipeline(self):
        """
        Resets the pipeline of the current editor
        """

        self.get_current_editor()._reset_pipeline()

    def update_scans_list(self):
        """
        Updates the list of database scans in every editor
        """

        for i in range(self.count()-1):
            pipeline = self.widget(i).scene.pipeline
            if hasattr(pipeline, "nodes"):
                for node_name, node in pipeline.nodes.items():
                    if node_name == "":
                        for plug_name, plug in node.plugs.items():
                            if plug_name == "database_scans":
                                node.set_plug_value(plug_name, self.scan_list)

    def open_sub_pipeline(self, sub_pipeline):
        """
        Opens a sub-pipeline in a new tab.

        :param sub_pipeline: the pipeline to open
        """

        # Reading the process configuration file
        config = Config()
        with open(os.path.join(config.get_mia_path(), 'properties', 'process_config.yml'), 'r') as stream:
            try:
                dic = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
                dic = {}

        sub_pipeline_name = sub_pipeline.name

        # get_path returns a list that is the package path to the sub_pipeline file
        sub_pipeline_list = get_path(sub_pipeline_name, dic['Packages'])
        sub_pipeline_name = sub_pipeline_list.pop()

        # Finding the real sub-pipeline filename
        sub_pipeline_filename = find_filename(dic['Paths'], sub_pipeline_list, sub_pipeline_name)
        self.load_pipeline(sub_pipeline_filename)

    def open_filter(self, node_name):
        """
        Opens a filter widget

        :param node_name: name of the corresponding node
        """
        node = self.get_current_pipeline().nodes[node_name]
        self.filter_widget = FilterWidget(self.project, node_name, node, self)
        self.filter_widget.show()

    def export_to_db_scans(self, node_name):
        """
        Exports the input of a filter to "database_scans" plug

        :param node_name:
        """

        # If database_scans is already a pipeline global input, the plug cannot be
        # exported. A link as to be added between database_scans and the input of the filter.
        if 'database_scans' in self.get_current_pipeline().user_traits().keys():
            self.get_current_pipeline().add_link('database_scans->{0}.input'.format(node_name))
        else:
            self.get_current_pipeline().export_parameter(
                node_name, 'input',
                pipeline_parameter='database_scans')
        self.get_current_editor().scene.update_pipeline()

    def check_modifications(self, current_index):
        """
        Checks if the nodes of the current pipeline have been modified

        """

        # If the user click on the last tab (with the '+'), it will throw an AttributeError
        try:
            self.widget(current_index).check_modifications()
        except AttributeError:
            pass

    def has_pipeline_nodes(self):
        """
        Checks if any of the pipelines in the editor tabs have pipeline nodes

        :return: True or False depending on if there are nodes in the editors
        """
        for idx in range(self.count()):
            p_e = self.widget(idx)
            if hasattr(p_e, 'scene'):
                # if the widget is a tab editor
                if p_e.scene.pipeline.nodes[''].plugs:
                    return True

        return False


class PipelineEditor(PipelineDevelopperView):
    """
    View to edit a pipeline graphically

    Attributes:
        - project: current project in the software
        - main_window: main window of the software
        - undos: list of actions to undo
        - redos: list of actions to redo

    Methods:
        - dragEnterEvent: event handler when the mouse enters the widget
        - dragMoveEvent: event handler when the mouse moves in the widget
        - dropEvent: event handler when something is dropped in the widget
        - find_process: finds the dropped process in the system's paths
        - update_history: updates the history for undos and redos
        - add_process: adds a process to the pipeline
        - del_node: deletes a node
        - _release_grab_link: method called when a link is released
        - add_link: add a link between two nodes
        - _del_link: deletes a link
        - update_node_name: updates a node name
        - update_plug_value: updates a plug value
        - _export_plug: export a plug to a pipeline global input or output
        - export_node_plugs: exports all the plugs of a node
        - _remove_plug: removes a plug
        - save_pipeline: saves the pipeline
        - check_modifications: checks if the nodes of the pipeline have been modified
        - get_current_filename: returns the relative path the pipeline was last saved to. Empty if never saved.
    """

    pipeline_saved = QtCore.pyqtSignal(str)
    pipeline_modified = QtCore.pyqtSignal(PipelineDevelopperView)

    def __init__(self, project, main_window):
        """
        Initialization of the PipelineEditor

        :param project: current project in the software
        """

        PipelineDevelopperView.__init__(self, pipeline=None, allow_open_controller=True,
                                        show_sub_pipelines=True, enable_edition=True)

        self.project = project
        self.main_window = main_window

        # Undo/Redo
        self.undos = []
        self.redos = []

    def dragEnterEvent(self, event):
        """
        Event handler when the mouse enters the widget

        :param event: event
        """

        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dragMoveEvent(self, event):
        """
        Event handler when the mouse moves in the widget

        :param event: event
        """

        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dropEvent(self, event):
        """
        Event handler when something is dropped in the widget
        :param event: event

        """

        if event.mimeData().hasFormat('component/name'):
            self.click_pos = QtGui.QCursor.pos()
            path = bytes(event.mimeData().data('component/name'))
            self.find_process(path.decode('utf8'))

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
                    QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
                    self.add_process(instance)
                    QtGui.QApplication.restoreOverrideCursor()

    def update_history(self, history_maker, from_undo, from_redo):
        """
        Updates the history for undos and redos
        This method is called after each action in the PipelineEditor.

        :param history_maker: list that contains information about what has been done
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        """

        if from_undo:
            self.redos.append(history_maker)
        else:
            self.undos.append(history_maker)
            # If the action does not come from an undo or a redo,
            # the redos has to be cleared
            if not from_redo:
                self.redos.clear()

        self.pipeline_modified.emit(self)

    def add_process(self, class_process, node_name=None, from_undo=False, from_redo=False, links=[]):
        """
        Adds a process to the pipeline

        :param class_process: process class's name (str)
        :param node_name: name of the corresponding node (using when undo/redo) (str)
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        :param links: list of links (using when undo/redo)
        """

        pipeline = self.scene.pipeline
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

        if hasattr(process, 'use_project') and process.use_project:
            process.project = self.project

        pipeline.add_process(node_name, process)

        # Capsul update
        node = pipeline.nodes[node_name]
        gnode = self.scene.add_node(node_name, node)
        gnode.setPos(self.mapToScene(self.mapFromGlobal(self.click_pos)))

        # If the process is added from a undo, all the links that were connected
        # to the corresponding node has to be reset
        for link in links:
            source = link[0]
            dest = link[1]
            active = link[2]
            weak = link[3]
            self.scene.add_link(source, dest, active, weak)
            # Writing a string to represent the link
            source_parameters = ".".join(source)
            dest_parameters = ".".join(dest)
            link_to_add = "->".join((source_parameters, dest_parameters))
            self.scene.pipeline.add_link(link_to_add)
            self.scene.update_pipeline()

        # For history
        history_maker = ["add_process"]

        if from_undo:
            # Adding the arguments to make the redo correctly
            history_maker.append(node_name)
        else:
            # Adding the arguments to make the undo correctly
            history_maker.append(node_name)
            history_maker.append(class_process)

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage("Node {0} has been added.".format(node_name))

    def del_node(self, node_name=None, from_undo=False, from_redo=False):
        """
        Deletes a node

        :param node_name: name of the corresponding node (using when undo/redo) (str)
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        """

        pipeline = self.scene.pipeline
        if not node_name:
            node_name = self.current_node_name
        node = pipeline.nodes[node_name]

        # Collecting the links from the node that is being deleted
        links = []
        for plug_name, plug in node.plugs.items():
            if plug.output:
                for link_to in plug.links_to:
                    (dest_node_name, dest_parameter, dest_node, dest_plug,
                     weak_link) = link_to
                    active = plug.activated

                    # Looking for the name of dest_plug in dest_node
                    dest_plug_name = None
                    for plug_name_d, plug_d in dest_node.plugs.items():
                        if plug_d == dest_plug:
                            dest_plug_name = plug_name_d
                            break

                    link_to_add = [(node_name, plug_name)]
                    link_to_add.append((dest_node_name, dest_plug_name))
                    link_to_add.append(active)
                    link_to_add.append(weak_link)

                    links.append(link_to_add)
            else:
                for link_from in plug.links_from:
                    (source_node_name, source_parameter, source_node, source_plug,
                     weak_link) = link_from
                    active = plug.activated

                    # Looking for the name of source_plug in source_node
                    source_plug_name = None
                    for plug_name_d, plug_d in source_node.plugs.items():
                        if plug_d == source_plug:
                            source_plug_name = plug_name_d
                            break

                    link_to_add = [(source_node_name, source_plug_name)]
                    link_to_add.append((node_name, plug_name))
                    link_to_add.append(active)
                    link_to_add.append(weak_link)

                    links.append(link_to_add)

        # Calling the original method
        PipelineDevelopperView.del_node(self, node_name)

        # For history
        history_maker = ["delete_process", node_name, node.process, links]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage("Node {0} has been deleted.".format(node_name))

    def _release_grab_link(self, event, ret=False):
        """
        Method called when a link is released
        :param event: mouse event corresponding to the release
        :param ret: boolean that is set to True in the original method to return the link
        """

        # Calling the original method
        link = PipelineDevelopperView._release_grab_link(self, event, ret=True)

        # For history
        history_maker = ["add_link", link]

        self.update_history(history_maker, from_undo=False, from_redo=False)

        self.main_window.statusBar().showMessage('Link {0} has been added.'.format(link))

    def add_link(self, source, dest, active, weak, from_undo=False, from_redo=False):
        """
        Adds a link between two nodes.

        :param source: tuple containing the node and plug source names
        :param dest: tuple containing the node and plug destination names
        :param active: boolean that is True if the link is activated
        :param weak: boolean that is True if the link is weak
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        """

        self.scene.add_link(source, dest, active, weak)

        # Writing a string to represent the link
        source_parameters = ".".join(source)
        dest_parameters = ".".join(dest)
        link = "->".join((source_parameters, dest_parameters))

        self.scene.pipeline.add_link(link)
        self.scene.update_pipeline()

        # For history
        history_maker = ["add_link", link]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage('Link {0} has been added.'.format(link))

    def _del_link(self, link=None, from_undo=False, from_redo=False):
        """
        Deletes a link

        :param link: string representation of a link (e.g. "process1.out->process2.in")
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        """

        if not link:
            link = self._current_link
        else:
            self._current_link = link

        (source_node_name, source_plug_name, source_node,
         source_plug, dest_node_name, dest_plug_name, dest_node,
         dest_plug) = self.scene.pipeline.parse_link(link)

        (dest_node_name, dest_parameter, dest_node, dest_plug,
         weak_link) = list(source_plug.links_to)[0]

        active = source_plug.activated and dest_plug.activated

        # Calling the original method
        PipelineDevelopperView._del_link(self)

        # For history
        history_maker = ["delete_link", (source_node_name, source_plug_name),
                         (dest_node_name, dest_plug_name), active, weak_link]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage('Link {0} has been deleted.'.format(link))

    def update_node_name(self, old_node, old_node_name, new_node_name, from_undo=False, from_redo=False):
        """
        Updates a node name

        :param old_node: Node object to change
        :param old_node_name: original name of the node (str)
        :param new_node_name: new name of the node (str)
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        """

        pipeline = self.scene.pipeline

        # Removing links of the selected node and copy the origin/destination
        links_to_copy = []
        for source_parameter, source_plug \
                in six.iteritems(old_node.plugs):
            for (dest_node_name, dest_parameter, dest_node, dest_plug,
                 weak_link) in source_plug.links_to.copy():
                pipeline.remove_link(old_node_name + "." + source_parameter + "->"
                                     + dest_node_name + "." + dest_parameter)
                links_to_copy.append(("to", source_parameter, dest_node_name, dest_parameter))

            for (dest_node_name, dest_parameter, dest_node, dest_plug,
                 weak_link) in source_plug.links_from.copy():
                pipeline.remove_link(dest_node_name + "." + dest_parameter + "->"
                                     + old_node_name + "." + source_parameter)
                links_to_copy.append(("from", source_parameter, dest_node_name, dest_parameter))

        # Creating a new node with the new name and deleting the previous one
        pipeline.nodes[new_node_name] = pipeline.nodes[old_node_name]
        del pipeline.nodes[old_node_name]

        # Setting the same links as the original node
        for link in links_to_copy:

            if link[0] == "to":
                pipeline.add_link(new_node_name + "." + link[1] + "->"
                                  + link[2] + "." + link[3])
            elif link[0] == "from":
                pipeline.add_link(link[2] + "." + link[3] + "->"
                                  + new_node_name + "." + link[1])

        # Updating the pipeline
        pipeline.update_nodes_and_plugs_activation()

        # For history
        history_maker = ["update_node_name", pipeline.nodes[new_node_name], new_node_name, old_node_name]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage('Node name "{0}" has been changed to "{1}".'.format(old_node_name,
                                                                                                     new_node_name))

    def update_plug_value(self, node_name, new_value, plug_name, value_type, from_undo=False, from_redo=False):
        """
        Updates a plug value

        :param node_name: name of the node (str)
        :param new_value: new value to set to the plug
        :param plug_name: name of the plug to change (str)
        :param value_type: type of the new value
        :param from_undo: boolean that is True if the action has been made using an undo
        :param from_redo: boolean that is True if the action has been made using a redo
        """

        old_value = self.scene.pipeline.nodes[node_name].get_plug_value(plug_name)
        self.scene.pipeline.nodes[node_name].set_plug_value(plug_name, value_type(new_value))

        # For history
        history_maker = ["update_plug_value", node_name, old_value, plug_name, value_type]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage(
            'Plug "{0}" of node "{1}" has been changed to "{2}".'.format(plug_name, node_name, new_value))

    def _export_plug(self, pipeline_parameter=False, optional=None,
                     weak_link=None, from_undo=False, from_redo=False,
                     temp_plug_name=None):
        """
        Export a plug to a pipeline global input or output

        :param pipeline_parameter: name of the pipeline input/output
        :param optional: True if the plug is optional
        :param weak_link: True if the link is weak
        :param from_undo: True if this method is called from an undo action
        :param from_redo: True if this method is called from a redo action
        :param temp_plug_name: tuple containing (the name of the node, the name of the plug) to export
        """
        # Bug: the first parameter (here pipeline_parameter) cannot be None
        # even if we write pipeline_parameter=None in the line above, it will be False...

        if temp_plug_name is None:
            dial = self._PlugEdit()
            dial.name_line.setText(self._temp_plug_name[1])
            dial.optional.setChecked(self._temp_plug.optional)
            temp_plug_name = self._temp_plug_name

            res = dial.exec_()
        else:
            res = True

        if res:
            if not pipeline_parameter:
                pipeline_parameter = str(dial.name_line.text())

            if optional is None:
                optional = dial.optional.isChecked()

            if weak_link is None:
                weak_link = dial.weak.isChecked()

            try:
                self.scene.pipeline.export_parameter(
                    temp_plug_name[0], temp_plug_name[1],
                    pipeline_parameter=pipeline_parameter,
                    is_optional=optional,
                    weak_link=weak_link)
            except TraitError:
                print("Cannot export {0}.{1} plug".format(temp_plug_name[0], temp_plug_name[1]))

            '''self.scene.pipeline.export_parameter(
                temp_plug_name[0], temp_plug_name[1],
                pipeline_parameter=pipeline_parameter,
                is_optional=optional,
                weak_link=weak_link)'''  # Uncomment to generate the error

            self.scene.update_pipeline()

        # For history
        history_maker = ["export_plug", ('inputs', pipeline_parameter), pipeline_parameter,
                         optional, weak_link]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage("Plug {0} has been exported.".format(temp_plug_name[1]))

    def export_node_plugs(self, node_name, inputs=True, outputs=True,
                          optional=False, from_undo=False, from_redo=False):
        """
        Exports all the plugs of a node

        :param node_name: node name
        :param inputs: True if the inputs have to be exported
        :param outputs: True if the outputs have to be exported
        :param optional: True if the optional plugs have to be exported
        :param from_undo: True if this method is called from an undo action
        :param from_redo: True if this method is called from a redo action
        """

        pipeline = self.scene.pipeline
        node = pipeline.nodes[node_name]
        parameter_list = []
        for parameter_name, plug in six.iteritems(node.plugs):
            if parameter_name in ("nodes_activation", "selection_changed"):
                continue
            if (((node_name, parameter_name) not in pipeline.do_not_export and
                ((outputs and plug.output and not plug.links_to) or
                    (inputs and not plug.output and not plug.links_from)) and
                 (optional or not node.get_trait(parameter_name).optional))):
                try:
                    pipeline.export_parameter(node_name, parameter_name)
                    parameter_list.append(parameter_name)
                except TraitError:
                    print("Cannot export {0}.{1} plug".format(node_name, parameter_name))

        # For history
        history_maker = ["export_plugs", parameter_list, node_name]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage("Plugs {0} have been exported.".format(str(parameter_list)))

    def _remove_plug(self, _temp_plug_name=None, from_undo=False, from_redo=False, from_export_plugs=False):
        """
        Removes a plug

        :param _temp_plug_name: tuple containing (the name of the node, the name of the plug) to remove
        :param from_undo: True if this method is called from an undo action
        :param from_redo: True if this method is called from a redo action
        :param from_export_plugs: True if this method is called from a "from_export_plugs" undo or redo action
        """
        if not _temp_plug_name:
            _temp_plug_name = self._temp_plug_name

        if _temp_plug_name[0] in ('inputs', 'outputs'):
            plug_name = _temp_plug_name[1]
            plug = self.scene.pipeline.pipeline_node.plugs[plug_name]
            optional = plug.optional
            new_temp_plugs = []  # contains the plugs that are connected to the input or output plug
            for link in plug.links_to:
                temp_plug = (link[0], link[1])
                new_temp_plugs.append(temp_plug)
            for link in plug.links_from:
                temp_plug = (link[0], link[1])
                new_temp_plugs.append(temp_plug)

            # To avoid the "_items" bug: setting the has_items attribute of the trait's handler to False
            node = self.scene.pipeline.nodes['']
            source_trait = node.get_trait(plug_name)
            if source_trait.handler.has_items:
                source_trait.handler.has_items = False

            self.scene.pipeline.remove_trait(_temp_plug_name[1])
            self.scene.update_pipeline()

            # if not from_undo and not from_redo:
            if not from_export_plugs:
                # For history
                history_maker = ["remove_plug", _temp_plug_name, new_temp_plugs, optional]

                self.update_history(history_maker, from_undo, from_redo)

                self.main_window.statusBar().showMessage("Plug {0} has been removed.".format(_temp_plug_name[1]))

    def check_modifications(self):
        """
        Checks if the nodes of the pipeline have been modified
        """

        pipeline = self.scene.pipeline
        config = Config()

        # List to store the removed links
        removed_links = []

        for node_name, node in pipeline.nodes.items():
            # Only if the node is a pipeline node ?
            if node_name and isinstance(node, PipelineNode):
                sub_pipeline_process = node.process
                current_process_id = sub_pipeline_process.id

                # Reading the process configuration file
                with open(os.path.join(config.get_mia_path(), 'properties', 'process_config.yml'), 'r') as stream:
                    try:
                        dic = yaml.load(stream)
                    except yaml.YAMLError as exc:
                        print(exc)
                        dic = {}

                sub_pipeline_name = sub_pipeline_process.name

                # get_path returns a list that is the package path to the sub_pipeline file
                sub_pipeline_list = get_path(sub_pipeline_name, dic['Packages'])
                sub_pipeline_name = sub_pipeline_list.pop()

                # Finding the real sub-pipeline filename
                sub_pipeline_filename = find_filename(dic['Paths'], sub_pipeline_list, sub_pipeline_name)

                saved_process = get_process_instance(sub_pipeline_filename)

                current_inputs = list(sub_pipeline_process.get_inputs().keys())
                current_outputs = list(sub_pipeline_process.get_outputs().keys())
                saved_inputs = list(saved_process.get_inputs().keys())
                saved_outputs = list(saved_process.get_outputs().keys())

                new_inputs = [item for item in saved_inputs if item not in current_inputs]
                new_outputs = [item for item in saved_outputs if item not in current_outputs]
                removed_inputs = [item for item in current_inputs if item not in saved_inputs]
                removed_outputs = [item for item in current_outputs if item not in saved_outputs]

                if new_inputs or new_outputs or removed_inputs or removed_outputs:

                    # Checking the links of the node
                    link_to_del = set()
                    for link, glink in six.iteritems(self.scene.glinks):
                        if link[0][0] == node_name or link[1][0] == node_name:
                            self.scene.removeItem(glink)
                            link_to_del.add((link, glink))
                    for link, glink in link_to_del:
                        del self.scene.glinks[link]

                    # Creating a new node
                    new_node = saved_process.pipeline_node
                    new_node.name = node_name
                    new_node.pipeline = pipeline
                    saved_process.parent_pipeline = weak_proxy(pipeline)
                    pipeline.nodes[node_name] = new_node

                    # Creating a new graphical node
                    gnode = NodeGWidget(
                        node_name, new_node.plugs, pipeline,
                        sub_pipeline=saved_process, process=saved_process,
                        colored_parameters=self.scene.colored_parameters,
                        logical_view=self.scene.logical_view, labels=self.scene.labels)

                    # Setting the new node to the same position as the previous one
                    pos = self.scene.pos.get(node_name)
                    gnode.setPos(pos)

                    # Removing the old node
                    self.scene.removeItem(self.scene.gnodes[node_name])
                    del self.scene.gnodes[node_name]

                    # Adding the new node to the scene
                    self.scene.gnodes[node_name] = gnode
                    self.scene.addItem(gnode)

                    for link, glink in link_to_del:
                        source = link[0]
                        dest = link[1]
                        if source[0] == 'inputs':
                            link_plug = source[1]
                            source = ('', link_plug)
                        if dest[0] == 'outputs':
                            link_plug = dest[1]
                            dest = ('', link_plug)

                        # Writing a string to represent the link
                        source_parameters = ".".join(source)
                        dest_parameters = ".".join(dest)
                        pipeline_link = "->".join((source_parameters, dest_parameters))

                        # Checking if a connected plug has been deleting
                        if dest[0] == node_name and dest[1] in removed_inputs:
                            removed_links.append(pipeline_link)
                            continue

                        if source[0] == node_name and source[1] in removed_outputs:
                            removed_links.append(pipeline_link)
                            continue

                        # Adding the link
                        self.scene.pipeline.add_link(pipeline_link)
                        self.scene.add_link(source, dest, True, False)

                    self.scene.update_pipeline()

        if removed_links:
            dialog_text = 'Pipeline {0} has been updated.\nRemoved links:'.format(node_name)
            for removed_link in removed_links:
                dialog_text += '\n{0}'.format(removed_link)

            pop_up = QtWidgets.QMessageBox()
            pop_up.setIcon(QtWidgets.QMessageBox.Warning)
            pop_up.setText(dialog_text)
            pop_up.setWindowTitle("Warning: links have been removed")
            pop_up.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            pop_up.exec_()

    def save_pipeline(self, filename=None):
        """
        Saves the pipeline

        :return: the pipeline file name
        """
        config = Config()
        if not filename:
            pipeline = self.scene.pipeline
            folder = os.path.abspath(os.path.join(config.get_mia_path(), 'processes', 'User_processes'))
            filename = QtWidgets.QFileDialog.getSaveFileName(
                None, 'Save the pipeline', folder,
                'Compatible files (*.py);; All (*)')[0]
            if not filename:                         # save widget was cancelled by the user
                return ''
            if os.path.splitext(filename)[1] == '':  # which means no extension
                filename += '.py'
            elif os.path.splitext(filename)[1] != '.py':
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText('The pipeline will be saved with a' +
                            ' ".py" extension instead of {0}'.format(os.path.splitext(filename)[1]))
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()
                filename = os.path.splitext(filename)[0] + '.py'
        if filename:
            posdict = dict([(key, (value.x(), value.y())) \
                            for key, value in six.iteritems(self.scene.pos)])
            old_pos = pipeline.node_position
            pipeline.node_position = posdict
            # pipeline_tools.save_pipeline(pipeline, filename)
            save_pipeline(pipeline, filename)
            self._pipeline_filename = unicode(filename)
            pipeline.node_position = old_pos

            self.pipeline_saved.emit(filename)
            return filename

    def get_current_filename(self):
        """
        Returns the relative path the pipeline was last saved to. Empty if never saved.

        :return: the current pipeline file name
        """
        if hasattr(self, '_pipeline_filename') and self._pipeline_filename:
            return os.path.relpath(self._pipeline_filename)
        else:
            return ''


def save_pipeline(pipeline, filename):
    '''
    Save the pipeline either in XML or .py source file
    '''
    from capsul.pipeline.xml import save_xml_pipeline
    # from capsul.pipeline.python_export import save_py_pipeline

    formats = {'.py': save_py_pipeline,
               '.xml': save_xml_pipeline}

    saved = False
    for ext, writer in six.iteritems(formats):
        if filename.endswith(ext):
            writer(pipeline, filename)
            saved = True
            break
    if not saved:
        # fallback to XML
        save_py_pipeline(pipeline, filename)


# Copy from python_export.py of CAPSUL's API

def save_py_pipeline(pipeline, py_file):
    """
    Save a pipeline in an Python source file

    Parameters
    ----------
    pipeline: Pipeline instance
        pipeline to save
    py_file: str
        .py file to save the pipeline in
    """
    # imports are done locally to avoid circular imports
    from capsul.api import Process, Pipeline
    from capsul.pipeline.pipeline_nodes import ProcessNode, Switch, \
        OptionalOutputSwitch
    from capsul.pipeline.process_iteration import ProcessIteration
    from capsul.process.process import NipypeProcess
    from traits.api import Undefined

    def _write_process(process, pyf, name, enabled):
        mod = process.__module__
        # if process is a function with XML decorator, we need to
        # retreive the original function name.
        func = getattr(process, '_function', None)
        if func:
            classname = func.__name__
        else:
            classname = process.__class__.__name__
        if isinstance(process, NipypeProcess):
            # procname = '.'.join((process.__class__.__module__, process.__class__.__name__))
            procname = '.'.join((process._nipype_module, process._nipype_class))
        else:
            procname = '.'.join((mod, classname))
        print('        self.add_process("%s", "%s")' % (name, procname),
              file=pyf)
        #if isinstance(process, NipypeProcess):
            ## WARNING: not sure I'm doing the right things for nipype. To be
            ## fixed if needed.
            #for param in process.inputs_to_copy:
                #elem = ET.SubElement(procnode, 'nipype')
                #elem.set('name', param)
                #if param in proces.inputs_to_clean:
                    #elem.set('copyfile', 'discard')
                #else:
                    #elem.set('copyfile', 'true')
                #np_input = getattr(process._nipype_interface.inputs, param)
                #if np_input:
                    #use_default = getattr(np_input, 'usedefault', False) # is it that?
                    #if use_default:
                        #elem.set('use_default', 'true')
            #for param, np_input in \
                    #six.iteritems(process._nipype_interface.inputs.__dict__):
                #use_default = getattr(np_input, 'usedefault', False) # is it that?
                #if use_default and param not in process.inputs_to_copy:
                    #elem = ET.SubElement(procnode, 'nipype')
                    #elem.set('name', param)
                    #elem.set('use_default', 'true')

    def _write_iteration(process_iter, pyf, name, enabled):
        process = process_iter.process
        mod = process.__module__
        # if process is a function with XML decorator, we need to
        # retreive the original function name.
        func = getattr(process, '_function', None)
        if func:
            classname = func.__name__
        else:
            classname = process.__class__.__name__
        procname = '.'.join((mod, classname))

        iteration_params = ', '.join(process_iter.iterative_parameters)
        # TODO: optional plugs, non-exported plugs...
        print('        self.add_iterative_process("%s", "%s", '
              'iterative_plugs=%s)'
              % (name, procname, process_iter.iterative_parameters),
              file=pyf)

    def _write_switch(switch, pyf, name, enabled):
        inputs = set()
        outputs = []
        optional = []
        opt_in = []
        for plug_name, plug in six.iteritems(switch.plugs):
            if plug.output:
                outputs.append(plug_name)
                if plug.optional:
                    optional.append(plug_name)
            else:
                name_parts = plug_name.split("_switch_")
                if len(name_parts) == 2 \
                        and name_parts[0] not in inputs:
                    inputs.add(name_parts[0])
                    if plug.optional:
                        opt_in.append(name_parts[0])
        optional_p = ''
        if len(optional) != 0:
            optional_p = ', make_optional=%s' % repr(optional)
        value_p = ''
        inputs = list(inputs)
        if switch.switch != inputs[0]:
            value_p = ', switch_value=%s' % repr(switch.switch)
        print('        self.add_switch("%s", %s, %s%s%s, export_switch=False)'
              % (name, repr(inputs), repr(outputs), optional_p, value_p),
              file=pyf)

    def _write_optional_output_switch(switch, pyf, name, enabled):
        output = None
        input = None
        for plug_name, plug in six.iteritems(switch.plugs):
            if plug.output:
                output = plug_name
            else:
                name_parts = plug_name.split("_switch_")
                if len(name_parts) == 2 and name_parts[0] != '_none':
                    input = name_parts[0]
        if not name and output:
            name = output
        if not output or output == name:
            print('        self.add_optional_output_switch("%s", "%s")'
                  % (name, input), file=pyf)
        else:
            print('        self.add_optional_output_switch("%s", "%s", "%s")'
                  % (name, input, output), file=pyf)

    def _write_processes(pipeline, pyf):
        print('        # nodes', file=pyf)
        for node_name, node in six.iteritems(pipeline.nodes):
            if node_name == "":
                continue
            if isinstance(node, OptionalOutputSwitch):
                _write_optional_output_switch(node, pyf, node_name,
                                              node.enabled)
            elif isinstance(node, Switch):
                _write_switch(node, pyf, node_name, node.enabled)
            elif isinstance(node, ProcessNode) \
                    and isinstance(node.process, ProcessIteration):
                _write_iteration(node.process, pyf, node_name, node.enabled)
            else:
                _write_process(node.process, pyf, node_name, node.enabled)

    def _write_processes_selections(pipeline, pyf):
        selection_parameters = []
        if hasattr(pipeline, 'processes_selection'):
            print('\n        # processes selection', file=pyf)
            for selector_name, groups \
                    in six.iteritems(pipeline.processes_selection):
                print('        self.add_processes_selection("%s", %s)'
                      % (selector_name, repr(groups)), file=pyf)
        return selection_parameters

    def _write_export(pipeline, pyf, param_name):
        plug = pipeline.pipeline_node.plugs[param_name]
        if plug.output:
            link = list(plug.links_from)[0]
        else:
            link = list(plug.links_to)[0]
        node_name, plug_name = link[:2]
        if param_name == plug_name:
            param_name = ''
        else:
            param_name = ', "%s"' % param_name
        weak_link = ''
        if link[-1]:
            weak_link = ', weak_link=True'
        print('        self.export_parameter("%s", "%s"%s%s)'
              % (node_name, plug_name, param_name, weak_link), file=pyf)
        return node_name, plug_name

    def _write_links(pipeline, pyf):
        exported = set()
        print('\n        # links', file=pyf)
        for node_name, node in six.iteritems(pipeline.nodes):
            for plug_name, plug in six.iteritems(node.plugs):
                if (node_name == "" and not plug.output) \
                        or (node_name != "" and plug.output):
                    links = plug.links_to
                    for link in links:
                        exported_plug = None
                        if node_name == "":
                            src = plug_name
                            if src not in exported:
                                exported_plug = _write_export(pipeline, pyf,
                                                              src)
                                exported.add(src)
                        else:
                            src = "%s.%s" % (node_name, plug_name)
                        if link[0] == "":
                            dst = link[1]
                            if dst not in exported:
                                exported_plug = _write_export(pipeline, pyf,
                                                              dst)
                                exported.add(dst)
                        else:
                            dst = "%s.%s" % (link[0], link[1])
                        if not exported_plug \
                                or '.'.join(exported_plug) not in (src, dst):
                            weak_link = ''
                            if link[-1]:
                                weak_link = ', weak_link=True'
                            print('        self.add_link("%s->%s"%s)'
                                  % (src, dst, weak_link), file=pyf)

    def _write_steps(pipeline, pyf):
        steps = pipeline.trait('pipeline_steps')
        if steps and getattr(pipeline, 'pipeline_steps', None):
            print('\n        # pipeline steps', file=pyf)
            for step_name, step \
                    in six.iteritems(pipeline.pipeline_steps.user_traits()):
                enabled = getattr(pipeline.pipeline_steps, step_name)
                if not enabled:
                    step_node.set('enabled', 'false')
                nodes = step.nodes
                print('        self.add_pipeline_step("%s", %s)'
                      % (step_name, repr(nodes)), file=pyf)

    def _write_nodes_positions(pipeline, pyf):
        node_position = getattr(pipeline, "node_position", None)
        if node_position:
            print('\n        # nodes positions', file=pyf)
            print('        self.node_position = {', file=pyf)
            for node_name, pos in six.iteritems(pipeline.node_position):
                if not isinstance(pos, (list, tuple)):
                    # pos is probably a QPointF
                    pos = (pos.x(), pos.y())
                print('            "%s": %s,' % (node_name, repr(pos)),
                      file=pyf)
            print('        }', file=pyf)
        if hasattr(pipeline, "scene_scale_factor"):
            print('        self.scene_scale_factor = %s'
                  % repr(pipeline.scene_scale_factor), file=pyf)

    def _write_doc(pipeline, pyf):
        if hasattr(pipeline, "__doc__"):
            docstr = pipeline.__doc__
            if docstr == Pipeline.__doc__:
                docstr = ""  # don't use the builtin Pipeline help
            else:
                # remove automatically added doc
                splitdoc = docstr.split('\n')
                notepos = [i for i, x in enumerate(splitdoc[:-2])
                              if x.endswith('.. note::')]
                autodocpos = None
                if notepos:
                    for i in notepos:
                        if splitdoc[i+2].find(
                                "* Type '{0}.help()'".format(
                                    pipeline.__class__.__name__)) != -1:
                            autodocpos = i
                if autodocpos is not None:
                    # strip empty trailing lines
                    while autodocpos >= 1 \
                            and splitdoc[autodocpos - 1].strip() == '':
                        autodocpos -= 1
                    docstr = '\n'.join(splitdoc[:autodocpos]) + '\n'
            if docstr.strip() == '':
                docstr = ''
            if docstr:
                doc = docstr.split('\n')
                docstr = '\n'.join([repr(x)[1:-1] for x in doc])
                print('    \"\"\"%s    \"\"\"' % docstr, file=pyf)

    def _write_values(pipeline, pyf):
        first = True
        for param_name, trait in six.iteritems(pipeline.user_traits()):
            if param_name not in pipeline.pipeline_node.plugs:
                continue
            # default cannot be set after trait creation
            #if trait.default:
                #if first:
                    #first = False
                    #print('\n        # default and initial values', file=pyf)
                #print('        self.trait("%s").default = %s'
                      #% (param_name, repr(trait.default)), file=pyf)
            value = getattr(pipeline, param_name)
            if value != trait.default and value not in (None, '', Undefined):
                if first:
                    first = False
                    print('\n        # default and initial values', file=pyf)
                print('        self.%s = %s'
                      % (param_name, repr(value)), file=pyf)

    def _write_filters(pipeline, pyf):
        first = True
        for node_name, node in six.iteritems(pipeline.nodes):
            # if isinstance(node.process, Input_Filter):  # Not working, don't know why
            if hasattr(node.process, 'filter'):
                # Getting filter parameters
                filt = node.process.filter
                if first:
                    first = False
                    print('\n        # filter parameters', file=pyf)
                # Settings filter parameters to the node
                print('\n        self.nodes["%s"].process.filter = Filter(%s, %s, %s, %s, %s, %s, "%s")'
                      % (node_name, filt.name, filt.nots, filt.values, filt.fields, filt.links,
                         filt.conditions, filt.search_bar), file=pyf)

    class_name = type(pipeline).__name__

    pyf = open(py_file, 'w')

    print('from capsul.api import Pipeline', file=pyf)
    print('from populse_mia.project.filter import Filter', file=pyf)
    print(file=pyf)
    print(file=pyf)
    print('class %s(Pipeline):' % class_name, file=pyf)

    _write_doc(pipeline, pyf)

    print(file=pyf)
    print('    def pipeline_definition(self):', file=pyf)

    _write_processes(pipeline, pyf)
    _write_links(pipeline, pyf)
    _write_processes_selections(pipeline, pyf)
    _write_steps(pipeline, pyf)
    # Not writing the initial values of the pipeline
    # _write_values(pipeline, pyf)
    _write_nodes_positions(pipeline, pyf)
    _write_filters(pipeline, pyf)

    print('\n        self.do_autoexport_nodes_parameters = False', file=pyf)

    pyf.close()


def get_path(name, dictionary, prev_paths=None):
    """
    This recursive function returns the package path to the selected sub-pipeline.

    :param name: name of the sub-pipeline
    :param dictionary: package tree (read from process_config.yml)
    :param prev_paths: paths of the last call of this function
    :return: the package path of the sub-pipeline if it is found, else None
    """

    if prev_paths is None:
        prev_paths = []

    # new_paths is a list containing the packages to the desired module
    new_paths = prev_paths.copy()
    for idx, (key, value) in enumerate(dictionary.items()):
        # If the value is a string, this means that this is a "leaf" of the tree
        # so the key is a module name.
        if isinstance(value, str):
            if key == name:
                new_paths.append(key)
                return new_paths
            else:
                continue
        # Else, this means that the value is still a dictionary, we are still in the tree
        else:
            new_paths.append(key)
            final_res = get_path(name, value, new_paths)
            # final_res is None if the module name has not been found in the tree
            if final_res:
                return final_res
            else:
                new_paths = prev_paths.copy()


def find_filename(paths_list, packages_list, file_name):
    """
    Finds the corresponding file name in the paths list of process_config.yml.

    :param paths_list: list of all the paths contained in process_config.yml
    :param packages_list: packages path
    :param file_name: name of the sub-pipeline
    :return: name of the corresponding file if it is found, else None
    """

    filenames = [file_name + '.py', file_name + '.xml']
    for filename in filenames:
        for path in paths_list:
            new_path = path
            for package in packages_list:
                new_path = os.path.join(new_path, package)

            # Making sure that the filename is found (has somme issues with case sensitivity)
            for f in os.listdir(new_path):
                new_file = os.path.join(new_path, f)
                if os.path.isfile(new_file) and f.lower() == filename.lower():
                    return new_file

