# -*- coding: utf-8 -*- #
"""

Contains:
    Class:
        - PipelineEditorTabs
        - PipelineEditor
    Function :
        - save_pipeline
        - get_path
        - find_filename

"""

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
from capsul.qt_gui.widgets.pipeline_developper_view import \
    PipelineDevelopperView, NodeGWidget
from capsul.pipeline.xml import save_xml_pipeline
from capsul.pipeline.python_export import save_py_pipeline

# soma-base imports
from soma.utils.weak_proxy import weak_proxy

# Populse_MIA imports
from populse_mia.pipeline_manager.node_controller import FilterWidget
from populse_mia.pop_ups.pop_up_close_pipeline import PopUpClosePipeline
from populse_mia.software_properties.config import Config
from populse_mia.utils.utils import verCmp

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

    Methods:
        - check_modifications: check if the nodes of the current pipeline have
           been modified
        - close_tab: close the selected tab and editor
        - emit_node_clicked: emit a signal when a node is clicked
        - emit_pipeline_saved: emit a signal when a pipeline is saved
        - emit_switch_clicked: emit a signal when a switch is clicked
        - export_to_db_scans: export the input of a filter to 'database_scans'
        - get_current_editor: get the instance of the current editor
        - get_current_filename: get the file name of the current pipeline
        - get_current_pipeline: get the instance of the current pipeline
        - get_current_tab_name: get the tab title of the current editor
        - get_filename_by_index: get the pipeline filename from its index in
           the editors
        - get_index_by_filename: get the index of the editor corresponding to
           the given pipeline filename
        - get_index_by_tab_name: get the index of the editor corresponding to
           the given tab name
        - get_tab_name_by_index: get the tab title from its index in the
           editors
        - has_pipeline_nodes: check if any of the pipelines in the editor tabs
           have pipeline nodes
        - load_pipeline: load a new pipeline
        - load_pipeline_parameters: load parameters to the pipeline of the
           current editor
        - new_tab: create a new tab and a new editor
        - open_filter: open a filter widget
        - open_sub_pipeline: open a sub-pipeline in a new tab
        - reset_pipeline: reset the pipeline of the current editor
        - save_pipeline: save the pipeline of the current editor
        - save_pipeline_parameters: save the pipeline parameters of the
           current editor
        - set_current_editor_by_tab_name: set the current editor
        - update_history: update undo/redo history of an editor
        - update_pipeline_editors: update editors
        - update_scans_list: update the list of database scans in every editor
    """

    pipeline_saved = QtCore.pyqtSignal(str)
    node_clicked = QtCore.pyqtSignal(str, Process)
    switch_clicked = QtCore.pyqtSignal(str, Switch)

    def __init__(self, project, scan_list, main_window):
        """Initialization of the Pipeline Editor tabs.

        :param project: current project in the software
        :param scan_list: list of the selected database files
        :param main_window: main window of the software
        """
        super(PipelineEditorTabs, self).__init__()

        self.project = project
        self.main_window = main_window
        self.setStyleSheet('QTabBar{font-size:12pt;font-family:Arial;'
                           'text-align: center;color:black;}')
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

    def check_modifications(self, current_index):
        """Check if the nodes of the current pipeline have been modified"""

        # If the user click on the last tab (with the '+'),
        # it will throw an AttributeError
        try:
            self.widget(current_index).check_modifications()
        except AttributeError:
            pass

    def close_tab(self, idx):
        """Close the selected tab and editor.

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
            self.setCurrentIndex(max(0, self.currentIndex() - 1))
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

    def emit_node_clicked(self, node_name, process):
        """Emit a signal when a node is clicked.

        :param node_name: node name
        :param process: process of the corresponding node
        """

        self.node_clicked.emit(node_name, process)

    def emit_pipeline_saved(self, filename):
        """Emit a signal when a pipeline is saved.

        :param filename: file name of the pipeline
        """

        self.setTabText(self.currentIndex(), os.path.basename(filename))
        self.pipeline_saved.emit(filename)

    def emit_switch_clicked(self, node_name, switch):
        """Emit a signal when a switch is clicked.

        :param node_name: node name
        :param switch: process of the corresponding node
        """

        self.switch_clicked.emit(node_name, switch)

    def export_to_db_scans(self, node_name):
        """Export the input of a filter to "database_scans" plug.

        :param node_name:
        """

        # If database_scans is already a pipeline global input, the plug
        # cannot be exported. A link as to be added between database_scans
        # and the input of the filter.
        if 'database_scans' in \
                self.get_current_pipeline().user_traits().keys():
            self.get_current_pipeline().add_link('database_scans->{0}'
                                                 '.input'.format(node_name))
        else:
            self.get_current_pipeline().export_parameter(
                node_name, 'input',
                pipeline_parameter='database_scans')
        self.get_current_editor().scene.update_pipeline()

    def get_current_editor(self):
        """Get the instance of the current editor.

        :return: the current editor
        """

        return self.get_editor_by_index(self.currentIndex())

    def get_current_filename(self):
        """Get the relative path to the file the pipeline in the current editor
           has been last saved to.
        If the pipeline has never been saved, returns the title of the tab.

        :return: the filename of the current editor
        """

        return self.get_filename_by_index(self.currentIndex())

    def get_current_pipeline(self):
        """Get the instance of the current pipeline.

        :return: the pipeline of the current editor
        """

        return self.get_current_editor().scene.pipeline

    def get_current_tab_name(self):
        """Get the tab name of the editor in the current tab.
        Trailing " \*" and ampersand ("&") characters are removed.

        :return: the current tab name
        """

        return self.get_tab_name_by_index(self.currentIndex())

    def get_editor_by_file_name(self, file_name):
        """Get the instance of an editor from its file name.

        :param file_name: name of the file the pipeline was last saved to
        :return: the editor corresponding to the file name
        """

        return self.get_editor_by_index(self.get_index_by_filename(file_name))

    def get_editor_by_index(self, idx):
        """Get the instance of an editor from its index in the editors.

        :param idx: index of the editor
        :return: the editor corresponding to the index
        """

        # last tab has "add tab" button, no editor
        if idx in range(self.count() - 1):
            return self.widget(idx)

    def get_editor_by_tab_name(self, tab_name):
        """Get the instance of an editor from its tab name.

        :param tab_name: name of the tab
        :return: the editor corresponding to the tab name
        """

        return self.get_editor_by_index(self.get_index_by_tab_name(tab_name))

    def get_filename_by_index(self, idx):
        """Get the relative path to the file the pipeline in the editor at the
           given index has been last saved to.
        If the pipeline has never been saved, returns the title of the tab.

        :param idx: index of the editor
        :return: the file name corresponding to the index
        """

        editor = self.get_editor_by_index(idx)
        if editor is not None:
            return editor.get_current_filename()

    def get_index_by_editor(self, editor):
        """Get the index of the editor corresponding to the given editor.

        :param editor: searched pipeline editor
        :return: the index corresponding to the editor
        """
        for idx in range(self.count() - 1):
            if self.get_editor_by_index(idx) == editor:
                return idx

    def get_index_by_filename(self, filename):
        """Get the index of the first editor corresponding to the given
           pipeline filename

        :param filename: filename of the searched pipeline
        :return: the index corresponding to the file name
        """

        if filename:
            # we always store file names as relative paths
            filename = os.path.relpath(filename)

            for idx in range(self.count() - 1):
                if self.get_filename_by_index(idx) == filename:
                    return idx

    def get_index_by_tab_name(self, tab_name):
        """Get the index of the editor corresponding to the given tab name.

        :param tab_name: name of the tab with the searched pipeline
        :return: the index corresponding to the tab name
        """

        for idx in range(self.count() - 1):
            if self.get_tab_name_by_index(idx) == tab_name:
                return idx

    def get_tab_name_by_index(self, idx):
        """Get the tab name of the editor at the given index.
        Trailing " \*" and ampersand ("&") characters are removed.

        :param idx: index of the editor
        :return: the tab name corresponding to the index
        """

        # last tab has "add tab" button, no tab name
        if idx in range(self.count() - 1):
            # remove Qt keyboard shortcut indicator
            tab_name = self.tabText(idx).replace("&", "", 1)
            if tab_name[-2:] == " *":
                tab_name = tab_name[:-2]

            return tab_name

    def has_pipeline_nodes(self):
        """Check if any of the pipelines in the editor tabs have pipeline nodes

        :return: True or False depending on if there are nodes in the editors
        """
        for idx in range(self.count()):
            p_e = self.widget(idx)
            if hasattr(p_e, 'scene'):
                # if the widget is a tab editor
                if p_e.scene.pipeline.nodes[''].plugs:
                    return True

        return False

    def load_pipeline(self, filename=None):
        """Load a new pipeline.

        :param filename: not None only when this method is called from
          "open_sub_pipeline"
        """

        current_tab_not_empty = len(
            self.get_current_editor().scene.pipeline.nodes.keys()) > 1
        new_tab_opened = False

        if filename is None:
            # Open new tab if the current PipelineEditor is not empty
            if current_tab_not_empty:
                # create new tab with new editor and make it current
                self.new_tab()
                working_index = self.currentIndex()
                new_tab_opened = True
            # get only the file name to load
            filename = self.get_current_editor().load_pipeline('', False)

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
                # actually load the pipeline
                filename = editor.load_pipeline(filename)
                if filename:
                    self.setTabText(working_index, os.path.basename(filename))
                    self.update_scans_list()
                    return  # success

        # if we're still here, something went wrong. clean up.
        if new_tab_opened:
            self.close_tab(working_index)

    def load_pipeline_parameters(self):
        """Load parameters to the pipeline of the current editor"""

        self.get_current_editor().load_pipeline_parameters()

    def new_tab(self):
        """Create a new tab and a new editor and makes the new tab current."""

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

        self.insertTab(self.count() - 1, p_e, name)
        self.setCurrentIndex(self.count() - 2)

    def open_filter(self, node_name):
        """Open a filter widget.

        :param node_name: name of the corresponding node
        """
        node = self.get_current_pipeline().nodes[node_name]
        self.filter_widget = FilterWidget(self.project, node_name, node, self)
        self.filter_widget.show()

    def open_sub_pipeline(self, sub_pipeline):
        """Open a sub-pipeline in a new tab.

        :param sub_pipeline: the pipeline to open
        """

        # Reading the process configuration file
        config = Config()
        with open(os.path.join(config.get_mia_path(),
                               'properties',
                               'process_config.yml'), 'r') as stream:

            try:
                if verCmp(yaml.__version__, '5.1', 'sup'):
                    dic = yaml.load(stream, Loader=yaml.FullLoader)

                else:
                    dic = yaml.load(stream)

            except yaml.YAMLError as exc:
                print(exc)
                dic = {}

        sub_pipeline_name = sub_pipeline.name

        # get_path returns a list that is the package path to
        # the sub_pipeline file
        sub_pipeline_list = get_path(sub_pipeline_name, dic['Packages'])
        sub_pipeline_name = sub_pipeline_list.pop()

        # Finding the real sub-pipeline filename
        sub_pipeline_filename = find_filename(
            dic['Paths'], sub_pipeline_list, sub_pipeline_name)
        self.load_pipeline(sub_pipeline_filename)

    def reset_pipeline(self):
        """Reset the pipeline of the current editor"""

        self.get_current_editor()._reset_pipeline()

    def save_pipeline(self, new_file_name=None):
        """Save the pipeline of the current editor."""
        if new_file_name is None:
            # Doing a "Save as" action
            new_file_name = os.path.basename(
                self.get_current_editor().save_pipeline())

            if (new_file_name and
                    os.path.basename(
                        self.get_current_filename()) != new_file_name):
                self.setTabText(self.currentIndex(), new_file_name)
        else:
            # Saving the current pipeline
            pipeline = self.get_current_pipeline()

            try:
                posdict = dict(
                    [(key, (value.x(), value.y())) for key, value in
                     six.iteritems(self.get_current_editor().scene.pos)])

            except:  # add by Irmage OM
                posdict = dict(
                    [(key, (value[0], value[1])) for key, value in
                     six.iteritems(self.get_current_editor().scene.pos)])

            # add by Irmage OM
            dimdict = dict(
                [(key, (value[0], value[1])) for key, value in
                 six.iteritems(self.get_current_editor().scene.dim)])

            # add by Irmage OM
            pipeline.node_dimension = dimdict

            old_pos = pipeline.node_position
            pipeline.node_position = posdict
            save_pipeline(pipeline, new_file_name)
            self.get_current_editor()._pipeline_filename = unicode(
                new_file_name)
            pipeline.node_position = old_pos
            self.pipeline_saved.emit(new_file_name)
            self.setTabText(self.currentIndex(),
                            os.path.basename(new_file_name))

    def save_pipeline_parameters(self):
        """Save the pipeline parameters of the current editor"""

        self.get_current_editor().save_pipeline_parameters()

    def set_current_editor_by_editor(self, editor):
        """Set the current editor.

        :param editor: editor in the tab that should be made current
        """

        self.setCurrentIndex(self.get_index_by_editor(editor))

    def set_current_editor_by_file_name(self, file_name):
        """Set the current editor.

        :param file_name: name of the file the pipeline was last saved to
        """

        self.setCurrentIndex(self.get_index_by_filename(file_name))

    def set_current_editor_by_tab_name(self, tab_name):
        """Set the current editor.

        :param tab_name: name of the tab
        """

        self.setCurrentIndex(self.get_index_by_tab_name(tab_name))

    def update_history(self, editor):
        """Update undo/redo history of an editor

        :param editor: editor
        """

        self.undos[editor] = editor.undos
        self.redos[editor] = editor.redos
        self.setTabText(self.currentIndex(),
                        self.get_current_tab_name() + " *")  # make sure the " *" is there

    def update_pipeline_editors(self, editor):
        """Update editor.

        :param editor: editor
        """

        self.update_history(editor)
        self.update_scans_list()

    def update_scans_list(self):
        """Update the list of database scans in every editor"""

        for i in range(self.count() - 1):
            pipeline = self.widget(i).scene.pipeline
            if hasattr(pipeline, "nodes"):
                for node_name, node in pipeline.nodes.items():
                    if node_name == "":
                        for plug_name, plug in node.plugs.items():
                            if plug_name == "database_scans":
                                node.set_plug_value(plug_name, self.scan_list)


class PipelineEditor(PipelineDevelopperView):
    """View to edit a pipeline graphically

    Methods:
        - _del_link: deletes a link
        - _export_plug: export a plug to a pipeline global input or output
        - _release_grab_link: method called when a link is released
        - _remove_plug: removes a plug
        - add_link: add a link between two nodes
        - add_process: adds a process to the pipeline
        - check_modifications: checks if the nodes of the pipeline have been
           modified
        - del_node: deletes a node
        - dragEnterEvent: event handler when the mouse enters the widget
        - dragMoveEvent: event handler when the mouse moves in the widget
        - dropEvent: event handler when something is dropped in the widget
        - export_node_plugs: exports all the plugs of a node
        - find_process: finds the dropped process in the system's paths
        - get_current_filename: returns the relative path the pipeline was
           last saved to. Empty if never saved.
        - save_pipeline: saves the pipeline
        - update_history: updates the history for undos and redos
        - update_node_name: updates a node name
        - update_plug_value: updates a plug value
    """

    pipeline_saved = QtCore.pyqtSignal(str)
    pipeline_modified = QtCore.pyqtSignal(PipelineDevelopperView)

    def __init__(self, project, main_window):
        """Initialization of the PipelineEditor.

        :param project: current project in the software
        """

        PipelineDevelopperView.__init__(self, pipeline=None,
                                        allow_open_controller=True,
                                        show_sub_pipelines=True,
                                        enable_edition=True)

        self.project = project
        self.main_window = main_window

        # Undo/Redo
        self.undos = []
        self.redos = []

    def _del_link(self, link=None, from_undo=False, from_redo=False):
        """Delete a link.

        :param link: string representation of a link
           (e.g. "process1.out->process2.in")
        :param from_undo: boolean, True if the action has been made using an
           undo
        :param from_redo: boolean, True if the action has been made using a
           redo
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

        self.main_window.statusBar().showMessage(
            'Link {0} has been deleted.'.format(link))

    def _export_plug(self, pipeline_parameter=False, optional=None,
                     weak_link=None, from_undo=False, from_redo=False,
                     temp_plug_name=None):
        """Export a plug to a pipeline global input or output.

        :param pipeline_parameter: name of the pipeline input/output
        :param optional: True if the plug is optional
        :param weak_link: True if the link is weak
        :param from_undo: True if this method is called from an undo action
        :param from_redo: True if this method is called from a redo action
        :param temp_plug_name: tuple containing (the name of the node, the
           name of the plug) to export
        """
        # Bug: the first parameter (here pipeline_parameter) cannot be None
        # even if we write pipeline_parameter=None in the line above,
        # it will be False...

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
                print("Cannot export {0}.{1} plug".format(temp_plug_name[0],
                                                          temp_plug_name[1]))

            '''self.scene.pipeline.export_parameter(
                temp_plug_name[0], temp_plug_name[1],
                pipeline_parameter=pipeline_parameter,
                is_optional=optional,
                weak_link=weak_link)'''  # Uncomment to generate the error

            self.scene.update_pipeline()

        # For history
        history_maker = ["export_plug", ('inputs', pipeline_parameter),
                         pipeline_parameter, optional, weak_link]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage(
            "Plug {0} has been exported.".format(temp_plug_name[1]))

    def _release_grab_link(self, event, ret=False):
        """Method called when a link is released.

        :param event: mouse event corresponding to the release
        :param ret: boolean that is set to True in the original method to
           return the link
        """

        # Calling the original method
        link = PipelineDevelopperView._release_grab_link(self, event, ret=True)

        # For history
        history_maker = ["add_link", link]

        self.update_history(history_maker, from_undo=False, from_redo=False)

        self.main_window.statusBar().showMessage(
            'Link {0} has been added.'.format(link))

    def add_link(self, source, dest, active, weak,
                 from_undo=False, from_redo=False):
        """Add a link between two nodes.

        :param source: tuple containing the node and plug source names
        :param dest: tuple containing the node and plug destination names
        :param active: boolean that is True if the link is activated
        :param weak: boolean that is True if the link is weak
        :param from_undo: boolean that is True if the action has been made
           using an undo
        :param from_redo: boolean that is True if the action has been made
           using a redo
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

        self.main_window.statusBar().showMessage(
            'Link {0} has been added.'.format(link))

    def add_process(self, class_process, node_name=None,
                    from_undo=False, from_redo=False, links=[]):
        """Add a process to the pipeline.

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

        # If the process is added from a undo, all the links
        # that were connected to the corresponding node has to be reset
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

        self.main_window.statusBar().showMessage(
            "Node {0} has been added.".format(node_name))

    def check_modifications(self):
        """Check if the nodes of the pipeline have been modified."""

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
                with open(os.path.join(config.get_mia_path(),
                                       'properties',
                                       'process_config.yml'), 'r') as stream:

                    try:
                        if verCmp(yaml.__version__, '5.1', 'sup'):
                            dic = yaml.load(stream,
                                            Loader=yaml.FullLoader)
                        else:
                            dic = yaml.load(stream)

                    except yaml.YAMLError as exc:
                        print(exc)
                        dic = {}

                sub_pipeline_name = sub_pipeline_process.name

                # get_path returns a list that is the package path
                # to the sub_pipeline file
                sub_pipeline_list = get_path(sub_pipeline_name,
                                             dic['Packages'])
                sub_pipeline_name = sub_pipeline_list.pop()

                # Finding the real sub-pipeline filename
                sub_pipeline_filename = find_filename(
                    dic['Paths'], sub_pipeline_list, sub_pipeline_name)

                saved_process = get_process_instance(sub_pipeline_filename)

                current_inputs = list(sub_pipeline_process.get_inputs().keys())
                current_outputs = list(
                    sub_pipeline_process.get_outputs().keys())
                saved_inputs = list(saved_process.get_inputs().keys())
                saved_outputs = list(saved_process.get_outputs().keys())

                new_inputs = [item for item in saved_inputs
                              if item not in current_inputs]
                new_outputs = [item for item in saved_outputs
                               if item not in current_outputs]
                removed_inputs = [item for item in current_inputs
                                  if item not in saved_inputs]
                removed_outputs = [item for item in current_outputs
                                   if item not in saved_outputs]

                if new_inputs or new_outputs or removed_inputs or \
                        removed_outputs:

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
                        logical_view=self.scene.logical_view,
                        labels=self.scene.labels)

                    # Setting the new node to the same position as the
                    # previous one
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
                        pipeline_link = "->".join((source_parameters,
                                                   dest_parameters))

                        # Checking if a connected plug has been deleting
                        if dest[0] == node_name and dest[1] in removed_inputs:
                            removed_links.append(pipeline_link)
                            continue

                        if source[0] == node_name and source[1] in \
                                removed_outputs:
                            removed_links.append(pipeline_link)
                            continue

                        # Adding the link
                        self.scene.pipeline.add_link(pipeline_link)
                        self.scene.add_link(source, dest, True, False)

                    self.scene.update_pipeline()

        if removed_links:
            dialog_text = 'Pipeline {0} has been updated.\n' \
                          'Removed links:'.format(node_name)
            for removed_link in removed_links:
                dialog_text += '\n{0}'.format(removed_link)

            pop_up = QtWidgets.QMessageBox()
            pop_up.setIcon(QtWidgets.QMessageBox.Warning)
            pop_up.setText(dialog_text)
            pop_up.setWindowTitle("Warning: links have been removed")
            pop_up.setStandardButtons(
                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            pop_up.exec_()

    def get_current_filename(self):
        """Return the relative path the pipeline was last saved to.
        Empty if never saved.

        :return: the current pipeline file name
        """
        if hasattr(self, '_pipeline_filename') and self._pipeline_filename:
            return os.path.relpath(self._pipeline_filename)
        else:
            return ''

    def del_node(self, node_name=None, from_undo=False, from_redo=False):
        """Delete a node.

        :param node_name: name of the corresponding node (using when undo/redo)
        :param from_undo: boolean, True if the action has been made using an
           undo
        :param from_redo: boolean, True if the action has been made using a
           redo
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
                    (source_node_name, source_parameter, source_node,
                     source_plug, weak_link) = link_from
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

        self.main_window.statusBar().showMessage(
            "Node {0} has been deleted.".format(node_name))

    def dragEnterEvent(self, event):
        """Event handler when the mouse enters the widget.

        :param event: event
        """

        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dragMoveEvent(self, event):
        """Event handler when the mouse moves in the widget.

        :param event: event
        """

        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dropEvent(self, event):
        """Event handler when something is dropped in the widget.

        :param event: event

        """

        if event.mimeData().hasFormat('component/name'):
            self.click_pos = QtGui.QCursor.pos()
            path = bytes(event.mimeData().data('component/name'))
            self.find_process(path.decode('utf8'))

    def find_process(self, path):
        """Find the dropped process in the system's paths.

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
        """Update the history for undos and redos.
        This method is called after each action in the PipelineEditor.

        :param history_maker: list that contains information about what has
            been done
        :param from_undo: boolean that is True if the action has been made
            using an undo
        :param from_redo: boolean that is True if the action has been made
            using a redo
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

    def update_node_name(self, old_node, old_node_name, new_node_name,
                         from_undo=False, from_redo=False):
        """Update a node name.

        :param old_node: Node object to change
        :param old_node_name: original name of the node (str)
        :param new_node_name: new name of the node (str)
        :param from_undo: boolean, True if the action has been made using an
           undo
        :param from_redo: boolean, True if the action has been made using a
           redo
        """

        pipeline = self.scene.pipeline

        # Removing links of the selected node and copy the origin/destination
        links_to_copy = []
        for source_parameter, source_plug \
                in six.iteritems(old_node.plugs):
            for (dest_node_name, dest_parameter, dest_node, dest_plug,
                 weak_link) in source_plug.links_to.copy():
                pipeline.remove_link(old_node_name + "." + source_parameter +
                                     "->" + dest_node_name + "." +
                                     dest_parameter)
                links_to_copy.append(("to", source_parameter,
                                      dest_node_name, dest_parameter))

            for (dest_node_name, dest_parameter, dest_node, dest_plug,
                 weak_link) in source_plug.links_from.copy():
                pipeline.remove_link(dest_node_name + "." + dest_parameter +
                                     "->" + old_node_name + "." +
                                     source_parameter)
                links_to_copy.append(("from", source_parameter, dest_node_name,
                                      dest_parameter))

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
        history_maker = ["update_node_name", pipeline.nodes[new_node_name],
                         new_node_name, old_node_name]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage(
            'Node name "{0}" has been changed to "{1}".'.format(
                old_node_name, new_node_name))

    def update_plug_value(self, node_name, new_value, plug_name, value_type,
                          from_undo=False, from_redo=False):
        """Update a plug value.

        :param node_name: name of the node (str)
        :param new_value: new value to set to the plug
        :param plug_name: name of the plug to change (str)
        :param value_type: type of the new value
        :param from_undo: boolean, True if the action has been made using an
        undo
        :param from_redo: boolean, True if the action has been made using a
        redo
        """

        old_value = self.scene.pipeline.nodes[node_name].get_plug_value(
            plug_name)
        self.scene.pipeline.nodes[node_name].set_plug_value(
            plug_name, value_type(new_value))

        # For history
        history_maker = ["update_plug_value", node_name, old_value,
                         plug_name, value_type]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage(
            'Plug "{0}" of node "{1}" has been changed to "{2}".'.format(
                plug_name, node_name, new_value))

    def export_node_plugs(self, node_name, inputs=True, outputs=True,
                          optional=False, from_undo=False, from_redo=False):
        """Export all the plugs of a node

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
                    print("Cannot export {0}.{1} plug".format(node_name,
                                                              parameter_name))

        # For history
        history_maker = ["export_plugs", parameter_list, node_name]

        self.update_history(history_maker, from_undo, from_redo)

        self.main_window.statusBar().showMessage(
            "Plugs {0} have been exported.".format(str(parameter_list)))

    def _remove_plug(self, _temp_plug_name=None, from_undo=False,
                     from_redo=False, from_export_plugs=False):
        """Remove a plug

        :param _temp_plug_name: tuple containing (the name of the node,
           the name of the plug) to remove
        :param from_undo: True if this method is called from an undo action
        :param from_redo: True if this method is called from a redo action
        :param from_export_plugs: True if this method is called from a
           "from_export_plugs" undo or redo action
        """
        if not _temp_plug_name:
            _temp_plug_name = self._temp_plug_name

        if _temp_plug_name[0] in ('inputs', 'outputs'):
            plug_name = _temp_plug_name[1]
            plug = self.scene.pipeline.pipeline_node.plugs[plug_name]
            optional = plug.optional
            # contains the plugs that are connected to the input or output plug
            new_temp_plugs = []
            for link in plug.links_to:
                temp_plug = (link[0], link[1])
                new_temp_plugs.append(temp_plug)
            for link in plug.links_from:
                temp_plug = (link[0], link[1])
                new_temp_plugs.append(temp_plug)

            # To avoid the "_items" bug: setting the has_items attribute
            # of the trait's handler to False
            node = self.scene.pipeline.nodes['']
            source_trait = node.get_trait(plug_name)
            if source_trait.handler.has_items:
                source_trait.handler.has_items = False

            self.scene.pipeline.remove_trait(_temp_plug_name[1])
            self.scene.update_pipeline()

            # if not from_undo and not from_redo:
            if not from_export_plugs:
                # For history
                history_maker = ["remove_plug", _temp_plug_name,
                                 new_temp_plugs, optional]

                self.update_history(history_maker, from_undo, from_redo)

                self.main_window.statusBar().showMessage(
                    "Plug {0} has been removed.".format(_temp_plug_name[1]))

    def save_pipeline(self, filename=None):
        """Save the pipeline.

        :return: the pipeline file name
        """
        config = Config()
        if not filename:
            pipeline = self.scene.pipeline
            folder = os.path.abspath(os.path.join(config.get_mia_path(),
                                                  'processes',
                                                  'User_processes'))

            if not os.path.isdir(folder):
                os.mkdir(folder)

            if not os.path.isfile(os.path.abspath(
                    os.path.join(folder, '__init__.py'))):
                with open(os.path.abspath(os.path.join(
                        folder, '__init__.py')), 'w'):
                    pass

            filename = QtWidgets.QFileDialog.getSaveFileName(
                None, 'Save the pipeline', folder,
                'Compatible files (*.py);; All (*)')[0]

            if not filename:  # save widget was cancelled by the user
                return ''

            if os.path.splitext(filename)[1] == '':  # which means no extension
                filename += '.py'

            elif os.path.splitext(filename)[1] != '.py':
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText('The pipeline will be saved with a' +
                            ' ".py" extension instead of {0}'.format(
                                os.path.splitext(filename)[1]))
                msg.setWindowTitle("Warning")
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.buttonClicked.connect(msg.close)
                msg.exec()
                filename = os.path.splitext(filename)[0] + '.py'

        if filename:
            posdict = dict([(key, (value.x(), value.y())) for key, value in
                            six.iteritems(self.scene.pos)])
            dimdict = dict([(key, (value[0], value[1])) for key, value in
                            six.iteritems(self.scene.dim)])  # add by Irmage OM

            pipeline.node_dimension = dimdict  # add by Irmage OM

            old_pos = pipeline.node_position
            pipeline.node_position = posdict
            # pipeline_tools.save_pipeline(pipeline, filename)
            save_pipeline(pipeline, filename)
            self._pipeline_filename = unicode(filename)
            pipeline.node_position = old_pos

            self.pipeline_saved.emit(filename)
            return filename


def find_filename(paths_list, packages_list, file_name):
    """
    Find the corresponding file name in the paths list of process_config.yml.

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

            # Making sure that the filename is found (has somme issues
            # with case sensitivity)
            for f in os.listdir(new_path):
                new_file = os.path.join(new_path, f)
                if os.path.isfile(new_file) and f.lower() == filename.lower():
                    return new_file


def get_path(name, dictionary, prev_paths=None):
    """Return the package path to the selected sub-pipeline.

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
        # If the value is a string, this means
        # that this is a "leaf" of the tree
        # so the key is a module name.
        if isinstance(value, str):
            if key == name:
                new_paths.append(key)
                return new_paths
            else:
                continue
        # Else, this means that the value is still a dictionary,
        # we are still in the tree
        else:
            new_paths.append(key)
            final_res = get_path(name, value, new_paths)
            # final_res is None if the module name has not
            # been found in the tree
            if final_res:
                return final_res
            else:
                new_paths = prev_paths.copy()


def save_pipeline(pipeline, filename):
    """Save the pipeline either in XML or .py source file."""
    formats = {'.py': save_py_pipeline,
               '.xml': save_xml_pipeline}
    saved = False

    for ext, writer in six.iteritems(formats):

        if filename.endswith(ext):
            writer(pipeline, filename)
            saved = True
            break

    if not saved:
        # fallback to .py
        save_py_pipeline(pipeline, filename)






