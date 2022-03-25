from configuration import config
conf = config.config

import unittest
from testfixtures import compare
import pickle
import utility.helpers


print("\n Test of function in helpers.py. \n")

class testHelpers(unittest.TestCase):
    def test_saveToFile(self):
        testDict_save = {"this": 1, "is": "two", "1": "a", "test": {"of": 5, "the": "save"}}
        utility.helpers.saveToFile(r"tests/filesForTests/test_save.pck", testDict_save)
        with open (r"tests/filesForTests/test_save.pck", "rb") as file:
            loaded_save = pickle.load(file)
        compare(testDict_save, loaded_save)

    def test_loadFile(self):
        testDict_load = {"this": 1, "is": "two", "1": "a", "test": {"of": 5, "the": "save"}}
        loaded_load = utility.helpers.loadFile(r"ASAB/test/FilesForTests//test_save.pck")
        compare(testDict_load, loaded_load)

if __name__ == "__main__":
    unittest.main(verbosity=2)