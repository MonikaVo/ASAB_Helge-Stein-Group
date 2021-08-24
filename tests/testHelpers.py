import unittest
from testfixtures import compare
import pickle
import os
import sys
import helpers


print("\n Test of function in helpers.py. \n")

class testHelpers(unittest.TestCase):
    def test_SaveToFile(self):
        testDict_save = {"this": 1, "is": "two", "1": "a", "test": {"of": 5, "the": "save"}}
        helpers.SaveToFile(r"tests/filesForTests/test_save.pck", testDict_save)
        with open (r"tests/filesForTests/test_save.pck", "rb") as file:
            loaded_save = pickle.load(file)
        compare(testDict_save, loaded_save)

    def test_LoadFile(self):
        testDict_load = {"this": 1, "is": "two", "1": "a", "test": {"of": 5, "the": "save"}}
        loaded_load = helpers.LoadFile(r"tests/filesForTests//test_save.pck")
        compare(testDict_load, loaded_load)

    def test_ListToDict(self):
        lst1 = ["a", "b", "c", "d"]
        dict1 = {0: "a", 1: "b", 2: "c", 3: "d"}
        dict1_help = helpers.ListToDict(lst1)
        lst2 = [1, 2, 3, 4]
        dict2 = {0: 1, 1: 2, 2: 3, 3: 4}
        dict2_help = helpers.ListToDict(lst2)
        lst3 = [1, "b", "see", 4]
        dict3 = {0: 1, 1: "b", 2: "see", 3: 4}
        dict3_help = helpers.ListToDict(lst3)       
        compare(dict1, dict1_help)
        compare(dict2, dict2_help)
        compare(dict3, dict3_help)

    def test_LoadConfig(self):
        confg = helpers.LoadConfig(r"tests/filesForTests/config_test.json")
        config_dict = {"paths": { "ASAB": ".../ASAB",  # edited prior to publication
        "QmixSDK_python": ".../QmixSDK/lib/python",  # edited prior to publication
        "QmixSDK": ".../QmixSDK",  # edited prior to publication
        "HardwareConfig": ".../ASAB_Config1_sim"}}  # edited prior to publication
        assert(".../ASAB" in sys.path and ".../QmixSDK/lib/python" in sys.path)  # edited prior to publication

if __name__ == "__main__":
    unittest.main(verbosity=2)