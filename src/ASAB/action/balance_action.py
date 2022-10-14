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
from ASAB.driver import balance_driver
from ASAB.utility.helpers import typeCheck


def readBalance(bal:balance_driver.balance) -> float:
    ''' This function calls the readBalance method of the balance_driver. It takes a balance object as an input parameter and returns a reading as a float.
    Inputs:
    bal: a balance object, from which to read the value
    
    Outputs:
    reading: a float representing the sign and the value of the reading '''

    # check the input types
    typeCheck(func=readBalance, locals=locals())
    # return the value read from the balance using the respective driver function
    return bal.readBalance()

if __name__ == "__main__":
    bal = balance_driver.balance(simulated=conf["balance"]["simulated"])