import os

os.chdir(os.path.dirname(os.path.realpath(__file__)))

from Database.Database import Database

def test_database_creation():
    """
    Tests the creation of the database file at software opening
    """
    database = Database(None, True)
    folder = database.folder
    print(folder)
    database_folder = os.path.join(folder, "database", "mia2.db")
    print(database_folder)
    assert os.path.exists(database_folder) == True

total_tests = 0
failed_tests = []

try:
    total_tests += 1
    test_database_creation()
except Exception:
    failed_tests.append("database_creation")

if len(failed_tests) > 0:
    errorMessage = "Some tests failed.\n"
    errorMessage += str(len(failed_tests)) + "/" + str(total_tests)  + " tests failed.\n"
    errorMessage += "Here is a list of the tests that failed:\n"
    for failed in failed_tests:
        errorMessage += "\t" + failed + "\n"
    raise Exception(errorMessage)