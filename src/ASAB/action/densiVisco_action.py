from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

## Imports from ASAB
from ASAB.driver import densiVisco_driver
from ASAB.utility.helpers import typeCheck

# Other imports
import logging

# create a logger for this module
logger_densiVisco_action = logging.getLogger(f"run_logger.{__name__}")


def measure(sampleName:str, method:str="Density"):
    ''' This function calls the driver function "measure" to perform a measurement.
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample for the measurement
    method: a string defining the method to be used as defined on the measuring device
    
    Outputs:
    This function has no outputs. '''

    # check the input types
    typeCheck(func=measure, locals=locals())

    # call the driver function do perform a measurement
    densiVisco_driver.measure(sampleName=sampleName, method=method)
    logger_densiVisco_action.info(f"{measure.__name__}\n"
                                  f"Measurement triggered."
                                  f"Sample name:\t{sampleName}\n"
                                  f"method:\t{method}")

def check(sampleName:str, checktype:str, method:str="Density"):
    ''' This function calls the driver function "check" to perform a check.
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample for the check
    checktype: a string defining the type of check to be performed. This label needs to be defined in the device
    method: a string defining the method to be used as defined on the measuring device
    
    Outputs:
    This function has no outputs. '''

    # check the input types
    typeCheck(func=check, locals=locals())

    # call the driver function do perform a check
    densiVisco_driver.check(sampleName=sampleName, checktype=checktype, method=method)

def retrieveData(sampleName:str, method:str, methodtype:str, savePath:str):
    ''' This funciton calls the driver function "retrieveData" to retrieve data from density and viscosity measurements and save them in a dict data format to a .json file in the specified folder (savePath).
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample for the measurement
    method: a string defining the method to be used as defined on the measuring device
    methodtype: a string defining the type of the method. This can be a check or a measurement.
    savePath: a string giving the path to which the output files shall be saved. It does not include the file name.
    
    Outputs:
    results: a dictionary containing the status, value, quality and sample name of the individual results. Invalid results are replaced by NaN. '''

    # check the input types
    typeCheck(func=retrieveData, locals=locals())
    
    # call the driver function do perform a check
    results = densiVisco_driver.retrieveData(sampleName=sampleName, method=method, methodtype=methodtype, savePath=savePath)
    logger_densiVisco_action.info(f"{retrieveData.__name__}\n"
                                  f"Data retrieved: {results}")
    return results