from numpy.random import sample
if __name__ == "__main__":
    from configuration import config
    conf = config.config
else:
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module

from utility.helpers import doAppends, loadFile
doAppends(conf)

from driver import balance_driver


def readBalance(bal):
    ''' This function calls the readBalance method of the balance_driver. It takes a balance object as an input parameter and returns a reading as a float. '''
    return bal.readBalance()


if __name__=="__main__":
    bal = balance_driver.balance(simulated=conf["balance"]["simulated"])