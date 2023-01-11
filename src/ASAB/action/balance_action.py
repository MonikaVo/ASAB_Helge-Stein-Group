from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

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