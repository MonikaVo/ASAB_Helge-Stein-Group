from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

from ASAB.configuration import config
cf = config.configASAB

## Imports from ASAB
from ASAB.utility.syringes import loadSyringeDict, Syringe
from ASAB.utility.helpers import loadVariable, saveToFile, typeCheck
from ASAB.utility import loggingASAB

# Imports from QmixSDK
import sys
sys.path.append(cf["QmixSDK_python"])
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk import qmixcontroller

# Other imports
import string # https://www.delftstack.com/howto/python/python-alphabet-list/
from typing import Union, List
import logging

# create a logger for this module
logger_CetoniDevice_driver = logging.getLogger(f"run_logger.{__name__}")

class valveObj(qmixvalve.Valve):
    ''' This class provides the functionalities of a valve as provided in the qmixsdk, but allows an extensioin e.g. adding
    a name attribute, This class is a child class to qmixValve.Valve and a grandchild class to qmixbus.Device. '''

    def __init__(self, valveType:str='', name:str='') -> None:
        ''' This function initialises a valve object.
        
        Inputs:
        name: a string defining the name of the valve
        valveType: a string defining, whether this valve is a 'rotary' (for QmixV valves), a 'pump' (for the
        valves mounted on pump modules), 'pump_conti' (for nemesys_S contiflow valves) or an 'ArduinoValve' (for valves
        connected to an Adruino)
        
        Outputs:
        This function has no outputs. '''

        ## Check the input types
        typeCheck(func=valveObj.__init__, locals=locals())

        super().__init__()
        self.name = name
        self.valveType = valveType

    def open(self) -> None:
        ''' This function puts a valve corresponding to a pump module to the "open" position. This position is available for nemesys_S
        contiflow valves. If the valve does not offer the respective position, a message is printed. A message is also printed, if the
        valve does not correspond to a pump module.
        
        Inputs:
        This function has no inputs.
        
        Outputs:
        This function has no outputs. '''

        # check, if the type of the valve corresponds to the one related to the nemesys_S contiflow valves, is a sufficient number of
        # valve positions is available and the valve is not a QmixV valve
        if (self.type == 'pumpValve_conti') and (self.number_of_valve_positions() > 3) and ('QmixV' not in self.get_device_name()):
            # try to switch the valve to position 3
            try:
                self.switch_valve_to_position(3)
            except: # -> This part is not yet tested.
                # If the valve does not have a position 3, raise an error
                raise AttributeError(f"The valve {self.name} does not offer an 'open' position. Maybe it's type is wrong.")
        else:
            # If the valve is of the wrong type, raise an error
            raise AttributeError(f"The valve {self.name} does not offer an 'open' position as it is a {self.type}.")

    def close(self) -> None:
        ''' This function puts a valve corresponding to a pump module to the "close" position. This position is available for nemesys_S
        contiflow valves. If the valve does not offer the respective position, a message is printed. A message is also printed, if the
        valve does not correspond to a pump module.
        
        Inputs:
        This function has no inputs.
        
        Outputs:
        This function has no outputs. '''

        # check, if the type of the valve corresponds to the one related to the nemesys_S contiflow valves, is a sufficient number of
        # valve positions is available and the valve is not a QmixV valve
        if (self.type == 'pumpValve_conti') and (self.number_of_valve_positions() > 3) and ('QmixV' not in self.get_device_name()):
            self.switch_valve_to_position(0)
        else:
            # If the valve is of the wrong type, raise an error
            raise AttributeError(f"The valve {self.name} does not offer an 'open' position as it is a {self.type}.")

class pumpObj(qmixpump.Pump):
    ''' This class inherits from the qmixpump.Pump class in the QmixSDK. This class contains some additional methods for the
        pumps. It is a child class to qmixpump.Pump and a grandchild class to qmixbus.Device. '''

    def __init__(self, name:str = '', pumpType:str = '') -> None:
        ''' This function initialises a pump object. It assigns the given name, an 'empty' status and a syringe to the pump
            object.
            
            Inputs:
            name: a string defining the name of the pump
            pumpType: a string defining the type of the pump as 'pump' (for neMESYS_Low_Pressure pumps) or 'pump_conti' (for Nemesys_S pumps)
                      This is adjusted to the valveTypes for easier checking.

            Outputs:
            This function has no outputs. '''

        ## Check the input types
        typeCheck(func=pumpObj.__init__, locals=locals())

        super().__init__()
        self.name = name
        self.status = "empty"
        # This attribute holds an object of the type "syringe", which contains the information regarding the syringe mounted
        # on the pump module corresponding to the pump object
        self.syringe = Syringe(desig="init", inner_dia_mm=0.0, piston_stroke_mm=0.0)
        self.pumpType = pumpType

def loadValvePositionDict(path_to_ValvePositionDict:str) -> dict:
    ''' This function loads a valvePositionDict from a .txt file and returns it as a dictionary. The valvePositionDict has
    the valve names as keys. Each of these keys has a dictionary as its value, which has the labels for each position in the
    format [valve label] = [valve name].[position] as keys and the numerical value from 0 to number_of_valve_positions-1 as
    values.
    
    Inputs:
    path_to_ValvePositionDict: a string defining the path from where the valvePositionDict shall be loaded

    Outputs:
    This function has no outputs. '''
    
    ## Check the input types
    typeCheck(func=loadValvePositionDict, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    # Load the valvePositionDict and return it
    vPd = loadVariable(loadPath=path_to_ValvePositionDict, variable='vPd')
    return vPd

def getValvePositionDict(vPd:Union[str,dict]) -> dict:
    ''' This funciton checks the type of vPd and loads a vPd dictionary, if vPd is given as a path to the vPd .py-file.
    
    Inputs:
    vPd: either a dictionary, which is a valvePositionDict, or a string specifying a path to the file, from which the valvePositionDict can be loaded.

    Outputs:
    valvePositionDict: a valvePositionDict in dictionary format '''

    ## Check the input types
    typeCheck(func=getValvePositionDict, locals=locals())


    # check the type of the valvePositionDict
    if isinstance(vPd, dict):
        # return the input, if it already is a dict
        valvePositionDict = vPd
    elif isinstance(vPd, str):
        if (Path(vPd).is_file()):
            # load the file and get the variable from there, if the input is a str
            valvePositionDict = loadValvePositionDict(path_to_ValvePositionDict=vPd)
        else:
            # raise a Value error, if the given string does not correspond to a path
            raise ValueError(f'The valvePositionDict given is {vPd} of type {type(vPd)}, which does not correspond to a path.')
    else:
        # raise a TypeError, if the type of the input is neither dict nor str
        raise TypeError(f'The valvePositionDict given is {vPd} of type {type(vPd)}, which is a type not supported by this function.')
    return valvePositionDict


# TODO:Add a class for channels

# Import this here to avoid error due to cyclic import
import ASAB.driver.Arduino_driver as AD

class cetoni:
    def __init__(self):
        pass
        
    def prepareCetoni(config_path:str=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path:str=cf["QmixSDK"], available_syringes:str=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config:dict=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_vPd:str=conf["CetoniDeviceDriver"]["valvePositionDict"]) -> dict:
        ''' This function sets the Cetoni setup operable. It takes the path for the relevant configuration file and the path to the QmixSDK module
        as inputs, prints the detected setup, configures the syringes and returns one dict containing the pumps ("Pumps"), one containing the valves ("Valves") and one containing all the channels ("Channels").
        
        Inputs:
        config_path: a string specifying the path, where to find the configuration needed to start the Cetoni device
        QmixSDK_path: a string specifying the path, where to find the QmixSDK toolkit
        available_syringes: a string specifying the path to a file containing a dictionary of syringe sizes and their parameters
        syringe_config: a dictionary specifying the designations of pump modules as keys and the corresponding name of the syringes as values
        save_name_vPd: a string specifying the path, where the valvePositionDict shall be saved
        
        Outputs:
        Pumps: a dictionary of pump objects (pumpObj) representing the pumps in the detected setup
        Valves: a dictionary of valve objects (valceObj) representing the valves in the detected setup
        Channels: a dictionary of channel objects (qmixcontroller.ControllerChannel()) representing the channels in the detected setup '''
        
        ## Check the input types
        typeCheck(func=cetoni.prepareCetoni, locals=locals())

        # Load the available syringes making the entries in the dict into syringe objects
        syr = loadSyringeDict(path_to_syringeDict=available_syringes)
        syringes_dict = syringe_config.copy()
        # Go through all entries in syringe_dict and get the designation of the syringe on each pump and assign the 
        # corresponding syringe object from syr to the respective key in the syringe_dict
        for pump in syringes_dict.keys():
            syringes_dict[pump] = syr[syringe_config[pump]]
        
        '''----------------Preparation start----------------'''
        # Create a list of the uppercase Alphabet to label pumps and valves
        alphabet = list(string.ascii_uppercase)

        # Open bus library
        qmixbus.Bus.open(config_path, QmixSDK_path)
        logger_CetoniDevice_driver.info(f"{cetoni.prepareCetoni.__name__}\nBus communication opened with \n"
                                        f"Cetoni configuration path: {config_path}\n"
                                        f"QmixSDK path: {QmixSDK_path}")

        # Get info about the numbers of accessible elements and retrieve handles and print overview
        print("\n\n--------------Detected Setup--------------\n\n")

        ## Pumps

        # Get number of pump modules
        noOfPumps = qmixpump.Pump.get_no_of_pumps()
        print("\n The number of pumps is {} with the names, lables, and types:\n".format(noOfPumps))
        logmsg = [f"The number of pumps is {noOfPumps} with the names, lables, and types:"]
        # Retrieve device handles for pump modules and save pumps in Pumps
        Pumps = {}
        for p in range(noOfPumps):
            # Initialise the pump object
            Pump = pumpObj()
            # Get the handle for the pump object
            Pump.lookup_by_device_index(p)
            # Assign a shorter name to the pump
            Pump_designation = "{}0.0".format(alphabet[p])
            Pump.name = Pump_designation
            # Assign a type to the pump depending on its device name
            if ('nemesys_low_pressure' in Pump.get_device_name().lower()):
                Pump.pumpType = 'pump'
            elif ('nemesys_s' in Pump.get_device_name().lower()):
                Pump.pumpType = 'pump_conti'
            # Add the pump to the dictionary of pumps
            Pumps[Pump_designation] = Pump
            print(Pump.get_device_name(), Pump.name, Pump.pumpType)
            logmsg.append(f"Device name:\t{Pump.get_device_name()}, pump name:\t{Pump.name}, pump type:\t{Pump.pumpType}")

        ## Valves

        # Initialize a valvePositionDict, correlating the valve position taken by the Cetoni API to the label of the respective node in the graph.
        valvePositionDict = {}
        # Get number of valves (QmixV elements PLUS valves for syringe pumps)
        noOfValves = qmixvalve.Valve.get_no_of_valves()
        print("\n The number of valves is {} with the names, labels, types and number of valve positions:\n".format(noOfValves))
        logmsg.append(f"\nThe number of valves is {noOfValves} with the names, labels, types and number of valve positions:")
        # Retrieve device handles for valves and save valves in Valves
        Valves = {}
        for v in range(noOfValves):
            # Initialise the valve object
            Valve = valveObj()
            # Get a handle for the valve
            Valve.lookup_by_device_index(v)
            # Assign a shorter name to the valve, names differ between Qmix valve valves and pump valves
            if Valve.get_device_name().__contains__("QmixV"):
                # Get the number of the valve to assign it correctly to the new designation
                valveNumber = Valve.get_device_name().split('_')[1]
                # Generate the valve designation
                Valve_designation = "V{}".format(int(valveNumber))
                # Assign the designation to the name of the valve
                Valve.name = Valve_designation
                # Define the valve type
                Valve.valveType = 'rotary'
                # Add the valve to the valves dictionary
                Valves[Valve_designation] = Valve
                # Add an entry for the respective valve to the valvePositionDict
                valvePositionDict[Valve_designation] = {}
                # Go through the number of valve positions for a QmixV valve, which is 10
                for i in range(1,Valve.number_of_valve_positions()+1):    #0,11): Changed to make the code more flexible regarding valves.
                    # Assemble the key for the respective port of the valve
                    key = f"{Valve_designation}.{i}"
                    # Generate an entry for the port of the valve, which is 1 below i in order to get the index of the position for the API.
                    # If i = 0, assign None, because all ports are connected to port 0 and port 0 does not have a valve position. Port zero is needed in the valvePositionDict for getValveFromName() in graph.
                    valvePositionDict[Valve_designation][key] = i-1 if i != 0 else None
            elif Valve.get_device_name().lower().__contains__("nemesys_"):
                # Get the type of nemesys valve it is
                if (Valve.get_device_name().lower().__contains__('_low_pressure')):
                    Valve.valveType = 'pump'
                elif (Valve.get_device_name().lower().__contains__('_s')):
                    Valve.valveType = 'pump_conti'
                # Go through the pumps
                for p in Pumps.keys():
                    # Get the Cetoni definition of the pump
                    pump_label = '_'.join(Pumps[p].get_device_name().lower().split('_')[:-1])
                    # Assign the name by linking it to the name of the pump. Therefore, find the letter for the pump in the list "Pump_desig"
                    if (pump_label in Valve.get_device_name().lower()):
                        # Check, if the pump has the same label as the valve
                        Valve_designation = "{}v".format(Pumps[p].name[0])
                        # Set the designation as the name of the valve
                        Valve.name = Valve_designation
                        # Generate an entry for the respective valve in the valvePositionDict
                        valvePositionDict[Valve_designation] = {}
                        # The valves on pump modules have two positions related to a port. Iterate over these. Further positions of these valves
                        # do not correspond to a port.
                        for z in [0,1]:
                            # Assemble the key for the respective port of the valve
                            key2 = f"{Valve_designation}.{z}"
                            if Valve.valveType=="pump":
                                # Generate an entry for the port of the valve, which is 1 for designation 1 and 0 for deignation 0.
                                valvePositionDict[Valve_designation][key2] = z
                            elif Valve.valveType=='pump_conti':
                                # Generate an entry for the port of the valve, which is 1 for designation 1 and 0 for deignation 0.
                                valvePositionDict[Valve_designation][key2] = z+1
                Valves[Valve_designation] = Valve
            else:
                # Print an info, if the valve is neither a QmixV valve nor a pump valve
                raise ValueError("An error occured. Unknown Type of valve.")
            print(Valve.get_device_name(), Valve.name, Valve.valveType, Valve.number_of_valve_positions())
            logmsg.append(f"Device name:\t{Valve.get_device_name()}, "
                          f"valve name:\t{Valve.name}, valve type:\t{Valve.valveType},"
                          f"number of valve positions:\t{Valve.number_of_valve_positions()}")

        ## Arduino Valves

        # Collect all the Arduino boards and relays in a dictionary each
        ArduinoDict = {}
        RelayDict = {}

        # If there are any Arduino elements defined in the configuration
        if conf["ArduinoDriver"] != {}:
            # If there are Arduino boards defined
            if ("Arduino" in conf["ArduinoDriver"].keys()) and (conf["ArduinoDriver"]["Arduino"] != []):
                # Instantiate all the Arduinos contained in the configuration
                for Arduino_dict in conf["ArduinoDriver"]["Arduino"]:
                    Arduino_designation = f"Ard_{Arduino_dict['ArduinoNo']}"
                    Arduino = AD.Arduino(name=Arduino_designation, number=Arduino_dict["ArduinoNo"], serialPort=Arduino_dict["serialPort"], settings=Arduino_dict["settings"], simulated=Arduino_dict["simulated"])
                    Arduino.connect()
                    ArduinoDict[Arduino_designation] = Arduino

            # If there are Arduino relays defined
            if ("ArduinoRelay" in conf["ArduinoDriver"].keys()) and (conf["ArduinoDriver"]["ArduinoRelay"] != []):
                # Instantiate all the Arduino relays contained in the configuration
                for relay_dict in conf["ArduinoDriver"]["ArduinoRelay"]:
                    relay_designation = f"Ard_{relay_dict['ArduinoNo']}_Relay_{relay_dict['relayNo']}"
                    RelayDict[relay_designation] = AD.ArduinoRelay(Arduino=ArduinoDict[f"Ard_{relay_dict['ArduinoNo']}"], relayNo=relay_dict['relayNo'], name=relay_designation)
                    
            # If there are Arduino valves defined
            if ("ArduinoValve" in conf["ArduinoDriver"].keys()) and (conf["ArduinoDriver"]["ArduinoValve"] != []):
                # Instantiate all the Arduino valves contained in the configuration
                for av_dict in conf["ArduinoDriver"]["ArduinoValve"]:
                    ArduinoValve_designation = f"ArdV_{av_dict['ArduinoNo']}_{av_dict['relayNo']}"
                    Valve = AD.ArduinoValve(name=ArduinoValve_designation, relay=RelayDict[f"Ard_{av_dict['ArduinoNo']}_Relay_{av_dict['relayNo']}"], Arduino=ArduinoDict[f"Ard_{av_dict['ArduinoNo']}"], positions=av_dict["positions"])
                    Valve.valveType = "ArduinoValve"
                    Valves[ArduinoValve_designation] = Valve
                    
                    ## Create an entry in the valvePositionDict
                    valvePositionDict[ArduinoValve_designation] = {}
                    # Go through the number of valve positions for the Arduino valve
                    for i in range(Valve.number_of_valve_positions()):
                        # Assemble the key for the respective port of the valve
                        key3 = f"{ArduinoValve_designation}.{i}"
                        valvePositionDict[ArduinoValve_designation][key3] = i

                    print(Valve.get_device_name(), Valve.name, Valve.valveType, Valve.number_of_valve_positions())
                    logmsg.append(f"Device name:\t{Valve.get_device_name()}, "
                                  f"valve name:\t{Valve.name}, valve type:\t{Valve.valveType},"
                                  f"number of valve positions:\t{Valve.number_of_valve_positions()}")

        ## Channels

        # Get number of control channels
        noOfControllerChannels = qmixcontroller.ControllerChannel.get_no_of_channels()
        print("\n The number of control channels is {} with the names and labels:\n".format(noOfControllerChannels))
        logmsg.append(f"\nThe number of control channels is {noOfControllerChannels} with the names and labels:")
        # Retrieve device handles for valves and save valves in Valves
        Channels = {}
        for c in range(noOfControllerChannels):
            # Initialise controller channel
            Channel = qmixcontroller.ControllerChannel()
            # Get a handle
            Channel.lookup_channel_by_index(c)
            # Assign a shorter name
            Channel_designation = Channel.get_name().replace("QmixQminus_", "QQ-_")
            Channel_designation = Channel_designation. replace("QmixQplus_Column", "QQ+_col")
            Channel_designation = Channel_designation.replace("Temperature", "temp")
            Channel_designation = Channel_designation.replace("ReactionLoop", "loop")
            Channel_designation = Channel_designation.replace("ReactorZone", "zone")
            Channels[Channel_designation] = Channel
            print(Channel.get_name(), Channel_designation)
            logmsg.append(f"Channel name:\t{Channel.get_name()}, channel label:\t{Channel_designation}")
        logmsg = "\n".join(logmsg)
        logger_CetoniDevice_driver.info(msg=f"{cetoni.prepareCetoni.__name__}\n{logmsg}")

        print("\n\n--------------Detected Setup--------------\n\n")
            
        # Setting devices operational

        qmixbus.Bus.start()
        logger_CetoniDevice_driver.info(f"{cetoni.prepareCetoni.__name__}\nBus communication started.")


        # Configuring syringes
        for pump in Pumps.keys():
            Pumps[pump].syringe = syringes_dict[pump]
            Pumps[pump].set_syringe_param(inner_diameter_mm= syringes_dict[pump].inner_dia_mm, max_piston_stroke_mm= syringes_dict[pump].piston_stroke_mm)
            # Set the units for volume and flow
            Pumps[pump].set_volume_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres)
            Pumps[pump].set_flow_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres, qmixpump.TimeUnit.per_second)
            # Check, if pump is in fault state and clear the error, if required
            if Pumps[pump].is_in_fault_state():
                Pumps[pump].clear_fault()
            # Enable the pump, if it is not in fault state and is not yet enabled
            if Pumps[pump].is_in_fault_state() == False and Pumps[pump].is_enabled() == False:
                Pumps[pump].enable(True)
            elif Pumps[pump].is_in_fault_state() == False and Pumps[pump].is_enabled() == True:
                pass
            else:
                # If none of the above two cases apply, print a message
                raise ValueError("There is an error. Pump {} is enabled: {}, is in fault state {}.".format(pump, Pumps[pump].is_enabled(), Pumps[pump].is_in_fault_state()))

        # Initialise the valve positions to 0
        for valve in Valves.keys():
            v = Valves[valve]
            if not (v.valveType == 'pump_conti'):
                Valves[valve].switch_valve_to_position(0)
            else:
                Valves[valve].switch_valve_to_position(1)
        '''----------------Preparation end----------------'''
        # Save the valvePositionDict to the path specified by save_name.
        saveToFile(folder='\\'.join(save_name_vPd.split('\\')[:-1]), filename=save_name_vPd.split('\\')[-1].split('.')[0], extension=save_name_vPd.split('\\')[-1].split('.')[1], data=f"vPd = {str(valvePositionDict)}")
        logger_CetoniDevice_driver.info(f"{cetoni.prepareCetoni.__name__}\nvalvePositionDict saved to {save_name_vPd}")
        return Pumps, Valves, Channels

    def quitCetoni() -> None:
        ''' This function quits the operation of the Cetoni device. It stops the BUS communication and closes the BUS. 
        
        Inputs:
        This function takes no inputs.
        
        Outputs:
        This function has no outputs. '''

        '''----------------Finishing start----------------'''
        # Setting devices pre operational
        qmixbus.Bus.stop()
        # Close bus library
        qmixbus.Bus.close()
        print("Communication with Cetoni device ended.")
        logger_CetoniDevice_driver.info(f"{cetoni.quitCetoni.__name__}\nCommunication with Cetoni device ended.")
        '''----------------Finishing end----------------'''

    def getValvePositions(valvesDict:dict, valvePositionDict:Union[str, dict]=conf["CetoniDeviceDriver"]["valvePositionDict"]) -> dict:
        ''' This function returns the positions of all valves in the system in a dictionary. The designations of the valves are the keys.
        It takes the dicts of valves and the path to the valvePositionDict as inputs.
        
        Inputs:
        valvesDict: a dictionary containing valve names as keys and valves as values
        valvePositionDict: a dictionary or a string of a path to the valvePositionDict containing all the positions of each valve with the
                           node name as keys and the numeric valve position as the values
        
        Outputs:
        valvePos: a dictionary containing the names of the valves as keys and the current position of the respective valve as values '''

        ## Check the input types
        typeCheck(func=cetoni.getValvePositions, locals=locals())   # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

        valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
        valvePos = {}
        for valve in valvePositionDict.keys():
            # Write the current valve position for each valve in the dict "valvePos"
            valvePos[valve] = valvesDict[valve].actual_valve_position()
        return valvePos

    def pumpingPumps(pumpsDict:dict) -> List[str]:
        ''' This function returns a list of pumps, which are currently pumping.
        Inputs:
        pumpsDict: a dictionary containing the names of the pumps as keys and the pump objects present in the setup as values
        
        Outputs:
        pumping: a list of names of pumps, which are currently pumping; meaning their .is_pumping() function returns True '''

        ## Check the input types
        typeCheck(func=cetoni.pumpingPumps, locals=locals())    # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

        # initialise an empty list to populate later
        pumping = []
        # go through all the pumps in the pumpsDict
        for p in pumpsDict.keys():
            # if the pump is pumping, append it to the list
            if pumpsDict[p].is_pumping():
                pumping.append(p)
        return pumping