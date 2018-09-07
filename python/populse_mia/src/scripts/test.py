import os

# Working from the scripts directory
from PyQt5.QtCore import Qt
from PyQt5 import QtCore

from populse_db.database import FIELD_TYPE_INTEGER

os.chdir(os.path.dirname(os.path.realpath(__file__)))

import unittest

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from Project.Project import Project, COLLECTION_CURRENT, COLLECTION_INITIAL, COLLECTION_BRICK, TAG_ORIGIN_USER, \
    TAG_FILENAME, TAG_CHECKSUM, TAG_TYPE, TAG_BRICKS, TAG_EXP_TYPE
from MainWindow.Main_Window import Main_Window
from SoftwareProperties.Config import Config
from capsul.api import get_process_instance


class TestMIADataBrowser(unittest.TestCase):

    def setUp(self):
        """
        Called before each test
        """

        # All the tests are run in regular mode
        config = Config()
        config.set_clinical_mode("no")

        self.app = QApplication([])
        self.project = Project(None, True)
        self.imageViewer = Main_Window(self.project, test=True)

    def tearDown(self):
        """
        Called after each test
        """

        self.imageViewer.project.unsaveModifications()
        self.imageViewer.close()

    def test_unnamed_project_software_opening(self):
        """
        Tests unnamed project creation at software opening
        """

        self.assertIsInstance(self.project, Project)
        self.assertEqual(self.imageViewer.project.getName(), "Unnamed project")
        tags = self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT)
        self.assertEqual(len(tags), 5)
        self.assertTrue(TAG_CHECKSUM in tags)
        self.assertTrue(TAG_FILENAME in tags)
        self.assertTrue(TAG_TYPE in tags)
        self.assertTrue(TAG_EXP_TYPE in tags)
        self.assertTrue(TAG_BRICKS in tags)
        self.assertEqual(self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT), [])
        self.assertEqual(self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL), [])
        collections = self.imageViewer.project.session.get_collections_names()
        self.assertEqual(len(collections), 3)
        self.assertTrue(COLLECTION_INITIAL in collections)
        self.assertTrue(COLLECTION_CURRENT in collections)
        self.assertTrue(COLLECTION_BRICK in collections)
        self.assertEqual(self.imageViewer.windowTitle(), "MIA - Multiparametric Image Analysis - Unnamed project")

    def test_projects_removed_from_current_projects(self):
        """
        Tests that the projects are removed from the list of current projects
        """

        config = Config()
        projects = config.get_opened_projects()
        self.assertEqual(len(projects), 1)
        self.assertTrue(self.imageViewer.project.folder in projects)

    def test_open_project(self):
        """
        Tests project opening
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")
        self.assertEqual(self.imageViewer.project.getName(), "project_8")
        self.assertEqual(self.imageViewer.windowTitle(), "MIA - Multiparametric Image Analysis - project_8")
        documents = self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT)
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
        documents = self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL)
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        # Testing without tag name
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(add_tag.msg.text(), "The tag name cannot be empty")

        QApplication.processEvents()

        # Testing with tag name already existing
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Type")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(add_tag.msg.text(), "This tag name already exists")

        QApplication.processEvents()

        # Testing with wrong type
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        add_tag.combo_box_type.setCurrentText(FIELD_TYPE_INTEGER)
        add_tag.type = FIELD_TYPE_INTEGER
        add_tag.text_edit_default_value.setText("Should be integer")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(add_tag.msg.text(), "Invalid default value")

        QApplication.processEvents()

        # Testing when everything is ok
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        add_tag.text_edit_default_value.setText("def_value")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))
        for document in self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT):
            self.assertEqual(self.imageViewer.project.session.get_value(COLLECTION_CURRENT, document, "Test"), "def_value")
        for document in self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL):
            self.assertEqual(self.imageViewer.project.session.get_value(COLLECTION_INITIAL, document, "Test"), "def_value")

        test_column = self.imageViewer.data_browser.table_data.get_tag_column("Test")
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, test_column)
            self.assertEqual(item.text(), "def_value")

        QApplication.processEvents()

        # Testing with list type
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
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

        test_list_column = self.imageViewer.data_browser.table_data.get_tag_column("Test_list")
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, test_list_column)
            self.assertEqual(item.text(), "[1, 2, 3]")

        QApplication.processEvents()

    def test_clone_tag(self):
        """
        Tests the pop up cloning a tag
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        # Testing without new tag name
        self.imageViewer.data_browser.clone_tag_action.trigger()
        clone_tag = self.imageViewer.data_browser.pop_up_clone_tag
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(clone_tag.msg.text(), "The tag name can't be empty")

        # Testing without any tag selected to clone
        self.imageViewer.data_browser.clone_tag_action.trigger()
        clone_tag = self.imageViewer.data_browser.pop_up_clone_tag
        clone_tag.line_edit_new_tag_name.setText("Test")
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(clone_tag.msg.text(), "The tag to clone must be selected")

        # Testing with tag name already existing
        self.imageViewer.data_browser.clone_tag_action.trigger()
        clone_tag = self.imageViewer.data_browser.pop_up_clone_tag
        clone_tag.line_edit_new_tag_name.setText("Type")
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertEqual(clone_tag.msg.text(), "This tag name already exists")

        self.imageViewer.data_browser.clone_tag_action.trigger()
        clone_tag = self.imageViewer.data_browser.pop_up_clone_tag
        clone_tag.line_edit_new_tag_name.setText("Test")
        clone_tag.search_bar.setText("BandWidth")
        clone_tag.list_widget_tags.setCurrentRow(0) # BandWidth tag selected
        QTest.mouseClick(clone_tag.push_button_ok, Qt.LeftButton)
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))
        test_row = self.imageViewer.project.session.get_field(COLLECTION_CURRENT, "Test")
        bandwidth_row = self.imageViewer.project.session.get_field(COLLECTION_CURRENT, "BandWidth")
        self.assertEqual(test_row.description, bandwidth_row.description)
        self.assertEqual(test_row.unit, bandwidth_row.unit)
        self.assertEqual(test_row.default_value, bandwidth_row.default_value)
        self.assertEqual(test_row.type, bandwidth_row.type)
        self.assertEqual(test_row.origin, TAG_ORIGIN_USER)
        self.assertEqual(test_row.visibility, True)
        test_row = self.imageViewer.project.session.get_field(COLLECTION_INITIAL, "Test")
        bandwidth_row = self.imageViewer.project.session.get_field(COLLECTION_INITIAL, "BandWidth")
        self.assertEqual(test_row.description, bandwidth_row.description)
        self.assertEqual(test_row.unit, bandwidth_row.unit)
        self.assertEqual(test_row.default_value, bandwidth_row.default_value)
        self.assertEqual(test_row.type, bandwidth_row.type)
        self.assertEqual(test_row.origin, TAG_ORIGIN_USER)
        self.assertEqual(test_row.visibility, True)

        for document in self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT):
            self.assertEqual(self.imageViewer.project.session.get_value(COLLECTION_CURRENT, document, "Test"), self.imageViewer.project.session.get_value(COLLECTION_CURRENT, document, "BandWidth"))
        for document in self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL):
            self.assertEqual(self.imageViewer.project.session.get_value(COLLECTION_INITIAL, document, "Test"), self.imageViewer.project.session.get_value(COLLECTION_INITIAL, document, "BandWidth"))

        test_column = self.imageViewer.data_browser.table_data.get_tag_column("Test")
        bw_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item_bw = self.imageViewer.data_browser.table_data.item(row, bw_column)
            item_test = self.imageViewer.data_browser.table_data.item(row, test_column)
            self.assertEqual(item_bw.text(), item_test.text())

    def test_remove_tag(self):
        """
        Tests the popup removing user tags
        """

        # Adding a tag
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)

        old_tags_current = self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT)
        old_tags_initial = self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL)
        self.imageViewer.data_browser.remove_tag_action.trigger()
        remove_tag = self.imageViewer.data_browser.pop_up_remove_tag
        QTest.mouseClick(remove_tag.push_button_ok, Qt.LeftButton)
        new_tags_current = self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT)
        new_tags_initial = self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL)
        self.assertTrue(old_tags_current == new_tags_current)
        self.assertTrue(old_tags_initial == new_tags_initial)

        old_tags_current = self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT)
        old_tags_initial = self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL)
        self.assertTrue("Test" in old_tags_current)
        self.assertTrue("Test" in old_tags_initial)
        self.imageViewer.data_browser.remove_tag_action.trigger()
        remove_tag = self.imageViewer.data_browser.pop_up_remove_tag
        remove_tag.list_widget_tags.setCurrentRow(0) # Test tag selected
        QTest.mouseClick(remove_tag.push_button_ok, Qt.LeftButton)
        new_tags_current = self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT)
        new_tags_initial = self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL)
        self.assertTrue("Test" not in new_tags_current)
        self.assertTrue("Test" not in new_tags_initial)

    def test_visualized_tags(self):
        """
        Tests the popup modifying the visualized tags
        """

        # Testing default tags visibility
        visibles = self.imageViewer.project.session.get_visibles()
        self.assertEqual(len(visibles), 4)
        self.assertTrue(TAG_FILENAME in visibles)
        self.assertTrue(TAG_BRICKS in visibles)
        self.assertTrue(TAG_TYPE in visibles)
        self.assertTrue(TAG_EXP_TYPE in visibles)

        # Testing columns displayed in the databrowser
        self.assertEqual(self.imageViewer.data_browser.table_data.columnCount(), 4)
        columns_displayed = []
        for column in range (0, self.imageViewer.data_browser.table_data.columnCount()):
            tag_displayed = self.imageViewer.data_browser.table_data.horizontalHeaderItem(column).text()
            if not self.imageViewer.data_browser.table_data.isColumnHidden(column):
                columns_displayed.append(tag_displayed)
        self.assertEqual(sorted(visibles), sorted(columns_displayed))

        # Testing that FileName tag is the first column
        self.assertEqual(self.imageViewer.data_browser.table_data.horizontalHeaderItem(0).text(), TAG_FILENAME)

        # Trying to set the visibles tags
        QTest.mouseClick(self.imageViewer.data_browser.visualized_tags_button, Qt.LeftButton)
        settings = self.imageViewer.data_browser.table_data.pop_up

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

        new_visibles = self.imageViewer.project.session.get_visibles()
        self.assertEqual(len(new_visibles), 3)
        self.assertTrue(TAG_FILENAME in new_visibles)
        self.assertTrue(TAG_EXP_TYPE in new_visibles)
        self.assertTrue(TAG_TYPE in new_visibles)

        columns_displayed = []
        for column in range(0, self.imageViewer.data_browser.table_data.columnCount()):
            item = self.imageViewer.data_browser.table_data.horizontalHeaderItem(column)
            if not self.imageViewer.data_browser.table_data.isColumnHidden(column):
                columns_displayed.append(item.text())
        self.assertEqual(len(columns_displayed), 3)
        self.assertTrue(TAG_FILENAME in columns_displayed)
        self.assertTrue(TAG_EXP_TYPE in columns_displayed)
        self.assertTrue(TAG_TYPE in columns_displayed)

        # Testing when showing a new tag
        QTest.mouseClick(self.imageViewer.data_browser.visualized_tags_button, Qt.LeftButton)
        settings = self.imageViewer.data_browser.table_data.pop_up
        settings.tab_tags.search_bar.setText(TAG_BRICKS)
        settings.tab_tags.list_widget_tags.item(0).setSelected(True)
        QTest.mouseClick(settings.tab_tags.push_button_select_tag, Qt.LeftButton)
        QTest.mouseClick(settings.push_button_ok, Qt.LeftButton)

        new_visibles = self.imageViewer.project.session.get_visibles()
        self.assertEqual(len(new_visibles), 4)
        self.assertTrue(TAG_FILENAME in new_visibles)
        self.assertTrue(TAG_EXP_TYPE in new_visibles)
        self.assertTrue(TAG_TYPE in new_visibles)
        self.assertTrue(TAG_BRICKS in new_visibles)

        columns_displayed = []
        for column in range(0, self.imageViewer.data_browser.table_data.columnCount()):
            item = self.imageViewer.data_browser.table_data.horizontalHeaderItem(column)
            if not self.imageViewer.data_browser.table_data.isColumnHidden(column):
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        # Checking that the 8 scans are shown in the databrowser
        self.assertEqual(self.imageViewer.data_browser.table_data.rowCount(), 9)
        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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
        self.imageViewer.data_browser.search_bar.setText("G1")
        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 2)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Testing that all the scans are back when clicking on the cross
        QTest.mouseClick(self.imageViewer.data_browser.button_cross, Qt.LeftButton)

        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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
        QTest.mouseClick(self.imageViewer.data_browser.button_cross, Qt.LeftButton)
        self.imageViewer.data_browser.search_bar.setText("*Not Defined*")
        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(scans_displayed, ["data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii"])

    def test_advanced_search(self):
        """
        Tests the advanced search widget
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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

        QTest.mouseClick(self.imageViewer.data_browser.advanced_search_button, Qt.LeftButton)

        # Testing - and + buttons
        self.assertEqual(len(self.imageViewer.data_browser.advanced_search.rows), 1)
        first_row = self.imageViewer.data_browser.advanced_search.rows[0]
        QTest.mouseClick(first_row[6], Qt.LeftButton)
        self.assertEqual(len(self.imageViewer.data_browser.advanced_search.rows), 2)
        second_row = self.imageViewer.data_browser.advanced_search.rows[1]
        QTest.mouseClick(second_row[5], Qt.LeftButton)
        self.assertEqual(len(self.imageViewer.data_browser.advanced_search.rows), 1)
        first_row = self.imageViewer.data_browser.advanced_search.rows[0]
        QTest.mouseClick(first_row[5], Qt.LeftButton)
        self.assertEqual(len(self.imageViewer.data_browser.advanced_search.rows), 1)

        field = self.imageViewer.data_browser.advanced_search.rows[0][2]
        condition = self.imageViewer.data_browser.advanced_search.rows[0][3]
        value = self.imageViewer.data_browser.advanced_search.rows[0][4]
        field_filename_index = field.findText(TAG_FILENAME)
        field.setCurrentIndex(field_filename_index)
        condition_contains_index = condition.findText("CONTAINS")
        condition.setCurrentIndex(condition_contains_index)
        value.setText("G1")
        QTest.mouseClick(self.imageViewer.data_browser.advanced_search.search, Qt.LeftButton)

        # Testing that only G1 scans are displayed with the filter applied
        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
                scans_displayed.append(scan_name)
        self.assertEqual(len(scans_displayed), 2)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)
        self.assertTrue("data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in scans_displayed)

        # Testing that every scan is back when clicking again on advanced search
        QTest.mouseClick(self.imageViewer.data_browser.advanced_search_button, Qt.LeftButton)
        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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
        self.imageViewer.data_browser.table_data.selectRow(0)
        self.imageViewer.data_browser.table_data.remove_scan()

        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"))
        bandwidth_column  = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        G1_bandwidth_databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, G1_bandwidth_databrowser)
        self.assertEqual(value, value_initial)

        item.setSelected(True)
        item.setText("25000")

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        G1_bandwidth_databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, G1_bandwidth_databrowser)
        self.assertEqual(value_initial, float(50000))

    def test_reset_cell(self):
        """
        Tests the method resetting the selected cells
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        bandwidth_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)
        item.setSelected(True)

        item.setText("25000")

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value_initial, float(50000))

        self.imageViewer.data_browser.table_data.itemChanged.disconnect()
        self.imageViewer.data_browser.table_data.reset_cell()
        self.imageViewer.data_browser.table_data.itemChanged.connect(
        self.imageViewer.data_browser.table_data.change_cell_color)

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)

    def test_reset_column(self):
        """
        Tests the method resetting the columns selected
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        bandwidth_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)
        item.setSelected(True)

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(1, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)
        item.setSelected(True)

        item.setText("70000")

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(70000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value_initial, float(50000))

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(1, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(70000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value_initial, float(25000))

        self.imageViewer.data_browser.table_data.itemChanged.disconnect()
        self.imageViewer.data_browser.table_data.reset_column()
        self.imageViewer.data_browser.table_data.itemChanged.connect(self.imageViewer.data_browser.table_data.change_cell_color)

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(0, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(50000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)

        value = float(self.imageViewer.project.session.get_value(COLLECTION_CURRENT,
                                                                              "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                              "BandWidth"))
        value_initial = float(self.imageViewer.project.session.get_value(COLLECTION_INITIAL,
                                                                 "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii",
                                                                 "BandWidth"))
        item = self.imageViewer.data_browser.table_data.item(1, bandwidth_column)
        databrowser = float(item.text())
        self.assertEqual(value, float(25000))
        self.assertEqual(value, databrowser)
        self.assertEqual(value, value_initial)

    def test_reset_row(self):
        """
        Tests row reset
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        bw_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")

        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        old_bw = bw_item.text()
        self.assertEqual(int(old_bw), 50000)

        bw_item.setSelected(True)
        bw_item.setText("25000")
        set_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        set_bw = set_item.text()
        self.assertEqual(int(set_bw), 25000)

        self.imageViewer.data_browser.table_data.clearSelection()

        item = self.imageViewer.data_browser.table_data.item(0, 0)
        item.setSelected(True)
        self.imageViewer.data_browser.table_data.itemChanged.disconnect()
        self.imageViewer.data_browser.table_data.reset_row()
        self.imageViewer.data_browser.table_data.itemChanged.connect(
            self.imageViewer.data_browser.table_data.change_cell_color)

        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        new_bw = bw_item.text()
        self.assertEqual(int(new_bw), 50000)

    def test_add_path(self):
        """
        Tests the popup to add a path
        """

        QTest.mouseClick(self.imageViewer.data_browser.addRowLabel, Qt.LeftButton)
        add_path = self.imageViewer.data_browser.table_data.pop_up_add_path

        QTest.mouseClick(add_path.ok_button, Qt.LeftButton)
        self.assertEqual(add_path.msg.text(), "Invalid arguments")

        add_path.file_line_edit.setText(os.path.join(".", "test_not_existing.py"))
        add_path.type_line_edit.setText("Python")
        QTest.mouseClick(add_path.ok_button, Qt.LeftButton)
        self.assertEqual(add_path.msg.text(), "Invalid arguments")

        add_path.file_line_edit.setText(os.path.join(".", "test.py"))
        add_path.type_line_edit.setText("Python")
        QTest.mouseClick(add_path.ok_button, Qt.LeftButton)

        self.assertEqual(self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT), [os.path.join('data', 'downloaded_data', 'test.py')])
        self.assertEqual(self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL), [os.path.join('data', 'downloaded_data', 'test.py')])
        self.assertEqual(self.imageViewer.data_browser.table_data.rowCount(), 1)
        self.assertEqual(self.imageViewer.data_browser.table_data.item(0, 0).text(), os.path.join('data', 'downloaded_data', 'test.py'))

    def test_send_documents_to_pipeline(self):
        """
        Tests the popup sending the documents to the pipeline manager
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        # Checking that the pipeline manager has an empty list at the beginning
        self.assertEqual(self.imageViewer.pipeline_manager.scan_list, [])

        # Sending the selection (all scans), but closing the popup
        QTest.mouseClick(self.imageViewer.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.imageViewer.data_browser.show_selection
        send_popup.close()

        # Checking that the list is stil empty
        self.assertEqual(self.imageViewer.pipeline_manager.scan_list, [])

        # Sending the selection (all scans)
        QTest.mouseClick(self.imageViewer.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.imageViewer.data_browser.show_selection
        send_popup.ok_clicked()

        # Checking that all scans have been sent to the pipeline manager
        scans = self.imageViewer.pipeline_manager.scan_list
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
        item1 = self.imageViewer.data_browser.table_data.item(0, 0)
        item1.setSelected(True)
        scan1 = item1.text()
        item2 = self.imageViewer.data_browser.table_data.item(1, 0)
        scan2 = item2.text()
        item2.setSelected(True)

        # Sending the selection (first 2 scans)
        QTest.mouseClick(self.imageViewer.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.imageViewer.data_browser.show_selection
        send_popup.ok_clicked()

        # Checking that the first 2 scans have been sent to the pipeline manager
        scans = self.imageViewer.pipeline_manager.scan_list
        self.assertEqual(len(scans), 2)
        self.assertTrue(scan1 in scans)
        self.assertTrue(scan2 in scans)

        # Testing with the rapid search
        self.imageViewer.data_browser.table_data.clearSelection()
        self.imageViewer.data_browser.search_bar.setText("G3")

        # Sending the selection (G3 scans)
        QTest.mouseClick(self.imageViewer.data_browser.send_documents_to_pipeline_button, Qt.LeftButton)
        send_popup = self.imageViewer.data_browser.show_selection
        send_popup.ok_clicked()

        # Checking that G3 scans have been sent to the pipeline manager
        scans = self.imageViewer.pipeline_manager.scan_list
        self.assertEqual(len(scans), 2)
        self.assertTrue(
            "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans)
        self.assertTrue(
            "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in scans)

    def test_sort(self):
        """
        Tests the sorting in the databrowser
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        mixed_bandwidths = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            bandwidth_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
            item = self.imageViewer.data_browser.table_data.item(row, bandwidth_column)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
                mixed_bandwidths.append(scan_name)

        self.imageViewer.data_browser.table_data.horizontalHeader().setSortIndicator(bandwidth_column, 0)

        up_bandwidths = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            bandwidth_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
            item = self.imageViewer.data_browser.table_data.item(row, bandwidth_column)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
                up_bandwidths.append(scan_name)

        self.assertNotEqual(mixed_bandwidths, up_bandwidths)
        self.assertEqual(sorted(mixed_bandwidths), up_bandwidths)

        self.imageViewer.data_browser.table_data.horizontalHeader().setSortIndicator(bandwidth_column, 1)

        down_bandwidths = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            bandwidth_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
            item = self.imageViewer.data_browser.table_data.item(row, bandwidth_column)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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
        self.imageViewer.action_software_preferences.trigger()
        properties = self.imageViewer.pop_up_preferences
        properties.tab_widget.setCurrentIndex(1)
        properties.save_checkbox.setChecked(True)
        QTest.mouseClick(properties.push_button_ok, Qt.LeftButton)

        config = Config()
        new_auto_save = config.isAutoSave()
        self.assertEqual(new_auto_save, "yes")

        # Auto save disabled again
        self.imageViewer.action_software_preferences.trigger()
        properties = self.imageViewer.pop_up_preferences
        properties.tab_widget.setCurrentIndex(1)
        properties.save_checkbox.setChecked(False)
        QTest.mouseClick(properties.push_button_ok, Qt.LeftButton)
        config = Config()
        reput_auto_save = config.isAutoSave()
        self.assertEqual(reput_auto_save, "no")

        # Checking that the changes are not effective if cancel is clicked
        self.imageViewer.action_software_preferences.trigger()
        properties = self.imageViewer.pop_up_preferences
        properties.tab_widget.setCurrentIndex(1)
        properties.save_checkbox.setChecked(True)
        QTest.mouseClick(properties.push_button_cancel, Qt.LeftButton)
        config = Config()
        auto_save = config.isAutoSave()
        self.assertEqual(auto_save, "no")

    def test_undo_redo_databrowser(self):
        """
        Tests the databrowser undo/redo
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        self.assertEqual(self.imageViewer.project.undos, [])
        self.assertEqual(self.imageViewer.project.redos, [])

        # Testing modified value undo/redo
        bw_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        bw_old = bw_item.text()
        self.assertEqual(int(bw_old), 50000)
        bw_item.setSelected(True)
        bw_item.setText("0")
        self.assertEqual(self.imageViewer.project.undos, [['modified_values', [['data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii', 'BandWidth', 50000.0, 0.0]]]])
        self.assertEqual(self.imageViewer.project.redos, [])
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        bw_set = bw_item.text()
        self.assertEqual(int(bw_set), 0)
        self.imageViewer.action_undo.trigger()
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        bw_undo = bw_item.text()
        self.assertEqual(int(bw_undo), 50000)
        self.assertEqual(self.imageViewer.project.redos, [['modified_values', [[
                                                                                   'data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii',
                                                                                   'BandWidth', 50000.0, 0.0]]]])
        self.assertEqual(self.imageViewer.project.undos, [])
        self.imageViewer.action_redo.trigger()
        self.assertEqual(self.imageViewer.project.undos, [['modified_values', [[
                                                                                   'data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii',
                                                                                   'BandWidth', 50000.0, 0.0]]]])
        self.assertEqual(self.imageViewer.project.redos, [])
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        bw_redo = bw_item.text()
        self.assertEqual(int(bw_redo), 0)

        # Testing scan removal undo/redo
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT)), 9)
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL)), 9)
        self.imageViewer.data_browser.table_data.selectRow(0)
        self.imageViewer.data_browser.table_data.remove_scan()
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT)), 8)
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL)), 8)
        self.imageViewer.action_undo.trigger()
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT)), 9)
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL)), 9)
        self.imageViewer.action_redo.trigger()
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_CURRENT)), 8)
        self.assertEqual(len(self.imageViewer.project.session.get_documents_names(COLLECTION_INITIAL)), 8)

        # Testing add tag undo/redo
        self.imageViewer.data_browser.add_tag_action.trigger()
        add_tag = self.imageViewer.data_browser.pop_up_add_tag
        add_tag.text_edit_tag_name.setText("Test")
        QTest.mouseClick(add_tag.push_button_ok, Qt.LeftButton)
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))
        self.imageViewer.action_undo.trigger()
        self.assertFalse("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertFalse("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))
        self.imageViewer.action_redo.trigger()
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))

        # Testing remove tag undo/redo
        self.imageViewer.data_browser.remove_tag_action.trigger()
        remove_tag = self.imageViewer.data_browser.pop_up_remove_tag
        remove_tag.list_widget_tags.setCurrentRow(0)  # Test tag selected
        QTest.mouseClick(remove_tag.push_button_ok, Qt.LeftButton)
        self.assertFalse("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertFalse("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))
        self.imageViewer.action_undo.trigger()
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))
        self.imageViewer.action_redo.trigger()
        self.assertFalse("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_CURRENT))
        self.assertFalse("Test" in self.imageViewer.project.session.get_fields_names(COLLECTION_INITIAL))

    def test_count_table(self):
        """
        Tests the count table popup
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        QTest.mouseClick(self.imageViewer.data_browser.count_table_button, Qt.LeftButton)
        count_table = self.imageViewer.data_browser.count_table_pop_up
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        # Selecting a cell
        bw_column = self.imageViewer.data_browser.table_data.get_tag_column("BandWidth")
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        bw_item.setSelected(True)
        self.assertEqual(int(bw_item.text()), 50000)
        self.assertEqual(self.imageViewer.project.session.get_value(COLLECTION_CURRENT, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"), 50000)

        # Clearing the cell
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        bw_item.setSelected(True)
        self.imageViewer.data_browser.table_data.itemChanged.disconnect()
        self.imageViewer.data_browser.table_data.clear_cell()
        self.imageViewer.data_browser.table_data.itemChanged.connect(self.imageViewer.data_browser.table_data.change_cell_color)

        # Checking that it's empty
        bw_item = self.imageViewer.data_browser.table_data.item(0, bw_column)
        self.assertEqual(bw_item.text(), "*Not Defined*")
        self.assertIsNone(self.imageViewer.project.session.get_value(COLLECTION_CURRENT, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii", "BandWidth"))

    def test_open_project_filter(self):
        """
        Tests project filter opening
        """

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        self.imageViewer.data_browser.open_filter_action.trigger()
        open_popup = self.imageViewer.data_browser.popUp
        open_popup.list_widget_filters.item(0).setSelected(True)
        QTest.mouseClick(open_popup.push_button_ok, Qt.LeftButton)

        scans_displayed = []
        for row in range(0, self.imageViewer.data_browser.table_data.rowCount()):
            item = self.imageViewer.data_browser.table_data.item(row, 0)
            scan_name = item.text()
            if not self.imageViewer.data_browser.table_data.isRowHidden(row):
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")


        bricks_column = self.imageViewer.data_browser.table_data.get_tag_column("Bricks")
        bricks_widget = self.imageViewer.data_browser.table_data.cellWidget(8, bricks_column)
        smmooth_button = bricks_widget.children()[1]
        self.assertEqual(smmooth_button.text(), "smooth1")
        QTest.mouseClick(smmooth_button, Qt.LeftButton)
        brick_history = self.imageViewer.data_browser.table_data.show_brick_popup
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

        self.imageViewer.switch_project("project_8", "project_8", "project_8")

        self.imageViewer.data_browser.table_data.itemChanged.disconnect()
        self.imageViewer.data_browser.table_data.multiple_sort_pop_up()
        self.imageViewer.data_browser.table_data.itemChanged.connect(self.imageViewer.data_browser.table_data.change_cell_color)

        multiple_sort = self.imageViewer.data_browser.table_data.pop_up
        multiple_sort.push_buttons[0].setText("BandWidth")
        multiple_sort.fill_values(0)
        multiple_sort.push_buttons[1].setText("Type")
        multiple_sort.fill_values(1)
        QTest.mouseClick(multiple_sort.push_button_sort, Qt.LeftButton)

        scan = self.imageViewer.data_browser.table_data.item(0, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii")
        scan = self.imageViewer.data_browser.table_data.item(1, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii")
        scan = self.imageViewer.data_browser.table_data.item(2, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii")
        scan = self.imageViewer.data_browser.table_data.item(3, 0).text()
        self.assertEqual(scan, "data/raw_data/sGuerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii")
        scan = self.imageViewer.data_browser.table_data.item(4, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.imageViewer.data_browser.table_data.item(5, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.imageViewer.data_browser.table_data.item(6, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.imageViewer.data_browser.table_data.item(7, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")
        scan = self.imageViewer.data_browser.table_data.item(8, 0).text()
        self.assertEqual(scan, "data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii")


class TestMIAPipelineManager(unittest.TestCase):

    def setUp(self):
        """
        Called before each test
        """

        # All the tests are run in regular mode
        config = Config()
        config.set_clinical_mode("no")

        self.app = QApplication([])
        self.project = Project(None, True)
        self.main_window = Main_Window(self.project, test=True)

    def tearDown(self):
        """
        Called after each test
        """

        self.main_window.project.unsaveModifications()
        self.main_window.close()

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

        # Modifying the pipeline editor
        from nipype.interfaces.spm import Smooth
        process_class = Smooth
        pipeline_editor_tabs.get_current_editor().click_pos = QtCore.QPoint(450, 500)
        pipeline_editor_tabs.get_current_editor().add_process(process_class)
        self.assertEqual(pipeline_editor_tabs.tabText(0)[-2:], " *")

        '''
        # Still some bug with the pop-up execution
        
        
        # Closing the modified pipeline editor and clicking on "Cancel"
        pipeline_editor_tabs.close_tab(0)
        pop_up_close = pipeline_editor_tabs.pop_up_close
        # QTest.mouseClick(pop_up_close.push_button_cancel, Qt.LeftButton)
        # QtCore.QTimer.singleShot(0, pop_up_close.push_button_cancel.clicked)
        pop_up_close.cancel_clicked()
        self.assertEqual(pipeline_editor_tabs.count(), 2)

        # Closing the modified pipeline editor and clicking on "Do not save"
        pipeline_editor_tabs.close_tab(0)
        pop_up_close = pipeline_editor_tabs.pop_up_close
        # QTest.mouseClick(pop_up_close.push_button_do_not_save, Qt.LeftButton)
        # QtCore.QTimer.singleShot(0, pop_up_close.push_button_cancel.clicked)
        pop_up_close.do_not_save_clicked()
        self.assertEqual(pipeline_editor_tabs.count(), 1)

        # TODO: HOW TO TEST "SAVE AS" ACTION ?
        
        '''

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
        # node_controller.display_parameters("smooth1", get_process_instance(process_class), pipeline)
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

    def test_open_filter(self):
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

        # TODO: open a project and modify the filter pop-up

    def test_save_pipeline(self):
        """
        Saves a simple pipeline
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

        # Exporting the input plugs
        pipeline_editor_tabs.get_current_editor().current_node_name = "threshold1"
        pipeline_editor_tabs.get_current_editor().export_node_unconnected_mandatory_plugs()

        from PipelineManager.PipelineEditor import save_pipeline
        filename = os.path.join('..', '..', 'processes', 'User_processes', 'test_pipeline.py')
        save_pipeline(pipeline, filename)
        self.assertTrue(os.path.isfile(os.path.join('..', '..', 'processes', 'User_processes', 'test_pipeline.py')))


if __name__ == '__main__':
    unittest.main()
