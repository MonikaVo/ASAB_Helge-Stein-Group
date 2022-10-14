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
from QmixSDK.lib.python.qmixsdk.qmixbus import DeviceError
from ASAB.utility.helpers import typeCheck
from ASAB.driver.CetoniDevice_driver import valveObj

## Other imports
import serial
import numpy as np
from ctypes import c_longlong

class emulatedPort():
    ''' This class allows for the emulation of a serial port for an Arduino including the following basic functionalities:
    open
    close
    readline
    write
    apply_settings
    get_settings '''

    def __init__(self) -> None:
        ''' This fucntion initalizes an object of the emulatedPort class. 
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        self.is_open = False
        self.port = ''
        self.message = '0'.encode('ascii')
        self.settings = {'baudrate': 9600, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': None, 'write_timeout': None, 'inter_byte_timeout': None}
        self.returnEmpty = False

    def open(self) -> None:
        ''' This function sets the self.is_open attribute to True, which simulates an open serial port.
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        self.is_open = True

    def close(self) -> None:
        ''' This function sets the self.is_open attribute to False, which simulates a closed serial port.
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        self.is_open = False

    def readline(self) -> None:
        ''' This function returns 0 or 1 depending on the message saved in self.message. If the self.returnEmpty parameter is
        True, it returns an empty string, which is valuable for testing.
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        # If self.returnEmpty is set to be True, an empty string is returned in any case. This is used for testing the behaviour
        # of functions when receiving an empty string.
        if self.returnEmpty:
            return ''.encode('ascii')
        # If self.returnEmpty is set to be False, the returned value may either be 1 or 0 depending on self.message.
        else:
            if '_1' in self.message.decode('ascii'):
                return '1'.encode('ascii')
            else:
                return '0'.encode('ascii')

    def write(self, message:str) -> None:
        ''' This function writes a message to self.message to simulate serial communication.
        Inputs:
        message: a string containing the message to write to self.message
        
        Outputs:
        This funciton has no outputs. '''

        # If the command is to read from the port, this function does nothing.
        if 'read' in message.decode('ascii'):
            pass
        # If the message does not contain a read instruction, it saves the message in self.message
        else:
            self.message = message
    
    def apply_settings(self, settings:dict) -> None:
        ''' This function simulates the apply_settings function of a serial port by replacing the standard settings in self.settings
        by the given settings.
        Inputs:
        settings: a dictionary containing the settings as values to strings naming the respective setting
        
        Outputs:
        This funciton has no outputs. '''

        # For each key in the new settings, replace the existing ones.
        for key in settings.keys():
            self.settings[key] = settings[key]
    
    def get_settings(self) -> None:
        ''' This function simulates the get_settings function of a serial port by returning self.settings.
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        return self.settings

class Arduino:
    ''' This class covers basic functionalities of the serial communication with an Arduino board. '''
    
    def __init__(self, name="", number=0, serialPort:str=conf["ArduinoDriver"]["Arduino"][0]["serialPort"], settings:dict=conf["ArduinoDriver"]["Arduino"][0]["settings"], simulated:bool=conf["ArduinoDriver"]["Arduino"][0]["simulated"]) -> None:
        ''' This function initializes an instance of the Arduino class to bind it to a serial port.
        Inputs:
        serialPort: a string specifying the COM port, to which the Arduino is connected
        settings: a dictionary specifying the settings of the serial port in the format {property: value}; properties can be e.g. baudrate, timeout,...
        simulated: a boolean variable to specify, whether the actual device or an emulating port shall be usd
        
        Outputs:
        This funciton has no outputs. '''
        
        # If the Arduino shall be simulated, use the emulatedPort class.
        if simulated:
            self.port = emulatedPort()

        # Otherwise use an actual serial port as specified in the serialPort variable
        else:
            self.port = serial.Serial()
        self.port.port = serialPort
        self.port.apply_settings(settings)
        self.simulated = simulated
        self.name = name
        self.number = number

    def connect(self) -> None:
        ''' This function opens the port and enables the communication.
        Inputs:
        This function requires no inputs.
        
        Outputs:
        This funciton has no outputs. '''
        
        self.port.open()
        if self.port.is_open:
            print(f'Communication with Arduino on port {self.port.port} is started.')

    def disconnect(self) -> None:
        ''' This function closes the port and stops the communication.
        Inputs:
        This function requires no inputs.
        
        Outputs:
        This funciton has no outputs. '''
        
        self.port.close()
        if not self.port.is_open:
            print(f'Communication with Arduino on port {self.port.port} is stopped.')

class ArduinoRelay:
    ''' This class provides the functionalities of an Arduino relay. It requires an object of the Arduino class to be instantiated
    as it uses the port of the Arduino object for communication. '''
    
    def __init__(self, Arduino:Arduino, relayNo:int, name:str="") -> None:
        ''' This function initializes an object of the ArduinoRelay class. It connects it with an Arduino object.
        Inputs:
        Arduino: an instance of the Arduino class
        relayNo: an integer between 1 and 4 specifying the relay, which shall be connected to this instance
        
        Outputs:
        This funciton has no outputs. '''
        
        self.port = Arduino.port
        self.relayNo = relayNo
        self.Arduino = Arduino
        self.name = name

    def setRelayState(self, state:int, relayNo:int=None) -> int:
        ''' This function sets the state of the relay. It can set it to either 1 or 0.
        Inputs:
        state: an integer describing the desired state of the relay, to which it shall be switched. It can take values of 0 for LOW or 1 for HIG.
        relayNo: an integer identifiying the relay to be controlled. The default is None, in which case the instance of the relay, through which this function is accessed, is switched.
        
        Outputs:
        actualState: an integer describing the actual state of the relay after performing the command; if no valid actualState is obtained from the serial port, 2 is returned. '''
        
        # If no other relay number is given, default to the one connected to the current instance of the ArduinoRelay class.
        if relayNo==None:
            relayNo = self.relayNo
        # Assemble the command to be written to the serial communication, containing the number of the relay and the desired state
        cmd = "{}_{}\n".format(str(relayNo),str(state))
        # Write the command to the communication port
        self.port.write(cmd.encode())
        # Read the response to get the actual state after the command
        actualState = self.port.readline().decode('ascii')
        # Print a message to the user to communicate the actual state of the relay
        print(f'Relay_{relayNo} is set to {actualState}.')
        # In the first communication after starting the communication, the message returned by the port is empty, which causes an error
        # in the conversion to an integer. Therefore, the actual state is only returned, if the string is not empty.
        if actualState != '':
            return int(actualState)
        # If the string in actualState is empty, return 2 to return an integer, but not a valid 0 or 1.
        else:
            return 2

    def getRelayState(self, relayNo:int=None) -> int:
        ''' This function gets the state of the relay.
        Inputs:
        relayNo: an integer identifiying the relay to be controlled. The default is None, in which case the instance of the relay, through which this function is accessed, is switched.
        
        Outputs:
        actualState: an integer describing the actual state of the relay after performing the command; if no valid actualState is obtained from the serial port, 2 is returned. '''
        
        # If no other relay number is given, default to the one connected to the current instance of the ArduinoRelay class.
        if relayNo==None:
            relayNo = self.relayNo
        # Assemble the command to be written to the serial communication, containing the number of the relay and the desired state
        cmd = "{}_read\n".format(str(relayNo))
        # Write the command to the communication port
        self.port.write(cmd.encode())
        # Read the response
        actualState = self.port.readline().decode('ascii')
        # Print a message to the user to communicate the actual state of the relay
        print(f'Relay_{relayNo} is at {actualState}.')
        # In the first communication after starting the communication, the message returned by the port is empty, which causes an error
        # in the conversion to an integer. Therefore, the actual state is only returned, if the string is not empty.
        if actualState != '':
            return int(actualState)
        # If the string in actualState is empty, return 2 to return an integer, but not a valid 0 or 1.
        else:
            return 2

class ArduinoValve(valveObj):
    ''' This class inherits from the valveObj class in the CetoniDevice driver and redefines the most important functions to 
    ensure, that the valve can be operated like the rotary valves in the Cetoni device. '''

    def __init__(self, name:str, relay:ArduinoRelay, Arduino:Arduino, positions:list=conf['ArduinoDriver']['ArduinoValve'][0]['positions']) -> None:   # TODO: FIX THE CONFIG! IT IS NOT USING THE RIGHT CONFIG HERE! DOES IT ELSEWHERE?
        ''' This function instantiates an object of the ArduinoValve class.
        Input:
        name: a string giving the name of the valve
        relay: an instance of the ArduinoRelay class connected to the relay, at which the valve is connected
        Arduino: an instance of the Arduino class connected to the relay shield, to which the valve is connected
        positions: a list giving the available positions of the valve as integers. 0 corresponds to the LOW / NO state of the relay, while 1 corresponds to the HIGH / NC state.
        
        Outputs:
        This funciton has no outputs. '''

        self.handle = c_longlong(123456)
        self.name = name
        self.positions = positions
        self.noOfPositions = len(positions)
        self.relay = relay
        self.Arduino = Arduino

    def number_of_valve_positions(self) -> None:
        ''' This function returns the number of valve positions for the instance used to call the function.
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        return self.noOfPositions

    def actual_valve_position(self) -> None:
        ''' This function returns the actual valve position for the instance used to call the function.
        Inputs:
        This function needs no inputs.
        
        Outputs:
        This funciton has no outputs. '''

        return self.relay.getRelayState()

    def switch_valve_to_position(self, valve_position:int) -> None:
        ''' This funciton switches the valve calling it to the position specified in valve_position.
        Inputs:
        valve_position: an integer describing the valve position to which the valve shall be switched. Valid inputs are 0 or 1.
        
        Outputs:
        This funciton has no outputs. '''

        # Set the state of the relay according to the desired position of the valve
        self.relay.setRelayState(valve_position)
        # Get the actual valve position after switsching the valve
        actual_pos = self.actual_valve_position()
        # Raise a ValueError, if the valve position after switching the valve does not correspond to the desired one.
        if actual_pos != valve_position:
            raise ValueError(f'The valve is not switched to the {valve_position} position, but is at {actual_pos}. Please check before continuing.') # TODO: Test this part of the function.

    def get_device_name(self):
        ''' This function ensures the compatibility of the Arduino valves with the QmixSDK. As this function as implemented
        in the QmixSDK does not work for non-Cetoni valves. '''

        return self.name
