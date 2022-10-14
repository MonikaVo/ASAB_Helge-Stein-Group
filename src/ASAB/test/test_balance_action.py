from ASAB.test.FilesForTests import config_test
conf = config_test.config

# ASAB imports
from ASAB.driver import balance_driver

def test_readBalance():
    # instantiate a simulated balance instance
    balance2 = balance_driver.balance(simulated=True)

    # read the value from the balance
    reading_result = balance2.readBalance()
    # get the target value for the balance instance
    reading_target = balance2.port.target

    # check the readings
    assert reading_result==reading_target, f'Readings to not match, result is {reading_result}, target is {reading_target}'
