import unittest
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from Project.Project import Project
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

if __name__ == '__main__':
    unittest.main()