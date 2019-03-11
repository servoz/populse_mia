##########################################################################
# Populse_mia - Copyright (C) IRMaGe/CEA, 2018
# Distributed under the terms of the CeCILL license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL_V2.1-en.html
# for details.
##########################################################################

import os
import sys

# Working from the scripts directory
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

from populse_db.database import FIELD_TYPE_INTEGER

os.chdir(os.path.dirname(os.path.realpath(__file__)))

import unittest

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from populse_mia.project.project import Project, COLLECTION_CURRENT, COLLECTION_INITIAL, COLLECTION_BRICK, \
    TAG_ORIGIN_USER, TAG_FILENAME, TAG_CHECKSUM, TAG_TYPE, TAG_BRICKS, TAG_EXP_TYPE
from populse_mia.main_window.main_window import MainWindow
from populse_mia.software_properties.config import Config
from capsul.api import get_process_instance


class TestMIADataBrowser(unittest.TestCase):

    def setUp(self):
        """
        Called before each test
        """

        # All the tests are run in regular mode
        config = Config()
        config.set_clinical_mode("no")

        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.project = Project(None, True)
        self.main_window = MainWindow(self.project, test=True)

    def tearDown(self):
        """
        Called after each test
        """

        self.main_window.project.unsaveModifications()
        self.main_window.close()

        # Removing the opened projects (in CI, the tests are run twice)
        config = Config()
        config.set_opened_projects([])
        config.saveConfig()

        self.app.exit()

    def test_unnamed_project_software_opening(self):
        """
        Tests unnamed project creation at software opening
        """

        self.assertIsInstance(self.project, Project)
        self.assertEqual(self.main_window.project.getName(), "Unnamed project")
        tags = self.main_window.project.session.get_fields_names(COLLECTION_CURRENT)
        self.assertEqual(len(tags), 5)
        self.assertTrue(TAG_CHECKSUM in tags)
        self.assertTrue(TAG_FILENAME in tags)
        self.assertTrue(TAG_TYPE in tags)
        self.assertTrue(TAG_EXP_TYPE in tags)
        self.assertTrue(TAG_BRICKS in tags)
        self.assertEqual(self.main_window.project.session.get_documents_names(COLLECTION_CURRENT), [])
        self.assertEqual(self.main_window.project.session.get_documents_names(COLLECTION_INITIAL), [])
        collections = self.main_window.project.session.get_collections_names()
        self.assertEqual(len(collections), 3)
        self.assertTrue(COLLECTION_INITIAL in collections)
        self.assertTrue(COLLECTION_CURRENT in collections)
        self.assertTrue(COLLECTION_BRICK in collections)
        self.assertEqual(self.main_window.windowTitle(), "MIA - Multiparametric Image Analysis - Unnamed project")

    def test_projects_removed_from_current_projects(self):
        """
        Tests that the projects are removed from the list of current projects
        """

        config = Config()
        projects = config.get_opened_projects()
        self.assertEqual(len(projects), 1)
        self.assertTrue(self.main_window.project.folder in projects)

    def test_open_project(self):
        """
        Tests project opening
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        self.assertEqual(self.main_window.project.getName(), "project_8")
        self.assertEqual(self.main_window.windowTitle(), "MIA - Multiparametric Image Analysis - project_8")
        documents = self.main_window.project.session.get_documents_names(COLLECTION_CURRENT)
        self.assertEqual(len(documents), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in documents)
        documents = self.main_window.project.session.get_documents_names(COLLECTION_INITIAL)
        self.assertEqual(len(documents), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in documents)

    def test_add_tag(self):
        """
        Tests the pop up adding a tag
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        # Testing without tag name
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(add_tag.msg.text(), "The tag name cannot be empty")

        QApplication.processEvents()

        # Testing with tag name already existing
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Type")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(add_tag.msg.text(), "This tag name already exists")

        QApplication.processEvents()

        # Testing with wrong type
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        add_tag.combo_box_type.setCurrentText(FIELD_TYPE_INTEGER)
        add_tag.type = FIELD_TYPE_INTEGER
        add_tag.text_edit_default_value.setText("Should be integer")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(add_tag.msg.text(), "Invalid default value")

        QApplication.processEvents()

        # Testing when everything is ok
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        add_tag.text_edit_default_value.setText("def_value")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))
        for document in self.main_window.project.session.get_documents_names(COLLECTION_CURRENT):
            self.assertEqual(self.main_window.project.session.get_value(COLLECTION_CURRENT, document, "Test"), "def_value")
        for document in self.main_window.project.session.get_documents_names(COLLECTION_INITIAL):
            self.assertEqual(self.main_window.project.session.get_value(COLLECTION_INITIAL, document, "Test"), "def_value")

        test_column = self.main_window.data_browser.table_data.get_tag_column("Test")
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, test_column)
            self.assertEqual(item.text(), "def_value")

        QApplication.processEvents()

        # Testing with list type
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test_list")
        add_tag.combo_box_type.setCurrentText("Integer List")
        QTest.mouseClick(add_tag.text_edit_default_value, Qt.LeftButton)
        QTest.mouseClick(add_tag.text_edit_default_value.list_creation.add_element_label, Qt.LeftButton)
        QTest.mouseClick(add_tag.text_edit_default_value.list_creation.add_element_label, Qt.LeftButton)
        table = add_tag.text_edit_default_value.list_creation.table
        item = QTableWidgetItem()
        item.setText(str(1))
        table.setItem(0, 0, item)
        item = QTableWidgetItem()
        item.setText(str(2))
        table.setItem(0, 1, item)
        item = QTableWidgetItem()
        item.setText(str(3))
        table.setItem(0, 2, item)
        QTest.mouseClick(add_tag.text_edit_default_value.list_creation.ok_button, Qt.LeftButton)
        self.assertEqual(add_tag.text_edit_default_value.text(), "[1, 2, 3]")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)

        test_list_column = self.main_window.data_browser.table_data.get_tag_column("Test_list")
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, test_list_column)
            self.assertEqual(item.text(), "[1, 2, 3]")

        QApplication.processEvents()

    def test_clone_tag(self):
        """
        Tests the pop up cloning a tag
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        # Testing without new tag name
        self.main_window.data_browser.clone_tag_action.trigger()
        clone_tag = self.main_window.data_browser.pop_up_clone_tag
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(clone_tag.msg.text(), "The tag name can't be empty")

        # Testing without any tag selected to clone
        self.main_window.data_browser.clone_tag_action.trigger()
        clone_tag = self.main_window.data_browser.pop_up_clone_tag
        clone_tag.line_edit_new_tag_name.setText("Test")
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(clone_tag.msg.text(), "The tag to clone must be selected")

        # Testing with tag name already existing
        self.main_window.data_browser.clone_tag_action.trigger()
        clone_tag = self.main_window.data_browser.pop_up_clone_tag
        clone_tag.line_edit_new_tag_name.setText("Type")
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(clone_tag.msg.text(), "This tag name already exists")

        self.main_window.data_browser.clone_tag_action.trigger()
        clone_tag = self.main_window.data_browser.pop_up_clone_tag
        clone_tag.line_edit_new_tag_name.setText("Test")
        clone_tag.search_bar.setText("BandWidth")
        clone_tag.list_widget_tags.setCurrentRow(0) # BandWidth tag selected
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))
        test_row = self.main_window.project.session.get_field(COLLECTION_CURRENT, "Test")
        bandwidth_row = self.main_window.project.session.get_field(COLLECTION_CURRENT, "BandWidth")
        self.assertEqual(test_row.description, bandwidth_row.description)
        self.assertEqual(test_row.unit, bandwidth_row.unit)
        self.assertEqual(test_row.default_value, bandwidth_row.default_value)
        self.assertEqual(test_row.type, bandwidth_row.type)
        self.assertEqual(test_row.origin, TAG_ORIGIN_USER)
        self.assertEqual(test_row.visibility, True)
        test_row = self.main_window.project.session.get_field(COLLECTION_INITIAL, "Test")
        bandwidth_row = self.main_window.project.session.get_field(COLLECTION_INITIAL, "BandWidth")
        self.assertEqual(test_row.description, bandwidth_row.description)
        self.assertEqual(test_row.unit, bandwidth_row.unit)
        self.assertEqual(test_row.default_value, bandwidth_row.default_value)
        self.assertEqual(test_row.type, bandwidth_row.type)
        self.assertEqual(test_row.origin, TAG_ORIGIN_USER)
        self.assertEqual(test_row.visibility, True)

        for document in self.main_window.project.session.get_documents_names(COLLECTION_CURRENT):
            self.assertEqual(self.main_window.project.session.get_value(COLLECTION_CURRENT, document, "Test"), self.main_window.project.session.get_value(COLLECTION_CURRENT, document, "BandWidth"))
        for document in self.main_window.project.session.get_documents_names(COLLECTION_INITIAL):
            self.assertEqual(self.main_window.project.session.get_value(COLLECTION_INITIAL, document, "Test"), self.main_window.project.session.get_value(COLLECTION_INITIAL, document, "BandWidth"))

        test_column = self.main_window.data_browser.table_data.get_tag_column("Test")
        bw_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item_bw = self.main_window.data_browser.table_data.item(row, bw_column)
            item_test = self.main_window.data_browser.table_data.item(row, test_column)
            self.assertEqual(item_bw.text(), item_test.text())

    def test_remove_tag(self):
        """
        Tests the popup removing user tags
        """

        # Adding a tag
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)

        old_tags_current = self.main_window.project.session.get_fields_names(COLLECTION_CURRENT)
        old_tags_initial = self.main_window.project.session.get_fields_names(COLLECTION_INITIAL)
        self.main_window.data_browser.remove_tag_action.trigger()
        remove_tag = self.main_window.data_browser.pop_up_remove_tag
        QTest.mouseClick(remove_tag.push_button_ok, Qt.LeftButton)
        new_tags_current = self.main_window.project.session.get_fields_names(COLLECTION_CURRENT)
        new_tags_initial = self.main_window.project.session.get_fields_names(COLLECTION_INITIAL)
        self.assertTrue(old_tags_current == new_tags_current)
        self.assertTrue(old_tags_initial == new_tags_initial)

        old_tags_current = self.main_window.project.session.get_fields_names(COLLECTION_CURRENT)
        old_tags_initial = self.main_window.project.session.get_fields_names(COLLECTION_INITIAL)
        self.assertTrue("Test" in old_tags_current)
        self.assertTrue("Test" in old_tags_initial)
        self.main_window.data_browser.remove_tag_action.trigger()
        remove_tag = self.main_window.data_browser.pop_up_remove_tag
        remove_tag.list_widget_tags.setCurrentRow(0) # Test tag selected
        QTest.mouseClick(remove_tag.push_button_ok, Qt.LeftButton)
        new_tags_current = self.main_window.project.session.get_fields_names(COLLECTION_CURRENT)
        new_tags_initial = self.main_window.project.session.get_fields_names(COLLECTION_INITIAL)
        self.assertTrue("Test" not in new_tags_current)
        self.assertTrue("Test" not in new_tags_initial)

    def test_visualized_tags(self):
        """
        Tests the popup modifying the visualized tags
        """

        # Testing default tags visibility
        visibles = self.main_window.project.session.get_visibles()
        self.assertEqual(len(visibles), 4)
        self.assertTrue(TAG_FILENAME in visibles)
        self.assertTrue(TAG_BRICKS in visibles)
        self.assertTrue(TAG_TYPE in visibles)
        self.assertTrue(TAG_EXP_TYPE in visibles)

        # Testing columns displayed in the databrowser
        self.assertEqual(self.main_window.data_browser.table_data.columnCount(), 4)
        columns_displayed = []
        for column in range (0, self.main_window.data_browser.table_data.columnCount()):
            tag_displayed = self.main_window.data_browser.table_data.horizontalHeaderItem(column).text()
            if not self.main_window.data_browser.table_data.isColumnHidden(column):
                columns_displayed.append(tag_displayed)
        self.assertEqual(sorted(visibles), sorted(columns_displayed))

        # Testing that FileName tag is the first column
        self.assertEqual(self.main_window.data_browser.table_data.horizontalHeaderItem(0).text(), TAG_FILENAME)

        # Trying to set the visibles tags
        QTest.mouseClick(self.main_window.data_browser.visualized_tags_button, Qt.LeftButton)
        settings = self.main_window.data_browser.table_data.pop_up

        # Testing that checksum tag isn't displayed
        settings.tab_tags.search_bar.setText(TAG_CHECKSUM)
        self.assertEqual(settings.tab_tags.list_widget_tags.count(), 0)

        # Testing that FileName is not displayed in the list of visible tags
        settings.tab_tags.search_bar.setText("")
        visibles_tags = []
        for row in range (0, settings.tab_tags.list_widget_selected_tags.count()):
            item = settings.tab_tags.list_widget_selected_tags.item(row).text()
            visibles_tags.append(item)
        self.assertEqual(len(visibles_tags), 3)
        self.assertTrue(TAG_BRICKS in visibles_tags)
        self.assertTrue(TAG_EXP_TYPE in visibles_tags)
        self.assertTrue(TAG_TYPE in visibles_tags)

        # Testing when hiding a tag
        settings.tab_tags.list_widget_selected_tags.item(0).setSelected(True) # Bricks tag selected
        QTest.mouseClick(settings.tab_tags.push_button_unselect_tag, Qt.LeftButton)
        visibles_tags = []
        for row in range(0, settings.tab_tags.list_widget_selected_tags.count()):
            item = settings.tab_tags.list_widget_selected_tags.item(row).text()
            visibles_tags.append(item)
        self.assertEqual(len(visibles_tags), 2)
        self.assertTrue(TAG_TYPE in visibles_tags)
        self.assertTrue(TAG_EXP_TYPE in visibles_tags)
        QTest.mouseClick(settings.push_button_ok, Qt.LeftButton)

        new_visibles = self.main_window.project.session.get_visibles()
        self.assertEqual(len(new_visibles), 3)
        self.assertTrue(TAG_FILENAME in new_visibles)
        self.assertTrue(TAG_EXP_TYPE in new_visibles)
        self.assertTrue(TAG_TYPE in new_visibles)

        columns_displayed = []
        for column in range(0, self.main_window.data_browser.table_data.columnCount()):
            item = self.main_window.data_browser.table_data.horizontalHeaderItem(column)
            if not self.main_window.data_browser.table_data.isColumnHidden(column):
                columns_displayed.append(item.text())
        self.assertEqual(len(columns_displayed), 3)
        self.assertTrue(TAG_FILENAME in columns_displayed)
        self.assertTrue(TAG_EXP_TYPE in columns_displayed)
        self.assertTrue(TAG_TYPE in columns_displayed)

        # Testing when showing a new tag
        QTest.mouseClick(self.main_window.data_browser.visualized_tags_button, Qt.LeftButton)
        settings = self.main_window.data_browser.table_data.pop_up
        settings.tab_tags.search_bar.setText(TAG_BRICKS)
        settings.tab_tags.list_widget_tags.item(0).setSelected(True)
        QTest.mouseClick(settings.tab_tags.push_button_select_tag, Qt.LeftButton)
        QTest.mouseClick(settings.push_button_ok, Qt.LeftButton)

        new_visibles = self.main_window.project.session.get_visibles()
        self.assertEqual(len(new_visibles), 4)
        self.assertTrue(TAG_FILENAME in new_visibles)
        self.assertTrue(TAG_EXP_TYPE in new_visibles)
        self.assertTrue(TAG_TYPE in new_visibles)
        self.assertTrue(TAG_BRICKS in new_visibles)

        columns_displayed = []
        for column in range(0, self.main_window.data_browser.table_data.columnCount()):
            item = self.main_window.data_browser.table_data.horizontalHeaderItem(column)
            if not self.main_window.data_browser.table_data.isColumnHidden(column):
                columns_displayed.append(item.text())
        self.assertEqual(len(columns_displayed), 4)
        self.assertTrue(TAG_FILENAME in columns_displayed)
        self.assertTrue(TAG_EXP_TYPE in columns_displayed)
        self.assertTrue(TAG_TYPE in columns_displayed)
        self.assertTrue(TAG_BRICKS in columns_displayed)

    def test_rapid_search(self):
        """
        Tests the rapid search bar
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        # Checking that the 8 scans are shown in the databrowser
        self.assertEqual(self.main_window.data_browser.table_data.rowCount(), 9)
        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Testing G1 rapid search
        self.main_window.data_browser.search_bar.setText("G1")
        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 2)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Testing that all the scans are back when clicking on the cross
        QTest.mouseClick(self.main_window.data_browser.button_cross, Qt.LeftButton)

        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Testing not defined values
        QTest.mouseClick(self.main_window.data_browser.button_cross, Qt.LeftButton)
        self.main_window.data_browser.search_bar.setText("*Not Defined*")
        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(scans_displayed, ["data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii"])

    def test_advanced_search(self):
        """
        Tests the advanced search widget
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        QTest.mouseClick(self.main_window.data_browser.advanced_search_button, Qt.LeftButton)

        # Testing - and + buttons
        self.assertEqual(len(self.main_window.data_browser.advanced_search.rows), 1)
        first_row = self.main_window.data_browser.advanced_search.rows[0]
        QTest.mouseClick(first_row[6], Qt.LeftButton)
        self.assertEqual(len(self.main_window.data_browser.advanced_search.rows), 2)
        second_row = self.main_window.data_browser.advanced_search.rows[1]
        QTest.mouseClick(second_row[5], Qt.LeftButton)
        self.assertEqual(len(self.main_window.data_browser.advanced_search.rows), 1)
        first_row = self.main_window.data_browser.advanced_search.rows[0]
        QTest.mouseClick(first_row[5], Qt.LeftButton)
        self.assertEqual(len(self.main_window.data_browser.advanced_search.rows), 1)

        field = self.main_window.data_browser.advanced_search.rows[0][2]
        condition = self.main_window.data_browser.advanced_search.rows[0][3]
        value = self.main_window.data_browser.advanced_search.rows[0][4]
        field_filename_index = field.findText(TAG_FILENAME)
        field.setCurrentIndex(field_filename_index)
        condition_contains_index = condition.findText("CONTAINS")
        condition.setCurrentIndex(condition_contains_index)
        value.setText("G1")
        QTest.mouseClick(self.main_window.data_browser.advanced_search.search, Qt.LeftButton)

        # Testing that only G1 scans are displayed with the filter applied
        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 2)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Testing that every scan is back when clicking again on advanced search
        QTest.mouseClick(self.main_window.data_browser.advanced_search_button, Qt.LeftButton)
        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

    def test_remove_scan(self):
        """
        Tests scans removal in the databrowser
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Trying to remove a scan
        self.main_window.data_browser.table_data.selectRow(0)
        self.main_window.data_browser.table_data.remove_scan()

        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 8)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans_displayed)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

    def test_set_value(self):
        """
        Tests the values modifications
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"))
        bandwidth_column  = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        G1_bandwidth_databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, G1_bandwidth_databrowser)
        self.assertEqual(value, value_initial)

        item.setSelected(True)
        item.setText("25000")

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        G1_bandwidth_databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, G1_bandwidth_databrowser)
        self.assertEqual(value_initial, float(50000))

    def test_reset_cell(self):
        """
        Tests the method resetting the selected cells
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        bandwidth_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)
        item.setSelected(True)

        item.setText("25000")

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value_initial, float(50000))

        self.main_window.data_browser.table_data.itemChanged.disconnect()
        self.main_window.data_browser.table_data.reset_cell()
        self.main_window.data_browser.table_data.itemChanged.connect(
        self.main_window.data_browser.table_data.change_cell_color)

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)

    def test_reset_column(self):
        """
        Tests the method resetting the columns selected
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        bandwidth_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)
        item.setSelected(True)

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(1, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)
        item.setSelected(True)

        item.setText("70000")

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(70000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value_initial, float(50000))

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(1, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(70000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value_initial, float(25000))

        self.main_window.data_browser.table_data.itemChanged.disconnect()
        self.main_window.data_browser.table_data.reset_column()
        self.main_window.data_browser.table_data.itemChanged.connect(self.main_window.data_browser.table_data.change_cell_color)

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)

        value = float(self.main_window.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                              "BandWidth"))
        value_initial = float(self.main_window.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                 "BandWidth"))
        item = self.main_window.data_browser.table_data.item(1, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)

    def test_reset_row(self):
        """
        Tests row reset
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        bw_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")

        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        old_bw = bw_item.text()
        self.assertEqual(int(old_bw), 50000)

        bw_item.setSelected(True)
        bw_item.setText("25000")
        set_item = self.main_window.data_browser.table_data.item(0, bw_column)
        set_bw = set_item.text()
        self.assertEqual(int(set_bw), 25000)

        self.main_window.data_browser.table_data.clearSelection()

        item = self.main_window.data_browser.table_data.item(0, 0)
        item.setSelected(True)
        self.main_window.data_browser.table_data.itemChanged.disconnect()
        self.main_window.data_browser.table_data.reset_row()
        self.main_window.data_browser.table_data.itemChanged.connect(
            self.main_window.data_browser.table_data.change_cell_color)

        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        new_bw = bw_item.text()
        self.assertEqual(int(new_bw), 50000)

    def test_add_path(self):
        """
        Tests the popup to add a path
        """

        QTest.mouseClick(self.main_window.data_browser.addRowLabel, Qt.LeftButton)
        add_path = self.main_window.data_browser.table_data.pop_up_add_path

        QTest.mouseClick(add_path.ok_button, Qt.LeftButton)
        self.assertEqual(add_path.msg.text(), "Invalid arguments")

        add_path.file_line_edit.setText(os.path.join(".", "test_not_existing.py"))
        add_path.type_line_edit.setText("Python")
        QTest.mouseClick(add_path.ok_button, Qt.LeftButton)
        self.assertEqual(add_path.msg.text(), "Invalid arguments")

        add_path.file_line_edit.setText(os.path.join(".", "test.py"))
        add_path.type_line_edit.setText("Python")
        QTest.mouseClick(add_path.ok_button, Qt.LeftButton)

        self.assertEqual(self.main_window.project.session.get_documents_names(COLLECTION_CURRENT),
                         [os.path.join('data', 'downloaded_data', 'test.py')])
        self.assertEqual(self.main_window.project.session.get_documents_names(COLLECTION_INITIAL),
                         [os.path.join('data', 'downloaded_data', 'test.py')])
        self.assertEqual(self.main_window.data_browser.table_data.rowCount(), 1)
        self.assertEqual(self.main_window.data_browser.table_data.item(0, 0).text(), os.path.join('data',
                                                                                                  'downloaded_data',
                                                                                                  'test.py'))

    def test_send_documents_to_pipeline(self):
        """
        Tests the popup sending the documents to the pipeline manager
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        # Checking that the pipeline manager has an empty list at the beginning
        self.assertEqual(self.main_window.pipeline_manager.scan_list, [])

        # Sending the selection (all scans), but closing the popup
        QTest.mouseClick(self.main_window.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.main_window.data_browser.show_selection
        send_popup.close()

        # Checking that the list is stil empty
        self.assertEqual(self.main_window.pipeline_manager.scan_list, [])

        # Sending the selection (all scans)
        QTest.mouseClick(self.main_window.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.main_window.data_browser.show_selection
        send_popup.ok_clicked()

        # Checking that all scans have been sent to the pipeline manager
        scans = self.main_window.pipeline_manager.scan_list
        self.assertEqual(len(scans), 9)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in scans)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans)

        # Selecting the first 2 scans
        item1 = self.main_window.data_browser.table_data.item(0, 0)
        item1.setSelected(True)
        scan1 = item1.text()
        item2 = self.main_window.data_browser.table_data.item(1, 0)
        scan2 = item2.text()
        item2.setSelected(True)

        # Sending the selection (first 2 scans)
        QTest.mouseClick(self.main_window.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.main_window.data_browser.show_selection
        send_popup.ok_clicked()

        # Checking that the first 2 scans have been sent to the pipeline manager
        scans = self.main_window.pipeline_manager.scan_list
        self.assertEqual(len(scans), 2)
        self.assertTrue(scan1 in scans)
        self.assertTrue(scan2 in scans)

        # Testing with the rapid search
        self.main_window.data_browser.table_data.clearSelection()
        self.main_window.data_browser.search_bar.setText("G3")

        # Sending the selection (G3 scans)
        QTest.mouseClick(self.main_window.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.main_window.data_browser.show_selection
        send_popup.ok_clicked()

        # Checking that G3 scans have been sent to the pipeline manager
        scans = self.main_window.pipeline_manager.scan_list
        self.assertEqual(len(scans), 2)
        self.assertTrue(
            "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans)
        self.assertTrue(
            "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans)

    def test_sort(self):
        """
        Tests the sorting in the databrowser
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        mixed_bandwidths = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            bandwidth_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
            item = self.main_window.data_browser.table_data.item(row, bandwidth_column)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                mixed_bandwidths.append(scan_name)

        self.main_window.data_browser.table_data.horizontalHeader().setSortIndicator(bandwidth_column, 0)

        up_bandwidths = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            bandwidth_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
            item = self.main_window.data_browser.table_data.item(row, bandwidth_column)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                up_bandwidths.append(scan_name)

        self.assertNotEqual(mixed_bandwidths, up_bandwidths)
        self.assertEqual(sorted(mixed_bandwidths), up_bandwidths)

        self.main_window.data_browser.table_data.horizontalHeader().setSortIndicator(bandwidth_column, 1)

        down_bandwidths = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            bandwidth_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
            item = self.main_window.data_browser.table_data.item(row, bandwidth_column)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                down_bandwidths.append(scan_name)

        self.assertNotEqual(mixed_bandwidths, down_bandwidths)
        self.assertEqual(sorted(mixed_bandwidths, reverse=True), down_bandwidths)

    def test_mia_preferences(self):
        """
        Tests the MIA preferences popup
        """

        config = Config()
        old_auto_save = config.isAutoSave()
        self.assertEqual(old_auto_save, "no")

        # Auto save activated
        self.main_window.action_software_preferences.trigger()
        properties = self.main_window.pop_up_preferences
        properties.tab_widget.setCurrentIndex(1)
        properties.save_checkbox.setChecked(True)
        QTest.mouseClick(properties.push_button_ok, Qt.LeftButton)

        config = Config()
        new_auto_save = config.isAutoSave()
        self.assertEqual(new_auto_save, "yes")

        # Auto save disabled again
        self.main_window.action_software_preferences.trigger()
        properties = self.main_window.pop_up_preferences
        properties.tab_widget.setCurrentIndex(1)
        properties.save_checkbox.setChecked(False)
        QTest.mouseClick(properties.push_button_ok, Qt.LeftButton)
        config = Config()
        reput_auto_save = config.isAutoSave()
        self.assertEqual(reput_auto_save, "no")

        # Checking that the changes are not effective if cancel is clicked
        self.main_window.action_software_preferences.trigger()
        properties = self.main_window.pop_up_preferences
        properties.tab_widget.setCurrentIndex(1)
        properties.save_checkbox.setChecked(True)
        QTest.mouseClick(properties.push_button_cancel, Qt.LeftButton)
        config = Config()
        auto_save = config.isAutoSave()
        self.assertEqual(auto_save, "no")

        # Checking that the values for the "Projects preferences" are well set
        self.assertEqual(config.get_max_projects(), 5.0)
        self.assertEqual(config.get_projects_save_path(), os.path.join(config.get_mia_path(), 'projects'))

    def test_undo_redo_databrowser(self):
        """
        Tests the databrowser undo/redo
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        self.assertEqual(self.main_window.project.undos, [])
        self.assertEqual(self.main_window.project.redos, [])

        # Testing modified value undo/redo
        bw_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        bw_old = bw_item.text()
        self.assertEqual(int(bw_old), 50000)
        bw_item.setSelected(True)
        bw_item.setText("0")
        self.assertEqual(self.main_window.project.undos, [['modified_values', [['data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii', 'BandWidth', 50000.0, 0.0]]]])
        self.assertEqual(self.main_window.project.redos, [])
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        bw_set = bw_item.text()
        self.assertEqual(int(bw_set), 0)
        self.main_window.action_undo.trigger()
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        bw_undo = bw_item.text()
        self.assertEqual(int(bw_undo), 50000)
        self.assertEqual(self.main_window.project.redos, [['modified_values', [[
                                                                                   'data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii',
                                                                                   'BandWidth', 50000.0, 0.0]]]])
        self.assertEqual(self.main_window.project.undos, [])
        self.main_window.action_redo.trigger()
        self.assertEqual(self.main_window.project.undos, [['modified_values', [[
                                                                                   'data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii',
                                                                                   'BandWidth', 50000.0, 0.0]]]])
        self.assertEqual(self.main_window.project.redos, [])
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        bw_redo = bw_item.text()
        self.assertEqual(int(bw_redo), 0)

        # Testing scan removal undo/redo
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_CURRENT)), 9)
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_INITIAL)), 9)
        self.main_window.data_browser.table_data.selectRow(0)
        self.main_window.data_browser.table_data.remove_scan()
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_CURRENT)), 8)
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_INITIAL)), 8)
        self.main_window.action_undo.trigger()
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_CURRENT)), 9)
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_INITIAL)), 9)
        self.main_window.action_redo.trigger()
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_CURRENT)), 8)
        self.assertEqual(len(self.main_window.project.session.get_documents_names(COLLECTION_INITIAL)), 8)

        # Testing add tag undo/redo
        self.main_window.data_browser.add_tag_action.trigger()
        add_tag = self.main_window.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))
        self.main_window.action_undo.trigger()
        self.assertFalse("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertFalse("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))
        self.main_window.action_redo.trigger()
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))

        # Testing remove tag undo/redo
        self.main_window.data_browser.remove_tag_action.trigger()
        remove_tag = self.main_window.data_browser.pop_up_remove_tag
        remove_tag.list_widget_tags.setCurrentRow(0)  # Test tag selected
        QTest.mouseClick(remove_tag.push_button_ok, Qt.LeftButton)
        self.assertFalse("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertFalse("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))
        self.main_window.action_undo.trigger()
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))
        self.main_window.action_redo.trigger()
        self.assertFalse("Test" in self.main_window.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertFalse("Test" in self.main_window.project.session.get_fields_names(COLLECTION_INITIAL))

    def test_count_table(self):
        """
        Tests the count table popup
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        QTest.mouseClick(self.main_window.data_browser.count_table_button, Qt.LeftButton)
        count_table = self.main_window.data_browser.count_table_pop_up
        self.assertEqual(len(count_table.push_buttons), 2)

        count_table.push_buttons[0].setText("BandWidth")
        count_table.fill_values(0)
        count_table.push_buttons[1].setText("EchoTime")
        count_table.fill_values(1)
        QTest.mouseClick(count_table.push_button_count, Qt.LeftButton)

        # Trying to add and remove tag buttons
        QTest.mouseClick(count_table.add_tag_label, Qt.LeftButton)
        self.assertEqual(len(count_table.push_buttons), 3)
        QTest.mouseClick(count_table.remove_tag_label, Qt.LeftButton)
        self.assertEqual(len(count_table.push_buttons), 2)

        self.assertEqual(count_table.push_buttons[0].text(), "BandWidth")
        self.assertEqual(count_table.push_buttons[1].text(), "EchoTime")

        QApplication.processEvents()

        self.assertEqual(count_table.table.horizontalHeaderItem(0).text(), "BandWidth")
        self.assertEqual(count_table.table.horizontalHeaderItem(1).text(), "75")
        self.assertEqual(count_table.table.horizontalHeaderItem(2).text(), "5.8239923")
        self.assertEqual(count_table.table.horizontalHeaderItem(3).text(), "5")
        self.assertEqual(count_table.table.verticalHeaderItem(3).text(), "Total")
        self.assertEqual(count_table.table.item(0, 0).text(), "50000")
        self.assertEqual(count_table.table.item(1, 0).text(), "25000")
        self.assertEqual(count_table.table.item(2, 0).text(), "65789.48")
        self.assertEqual(count_table.table.item(3, 0).text(), "3")
        self.assertEqual(count_table.table.item(0, 1).text(), "2")
        self.assertEqual(count_table.table.item(1, 1).text(), "")
        self.assertEqual(count_table.table.item(2, 1).text(), "")
        self.assertEqual(count_table.table.item(3, 1).text(), "2")
        self.assertEqual(count_table.table.item(0, 2).text(), "")
        self.assertEqual(count_table.table.item(1, 2).text(), "2")
        self.assertEqual(count_table.table.item(2, 2).text(), "")
        self.assertEqual(count_table.table.item(3, 2).text(), "2")
        self.assertEqual(count_table.table.item(0, 3).text(), "")
        self.assertEqual(count_table.table.item(1, 3).text(), "")
        self.assertEqual(count_table.table.item(2, 3).text(), "5")
        self.assertEqual(count_table.table.item(3, 3).text(), "5")

    def test_clear_cell(self):
        """
        Tests the method clearing cells
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        # Selecting a cell
        bw_column = self.main_window.data_browser.table_data.get_tag_column("BandWidth")
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        bw_item.setSelected(True)
        self.assertEqual(int(bw_item.text()), 50000)
        self.assertEqual(self.main_window.project.session.get_value(COLLECTION_CURRENT, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"), 50000)

        # Clearing the cell
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        bw_item.setSelected(True)
        self.main_window.data_browser.table_data.itemChanged.disconnect()
        self.main_window.data_browser.table_data.clear_cell()
        self.main_window.data_browser.table_data.itemChanged.connect(self.main_window.data_browser.table_data.change_cell_color)

        # Checking that it's empty
        bw_item = self.main_window.data_browser.table_data.item(0, bw_column)
        self.assertEqual(bw_item.text(), "*Not Defined*")
        self.assertIsNone(self.main_window.project.session.get_value(COLLECTION_CURRENT, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"))

    def test_open_project_filter(self):
        """
        Tests project filter opening
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        self.main_window.data_browser.open_filter_action.trigger()
        open_popup = self.main_window.data_browser.popUp
        open_popup.list_widget_filters.item(0).setSelected(True)
        QTest.mouseClick(open_popup.push_button_ok, Qt.LeftButton)

        scans_displayed = []
        for row in range(0, self.main_window.data_browser.table_data.rowCount()):
            item = self.main_window.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.main_window.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 2)
        self.assertTrue(
            "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue(
            "data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

    def test_brick_history(self):
        """
        Tests the brick history popup
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        bricks_column = self.main_window.data_browser.table_data.get_tag_column("Bricks")
        bricks_widget = self.main_window.data_browser.table_data.cellWidget(8, bricks_column)
        smmooth_button = bricks_widget.children()[1]
        self.assertEqual(smmooth_button.text(), "smooth1")
        QTest.mouseClick(smmooth_button, Qt.LeftButton)
        brick_history = self.main_window.data_browser.table_data.show_brick_popup
        brick_table = brick_history.table
        self.assertEqual(brick_table.horizontalHeaderItem(0).text(), "Name")
        self.assertEqual(brick_table.horizontalHeaderItem(1).text(), "Init")
        self.assertEqual(brick_table.horizontalHeaderItem(2).text(), "Init Time")
        self.assertEqual(brick_table.horizontalHeaderItem(3).text(), "Exec")
        self.assertEqual(brick_table.horizontalHeaderItem(4).text(), "Exec Time")
        self.assertEqual(brick_table.horizontalHeaderItem(5).text(), "data_type")
        self.assertEqual(brick_table.horizontalHeaderItem(6).text(), "fwhm")
        self.assertEqual(brick_table.horizontalHeaderItem(7).text(), "implicit_masking")
        self.assertEqual(brick_table.horizontalHeaderItem(8).text(), "in_files")
        self.assertEqual(brick_table.horizontalHeaderItem(9).text(), "out_prefix")
        self.assertEqual(brick_table.horizontalHeaderItem(10).text(), "smoothed_files")
        self.assertEqual(brick_table.item(0, 0).text(), "smooth1")
        self.assertEqual(brick_table.item(0, 1).text(), "Done")
        self.assertEqual(brick_table.item(0, 2).text(), "2018-08-08 18:22:25.554610")
        self.assertEqual(brick_table.item(0, 3).text(), "Done")
        self.assertEqual(brick_table.item(0, 4).text(), "2018-08-08 18:22:32.371745")
        self.assertEqual(brick_table.item(0, 5).text(), "0")
        self.assertEqual(brick_table.cellWidget(0, 6).children()[1].text(), "6")
        self.assertEqual(brick_table.cellWidget(0, 6).children()[2].text(), "6")
        self.assertEqual(brick_table.cellWidget(0, 6).children()[3].text(), "6")
        self.assertEqual(brick_table.item(0, 7).text(), "False")
        self.assertEqual(brick_table.cellWidget(0, 8).children()[1].text(), "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii")
        self.assertEqual(brick_table.item(0, 9).text(), "s")
        self.assertEqual(brick_table.cellWidget(0, 10).children()[1].text(), "data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii")

    def test_multiple_sort(self):
        """
        Tests the multiple sort popup
        """

        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        self.main_window.data_browser.table_data.itemChanged.disconnect()
        self.main_window.data_browser.table_data.multiple_sort_pop_up()
        self.main_window.data_browser.table_data.itemChanged.connect(self.main_window.data_browser.table_data.change_cell_color)

        multiple_sort = self.main_window.data_browser.table_data.pop_up
        multiple_sort.push_buttons[0].setText("BandWidth")
        multiple_sort.fill_values(0)
        multiple_sort.push_buttons[1].setText("Type")
        multiple_sort.fill_values(1)
        QTest.mouseClick(multiple_sort.push_button_sort, Qt.LeftButton)

        scan = self.main_window.data_browser.table_data.item(0, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii")
        scan = self.main_window.data_browser.table_data.item(1, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii")
        scan = self.main_window.data_browser.table_data.item(2, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii")
        scan = self.main_window.data_browser.table_data.item(3, 0).text()
        self.assertEqual(scan, "data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii")
        scan = self.main_window.data_browser.table_data.item(4, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.main_window.data_browser.table_data.item(5, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.main_window.data_browser.table_data.item(6, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.main_window.data_browser.table_data.item(7, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.main_window.data_browser.table_data.item(8, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")


class TestMIAPipelineManager(unittest.TestCase):

    def setUp(self):
        """
        Called before each test
        """

        # All the tests are run in regular mode
        config = Config()
        config.set_clinical_mode("no")

        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.project = Project(None, True)
        self.main_window = MainWindow(self.project, test=True)

    def tearDown(self):
        """
        Called after each test
        """

        self.main_window.project.unsaveModifications()
        self.main_window.close()

        # Removing the opened projects (in CI, the tests are run twice)
        config = Config()
        config.set_opened_projects([])
        config.saveConfig()

        self.app.exit()

    def test_add_tab(self):
        """
        Adds tabs to the PipelineEditorTabs
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs

        # Adding two new tabs
        pipeline_editor_tabs.new_tab()
        self.assertEqual(pipeline_editor_tabs.count(), 3)
        self.assertEqual(pipeline_editor_tabs.tabText(1), "New Pipeline 1")
        pipeline_editor_tabs.new_tab()
        self.assertEqual(pipeline_editor_tabs.count(), 4)
        self.assertEqual(pipeline_editor_tabs.tabText(2), "New Pipeline 2")

    def test_close_tab(self):
        """
        Closes a tab to the PipelineEditorTabs
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs

        # Adding a new tab and closing the first one
        pipeline_editor_tabs.new_tab()
        pipeline_editor_tabs.close_tab(0)
        self.assertEqual(pipeline_editor_tabs.count(), 2)
        self.assertEqual(pipeline_editor_tabs.tabText(0), "New Pipeline 1")

        # When the last editor is closed, one is automatically opened
        pipeline_editor_tabs.close_tab(0)
        self.assertEqual(pipeline_editor_tabs.tabText(0), "New Pipeline")

        # Modifying the pipeline editor
        from nipype.interfaces.spm import Smooth
        process_class = Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)
        self.assertEqual(pipeline_editor_tabs.tabText(0)[-2:], " *")

        # # Still some bug with the pop-up execution
        #
        #
        # # Closing the modified pipeline editor and clicking on "Cancel"
        # pipeline_editor_tabs.close_tab(0)
        # pop_up_close = pipeline_editor_tabs.pop_up_close
        # # QTest.mouseClick(pop_up_close.push_button_cancel, Qt.LeftButton)
        # # QtCore.QTimer.singleShot(0, pop_up_close.push_button_cancel.clicked)
        # pop_up_close.cancel_clicked()
        # self.assertEqual(pipeline_editor_tabs.count(), 2)
        #
        # # Closing the modified pipeline editor and clicking on "Do not save"
        # pipeline_editor_tabs.close_tab(0)
        # pop_up_close = pipeline_editor_tabs.pop_up_close
        # # QTest.mouseClick(pop_up_close.push_button_do_not_save, Qt.LeftButton)
        # # QtCore.QTimer.singleShot(0, pop_up_close.push_button_cancel.clicked)
        # pop_up_close.do_not_save_clicked()
        # self.assertEqual(pipeline_editor_tabs.count(), 1)

        # TODO: HOW TO TEST "SAVE AS" ACTION ?

    def test_find_process(self):
        """
        Adds a Nipype SPM's Smooth process using the find_process method
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().find_process('nipype.interfaces.spm.Smooth')

        self.assertTrue('smooth1' in pipeline_editor_tabs.get_current_pipeline().nodes.keys())

    def test_update_node_name(self):
        """
        Displays parameters of a node and updates its name
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        node_controller = self.main_window.pipeline_manager.nodeController

        # Adding a process
        from nipype.interfaces.spm import Smooth
        process_class = Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth1"

        # Displaying the node parameters
        pipeline = pipeline_editor_tabs.get_current_pipeline()
        # node_controller.display_parameters("smooth1", get_process_instance(process_class), pipeline)
        self.main_window.pipeline_manager.displayNodeParameters("smooth1", get_process_instance(process_class))
        node_controller.update_node_name(pipeline, "smooth_test")
        self.assertTrue("smooth_test" in pipeline.nodes.keys())

        # Adding another Smooth process
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth1"
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth2"

        # Adding link between nodes
        source = ('smooth_test', '_smoothed_files')
        dest = ('smooth1', 'in_files')
        pipeline_editor_tabs.get_current_editor().add_link(source, dest, True, False)

        source = ('smooth1', '_smoothed_files')
        dest = ('smooth2', 'in_files')
        pipeline_editor_tabs.get_current_editor().add_link(source, dest, True, False)

        # Displaying the node parameters (smooth1)
        #  node_controller.display_parameters("smooth1", get_process_instance(process_class), pipeline)
        self.main_window.pipeline_manager.displayNodeParameters("smooth1", get_process_instance(process_class))

        # This should not change the node name because there is already a "smooth_test" process in the pipeline
        node_controller.update_node_name(pipeline, "smooth_test")
        self.assertTrue("smooth1" in pipeline.nodes.keys())

        # Changing to another value
        node_controller.update_node_name(pipeline, "smooth_test2")
        self.assertTrue("smooth_test2" in pipeline.nodes.keys())

        # Verifying that the updated node has the same links
        self.assertEqual(len(pipeline.nodes["smooth_test2"].plugs["in_files"].links_from), 1)
        self.assertEqual(len(pipeline.nodes["smooth_test2"].plugs["_smoothed_files"].links_to), 1)

    def test_update_plug_value(self):
        """
        Displays parameters of a node and updates a plug value
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        node_controller = self.main_window.pipeline_manager.nodeController

        # Adding a process
        from nipype.interfaces.spm import Threshold
        process_class = Threshold
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "threshold1"

        # Displaying the node parameters
        pipeline = pipeline_editor_tabs.get_current_pipeline()
        node_controller.display_parameters("threshold1", get_process_instance(process_class), pipeline)

        # Updating the value of the "synchronize" plug
        index = node_controller.get_index_from_plug_name("synchronize", "in")
        node_controller.line_edit_input[index].setText("1")
        node_controller.line_edit_input[index].returnPressed.emit()  # This calls "update_plug_value" method
        self.assertEqual(1, pipeline.nodes["threshold1"].get_plug_value("synchronize"))

        # Updating the value of the "_activation_forced" plug
        index = node_controller.get_index_from_plug_name("_activation_forced", "out")
        node_controller.line_edit_output[index].setText("True")
        node_controller.line_edit_output[index].returnPressed.emit()  # This calls "update_plug_value" method
        self.assertEqual(True, pipeline.nodes["threshold1"].get_plug_value("_activation_forced"))

        # Exporting the input plugs and modifying the "synchronize" input plug
        pipeline_editor_tabs.get_current_editor().current_node_name = "threshold1"
        pipeline_editor_tabs.get_current_editor().export_node_all_unconnected_inputs()

        input_process = pipeline.nodes[""].process
        node_controller.display_parameters("inputs", get_process_instance(input_process), pipeline)

        index = node_controller.get_index_from_plug_name("synchronize", "in")
        node_controller.line_edit_input[index].setText("2")
        node_controller.line_edit_input[index].returnPressed.emit()  # This calls "update_plug_value" method
        self.assertEqual(2, pipeline.nodes["threshold1"].get_plug_value("synchronize"))

    def test_display_filter(self):
        """
        Displays parameters of a node and displays a plug filter
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        node_controller = self.main_window.pipeline_manager.nodeController

        # Adding a process
        from nipype.interfaces.spm import Threshold
        process_class = Threshold
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "threshold1"
        pipeline = pipeline_editor_tabs.get_current_pipeline()

        # Exporting the input plugs and modifying the "synchronize" input plug
        pipeline_editor_tabs.get_current_editor().current_node_name = "threshold1"
        pipeline_editor_tabs.get_current_editor().export_node_all_unconnected_inputs()

        input_process = pipeline.nodes[""].process
        node_controller.display_parameters("inputs", get_process_instance(input_process), pipeline)
        index = node_controller.get_index_from_plug_name("synchronize", "in")
        node_controller.line_edit_input[index].setText("2")
        node_controller.line_edit_input[index].returnPressed.emit()  # This calls "update_plug_value" method

        # Calling the display_filter method
        node_controller.display_filter("inputs", "synchronize", (), input_process)
        node_controller.pop_up.close()
        self.assertEqual(2, pipeline.nodes["threshold1"].get_plug_value("synchronize"))

        # TODO: open a project and modify the filter pop-up

    '''def test_open_filter(self):
        """
        Opens an input filter
        """

        # Adding the processes path to the system path
        import sys
        sys.path.append(os.path.join('..', '..', 'processes'))

        # Importing the package
        package_name = 'MIA_processes.IRMaGe.Tools'
        __import__(package_name)
        pkg = sys.modules[package_name]
        process_class = None
        for name, cls in sorted(list(pkg.__dict__.items())):
            if name == 'Input_Filter':
                process_class = cls

        if not process_class:
            print('No Input_Filer class found')
            return

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        pipeline = pipeline_editor_tabs.get_current_pipeline()

        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "input_filter1"
        pipeline_editor_tabs.open_filter("input_filter1")
        pipeline_editor_tabs.filter_widget.close()
        self.assertFalse(pipeline.nodes["input_filter1"].get_plug_value("output"))

        # TODO: open a project and modify the filter pop-up'''

    def test_save_pipeline(self):
        """
        Saves a simple pipeline
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        node_controller = self.main_window.pipeline_manager.nodeController
        config = Config()

        # Adding a process
        from nipype.interfaces.spm import Smooth
        process_class = Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth1"

        # Displaying the node parameters
        pipeline = pipeline_editor_tabs.get_current_pipeline()
        node_controller.display_parameters("smooth1", get_process_instance(process_class), pipeline)

        # Exporting the input plugs
        pipeline_editor_tabs.get_current_editor().current_node_name = "smooth1"
        pipeline_editor_tabs.get_current_editor().export_node_unconnected_mandatory_plugs()
        pipeline_editor_tabs.get_current_editor().export_node_all_unconnected_outputs()

        from populse_mia.pipeline_manager.pipeline_editor import save_pipeline
        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        save_pipeline(pipeline, filename)
        self.main_window.pipeline_manager.updateProcessLibrary(filename)
        self.assertTrue(os.path.isfile(os.path.join(config.get_mia_path(), 'processes', 'User_processes',
                                                    'test_pipeline.py')))

    def test_z_load_pipeline(self):
        """
        Loads a pipeline (z to run at the end)
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        pipeline_editor_tabs.load_pipeline(filename)

        pipeline = pipeline_editor_tabs.get_current_pipeline()
        self.assertTrue("smooth1" in pipeline.nodes.keys())

    def test_z_get_editor(self):
        """
        Gets the instance of an editor (z to run at the end)

        This tests:
         - PipelineEditorTabs.get_editor_by_index
         - PipelineEditorTabs.get_current_editor
         - PipelineEditorTabs.get_editor_by_tab_name
         - PipelineEditorTabs.get_editor_by_filename
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        pipeline_editor_tabs.load_pipeline(filename)

        editor0 = pipeline_editor_tabs.get_current_editor()
        pipeline_editor_tabs.new_tab()  # create new tab with new editor and make it current
        editor1 = pipeline_editor_tabs.get_current_editor()

        self.assertEqual(pipeline_editor_tabs.get_editor_by_index(0), editor0)
        self.assertEqual(pipeline_editor_tabs.get_editor_by_index(1), editor1)
        self.assertEqual(pipeline_editor_tabs.get_current_editor(), editor1)
        self.assertEqual(pipeline_editor_tabs.get_editor_by_tab_name("test_pipeline.py"), editor0)
        self.assertEqual(pipeline_editor_tabs.get_editor_by_tab_name("New Pipeline 1"), editor1)
        self.assertEqual(pipeline_editor_tabs.get_editor_by_tab_name("dummy"), None)
        self.assertEqual(pipeline_editor_tabs.get_editor_by_file_name(filename), editor0)
        self.assertEqual(pipeline_editor_tabs.get_editor_by_file_name("dummy"), None)

    def test_z_get_filename(self):
        """
        Gets the relative path to the file the pipeline in an editor
        has been last saved to. (z to run at the end)

        This tests:
         - PipelineEditorTabs.get_filename_by_index
         - PipelineEditorTabs.get_current_filename
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        pipeline_editor_tabs.load_pipeline(filename)

        self.assertEqual(os.path.abspath(pipeline_editor_tabs.get_filename_by_index(0)), filename)
        self.assertEqual(pipeline_editor_tabs.get_filename_by_index(1), None)
        self.assertEqual(os.path.abspath(pipeline_editor_tabs.get_current_filename()), filename)

    def test_z_get_tab_name(self):
        """
        Gets the tab name of the editor. (z to run at the end)

        This tests:
         - PipelineEditorTabs.get_tab_name_by_index
         - PipelineEditorTabs.get_current_tab_name
        """

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs

        self.assertEqual(pipeline_editor_tabs.get_tab_name_by_index(0), "New Pipeline")
        self.assertEqual(pipeline_editor_tabs.get_tab_name_by_index(1), None)
        self.assertEqual(pipeline_editor_tabs.get_current_tab_name(), "New Pipeline")

    def test_z_get_index(self):
        """
        Gets the index of an editor. (z to run at the end)

        This tests:
         - PipelineEditorTabs.get_index_by_tab_name
         - PipelineEditorTabs.get_index_by_filename
         - PipelineEditorTabs.get_index_by_editor
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        pipeline_editor_tabs.load_pipeline(filename)

        editor0 = pipeline_editor_tabs.get_current_editor()
        pipeline_editor_tabs.new_tab()  # create new tab with new editor and make it current
        editor1 = pipeline_editor_tabs.get_current_editor()

        self.assertEqual(pipeline_editor_tabs.get_index_by_tab_name("test_pipeline.py"), 0)
        self.assertEqual(pipeline_editor_tabs.get_index_by_tab_name("New Pipeline 1"), 1)
        self.assertEqual(pipeline_editor_tabs.get_index_by_tab_name("dummy"), None)

        self.assertEqual(pipeline_editor_tabs.get_index_by_filename(filename), 0)
        self.assertEqual(pipeline_editor_tabs.get_index_by_filename("dummy"), None)

        self.assertEqual(pipeline_editor_tabs.get_index_by_editor(editor0), 0)
        self.assertEqual(pipeline_editor_tabs.get_index_by_editor(editor1), 1)
        self.assertEqual(pipeline_editor_tabs.get_index_by_editor("dummy"), None)

    def test_z_set_current_editor(self):
        """
        Sets the current editor (z to run at the end)

        This tests:
         - PipelineEditorTabs.set_current_editor_by_tab_name
         - PipelineEditorTabs.set_current_editor_by_file_name
         - PipelineEditorTabs.set_current_editor_by_editor
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        pipeline_editor_tabs.load_pipeline(filename)

        editor0 = pipeline_editor_tabs.get_current_editor()
        pipeline_editor_tabs.new_tab()  # create new tab with new editor and make it current
        editor1 = pipeline_editor_tabs.get_current_editor()

        pipeline_editor_tabs.set_current_editor_by_tab_name("test_pipeline.py")
        self.assertEqual(pipeline_editor_tabs.currentIndex(), 0)
        pipeline_editor_tabs.set_current_editor_by_tab_name("New Pipeline 1")
        self.assertEqual(pipeline_editor_tabs.currentIndex(), 1)

        pipeline_editor_tabs.set_current_editor_by_file_name(filename)
        self.assertEqual(pipeline_editor_tabs.currentIndex(), 0)

        pipeline_editor_tabs.set_current_editor_by_editor(editor1)
        self.assertEqual(pipeline_editor_tabs.currentIndex(), 1)
        pipeline_editor_tabs.set_current_editor_by_editor(editor0)
        self.assertEqual(pipeline_editor_tabs.currentIndex(), 0)

    def test_z_open_sub_pipeline(self):
        """
        Opens a sub_pipeline (z to run at the end)
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        # Adding the processes path to the system path
        sys.path.append(os.path.join(config.get_mia_path(), 'processes'))

        # Importing the package
        package_name = 'User_processes'
        __import__(package_name)
        pkg = sys.modules[package_name]
        for name, cls in sorted(list(pkg.__dict__.items())):
            if name == 'Test_pipeline':
                process_class = cls

        # Adding the "test_pipeline" as a process
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)

        # Opening the sub-pipeline in a new editor
        pipeline = pipeline_editor_tabs.get_current_pipeline()
        process_instance = pipeline.nodes["test_pipeline1"].process
        pipeline_editor_tabs.open_sub_pipeline(process_instance)

        self.assertTrue(pipeline_editor_tabs.count(), 3)
        self.assertEqual(os.path.basename(pipeline_editor_tabs.get_filename_by_index(1)), "test_pipeline.py")

    def test_z_init_pipeline(self):
        """
        Initializes the pipeline (z to run at the end)
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        config = Config()

        # Forcing the exit and disabling the init progressbar
        self.main_window.force_exit = True
        self.main_window.pipeline_manager.disable_progress_bar = True

        # Adding the processes path to the system path
        sys.path.append(os.path.join(config.get_mia_path(), 'processes'))

        # Importing the package
        package_name = 'User_processes'
        __import__(package_name)
        pkg = sys.modules[package_name]
        for name, cls in sorted(list(pkg.__dict__.items())):
            if name == 'Test_pipeline':
                process_class = cls

        # Adding the "test_pipeline" as a process
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)

        # Added another Smooth process
        from nipype.interfaces.spm import Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 550)
        pipeline_editor_tabs.get_current_editor().add_process(Smooth)

        pipeline = pipeline_editor_tabs.get_current_pipeline()

        # Verifying that all the processes are here
        self.assertTrue('test_pipeline1' in pipeline.nodes.keys())
        self.assertTrue('smooth1' in pipeline.nodes.keys())

        # Adding a link
        pipeline_editor_tabs.get_current_editor().add_link(("smooth1", "_smoothed_files"),
                                                           ("test_pipeline1", "in_files"),
                                                           active=True, weak=False)

        # Choosing a nii file from the project_8's raw_data folder
        folder = os.path.abspath(os.path.join(config.get_mia_path(), 'resources', 'mia', 'project_8',
                                              'data', 'raw_data'))
        nii_file = 'Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii'
        nii_path = os.path.abspath(os.path.join(folder, nii_file))

        # Setting values to verify that the initialization works well
        pipeline.nodes['smooth1'].set_plug_value('in_files', nii_path)
        pipeline.nodes['smooth1'].set_plug_value('out_prefix', 'TEST')

        # Initialization of the pipeline
        self.main_window.pipeline_manager.initPipeline()

        # Verifying the results
        self.assertEqual(pipeline.nodes['smooth1'].get_plug_value('_smoothed_files'),
                         os.path.abspath(os.path.join(folder, 'TEST' + nii_file)))
        self.assertEqual(pipeline.nodes['test_pipeline1'].get_plug_value('_smoothed_files'),
                         os.path.abspath(os.path.join(folder, 'sTEST' + nii_file)))

    '''def test_init_MIA_processes(self):
        """
        Adds all the tools processes, initializes and runs the pipeline
        """

        # Forcing the exit
        self.main_window.force_exit = True

        # Adding the processes path to the system path
        import sys
        sys.path.append(os.path.join('..', '..', 'processes'))

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs

        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)

        # Importing the package
        package_name = 'MIA_processes.IRMaGe.Tools'
        __import__(package_name)
        pkg = sys.modules[package_name]
        process_class = None
        for name, cls in sorted(list(pkg.__dict__.items())):
            if name != "Input_Filter":
                try:
                    proc_instance = get_process_instance(cls)
                except:
                    pass
                else:
                    print("class", cls)
                    process_class = cls
                    pipeline_editor_tabs.get_current_editor().add_process(process_class)

        pipeline = pipeline_editor_tabs.get_current_pipeline()

        # Verifying that all the processes are here
        self.assertTrue('duplicate_file1' in pipeline.nodes.keys())
        self.assertTrue('find_in_list1' in pipeline.nodes.keys())
        self.assertTrue('files_to_list1' in pipeline.nodes.keys())
        self.assertTrue('list_to_file1' in pipeline.nodes.keys())
        self.assertTrue('list_duplicate1' in pipeline.nodes.keys())
        self.assertTrue('roi_list_generator1' in pipeline.nodes.keys())

        # Setting values to verify that the initialization works well
        pipeline.nodes['duplicate_file1'].set_plug_value('file1', 'test_file.txt')
        pipeline.nodes['find_in_list1'].set_plug_value('in_list', ['test1.txt', 'test2.txt'])
        pipeline.nodes['find_in_list1'].set_plug_value('pattern', '1')
        pipeline.nodes['files_to_list1'].set_plug_value('file1', 'test1.txt')
        pipeline.nodes['files_to_list1'].set_plug_value('file2', 'test2.txt')
        pipeline.nodes['list_to_file1'].set_plug_value('file_list', ['test1.txt', 'test2.txt'])
        pipeline.nodes['list_duplicate1'].set_plug_value('file_name', 'test_file.txt')
        pipeline.nodes['roi_list_generator1'].set_plug_value('pos', ['TEST1', 'TEST2'])

        # Initialization/run of the pipeline
        self.main_window.pipeline_manager.initPipeline()
        self.main_window.pipeline_manager.runPipeline()

        # Verifying the results
        self.assertEqual(pipeline.nodes['duplicate_file1'].get_plug_value('out_file1'), 'test_file.txt')
        self.assertEqual(pipeline.nodes['duplicate_file1'].get_plug_value('out_file2'), 'test_file.txt')
        self.assertEqual(pipeline.nodes['find_in_list1'].get_plug_value('out_file'), 'test1.txt')
        self.assertEqual(pipeline.nodes['files_to_list1'].get_plug_value('file_list'), ['test1.txt', 'test2.txt'])
        self.assertEqual(pipeline.nodes['list_to_file1'].get_plug_value('file'), 'test1.txt')
        self.assertEqual(pipeline.nodes['list_duplicate1'].get_plug_value('out_list'), ['test_file.txt'])
        self.assertEqual(pipeline.nodes['list_duplicate1'].get_plug_value('out_file'), 'test_file.txt')
        self.assertEqual(pipeline.nodes['roi_list_generator1'].get_plug_value('roi_list'), [['TEST1', '_L'],
                                                                                            ['TEST1', '_R'],
                                                                                            ['TEST2', '_L'],
                                                                                            ['TEST2', '_R']])

    def test_init_SPM_pre_processes(self):
        """
        Adds all SPM pre-processes and initializes the pipeline
        """

        # Forcing the exit
        self.main_window.force_exit = True

        # Adding the processes path to the system path
        import sys
        sys.path.append(os.path.join('..', '..', 'processes'))

        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs

        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)

        # Importing the package
        package_name = 'MIA_processes.SPM'
        __import__(package_name)
        pkg = sys.modules[package_name]
        process_class = None
        preproc_list = ['Smooth', 'NewSegment', 'Normalize', 'Realign', 'Coregister']
        for name, cls in sorted(list(pkg.__dict__.items())):
            if name in preproc_list:
                try:
                    proc_instance = get_process_instance(cls)
                except:
                    pass
                else:
                    process_class = cls
                    pipeline_editor_tabs.get_current_editor().add_process(process_class)

        pipeline = pipeline_editor_tabs.get_current_pipeline()

        # Verifying that all the processes are here
        self.assertTrue('smooth1' in pipeline.nodes.keys())
        self.assertTrue('newsegment1' in pipeline.nodes.keys())
        self.assertTrue('normalize1' in pipeline.nodes.keys())
        self.assertTrue('realign1' in pipeline.nodes.keys())
        self.assertTrue('coregister1' in pipeline.nodes.keys())

        # Choosing a nii file from the project_8's raw_data folder
        folder = os.path.join('project_8', 'data', 'raw_data')
        nii_file = 'Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii'
        nii_no_ext = 'Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000'
        nii_path = os.path.abspath(os.path.join(folder, nii_file))

        # Setting values to verify that the initialization works well
        pipeline.nodes['smooth1'].set_plug_value('in_files', nii_path)
        pipeline.nodes['newsegment1'].set_plug_value('channel_files', nii_path)
        pipeline.nodes['normalize1'].set_plug_value('apply_to_files', nii_path)
        if os.path.isfile(os.path.join(folder, 'y_' + nii_file)):
            pipeline.nodes['normalize1'].set_plug_value('deformation_file',
                                                        os.path.abspath(os.path.join(folder, 'y_' + nii_file)))
        else:
            # This makes no sense but for the moment, we only check the initialization
            # and we just need to put a file in this plug
            pipeline.nodes['normalize1'].set_plug_value('deformation_file',
                                                        os.path.abspath(os.path.join(folder, nii_file)))

        pipeline.nodes['realign1'].set_plug_value('in_files', nii_path)

        # This makes no sense but for the moment, we only check the initialization
        # and we just need to put a file in this plug
        pipeline.nodes['coregister1'].set_plug_value('apply_to_files', nii_path)
        pipeline.nodes['coregister1'].set_plug_value('target', nii_path)
        pipeline.nodes['coregister1'].set_plug_value('source', nii_path)

        # Initialization/run of the pipeline
        self.main_window.pipeline_manager.initPipeline()

        # Verifying the results
        self.assertEqual(pipeline.nodes['smooth1'].get_plug_value('smoothed_files'),
                         os.path.abspath(os.path.join(folder, 's' + nii_file)))
        self.assertTrue(pipeline.nodes['newsegment1'].get_plug_value('native_class_images'),
                        os.path.abspath(os.path.join(folder, 'c1' + nii_file)))
        self.assertTrue(pipeline.nodes['newsegment1'].get_plug_value('native_class_images'),
                        os.path.abspath(os.path.join(folder, 'c2' + nii_file)))
        self.assertTrue(pipeline.nodes['newsegment1'].get_plug_value('native_class_images'),
                        os.path.abspath(os.path.join(folder, 'c3' + nii_file)))
        self.assertTrue(pipeline.nodes['newsegment1'].get_plug_value('native_class_images'),
                        os.path.abspath(os.path.join(folder, 'c4' + nii_file)))
        self.assertTrue(pipeline.nodes['newsegment1'].get_plug_value('native_class_images'),
                        os.path.abspath(os.path.join(folder, 'c5' + nii_file)))
        self.assertTrue(pipeline.nodes['newsegment1'].get_plug_value('native_class_images'),
                        os.path.abspath(os.path.join(folder, 'c6' + nii_file)))
        self.assertEqual(pipeline.nodes['newsegment1'].get_plug_value('bias_field_images'),
                         os.path.abspath(os.path.join(folder, 'BiasField_' + nii_file)))
        self.assertEqual(pipeline.nodes['newsegment1'].get_plug_value('forward_deformation_field'),
                         os.path.abspath(os.path.join(folder, 'y_' + nii_file)))
        self.assertEqual(pipeline.nodes['normalize1'].get_plug_value('normalized_files'),
                         os.path.abspath(os.path.join(folder, 'w' + nii_file)))
        self.assertEqual(pipeline.nodes['realign1'].get_plug_value('realigned_files'),
                         os.path.abspath(os.path.join(folder, 'r' + nii_file)))
        self.assertEqual(pipeline.nodes['realign1'].get_plug_value('mean_image'),
                         os.path.abspath(os.path.join(folder, 'mean' + nii_file)))
        self.assertEqual(pipeline.nodes['realign1'].get_plug_value('realignment_parameters'),
                         os.path.abspath(os.path.join(folder, 'rp_' + nii_no_ext + '.txt')))
        self.assertEqual(pipeline.nodes['coregister1'].get_plug_value('coregistered_files'),
                         os.path.abspath(os.path.join(folder, nii_file)))'''

    def test_iteration_table(self):
        """
        Plays with the iteration table
        """
        config = Config()
        mia_path = config.get_mia_path()
        project_8_path = os.path.join(mia_path, 'resources', 'mia', 'project_8')
        self.main_window.switch_project(project_8_path, "project_8", "project_8")

        iteration_table = self.main_window.pipeline_manager.iterationTable
        iteration_table.check_box_iterate.setChecked(True)
        iteration_table.update_iterated_tag("BandWidth")
        self.assertEqual(iteration_table.iterated_tag_label.text(), "BandWidth:")
        iteration_table.add_tag()
        self.assertEqual(len(iteration_table.push_buttons), 3)
        iteration_table.remove_tag()
        self.assertEqual(len(iteration_table.push_buttons), 2)
        iteration_table.add_tag()
        iteration_table.push_buttons[2].setText("AcquisitionTime")
        iteration_table.fill_values(2)
        iteration_table.update_table()
        self.assertTrue(iteration_table.combo_box.currentText() in ["25000.0", "65789.48", "357142.84", "50000.0"])

    def test_undo_redo(self):
        """
        Tests the undo/redo actions
        """

        pipeline_manager = self.main_window.pipeline_manager
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        node_controller = self.main_window.pipeline_manager.nodeController

        # Adding a process
        from nipype.interfaces.spm import Smooth
        process_class = Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth1"
        pipeline = pipeline_editor_tabs.get_current_pipeline()
        self.assertTrue("smooth1" in pipeline.nodes.keys())

        pipeline_manager.undo()
        self.assertFalse("smooth1" in pipeline.nodes.keys())

        pipeline_manager.redo()
        self.assertTrue("smooth1" in pipeline.nodes.keys())

        # Deleting the process
        pipeline_editor_tabs.get_current_editor().current_node_name = "smooth1"
        pipeline_editor_tabs.get_current_editor().del_node()
        self.assertFalse("smooth1" in pipeline.nodes.keys())

        pipeline_manager.undo()
        self.assertTrue("smooth1" in pipeline.nodes.keys())

        pipeline_manager.redo()
        self.assertFalse("smooth1" in pipeline.nodes.keys())

        # Adding a new process
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth1"

        # Exporting the "out_prefix" plug
        pipeline_editor_tabs.get_current_editor()._export_plug(temp_plug_name=("smooth1", "out_prefix"),
                                                               pipeline_parameter="prefix_smooth",
                                                               optional=False,
                                                               weak_link=False)

        self.assertTrue("prefix_smooth" in pipeline.nodes[''].plugs.keys())

        pipeline_manager.undo()
        self.assertFalse("prefix_smooth" in pipeline.nodes[''].plugs.keys())

        pipeline_manager.redo()
        self.assertTrue("prefix_smooth" in pipeline.nodes[''].plugs.keys())

        # Deleting the "out_prefix" plug
        pipeline_editor_tabs.get_current_editor()._remove_plug(_temp_plug_name=("inputs", "prefix_smooth"))
        self.assertFalse("prefix_smooth" in pipeline.nodes[''].plugs.keys())

        pipeline_manager.undo()
        self.assertTrue("prefix_smooth" in pipeline.nodes[''].plugs.keys())

        pipeline_manager.redo()
        self.assertFalse("prefix_smooth" in pipeline.nodes[''].plugs.keys())

        # TODO: export_plugs (currently there is a bug when a plug is of type list)

        # Adding a new process
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 550)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth2"

        # Adding a link
        pipeline_editor_tabs.get_current_editor().add_link(("smooth1", "_smoothed_files"),
                                                           ("smooth2", "in_files"),
                                                           active=True, weak=False)

        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_manager.undo()
        self.assertEqual(0, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(0, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_manager.redo()
        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        # Removing a link
        link = "smooth1._smoothed_files->smooth2.in_files"
        pipeline_editor_tabs.get_current_editor()._del_link(link)
        self.assertEqual(0, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(0, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_manager.undo()
        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_manager.redo()
        self.assertEqual(0, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(0, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        # Re-adding a link
        pipeline_editor_tabs.get_current_editor().add_link(("smooth1", "_smoothed_files"),
                                                           ("smooth2", "in_files"),
                                                           active=True, weak=False)

        # Updating the node name
        node_controller.display_parameters("smooth2", get_process_instance(process_class), pipeline)
        node_controller.line_edit_node_name.setText("my_smooth")
        node_controller.update_node_name(pipeline)
        self.assertTrue("my_smooth" in pipeline.nodes.keys())
        self.assertFalse("smooth2" in pipeline.nodes.keys())
        self.assertEqual(1, len(pipeline.nodes["my_smooth"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_manager.undo()
        self.assertFalse("my_smooth" in pipeline.nodes.keys())
        self.assertTrue("smooth2" in pipeline.nodes.keys())
        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_manager.redo()
        self.assertTrue("my_smooth" in pipeline.nodes.keys())
        self.assertFalse("smooth2" in pipeline.nodes.keys())
        self.assertEqual(1, len(pipeline.nodes["my_smooth"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        # Updating a plug value
        index = node_controller.get_index_from_plug_name("out_prefix", "in")
        node_controller.line_edit_input[index].setText("PREFIX")
        node_controller.update_plug_value("in", "out_prefix", pipeline, str)

        self.assertEqual("PREFIX", pipeline.nodes["my_smooth"].get_plug_value("out_prefix"))

        pipeline_manager.undo()
        self.assertEqual("s", pipeline.nodes["my_smooth"].get_plug_value("out_prefix"))

        pipeline_manager.redo()
        self.assertEqual("PREFIX", pipeline.nodes["my_smooth"].get_plug_value("out_prefix"))

    def test_delete_processes(self):
        """
        Deletes a process and makes the undo/redo action
        """

        pipeline_manager = self.main_window.pipeline_manager
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs

        # Adding processes
        from nipype.interfaces.spm import Smooth
        process_class = Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth1"
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth2"
        pipeline_editor_tabs.get_current_editor().add_process(process_class)  # Creates a node called "smooth3"

        pipeline = pipeline_editor_tabs.get_current_pipeline()

        self.assertTrue("smooth1" in pipeline.nodes.keys())
        self.assertTrue("smooth2" in pipeline.nodes.keys())
        self.assertTrue("smooth3" in pipeline.nodes.keys())

        pipeline_editor_tabs.get_current_editor().add_link(("smooth1", "_smoothed_files"),
                                                           ("smooth2", "in_files"),
                                                           active=True, weak=False)

        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_editor_tabs.get_current_editor().add_link(("smooth2", "_smoothed_files"),
                                                           ("smooth3", "in_files"),
                                                           active=True, weak=False)

        self.assertEqual(1, len(pipeline.nodes["smooth3"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["_smoothed_files"].links_to))

        pipeline_editor_tabs.get_current_editor().current_node_name = "smooth2"
        pipeline_editor_tabs.get_current_editor().del_node()

        self.assertTrue("smooth1" in pipeline.nodes.keys())
        self.assertFalse("smooth2" in pipeline.nodes.keys())
        self.assertTrue("smooth3" in pipeline.nodes.keys())
        self.assertEqual(0, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))
        self.assertEqual(0, len(pipeline.nodes["smooth3"].plugs["in_files"].links_from))

        pipeline_manager.undo()
        self.assertTrue("smooth1" in pipeline.nodes.keys())
        self.assertTrue("smooth2" in pipeline.nodes.keys())
        self.assertTrue("smooth3" in pipeline.nodes.keys())
        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))
        self.assertEqual(1, len(pipeline.nodes["smooth3"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["_smoothed_files"].links_to))

        pipeline_manager.redo()
        self.assertTrue("smooth1" in pipeline.nodes.keys())
        self.assertFalse("smooth2" in pipeline.nodes.keys())
        self.assertTrue("smooth3" in pipeline.nodes.keys())
        self.assertEqual(0, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))
        self.assertEqual(0, len(pipeline.nodes["smooth3"].plugs["in_files"].links_from))

    def test_zz_check_modifications(self):
        """
        Opens a pipeline, opens it as a process in another tab, modifies it and check the modifications
        """
        pipeline_editor_tabs = self.main_window.pipeline_manager.pipelineEditorTabs
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        config = Config()

        filename = os.path.join(config.get_mia_path(), 'processes', 'User_processes', 'test_pipeline.py')
        pipeline_editor_tabs.load_pipeline(filename)

        pipeline = pipeline_editor_tabs.get_current_pipeline()
        self.assertTrue("smooth1" in pipeline.nodes.keys())

        pipeline_editor_tabs.new_tab()
        pipeline_editor_tabs.set_current_editor_by_tab_name("New Pipeline 1")
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)

        pipeline_editor_tabs.get_current_editor().find_process("User_processes.Test_pipeline")
        pipeline = pipeline_editor_tabs.get_current_pipeline()

        self.assertTrue("test_pipeline1" in pipeline.nodes.keys())

        pipeline_editor_tabs.get_current_editor().find_process("nipype.interfaces.spm.Smooth")
        pipeline_editor_tabs.get_current_editor().find_process("nipype.interfaces.spm.Smooth")
        self.assertTrue("smooth1" in pipeline.nodes.keys())
        self.assertTrue("smooth2" in pipeline.nodes.keys())

        pipeline_editor_tabs.get_current_editor().add_link(("smooth1", "_smoothed_files"),
                                                           ("test_pipeline1", "in_files"),
                                                           active=True, weak=False)

        self.assertEqual(1, len(pipeline.nodes["test_pipeline1"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["smooth1"].plugs["_smoothed_files"].links_to))

        pipeline_editor_tabs.get_current_editor().add_link(("test_pipeline1", "_smoothed_files"),
                                                           ("smooth2", "in_files"),
                                                           active=True, weak=False)

        self.assertEqual(1, len(pipeline.nodes["smooth2"].plugs["in_files"].links_from))
        self.assertEqual(1, len(pipeline.nodes["test_pipeline1"].plugs["_smoothed_files"].links_to))

        pipeline_editor_tabs.set_current_editor_by_tab_name("test_pipeline.py")
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)

        pipeline_editor_tabs.get_current_editor().export_node_plugs("smooth1", optional=True)
        self.main_window.pipeline_manager.savePipeline()

        pipeline_editor_tabs.set_current_editor_by_tab_name("New Pipeline 1")
        pipeline_editor_tabs.get_current_editor().scene.pos["test_pipeline1"] = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().check_modifications()

        pipeline = pipeline_editor_tabs.get_current_pipeline()
        self.assertTrue("fwhm" in pipeline.nodes["test_pipeline1"].plugs.keys())


if __name__ == '__main__':
    unittest.main()
