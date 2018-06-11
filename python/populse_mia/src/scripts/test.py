import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from Project.Project import Project, COLLECTION_CURRENT, COLLECTION_INITIAL
from MainWindow.Main_Window import Main_Window
from SoftwareProperties.Config import Config
from PopUps.Ui_Dialog_add_tag import Ui_Dialog_add_tag
import os
import populse_db

class TestMIADataBrowser(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.project = Project(None, True)
        self.imageViewer = Main_Window(self.project)

    def tearDown(self):
        self.imageViewer.close()

    def test_unnamed_project_software_opening(self):
        """
        Tests unnamed project creation at software opening
        """

        self.assertIsInstance(self.project, Project)
        self.assertEqual(self.imageViewer.project.getName(), "Unnamed project")
        tags = self.imageViewer.project.database.get_fields_names(COLLECTION_CURRENT)
        self.assertEqual(len(tags), 3)
        self.assertTrue("Checksum" in tags)
        self.assertTrue("FileName" in tags)
        self.assertTrue("Type" in tags)
        self.assertEqual(self.imageViewer.project.database.get_documents_names(COLLECTION_CURRENT), [])
        self.assertEqual(self.imageViewer.project.database.get_documents_names(COLLECTION_INITIAL), [])
        collections = self.imageViewer.project.database.get_collections_names()
        self.assertEqual(len(collections), 2)
        self.assertTrue(COLLECTION_INITIAL in collections)
        self.assertTrue(COLLECTION_CURRENT in collections)
        self.assertEqual(self.imageViewer.windowTitle(), "MIA2 - Multiparametric Image Analysis 2 - Unnamed project")

    """
    def test_new_project_opening(self):
        '''
        Tests the opening of a new project
        '''

        self.imageViewer.action_create.trigger()
        print(self.imageViewer.exPopup.selectedFiles())
        self.imageViewer.close()
    """

    def test_projects_removed_from_current_projects(self):
        """
        Tests that the projects are removed from the list of current projects
        """

        config = Config()
        projects = config.get_opened_projects()
        self.assertEqual(len(projects), 1)
        self.assertTrue(self.imageViewer.project.folder in projects)

    def test_open_project(self):
        '''
        Tests project opening
        '''

        self.imageViewer.switch_project("project_8", "project_8", "project_8")
        self.assertEqual(self.imageViewer.project.getName(), "project_8")
        self.assertEqual(self.imageViewer.windowTitle(), "MIA2 - Multiparametric Image Analysis 2 - project_8")
        documents = self.imageViewer.project.database.get_documents_names(COLLECTION_CURRENT)
        self.assertEqual(len(documents), 8)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        documents = self.imageViewer.project.database.get_documents_names(COLLECTION_INITIAL)
        self.assertEqual(len(documents), 8)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-02-G1_Guerbet_Anat-RARE__pvm_-00-02-20.000.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-04-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-05-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-06-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-08-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-09-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-10-G3_Guerbet_MDEFT-MDEFT__pvm_-00-09-40.800.nii" in documents)
        self.assertTrue("data/raw_data/Guerbet-C6-2014-Rat-K52-Tube27-2014-02-14_10-23-17-11-G4_Guerbet_T1SE_800-RARE__pvm_-00-01-42.400.nii" in documents)

    def test_add_tag(self):
        """
        Tests the pop up adding a tag
        """

        add_tag = Ui_Dialog_add_tag(self.imageViewer.data_browser, self.imageViewer.data_browser.project)
        QTest.mouseClick(add_tag.push_button_ok, 1)
        self.assertEqual(add_tag.msg.text(), "The tag name cannot be empty")

        add_tag = Ui_Dialog_add_tag(self.imageViewer.data_browser, self.imageViewer.data_browser.project)
        add_tag.text_edit_tag_name.setText("Type")
        QTest.mouseClick(add_tag.push_button_ok, 1)
        self.assertEqual(add_tag.msg.text(), "This tag name already exists")

        add_tag = Ui_Dialog_add_tag(self.imageViewer.data_browser, self.imageViewer.data_browser.project)
        add_tag.text_edit_tag_name.setText("Test")
        add_tag.combo_box_type.setCurrentText(populse_db.database.FIELD_TYPE_INTEGER)
        add_tag.type = populse_db.database.FIELD_TYPE_INTEGER
        add_tag.text_edit_default_value.setText("Should be integer")
        QTest.mouseClick(add_tag.push_button_ok, 1)
        self.assertEqual(add_tag.msg.text(), "Invalid default value")

        add_tag = Ui_Dialog_add_tag(self.imageViewer.data_browser, self.imageViewer.data_browser.project)
        add_tag.text_edit_tag_name.setText("Test")
        QTest.mouseClick(add_tag.push_button_ok, 1)
        self.assertTrue("Test" in self.imageViewer.project.database.get_fields_names(COLLECTION_CURRENT))
        self.assertTrue("Test" in self.imageViewer.project.database.get_fields_names(COLLECTION_INITIAL))

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    unittest.main()