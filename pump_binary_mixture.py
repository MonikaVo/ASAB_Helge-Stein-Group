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
import pandas as pd

'''----------------create Syringe-Dict begin---------------'''

class Syringe:
    def __init__(self, inner_diameter, piston_stroke, filled_wait_time):
        self.inner_diameter = inner_diameter     # in mm
        self.piston_stroke = piston_stroke       # in mm
        self.filled_wait_time = filled_wait_time        # in s

#define each available syringe
syringe25 = Syringe(23.0329, 60, 300)
syringe2_5 = Syringe(7.28366, 60, 120)
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

flow_rate = 0.03

# valve 1 lights up
# valve 1 is 1
# manually enter, which valves are set how (qmix: 0-9; NeM: 0-1)
qmix_valve_input = {
    "QmixV_1_valve" : 0,
    "QmixV_2_valve" : 6,
    "QmixV_3_valve" : 0,
    "QmixV_4_valve" : 4,
    "QmixV_5_valve" : 5,
    "QmixV_6_valve" : 6
}
neM_LP_valve_input = {
    "neM-LP_1_valve" : 1,
    "neM-LP_2_valve" : 1,
    "neM-LP_3_valve" : 1,
    "neM-LP_4_valve" : 1,
    "neM-LP_5_valve" : 1,
    "neM-LP_6_valve" : 1
}

qmix_valve_output = {
    "QmixV_1_valve" : 0,
    "QmixV_2_valve" : 6,
    "QmixV_3_valve" : 1,
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

# Initialize ContiFlowPump (two pumps virtually connected)
pump_1to2 = ContiFlowPump()
pump_1to2.create(Pumps["neM-LP_1_pump"], Pumps["neM-LP_2_pump"])
pump_1to2.configure_contiflow_valve(0, 0, Valves_pumps["neM-LP_1_valve"], 0, 0, -1)
pump_1to2.configure_contiflow_valve(1, 0, Valves_pumps["neM-LP_2_valve"], 0, 0, -1)
print("Syringe Pump of Pump Channel 0: ", pump_1to2.get_syringe_pump(0))
print("Syringe Pump of Pump Channel 1: ", pump_1to2.get_syringe_pump(1))
print("parameter of Syringe Pump Channel 0: inner diameter, max piston stroke: ", pump_1to2.get_syringe_param())
print("parameter of Syringe Pump Channel 1: inner diameter, max piston stroke: ", pump_1to2.get_syringe_param())

pump_1to2.set_device_property(ContiFlowProperty.SWITCHING_MODE,ContiFlowSwitchingMode.CROSS_FLOW)
max_refill_flow = pump_1to2.get_device_property(ContiFlowProperty.MAX_REFILL_FLOW)
pump_1to2.set_device_property(ContiFlowProperty.REFILL_FLOW, max_refill_flow / 2.0)
pump_1to2.set_device_property(ContiFlowProperty.CROSSFLOW_DURATION_S, crossflow_seconds)
pump_1to2.set_device_property(ContiFlowProperty.OVERLAP_DURATION_S, 0)
max_conti_flow = pump_1to2.get_flow_rate_max()
print("Max. pumpt_1to2 flow rate: ", max_conti_flow)

# clear all device errors and set device into enabled state
pump_1to2.clear_fault()
pump_1to2.enable(True)

# initialize contiflow
# ignored, since reference move would be done

flow_rate = min(Pumps["neM-LP_1_pump"], Pumps["neM-LP_2_pump"])



'''----------------Preparation end----------------'''


###################ACTION CODE START##########################

# create dict chemList including objects of class chemicals
# only necessary, if "Chemicals_database.csv" changed
# chemList = chemicals.getChemicalsList("experiment\\Chemicals_database.csv")           #https://coderslegacy.com/import-class-from-python-file/, https://www.geeksforgeeks.org/python-read-csv-using-pandas-read_csv/

# load chemList
chemList = chemicals.loadChemicalsList("chemList")
# Define mixture
# mixratio = list(input("define mixratio: "))     # enter mixratio as e.g. 0.5, 0.5
# components = list(input("define components: "))     # enter components as e.g. water, ethanol
# amount = input("define total amount of mixture: ")
# vol = calcComp.calcComp(chemList, mixratio, components, amount)
# print(vol)


# switch valves ready for filling the pump
print("change valve position for aspirating")
for valve in qmix_valve_input.keys():
    Valves_Qmix[valve].switch_valve_to_position(qmix_valve_input[valve])
    # print(valve, " Position: ", Valves_Qmix[valve].actual_valve_position())
for valve in neM_LP_valve_input.keys():
    Valves_pumps[valve].switch_valve_to_position(neM_LP_valve_input[valve])
    # print(valve, " Position: ", Valves_pumps[valve].actual_valve_position())

# start filling the pump
# Pumps["neM-LP_1_pump"].aspirate(p*Pumps["neM-LP_1_pump"].get_volume_max(), 0.5*Pumps["neM-LP_1_pump"].get_flow_rate_max())
print("ready to start pumping? Press any key to continue")
input()
print("Start Pumping")
Pumps["neM-LP_1_pump"].aspirate(test_volume[i]*Pumps["neM-LP_1_pump"].get_volume_max(), flow_rate)

# wait until pump is full
timer = qmixbus.PollingTimer(600000)
timer.wait_until(Pumps["neM-LP_1_pump"].is_pumping, False)
print("finished pumping, wait for pump to get filled")
# abhängig von der Füllhöhe oder von maximal möglicher Füllung warten?
# time.sleep(syringe_dict["neM-LP_1_pump"].filled_wait_time)
print("\nFilling level of Pump 1:", Pumps["neM-LP_1_pump"].get_fill_level())
print("confirm the pump is full and can be dispensed")
input()

# switch valves for pumping syringe 1 to 2

# pump syringe 1 to 2
pump_1to2.set_fill_level(0, flow_rate)

# switch valves ready for emptying pump
print("change valve position for dispensing")
for valve in qmix_valve_output.keys():
    Valves_Qmix[valve].switch_valve_to_position(qmix_valve_output[valve])
    # print(valve, " Position: ", Valves_Qmix[valve].actual_valve_position())
for valve in neM_LP_valve_output.keys():
    Valves_pumps[valve].switch_valve_to_position(neM_LP_valve_output[valve])
    # print(valve, " Position: ", Valves_pumps[valve].actual_valve_position())

#start emptying the pump
print("dispense pump")
# Pumps["neM-LP_1_pump"].dispense(Pumps["neM-LP_1_pump"].get_fill_level(), 0.5*Pumps["neM-LP_1_pump"].get_flow_rate_max())
Pumps["neM-LP_1_pump"].dispense(Pumps["neM-LP_1_pump"].get_fill_level(), flow_rate)
timer.wait_until(Pumps["neM-LP_1_pump"].is_pumping, False)
#wait, until pump is empty
#print("time to wait for emptying the pump", p*Pumps["neM-LP_1_pump"].get_volume_max()/Pumps["neM-LP_1_pump"].get_flow_rate_max()+5)
#time.sleep(p*Pumps["neM-LP_1_pump"].get_volume_max()*Pumps["neM-LP_1_pump"].get_flow_rate_max()+5)
print("\nFilling level of Pump 1:", Pumps["neM-LP_1_pump"].get_fill_level())





###################ACTION CODE END##########################


'''----------------Finishing start----------------'''

# Setting devices pre operational
qmixbus.Bus.stop()
# Close bus library
qmixbus.Bus.close()

'''----------------Finishing end----------------'''