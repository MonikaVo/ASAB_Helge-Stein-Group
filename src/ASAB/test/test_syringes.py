from ASAB.test.FilesForTests import config_test
conf = config_test.config
from ASAB.utility import syringes

def test__init__():
    syr1 = syringes.syringe(desig=conf["syringes"]["testInput"]["testInit"][0]["designation"], inner_dia_mm=conf["syringes"]["testInput"]["testInit"][0]["innerDia"], piston_stroke_mm=conf["syringes"]["testInput"]["testInit"][0]["pistonStroke"])
    assert syr1.desig == conf["syringes"]["testInput"]["testInit"][0]["designation"], "Designation not correct."
    assert syr1.inner_dia_mm == conf["syringes"]["testInput"]["testInit"][0]["innerDia"], "Inner diameter not correct."
    assert syr1.piston_stroke_mm == conf["syringes"]["testInput"]["testInit"][0]["pistonStroke"], "Piston Stroke not correct."

    syr2 = syringes.loadSyringeDict(conf["syringes"]["savePath"])["2_5_mL"]
    assert syr2.desig == conf["syringes"]["testInput"]["testInit"][1]["designation"], "Designation not correct." 
    assert syr2.inner_dia_mm == conf["syringes"]["testInput"]["testInit"][1]["innerDia"], "Inner diameter not correct." 
    assert syr2.piston_stroke_mm == conf["syringes"]["testInput"]["testInit"][1]["pistonStroke"], "Piston Stroke not correct."