#!/usr/bin/python3

import sys
import sip
import six
import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QHBoxLayout, \
    QLabel, QLineEdit, QGroupBox, QFileDialog

from matplotlib.backends.qt_compat import QtWidgets
from functools import partial

from soma.controller import trait_ids

from DataBrowser.AdvancedSearch import AdvancedSearch
from DataBrowser.DataBrowser import TableDataBrowser
from Project.Filter import Filter

if sys.version_info[0] >= 3:
    unicode = str
    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()


class NodeController(QWidget):
    """ The node controller is displayed on the right of the pipeline editor"""

    value_changed = pyqtSignal(list)

    def __init__(self, project, scan_list, parent=None):
        super(NodeController, self).__init__(parent)
        self.v_box_final = QVBoxLayout()
        self.h_box_node_name = QHBoxLayout()
        self.project = project
        self.scan_list = scan_list

    def display_parameters(self, node_name, process, pipeline):
        """ Methods that displays all the parameters of the selected nodes"""

        self.node_name = node_name

        """self.advanced_search = AdvancedSearch(self.project, self)
        self.advanced_search.show_search()"""

        self.line_edit_input = []
        self.line_edit_output = []
        if len(self.children()) > 0:
            self.clearLayout(self)

        self.v_box_final = QVBoxLayout()

        # Node name
        label_node_name = QLabel()
        label_node_name.setText('Node name:')

        self.line_edit_node_name = QLineEdit()
        if self.node_name not in ('inputs', 'outputs'):
            self.line_edit_node_name.setText(self.node_name)
            self.line_edit_node_name.returnPressed.connect(partial(self.update_node_name, pipeline))
        else:
            self.line_edit_node_name.setText('Pipeline inputs/outputs')
            self.line_edit_node_name.setReadOnly(True)

        self.h_box_node_name = QHBoxLayout()
        self.h_box_node_name.addWidget(label_node_name)
        self.h_box_node_name.addWidget(self.line_edit_node_name)

        # Inputs
        self.button_group_inputs = QGroupBox('Inputs')
        self.v_box_inputs = QVBoxLayout()
        idx = 0

        for name, trait in process.user_traits().items():
            if name == 'nodes_activation':
                continue
            if not trait.output:
                label_input = QLabel()
                label_input.setText(str(name))

                value = getattr(process, name)
                trait_type = trait_ids(process.trait(name))

                self.line_edit_input.insert(idx, QLineEdit())
                self.line_edit_input[idx].setText(str(value))
                self.line_edit_input[idx].returnPressed.connect(partial(self.update_plug_value, idx, 'in',
                                                                        name, pipeline, type(value)))

                h_box = QHBoxLayout()
                h_box.addWidget(label_input)
                h_box.addWidget(self.line_edit_input[idx])

                if trait_type[0] in ['File', 'ImageFileSPM', 'List_ImageFileSPM']:
                    # If the trait is a file, adding a 'Browse' button
                    push_button = QPushButton('Browse')
                    push_button.clicked.connect(partial(self.browse_file, idx, 'in', self.node_name,
                                                        name, pipeline, type(value)))
                    h_box.addWidget(push_button)

                if hasattr(trait, 'optional'):
                    parameters = (idx, pipeline, type(value))
                    if not trait.optional:
                        push_button = QPushButton('Filter')
                        push_button.clicked.connect(partial(self.display_filter, self.node_name, name, parameters))
                        h_box.addWidget(push_button)
                    else:
                        if hasattr(trait, 'mandatory'):
                            if trait.mandatory:
                                push_button = QPushButton('Filter')
                                push_button.clicked.connect(partial(self.display_filter, self.node_name, name, parameters))
                                h_box.addWidget(push_button)

                self.v_box_inputs.addLayout(h_box)

                idx += 1

        self.button_group_inputs.setLayout(self.v_box_inputs)

        # Outputs
        self.button_group_outputs = QGroupBox('Outputs')
        self.v_box_outputs = QVBoxLayout()
        idx = 0

        for name, trait in process.traits(output=True).items():
            label_output = QLabel()
            label_output.setText(str(name))

            value = getattr(process, name)
            trait_type = trait_ids(process.trait(name))

            self.line_edit_output.insert(idx, QLineEdit())
            self.line_edit_output[idx].setText(str(value))
            self.line_edit_output[idx].returnPressed.connect(partial(self.update_plug_value, idx, 'out',
                                                                     name, pipeline, type(value)))

            h_box = QHBoxLayout()
            h_box.addWidget(label_output)
            h_box.addWidget(self.line_edit_output[idx])

            if trait_type[0] in ['File', 'ImageFileSPM', 'List_ImageFileSPM']:
                # If the trait is a file, adding a 'Browse' button
                push_button = QPushButton('Browse')
                push_button.clicked.connect(partial(self.browse_file, idx, 'out', self.node_name,
                                                    name, pipeline, type(value)))
                h_box.addWidget(push_button)

            self.v_box_outputs.addLayout(h_box)

            idx += 1

        self.button_group_outputs.setLayout(self.v_box_outputs)

        self.v_box_final.addLayout(self.h_box_node_name)
        #self.v_box_final.addWidget(self.advanced_search)
        self.v_box_final.addWidget(self.button_group_inputs)
        self.v_box_final.addWidget(self.button_group_outputs)

        self.setLayout(self.v_box_final)

    def update_node_name(self, pipeline, new_node_name=None):
        """ Method that allow to change the name of the selected node and update
        the pipeline. Because the nodes are stored in a dictionary, we have to
        create a new node that has the same traits as the selected one and create
        new links that are the same than the selected node."""
        old_node = pipeline.nodes[self.node_name]
        old_node_name = self.node_name

        if not new_node_name:
            new_node_name = self.line_edit_node_name.text()

        if new_node_name in list(pipeline.nodes.keys()):
            print("Node name already in pipeline")

        else:
            # Removing links of the selected node and copy the origin/destination
            links_to_copy = []
            for source_parameter, source_plug \
                    in six.iteritems(old_node.plugs):
                for (dest_node_name, dest_parameter, dest_node, dest_plug,
                     weak_link) in source_plug.links_to.copy():
                    pipeline.remove_link(self.node_name + "." + source_parameter + "->"
                                      + dest_node_name + "." + dest_parameter)
                    links_to_copy.append(("to", source_parameter, dest_node_name, dest_parameter))

                for (dest_node_name, dest_parameter, dest_node, dest_plug,
                     weak_link) in source_plug.links_from.copy():
                    pipeline.remove_link(dest_node_name + "." + dest_parameter + "->"
                                      + self.node_name + "." + source_parameter)
                    links_to_copy.append(("from", source_parameter, dest_node_name, dest_parameter))

            # Creating a new node with the new name and deleting the previous one
            pipeline.nodes[new_node_name] = pipeline.nodes[self.node_name]
            del pipeline.nodes[self.node_name]

            # Updating the node_name attribute
            self.node_name = new_node_name

            # Setting the same links as the original node
            for link in links_to_copy:

                if link[0] == "to":
                    pipeline.add_link(self.node_name + "." + link[1] + "->"
                                      + link[2] + "." + link[3])
                elif link[0] == "from":
                    pipeline.add_link(link[2] + "." + link[3] + "->"
                                      + self.node_name + "." + link[1])

            # Updating the pipeline
            pipeline.update_nodes_and_plugs_activation()

            # To undo/redo
            self.value_changed.emit(["node_name", pipeline.nodes[new_node_name], new_node_name, old_node_name])

    def update_plug_value(self, index, in_or_out, plug_name, pipeline, value_type, new_value=None):
        """ Method that updates in the pipeline the value of a plug """

        if not new_value:

            if in_or_out == 'in':
                new_value = self.line_edit_input[index].text()
            elif in_or_out == 'out':
                new_value = self.line_edit_output[index].text()
            else:
                new_value = None
                #TODO: RAISE ERROR
                pass

            try:
                new_value = eval(new_value)
            except:
                #TODO: RAISE SYNTHAXERROR
                pass

            if value_type not in [float, int, str, list]:
                #new_value = eval(new_value)
                value_type = str
                #TODO: RAISE ERROR

        if self.node_name in ['inputs', 'outputs']:
            node_name = ''
        else:
            node_name = self.node_name

        old_value = pipeline.nodes[node_name].get_plug_value(plug_name)
        pipeline.nodes[node_name].set_plug_value(plug_name, new_value)
        if in_or_out == 'in':
            self.line_edit_input[index].setText(str(new_value))
        elif in_or_out == 'out':
            self.line_edit_output[index].setText(str(new_value))


        # To undo/redo
        self.value_changed.emit(["plug_value", self.node_name, old_value, plug_name, value_type, new_value])

    def display_filter(self, node_name, plug_name, parameters):

        pop_up = PlugFilter(self.project, self.scan_list, node_name, plug_name)
        pop_up.show()
        pop_up.plug_value_changed.connect(partial(self.update_plug_value_from_filter, plug_name, parameters))
        """pop_up.plug_value_changed.connect(partial(self.update_plug_value, index, "in", plug_name,
                                                  pipeline, value_type))"""

    def update_plug_value_from_filter(self, plug_name, parameters, path_list):

        index = parameters[0]
        pipeline = parameters[1]
        value_type = parameters[2]

        len_list = len(path_list)
        if len_list == 1:
            res = path_list[0]
        elif len_list > 1:
            res = path_list
        else:
            res = []

        self.update_plug_value(index, "in", plug_name, pipeline, value_type, res)

    def browse_file(self, idx, in_or_out, node_name, plug_name, pipeline, value_type):
        """ Method that is called to open a browser to select file(s) """
        file_dialog = QFileDialog()
        # TODO: TO CHANGE WITH OUR OWN QFILEDIALOG
        if in_or_out == 'in':
            file_name = file_dialog.getOpenFileName()
            file_name = file_name[0]
            self.line_edit_input[idx].setText(file_name)
        elif in_or_out == 'out':
            file_name = file_dialog.getSaveFileName()
            file_name = file_name[0]
            self.line_edit_output[idx].setText(file_name)
        else:
            # TODO: RAISE ERROR
            pass
        self.update_plug_value(idx, in_or_out, plug_name, pipeline, value_type)

    def clearLayout(self, layout):
        for i in reversed(range(len(layout.children()))):
            if type(layout.layout().itemAt(i)) == QtWidgets.QWidgetItem:
                layout.layout().itemAt(i).widget().setParent(None)
            if type(layout.layout().itemAt(i)) == QtWidgets.QHBoxLayout or type(
                    layout.layout().itemAt(i)) == QtWidgets.QVBoxLayout:
                layout.layout().itemAt(i).deleteLater()
                for j in reversed(range(len(layout.layout().itemAt(i)))):
                    layout.layout().itemAt(i).itemAt(j).widget().setParent(None)

        if layout.layout() is not None:
            sip.delete(layout.layout())


class PlugFilter(QWidget):
    """ The plug is displayed to filter a plug of the current pipeline"""

    plug_value_changed = pyqtSignal(list)

    def __init__(self, project, scan_list, node_name="", plug_name="", parent=None):
        super(PlugFilter, self).__init__(parent)

        self.project = project
        self.scan_list = scan_list
        filter_to_apply = self.project.currentFilter

        self.setWindowTitle("Filter - " + node_name + " - " + plug_name)

        # Graphical components
        self.table_data = TableDataBrowser(self.project, self)

        self.advanced_search = AdvancedSearch(self.project, self, self.scan_list)
        self.advanced_search.apply_filter(filter_to_apply)
        self.advanced_search.show_search()

        push_button_ok = QPushButton("OK")
        push_button_ok.clicked.connect(self.ok_clicked)

        push_button_cancel = QPushButton("Cancel")
        push_button_cancel.clicked.connect(self.close)

        # Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(push_button_ok)
        buttons_layout.addWidget(push_button_cancel)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.advanced_search)
        main_layout.addWidget(self.table_data)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def ok_clicked(self):

        """(fields, conditions, values, links, nots) = self.advanced_search.get_filters()
        filter = Filter(None, nots, values, fields, links, conditions, "")
        self.advanced_search.apply_filter(filter)"""

        self.set_plug_value()
        self.save_filter()
        self.close()

    def set_plug_value(self):
        """ Emitting a signal to set the file names to the plug value. """

        (fields, conditions, values, links, nots) = self.advanced_search.get_filters()
        path_names = self.project.database.get_paths_matching_advanced_search(links, fields, conditions,
                                                                              values, nots, self.scan_list)

        for i in range(len(path_names)):

            path_names[i] = os.path.relpath(os.path.join(self.project.folder, path_names[i]))
        self.plug_value_changed.emit(path_names)

    def save_filter(self):
        """ Saving the filter and setting to the plug. """
        pass
