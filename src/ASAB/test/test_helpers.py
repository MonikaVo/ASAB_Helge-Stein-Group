from ASAB.configuration import default_config
conf = default_config.config

import ASAB.utility.helpers


print("\n Test of function in helpers.py. \n")

def test_saveToFile():
    testDict_save = {"this": 1, "is": "two", "1": "a", "test": {"of": 5, "the": "save"}}
    print(testDict_save)
    ASAB.utility.helpers.saveToFile(r"ASAB/test/FilesForTests/test_save.txt", testDict_save)
    with open (r"ASAB/test/FilesForTests/test_save.txt", "r") as file:
        loaded_save = file.readlines()[0]
    dict_loaded = eval(loaded_save)
    assert(testDict_save == dict_loaded)

def test_loadTxtFile():
    # Use helper function to load and evaluate
    withHelper = ASAB.utility.helpers.loadTxtFile(loadPath=r"ASAB/test/FilesForTests/test_save.txt")
    # Read and evaluate for reference
    with open (r"ASAB/test/FilesForTests/test_save.txt", "r") as file:
        loaded_save = file.readlines()[0]
    read = eval(loaded_save)
    assert(read == withHelper)