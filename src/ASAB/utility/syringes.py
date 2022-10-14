## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError as ie:
    # if the import fails, check, if it is a test, which means, that a file in a pytest folder will be main and thus it will be in the path returned in the error message of the ImportError.
    if ('pytest' in str(ie)):
        # the software will produce a warning, which reports the switch to the testing configuration. This warning is always shown.
        import warnings
        warnings.filterwarnings('always')
        warnings.warn('Configuration from main not available, but this looks like a test. Loading test configuration instead.', category=ImportWarning)
        # the filtering funcitons are set to default again
        warnings.filterwarnings('default')
        # the test configuration is imported
        from ASAB.test.FilesForTests import config_test
        conf = config_test.config
    # if "pytest" is not in the error message, it is assumed, that the call did not originate from a test instance and it therefore raises the ImportError.
    else:
        raise ie

## Imports from ASAB
from ASAB.utility.helpers import loadTxtFile, loadVariable, saveToFile

## Other imports
import numpy as np

class syringe:
    """
    Class to define a syringe.
    """
    def __init__(self, desig:str, inner_dia_mm:float, piston_stroke_mm:float) -> None:
        ''' This function initialises the properties of a syringe
        
        Inputs:
        desig: a string representing the label of the syringe
        inner_dia_mm: a floating point number reporting the inner diameter of the syringe in mm
        piston_stroke_mm: a floating point number reporting the range of motion for the piston of the syringe in mm
        
        Outputs:
        This function has no outputs. '''

        # set all the parameters for the syringe and calculate the ones, which are implicit
        self.desig = desig
        self.inner_dia_mm = inner_dia_mm
        self.piston_stroke_mm = piston_stroke_mm
        self.minimum_volume_mL = np.around(((np.pi*(inner_dia_mm/2.)**2.*piston_stroke_mm)/1000.) * 0.15, 4) # 15 % of the total volume. Minimum according to user manual of syringes.   https://arrayjson.com/numpy-pi/
        self.minimum_flow_mL_per_sec = (np.pi * (self.inner_dia_mm/2.)**2. * (1.042/1000.))/1000. # this gives the minimum non-zero flow! Zero is possible for all syringes. The minimum pulsation free speed of the gear is 1.042 µL/s as per the Cetoni manual.
        self.maximum_flow_mL_per_sec = (np.pi * (self.inner_dia_mm/2.)**2. * (6.33))/1000.  # The maximum speed of the gear is 6.33 mm/s as per the Cetoni manual.

def from_dict(dict:dict) -> syringe:
    ''' This function initialises a syringe based on a dictionary containing the attributes as keys and their respective values as value
    
    Inputs:
    dict: a dictionary containing the attributes of a syringe as keys and their respective values as values
    
    Outputs:
    syringeFromDict: a syringe object with the attributes as defined in dict '''

    # instantiate a syringe based on the information in dict
    syringeFromDict = syringe(desig=dict["desig"], inner_dia_mm=dict["inner_dia_mm"], piston_stroke_mm=dict["piston_stroke_mm"])
    return syringeFromDict

def loadSyringeDict(path_to_syringeDict:str) -> dict:
    ''' This function initialises an empty syringeDict and loads syringes from a file
    
    Inputs:
    path_to_syringeDict: a string specifying, where the file containing the dictionary of syringes is stored

    Outputs:
    syringeDict: a dictionary containing syringe objects as values '''

    # instantiate an empty dictionary
    syringeDict = {}
    # load the file from the given path
    dataDict = loadVariable(loadPath=path_to_syringeDict, variable='Syringes')
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
folderPath = '\\'.join(conf["syringes"]["savePath"].split('\\')[:-1])
name = conf["syringes"]["savePath"].split('\\')[-1].split('.')[0]
extension = conf["syringes"]["savePath"].split('\\')[-1].split('.')[1]
saveToFile(folder=folderPath, filename=name, extension=extension, data=f"Syringes = {str(Syringes)}")