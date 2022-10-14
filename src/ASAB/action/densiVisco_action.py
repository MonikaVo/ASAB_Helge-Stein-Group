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
from ASAB.driver import densiVisco_driver
from ASAB.utility.helpers import typeCheck

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
    savePath: a string giving the path to which the output files shall be saved. I does not include the file name.
    
    Outputs:
    results: a dictionary containing the status, value, quality and sample name of the individual results. Invalid results are replaced by NaN. '''

    # check the input types
    typeCheck(func=retrieveData, locals=locals())
    
    # call the driver function do perform a check
    results = densiVisco_driver.retrieveData(sampleName=sampleName, method=method, methodtype=methodtype, savePath=savePath)
    return results