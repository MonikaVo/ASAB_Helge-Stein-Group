# Import configurations
from ctypes import c_longlong
from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.configuration import config
cf = config.configASAB

# Imports from ASAB
from ASAB.driver import Arduino_driver

# Other imports
import serial

print("\n Test of functions in Arduino_driver.py. \n")

def test_Arduino__init__():
    # instatiate the test object
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], number=conf['ArduinoDriver']['Arduino'][0]['ArduinoNo'], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])

    # ensure, that the port is a Serial port or an emulated prot depending on the simulation parameter
    portType_result = type(Arduino_test.port)
    if Arduino_test.simulated:
        portType_target = Arduino_driver.emulatedPort
    else:
        portType_target = serial.Serial
    assert portType_result == portType_target, f'The serial port is of type {type(Arduino_test.port)} instead of {portType_target}.'

    # check the name of the Arduino object
    name_result = Arduino_test.name
    name_target = conf["test_ArduinoDriver"]["inputs"]["nameArduino"]
    assert name_result == name_target, f"The name is {name_result} instead of {name_target}."

    # check the number of the Arduino object
    number_result = Arduino_test.number
    number_target = conf['ArduinoDriver']['Arduino'][0]['ArduinoNo']
    assert number_result == number_target, f"The number is {number_result} instead of {number_target}."

    
    # check the port for the Arduino object
    port_result = Arduino_test.port.port
    port_target = conf['ArduinoDriver']['Arduino'][0]['serialPort']
    assert port_result == port_target, f'The port is {port_result} instead of {port_target}.'

    # check the settings
    settings_result = Arduino_test.port.get_settings()
    settings_target = conf['ArduinoDriver']['Arduino'][0]['settings']
    for key in settings_target.keys():
        assert settings_result[key] == settings_target[key], f'The setting for {key} is {settings_result[key]} instead of {settings_target[key]}.'

    # check simulation parameter
    simulated_test = Arduino_test.simulated
    simulated_target = conf['ArduinoDriver']['Arduino'][0]['simulated']
    assert simulated_test == simulated_target, f'Test Arduino is simulated {simulated_test} instead of {simulated_target}.'

    ## close the serial communication
    Arduino_test.port.close()


def test_Arduino_connect():
    # instatiate the test object
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])

    # start the communication
    Arduino_test.connect()

    # check that the port is open
    portState_result = Arduino_test.port.is_open
    assert portState_result == True, f'The port is open {portState_result} instead of True.'

    ## close the serial communication
    Arduino_test.port.close()


def test_Arduino_disconnect():
    # instatiate the test object
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])

    # start the communication
    Arduino_test.connect()

    # if the port is open, close it
    if Arduino_test.port.is_open:
        Arduino_test.disconnect()
        # check, that the port is closed
        portState_result = Arduino_test.port.is_open
        assert portState_result == False, f'The port is open {portState_result} instead of True.'
    else:
        assert True == False, 'The port was not opened and can therefore not be closed.'

    ## close the serial communication
    Arduino_test.port.close()


def test_ArduinoRelay__init__():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])

    # check the port
    port_result = Relay_test.port.port
    port_target = conf['ArduinoDriver']['Arduino'][0]['serialPort']
    assert port_result == port_target, f'The port is {port_result} instead of {port_target}.'

    # check the relay name
    relayname_result = Relay_test.name
    relayname_target = conf['test_ArduinoDriver']['inputs']['nameRelay']
    assert relayname_result == relayname_target, f'The relayNo is {relayname_result} instead of {relayname_target}.'

    # check the relay number
    relayNo_result = Relay_test.relayNo
    relayNo_target = conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo']
    assert relayNo_result == relayNo_target, f'The relayNo is {relayNo_result} instead of {relayNo_target}.'

    # check the connected Arduino
    arduino_result = Relay_test.Arduino
    arduino_target = Arduino_test
    assert arduino_result == arduino_target, f'The Arduino is {arduino_result} instead of {arduino_target}.'


def test_ArduinoRelay_setRelayState():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])

    # start the communication
    Arduino_test.connect()

    # get the state of the ArduinoRelay before applying setRelayState
    stateBefore = Arduino_test.port.readline().decode('ascii')
    # get the target and required initial state from the configuration file
    state_target = conf['test_ArduinoDriver']['targets']['setRelayState']['targetState']
    stateInitial = conf['test_ArduinoDriver']['inputs']['setRelayState']['initState']

    # The test is only useful, if stateBefore is equal to the configured initial state and different from the target state
    if (int(stateBefore) == stateInitial) and (int(stateBefore) != state_target):
        # apply the function and ensure the result
        state_result = Relay_test.setRelayState(state_target)
        assert state_result == state_target, f'The state is {state_result} instead of {state_target}.'
    # If the relay is in the wrong start state, the test shall fail with a respective message.
    else:
        assert True == False, f'The inital state of the relay is {stateBefore}, but state {stateInitial} is needed.'

    ## close the serial communication
    Arduino_test.port.close()


    ## Check the result for an empty return string using a simulated Arduino

    # instantiate a simulated Arduino
    Arduino_test2 = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=True)
    # set the new simulated Arduino up to return empty strings
    Arduino_test2.port.returnEmpty = True
    # instantiate an ArduinoRelay based on the simulated Arduino
    Relay_test2 = Arduino_driver.ArduinoRelay(Arduino=Arduino_test2, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])

    # define the state to set
    state_set2 = 1
    # define the target result upon receiving and empty string
    state_target2 = 2

    # apply the function and ensure the result
    state_result2 = Relay_test2.setRelayState(state_set2)
    assert state_result2 == state_target2, f'The state is {state_result2} instead of {state_target2}.'

    ## close the serial communication
    Arduino_test.port.close()


def test_ArduinoRelay_getRelayState():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])

    # start the communication
    Arduino_test.connect()

    # get the current state of the ArduinoRelay
    state_target = int(Arduino_test.port.readline().decode('ascii'))

    # apply the function and ensure the result
    state_result = Relay_test.getRelayState()
    assert state_result == state_target, f'The read state is {state_result} instead of {state_target}.'

    ## close the serial communication
    Arduino_test.port.close()


    ## Check the result for an empty return string using a simulated Arduino

    # instantiate a simulated Arduino
    Arduino_test2 = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=True)
    # set the new simulated Arduino up to return empty strings
    Arduino_test2.port.returnEmpty = True
    # instantiate an ArduinoRelay based on the simulated Arduino
    Relay_test2 = Arduino_driver.ArduinoRelay(Arduino=Arduino_test2, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])

    # define the target result upon receiving and empty string
    state_target2 = 2

    # apply the function and ensure the result
    state_result2 = Relay_test2.getRelayState()
    assert state_result2 == state_target2, f'The read state is {state_result2} instead of {state_target2}.'

    ## close the serial communication
    Arduino_test.port.close()


def test_ArduinoValve__init__():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])
    #instantiate the valve
    Valve_test = Arduino_driver.ArduinoValve(name=conf['ArduinoDriver']['ArduinoValve'][0]['name'], relay=Relay_test, Arduino=Arduino_test, positions=conf['ArduinoDriver']['ArduinoValve'][0]['positions'])
    
    # get the target values

    # The handles cannot be compared
    # handle_target = c_longlong(conf['test_ArduinoDriver']['targets']['init']['handle'])
    name_target = conf['ArduinoDriver']['ArduinoValve'][0]['name']
    positions_target = conf['ArduinoDriver']['ArduinoValve'][0]['positions']
    noOfPositions_target= len(conf['ArduinoDriver']['ArduinoValve'][0]['positions'])
    relay_target = Relay_test
    arduino_target = Arduino_test

    # collect the targets in a dictionary
    collectedTargets = {'name': name_target, 'positions': positions_target, 'noOfPositions': noOfPositions_target, 'relay': relay_target, 'arduino': arduino_target}

    # check handle

    # The handles cannot be compared
    # handle_result = Valve_test.handle
    name_result = Valve_test.name
    positions_result = Valve_test.positions
    noOfPositions_result = Valve_test.noOfPositions
    relay_result = Valve_test.relay
    arduino_result = Valve_test.Arduino

    # collect the results in a dictionary
    collectedResults = {'name': name_result, 'positions': positions_result, 'noOfPositions': noOfPositions_result, 'relay': relay_result, 'arduino': arduino_result}

    # ensure, that all the results match the targets
    for key in collectedResults.keys():
        assert collectedResults[key] == collectedTargets[key], f'The {key} is {collectedResults[key]} instead of {collectedTargets[key]}.'

def test_ArduinoValve_number_of_valve_positions():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])
    #instantiate the valve
    Valve_test = Arduino_driver.ArduinoValve(name=conf['ArduinoDriver']['ArduinoValve'][0]['name'], relay=Relay_test, Arduino=Arduino_test, positions=conf['ArduinoDriver']['ArduinoValve'][0]['positions'])

    # get the target value for the number of valve positions
    noOfValvePositions_target = conf['test_ArduinoDriver']['targets']['noOfValvePositions']['noOfValvePositions']

    # apply the function and ensure the result
    noOfValvePositions_result = Valve_test.number_of_valve_positions()
    assert noOfValvePositions_result == noOfValvePositions_target, f'The number of valve positions is {noOfValvePositions_result} instead of {noOfValvePositions_target}.'

def test_ArduinoValve_actual_valve_position():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])
    #instantiate the valve
    Valve_test = Arduino_driver.ArduinoValve(name=conf['ArduinoDriver']['ArduinoValve'][0]['name'], relay=Relay_test, Arduino=Arduino_test, positions=conf['ArduinoDriver']['ArduinoValve'][0]['positions'])

    # Open the serial communication
    Arduino_test.connect()

    # get the target value
    valvePosition_target = int(Arduino_test.port.readline().decode('ascii'))

    # apply the function and ensure the result
    valvePosition_result = Valve_test.actual_valve_position()
    assert valvePosition_result == valvePosition_target, f'The valve position is {valvePosition_result} instead of {valvePosition_target}.'

    ## close the serial communication
    Arduino_test.port.close()


def test_ArduinoValve_switch_valve_to_position():
    # instantiate the Arduino
    Arduino_test = Arduino_driver.Arduino(name=conf["test_ArduinoDriver"]["inputs"]["nameArduino"], serialPort=conf['ArduinoDriver']['Arduino'][0]['serialPort'], settings=conf['ArduinoDriver']['Arduino'][0]['settings'], simulated=conf['ArduinoDriver']['Arduino'][0]['simulated'])
    # instatiate the relay
    Relay_test = Arduino_driver.ArduinoRelay(Arduino=Arduino_test, relayNo=conf['ArduinoDriver']['ArduinoRelay'][0]['relayNo'], name=conf['test_ArduinoDriver']['inputs']['nameRelay'])
    #instantiate the valve
    Valve_test = Arduino_driver.ArduinoValve(name=conf['ArduinoDriver']['ArduinoValve'][0]['name'], relay=Relay_test, Arduino=Arduino_test, positions=conf['ArduinoDriver']['ArduinoValve'][0]['positions'])
    
    # start the communication
    Arduino_test.connect()

    # get the position of the ArduinoValve before applying switch_valve_to_position
    positionBefore = Arduino_test.port.readline().decode('ascii')
    # get the target and required initial position from the configuration file
    position_target = conf['test_ArduinoDriver']['targets']['switchToPosition']['targetPosition']
    positionInitial = conf['test_ArduinoDriver']['inputs']['switchToPosition']['initPosition']

    # The test is only useful, if positionBefore is equal to the configured initial position and different from the target position
    if (int(positionBefore) == positionInitial) and (int(positionBefore) != position_target):
        # apply the function
        Valve_test.switch_valve_to_position(position_target)
        # check the actual position of the valve after switching it
        position_result = Valve_test.actual_valve_position()
        assert position_result == position_target, f'The position is {position_result} instead of {position_target}.'
    # If the valve is in the wrong start position, the test shall fail with a respective message.
    else:
        assert True == False, f'The inital position of the valve is {positionBefore}, but position {positionInitial} is needed.'

    ## close the serial communication
    Arduino_test.port.close()
