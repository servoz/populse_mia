import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from Project.Project import Project, COLLECTION_CURRENT, COLLECTION_INITIAL
from MainWindow.Main_Window import Main_Window

class TestMIADataBrowser(unittest.TestCase):

    def setUp(self):
        self.app = QApplication([])
        self.project = Project(None, True)
        self.imageViewer = Main_Window(self.project)

    def tearDown(self):
        pass

    def test_unnamed_project_software_opening(self):
        self.assertIsInstance(self.project, Project)
        self.assertEqual(self.imageViewer.project.getName(), "Unnamed project")
        tags = self.imageViewer.project.database.get_fields_names(COLLECTION_CURRENT)
        self.assertEqual(len(tags), 3)
        self.assertTrue("Checksum" in tags)
        self.assertTrue("FileName" in tags)
        self.assertTrue("Type" in tags)
        self.assertEqual(self.imageViewer.project.database.get_documents_names(COLLECTION_CURRENT), [])
        collections = self.imageViewer.project.database.get_collections_names()
        self.assertEqual(len(collections), 2)
        self.assertTrue(COLLECTION_INITIAL in collections)
        self.assertTrue(COLLECTION_CURRENT in collections)

if __name__ == '__main__':
    unittest.main()