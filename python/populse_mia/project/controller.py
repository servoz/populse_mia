##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import glob
import os.path
import json
import hashlib  # To generate the md5 of each path
import datetime
from time import time, sleep
from datetime import datetime

# PyQt5 imports
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QProgressDialog

# Populse_MIA imports
from populse_mia.project.project import COLLECTION_CURRENT, COLLECTION_INITIAL, TAG_CHECKSUM, TAG_TYPE, TAG_FILENAME, \
    TYPE_NII
from populse_mia.project.database_mia import TAG_ORIGIN_BUILTIN, TAG_ORIGIN_USER

# Populse_db imports
from populse_db.database import FIELD_TYPE_STRING, FIELD_TYPE_DATETIME, FIELD_TYPE_DATE, FIELD_TYPE_TIME, \
    FIELD_TYPE_LIST_STRING, FIELD_TYPE_INTEGER, FIELD_TYPE_LIST_INTEGER, FIELD_TYPE_FLOAT, FIELD_TYPE_LIST_FLOAT, \
    FIELD_TYPE_BOOLEAN, FIELD_TYPE_LIST_BOOLEAN, FIELD_TYPE_LIST_DATE, FIELD_TYPE_LIST_DATETIME, FIELD_TYPE_LIST_TIME


def getJsonTagsFromFile(file_path, path):
    """
    Returns a list of [tag, value] contained in a Json file

    :param file_path: file path of the Json file (without the extension)
    :param path: project path
    :return: a list of the Json tags of the file
    """
    json_tags = []
    with open(os.path.join(path, file_path) + ".json") as f:
        for name, value in json.load(f).items():
            json_tags.append([name, value])
    return json_tags


def read_log(project, main_window):

    """
    From the log export file of the import software, the data base (here the current project) is loaded with the tags

    :param project: current project in the software
    :param main_window: software's main window
    :return: the scans that have been added
    """

    main_window.progress = ImportProgress(project)
    main_window.progress.show()
    main_window.progress.exec()

    return main_window.progress.worker.scans_added


class ImportProgress(QProgressDialog):
    """
    Import progress bar
    """
    def __init__(self, project):

        super(ImportProgress, self).__init__("Please wait while the paths are being imported...", None, 0, 3)

        self.setWindowTitle("Importing the paths")
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setModal(True)

        self.setMinimumDuration(0)
        self.setValue(0)

        self.worker = ImportWorker(project, self)
        self.worker.finished.connect(self.close)
        self.worker.notifyProgress.connect(self.onProgress)
        self.worker.start()

    def onProgress(self, i):
        """
        Signal to set the import progressbar value
        """

        self.setValue(i)


class ImportWorker(QThread):
    """
    Thread import
    """

    notifyProgress = pyqtSignal(int)

    def __init__(self, project, progress):
        super().__init__()
        self.project = project
        self.progress = progress

    def run(self):

        # import pprofile
        # prof = pprofile.Profile()
        # with prof():
        # import cProfile
        # pr = cProfile.Profile()
        # pr.enable()

        begin = time()

        raw_data_folder = os.path.relpath(os.path.join(self.project.folder, 'data', 'raw_data'))

        # Checking all the export logs from MRIManager and taking the most recent
        list_logs = glob.glob(os.path.join(raw_data_folder, "logExport*.json"))
        log_to_read = max(list_logs, key=os.path.getctime)

        with open(log_to_read, "r", encoding="utf-8") as file:
            list_dict_log = json.load(file)

        # For history
        historyMaker = []
        historyMaker.append("add_scans")
        self.scans_added = []
        values_added = []
        tags_added = []
        tags_names_added = []
        documents = {}

        tags_to_remove = ["Dataset data file", "Dataset header file"]  # List of tags to remove

        for dict_log in list_dict_log:

            if dict_log['StatusExport'] == "Export ok":
                file_name = dict_log['NameFile']
                path_name = raw_data_folder
                with open(os.path.join(path_name, file_name) + ".nii", 'rb') as scan_file:
                    data = scan_file.read()
                    original_md5 = hashlib.md5(data).hexdigest()

                file_path = os.path.join(raw_data_folder, file_name + ".nii")
                file_database_path = os.path.relpath(file_path, self.project.folder)

                document_not_existing = self.project.session.get_document(COLLECTION_CURRENT, file_database_path) is None
                if document_not_existing:
                    self.scans_added.append(file_database_path)  # Scan added to history

                documents[file_database_path] = {}
                documents[file_database_path][TAG_FILENAME] = file_database_path

                # For each tag in each scan
                for tag in getJsonTagsFromFile(file_name, path_name):

                    # We do the tag only if it's not in the tags to remove
                    if tag[0] not in tags_to_remove:
                        properties = tag[1]
                        unit = None
                        format = ''
                        tag_type = FIELD_TYPE_STRING
                        description = None
                        if isinstance(properties, dict):
                            value = properties['value']
                            unit = properties['units']
                            if unit == "":
                                unit = None
                            format = properties['format']
                            tag_type = properties['type']
                            if tag_type == "":
                                tag_type = FIELD_TYPE_STRING
                            description = properties['description']
                            if description == "":
                                description = None
                        else:
                            value = properties[0]

                        tag_name = tag[0]

                        # Creating date types
                        if format is not None and format != "":
                            format = format.replace("yyyy", "%Y")
                            format = format.replace("MM", "%m")
                            format = format.replace("dd", "%d")
                            format = format.replace("HH", "%H")
                            format = format.replace("mm", "%M")
                            format = format.replace("ss", "%S")
                            format = format.replace("SSS", "%f")
                            if "%Y" in format and "%m" in format and "%d" in format and "%H" in format and \
                                    "%M" in format and "%S" in format:
                                tag_type = FIELD_TYPE_DATETIME
                            elif "%Y" in format and "%m" in format and "%d" in format:
                                tag_type = FIELD_TYPE_DATE
                            elif "%H" in format and "%M" in format and "%S" in format:
                                tag_type = FIELD_TYPE_TIME

                        if tag_name != "Json_Version":
                            # Preparing value and type
                            if len(value) is 1:
                                value = value[0]
                            else:
                                if tag_type == FIELD_TYPE_STRING:
                                    tag_type = FIELD_TYPE_LIST_STRING
                                elif tag_type == FIELD_TYPE_INTEGER:
                                    tag_type = FIELD_TYPE_LIST_INTEGER
                                elif tag_type == FIELD_TYPE_FLOAT:
                                    tag_type = FIELD_TYPE_LIST_FLOAT
                                elif tag_type == FIELD_TYPE_BOOLEAN:
                                    tag_type = FIELD_TYPE_LIST_BOOLEAN
                                elif tag_type == FIELD_TYPE_DATE:
                                    tag_type = FIELD_TYPE_LIST_DATE
                                elif tag_type == FIELD_TYPE_DATETIME:
                                    tag_type = FIELD_TYPE_LIST_DATETIME
                                elif tag_type == FIELD_TYPE_TIME:
                                    tag_type = FIELD_TYPE_LIST_TIME
                                value_prepared = []
                                for value_single in value:
                                    value_prepared.append(value_single[0])
                                value = value_prepared

                        if tag_type == FIELD_TYPE_DATETIME or tag_type == FIELD_TYPE_DATE or \
                                tag_type == FIELD_TYPE_TIME:
                            if value is not None and value != "":
                                value = datetime.strptime(value, format)
                                if tag_type == FIELD_TYPE_TIME:
                                    value = value.time()
                                elif tag_type == FIELD_TYPE_DATE:
                                    value = value.date()

                        # TODO time lists

                        tag_row = self.project.session.get_field(COLLECTION_CURRENT, tag_name)
                        if tag_row is None and tag_name not in tags_names_added:
                            # Adding the tag as it's not in the database yet
                            tags_added.append(
                                [COLLECTION_CURRENT, tag_name, tag_type, description, False, TAG_ORIGIN_BUILTIN, unit,
                                 None])
                            tags_added.append(
                                [COLLECTION_INITIAL, tag_name, tag_type, description, False, TAG_ORIGIN_BUILTIN, unit,
                                 None])
                            tags_names_added.append(tag_name)

                        # The value is accepted if it's not empty or null
                        if value is not None and value != "":
                            if document_not_existing:
                                values_added.append(
                                    [file_database_path, tag_name, value, value])  # Value added to history
                            documents[file_database_path][tag_name] = value

                if document_not_existing:
                    # Tags added manually
                    values_added.append(
                        [file_database_path, TAG_CHECKSUM, original_md5, original_md5])  # Value added to history
                    values_added.append([file_database_path, TAG_TYPE, TYPE_NII, TYPE_NII])  # Value added to history
                documents[file_database_path][TAG_CHECKSUM] = original_md5
                documents[file_database_path][TAG_TYPE] = TYPE_NII

        # Missing values added thanks to default values
        for tag in self.project.session.get_fields(COLLECTION_CURRENT):
            if tag.origin == TAG_ORIGIN_USER:
                for scan in self.scans_added:
                    if tag.default_value is not None and self.project.session.get_value(COLLECTION_CURRENT, scan[0],
                                                                                        tag.name) is None:
                        values_added.append(
                            [scan, tag.name, tag.default_value, tag.default_value])  # Value added to history
                        documents[scan][tag.name] = tag.default_value

        self.notifyProgress.emit(1)
        sleep(0.1)

        self.project.session.add_fields(tags_added)

        self.notifyProgress.emit(2)
        sleep(0.1)

        current_paths = self.project.session.get_documents_names(COLLECTION_CURRENT)

        for document in documents:
            if document in current_paths:
                self.project.session.remove_document(COLLECTION_CURRENT, document)
                self.project.session.remove_document(COLLECTION_INITIAL, document)
            self.project.session.add_document(COLLECTION_CURRENT, documents[document], flush=False)
            self.project.session.add_document(COLLECTION_INITIAL, documents[document], flush=False)
        self.project.session.session.flush()

        self.notifyProgress.emit(3)
        sleep(0.1)

        # For history
        historyMaker.append(self.scans_added)
        historyMaker.append(values_added)
        self.project.undos.append(historyMaker)
        self.project.redos.clear()

        print('\nData export duration in the database:')
        print("read_log time: " + str(round(time() - begin, 2)) + ' s\n')
        # print("read_log time: " + str(time() - begin))

        # pr.disable()
        # pr.print_stats(sort='time')
        # prof.print_stats()


def verify_scans(project, path):
    """
    Checks if the project's scans have been modified

    :param project: current project in the software
    :param path:
    :return: the list of scans that have been modified
    """
    # Returning the files that are problematic
    return_list = []
    for scan in project.session.get_documents_names(COLLECTION_CURRENT):

        file_name = scan
        file_path = os.path.relpath(os.path.join(project.folder, file_name))

        if os.path.exists(file_path):
            # If the file exists, we do the checksum
            with open(file_path, 'rb') as scan_file:
                data = scan_file.read()
                actual_md5 = hashlib.md5(data).hexdigest()

            initial_checksum = project.session.get_value(COLLECTION_CURRENT, scan, TAG_CHECKSUM)
            if initial_checksum is not None and actual_md5 != initial_checksum:
                return_list.append(file_name)

        else:
            # Otherwise, we directly add the file in the list
            return_list.append(file_name)

    return return_list


def save_project(project):
    """
    Saves the modifications of the project
    
    :param project: current project in the software
    """
    project.saveModifications()
