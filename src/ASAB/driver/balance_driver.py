from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

## Imports from ASAB
from ASAB.utility.helpers import typeCheck

## Other imports
import serial  # https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.in_waiting
import time
import numpy as np

class balance:
    ''' This class provides basic functionalities required to work with a balance connected to a COM port. '''
    def __init__(self, serialPort:str=conf["balanceDriver"]["serialPort"], settings:dict=conf["balanceDriver"]["settings"], simulated:bool=conf["balanceDriver"]["simulated"]) -> None:
        ''' This function initiates an instance of the balance class.
        Inputs:
        serialPort: a string representing the name of the COM port, to which the balance is connected
        settings: a dictionary representing the settings to apply for the serial communication
        simulated: a boolean to indicate, whether the balance shall be simulated (True) or not (False)

        Outputs:
        This function has no outputs. '''
        
        ## Check the input types
        typeCheck(func=balance.__init__, locals=locals())

        # If the balance shall be simulated, set the port to be an emulated port. Else set it as a serial object to work with the actual COM port
        if simulated:
            self.port = emulatedPort()
            self.port.port = serialPort
            self.port.apply_settings(settings)
            self.simulated = simulated
        else:
            self.port = serial.Serial()
            self.port.port = serialPort
            self.port.apply_settings(settings)
            self.simulated = simulated

    def readBalance(self) -> float:
        ''' This function reads the balance and returns the mass as read from the COM port. It ignores the unit, but accounts for the sign.
        Inputs:
        This function takes no inputs.
        
        Outputs:
        mass: a float representing the sign and value of the mass read from the balance. '''
        # Open the port
        self.port.open()
        # Sleep, while there is an insufficient number of bytes to read.
        while self.port.in_waiting<22:
            time.sleep(0.001)
        # Read a full line of the data
        mass = self.port.readline()
        # Decode it using ASCII
        mass = mass.decode("ASCII")
        # Get the sign of the balance reading
        sign = mass[6]
        # Get the value of the balance reading
        value = mass[7:16]
        # Remove spaces to the left of the value
        value = value.lstrip()
        # Combine the sign and the value and make it a float
        signedValue = sign + value
        mass = float(signedValue)
        # Close the port
        self.port.close()
        return mass

class emulatedPort():
    ''' This class allows for the emulation of a serial port for a balance. '''
    def __init__(self) -> None:
        ''' This function initializes an instance of an emulated serial port providing the functionalities to simulate a balance.
        Inputs:
        This function takes no inputs.

        Outputs:
        This function has no outputs. '''

        self.is_open = False
        self.port =""
        self.in_waiting = 22
        self.target = 0.0
        self.settings = {'baudrate': 9600, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': None, 'write_timeout': None, 'inter_byte_timeout': None}
        # The counter i is used to get an increasing balance read for the simulated balance as it speeds up the process for simulated balances
        self.i = 0

    def open(self) -> None:
        ''' This function opens the emulated port by setting its is_open attribute to True.
        Inputs:
        This function takes no inputs.
        
        Outputs:
        This function has no outputs. '''

        self.is_open = True

    def readline(self) -> bytes:
        ''' This function reads a line from the emulated port. This function returns a numerical value formatted as a balance reading and ascii encoded.
        Inputs:
        This function takes no inputs.
        
        Outputs:
        ret: a bytes object, which contains a balance reading in the unit g and formatted according to the readings of the balance encoded as ascii '''

        gener = np.random.default_rng()
        # Generate list of increasing balance reads
        listreads = [-0.2568 + 0.003*x for x in range(200)]
        # Generate an arbitrary read
        read = listreads[self.i] + gener.choice(np.linspace(start=-1., stop=1.5, num=np.random.randint(low=30, high=70)))    # https://numpy.org/devdocs/reference/random/generated/numpy.random.choice.html, https://numpy.org/devdocs/reference/random/generated/numpy.random.randint.html
        # Get the sign of the read
        if read < 0.0:
            sign = "-"
        else:
            sign = " "
        # Round the read to four decimal digits
        read = np.round(a=read, decimals=4) # https://numpy.org/doc/stable/reference/generated/numpy.round_.html
        # Save the reference value for testing correct processing
        self.target=read
        # Get the absolute value of the reading
        read = np.absolute(read)
        # Format the read value as a 9 characters long string with leading spaces and four decimal digits.
        read = format(read, " 9.4f")    # https://www.pythoncontent.com/understanding-__format__-in-python/
        # Assemble the output string
        ret = f"G     {sign}{read} g    "
        # Progress the balance read counter by 1
        self.i += 1
        # Return an ASCII encoded result
        return ret.encode("ASCII") # https://docs.python.org/3/howto/unicode.html#encodings

    def close(self) -> None:
        ''' This function closes the emulated port by setting its is_open attribute to False.
        Inputs:
        This function takes no inputs.
        
        Outputs:
        This function has no outputs. '''

        self.is_open = False

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
