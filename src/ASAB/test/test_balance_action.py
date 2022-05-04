from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.driver import balance_driver

def test_readBalance():
    balance2 = balance_driver.balance(simulated=True)

    reading_result = balance2.readBalance()
    reading_target = balance2.port.target

    assert reading_target==reading_result
    #assertEqual(first=reading_target, second=reading_result, msg="Readings do not match.")
