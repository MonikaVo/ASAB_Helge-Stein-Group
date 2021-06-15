import unittest
import os
print(os.getcwd())
import sys
sys.path.append(r"../tests")
sys.path.append(r"../experiment")
sys.path.append(r"..")
from experiment import chemicals
from testfixtures import compare
import pickle


class testChemicals(): # https://data-flair.training/blogs/python-unittest/
    # # Test SaveToFile
    # def test_SaveToFile(self):
    #     dct = {"1": "write", "2": 1.0, "3": "information", "3": 2, "4": "file"}
    #     chemicals.SaveToFile(r"tests/test_save", dct)
    #     with open(r"tests/test_save", "rb") as d_load:
    #         dct_loaded = pickle.load(d_load)
    #     self.assertDictEqual(dct_loaded, dct)
    
    # # Test __init__: Are the attributes correctly assigned to the object?
    # def test_init(self):
    #     chem = chemicals.chemical("H2O", "water", 0.9982, 18.02)
    #     self.assertEqual([chem.nameShort, chem.nameLong, chem.density, chem.molarMass], ["H2O", "water", 0.9982, 18.02])


    # # Test getChemicalsList: Are the entries in the generated chemList object correct?
    # def test_getChemicalsList(self):
    #     lst = chemicals.getChemicalsList(r"tests/Chemicals_test_database.csv")
    #     compareList = {"H2O": chemicals.chemical("H2O", "water", 0.9982, 18.02), "EtOH": chemicals.chemical('EtOH', 'ethanol', 0.7893, 46.07)}
    #     compare(lst["H2O"], compareList["H2O"])  # https://testfixtures.readthedocs.io/en/latest/comparing.html
    #     compare(lst["EtOH"], compareList["EtOH"])


    # Test loadChemicalsList: Are the entries in the loaded chemList object correct?
    def test_loadChemicalsList(self, path = r"../tests/chemList_test.pck"):
        print(os.getcwd())
        lst2 = chemicals.loadChemicalsList(path)
        print(os.getcwd())
        print(lst2.keys())
        print(lst2)
        print(lst2["H2O"].nameShort)
        #self.assertEqual(1,1)
        # compareList = {"H2O": chemicals.chemical("H2O", "water", 0.9982, 18.02), "EtOH": chemicals.chemical('EtOH', 'ethanol', 0.7893, 46.07)}
        # compare(lst2["H2O"], compareList["H2O"])  # https://testfixtures.readthedocs.io/en/latest/comparing.html
        # compare(lst2["EtOH"], compareList["EtOH"])

if __name__ == "__main__":
    #unittest.main(verbosity=2)
    t = testChemicals()
    p = t.test_loadChemicalsList()
    print(type(p))