## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    # if the import was not successful, go to default config
    from ASAB.configuration import default_config
    conf = default_config.config

from utility.helpers import saveToFile

import numpy as np

class syringe:
    """
    Class to define a syringe.
    """
    def __init__(self, desig:str, inner_dia_mm:float, piston_stroke_mm:float):
        # Initialise the properties of the syringe
        self.desig = desig
        self.inner_dia_mm = inner_dia_mm
        self.piston_stroke_mm = piston_stroke_mm
        self.minimum_volume_mL = np.around(((np.pi*(inner_dia_mm/2.)**2*piston_stroke_mm)/1000.) * 0.15, 4) # 15 % of the total volume. Minimum according to user manual of syringes.   https://arrayjson.com/numpy-pi/

# List of available Syringes:
syr_25ml = syringe(desig="25_ml", inner_dia_mm=23.0329, piston_stroke_mm=60.)
syr_10ml = syringe(desig="10_ml", inner_dia_mm=14.5673, piston_stroke_mm=60.)
syr_5ml = syringe(desig="5_ml", inner_dia_mm=10.3006, piston_stroke_mm=60.)
syr_2_5ml = syringe(desig="2_5_ml", inner_dia_mm=7.28366, piston_stroke_mm=60.)
syr_1ml = syringe(desig="1_ml", inner_dia_mm=4.60659,piston_stroke_mm=60.)
syr_25myl = syringe(desig="25_myl", inner_dia_mm=0.728366, piston_stroke_mm=60.)

# Dictionary inlcluding the available syringes:
Syringes = {"25_ml": syr_25ml, "10_ml": syr_10ml, "25_myl": syr_25myl, "1_ml": syr_1ml, "2_5_ml": syr_2_5ml, "5_ml": syr_5ml}
saveToFile(saveFile=conf["syringes"]["savePath"], data=Syringes)

#TODO: Add minimum and maximum flow