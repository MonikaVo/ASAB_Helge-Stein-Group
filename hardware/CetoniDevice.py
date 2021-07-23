# Add Qmix SDK path to module search path in order to make sure Python finds SDK modules.
import sys

sys.path.append(r"...\QmixSDK\lib\python")  # edited prior to publication
sys.path.append(r"..")  # edited prior to publication

# Import qmixsdk modules
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk import qmixcontroller
from hardware import syringes
from helpers import LoadFile

syr = LoadFile(r"filesForOperation/hardware/syringes.pck")

# Import other modules
import time

def prepareCetoni(config_path=r"...\ASAB_Conf1", QmixSDK_path=r"...\QmixSDK", syringes_dict={"A0.0": syr["2_5_ml"], "B0.0": syr["2_5_ml"], "C0.0": syr["2_5_ml"], "D0.0": syr["2_5_ml"], "E0.0": syr["2_5_ml"], "F0.0": syr["2_5_ml"]}):  # edited prior to publication
    ''' This function sets the Cetoni setup operable. It takes the path for the relevant configuration file and the path to the QmixSDK module
    as inputs, prints the detected setup, configures the syringes and returns one dict containing the pumps ("Pumps") and one containing the valves ("Valves"). '''
    
    '''----------------Preparation start----------------'''

    # Open bus library
    qmixbus.Bus.open(config_path, QmixSDK_path)

    #setup_config()

    # Get info about the numbers of accessible elements and retrieve handles and print overview
    print("\n\n--------------Detected Setup--------------\n\n")
    # Get number of pump modules:
    noOfPumps = qmixpump.Pump.get_no_of_pumps()
    print("\n The number of pumps is {} with the names and lables:\n".format(noOfPumps))
    # Retrieve device handles for pump modules and save pumps in Pumps:
    Pumps = {}
    Pump_desig = ["A", "B", "C", "D", "E", "F"]
    for p in range(noOfPumps):
        Pump = qmixpump.Pump()
        Pump.lookup_by_device_index(p)
        # Assign designation shorter than name:
        Pump_designation = "{}0.0".format(Pump_desig[p])
        Pumps[Pump_designation] = Pump
        print(Pump.get_device_name(), Pump_designation)

    # Get number of valves (QmixV elements PLUS valves for syringe pumps):
    noOfValves = qmixvalve.Valve.get_no_of_valves()
    print("\n The number of valves is {} with the names and labels:\n".format(noOfValves))
    # Retrieve device handles for valves and save valves in Valves:
    Valves = {}
    QmixValvesCount = 0
    for v in range(noOfValves):
        Valve = qmixvalve.Valve()
        Valve.lookup_by_device_index(v)
        # Define designation shorter than name:
        if Valve.get_device_name().__contains__("QmixV"):
            Valve_designation = "V{}".format(int(v)+1)
            Valves[Valve_designation] = Valve
            QmixValvesCount += 1
        elif Valve.get_device_name().__contains__("neMESYS_Low_Pressure"):
            for i in range(len(Pump_desig)):
                if str(i+1) in Valve.get_device_name():
                    Valve_designation = "{}v".format(Pump_desig[i])
            Valves[Valve_designation] = Valve
        else:
            print("An error occured. Unknown Type of valve.")
        print(Valve.get_device_name(), Valve_designation)

    # Get number of control channels:
    noOfControllerChannels = qmixcontroller.ControllerChannel.get_no_of_channels()
    print("\n The number of control channels is {} with the names and labels:\n".format(noOfControllerChannels))
    # Retrieve device handles for channels and save channels in Channels:
    Channels = {}
    for c in range(noOfControllerChannels):
        Channel = qmixcontroller.ControllerChannel()
        Channel.lookup_channel_by_index(c)
        # Assign designation shorter than name:
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
        Pumps[pump].set_syringe_param(inner_diameter_mm= syringes_dict[pump].inner_dia_mm, max_piston_stroke_mm= syringes_dict[pump].piston_stroke_mm)
        Pumps[pump].set_volume_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres)
        Pumps[pump].set_flow_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres, qmixpump.TimeUnit.per_second)
        if Pumps[pump].is_in_fault_state():
            Pumps[pump].clear_fault()
        if Pumps[pump].is_in_fault_state() == False and Pumps[pump].is_enabled() == False:
            Pumps[pump].enable(True)
        elif Pumps[pump].is_in_fault_state() == False and Pumps[pump].is_enabled() == True:
            pass
        else:
            print("There is an error. Pump {} is enabled: {}, is in fault state {}.".format(pump, Pumps[pump].is_enabled(), Pumps[pump].is_in_fault_state()))
        print(Pumps[pump].get_syringe_param(), Pumps[pump].get_flow_rate_max(), Pumps[pump].get_volume_max())        
    
    return Pumps, Valves
    '''----------------Preparation end----------------'''

def quitCetoni():
    ''' This function quits the operation of the Cetoni device. It stops the BUS communication and closes the BUS. '''

    '''----------------Finishing start----------------'''
    # Setting devices pre operational
    qmixbus.Bus.stop()
    # Close bus library
    qmixbus.Bus.close()
    '''----------------Finishing end----------------'''