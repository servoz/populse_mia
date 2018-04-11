import sys
import os
import yaml
import inspect
import pkgutil

# PyQt / PySide import, via soma
from soma.qt_gui import qt_backend
#qt_backend.set_qt_backend('PySide', pyqt_api=2, compatible_qt5=True)
from soma.qt_gui.qt_backend.QtCore import Qt, Signal, QModelIndex, \
    QAbstractItemModel, QByteArray, QMimeData
from soma.qt_gui.qt_backend.Qt import QWidget, QTreeWidget, QLabel, \
    QPushButton, QDialog, QTreeWidgetItem, QHBoxLayout, QVBoxLayout, \
    QLineEdit, QApplication, QSplitter, QFileDialog, QTreeView

# CAPSUL import
from capsul.api import get_process_instance, StudyConfig

# Soma import
from soma.path import find_in_path


class ProcessLibraryWidget(QWidget):
    ''' A widget that includes a process library and a package library.
    '''
    def __init__(self):
        """ Generate the widget.
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

        # Push button to call the package library
        push_button_pkg_lib = QPushButton()
        push_button_pkg_lib.setText('Package Library')
        push_button_pkg_lib.clicked.connect(self.open_pkg_lib)

        # Test to see the inputs/outputs of a process
        self.label_test = QLabel()

        # Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.label_test)
        self.splitter.addWidget(self.process_library)

        # Layout
        h_box = QHBoxLayout()
        h_box.addWidget(self.splitter)
        h_box.addWidget(push_button_pkg_lib)

        self.setLayout(h_box)

        self.pkg_library = PackageLibraryDialog()
        self.pkg_library.signal_save.connect(self.update_process_library)

    def display_parameters(self, item):
        """ This method was used to display the parameters of a process.
        It will be useful to generate processes in the near future.
        """

        study_config = StudyConfig(modules=StudyConfig.default_modules + ['NipypeConfig'])

        process_name = item.text(0)
        list_path = []
        while item is not self.process_library.topLevelItem(0):
            item = item.parent()
            list_path.append(item.text(0))

        list_path = list(reversed(list_path))
        package_name = '.'.join(list_path)

        __import__(package_name)
        pkg = sys.modules[package_name]

        for k, v in sorted(list(pkg.__dict__.items())):
            if k == process_name:
                try:
                    process = get_process_instance(v)
                except:
                    print('AIEEEE')
                    pass
                else:
                    print(process.get_inputs())
                txt = "Inputs: \n" + str(v.input_spec())
                txt2 = "\nOutputs: \n" + str(v.output_spec())
                self.label_test.setText(txt + txt2)

    def update_config(self):
        self.process_config = self.load_config()
        self.load_packages()

    def update_process_library(self):
        self.update_config()
        self.process_library.package_tree = self.packages
        self.process_library.load_dictionary(self.packages)

    def open_pkg_lib(self):
        self.pkg_library.show()

    @staticmethod
    def load_config():
        if not os.path.exists('process_config.yml'):
            open('process_config.yml', 'a').close()
        with open('process_config.yml', 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_packages(self):
        try:
            self.packages = self.process_config["Packages"]
        except KeyError:
            self.packages = {}
        except TypeError:
            self.packages = {}

    def save_config(self):
        self.process_config["Packages"] = self.packages
        with open('process_config.yml', 'w', encoding='utf8') as stream:
            yaml.dump(self.process_config, stream, default_flow_style=False, allow_unicode=True)

class Node(object):

    def __init__(self, name, parent=None):
        self._name = name
        self._parent = parent
        self._children = []
        self._value = None
        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return 'NODE'

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
            node = Node(name, parent)
            node = node_structure_from_dict(data, node, root_node)
        else:
            if data == 'process_enabled':
                node = Node(name, parent)
                node.value = data

    return root_node

class ProcessLibrary(QTreeView):
    """returns an object containing the tree of the given dictionary d.
    example:
    tree = DictionaryTree(d)
    tree.edit()
    d_edited = tree.dict()
    d_edited contains the dictionary with the edited data.
    this has to be refactored...
    """

    def __init__(self, d):
        super(ProcessLibrary, self).__init__()
        self.load_dictionary(d)

    def load_dictionary(self,d):
        """load a dictionary into my tree application"""
        self._d = d
        self._nodes = node_structure_from_dict(d)
        self._model = DictionaryTreeModel(self._nodes)
        self.setModel(self._model)
        self.expandAll()

    def to_dict(self):
        """returns a dictionary from the tree-data"""
        return self._model.to_dict()


class PackageLibraryDialog(QDialog):
    ''' A dialog that displays a package library.
    '''

    signal_save = Signal()

    def __init__(self):
        """ Generate the library.
        """
        super(PackageLibraryDialog, self).__init__()

        self.setWindowTitle("Package Library")

        self.process_config = self.load_config()
        self.load_packages()

        self.package_library = PackageLibrary(self.packages)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText('Type a package')

        push_button_browse = QPushButton()
        push_button_browse.setText("Browse")
        push_button_browse.clicked.connect(self.browse_package)

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

        h_box_browse = QHBoxLayout()
        h_box_browse.addWidget(self.line_edit)
        h_box_browse.addWidget(push_button_browse)

        v_box = QVBoxLayout()
        v_box.addLayout(h_box_browse)
        v_box.addWidget(push_button_add_pkg)
        v_box.addWidget(push_button_rm_pkg)
        v_box.addWidget(push_button_save)

        h_box = QHBoxLayout()
        h_box.addWidget(self.package_library)
        h_box.addLayout(v_box)

        self.setLayout(h_box)

    def load_config(self):
        with open('process_config.yml', 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_packages(self):
        try:
            self.packages = self.process_config["Packages"]
        except KeyError:
            self.packages = {}
        except TypeError:
            self.packages = {}

    def save_config(self):
        self.process_config["Packages"] = self.packages
        with open('process_config.yml', 'w', encoding='utf8') as stream:
            yaml.dump(self.process_config, stream, default_flow_style=False, allow_unicode=True)

    def browse_package(self):
        file_dialog = QFileDialog()
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        file_dialog.setFileMode(QFileDialog.Directory)

        python_path = os.environ['PYTHONPATH'].split(os.pathsep)
        python_path = python_path[0]
        file_dialog.setDirectory(python_path)

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            file_name = file_name.replace(python_path, '')
            file_name = file_name.replace('/', '.').replace('\\', '.')
            if len(file_name) != 0 and file_name[0] == '.':
                file_name = file_name[1:]

            self.line_edit.setText(file_name)

    def add_package_with_text(self):
        self.add_package(self.line_edit.text())

    def add_package(self, module):
        self.packages = self.package_library.package_tree
        if module:
            __import__(module)
            pkg = sys.modules[module]
            for importer, modname, ispkg in pkgutil.iter_modules(pkg.__path__):
                if ispkg:
                    self.add_package(str(module + '.' + modname))
                #else:
            for k, v in sorted(list(pkg.__dict__.items())):
                if inspect.isclass(v):
                    try:
                        find_in_path(k)
                        #get_process_instance(v)
                    except:
                        #TODO: WHICH TYPE OF EXCEPTION?
                        pass
                    else:
                        path_list = module.split('.')
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

    def remove_package_with_text(self):
        self.remove_package(self.line_edit.text())

    def remove_package(self, module):
        self.packages = self.package_library.package_tree
        if module:
            path_list = module.split('.')
            pkg_iter = self.packages

            for element in path_list:
                if element in pkg_iter.keys():
                    if element is not path_list[-1]:
                        pkg_iter = pkg_iter[element]
                    else:
                        del pkg_iter[element]
                else:
                    print('Package not found')
                    break

        self.package_library.package_tree = self.packages
        self.package_library.generate_tree()

    def save(self):
        # Updating the packages according to the package library tree
        self.packages = self.package_library.package_tree
        if self.process_config:
            if self.process_config.get("Packages"):
                del self.process_config["Packages"]
        else:
            self.process_config = {}
        self.process_config["Packages"] = self.packages
        with open('process_config.yml', 'w', encoding='utf8') as configfile:
            yaml.dump(self.process_config, configfile, default_flow_style=False, allow_unicode=True)
            self.signal_save.emit()


class PackageLibrary(QTreeWidget):
    ''' A library that displays all the available package.
    '''
    def __init__(self, package_tree):
        """ Generate the library.
        """
        super(PackageLibrary, self).__init__()

        self.itemChanged.connect(self.update_checks)
        self.package_tree = package_tree
        self.generate_tree()
        self.setAlternatingRowColors(True)
        self.setHeaderLabel("Packages")

    def update_checks(self, item, column):
        # Checked state is stored on column 0
        if column == 0:
            self.recursive_checks(item)

    def set_package_view(self, item, state):
        if state == Qt.Checked:
            val = 'process_enabled'
        else:
            val = 'process_disabled'

        list_path = []
        list_path.append(item.text(0))
        while item is not self.topLevelItem(0):
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
        check_state = parent.checkState(0)

        if parent.childCount() == 0:
            self.set_package_view(parent, check_state)

        for i in range(parent.childCount()):
            parent.child(i).setCheckState(0, check_state)
            self.recursive_checks(parent.child(i))

    def recursive_checks_from_child(self, child):

        if child is not self.topLevelItem(0):
            parent = child.parent()
            if parent.checkState(0) == Qt.Unchecked:
                parent.setCheckState(0, Qt.Checked)
                self.recursive_checks_from_child(parent)
        else:
            child.setCheckState(0, Qt.Checked)

    def generate_tree(self):
        self.itemChanged.disconnect()
        self.clear()
        self.fill_item(self.invisibleRootItem(), self.package_tree)
        self.itemChanged.connect(self.update_checks)

    def fill_item(self, item, value):
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