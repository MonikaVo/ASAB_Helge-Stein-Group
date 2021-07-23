import sys
sys.path.append(".../QmixSDK/lib/python")  # edited prior to publication
sys.path.append(r"..")  # edited prior to publication
from helpers import SaveToFile

class syringe:
    """
    Class to define a syringe.
    """
    def __init__(self, desig, inner_dia_mm, piston_stroke_mm):
        self.desig = desig
        self.inner_dia_mm = inner_dia_mm
        self.piston_stroke_mm = piston_stroke_mm

    def get_desig(self):
        return self.desig

    def get_inner_dia_mm(self):
        return self.inner_dia_mm

    def get_piston_stroke_mm(self):
        return self.piston_stroke_mm

    def set_desig(self, new_desig):
        self.desig = new_desig
        return self.desig

    def set_inner_dia_mm(self, new_dia):
        self.inner_dia_mm = new_dia
        return self.inner_dia_mm

    def set_piston_stroke_mm(self, new_stroke):
        self.piston_stroke_mm = new_stroke
        return self.piston_stroke_mm

# List of available Syringes:
syr_25ml = syringe("25_ml", 23.0329, 60)
syr_25myl = syringe("25_myl", 0.728366, 60)
syr_1ml = syringe("1_ml", 4.60659, 60)
syr_2_5ml = syringe("2_5_ml", 7.28366, 60)

# Dictionary inlcluding the available syringes:
Syringes = {"25_ml": syr_25ml, "25_myl": syr_25myl, "1_ml": syr_1ml, "2_5_ml": syr_2_5ml}
SaveToFile(r"filesForOperation/hardware/syringes.pck", Syringes)