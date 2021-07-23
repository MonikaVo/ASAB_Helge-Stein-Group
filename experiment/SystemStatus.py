#import os
import sys
sys.path.append(r"..")  # edited prior to publication
sys.path.append(r"...\QmixSDK\lib\python")  # edited prior to publication
from helpers import LoadFile, ListToDict
from hardware import graph, CetoniDevice
import networkx as nx
import numpy as np
from qmixsdk import qmixvalve, qmixpump, qmixbus

# ### Workaround helpers issue
# def LoadFile(loadFile):
#     ''' This function loads an object from a pickle file from the path stated as loadFile. '''
#     with open(loadFile, 'rb') as load_file:
#         out = pickle.load(load_file)
#     return out
# ###


''' This file needs to be called AFTER initialization of the ASAB hardware and start of the BUS communication. '''

# Set up a polling timer
timer = qmixbus.PollingTimer(600000)

# TODO: define flush to get defined status at start
def initialize_system():
    ''' This function is used to put the system into a defined status prior to a new experiment or after cancelation or error of an experiment. '''
    # Flush the system using a liquid or using the ambient gas. It depends on what is supplied to the specified inlet.
    flush(pathToFlush="full", cleaningAgent="V3.9", waste="V3.10",setup_path="hardware/setup.pck", mode="liquid")
    status = []

    return "System initialized."

# TODO: dict with tubing status
def get_systemStatus():
    pass

def flush(pathToFlush, cleaningAgent, waste, setup_path=r"hardware/setup.pck", mode="gas"):
    ''' This function flushes the system with a specified substance supplied to the given input node. The selection of the mode determines the
    status of the affected path after flushing. After flushing, the affected path is considered as filled with the respective cleaning agent.
    If pathToFlush=="full", the whole system is flushed. Else, the given path is flushed. cleaningAgent gives the node, at which the cleaning
    agent is available. The waste defines the node, where the cleaning agent shall be expelled. '''
    graph_setup, valvePositionDict = graph.loadGraph(setup_path)
    if type(pathToFlush)== str and pathToFlush == "full":
        # TODO: Find the shortest way in the graph covering all the nodes and flush this path.
        pass
    else:
        pathToFlush_processed = ListToDict(pathToFlush)
        # Check, if pathToFlush_processed includes the node, where the cleaing agent is available. If this is not the case, find a path, that does.
        if cleaningAgent not in pathToFlush_processed:
            # Find the nearest free pump from cleaningAgent, for which the path has the least dead volume
            #pumps_candidtates = []
            #for pump in Pumps.keys():
                #if status[pump]=="empty":
                    # pumps_candidtates.append(pump)
            pumpCleaning, path_CAToPumpCleaning = graph.findClosest(graph_setup, cleaningAgent, Pumps.keys(), "dead_volume", "out")
            
            # Find the nearest free pump from waste, for which the path has the least dead volume, and which is not the pump chosen for the cleaning agent
            pumpWaste, path_PumpWasteToWaste = graph.findClosest(graph_setup, waste, Pumps.keys(), "dead_volume", "in")


            # Select the direction of the flush based on the least dead volume. Compare distances from the chosen pumps to the starting and end node
            start = str(pathToFlush_processed[0])
            print("pumpCleaning{}".format(pumpCleaning))
            print("Path Cleaining", path_CAToPumpCleaning)
            print("type pumpWaste", type(pumpWaste))
            shortestCAPump_start = nx.dijkstra_path(graph_setup, pumpCleaning, "A0.0", "dead_volume")
            shortestCAPump_end = nx.dijkstra_path(graph_setup, pumpCleaning, pathToFlush_processed[-1], "dead_volume")
            shortestStart_wastePump = nx.dijkstra_path(graph_setup, pathToFlush_processed[0], pumpWaste, "dead_volume")
            shortestEnd_wastePump = nx.dijkstra_path(graph_setup, pathToFlush_processed[-1], pumpWaste, "dead_volume")

            # Select the combination of paths to waste and cleaningAgent, which has the lowest dead volume and the waste and the cleaningAgent
            # are not connected to the same node.
            CAPump_startWastePump_end = nx.dijkstra_path_length(shortestCAPump_start)+nx.dijkstra_path_length(shortestEnd_wastePump)
            CAPump_endWastePump_start = nx.dijkstra_path_length(shortestCAPump_end)+nx.dijkstra_path_length(shortestStart_wastePump)
            selection = min(CAPump_startWastePump_end, CAPump_endWastePump_start)

            #  Add the selected paths to pathToFlush_processed.
            path_CAToPumpCleaning = nx.dijkstra_path(graph_setup, cleaningAgent, pumpCleaning, "dead_volume").remove(pumpCleaning)
            path_PumpWasteToWaste = nx.dijkstra_path(graph_setup, pumpWaste, waste, "dead_volume")

            if selection==CAPump_startWastePump_end:
                path_PumpCleaningToStartFlush = nx.dijkstra_path(graph_setup, pumpCleaning, pathToFlush_processed[0], "dead_volume").remove(pathToFlush_processed[0])
                path_EndFlushToPumpWaste = nx.dijkstra_path(graph_setup, pathToFlush_processed[-1], pumpWaste,"dead_volume"). remove(pumpWaste)
                pathToFlush_new = path_CAToPumpCleaning + path_PumpCleaningToStartFlush + path_EndFlushToPumpWaste + path_PumpWasteToWaste
            elif selection==CA_endWaste_start:
                path_PumpCleaningToEndFlush = nx.dijkstra_path(graph_setup, pumpCleaning, pathToFlush_processed[-1], "dead_volume").remove(pathToFlush_processed[-1])
                path_StartFlushToPumpWaste = nx.dijkstra_path(graph_setup, pathToFlush_processed[0], pumpWaste,"dead_volume"). remove(pumpWaste)
                pathToFlush_new = path_CAToPumpCleaning + path_PumpCleaningToEndFlush + pathToFlush_processed.revese() + path_StartFlushToPumpWaste   # https://www.geeksforgeeks.org/python-reversing-list/
            else:
                print("No valid path to flush is found. Please make sure that the given setup is correct and that all input parameters are chosen correctly.")
            
            # Get the required settings for the valves to realize the path to be flushed
            valveSettings = graph.getValveSettings(pathToFlush_new)

            # Get the dead volume of the path and calculate the required cleaning volume based on that
            dead_volume = graph.getTotalQuantity(graph.getEdgedictFromNodelist(graph_setup, pathToFlush_new))

            # Determine the volume for one cleaning run
            volumeCleaning = dead_volume * 3.

            # Switch the valves according to pathToFlush_new
            for valve in ValveSettings.keys():
                Valves[valve].switch_valve_to_position(valveSettings[valve]) 

            

            # Select the free pump closest to the waste container.
            pumps_candidtates = []
            for pump in Pumps.keys():
                if status[pump]=="empty" and pump != pumpCleaning:
                    pumps_candidtates.append(pump)
            pumpWaste = graph.findClosest(graph_setup, pathToFlush_new[-1], pumps_candidtates, "dead_volume", "out")

            # Aspirate the required (or maximum) volume of cleaning agent. If syringe maximum is below required, repeat the process.
            remainingVolume = volumeCleaning
            if volumeCleaning > Pump[pumpCleaning].get_volume_max():
                while remainingVolume > Pump[pumpCleaning].get_volume_max():
                    Pumps[pumpCleaning].aspirate(Pump[pumpCleaning].get_volume_max())
                    timer.wait
                    Pumps[pumpCleaning].dispense(Pump[pumpCleaning].get_volume_max())
                    remainingVolume = remainingVolume - Pump[pumpCleaning].get_volume_max()
                Pumps[pumpCleaning].aspirate(remainingVolume)
            else:
                Pumps[pumpCleaning].aspirate(volumeCleaning)

            # Pump cleaning liquid through the path.

            # Repeat if several cleaning cycles are selected

            # TODO: Error handling in case of invalid path. Consider switching of valves to flush the path in several steps. Reuse for full flush.  

    if mode=="gas":
        pass
    elif mode=="liquid":
        pass
    else:
        print("ERROR: No flush mode was defined. Please define a flush mode.")

# TODO: define pumping as pumping+update of dict
def pumpAndUpdate():
    pass

def update():
    pass

# TODO: Check operability of flush routine.

#"C:\Users\MonikaVogler\Desktop\ASAB_Config1_sim"
#"W:\QmixSDK"
Pumps, Valves = CetoniDevice.prepareCetoni(r"...\ASAB_Config1_sim", r"...\QmixSDK")  # edited prior to publication
flush(['A0.0', 'A0.1', 'Av1', 'V1.1', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.1', 'Reservoir1'], "Reservoir2", "Reservoir3", mode="liquid")