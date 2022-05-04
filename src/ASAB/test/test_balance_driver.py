from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.driver import balance_driver

def test___init__():
    port_target = conf["balanceDriver"]["serialPort"]
    settings_target = conf["balanceDriver"]["settings"]

    balance1 = balance_driver.balance(simulated=False)

    port_result = balance1.port.port
    settings_result = balance1.port.get_settings()

    assert port_target == port_result
    assert settings_target == settings_result



def test_readBalance():
    balance2 = balance_driver.balance(simulated=True)

    reading_result = balance2.readBalance()
    reading_target = balance2.port.target

    assert reading_target == reading_result