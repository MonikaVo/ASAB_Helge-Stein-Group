## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    # if the import was not successful, go to default config
    from ASAB.configuration import default_config
    conf = default_config.config

from ASAB.utility.helpers import loadTxtFile, saveToFile

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

def from_dict(dict:dict):
    # This function initialises a syringe based on a dict containing the attributes as keys and their respective values as value
    syringeFromDict = syringe(desig=dict["desig"], inner_dia_mm=dict["inner_dia_mm"], piston_stroke_mm=dict["piston_stroke_mm"])
    return syringeFromDict

def loadSyringeDict(path_to_syringeDict:str):
    # initialise an empty syringeDict
    syringeDict = {}
    dataDict = loadTxtFile(path_to_syringeDict)
    # Make the values in the dict to syringes
    for key, value in dataDict.items():
        syringeDict[key] = from_dict(value)
    return syringeDict

# List of available Syringes:
syr_25mL = syringe(desig="25_mL", inner_dia_mm=23.0329, piston_stroke_mm=60.)
syr_10mL = syringe(desig="10_mL", inner_dia_mm=14.5673, piston_stroke_mm=60.)
syr_5mL = syringe(desig="5_mL", inner_dia_mm=10.3006, piston_stroke_mm=60.)
syr_2_5mL = syringe(desig="2_5_mL", inner_dia_mm=7.28366, piston_stroke_mm=60.)
syr_1mL = syringe(desig="1_mL", inner_dia_mm=4.60659,piston_stroke_mm=60.)
syr_25myl = syringe(desig="25_myl", inner_dia_mm=0.728366, piston_stroke_mm=60.)

# Dictionary inlcluding the available syringes:
Syringes = {"25_mL": syr_25mL.__dict__, "10_mL": syr_10mL.__dict__, "25_myl": syr_25myl.__dict__, "1_mL": syr_1mL.__dict__, "2_5_mL": syr_2_5mL.__dict__, "5_mL": syr_5mL.__dict__}
saveToFile(savePath=conf["syringes"]["savePath"], data=str(Syringes))

#TODO: Add minimum and maximum flow
