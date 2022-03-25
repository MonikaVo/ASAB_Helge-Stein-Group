from pickle import load
import unittest
from tests.filesForTests import config_test
import utility
from utility.helpers import doAppends, loadFile
conf = config_test.config
doAppends(conf)

import unittest
from testfixtures import compare

from utility import syringes
from utility.syringes import syringe

class test_syringes(unittest.TestCase):
    
    def test__init__(self):
        syr1 = syringes.syringe(desig=conf["syringes"]["testInput"]["testInit"][0]["designation"], inner_dia_mm=conf["syringes"]["testInput"]["testInit"][0]["innerDia"], piston_stroke_mm=conf["syringes"]["testInput"]["testInit"][0]["pistonStroke"])
        self.assertEqual(first=syr1.desig, second=conf["syringes"]["testInput"]["testInit"][0]["designation"], msg="Designation not correct.")
        self.assertEqual(first=syr1.inner_dia_mm, second=conf["syringes"]["testInput"]["testInit"][0]["innerDia"], msg="Inner diameter not correct.")
        self.assertEqual(first=syr1.piston_stroke_mm, second=conf["syringes"]["testInput"]["testInit"][0]["pistonStroke"], msg="Piston Stroke not correct.")

        syr2 = loadFile(loadFile=conf["syringes"]["savePath"])["2_5_ml"]
        self.assertEqual(first=syr2.desig, second=conf["syringes"]["testInput"]["testInit"][1]["designation"], msg="Designation not correct.")
        self.assertEqual(first=syr2.inner_dia_mm, second=conf["syringes"]["testInput"]["testInit"][1]["innerDia"], msg="Inner diameter not correct.")
        self.assertEqual(first=syr2.piston_stroke_mm, second=conf["syringes"]["testInput"]["testInit"][1]["pistonStroke"], msg="Piston Stroke not correct.")

if __name__ == "__main__":
    unittest.main(verbosity=2)