import unittest
import pandas as pd
from experiment import chemicals

# TODO: import of chemicals

class testChemicals(unittest.TestCase): # https://data-flair.training/blogs/python-unittest/
    # Test SaveToFile
    def test_SafeToFile(self):
        pass
    
    # Test __init__: Are the attributes correctly assigned to the object?
    def test_init(self):
        chem = chemicals.chemical("H2O", "water", 0.9982, 18.02)
        self.assertEqual([chem.nameShort, chem.nameLong, chem.density, chem.molarMass], ["H2O", "water", 0.9982, 18.02])

    # Test getChemicalsList: Are the entries in the generated chemList object correct?
    def test_getChemicalsList(self):
        chem_data = pd.read_csv(r"Chemicals_test_database.csv")
        lst = chemicals.getChemicalsList(chem_data)
        self.assertDictEqual(lst["H2O"].__dict__,{'nameShort': 'H2O', 'nameLong': 'water', 'density': 0.9982, 'molarMass': 18.02})
        self.assertDictEqual(lst["EtOH"].__dict__,{'nameShort': 'EtOH', 'nameLong': 'ethanol', 'density': 0.7893, 'molarMass': 46.07})

    # Test loadChemicalsList: Are the entries in the loaded chemList object correct?
    def test_loadChemicalsList(self):
        lst2 = chemicals.loadChemicalsList(r"chemList_test")
        self.assertDictEqual(lst2["H2O"].__dict__,{'nameShort': 'H2O', 'nameLong': 'water', 'density': 0.9982, 'molarMass': 18.02})
        self.assertDictEqual(lst2["EtOH"].__dict__,{'nameShort': 'EtOH', 'nameLong': 'ethanol', 'density': 0.7893, 'molarMass': 46.07})    