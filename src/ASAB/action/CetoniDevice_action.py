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
from ASAB.utility.helpers import typeCheckDict
from ASAB.driver import CetoniDevice_driver, balance_driver
from ASAB.action import balance_action, densioVisco_action
from ASAB.utility import graph
from ASAB.driver.CetoniDevice_driver import getValvePositionDict, pumpObj

## Imports from QmixSDK
import sys
sys.path.append(cf["QmixSDK_python"])
from qmixsdk import qmixbus

## Other imports
from typing import Union
import numpy as np
import pandas as pd
from tqdm import tqdm
import networkx as nx
from networkx.exception import NodeNotFound, NetworkXNoPath
import time
import itertools as it


def flushSyringe(pumps:dict, valves:dict, pump:str, reservoir:str, waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"], repeat:int=3):
    ''' This function flushes the syringe with the fluid, which will be aspirated in the syringe in order to dilute remainders from previous fluids. '''    
    ## Check the input types
    inputTypes = {"pumps": dict, "valves": dict, "pump": str, "reservoir": str, "waste": str, "flow": float, "repeat": int}
    typeCheckDict(inputTypes=inputTypes)

    # Initialize a timer
    duration = 120000
    timer = qmixbus.PollingTimer(period_ms=duration)
    ## Find relevant paths
    # Find a path from the reservoir to the pump
    pathRP = graph.findPath(start_node=reservoir, end_node=pump)
    # Find a path from the pump to the waste
    pathPW = graph.findPath(start_node=pump, end_node=waste)
    ## Go through the number of repetitions and aspirate from the resevoir and dispense to the waste
    for i in range(repeat):
        # Switch valves according to pathRP
        switchValves(nodelist=pathRP, valvesDict=valves)
        # Aspirate 30 % of the max. volume to the pump
        pumps[pump].set_fill_level(level=0.3*pumps[pump].get_volume_max(), flow=flow)
        # Wait until the pump has finished pumping
        timer.wait_until(pumps[pump].is_pumping, False)
        # Switch valves according to pathPW
        switchValves(nodelist=pathPW, valvesDict=valves)
        # Dispense the content of the syringe to the waste
        pumps[pump].set_fill_level(level=0.0, flow=flow)
        # Wait until the pump has finished pumping
        timer.wait_until(pumps[pump].is_pumping, False)

def mix(mixRatio:dict, pumps:dict, valves:dict, assignment:dict=conf["CetoniDevice"]["assignment"], waste:str=conf["CetoniDevice"]["waste"], gas:str=conf["CetoniDevice"]["gas"], setup:Union[str,nx.DiGraph]=conf["CetoniDeviceDriver"]["setup"], flow:float=conf["CetoniDeviceDriver"]["flow"]):
    ''' This function mixes from reservoirs according to the given mixing ratio.
    mixRatio = {"Reservoi1": 0.2, "Reservoir2": 0.8}'''

    ## Check the input types
    inputTypes = {'mixRatio':dict, 'pumps':dict, 'valves':dict, 'assignment':dict, 'waste':str, 'flow':float}
    typeCheckDict(inputTypes=inputTypes)
    # check setup
    setup = graph.getGraph(setup)

    # Generate an assignment from reservoirs to pumps from the assignment of pumps to reservoirs
    revAssignment = dict(zip(assignment.values(), assignment.keys()))
    ## Determine the flows required to get the mixture
    # Initialize a dict of flows
    flows = {}
    for reservoir in mixRatio.keys():
        flows[reservoir] = mixRatio[reservoir]*flow
    print(flows)
    # Get the pumps, which are related to the reservoirs in flow.keys()
    involvedPumps = [revAssignment[r] for r in flows.keys()]

    ## Fill each of the involved syringes with the respective fluid
    # Collect the dead volume of each path to the waste in dV
    dV = []
    ## Fill each pump with its respective fluid
    for p in involvedPumps:
        print(p)
        # Find a path from the syringe to the reservoir
        pathRP = graph.findPath(start_node=assignment[p], end_node=p)
        # Switch valves according to pathR
        switchValves(nodelist=pathRP, valvesDict=valves)
        # Fill the syringe up to maximum volume
        print("Filling syringe")
        print(assignment[p], p)
        fillSyringe(pump=pumps[p], volume=pumps[p].get_volume_max(), reservoir=assignment[p], valvesDict=valves)
        
    for pu in involvedPumps:
        # Find a path from pump to waste
        pathPW = graph.findPath(start_node=pu, end_node=waste)
        # Append the dead volume of pathPW to dV
        dV.append(graph.getTotalQuantity(nodelist=pathPW, quantity="dead_volume"))
        # Switch the valves according to pathPW
        switchValves(nodelist=pathPW, valvesDict=valves)
        # Generate the flow required for the respective reservoir
        pumps[pu].generate_flow(flows[assignment[pu]])
    
    ## Wait until the dead volume of the path from the pump to the waste with the largest dead volume is pumped two times
    # Get the maximum dead volume
    dV_max = max(dV)
    # Wait until dV_max is pumped two times with flow
    timer2 = qmixbus.PollingTimer(period_ms = (2.*dV_max/flow)*1000.)
    timer2.wait_until(timer2.is_expired, True)


def emptySyringes(pumps:dict, valves:dict, waste:str=conf["CetoniDevice"]["waste"], gas:str=conf["CetoniDevice"]["gas"], repeats:int = 3):
    ''' This function removes remaining liquid from all the pumps in the system, by aspirating it into one pump and dispensing it from there to the waste. '''
    # TODO: Test this function
    
    ## Check the input types
    inputTypes = {'pumps':dict, 'valves':dict, 'waste':str, 'gas':str, 'repeats': int}
    typeCheckDict(inputTypes=inputTypes)
    
    # Initialize a timer
    timer = qmixbus.PollingTimer(period_ms=120000)
    # Find candidates with a volume as large as possible for collecting the remainders
    collect_candidates = graph.findPumps(pumps=pumps, status="target=='empty'", secondary={"maximumVolume": np.max})
    # Choose the candidate closest to the waste
    collect, pathCW = graph.findClosest(node=waste, candidates=list(collect_candidates.keys()), direction="in")
    # Set the status of collect to occupied
    pumps[collect].status = "occupied"
    # Find candidates with a volume as large as possible for assisting in cleaing the collection pump afterwards
    assist_candidates = graph.findPumps(pumps=pumps, status="target=='empty'", secondary={"maximumVolume": np.max})
    # Choose the assist pump closest to collect
    assist, pathCA = graph.findClosest(node=collect, candidates=list(assist_candidates.keys()), direction="in")
    # Set the status of assis to occupied
    pumps[assist].status = "occupied"
    for n in range(repeats):
        # Go through all the pumps
        for pump in pumps.keys():
            if (pumps[pump].name != collect):
                # Get the fill level of collect
                level_collect = pumps[collect].get_fill_level()
                # Find a path from pump to collect
                pathAsp = graph.findPath(start_node=pumps[pump].name, end_node=collect, weight="dead_volume")
                # Get the volume of pathAsp
                dV_pathAsp = graph.getTotalQuantity(nodelist=pathAsp, quantity="dead_volume")
                # Check, if the next level exceeds the maximum fill level of collect
                if level_collect+dV_pathAsp*1.5 > pumps[collect].get_volume_max():
                    # If it exceeds the volume, dispense to the waste
                    # Switch the valves according to pathCW
                    switchValves(nodelist=pathCW, valvesDict=valves)
                    # Dispense the collected remainings to the waste
                    pumps[collect].set_fill_level(level=0.0, flow=pumps[collect].get_flow_rate_max()/5.)
                    # Wait for the pump to finish pumping
                    timer.wait_until(pumps[collect].is_pumping, False)
                    # Get the new fill level of collect
                    level_collect = pumps[collect].get_fill_level()
                # Switch the valves according to pathAsp
                switchValves(nodelist=pathAsp, valvesDict= valves)
                # Aspirate dV_pathAsp*1.5 to collect
                pumps[collect].set_fill_level(level=level_collect+dV_pathAsp*1.5, flow=0.03)
                # Wait for the pump to finish pumping
                timer.wait_until(pumps[collect].is_pumping, False)
    # Switch the valves according to pathCW
    switchValves(nodelist=pathCW, valvesDict=valves)
    # Dispense the collected remainings to the waste
    pumps[collect].set_fill_level(level=0.0, flow=pumps[collect].get_flow_rate_max()/5.)
    # Wait for the pump to finish pumping
    timer.wait_until(pumps[collect].is_pumping, False)

    ## Aspirate gas to assist
    # Find a path from gas to assist
    pathGA = graph.findPath(start_node=gas, end_node=assist, weight="dead_volume")
    # Switch the valves according to pathGA
    switchValves(nodelist=pathGA, valvesDict=valves)
    # Aspirate half the volume of assist or collect, whichever is smaller
    pumps[assist].set_fill_level(level=np.min([pumps[assist].get_volume_max()/2., pumps[collect].get_volume_max()/2.]), flow=pumps[assist].get_flow_rate_max()/5.)
    # Wait for the pump to finish pumping
    timer.wait_until(pumps[assist].is_pumping, False)

    ## Aspirate from collect in the direction of assist
    # Get the fill level of assist
    level_assist = pumps[assist].get_fill_level()
    # Find a path from collect to assist
    pathCA = graph.findPath(start_node=collect, end_node=assist)
    # Get the volume of pathCA
    dV_pathCA = graph.getTotalQuantity(nodelist=pathCA, quantity="dead_volume")
    # Switch the valves according to pathCA
    switchValves(nodelist=pathCA, valvesDict=valves)
    # Aspirate two thirds of the volume of pathCA to assist
    pumps[assist].set_fill_level(level=level_assist+(2.*dV_pathCA/3.), flow=0.03)
    # Wait for the pump to finish pumping
    timer.wait_until(pumps[assist].is_pumping, False)

    ## Dispense from assist to waste
    # Find a path from assist to waste
    pathAW = graph.findPath(start_node=assist, end_node=waste)
    # Switch the valves according to pathAW
    switchValves(nodelist=pathAW, valvesDict=valves)
    # Dispense from assist to waste
    pumps[assist].set_fill_level(level=0.0, flow=pumps[assist].get_flow_rate_max()/5.)
    # Wait for the pump to finish pumping
    timer.wait_until(pumps[assist].is_pumping, False)

    ## Switch every pump to gas and release the pressure generated in the system
    # Go through all the pumps
    for pump in pumps.keys():
        # Find a path from gas to pump
        pathGP = graph.findPath(start_node=gas, end_node=pump)
        # switch the valves according to pathGP
        switchValves(nodelist=pathGP, valvesDict=valves)
        # Aspirate gas to pump
        pumps[pump].set_fill_level(level=repeats*dV_pathAsp*1.5, flow=pumps[pump].get_flow_rate_max()/5.)
        # Wait for the pump to finish pumping
        timer.wait_until(pumps[pump].is_pumping, False)
        # Switch the valves to the path from pump to collect
        switchValves(nodelist=pathAsp, valvesDict=valves)
        # Dispense the gas to pathAsp without moving the collect pump
        pumps[pump].set_fill_level(level=0.0, flow=0.03)
        # Wait for the pump to finish pumping
        timer.wait_until(pumps[pump].is_pumping, False)


def cleanMixingsystem(pumpsDict:dict, valvesDict:dict, medium1:str, intermediate:bool = True, medium2:str=conf["CetoniDevice"]["gas"], waste=conf["CetoniDevice"]["waste"], paths=conf["CetoniDevice"]["pathsToClean"], valvePositionDict:dict=CetoniDevice_driver.cetoni.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]), setup=loadFile(conf["CetoniDeviceDriver"]["setup"]), flow:float=conf["CetoniDeviceDriver"]["flow"], repeats:int = 3):
    ''' This function cleans the used paths of an experiment first using solvent and subsequently using gas. It is intended to be used after small experiments, where a cleaning of the full
    system will not be reasonable. The variable intermediate determines, if it is a final cleaning after finishing experiments (False) or if it is an intermediate cleaning in between experiments (True). It requires all the tubing, which is not solvent and not gas to be put to the waste. '''
    # TODO: Test this function!!! TODO: Pump all the remainders in the pumps to one pump and again to the waste in order to reduce the remaining amount of solvent.
    input("Please confirm that all tubes except the ones for the cleaning media are put to the waste.")

    ## Check the input types
    inputTypes = {'pumpsDict':dict, 'valvesDict':dict, 'medium1':str, 'intermediate':bool, 'medium2':str, 'waste':str, 'paths':list, 'flow':float, 'repeats':int}
    typeCheckDict(inputTypes=inputTypes)
    # check valvePositionDict
    valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
    # check setup
    setup = graph.getGraph(setup)

    timer = qmixbus.PollingTimer(180000)
    # Go through all paths
    for path in tqdm(paths):
        print(path)
        # Get the dead volume of the path to clean
        dV_path = graph.getTotalQuantity(nodelist=path, quantity="dead_volume")
        # If the path is a simple path starting from a pump and ending in a reservoir
        if (path[0] in list(pumpsDict.keys())) and ("Reservoir" in path[-1]):
            # The path can stay as it is only, if both media are not in the path.
            if (medium1 not in path) and (medium2 not in path) and not intermediate: # -> TODO: find an alternative reservoir to put the waste
                path = path
            # If one of the media is contained in the path, the final reservoir needs to be changed to the waste
            else:
                print("startReplacement", path[-3])
                replacement = graph.findPath(start_node=path[-3], end_node=waste)
                path=path[0:-3]+replacement
            print(path)
            # Clean first with medium1 and afterwards with medium2
            for medium in [medium1, medium2]:
                # Clean n times with the respective medium
                for n in range(repeats):
                    print("n:", n)
                    print("pump", path[0])
                    print("path:", path)
                    # Get the path to aspirate the medium
                    aspPath = graph.findPath(start_node=medium, end_node=path[0], valvePositionDict=valvePositionDict, graph=setup, weight="dead_volume")
                    # Switch valves to aspirate medium
                    switchValves(nodelist=aspPath, settings={}, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
                    print("aspPath", aspPath)
                    # Fill the syringe with the medium.
                    pumpsDict[path[0]].set_fill_level(level=np.min([3.*dV_path, pumpsDict[path[0]].get_volume_max()]), flow=pumpsDict[path[0]].get_flow_rate_max()/5.)
                    print(np.min([3., pumpsDict[path[0]].get_volume_max()]))
                    # Wait for the pump to finish pumping
                    timer.restart()
                    timer.wait_until(pumpsDict[path[0]].is_pumping, False)
                    # Switch valves to path to be cleaned.
                    switchValves(nodelist=path, settings={}, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
                    # Empty the syringe through the path to be cleaned.
                    pumpsDict[path[0]].set_fill_level(level=0.0, flow=pumpsDict[path[0]].get_flow_rate_max()/5.)
                    # Wait for the pump to finish pumping
                    timer.restart()
                    timer.wait_until(pumpsDict[path[0]].is_pumping, False)
        # If the path is a loop starting from a pump and ending in a pump
        elif (path[0] in list(pumpsDict.keys())) and (path[-1] in list(pumpsDict.keys())):
            # If none of the media is in the path, clean the path
            if (medium1 not in path) and (medium2 not in path):
                # Clean first with medium1 and afterwards with medium2
                for medium in [medium1, medium2]:
                    # Clean n times with the respective medium
                    for n in range(repeats):
                        # Find a path to aspirate the medium in path[0]
                        pathMS = graph.findPath(start_node=medium, end_node=path[0])
                        # Switch the valves to aspirate the medium in path[0]
                        switchValves(nodelist=pathMS, valvesDict=valvesDict)
                        # Aspirate the medium in path[0]
                        pumpsDict[path[0]].set_fill_level(level=np.min([3.*dV_path, pumpsDict[path[0]].get_volume_max()]), flow=flow)
                        # Wait for path[0] to finish pumping
                        timer.wait_until(pumpsDict[path[0]].is_pumping, False)
                        # Get the fill level of path[0]
                        level_p0 = pumpsDict[path[0]].get_fill_level()
                        # Switch the valves according to path
                        switchValves(nodelist=path, valvesDict=valvesDict)
                        # Pump from path[0] to path[-1]
                        pumpsDict[path[0]].set_fill_level(level=0.0, flow=flow)
                        pumpsDict[path[-1]].set_fill_level(level=level_p0, flow=flow)
                        # Wait until both pumps have finished pumping
                        timer.wait_until(pumpsDict[path[0]].is_pumping, False)
                        timer.wait_until(pumpsDict[path[-1]].is_pumping, False)
                        # Find a path from path[-1] to waste
                        pathEW = graph.findPath(start_node=path[-1], end_node=waste)
                        # Switch the valves according to 
                        switchValves(pathEW, valvesDict=valvesDict)
                        # Dispense from path[-1] to the waste
                        pumpsDict[path[-1]].set_fill_level(level=0.0, flow=flow)
                        # Wait for the pump to finish pumping
                        timer.wait_until(pumpsDict[path[-1]].is_pumping, False)
            # If medium1 or medium2 are in the path, skip this path
            else:
                next
    return True

def cleanInstrument(pumpsDict:dict, valvesDict:dict, instrumenttype:str, medium1:str, pumpIN:str="A0.0", pumpOUT:str="B0.0", medium2:str=conf["CetoniDevice"]["gas"], waste:str=conf["CetoniDevice"]["waste"], repeats:int=3):
    ''' This function provides the functionality to clean the density and viscosity meter and the NMR. Further applications will be the
    cleaning of the UV-Vis spectrometer, the mixing chip and other loops in the system. '''
    # TODO: Test this function!!! TODO: Pump all the remainders in the pumps to one pump and again to the waste in order to reduce the remaining amount of solvent.
    # TODO: improve the algorithm in order to use as little solvent as possible, but hinder it from remaining in the instrument.

    ## Check the input types
    inputTypes = {'pumpsDict':dict, 'valvesDict':dict, 'instrumenttype':str, 'medium1':str, 'pumpIN':str, 'pumpOUT':str, 'medium2':str, 'waste':str, 'repeats':int}
    typeCheckDict(inputTypes=inputTypes)

    instrumentIN = f"{instrumenttype}IN"
    instrumentOUT = f"{instrumenttype}OUT"
    # Instatiate a timer
    timer=qmixbus.PollingTimer(120000)
    # Get the relevant paths
    # Get the path from pumpIN through the instrument to pumpOUT
    pathIN = graph.findPath(pumpIN, instrumentIN)
    pathOUT = graph.findPath(instrumentOUT, pumpOUT)
    path = pathIN + pathOUT
    print(path)
    # Determine the volume and flow to operate with the given pumps
    vol = min(5.0, 2.*graph.getTotalQuantity(nodelist=path, quantity="dead_volume"), pumpsDict[pumpIN].get_volume_max(), pumpsDict[pumpOUT].get_volume_max()) 
    flow = min(pumpsDict[pumpIN].get_flow_rate_max()/5., pumpsDict[pumpOUT].get_flow_rate_max()/5.)
    # Clean first with medium1, then with medium2
    for medium in [medium1, medium2]:
        # Initialize the pumps
        pumpIN_new = pumpIN
        pumpOUT_new = pumpOUT
        # Find a path to aspirate the medium in pumpIN_new
        pathMI = graph.findPath(medium, pumpIN_new)
        # Switch the valves to aspirate the medium in pumpIN_new
        switchValves(nodelist=pathMI, valvesDict=valvesDict)
        # Aspirate the medium in pumpIN_new
        pumpsDict[pumpIN_new].set_fill_level(level=vol, flow=flow)
        # Wait for pumpIN_new to finish pumping
        timer.wait_until(pumpsDict[pumpIN_new].is_pumping, False)
        # Clean n times pumping the liquid between input and output
        for n in range(repeats):
            # Switch the valves according to path
            switchValves(nodelist=path, valvesDict=valvesDict)
            # Pump from pumpIN_new to pumpOUT_new
            pumpsDict[pumpIN_new].set_fill_level(level=0.0, flow=flow)
            pumpsDict[pumpOUT_new].set_fill_level(level=vol, flow=flow)
            # Wait until both pumps have finished pumping
            timer.wait_until(pumpsDict[pumpIN_new].is_pumping, False)
            timer.wait_until(pumpsDict[pumpOUT_new].is_pumping, False)
            # If it is not the last round
            if n != repeats-1:
                # Exchange input and output pumps
                pumpIN_new, pumpOUT_new = pumpOUT_new, pumpIN_new
            else:
                print(n)
                # Do not exchange input and output pumps
                pumpIN_new, pumpOUT_new = pumpIN_new, pumpOUT_new
            print(pumpIN_new, pumpOUT_new)
            # Find new paths for input and output
            pathIN = graph.findPath(pumpIN_new, instrumentIN)
            pathOUT = graph.findPath(instrumentOUT, pumpOUT_new)
            path = pathIN + pathOUT
            print(path)
        # Get a path from pumpOUT_new to the waste
        pathOW=graph.findPath(pumpOUT_new, waste)
        # Switch the valves according to pathOW
        switchValves(pathOW, valvesDict=valvesDict)
        # Dispense from pumpOUT_new to the waste
        pumpsDict[pumpOUT_new].set_fill_level(level=0.0, flow=flow)
        # Wait for the pump to finish pumping
        timer.wait_until(pumpsDict[pumpOUT_new].is_pumping, False)
    return True

def cleanAll(pumpsDict:dict, valvesDict:dict, medium1:str, intermediate:bool=True, medium2:str=conf["CetoniDevice"]["gas"], repeat:int=3):
    ''' This function cleans the full system. This means it cleans all aspirationpaths and dispense paths in the mixing region and additionally,
    it cleans all the loops going to analysis systems. '''
    # TODO: Test this function!!!

    ## Check the input types
    inputTypes = {'pumpsDict':dict, 'valvesDict':dict, 'medium1':str, 'intermediate':bool, 'medium2':str, 'repeat':int}
    typeCheckDict(inputTypes=inputTypes)

    all = ["densioVisco", "uvVis"]
    for inst in all:
        cleanInstrument(pumpsDict=pumpsDict, valvesDict=valvesDict, instrumenttype=inst, medium1=medium1, medium2=medium2, repeats=repeat)
    cleanMixingsystem(medium1=medium1, intermediate=intermediate, medium2=medium2, pumpsDict=pumpsDict, valvesDict=valvesDict, repeats=repeat)
    emptySyringes(pumps=pumpsDict, valves=valvesDict)
    goToRefPos(pumpsDict=pumpsDict, valvesDict=valvesDict, mode="end")
    return True

def switchValves(nodelist:list, valvesDict:dict, settings:dict={}, valvePositionDict:dict=CetoniDevice_driver.cetoni.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"])):
    ''' This function gets the valve positions required to realize a certain path and switches the valves accordingly. '''
    
    ## Check the input types
    inputTypes = {'nodelist':list, 'valvesDict':dict, 'settings':dict}
    typeCheckDict(inputTypes=inputTypes)
    # check valvePositionDict
    valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
    
    # Check, if the function is called with a list of nodes or a list of settings
    if len(settings) == 0:
        # If settings is an empty dict, get the valve settings from "graph.getValveSettings"
        valveSettings = graph.getValveSettings(nodelist, valvePositionDict)
    else:
        # If settings is given, use these settings
        valveSettings = settings
    print("Valves switched to the following positions: \n")
    # For every valve
    for valve in valveSettings.keys():
        if valve in valvePositionDict.keys():
            # Change the valve position according to the settings
            valvesDict[valve].switch_valve_to_position(valveSettings[valve])
            # Print how the valves are switched
            print(f"{valve}: {valvesDict[valve].actual_valve_position()}")

def fillSyringe(pump:pumpObj, volume:float, valvesDict:dict, reservoir:str, waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"], setup=conf["CetoniDeviceDriver"]["setup"], valvePositionDict:dict=conf["CetoniDeviceDriver"]["valvePositionDict"], simulateBalance:bool=conf["CetoniDeviceDriver"]["simulateBalance"]):
    ''' This function ensures that the syringe does not contain gas, but only liquid. '''
        
    ## Check the input types
    inputTypes = {'pump':pumpObj, 'volume':float, 'valvesDict':dict, 'reservoir':str, 'waste':str, 'flow':float, 'simulateBalance':bool}
    typeCheckDict(inputTypes=inputTypes)
    # check valvePositionDict
    valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
    # check setup
    setup = graph.getGraph(setup)
        
    print(flow)
    # Initialise a balance object
    bal = balance_driver.balance()
    # Save the current valve positions
    origValvePos = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    # Initialise the timer
    duration = (volume/flow)*1200
    timer = qmixbus.PollingTimer(period_ms=duration)
    # Find a path from the pump to the waste
    pathPW = graph.findPath(start_node=pump.name, end_node=waste, valvePositionDict=valvePositionDict, graph=setup)
    # Get the dead volume of the path from the pump to the waste
    deadVolPW = graph.getTotalQuantity(nodelist=pathPW, quantity="dead_volume")
    # Add two times the dead volume to the required volume as a buffer
    volumeWithBuffer = volume + 2.0 * deadVolPW
    # Check, if the pump is large enough to accommodate the volume including the buffer
    if  volumeWithBuffer < pump.get_volume_max():
        # If the syringe is large enough, set vol to the volume including the buffer
        vol = volumeWithBuffer
        print("VolumeWithBuffer",vol)
    else:
        # If the syringe is not large enough, use the full volume of the syringe
        vol = pump.get_volume_max()
        print("Volume max", vol)
    # Find a path from the reservoir to the pump
    pathRP = graph.findPath(start_node=reservoir, end_node=pump.name, valvePositionDict=valvePositionDict, graph=setup)
    # Switch the valves according to pathRP
    switchValves(nodelist=pathRP, settings={}, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    # Aspirate vol into the syringe
    pump.set_fill_level(level=vol, flow=flow)
    # Wait until the pump has finished pumping and wait some additional time to let the liquid flow
    print("Waiting")
    timer.restart()
    timer.wait_until(fun=pump.is_pumping, expected_result=False)
    timer2 = qmixbus.PollingTimer(period_ms=20000)
    timer2.wait_until(fun=timer2.is_expired, expected_result=True)
    # Switch the valves according to pathPW
    switchValves(nodelist=pathPW, settings={}, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    # Get the current volume in the syringe of the pump
    currentVol = pump.get_fill_level()
    print(currentVol)
    print(2.0*graph.getTotalQuantity(nodelist=pathPW, quantity="dead_volume"))
    # Dispense two times the dead volume of the path to the waste
    new_level = currentVol - 2.0*graph.getTotalQuantity(nodelist=pathPW, quantity="dead_volume")
    print(new_level)
    

    # FIXME: Not valid for the general case. Only for checkDefinition application
    if new_level < 0:
        new_level = currentVol



    pump.set_fill_level(level=new_level, flow=flow)
    # Wait until the pump has finished pumping
    print("Waiting2")
    timer.restart()
    print("starting timer")
    timer.wait_until(fun=pump.is_pumping, expected_result=False)
    print("done waiting")
    print(balance_action.readBalance(bal))
    # Initialise the balance readings list with the current reading of the balance
    readingsBalance = [balance_action.readBalance(bal)]
    print(readingsBalance)
    filling = pump.get_fill_level()
    # Set the limit for dispensing to 0.1*the volume contained in the syringe
    limit_level = filling*0.1
    # Start dispensing
    pump.set_fill_level(level=limit_level, flow=flow)
    # While the pump is pumping
    while pump.is_pumping():
        while len(readingsBalance) < 10:
            # Read the balance
            currentMass = balance_action.readBalance(bal)
            # Add the new value to the list of readings
            readingsBalance.append(currentMass)
        # Read the balance
        currentMass = balance_action.readBalance(bal)
        # Add the new value to the list of readings
        readingsBalance.append(currentMass)
        # Determine the gradient in a linear fit
        gradient = np.polyfit(x=range(10),y=readingsBalance[-10::],deg=1)[0]  #https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html
        print(gradient)
        # Check, if the gradient exceeds a threshold
        if gradient>0.003:
            # Stop pumping after certain increase is reached -> TODO: Add something to make sure that the dead volume is still pumped through the tube!!!
            pump.stop_pumping()
    # Check, if the pump stopped due to the lower volume limit
    if pump.get_fill_level() <= limit_level:
        # Print a message, if the lower limit was hit
        print("The syringe seems to be empty. Please check the cause for that.")
    # Get the current fill level of the pump
    filling_full = pump.get_fill_level()
    # Switch the valves back to the initial positions
    switchValves(nodelist=[], settings=origValvePos, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    # Return the fill level of the pump
    return filling_full # -> TODO: Define a deviation from the requested volume that is acceptable and repeat the process, if the fill level is lower.

def getVolFracs(fracs:tuple, labels:tuple, density:dict, molarMass:dict, mode:str="mole"):
    ''' This function calculates volume fractions from molar fractions. Further options will be available as needed. Implemented for ternary only! It negelects the mixing volume. '''
    # TODO: Test this function!!!
    
    ## Check the input types
    inputTypes = {'fracs':tuple, 'labels':tuple, 'density':dict, 'molarMass':dict, 'mode':str}
    typeCheckDict(inputTypes=inputTypes)
    
    fracs = dict(zip(labels, fracs))
    # Prepare a dataframe for the ratios of each relevant quantity
    empty = np.full((len(fracs), len(fracs)), fill_value=np.NaN)
    # Generate the dataframes
    moleRatios = pd.DataFrame(data=empty.copy(), columns=labels, index=labels)
    densityRatios = pd.DataFrame(data=empty.copy(), columns=labels, index=labels)
    massRatios = pd.DataFrame(data=empty.copy(), columns=labels, index=labels)
    # Get the positions of the relevant ratios
    permutations = list(it.permutations(labels, 2))
    # Fill the dataframes with the relevant ratios
    for p in permutations:
        # If the fraction would require to divide by zero, the value shall be set to NaN. Zero cannot be used, because this will lead to the calculation of the volume fraction to 1.0.
        try:
            moleRatios.loc[p[0], p[1]] = fracs[p[0]]/fracs[p[1]]
        except ZeroDivisionError:
            moleRatios.loc[p[0], p[1]] = np.nan
        densityRatios.loc[p[0], p[1]] = density[p[0]]/density[p[1]]
        massRatios.loc[p[0], p[1]] = molarMass[p[0]]/molarMass[p[1]]
    # Initialize dictionary to store the volume fractions
    volFracs = {}
    # Calculate the volume fractions
    volFracs[labels[0]] = 1./(moleRatios.loc[labels[2], labels[0]]*densityRatios.loc[labels[0], labels[2]]*massRatios.loc[labels[2],labels[0]] + 1. + moleRatios.loc[labels[1], labels[0]]*densityRatios.loc[labels[0], labels[1]]*massRatios.loc[labels[1],labels[0]])
    volFracs[labels[1]] = 1./(moleRatios.loc[labels[0], labels[1]]*densityRatios.loc[labels[1], labels[0]]*massRatios.loc[labels[0],labels[1]] + 1. + moleRatios.loc[labels[2], labels[1]]*densityRatios.loc[labels[1], labels[2]]*massRatios.loc[labels[2],labels[1]])
    volFracs[labels[2]] = 1./(moleRatios.loc[labels[1], labels[2]]*densityRatios.loc[labels[2], labels[1]]*massRatios.loc[labels[1],labels[2]] + 1. + moleRatios.loc[labels[0], labels[2]]*densityRatios.loc[labels[2], labels[0]]*massRatios.loc[labels[0],labels[2]])
    # Replace nan values by 0.0 in order to get numeric values for all volume fractions
    for key in volFracs.keys():
        volFracs[key] = np.nan_to_num(volFracs[key], nan=0.0)
    return volFracs

def provideSample(measurementtype:str, sample_node:str, pumps:dict, valves:dict, waste:str=conf["CetoniDevice"]["waste"]):
    ''' This function moves the sample to the requested device. '''
    # TODO: Test this function!!!
    
    ## Check the input types
    inputTypes = {'measurementtype':str, 'sample_node':str, 'pumps':dict, 'valves':dict, 'waste':str}
    typeCheckDict(inputTypes=inputTypes)
    
    # Find a path from the sample_node to the inlet of the device
    pathSIN = graph.findPath(start_node=sample_node, end_node=f"{measurementtype}IN")
    # Find a path from the outlet of the device to the waste
    pathOUTW = graph.findPath(start_node=f"{measurementtype}OUT", end_node=conf["CetoniDevice"]["waste"])
    # Assemble the total path
    pathTotal = pathSIN + pathOUTW
    # Check the validity of pathTotal and if it is valid, switch the valves accordingly
    if graph.pathIsValid(pathTotal):
        switchValves(nodelist=pathTotal, valvesDict=valves)
    else:
        print("ERROR: The total path is not valid.")
    ## Wait until the volume required for the measurement is pumped 1.5 times or the first pump stops pumping and stop the flow
    # Initialize a timer
    timer = qmixbus.PollingTimer(period_ms = 1.2 * 1000. *((graph.getTotalQuantity(nodelist=pathSIN, quantity="dead_volume") + conf["CetoniDevice"]["measureVolumes"][measurementtype])/conf["CetoniDeviceDriver"]["flow"]))
    print("volume to be pumped: ", graph.getTotalQuantity(nodelist=pathSIN, quantity="dead_volume") + conf["CetoniDevice"]["measureVolumes"][measurementtype])
    print(f"time to be waited: {timer.get_msecs_to_expiration()/1000.} s, {timer.get_msecs_to_expiration()/60000.} min")
    # Get the currently pumping pumps
    pumpingPs = CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict = pumps)
    # Wait and check the two conditions
    while not timer.is_expired() and pumpingPs == CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict=pumps):
        time.sleep(0.1)
    # Stop all pumps
    CetoniDevice_driver.pumpObj.stop_all_pumps()
    ## Wait a while for the liquid to get stable
    time.sleep(10)

def conductMeasurement(measurementtype:str, method:str, sampleName:str, sample:str, pumpsDict:dict, valvesDict:dict, waste:str=conf["CetoniDevice"]["waste"], gas:str=conf["CetoniDevice"]["gas"], flow:float=conf["CetoniDeviceDriver"]["flow"], repeat:int=2):
    ''' This function provides the functionalities required from the pumps and valves in order to supply the sample to an instrument for measurement. '''
    # TODO: Test this function!!!
    
    ## Check the input types
    inputTypes = {'measurementtype':str, 'method':str, 'sampleName':str, 'sample':str, 'pumpsDict':dict, 'valvesDict':dict, 'waste':str, 'gas':str, 'flow':float, 'repeat':int}
    typeCheckDict(inputTypes=inputTypes)
    
    # Get the dict containing the volume required for the respective measurement from the config file
    measureVols = conf["CetoniDevice"]["measureVolumes"]
    # Get the available volume of the sample
    sampleVol = pumpsDict[sample].get_fill_level()
    # Get the volume of sample needed for the measurement
    measureVol = measureVols[measurementtype]
    # Check, if the sample volume is sufficient
    if sampleVol >= measureVol:
        # For safety, set the status of sample pump to occupied
        pumpsDict[sample].status = "occupied"
        # All actions connected to the supported measurementtypes
        actions = {"densioVisco": densioVisco_action}#, "nmr": nmr_action, "uvVis": uvVis_action}
        # Instantiate a timer
        timer1 = qmixbus.PollingTimer(120000)
        # Check the requested experiment and define the input and output
        instrumentIN = f"{measurementtype}IN"
        instrumentOUT = f"{measurementtype}OUT"
        action = actions[measurementtype]
        # Find a path from the pump containing the sample to the input of the requested instrument
        pathSI = graph.findPath(start_node=sample, end_node=instrumentIN)
        # Get the fill level of sample pump
        level_sample = pumpsDict[sample].get_fill_level()
        # Determine the reqiured volume for the output pump. If the output pump has twice the volume of the sample, gas can be pumped through the cycle
        # to drain all the sample from the sample pump to the output pump
        volOUTrequired = 2.0 * level_sample
        # Find candidates, which are empty and have sufficient volume
        pumpOUT_candidates = graph.findPumps(pumpList=list(pumpsDict.keys()), pumps=pumpsDict, maximumVolume=f"target>={volOUTrequired}", status="target=='empty'")
        pumpOUT, pathOP = graph.findClosest(node=instrumentOUT, candidates=list(pumpOUT_candidates.keys()))
        # Set the status of pumpOUT to occupied
        pumpsDict[pumpOUT].status = "occupied"
        # Get the dead volume of pathSI, because it determines the volume the auxiliary pump needs to have
        dV_pathSI = graph.getTotalQuantity(nodelist=pathSI, quantity="dead_volume")
        # Find candidates for an auxiliary pump to supply gas to the sample pump
        pumpAssist_candidates = graph.findPumps(pumpList=list(pumpsDict.keys()), pumps=pumpsDict, maximumVolume=f"target>={dV_pathSI}", status="target=='empty'") # TODO: capture no sufficient pump available issue
        # Select the assistant pump closest to sample
        assist,  pathAS = graph.findClosest(node=sample, candidates=list(pumpAssist_candidates.keys()), direction="in")
        # Find a path from gas to pumpAssist
        pathGA = graph.findPath(start_node=gas, end_node=assist)
        # Switch the valves to pathGA
        switchValves(nodelist=pathGA, valveDict=valvesDict)
        # Aspirate the dV_pathSI to assist
        pumpsDict[assist].set_fill_level(level=dV_pathSI, flow=flow)
        # Wait for assist to stop pumping
        timer1.wait_until(pumpsDict[assist].is_pumping, False)
        # Combine the paths to get the path through the device
        path = pathSI + pathOP
        # Get the dead volume of the path
        dV_path = graph.getTotalQuantity(nodelist=path, quantity="dead_volume")
        print(path)
        # Switch the valves according to path
        switchValves(nodelist=path, valvesDict=valvesDict)
        
        
        ## Dispense the sample to the path
        # Get the fill levels of sample and out
        level_sample = pumpsDict[sample].get_fill_level()
        level_out = pumpsDict[pumpOUT].get_fill_level()
        # Dispense all the sample from sample to pumpOUT
        pumpsDict[sample].set_fill_level(level=0.0, flow=flow)
        pumpsDict[pumpOUT].set_fill_level(level=level_out+level_sample, flow=flow)
        # Wait for both pumps to finish pumping
        timer1.wait_until(pumpsDict[sample].is_pumping, False)
        timer1.wait_until(pumpsDict[pumpOUT].is_pumping, False)

    input("Please start the measurement and confirm, when it is done. After your confirmation, the sample will be withdrawn from the instrument.")


    ## Pull the sample out of the instrument
    # Find a path from gas to sample
    pathGS = graph.findPath(start_node=gas, end_node=sample)
    # Switch valves according to pathGS
    switchValves(nodelist=pathGS, valvesDict=valvesDict)
    # Aspirate gas to the sample pump
    pumpsDict[sample].set_fill_level(level=np.min([pumpsDict[sample].get_volume_max(), dV_path]), flow=flow)
    # Switch the valves back to path
    switchValves(nodelist=path, valvesDict=valvesDict)
    ## Dispense the gas through the instrument to pumpOUT
    # Get the fill levels of sample and out
    level_sample = pumpsDict[sample].get_fill_level()
    level_out = pumpsDict[pumpOUT].get_fill_level()
    # Dispense all the gas from sample to pumpOUT
    pumpsDict[sample].set_fill_level(level=0.0, flow=flow)
    pumpsDict[pumpOUT].set_fill_level(level=level_out+level_sample, flow=flow)
    # Wait for both pumps to finish pumping
    timer1.wait_until(pumpsDict[sample].is_pumping, False)
    timer1.wait_until(pumpsDict[pumpOUT].is_pumping, False)

    ## Readjust the fill level of pumpOUT
    # Find a path from pumpOUT to waste
    pathOW = graph.findPath(start_node=pumpOUT, end_node=waste)
    # Switch the valves according to pathOW
    switchValves(nodelist=pathOW, valvesDict=valvesDict)
    return True, pumpOUT

def goToRefPos(pumpsDict:dict, valvesDict:dict, mode:str, gas:str=conf["CetoniDevice"]["gas"], waste:str=conf["CetoniDevice"]["waste"]):
    ''' This function moves the syringes to their reference positions. This means that they move to 2 mL or half their size, depending on what is the smaller value. This
    is done before leaving the machine in order to have remaining fluid inside the syringes as much as possible and keeping it away from other components like valves, if
    it is avoidable. '''
    # TODO: Test this function!!!
    
    ## Check the input types
    inputTypes = {'pumpsDict':dict, 'valvesDict':dict, 'mode':str, 'gas':str, 'waste':str}
    typeCheckDict(inputTypes=inputTypes)
    
    timer = qmixbus.PollingTimer(120000)
    for p in list(pumpsDict.keys()):
        try:
            if mode == "end":
                level = np.min([2.0, pumpsDict[p].get_volume_max()/2.])
                print(level)
                path = graph.findPath(gas, p)
                print(path)
            elif mode == "start":
                level = 0.0
                path = graph.findPath(p, waste)
            switchValves(path, valvesDict=valvesDict)
            pumpsDict[p].set_fill_level(level, pumpsDict[p].get_flow_rate_max()/5.)
            timer.wait_until(pumpsDict[p].is_pumping, False)
        except (NodeNotFound, NetworkXNoPath) as e:
            pass
