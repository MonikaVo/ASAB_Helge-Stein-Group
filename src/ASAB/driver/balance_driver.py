## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    # if the import was not successful, go to default config
    from ASAB.configuration import default_config
    conf = default_config.config

## Other imports
import serial  # https://pyserial.readthedocs.io/en/latest/pyserial_api.html#serial.Serial.in_waiting
import time
import numpy as np

class balance:
    ''' This class provides basic functionalities required to work with a balance. '''
    def __init__(self, serialPort=conf["balanceDriver"]["serialPort"], settings=conf["balanceDriver"]["settings"], simulated=conf["balanceDriver"]["simulated"]):
        # If the balance shall be simulated, set the port to be an emulated port. Else set it as a serial object to work with the actual COM port
        if simulated:
            self.port = emulatedPort()
        else:
            self.port = serial.Serial()
            self.port.port = serialPort
            self.port.apply_settings(settings)

    def readBalance(self):
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
    def __init__(self):
        self.is_open = False
        self.port ="Test"
        self.in_waiting = 22
        self.target = 0.0

    def open(self):
        self.is_open = True

    def readline(self):
        gener = np.random.default_rng()
        # Generate an arbitrary read
        read = gener.choice(np.linspace(start=-10.0, stop=15.0, num=np.random.randint(low=30, high=70)))    # https://numpy.org/devdocs/reference/random/generated/numpy.random.choice.html, https://numpy.org/devdocs/reference/random/generated/numpy.random.randint.html
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
        # Return an ASCII encoded result
        return ret.encode("ASCII") # https://docs.python.org/3/howto/unicode.html#encodings

    def close(self):
        pass
