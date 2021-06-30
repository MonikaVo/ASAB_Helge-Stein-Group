# Add Qmix SDK path to module search path in order to make sure Python finds SDK modules.
import sys
sys.path.append(r".../QmixSDK/lib/python")  # edited prior to publication
from experiment import calcComp, chemicals
# import qmix modules
from qmixsdk import qmixbus, qmixpump, qmixvalve, qmixcontroller
from qmixsdk.qmixpump import ContiFlowProperty, ContiFlowPump, ContiFlowSwitchingMode


# import other modules
import time
# import calcComp
# import chemicals
# import testCalcComp
import pandas as pd

'''----------------create Syringe-Dict begin---------------'''

class Syringe:
    def __init__(self, inner_diameter, piston_stroke, filled_wait_time, flow_rate):
        self.inner_diameter = inner_diameter     # in mm
        self.piston_stroke = piston_stroke       # in mm
        self.filled_wait_time = filled_wait_time        # in s
        self.flow_rate = flow_rate      # in mL per s

#define each available syringe
syringe25 = Syringe(23.0329, 60, 300, 0.5)
syringe2_5 = Syringe(7.28366, 60, 120, 0.05)
syringe1 = Syringe(4.60659, 60, 300, 0.03)
syringe0_025 = Syringe(0.728366, 60, 10, 0.0005)

#manually enter, which syringe is at which pump, e.g.:
syringe_dict = {
    "neM-LP_1_pump" : syringe1,
    "neM-LP_2_pump" : syringe2_5,
    "neM-LP_3_pump" : syringe2_5,
    "neM-LP_4_pump" : syringe1,
    "neM-LP_5_pump" : syringe0_025,
    "neM-LP_6_pump" : syringe2_5
}

# valve 1 lights up
# valve 1 is 1
# manually enter, which valves are set how (qmix: 0-9; NeM: 0-1)
qmix_valve_aspirate_first_component = {
    "QmixV_3_valve" : 0,
}
neM_LP_valve_aspirate_first_component = {
    "neM-LP_1_valve" : 1,
}

neM_LP_valve_first_to_second_syringe = {
    "neM-LP_1_valve" : 0,
    "neM-LP_2_valve" : 1,
}

qmix_valve_aspirate_second_component = {
    "QmixV_3_valve" : 1,
}
neM_LP_valve_aspirate_second_component = {
    "neM-LP_1_valve" : 1,
}

neM_LP_valve_pump_to_nmr = {
    "neM-LP_2_valve" : 0,
}

neM_LP_valve_second_to_third_syringe = {
    "neM-LP_2_valve": 0,
    "neM-LP_3_valve": 1,
}

qmix_valve_aspirate_components = [qmix_valve_aspirate_first_component, qmix_valve_aspirate_second_component]
neM_valve_aspirate_components = [neM_LP_valve_aspirate_first_component, neM_LP_valve_aspirate_second_component]

'''----------------create Syringe-Dict end---------------'''

'''----------------Preparation start----------------'''

# # Define paths for relevant folders
# # Path to configuration
config_path = r"...\ASAB_Conf1"  # edited prior to publication
# # Path to QmixSDK
QmixSDK_path = r"...\QmixSDK"  # edited prior to publication
# Open bus library
qmixbus.Bus.open(config_path, QmixSDK_path)

# setup_config()
# Get info about the numbers of accessible elements and retrieve handles and print overview
print("\n\n--------------Detected Setup--------------\n\n")

# Get number of pump modules:
noOfPumps = qmixpump.Pump.get_no_of_pumps()
print("\n The number of pumps is {} with the names and lables:\n".format(noOfPumps))
# Retrieve device handles for pump modules and save pumps in Pumps:
Pumps = {}
for p in range(noOfPumps):
    Pump = qmixpump.Pump()
    Pump.lookup_by_device_index(p)
    # Assign designation shorter than name:
    Pump_designation = Pump.get_device_name().replace("neMESYS_Low_Pressure_", "neM-LP_")
    Pump_designation = Pump_designation.replace("Pump", "pump")
    Pumps[Pump_designation] = Pump
    print(Pump.get_device_name(), Pump_designation)

# Get number of valves (QmixV elements PLUS valves for syringe pumps):
noOfValves = qmixvalve.Valve.get_no_of_valves()
print("\n The number of valves is {} with the names and labels:\n".format(noOfValves))
# Retrieve device handles for valves and save valves in Valves:
Valves_Qmix = {}
Valves_pumps = {}
for v in range(noOfValves):
    Valve = qmixvalve.Valve()
    Valve.lookup_by_device_index(v)
    # Separate QmixV module valves from valves on pump modules and define designation shorter than name:
    if Valve.get_device_name().__contains__("QmixV"):
        Valve_designation = Valve.get_device_name().replace("_Valve", "_valve")
        Valves_Qmix[Valve_designation] = Valve
    elif Valve.get_device_name().__contains__("neMESYS_Low_Pressure"):
        Valve_designation = Valve.get_device_name().replace("neMESYS_Low_Pressure_", "neM-LP_")
        Valve_designation = Valve_designation.replace("_Valve", "_valve")
        Valves_pumps[Valve_designation] = Valve
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
    Channel_designation = Channel_designation.replace("QmixQplus_Column", "QQ+_col")
    Channel_designation = Channel_designation.replace("Temperature", "temp")
    Channel_designation = Channel_designation.replace("ReactionLoop", "loop")
    Channel_designation = Channel_designation.replace("ReactorZone", "zone")
    Channels[Channel_designation] = Channel
    print(Channel.get_name(), Channel_designation)

print("\n\n--------------Detected Setup--------------\n\n")
# Setting devices operational
qmixbus.Bus.start()

# Initialize and configure pumps
for pump in Pumps.keys():
    # TODO@warning_message
    # print("Now a calibration move is done. All syringes have to be removed. Confirm with any key")
    # input()
    # Pumps[pump].calibrate()
    # timer = qmixbus.PollingTimer(60000)
    # timer.wait_until(Pumps[pump].is_calibration_finished, True)
    Pumps[pump].set_syringe_param(inner_diameter_mm=syringe_dict[pump].inner_diameter, max_piston_stroke_mm=syringe_dict[pump].piston_stroke)
    Pumps[pump].set_volume_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres)
    Pumps[pump].set_flow_unit(qmixpump.UnitPrefix.milli, qmixpump.VolumeUnit.litres, qmixpump.TimeUnit.per_second)
    if Pumps[pump].is_in_fault_state():
        Pumps[pump].clear_fault()
    if Pumps[pump].is_in_fault_state() == False and Pumps[pump].is_enabled() == False:
        Pumps[pump].enable(True)
    elif Pumps[pump].is_in_fault_state() == False and Pumps[pump].is_enabled() == True:
        pass
    else:
        print("There is an error. Pump {} is enabled: {}, is in fault state {}.".format(pump, Pumps[pump].is_enabled(),Pumps[pump].is_in_fault_state()))
    print(Pumps[pump].get_syringe_param(), Pumps[pump].get_flow_rate_max(), Pumps[pump].get_volume_max())

# Initialize valves - set valves to a defined position
for valve in Valves_Qmix.keys():
    Valves_Qmix[valve].switch_valve_to_position(0)
    # print("{} at position {}".format(valve, Valves_Qmix[valve].actual_valve_position()))
for valve_p in Valves_pumps.keys():
    Valves_pumps[valve_p].switch_valve_to_position(0)
    # print("{} at position {} of {} positions".format(valve_p, Valves_pumps[valve_p].actual_valve_position(), Valves_pumps[valve_p].number_of_valve_positions()))

def pump_to_other(pump1, pump2, volume, flow_rate):
    # aspirate pump 2
    pump2.pump_volume(-volume, flow_rate)
    # dispense pump 1
    pump1.pump_volume(volume, flow_rate)
    # wait till pumps stopped pumping
    timer.wait_until(pump2.is_pumping and pump1.is_pumping, False)


pump_1to2_flow_rate = min(Pumps["neM-LP_1_pump"].get_flow_rate_max(), Pumps["neM-LP_2_pump"].get_flow_rate_max())
print("pump_1to2_flow_rate: ", pump_1to2_flow_rate)

pump_2to3_flow_rate = min(Pumps["neM-LP_2_pump"].get_flow_rate_max(), Pumps["neM-LP_3_pump"].get_flow_rate_max())
print("pump_2to3_flow_rate: ", pump_1to2_flow_rate)

'''----------------Preparation end----------------'''


###################ACTION CODE START##########################

# create dict chemList including objects of class chemicals
# only necessary, if "Chemicals_database.csv" changed
# chemList = chemicals.getChemicalsList("experiment\\Chemicals_database.csv")           #https://coderslegacy.com/import-class-from-python-file/, https://www.geeksforgeeks.org/python-read-csv-using-pandas-read_csv/

# load chemList
chemList = chemicals.loadChemicalsList("chemList")
components = ['EtOH', 'H2O']     # enter components as list
amount = 2      # enter total amount of mixture in mL
vol = [0.9, 0.9]

for i in range(2):
    for i in range(len(components)):
        # start filling the pump
        print("Start aspirating tube ", i, " into first syringe")
        timer = qmixbus.PollingTimer(600000)
       #switch valves ready for aspirating component into first syringe
        for valve in qmix_valve_aspirate_components[i].keys():
            Valves_Qmix[valve].switch_valve_to_position(qmix_valve_aspirate_components[i][valve])
        for valve in neM_valve_aspirate_components[i].keys():
            Valves_pumps[valve].switch_valve_to_position(neM_valve_aspirate_components[i][valve])

        Pumps["neM-LP_1_pump"].aspirate(vol[i], syringe_dict['neM-LP_1_pump'].flow_rate)
        # wait until pump is full
        timer.wait_until(Pumps["neM-LP_1_pump"].is_pumping, False)
        # switch valves for pumping from syringe 1 to 2
        print("\nswitch valves for pumping from syringe 1 to 2")
        for valve in neM_LP_valve_first_to_second_syringe.keys():
            Valves_pumps[valve].switch_valve_to_position(neM_LP_valve_first_to_second_syringe[valve])
            # print(valve, " Position: ", Valves_pumps[valve].actual_valve_position())

        # start pumping component from syringe 1 to 2
        print("Start aspirating tube into second syringe")
        pump_to_other(Pumps["neM-LP_1_pump"], Pumps["neM-LP_2_pump"], Pumps["neM-LP_1_pump"].get_fill_level(), pump_1to2_flow_rate * 0.5)

    # switch valves for pumping to the nmr
    print("\nswitch valves to pump from syringe 2 via nmr to syringe 3")
    for valve in neM_LP_valve_second_to_third_syringe.keys():
        Valves_pumps[valve].switch_valve_to_position(neM_LP_valve_second_to_third_syringe[valve])
        # print(valve, " Position: ", Valves_pumps[valve].actual_valve_position())

    # pump mixture to nmr
    pump_to_other(Pumps["neM-LP_2_pump"], Pumps["neM-LP_3_pump"], Pumps["neM-LP_2_pump"].get_fill_level(), pump_2to3_flow_rate*0.5)

    #pump to waste
    Valves_pumps["neM-LP_3_valve"].switch_valve_to_position(0)
    Pumps["neM-LP_3_pump"].dispense(Pumps["neM-LP_3_pump"].get_fill_level(), syringe_dict['neM-LP_3_pump'].flow_rate)
    # wait until pump is full
    timer.wait_until(Pumps["neM-LP_3_pump"].is_pumping, False)



###################ACTION CODE END##########################


'''----------------Finishing start----------------'''

# Setting devices pre operational
qmixbus.Bus.stop()
# Close bus library
qmixbus.Bus.close()

'''----------------Finishing end----------------'''