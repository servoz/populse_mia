#!/usr/bin/python3

import sys

from PyQt5 import QtGui
import os
import six

from capsul.api import get_process_instance
from .CAPSUL_Files.pipeline_developper_view import PipelineDevelopperView

if sys.version_info[0] >= 3:
    unicode = str
    def values(d):
        return list(d.values())
else:
    def values(d):
        return d.values()


class PipelineEditor(PipelineDevelopperView):
    def __init__(self, scene, parent=None):
        PipelineDevelopperView.__init__(self, pipeline=None, allow_open_controller=True,
                                        show_sub_pipelines=True, enable_edition=True)

        # Undo/Redo
        self.undos = []
        self.redos = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('component/name'):
            self.click_pos = QtGui.QCursor.pos()

            path = bytes(event.mimeData().data('component/name'))
            self.find_process(path.decode('utf8'))

    def find_process(self, path):
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
                    self.add_process(instance)

    def add_process(self, class_process, node_name=None, redo=False):

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

        pipeline.add_process(node_name, process)

        # CAPSUL UPDATE
        node = pipeline.nodes[node_name]
        gnode = self.scene.add_node(node_name, node)
        gnode.setPos(self.mapToScene(self.mapFromGlobal(self.click_pos)))

        # For history
        history_maker = []
        history_maker.append("add_process")
        history_maker.append(node_name)
        history_maker.append(class_process)
        self.undos.append(history_maker)
        if not redo:
            self.redos.clear()

    def del_node(self, node_name=None, redo=False):

        pipeline = self.scene.pipeline
        if not node_name:
            node_name = self.current_node_name
        node = pipeline.nodes[node_name]

        PipelineDevelopperView.del_node(self, node_name)

        # For history
        history_maker = []
        history_maker.append("delete_process")
        history_maker.append(node_name)
        history_maker.append(node.process)
        self.undos.append(history_maker)
        if not redo:
            self.redos.clear()
        # TODO: ADD ALL THE PLUG CONNEXION AND VALUES

    def add_link(self, source, dest, active, weak, redo=False):
        self.scene.add_link(source, dest, active, weak)

        # Writing a string to represent the link
        source_parameters = ".".join(source)
        dest_parameters = ".".join(dest)
        link = "->".join((source_parameters, dest_parameters))

        # For history
        history_maker = []
        history_maker.append("add_link")
        history_maker.append(link)
        self.undos.append(history_maker)

        print("add_link link :", link)

        if not redo:
            self.redos.clear()

    def _del_link(self, link=False, redo=False):
        if not link:
            link = self._current_link

        print("LINK: ", link)

        (source_node_name, source_plug_name, source_node,
         source_plug, dest_node_name, dest_plug_name, dest_node,
         dest_plug) = self.scene.pipeline.parse_link(link)

        (dest_node_name, dest_parameter, dest_node, dest_plug,
         weak_link) = list(source_plug.links_to)[0]

        active = source_plug.activated and dest_plug.activated

        PipelineDevelopperView._del_link(self)

        # For history
        history_maker = []
        history_maker.append("delete_link")
        history_maker.append((source_node_name, source_plug_name))
        history_maker.append((dest_node_name, dest_plug_name))
        history_maker.append(active)
        history_maker.append(weak_link)
        self.undos.append(history_maker)

        if not redo:
            self.redos.clear()

    def export_plugs(self, inputs=True, outputs=True, optional=False):
        # TODO: TO IMPROVE
        # For history
        history_maker = []
        history_maker.append("export_plugs")

        for node_name in self.scene.pipeline.nodes:
            if node_name != "":
                history_maker.append(node_name)

        self.undos.append(history_maker)
        self.redos.clear()

        PipelineDevelopperView.export_plugs(self, inputs, outputs, optional)

    def update_node_name(self, old_node, old_node_name, new_node_name, redo=False):
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
        history_maker = []
        history_maker.append("node_name")
        history_maker.append(pipeline.nodes[new_node_name])
        history_maker.append(new_node_name)
        history_maker.append(old_node_name)

        self.undos.append(history_maker)
        if not redo:
            self.redos.clear()

    def update_plug_value(self, node_name, new_value, plug_name, value_type, redo=False):
        old_value = self.scene.pipeline.nodes[node_name].get_plug_value(plug_name)
        self.scene.pipeline.nodes[node_name].set_plug_value(plug_name, value_type(new_value))

        # For history
        history_maker = []
        history_maker.append("plug_value")
        history_maker.append(node_name)
        history_maker.append(old_value)
        history_maker.append(plug_name)
        history_maker.append(value_type)

        self.undos.append(history_maker)
        if not redo:
            self.redos.clear()
