## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    # if the import was not successful, go to default config
    from ASAB.configuration import default_config
    conf = default_config.config

from ASAB.configuration import config
cf = config.configASAB

## Imports from ASAB
from ASAB.utility.syringes import loadSyringeDict, syringe
from ASAB.utility.helpers import saveToFile

# Import from QmixSDK
import sys
sys.path.append(cf["QmixSDK_python"])
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk import qmixcontroller

# Other imports
import string # https://www.delftstack.com/howto/python/python-alphabet-list/
from typing import Union

class valveObj(qmixvalve.Valve):
    def __init__(self):
        super().__init__()
        self.name = ""

    def open(self):
        # TODO: Test this function
        ''' This function puts a valve corresponding to a pump module to the "open" position. This position is available for nemesys_S
        contiflow valves. If the valve does not offer the respective position, a mesage is printed. A message is also printed, if the
        valve does not correspond to a pump module.'''
        if "." not in self.name:
            try:
                self.switch_valve_to_position(2)
            except:
                print("This valve does not offer an 'open' position.")
        else:
            print("This valve is not corresponding to a pump module.")

    def close(self):
        # TODO: Test this function
        ''' This function puts a valve corresponding to a pump module to the "closed" position. This position is available for nemesys_S
        contiflow valves. If the valve does not offer the respective position, a mesage is printed. A message is also printed, if the
        valve does not correspond to a pump module.'''
        if "." not in self.name:
            try:
                self.switch_valve_to_position(3)
            except:
                print("This valve does not offer an 'closed' position.")
        else:
            print("This valve is not corresponding to a pump module.")

class pumpObj(qmixpump.Pump):
    ''' This class inherits from the qmixpump.Pump class in the QmixSDK. This class contains some additional methods for the pumps. It is a child class to qmixpump.Pump and a grandchild class to
        qmixbus.Device. '''
    def __init__(self):
        super().__init__()
        self.name = ""
        self.status = "empty"
        # This attribute holds an object of the type "syringe", which contains the information regarding the syringe mounted on the pump module corresponding to the pump object
        self.syringe = syringe(desig="init", inner_dia_mm=0.0, piston_stroke_mm=0.0)

# TODO: Test this function
def loadValvePositionDict(path_to_ValvePositionDict:str):
    # Open and read the file containing the data
    with open(path_to_ValvePositionDict, "r") as file:
        rawString = file.readlines()[0]
    # Make the rawString string to a dict
    vPd = eval(rawString)
    return vPd

# TODO: Test this function
def getValvePositionDict(vPd:Union[str,dict]):
    ''' This funciton checks the type of vPd and loads a vPd dictionary, if vPd is not yet a dictionary. '''
    # check valvePositionDict
    if isinstance(vPd, dict):
        valvePositionDict = vPd
    elif isinstance(vPd, str):
        valvePositionDict = loadValvePositionDict(vPd)
    else:
        raise ValueError(f'Incorrect type of {vPd} {type(vPd)} instead of str or dict.')
    return valvePositionDict

class cetoni:
    def __init__(self):
        pass
        
    def prepareCetoni(config_path:str=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path:str=cf["QmixSDK"], available_syringes:str=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config:dict=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"], save_name_pumps=conf["CetoniDeviceDriver"]["pumps"], save_name_valves=conf["CetoniDeviceDriver"]["valves"], save_name_channels=conf["CetoniDeviceDriver"]["channels"]):
        ''' This function sets the Cetoni setup operable. It takes the path for the relevant configuration file and the path to the QmixSDK module
        as inputs, prints the detected setup, configures the syringes and returns one dict containing the pumps ("Pumps") and one containing the valves ("Valves"). '''
        
        # Load the available syringes
        syr = loadSyringeDict(available_syringes)
        syringes_dict = syringe_config.copy()
        # Go through all entries in syringe_dict and get the designation of the syringe on each pump and assign the corresponding syringe object from syr to the respective key in the syringe_dict
        for pump in syringes_dict.keys():
            syringes_dict[pump] = syr[syringe_config[pump]]
        
        '''----------------Preparation start----------------'''

        # Open bus library
        qmixbus.Bus.open(config_path, QmixSDK_path)

        # Get info about the numbers of accessible elements and retrieve handles and print overview
        print("\n\n--------------Detected Setup--------------\n\n")
        # Get number of pump modules
        noOfPumps = qmixpump.Pump.get_no_of_pumps()
        print("\n The number of pumps is {} with the names and lables:\n".format(noOfPumps))
        # Retrieve device handles for pump modules and save pumps in Pumps
        Pumps = {}
        Pump_desig = list(string.ascii_uppercase)
        for p in range(noOfPumps):
            # Initialise the pump object
            Pump = pumpObj()
            # Get the handle for the pump object
            Pump.lookup_by_device_index(p)
            # Assign a shorter name to the pump
            Pump_designation = "{}0.0".format(Pump_desig[p])
            Pump.name = Pump_designation
            # Add the pump to the dictionary of pumps
            Pumps[Pump_designation] = Pump
            print(Pump.get_device_name(), Pump_designation)

        # Initialize a valvePositionDict, correlating the valve position taken by the Cetoni API to the label of the respective node in the graph.
        valvePositionDict = {}
        # Get number of valves (QmixV elements PLUS valves for syringe pumps)
        noOfValves = qmixvalve.Valve.get_no_of_valves()
        print("\n The number of valves is {} with the names and labels:\n".format(noOfValves))
        # Retrieve device handles for valves and save valves in Valves
        Valves = {}
        for v in range(noOfValves):
            # Initialise the valve object
            Valve = valveObj()
            # Get a handle for the valve
            Valve.lookup_by_device_index(v)
            # Assign a shorter name to the valve, names differ between Qmix valve valves and pump valves
            if Valve.get_device_name().__contains__("QmixV"):
                Valve_designation = "V{}".format(int(v)+1)
                # Add the valve to the valves dictionary
                Valves[Valve_designation] = Valve
                # Add an entry for the respective valve to the valvePositionDict
                valvePositionDict[Valve_designation] = {}
                # Go through the number of valve positions for a QmixV valve, which is 10
                for i in range(0,11):
                    # Assemble the key for the respective port of the valve
                    key = f"{Valve_designation}.{i}"
                    # Generate an entry for the port of the valve, which is 1 below i in order to get the index of the position for the API.
                    # If i = 0, assign None, because all ports are connected to port 0 and port 0 does not have a valve position. Port zero is needed in the valvePositionDict for getValveFromName() in graph.
                    valvePositionDict[Valve_designation][key] = i-1 if i != 0 else None
            elif Valve.get_device_name().lower().__contains__("nemesys_"):
                # Go through the number of pumps
                for i in range(len(Pump_desig)):
                    # Assign the name by linking it to the name of the pump. Therefore, find the letter for the pump in the list "Pump_desig"
                    if str(i+1) in Valve.get_device_name():
                        Valve_designation = "{}v".format(Pump_desig[i])
                        # Generate an entry for the respective valve in the valvePositionDict
                        valvePositionDict[Valve_designation] = {}
                        # The valves on pump modules have two positions related to a port. Iterate over these. Further positions of these valves do not correspond to a port.
                        for z in [0,1]:
                            # Assemble the key for the respective port of the valve
                            key2 = f"{Valve_designation}{z}"
                            # Generate an entry for the port of the valve, which is 1 for designation 1 and 0 for deignation 0.
                            valvePositionDict[Valve_designation][key2] = z
                Valves[Valve_designation] = Valve
            else:
                # Print an info, if the valve is neither a QmixV valve nor a pump valve
                print("An error occured. Unknown Type of valve.")
            Valve.name = Valve_designation
            print(Valve.get_device_name(), Valve_designation)

        # Get number of control channels
        noOfControllerChannels = qmixcontroller.ControllerChannel.get_no_of_channels()
        print("\n The number of control channels is {} with the names and labels:\n".format(noOfControllerChannels))
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
        print("\n\n--------------Detected Setup--------------\n\n")
            
        # Setting devices operational

        qmixbus.Bus.start()

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
                print("There is an error. Pump {} is enabled: {}, is in fault state {}.".format(pump, Pumps[pump].is_enabled(), Pumps[pump].is_in_fault_state()))
            #print(Pumps[pump].get_syringe_param(), Pumps[pump].get_flow_rate_max(), Pumps[pump].get_volume_max())        

        # Initialise the valve positions to 0
        for valve in Valves.keys():
            Valves[valve].switch_valve_to_position(0)
        '''----------------Preparation end----------------'''
        # Save the valvePositionDict to the path specified by save_name.
        saveToFile(savePath=save_name_VdP, data=str(valvePositionDict))
        return Pumps, Valves, Channels

    def quitCetoni():
        ''' This function quits the operation of the Cetoni device. It stops the BUS communication and closes the BUS. '''

        '''----------------Finishing start----------------'''
        # Setting devices pre operational
        qmixbus.Bus.stop()
        # Close bus library
        qmixbus.Bus.close()
        '''----------------Finishing end----------------'''

    def getValvePositions(valvesDict:dict, valvePositionDict:dict=loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"])):
        ''' This function returns the positions of all valves in the system in a dictionary. The designations of the valves are the keys. '''
        valvePos = {}
        for valve in valvePositionDict.keys():
            # Write the current valve position for each valve in the dict "valvePos"
            valvePos[valve] = valvesDict[valve].actual_valve_position()
        return valvePos

    def pumpingPumps(pumpsDict:dict):
        ''' This function returns a list of pumps, which are currently pumping.'''
        pumping = []
        for p in list(pumpsDict.keys()):
            if pumpsDict[p].is_pumping():
                pumping.append(p)
        return pumping