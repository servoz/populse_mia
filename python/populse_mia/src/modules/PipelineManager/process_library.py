import sys
import os
from glob import glob
import yaml
import inspect
import pkgutil
import zipfile

# PyQt5 import # TO REMOVE
from PyQt5.QtCore import QSortFilterProxyModel

# PyQt / PySide import, via soma
from soma.qt_gui import qt_backend
#qt_backend.set_qt_backend('PySide', pyqt_api=2, compatible_qt5=True)
from soma.qt_gui.qt_backend.QtCore import Qt, Signal, QModelIndex, \
    QAbstractItemModel, QByteArray, QMimeData
from soma.qt_gui.qt_backend.Qt import QWidget, QTreeWidget, QLabel, \
    QPushButton, QDialog, QTreeWidgetItem, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QApplication, QSplitter, QFileDialog, QTreeView, \
    QMessageBox

# CAPSUL import
from capsul.api import get_process_instance, StudyConfig

# Soma import
from soma.path import find_in_path


class ProcessLibraryWidget(QWidget):          
    """
    Widget that handles the available Capsul's processes in the software

    Attributes:
        - process_library: library of the selected processes
        - pkg_library: widget to control which processes to show in the process library
        - packages: tree-dictionary that is the representation of the process library. A dictionary, where keys are the name of a module (brick) and values are 'process_enabled' or 'process_disabled'. Key can be a submodule. In this case the value is a dictionary where keys are the name of a module (brick) and values are 'process_enabled' or 'process_disabled'. etc. ex. {'User_processes': {'Double_smooth': 'process_enabled', 'Filter_test': 'process_disabled'}, 'nipype': {'interfaces': {'BIDSDataGrabber': 'process_enabled', 'fsl': {'AR1Image': 'process_disabled'}}}}.
        - paths: list of path to add to the system path

    Methods:
        - update_config: updates the config and loads the corresponding packages
        - update_process_library: updates the tree of the process library
        - open_pkg_lib: opens the package library
        - load_config: read the config in process_config.yml and return it as a dictionary
        - load_packages: sets packages and paths to the widget and to the system paths
        - save_config: saves the current config to process_config.yml
    """

    def __init__(self):
        """
        Initializes the ProcessLibraryWidget
        """

        super(ProcessLibraryWidget, self).__init__()

        self.setWindowTitle("Process Library")

        # Process Config
        self.update_config()

        # Process Library
        self.process_library = ProcessLibrary(self.packages)
        self.process_library.setDragDropMode(self.process_library.DragOnly)
        self.process_library.setAcceptDrops(False)
        self.process_library.setDragEnabled(True)
        self.process_library.setSelectionMode(self.process_library.SingleSelection)

        # # Push button to call the package library
        # push_button_pkg_lib = QPushButton()
        # push_button_pkg_lib.setText('Package library manager')
        # push_button_pkg_lib.clicked.connect(self.open_pkg_lib)

        # Test to see the inputs/outputs of a process
        self.label_test = QLabel()

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.label_test)
        self.splitter.addWidget(self.process_library)

        # Layout
        h_box = QVBoxLayout()
        # h_box.addWidget(push_button_pkg_lib)
        h_box.addWidget(self.splitter)

        self.setLayout(h_box)

        self.pkg_library = PackageLibraryDialog()
        self.pkg_library.signal_save.connect(self.update_process_library)

    def update_config(self):
        """
        Updates the config and loads the corresponding packages

        :return:
        """

        self.process_config = self.load_config()
        self.load_packages()

    def update_process_library(self):
        """
        Updates the tree of the process library

        :return:
        """

        self.update_config()
        self.process_library.package_tree = self.packages
        self.process_library.load_dictionary(self.packages)

    def open_pkg_lib(self):
        """
        Opens the package library

        :return:
        """

        self.pkg_library.show()

    @staticmethod
    def load_config():
        """
        Read the config in process_config.yml and return it as a dictionary

        :return: the config as a dictionary
        """

        if not os.path.exists(os.path.join('..', '..', 'properties', 'process_config.yml')):
            open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'a').close()
        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_packages(self):
        """
        Sets packages and paths to the widget and to the system paths

        :return:
        """

        try:
            self.packages = self.process_config["Packages"]
        except KeyError:
            self.packages = {}
        except TypeError:
            self.packages = {}

        try:
            self.paths = self.process_config["Paths"]
        except KeyError:
            self.paths = []
        except TypeError:
            self.paths = []

        for path in self.paths:
            # Adding the module path to the system path
            sys.path.insert(0, os.path.abspath(path))

    def save_config(self):
        """
        Saves the current config to process_config.yml

        :return:
        """

        self.process_config["Packages"] = self.packages
        self.process_config["Paths"] = self.paths
        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'w', encoding='utf8') as stream:
            yaml.dump(self.process_config, stream, default_flow_style=False, allow_unicode=True)


class Node(object):

    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._children = []
        self._value = None
        if parent is not None:
            parent.addChild(self)

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False

        self._children.pop(position)
        child._parent = None
        return True

    def attrs(self):
        classes = self.__class__.__mro__
        keyvalued = {}
        for cls in classes:
            for key, value in cls.items():
                if isinstance(value, property):
                    keyvalued[key] = value.fget(self)
        return keyvalued

    def to_list(self):
        output = []
        if self._children:
            for child in self._children:
                output += [self.name, child.to_list()]
        else:
            output += [self.name, self.value]
        return output

    def to_dict(self, d={}):
        for child in self._children:
            child._recurse_dict(d)
        return d

    def _recurse_dict(self, d):
        if self._children:
            d[self.name] = {}
            for child in self._children:
                child._recurse_dict(d[self.name])
        else:
            d[self.name] = self.value

    def name():
        def fget(self):
            return self._name
        def fset(self, value):
            self._name = value
        return locals()
    name = property(**name())

    def value():
        def fget(self):
            return self._value
        def fset(self, value):
            self._value = value
        return locals()
    value = property(**value())

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):
        output = ''
        tabLevel += 1

        for i in range(tabLevel):
            output += '    '

        output += ''.join(('|----', self._name,' = ', '\n'))

        for child in self._children:
            output += child.log(tabLevel)

        tabLevel -= 1
        output += '\n'
        return output

    def __repr__(self):
        return self.log()

    def data(self, column):
        if column is 0:
            parent = self._parent
            text = self.name
            while parent.name != 'Root':
                text = parent.name + '.' + text
                parent = parent._parent
            return text #self.name

        elif column is 1:
            return self.value

    def setData(self, column, value):
        if column is 0:
            self.name = value
        if column is 1:
            self.value = value

    def resource(self):
        return None


class DictionaryTreeModel(QAbstractItemModel):
    """Data model providing a tree of an arbitrary dictionary"""

    def __init__(self, root, parent=None):
        super(DictionaryTreeModel, self).__init__(parent)
        self._rootNode = root

    def mimeTypes(self):
        return ['component/name']

    def mimeData(self, idxs):
        mimedata = QMimeData()
        for idx in idxs:
            if idx.isValid():
                node = idx.internalPointer()
                txt = node.data(idx.column())
                mimedata.setData('component/name', QByteArray(txt.encode()))
        return mimedata

    def rowCount(self, parent):
        """the number of rows is the number of children"""
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    def columnCount(self, parent):
        """Number of columns is always 1 """
        return 1

    def data(self, index, role):
        """returns the data requested by the view"""
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole or role == Qt.EditRole:
            return node.name

    def setData(self, index, value, role=Qt.EditRole):
        """this method gets called when the user changes data"""
        if index.isValid():
            if role == Qt.EditRole:
                node = index.internalPointer()
                node.setData(index.column(), value)
                return True
        return False

    def headerData(self, section, orientation, role):
        """returns the name of the requested column"""
        if role == Qt.DisplayRole:
            if section == 0:
                return "Packages"
            if section == 1:
                return "Value"

    def flags(self, index):
        """everything is enable and selectable. Only the leaves can be dragged. """
        node = index.internalPointer()
        if node.childCount() > 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

    def parent(self, index):
        """returns the parent from given index"""
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        """returns an index from given row, column and parent"""
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)

        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def getNode(self, index):
        """returns a Node() from given index"""
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node

        return self._rootNode

    def insertRows(self, position, rows, parent=QModelIndex()):
        """insert rows from starting position and number given by rows"""
        parentNode = self.getNode(parent)

        self.beginInsertRows(parent, position, position + rows - 1)

        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)

        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QModelIndex()):
        """remove the rows from position to position+rows"""
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)

        for row in range(rows):
            success = parentNode.removeChild(position)

        self.endRemoveRows()
        return success

    def to_dict(self):
        return self._rootNode.to_dict()

def node_structure_from_dict(datadict, parent=None, root_node=None):
    """returns a hierarchical node stucture required by the TreeModel"""
    
    if not parent:
        root_node = Node('Root')
        parent = root_node

    for name, data in sorted(datadict.items()):
        
        if isinstance(data, dict):

            if True in [True for value in data.values() if value == 'process_enabled']:
                list_name = [value for value in data.values() if value == 'process_enabled']

            else:
                
                list_name=[]
                list_values = [value for value in data.values() if isinstance(value, dict)]

                while (list_values):
                    value = list_values.pop()

                    for i in value.values():

                        if not isinstance(i, dict):
                            list_name.append(i)

                    list_values = list_values + [i for i in value.values() if isinstance(i, dict)]

            #if not list_name: list_name = [i for i in data.values()]
                
            if (all(item == 'process_disabled' for item in list_name)):
                continue
                
            node = Node(name, parent)
            node = node_structure_from_dict(data, node, root_node)
            
        elif data == 'process_enabled':
            node = Node(name, parent)
            node.value = data

    return root_node

class ProcessLibrary(QTreeView):
    """
    Tree to display the available Capsul's processes

    Attributes:
        - dictionary: dictionary corresponding to the tree
        - _model: model used

    Methods:
        - load_dictionary: loads a dictionary to the tree
        - to_dict: returns a dictionary from the current tree

    """

    def __init__(self, d):
        super(ProcessLibrary, self).__init__()
        self.load_dictionary(d)

    def load_dictionary(self, d):
        """
        Loads a dictionary to the tree

        :param d: dictionary to load. See the packages attribut in the ProcessLibraryWidget class.
        :return:
        """
        
        self.dictionary = d
        self._nodes = node_structure_from_dict(d)
        self._model = DictionaryTreeModel(self._nodes)
        self.setModel(self._model)
        self.expandAll()

    def to_dict(self):
        """
        Returns a dictionary from the current tree

        :return: the dictionary
        """

        return self._model.to_dict()


class PackageLibraryDialog(QDialog):
    """
    Dialog that controls which processes to show in the process library

    Attributes:
        - process_library: library of the selected processes
        - package_library: widget to control which processes to show in the process library
        - packages: tree-dictionary that is the representation of the process library
        - paths: list of path to add to the system path

    Methods:
        - load_config: updates the config and loads the corresponding packages
        - update_config: updates the process_config and package_library attributes
        - load_packages: updates the tree of the process library
        - save_config: saves the current config to process_config.yml
        - browse_package: opens a browser to select a package
        - add_package_with_text: adds a package from the line edit's text
        - add_package: adds a package and its modules to the package tree
        - remove_package_with_text: removes the package in the line edit from the package tree
        - remove_package: removes a package from the package tree
        - save: saves the tree to the process_config.yml file
        - import_file: import a python module from a path
    """

    signal_save = Signal()

    def __init__(self):
        """
        Initialization of the PackageLibraryDialog widget
        """

        super(PackageLibraryDialog, self).__init__()

        self.setWindowTitle("Package library manager")

        # True if the path specified in the line edit is a path with '/'
        self.is_path = False

        self.process_config = self.load_config()
        self.load_packages()

        self.package_library = PackageLibrary(self.packages, self.paths)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('Type a Python package (ex. nipype.interfaces.spm)')

        '''push_button_browse = QPushButton()
        push_button_browse.setText("Browse")
        push_button_browse.clicked.connect(self.browse_package)'''

        push_button_add_pkg = QPushButton()
        push_button_add_pkg.setText("Add package")
        push_button_add_pkg.clicked.connect(self.add_package_with_text)

        push_button_rm_pkg = QPushButton()
        push_button_rm_pkg.setText("Remove package")
        push_button_rm_pkg.clicked.connect(self.remove_package_with_text)

        push_button_save = QPushButton()
        push_button_save.setText("Save changes")
        push_button_save.clicked.connect(self.save)

        # Layout

        h_box_line_edit = QHBoxLayout()
        h_box_line_edit.addWidget(self.line_edit)
        # h_box_line_edit.addWidget(push_button_add_pkg)
        # h_box_browse.addWidget(push_button_browse)

        h_box_save = QHBoxLayout()
        h_box_save.addStretch(1)
        h_box_save.addWidget(push_button_save)

        h_box_buttons = QHBoxLayout()
        h_box_buttons.addStretch(1)
        h_box_buttons.addWidget(push_button_add_pkg)
        h_box_buttons.addStretch(1)
        h_box_buttons.addWidget(push_button_rm_pkg)
        h_box_buttons.addStretch(1)

        v_box = QVBoxLayout()
        v_box.addStretch(1)
        v_box.addLayout(h_box_line_edit)
        v_box.addLayout(h_box_buttons)
        v_box.addStretch(1)
        v_box.addLayout(h_box_save)

        h_box = QHBoxLayout()
        h_box.addWidget(self.package_library)
        h_box.addLayout(v_box)

        self.setLayout(h_box)

    @staticmethod
    def load_config():
        """
        Updates the config and loads the corresponding packages

        :return:
        """

        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def update_config(self):
        """
        Updates the process_config and package_library attributes

        :return:
        """
        self.process_config = self.load_config()
        self.load_packages()
        self.package_library.package_tree = self.packages
        self.package_library.paths = self.paths
        self.package_library.generate_tree()

    def load_packages(self):
        """
        Updates the tree of the process library

        :return:
        """

        try:
            self.packages = self.process_config["Packages"]
        except KeyError:
            self.packages = {}
        except TypeError:
            self.packages = {}

        try:
            self.paths = self.process_config["Paths"]
        except KeyError:
            self.paths = []
        except TypeError:
            self.paths = []

    def save_config(self):
        """
        Saves the current config to process_config.yml

        :return:
        """

        self.process_config["Packages"] = self.packages
        self.process_config["Paths"] = self.paths
        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'w', encoding='utf8') as stream:
            yaml.dump(self.process_config, stream, default_flow_style=False, allow_unicode=True)

    def browse_package(self):
        """
        Opens a browser to select a package

        :return:
        """

        file_dialog = QFileDialog()
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)

        # To select files or directories, we should use a proxy model
        # but mine is not working yet...
        #file_dialog.setProxyModel(FileFilterProxyModel())
        file_dialog.setFileMode(QFileDialog.Directory)
        #file_dialog.setFileMode(QFileDialog.Directory | QFileDialog.ExistingFile)
        #file_dialog.setFilter("Processes (*.py *.xml)")

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            file_name = os.path.abspath(file_name)
            self.is_path = True
            self.line_edit.setText(file_name)

    def add_package_with_text(self):
        """
        Adds a package from the line edit's text

        :return:
        """

        if self.is_path:
            path, package = os.path.split(self.line_edit.text())
            # Adding the module path to the system path
            sys.path.append(path)
            self.add_package(package)
            self.paths.append(os.path.relpath(path))
        else:
            self.add_package(self.line_edit.text())

    def add_package(self, module_name, class_name=None):
        """
        Adds a package and its modules to the package tree

        :param module_name: name of the module
        :param class_name: name of the class

        :package_library: PipelineManager.process_library.PackageLibrary object
        :package_library.package_tree: current package tree known in Package Library window
        :return:
        """

        self.packages = self.package_library.package_tree
        if module_name:

            # Reloading the package
            if module_name in sys.modules.keys():
                del sys.modules[module_name]

            try:
                __import__(module_name)
                pkg = sys.modules[module_name]

                # Checking if there are subpackages
                for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                    if ispkg:
                        self.add_package(str(module_name + '.' + modname))

                for k, v in sorted(list(pkg.__dict__.items())):
                    if class_name and k != class_name:
                        continue
                    # Checking each class of in the package
                    if inspect.isclass(v):
                        try:
                            find_in_path(k)
                            #get_process_instance(v)
                        except:
                            #TODO: WHICH TYPE OF EXCEPTION?
                            pass
                        else:
                            # Updating the tree's dictionnary
                            path_list = module_name.split('.')
                            path_list.append(k)
                            pkg_iter = self.packages
                            for element in path_list:
                                if element in pkg_iter.keys():
                                    pkg_iter = pkg_iter[element]
                                else:
                                    if element is path_list[-1]:
                                        pkg_iter[element] = 'process_enabled'
                                    else:
                                        pkg_iter[element] = {}
                                        pkg_iter = pkg_iter[element]

                self.package_library.package_tree = self.packages
                self.package_library.generate_tree()

            except Exception as err:
                msg = QMessageBox()
                msg.setText("{0}: {1}.".format(err.__class__, err))
                msg.setIcon(QMessageBox.Warning)
                msg.exec_()

    def remove_package_with_text(self):
        """
        Removes the package in the line edit from the package tree

        :return:
        """

        self.remove_package(self.line_edit.text())

    def remove_package(self, package):
        """
        Removes a package from the package tree

        :param package: module's representation as a string (e.g.: nipype.interfaces.spm)
        :return:
        """

        self.packages = self.package_library.package_tree
        if package:
            path_list = package.split('.')
            pkg_iter = self.packages

            for element in path_list:
                if element in pkg_iter.keys():
                    if element is not path_list[-1]:
                        pkg_iter = pkg_iter[element]
                    else:
                        del pkg_iter[element]
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Warning: Package not found in Package Library")
                    msg.setText("Package {0} not found".format(package))
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.buttonClicked.connect(msg.close)
                    msg.exec()
                    break

        self.package_library.package_tree = self.packages
        self.package_library.generate_tree()

    def save(self):
        """
        Saves the tree to the process_config.yml file

        :return:
        """

        # Updating the packages and the paths according to the package library tree
        self.packages = self.package_library.package_tree
        self.paths = self.package_library.paths

        if self.process_config:
            if self.process_config.get("Packages"):
                del self.process_config["Packages"]
            if self.process_config.get("Paths"):
                del self.process_config["Paths"]
        else:
            self.process_config = {}

        self.process_config["Packages"] = self.packages
        self.process_config["Paths"] = list(set(self.paths))

        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'w', encoding='utf8') as configfile:
            yaml.dump(self.process_config, configfile, default_flow_style=False, allow_unicode=True)
            self.signal_save.emit()


def import_file(full_name, path):
    """
    Import a python module from a path. 3.4+ only.

    Does not call sys.modules[full_name] = path

    :param full_name: name of the package
    :param path: path of the package
    :return: module
    """

    from importlib import util

    spec = util.spec_from_file_location(full_name, path)
    mod = util.module_from_spec(spec)

    spec.loader.exec_module(mod)
    return mod


class FileFilterProxyModel(QSortFilterProxyModel):
    """ Just a test for the moment. Should be useful to use in the file dialog. """
    def __init__(self):
        super(FileFilterProxyModel, self).__init__()

    def filterAcceptsRow(self, source_row, source_parent):
        source_model = self.sourceModel()
        index0 = source_model.index(source_row, 0, source_parent)
        # Always show directories
        if source_model.isDir(index0):
            return True
        # filter files
        filename = source_model.fileName(index0)
        #       filename=self.sourceModel().index(row,0,parent).data().lower()
        #return True
        if filename.count(".py") + filename.count(".xml") == 0:
            return False
        else:
            return True

    """def flags(self, index):
        flags = super(FileFilterProxyModel, self).flags(index)
        source_model = self.sourceModel()
        if source_model.isDir(index):
            flags |= Qt.ItemIsSelectable
            return flags

        # filter files
        filename = source_model.fileName(index)

        if filename.count(".py") + filename.count(".xml") == 0:
            flags &= ~Qt.ItemIsSelectable
            return flags
        else:
            flags |= Qt.ItemIsSelectable
            return flags"""


class PackageLibrary(QTreeWidget):
    """
    Tree that displays the user-added packages and their modules
    The user can check or not each module/package

    Attributes:
        - package_tree: representation of the packages as a tree-dictionary
        - paths: list of paths to add to the system to import the packages

    Methods:
        - update_checks: updates the checks of the tree from an item
        - set_module_view: sets if a module has to be enabled or disabled in the process library
        - recursive_checks: checks/unchecks all child items
        - recursive_checks_from_child: checks/unchecks all parent items
        - generate_tree: generates the package tree
        - fill_item: fills the items of the tree recursively
    """

    def __init__(self, package_tree, paths):
        """
        Initialization of the PackageLibrary widget
        :param package_tree: representation of the packages as a tree-dictionary
        :param paths: list of paths to add to the system to import the packages
        """

        super(PackageLibrary, self).__init__()

        self.itemChanged.connect(self.update_checks)
        self.package_tree = package_tree
        self.paths = paths
        self.generate_tree()
        self.setAlternatingRowColors(True)
        self.setHeaderLabel("Packages")

    def update_checks(self, item, column):
        """
        Updates the checks of the tree from an item

        :param item: item on which to begin
        :param column: column from the check (should always be 0)
        :return:
        """
        # Checked state is stored on column 0
        if column == 0:
            self.itemChanged.disconnect()
            if item.childCount():
                self.recursive_checks(item)
            if item.parent():
                self.recursive_checks_from_child(item)

            self.itemChanged.connect(self.update_checks)

    def set_module_view(self, item, state):
        """
        Sets if a module has to be enabled or disabled in the process library

        :param item: item selected in the current tree
        :param state: checked or not checked

        :Qt.Checked == 2. So if val == 2 -> checkbox is checked, and if val == 0 -> checkbox is not checked
        :pkg_iter: dictionary where keys are the name of a module (brick) and values are 'process_enabled' or 'process_disabled'. Key can be a submodule. In this case the value is a dictionary where keys are the name of a module (brick) and values are 'process_enabled' or 'process_dsabled'. etc. pkg_iter take only the modules concerning the top package where a change of status where done. 
        :return:
        """
        
        if state == Qt.Checked:
            val = 'process_enabled'
        else:
            val = 'process_disabled'

        list_path = []
        list_path.append(item.text(0))
        self.top_level_items = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]

        while item not in self.top_level_items:
            item = item.parent()
            list_path.append(item.text(0))

        pkg_iter = self.package_tree
        list_path = list(reversed(list_path))
        for element in list_path:
            if element in pkg_iter.keys():
                if element is list_path[-1]:
                    pkg_iter[element] = val
                else:
                    pkg_iter = pkg_iter[element]
            else:
                print('Package not found')
                break

    def recursive_checks(self, parent):
        """
        Checks/unchecks all child items

        :param parent: parent item
        :return:
        """

        check_state = parent.checkState(0)

        if parent.childCount() == 0:
            self.set_module_view(parent, check_state)

        for i in range(parent.childCount()):
            parent.child(i).setCheckState(0, check_state)
            self.recursive_checks(parent.child(i))

    def recursive_checks_from_child(self, child):
        """
        Checks/unchecks all parent items

        :param child: child item
        :return:
        """

        check_state = child.checkState(0)

        if child.childCount() == 0:
            self.set_module_view(child, check_state)

        if child.parent():
            parent = child.parent()
            if child.checkState(0) == Qt.Checked:
                if parent.checkState(0) == Qt.Unchecked:
                    parent.setCheckState(0, Qt.Checked)
                    self.recursive_checks_from_child(parent)
            else:
                # checked_children = []
                # for child in range(parent.childCount()):
                #
                #     if child.checkState(0) == Qt.Checked:
                #         checked_children.append()

                checked_children = [child for child in range(parent.childCount())
                                    if parent.child(child).checkState(0) == Qt.Checked]
                if not checked_children:
                    parent.setCheckState(0, Qt.Unchecked)
                    self.recursive_checks_from_child(parent)

    def generate_tree(self):
        """
        Generates the package tree

        :return:
        """

        self.itemChanged.disconnect()
        self.clear()
        self.fill_item(self.invisibleRootItem(), self.package_tree)
        self.itemChanged.connect(self.update_checks)

    def fill_item(self, item, value):
        """
        Fills the items of the tree recursively

        :param item: current item to fill
        :param value: value of the item in the tree
        :return:
        """

        item.setExpanded(True)

        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QTreeWidgetItem()
                child.setText(0, str(key))
                item.addChild(child)
                if type(val) is dict:
                    self.fill_item(child, val)
                else:
                    if val == 'process_enabled':
                        child.setCheckState(0, Qt.Checked)
                        self.recursive_checks_from_child(child)
                    elif val == 'process_disabled':
                        child.setCheckState(0, Qt.Unchecked)

        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, str(val))

                child.setExpanded(True)

        else:
            child = QTreeWidgetItem()
            child.setText(0, str(value))
            item.addChild(child)


class ProcessHelp(QWidget):
    ''' A widget that displays information about the selected process.
    '''
    def __init__(self, process):
        """ Generate the help.
        """
        super(ProcessHelp, self).__init__()

        label = QLabel()
        label.setText(process.help())


class InstallProcesses(QWidget):
    """
    A widget that allows to browse a Python package or a zip file to install the
    processes that it is containing.
    """

    process_installed = Signal()

    def __init__(self):
        super(InstallProcesses, self).__init__()

        v_layout = QVBoxLayout()
        self.setLayout(v_layout)

        label_text = 'Choose zip file containing Python packages'
        v_layout.addWidget(QLabel(label_text))

        edit_layout = QHBoxLayout()
        v_layout.addLayout(edit_layout)

        self.path_edit = QLineEdit()
        edit_layout.addWidget(self.path_edit)
        self.browser_button = QPushButton('Browse')
        edit_layout.addWidget(self.browser_button)

        bottom_layout = QHBoxLayout()
        v_layout.addLayout(bottom_layout)

        install_button = QPushButton('Install package')
        bottom_layout.addWidget(install_button)

        quit_button = QPushButton('Quit')
        bottom_layout.addWidget(quit_button)

        install_button.clicked.connect(self.install)
        quit_button.clicked.connect(self.close)
        self.browser_button.clicked.connect(self.get_filename)

    def get_filename(self):
        filename = QFileDialog.getOpenFileName(caption='Select a zip file',
                                               filter='Compatible files (*.zip)')
        if filename:
            self.path_edit.setText(filename[0])

    def install(self):

        def add_package(proc_dic, module_name):
            """
            Adds a package and its modules to the package tree


            :param proc_dic: the process tree-dictionary
            :param module_name: name of the module
            :return: proc_dic: the modified process tree-dictionary
            """

            if module_name:

                # Reloading the package
                if module_name in sys.modules.keys():
                    del sys.modules[module_name]

                __import__(module_name)
                pkg = sys.modules[module_name]

                # Checking if there are subpackages
                for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                    if ispkg:
                        add_package(proc_dic, str(module_name + '.' + modname))

                for k, v in sorted(list(pkg.__dict__.items())):
                    # Checking each class of in the package
                    if inspect.isclass(v):
                        try:
                            find_in_path(k)
                        except:
                            pass
                        else:
                            # Updating the tree's dictionnary
                            path_list = module_name.split('.')
                            path_list.append(k)
                            pkg_iter = proc_dic
                            for element in path_list:
                                if element in pkg_iter.keys():
                                    pkg_iter = pkg_iter[element]
                                else:
                                    if element is path_list[-1]:
                                        pkg_iter[element] = 'process_enabled'
                                    else:
                                        pkg_iter[element] = {}
                                        pkg_iter = pkg_iter[element]

                return proc_dic

        filename = self.path_edit.text()
        if not os.path.isfile(filename):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("The specified file cannot be found")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            return
        if os.path.splitext(filename)[1] != ".zip":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("The specified file has to be a .zip file")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(msg.close)
            msg.exec()
            return

        # Extraction of the zipped content
        zip_ref = zipfile.ZipFile(filename, 'r')
        zip_ref.extractall(os.path.join('..', '..', 'processes'))
        zip_ref.close()

        # Process config update
        if not os.path.isfile(os.path.join('..', '..', 'properties', 'process_config.yml')):
            open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'a').close()

        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'r') as stream:
            try:
                process_dic = yaml.load(stream)
            except yaml.YAMLError as exc:
                process_dic = {}
                print(exc)

        if process_dic is None:
            process_dic = {}

        try:
            packages = process_dic["Packages"]
        except KeyError:
            packages = {}
        except TypeError:
            packages = {}

        try:
            paths = process_dic["Paths"]
        except KeyError:
            paths = []
        except TypeError:
            paths = []

        package_name = os.path.splitext(os.path.basename(filename))[0]
        sys.path.append(os.path.join('..', '..', 'processes'))
        final_package_dic = add_package(packages, package_name)

        if not os.path.abspath(os.path.join('..', '..', 'processes')) in paths:
            paths.append(os.path.abspath(os.path.join('..', '..', 'processes')))

        process_dic["Packages"] = final_package_dic
        process_dic["Paths"] = paths
        # Idea: Should we encrypt the path ?

        with open(os.path.join('..', '..', 'properties', 'process_config.yml'), 'w', encoding='utf8') as stream:
            yaml.dump(process_dic, stream, default_flow_style=False, allow_unicode=True)

        self.process_installed.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    print('using Qt backend:', qt_backend.get_qt_backend())
    plw = ProcessLibraryWidget()
    plw.show()
    sys.exit(app.exec_())



################# OLD VERSION OF THE TREE VIEW (WITH A QTREEWIDGET)
'''class ProcessLibrary(QTreeWidget):
    """ A library that displays all the available processes.
    """
    def __init__(self, package_tree):
        """ Generate the library.
        """
        super(ProcessLibrary, self).__init__()
        self.setHeaderLabel("Available processes")
        self.package_tree = package_tree
        self.generate_tree()

    def generate_tree(self):
        self.clear()
        self.fill_item(self.invisibleRootItem(), self.package_tree)

    def fill_item(self, item, value):
        item.setExpanded(True)

        if type(value) is dict:
            for key, val in sorted(value.items()):
                child = QTreeWidgetItem()
                child.setText(0, str(key))
                if type(val) is dict:
                    item.addChild(child)
                    self.fill_item(child, val)
                else:
                    if val == 'process_enabled':
                        item.addChild(child)

        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, str(val))

                child.setExpanded(True)

        else:
            if value == 'process_enabled':
                child = QTreeWidgetItem()
                child.setText(0, str(value))
                item.addChild(child)

    def add_package(self, package):
        pass

    def remove_package(self, package):
        pass

'''
