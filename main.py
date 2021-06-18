# Add Qmix SDK path to module search path in order to make sure Python finds SDK modules.
import sys
sys.path.append(r".../QmixSDK/lib/python")  # edited prior to publication
from experiment import calcComp, chemicals
# import qmix modules
from qmixsdk import qmixbus, qmixpump, qmixvalve, qmixcontroller

# import other modules
import time
# import calcComp
# import chemicals
# import testCalcComp

'''----------------create Syringe-Dict begin---------------'''

class Syringe:
    def __init__(self, inner_diameter, piston_stroke, filled_wait_time):
        self.inner_diameter = inner_diameter     # in mm
        self.piston_stroke = piston_stroke       # in mm
        self.filled_wait_time = filled_wait_time        # in s

#define each available syringe
syringe25 = Syringe(23.0329, 60, 300)
syringe2_5 = Syringe(7.28366, 60, 60)
syringe1 = Syringe(4.60659, 60, 30)
syringe0_025 = Syringe(0.728366, 60, 10)

#manually enter, which syringe is at which pump, e.g.:
syringe_dict = {
    "neM-LP_1_pump" : syringe1,
    "neM-LP_2_pump" : syringe2_5,
    "neM-LP_3_pump" : syringe25,
    "neM-LP_4_pump" : syringe1,
    "neM-LP_5_pump" : syringe0_025,
    "neM-LP_6_pump" : syringe2_5
}

#manually enter, which valves are set how
qmix_valve_input = {
    "QmixV_1_valve" : 1,
    "QmixV_2_valve" : 2,
    "QmixV_3_valve" : 3,
    "QmixV_4_valve" : 4,
    "QmixV_5_valve" : 5,
    "QmixV_6_valve" : 6
}
neM_LP_valve_input = {
    "neM-LP_1_valve" : 0,
    "neM-LP_2_valve" : 0,
    "neM-LP_3_valve" : 0,
    "neM-LP_4_valve" : 1,
    "neM-LP_5_valve" : 1,
    "neM-LP_6_valve" : 1
}

qmix_valve_output = {
    "QmixV_1_valve" : 9,
    "QmixV_2_valve" : 8,
    "QmixV_3_valve" : 7,
    "QmixV_4_valve" : 6,
    "QmixV_5_valve" : 5,
    "QmixV_6_valve" : 4
}
neM_LP_valve_output = {
    "neM-LP_1_valve" : 1,
    "neM-LP_2_valve" : 1,
    "neM-LP_3_valve" : 1,
    "neM-LP_4_valve" : 0,
    "neM-LP_5_valve" : 0,
    "neM-LP_6_valve" : 0
}

'''----------------create Syringe-Dict end---------------'''

'''----------------Preparation start----------------'''

# # Define paths for relevant folders
# # Path to configuration
config_path = r"...\ASAB_Config1_sim"  # edited prior to publication
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
    Pumps[pump].calibrate()
    timer = qmixbus.PollingTimer(60000)
    timer.wait_until(Pumps[pump].is_calibration_finished, True)
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

'''----------------Preparation end----------------'''

###################ACTION CODE START##########################

# create dict chemList including objects of class chemicals
# only necessary, if "Chemicals_database.csv" changed
# chemList = chemicals.getChemicalsList("experiment\\Chemicals_database.csv")           #https://coderslegacy.com/import-class-from-python-file/, https://www.geeksforgeeks.org/python-read-csv-using-pandas-read_csv/

# load chemList
chemList = chemicals.loadChemicalsList("chemList")

# Define mixture
# vol = calcComp.calcComp(chemList, mixratio, components, amount)
# print(vol)

# pumping a test volume, 100 %, 50 %, 25 % and 10 % of the possible volume of each syringe
test_volume = [0.1, 0.25, 0.5, 1]


for p in test_volume:
    # switch valves ready for filling the pump
    print()
    for valve in qmix_valve_input.keys():
        Valves_Qmix[valve].switch_valve_to_position(qmix_valve_input[valve])
        print(valve, " Position: ", Valves_Qmix[valve].actual_valve_position())
    for valve in neM_LP_valve_input.keys():
        Valves_pumps[valve].switch_valve_to_position(neM_LP_valve_input[valve])
        print(valve, " Position: ", Valves_pumps[valve].actual_valve_position())


    # start filling the pump
    Pumps["neM-LP_1_pump"].aspirate(p*Pumps["neM-LP_1_pump"].get_volume_max(), Pumps["neM-LP_1_pump"].get_flow_rate_max())
    # wait until pump is full
    timer.wait_until(Pumps["neM-LP_1_pump"].is_pumping, False)
    # abhängig von der Füllhöhe oder von maximal möglicher Füllung warten?
    time.sleep(syringe_dict["neM-LP_1_pump"].filled_wait_time)
    print("\nFilling level of Pump 1:", Pumps["neM-LP_1_pump"].get_fill_level())

    # switch valves ready for emptying pump, available valves positions from 0 to 9
    print()
    for valve in qmix_valve_output.keys():
        Valves_Qmix[valve].switch_valve_to_position(qmix_valve_output[valve])
        print(valve, " Position: ", Valves_Qmix[valve].actual_valve_position())
    for valve in neM_LP_valve_output.keys():
        Valves_pumps[valve].switch_valve_to_position(neM_LP_valve_output[valve])
        print(valve, " Position: ", Valves_pumps[valve].actual_valve_position())

    #start emptying the pump
    Pumps["neM-LP_1_pump"].dispense(Pumps["neM-LP_1_pump"].get_fill_level(), Pumps["neM-LP_1_pump"].get_flow_rate_max())
    timer.wait_until(Pumps["neM-LP_1_pump"].is_pumping, False)
    print("\nFilling level of Pump 1:", Pumps["neM-LP_1_pump"].get_fill_level())
###################ACTION CODE END##########################


'''----------------Finishing start----------------'''

# Setting devices pre operational
qmixbus.Bus.stop()
# Close bus library
qmixbus.Bus.close()

'''----------------Finishing end----------------'''