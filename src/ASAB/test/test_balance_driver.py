from ASAB.test.FilesForTests import config_test
conf = config_test.config

# ASAB imports
from ASAB.driver import balance_driver

# Other imports
import serial

def test___init__():
    # get the target values for the port, the settings and the simulation
    port_target = conf["balanceDriver"]["serialPort"]
    settings_target = conf["balanceDriver"]["settings"]
    simulated_target = conf["balanceDriver"]["simulated"]

    # instantiate a balance object using the respective settings
    balance1 = balance_driver.balance()

    # ensure, that the port is a Serial port or an emulated prot depending on the simulation parameter
    portType_result = type(balance1.port)
    if balance1.simulated:
        portType_target = balance_driver.emulatedPort
    else:
        portType_target = serial.Serial
    assert portType_result == portType_target, f'The serial port is of type {type(balance1.port)} instead of {portType_target}.'


    # get the port, settings and simulation from the balance object
    port_result = balance1.port.port
    settings_result = balance1.port.get_settings()
    simulated_result = balance1.simulated

    # check the three parameters
    assert port_target == port_result, f'The port is {port_result} instead of {port_target}.'
    assert settings_target == settings_result, f'The settings are {settings_result} instead of {settings_target}.'
    assert simulated_target == simulated_result, f'The simulation status is {simulated_result} instead of {simulated_target}.'

def test_readBalance():
    # instantiate the balance in a simulated mode
    balance2 = balance_driver.balance(simulated=True)

    # read from the simulated balance instance
    reading_result = balance2.readBalance()
    # get the target value for the port
    reading_target = balance2.port.target

    # check the reading
    assert reading_target == reading_result, f'The reading is {reading_result} instead of {reading_target}.'