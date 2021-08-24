import sys
sys.path.append(r"..")      # https://stackoverflow.com/questions/4383571/importing-files-from-different-folder
from experiment import calcComp
from experiment import chemicals
import unittest
import numpy as np

# generate chemList, when chemList already exist, then load chemList
chemList = chemicals.loadChemicalsList("chemList")

print(chemList)

def test_calcComp():
    # https://stackoverflow.com/questions/12136762/assertalmostequal-in-python-unit-test-for-collections-of-floats#12139899
    np.testing.assert_almost_equal(calcComp.calcComp(chemList, [1, 1], ["EtOH", "H2O"], 2.0), [1.527549, 0.472451], decimal=5)
    np.testing.assert_almost_equal(calcComp.calcComp(chemList, [0.5, 0.5], ["EtOH", "H2O"], 2.0), [1.527549, 0.472451], decimal=5)
    np.testing.assert_almost_equal(calcComp.calcComp(chemList, [1, 2], ["hexane", "EtOH"], 1.0), [0.52798, 0.47202], decimal=5)
    np.testing.assert_almost_equal(calcComp.calcComp(chemList, [1, 2], ["hexane", "EtOH"], 0.5), [0.26399, 0.23601], decimal=5)
    np.testing.assert_almost_equal(calcComp.calcComp(chemList, [0.2, 0.7, 0.1], ["EtOH", "H2O", "hexane"], 1), [0.312397, 0.338171, 0.349432], decimal=5)
    np.testing.assert_almost_equal(calcComp.calcComp(chemList, [7, 15, 9], ["acetone", "toluene", "hexane"], 18),[2.82555, 8.7222 , 6.45225], decimal=5)

test_calcComp()
