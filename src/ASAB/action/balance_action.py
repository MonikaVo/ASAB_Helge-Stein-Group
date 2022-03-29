## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    # if the import was not successful, go to default config
    from ASAB.configuration import default_config
    conf = default_config.config
 
 ## Imports from ASAB
from ASAB.driver import balance_driver


def readBalance(bal):
    ''' This function calls the readBalance method of the balance_driver. It takes a balance object as an input parameter and returns a reading as a float. '''
    return bal.readBalance()

if __name__ == "__main__":
    bal = balance_driver.balance(simulated=conf["balance"]["simulated"])