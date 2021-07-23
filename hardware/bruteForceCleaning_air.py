''' --- Startup and imports --- '''
import helpers

# Load the configuration file.
config = helpers.LoadConfig()

# Do the remaining imports.
from datetime import datetime
import networkx as nx
from qmixsdk import qmixbus, qmixvalve, qmixpump
from hardware import CetoniDevice, graph

# Read the path to the hardware configuration and the QmixSDK from the config file.
hardwareConfig = config["paths"]["HardwareConfig"]
qmix = config["paths"]["QmixSDK"]

# Start the timer to determin the runtime of the routine.
starttime = datetime.now()

''' --- Startup and imports --- '''

Pumps, Valves = CetoniDevice.prepareCetoni(hardwareConfig, qmix)
graph.generate_valvePositionDict()
graph_setup, valvePositionDict = graph.loadGraph()
graph_setup.remove_edge("lambdaIN", "lambdaOUT")
graph_setup.remove_edge("lambdaOUT", "lambdaIN")
graph_setup.remove_edge("NMRin", "NMRout")

cleaningAgent = "Reservoir1"
waste = "Reservoir2"
#aspirationPath = nx.dijkstra_path(graph_setup, cleaningAgent, "A0.0", "dead_volume")
#valveSettings = graph.getValveSettings(aspirationPath, valvePositionDict)

timer = qmixbus.PollingTimer(180000)
duration_timer = 180000

pathToValve = {}
valveSettingsToValve = {}
for i in range(1,7):
    pathToValve[f"pathToValve{i}"] = nx.dijkstra_path(graph_setup, "A0.0", f"V{i}.0", "dead_volume")
    valveSettingsToValve[f"valveSettingsV{i}"] = graph.getValveSettings(pathToValve[f"pathToValve{i}"], valvePositionDict)

# Clean valve V1
# Aspirate solvent in each pump -> valve 1 clean
pathToPump = {}
for pump in Pumps.keys():
    pathToPump[pump] = nx.dijkstra_path(graph_setup, cleaningAgent, pump)
print(pathToPump)

''' Step 1 '''
print("Step 1")

reservoirs = {"A0.0": "Reservoir3", "B0.0": "Reservoir4", "C0.0": "Reservoir5", "D0.0": "Reservoir6", "E0.0": "Reservoir7", "F0.0": "Reservoir8"}
for pump in ["A0.0", "B0.0", "C0.0", "D0.0", "E0.0", "F0.0"]:
    print(pump)
    valveSettings1 = graph.getValveSettings(pathToPump[pump], valvePositionDict)
    print("valveSettings1: \n", valveSettings1)
    for valve_asp in valveSettings1.keys():
        Valves[valve_asp].switch_valve_to_position(valveSettings1[valve_asp])
        print("ValvePositionCheck: ", Valves[valve_asp].actual_valve_position())
    Pumps[pump].set_fill_level(1.0, 0.03)
    timer.wait_until(Pumps[pump].is_pumping, False)
    print(f"{pump} is pumping:", Pumps[pump].is_pumping())
    # Dispense solvent through V3.3 to V3.8 -> valve 3 clean
    pathToClean = nx.dijkstra_path(graph_setup, pump, reservoirs[pump], "dead_volume")
    print("PathToClean: ", pathToClean)
    valveSettings_pathToClean = graph.getValveSettings(pathToClean, valvePositionDict)
    print("valveSettings_pathToClean: ", valveSettings_pathToClean)
    #print(valveSettings_pathToClean)
    for valve_disp in valveSettings_pathToClean.keys():
        if valve_disp in valvePositionDict.keys():
            Valves[valve_disp].switch_valve_to_position(valveSettings_pathToClean[valve_disp])
            print(Valves[valve_disp].actual_valve_position())
    Pumps[pump].set_fill_level(0.0, 0.03)
    timer.set_period(300000)
    timer.wait_until(Pumps[pump].is_pumping, False)
    print(f"{pump} is pumping:", Pumps[pump].is_pumping())
print("Step 1 finished! \n Valve 1 clean \n Valve 3 clean")

''' Step 2 '''
print("Step 2")

print("\n Starting Step 2! \n")

# Pump from pump F to E to D to C to B to A to waste -> V2.10 pending

# cleaningAgent -> F
aspirationPath = pathToPump["F0.0"]
print("aspirationPath: ", aspirationPath)
valveSettings = graph.getValveSettings(aspirationPath, valvePositionDict)
print("valveSettings: ", valveSettings)

for valve_asp in valveSettings.keys():
    if valve_asp in valvePositionDict.keys():
        Valves[valve_asp].switch_valve_to_position(valveSettings[valve_asp])
        print("ValvePositionCheck: ", Valves[valve_asp].actual_valve_position())
Pumps["F0.0"].set_fill_level(2.0, 0.03)
timer.wait_until(Pumps["F0.0"].is_pumping, False)
print("F0.0 is pumping:", Pumps[pump].is_pumping())

# F -> E
pathToE = ["F0.0", "F0.1", "Fv1", "V1.6", "V1.0", "V2.0", "V2.5", "EY2", "EY1", "Ev2", "E0.1", "E0.0"]
print("pathToE: ", pathToE)
valveSettings_pathToE = graph.getValveSettings(pathToE, valvePositionDict)
print("valveSettins_pathToE: ", valveSettings_pathToE)

for valve_disp in valveSettings_pathToE.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToE[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

def pump_to_other(pump1, pump2, volume, flow_rate): # By Lisa Schroeder
    # aspirate pump 2
    pump2.pump_volume(-volume, flow_rate)
    # dispense pump 1
    pump1.pump_volume(volume, flow_rate)
    # wait till pumps stopped pumping
    timer.wait_until(pump2.is_pumping and pump1.is_pumping, False)

timer.set_period(duration_timer)
pump_to_other(Pumps["F0.0"], Pumps["E0.0"], Pumps["F0.0"].get_fill_level(), 0.03)

# E -> D
pathToD = ["E0.0", "E0.1", "Ev1", "V1.5", "V1.0", "V2.0", "V2.4", "DY2", "DY1", "Dv2", "D0.1", "D0.0"]
print("pathToD: ", pathToD)
valveSettings_pathToD = graph.getValveSettings(pathToD, valvePositionDict)
print("valveSettins_pathToD: ", valveSettings_pathToD)

for valve_disp in valveSettings_pathToD.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToD[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["E0.0"], Pumps["D0.0"], Pumps["E0.0"].get_fill_level(), 0.03)

# D -> C
pathToC = ["D0.0", "D0.1", "Dv1", "V1.4", "V1.0", "V2.0", "V2.3", "CY2", "CY1", "Cv2", "C0.1", "C0.0"]
print("pathToC: ", pathToC)
valveSettings_pathToC = graph.getValveSettings(pathToC, valvePositionDict)
print("valveSettins_pathToC: ", valveSettings_pathToC)

for valve_disp in valveSettings_pathToC.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToC[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["D0.0"], Pumps["C0.0"], Pumps["D0.0"].get_fill_level(), 0.03)

# C -> B
pathToB = ["C0.0", "C0.1", "Cv1", "V1.3", "V1.0", "V2.0", "V2.2", "BY2", "BY1", "Bv2", "B0.1", "B0.0"]
print("pathToB: ", pathToB)
valveSettings_pathToB = graph.getValveSettings(pathToB, valvePositionDict)
print("valveSettins_pathToB: ", valveSettings_pathToB)

for valve_disp in valveSettings_pathToB.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToB[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["C0.0"], Pumps["B0.0"], Pumps["C0.0"].get_fill_level(), 0.03)

# B -> A
pathToA = ["B0.0", "B0.1", "Bv1", "V1.2", "V1.0", "V2.0", "V2.1", "AY2", "AY1", "Av2", "A0.1", "A0.0"]
print("pathToA: ", pathToA)
valveSettings_pathToA = graph.getValveSettings(pathToA, valvePositionDict)
print("valveSettins_pathToB: ", valveSettings_pathToA)

for valve_disp in valveSettings_pathToA.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToA[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["B0.0"], Pumps["A0.0"], Pumps["B0.0"].get_fill_level(), 0.03)

# A -> waste
pathToWaste = nx.dijkstra_path(graph_setup, "A0.0", waste)
print("pathToWaste: ", pathToWaste)
valveSettings_pathToWaste = graph.getValveSettings(pathToWaste, valvePositionDict)
print("valveSettings_pathToWaste: ", valveSettings_pathToWaste)

for valve_waste in valveSettings_pathToWaste.keys():
    if valve_waste in valvePositionDict.keys():
        Valves[valve_waste].switch_valve_to_position(valveSettings_pathToWaste[valve_waste])
        print("ValvePositionCheck: ", Valves[valve_waste].actual_valve_position())

Pumps["A0.0"].set_fill_level(0.0, 0.03)
timer.set_period(duration_timer)
timer.wait_until(Pumps["A0.0"].is_pumping, False)
print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())
print("Step 2 finished!")

''' Step 3 '''
print("Step 3")

print("\n Starting Step 3! \n")

# Pump from pump A to V5.1, 2, 4, 5, 6, 7, 8, 9 -> V2 clean
aspirationPath = pathToPump["A0.0"]
print(aspirationPath)
valveSettings_asp = graph.getValveSettings(aspirationPath, valvePositionDict)
print(valveSettings_asp)

for valve in valveSettings_asp.keys():
    if valve in valvePositionDict.keys():
        Valves[valve].switch_valve_to_position(valveSettings_asp[valve])
        print("ValvePositionCheck: ", Valves[valve].actual_valve_position())

Pumps["A0.0"].set_fill_level(2.5, 0.03)
timer.set_period(duration_timer)
timer.restart()
timer.wait_until(Pumps["A0.0"].is_pumping, False)
print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())

index = list(range(1,10))
print(index)
index.remove(3)
print(index)

pathToV5 = nx.dijkstra_path(graph_setup, "A0.0", "V5.0")
print(pathToV5)
valveSettings_pathToV5 = graph.getValveSettings(pathToV5, valvePositionDict)
print("valveSettings_pathToV5: ", valveSettings_pathToV5)

for val in valveSettings_pathToV5.keys():
    print(val)
    if val in valvePositionDict.keys():
        print(val)
        Valves[val].switch_valve_to_position(valveSettings_pathToV5[val])
    print("ValvePositionCheck: ", Valves[val].actual_valve_position())

for j in index:
    if Pumps["A0.0"].get_fill_level() > 0.03*40:
        path = pathToV5.copy()
        out = [f"V5.{j}"]
        print(out)
        path = path + out
        print("path: ", path)
        valveSettings_path = graph.getValveSettings(path, valvePositionDict)
        print("valveSettings_path: ", valveSettings_path)
        for valve in valveSettings_path.keys():
            if valve in valvePositionDict.keys():
                Valves[valve].switch_valve_to_position(valveSettings_path[valve])
            print("ValvePositionCheck: ", Valves[valve].actual_valve_position())

        Pumps["A0.0"].generate_flow(0.03)
        timer.set_period(40000)
        timer.restart()
        timer.wait_until(timer.is_expired, True)
        Pumps["A0.0"].stop_pumping()
        print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())
    else:
        for valve in valveSettings_asp.keys():
            if valve in valvePositionDict.keys():
                Valves[valve].switch_valve_to_position(valveSettings_asp[valve])
            print("ValvePositionCheck: ", Valves[valve].actual_valve_position())

        Pumps["A0.0"].set_fill_level(2.5, 0.03)
        timer.set_period(duration_timer)
        timer.restart()
        timer.wait_until(Pumps["A0.0"].is_pumping, False)
        print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())

        path = pathToV5.copy()
        out = [f"V5.{j}"]
        print(out)
        path = path + out
        print("path: ", path)
        valveSettings_path = graph.getValveSettings(path, valvePositionDict)
        print("valveSettings_path: ", valveSettings_path)
        for valv in valveSettings_path.keys():
            if valv in valvePositionDict.keys():
                Valves[valv].switch_valve_to_position(valveSettings_path[valv])
            print("ValvePositionCheck: ", Valves[valv].actual_valve_position())

        Pumps["A0.0"].generate_flow(0.03)
        timer.set_period(40000)
        timer.restart()
        timer.wait_until(timer.is_expired, True)
        Pumps["A0.0"].stop_pumping()
        print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())

print("Step 3 finished! \n Valve 2 clean!")

''' Step 4 '''
print("Step 4")

print("\n Starting Step 4! \n")

# Pump from pump A to V5.3, V6.2, V6.0, V4.0, B, waste -> V5 clean
aspirationPath = pathToPump["A0.0"]
print(aspirationPath)
valveSettings_asp = graph.getValveSettings(aspirationPath, valvePositionDict)
print(valveSettings_asp)

for valve in valveSettings_asp.keys():
    if valve in valvePositionDict.keys():
        Valves[valve].switch_valve_to_position(valveSettings_asp[valve])
    print("ValvePositionCheck: ", Valves[valve].actual_valve_position())

Pumps["A0.0"].set_fill_level(2.0, 0.03)
timer.wait_until(Pumps["A0.0"].is_pumping, False)
print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())

flushPath = nx.dijkstra_path(graph_setup, "A0.0", "V6.2")
print("flushPath: ", flushPath)
furtherPath = nx.dijkstra_path(graph_setup, "V6.2", "B0.0")
print("furtherPath:", furtherPath)
flushPath.remove("V6.2")
print("flushPath reduced: ", flushPath)

path = flushPath + furtherPath
print("path: ", path)

pump_to_other(Pumps["A0.0"], Pumps["B0.0"], Pumps["A0.0"].get_fill_level(), 0.03)
#timer.set_period(duration_timer)
#timer.restart()
#timer.wait_until(timer.is_expired, True)

wastePath = nx.dijkstra_path(graph_setup, "B0.0", waste, "dead_volume")
print("wastePath: ", wastePath)
Pumps["B0.0"].set_fill_level(0.0, 0.03)
timer.set_period(duration_timer)
timer.restart()
timer.wait_until(Pumps["B0.0"].is_pumping, False)
print("B0.0 is pumping:", Pumps["B0.0"].is_pumping())

print("Step 4 finished! \n Valve 5 clean!")

''' Step 5 '''
print("Step 5")

print("\n Starting Step 5! \n")

# Aspirate solvent to pump A, B, C, D, E, F via V6.1, 3, 4, 5, 6, 7, 8, 9 then to waste -> V6 clean, V4 clean
starts = ["Q-3", "Q+Chip6", "Q+Chip7", "Q+Chip8", "Q+Chip9", "Q+Chip10", "lambdaOUT", "NMRout"]
startspp = {"B0.0": "Q+Chip8", "C0.0": "Q+Chip9", "D0.0": "Q+Chip10", "E0.0": "lambdaOUT", "F0.0": "NMRout"}

for pump in Pumps.keys():
    print(pump)
    if pump == "A0.0":
        for start in starts[0:3]:
            print(starts[0:3])
            print(start)
            path_chip = nx.dijkstra_path(graph_setup, start, pump, "dead_volume")
            print(path_chip)
            valveSettings_toChip = graph.getValveSettings(path_chip, valvePositionDict)
            print(valveSettings_toChip)

            for valve in valveSettings_toChip.keys():
                if valve in valvePositionDict.keys():
                    Valves[valve].switch_valve_to_position(valveSettings_toChip[valve])
                    print("ValvePositionCheck: ", Valves[valve].actual_valve_position())

            Pumps[pump].set_fill_level(0.6, 0.03)
            timer.set_period(duration_timer)
            timer.restart()
            timer.wait_until(Pumps[pump].is_pumping, False)
            print(f"{pump} is pumping:", Pumps[pump].is_pumping())

            toWaste = nx.dijkstra_path(graph_setup, pump, waste, "dead_volume")
            print("toWaste: ", toWaste)
            valveSettings_toWaste = graph.getValveSettings(toWaste, valvePositionDict)
            print("valveSettings_toWaste: ", valveSettings_toWaste)

            for valve in valveSettings_toWaste.keys():
                if valve in valvePositionDict.keys():
                    Valves[valve].switch_valve_to_position(valveSettings_toWaste[valve])
                    print("ValvePositionCheck: ", Valves[valve].actual_valve_position())
            
            Pumps[pump].set_fill_level(0.0, 0.03)
            timer.set_period(duration_timer)
            timer.restart()
            timer.wait_until(Pumps[pump].is_pumping, False)
            print(f"{pump} is pumping:", Pumps[pump].is_pumping())
    else:
            path_chip = nx.dijkstra_path(graph_setup, startspp[pump], pump, "dead_volume")
            print(path_chip)
            valveSettings_toChip = graph.getValveSettings(path_chip, valvePositionDict)
            print(valveSettings_toChip)

            for valve in valveSettings_toChip.keys():
                if valve in valvePositionDict.keys():
                    Valves[valve].switch_valve_to_position(valveSettings_toChip[valve])
                    print("ValvePositionCheck: ", Valves[valve].actual_valve_position())

            Pumps[pump].set_fill_level(0.6, 0.03)
            timer.set_period(duration_timer)
            timer.restart()
            timer.wait_until(Pumps[pump].is_pumping, False)
            print(f"{pump} is pumping:", Pumps[pump].is_pumping())

            toWaste = nx.dijkstra_path(graph_setup, pump, waste, "dead_volume")
            print("toWaste: ", toWaste)
            valveSettings_toWaste = graph.getValveSettings(toWaste, valvePositionDict)
            print("valveSettings_toWaste: ", valveSettings_toWaste)

            for valve in valveSettings_toWaste.keys():
                if valve in valvePositionDict.keys():
                    Valves[valve].switch_valve_to_position(valveSettings_toWaste[valve])
                    print("ValvePositionCheck: ", Valves[valve].actual_valve_position())
            
            Pumps[pump].set_fill_level(0.0, 0.03)
            timer.set_period(duration_timer)
            timer.restart()
            timer.wait_until(Pumps[pump].is_pumping, False)
            print(f"{pump} is pumping:", Pumps[pump].is_pumping())

print("Step 5 finished! \n Valve 6 clean! \n Valve 4 clean!")

''' Step 2 repeat '''
print("Step 2 repeat")

print("\n Starting Step 2 repeat! \n")

# Pump from pump F to E to D to C to B to A to waste -> V2.10 pending

# cleaningAgent -> F
aspirationPath = pathToPump["F0.0"]
print("aspirationPath: ", aspirationPath)
valveSettings = graph.getValveSettings(aspirationPath, valvePositionDict)
print("valveSettings: ", valveSettings)

for valve_asp in valveSettings.keys():
    if valve_asp in valvePositionDict.keys():
        Valves[valve_asp].switch_valve_to_position(valveSettings[valve_asp])
        print("ValvePositionCheck: ", Valves[valve_asp].actual_valve_position())
Pumps["F0.0"].set_fill_level(2.0, 0.03)
timer.wait_until(Pumps["F0.0"].is_pumping, False)
print("F0.0 is pumping:", Pumps[pump].is_pumping())

# F -> E
pathToE = ["F0.0", "F0.1", "Fv1", "V1.6", "V1.0", "V2.0", "V2.5", "EY2", "EY1", "Ev2", "E0.1", "E0.0"]
print("pathToE: ", pathToE)
valveSettings_pathToE = graph.getValveSettings(pathToE, valvePositionDict)
print("valveSettins_pathToE: ", valveSettings_pathToE)

for valve_disp in valveSettings_pathToE.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToE[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

def pump_to_other(pump1, pump2, volume, flow_rate): # By Lisa Schroeder
    # aspirate pump 2
    pump2.pump_volume(-volume, flow_rate)
    # dispense pump 1
    pump1.pump_volume(volume, flow_rate)
    # wait till pumps stopped pumping
    timer.wait_until(pump2.is_pumping and pump1.is_pumping, False)

timer.set_period(duration_timer)
pump_to_other(Pumps["F0.0"], Pumps["E0.0"], Pumps["F0.0"].get_fill_level(), 0.03)

# E -> D
pathToD = ["E0.0", "E0.1", "Ev1", "V1.5", "V1.0", "V2.0", "V2.4", "DY2", "DY1", "Dv2", "D0.1", "D0.0"]
print("pathToD: ", pathToD)
valveSettings_pathToD = graph.getValveSettings(pathToD, valvePositionDict)
print("valveSettins_pathToD: ", valveSettings_pathToD)

for valve_disp in valveSettings_pathToD.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToD[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["E0.0"], Pumps["D0.0"], Pumps["E0.0"].get_fill_level(), 0.03)

# D -> C
pathToC = ["D0.0", "D0.1", "Dv1", "V1.4", "V1.0", "V2.0", "V2.3", "CY2", "CY1", "Cv2", "C0.1", "C0.0"]
print("pathToC: ", pathToC)
valveSettings_pathToC = graph.getValveSettings(pathToC, valvePositionDict)
print("valveSettins_pathToC: ", valveSettings_pathToC)

for valve_disp in valveSettings_pathToC.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToC[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["D0.0"], Pumps["C0.0"], Pumps["D0.0"].get_fill_level(), 0.03)

# C -> B
pathToB = ["C0.0", "C0.1", "Cv1", "V1.3", "V1.0", "V2.0", "V2.2", "BY2", "BY1", "Bv2", "B0.1", "B0.0"]
print("pathToB: ", pathToB)
valveSettings_pathToB = graph.getValveSettings(pathToB, valvePositionDict)
print("valveSettins_pathToB: ", valveSettings_pathToB)

for valve_disp in valveSettings_pathToB.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToB[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["C0.0"], Pumps["B0.0"], Pumps["C0.0"].get_fill_level(), 0.03)

# B -> A
pathToA = ["B0.0", "B0.1", "Bv1", "V1.2", "V1.0", "V2.0", "V2.1", "AY2", "AY1", "Av2", "A0.1", "A0.0"]
print("pathToA: ", pathToA)
valveSettings_pathToA = graph.getValveSettings(pathToA, valvePositionDict)
print("valveSettins_pathToB: ", valveSettings_pathToA)

for valve_disp in valveSettings_pathToA.keys():
    if valve_disp in valvePositionDict.keys():
        Valves[valve_disp].switch_valve_to_position(valveSettings_pathToA[valve_disp])
        print("ValvePositionCheck: ", Valves[valve_disp].actual_valve_position())

timer.set_period(duration_timer)
pump_to_other(Pumps["B0.0"], Pumps["A0.0"], Pumps["B0.0"].get_fill_level(), 0.03)

# A -> waste
pathToWaste = nx.dijkstra_path(graph_setup, "A0.0", waste)
print("pathToWaste: ", pathToWaste)
valveSettings_pathToWaste = graph.getValveSettings(pathToWaste, valvePositionDict)
print("valveSettings_pathToWaste: ", valveSettings_pathToWaste)

for valve_waste in valveSettings_pathToWaste.keys():
    if valve_waste in valvePositionDict.keys():
        Valves[valve_waste].switch_valve_to_position(valveSettings_pathToWaste[valve_waste])
        print("ValvePositionCheck: ", Valves[valve_waste].actual_valve_position())

Pumps["A0.0"].set_fill_level(0.0, 0.03)
timer.set_period(duration_timer)
timer.wait_until(Pumps["A0.0"].is_pumping, False)
print("A0.0 is pumping:", Pumps["A0.0"].is_pumping())
print("Step 2 repeat finished!")


print("Cleaning routine done. Please empty waste container.")

print(datetime.now()-starttime) # https://stackoverflow.com/questions/6786990/find-out-time-it-took-for-a-python-script-to-complete-execution