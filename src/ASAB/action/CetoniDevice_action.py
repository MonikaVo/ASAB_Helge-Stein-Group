from ASAB.utility.helpers import importConfig
from pathlib import Path
import os

conf = importConfig(str(Path(__file__).stem))

from ASAB.configuration import config
cf = config.configASAB

## Imports from ASAB
from ASAB.utility.helpers import typeCheck
from ASAB.driver import CetoniDevice_driver, balance_driver
from ASAB.action import balance_action
from ASAB.utility import graph
from ASAB.driver.CetoniDevice_driver import getValvePositionDict, pumpObj
import ASAB.utility.solutionHandler as solutionHandler

## Imports from QmixSDK
import sys
sys.path.append(cf["QmixSDK_python"])
from qmixsdk import qmixbus
from qmixsdk.qmixbus import PollingTimer

## Other imports
from typing import Tuple, Union
import numpy as np
import networkx as nx
from networkx.exception import NodeNotFound, NetworkXNoPath
import time
import logging
import warnings

# create a logger for this module
logger_CetoniDevice_action = logging.getLogger(f"run_logger.{__name__}")

def prepareRun(graphSave:bool, graphShow:bool, refPos:bool) -> dict:
    """ This function prepares the Cetoni device and sets all the devices operational,
    generates a graph, the chemicalsDict and the solutionsDict.
    
    Inputs:
    graphSave: a boolean defining, whether the graph shall be saved
    graphShow: a boolean defining, whether the graph shall be displayed
    refPos: a boolean defining, whether the syringes shall close prior to other actions
    
    Outputs:
    restults: a dictionary summarizing the results (pumps, valves, channels, graph, positions,
    chemicalsDict, solutionsDict)
    """

    ## Check the input types
    typeCheck(func=prepareRun, locals=locals())

    # Generate the directory to save the inputs
    Path(conf["runFolder"]).joinpath("inputs").mkdir(parents=True, exist_ok=True)
    # Copy the inputs and the script
    for file in [
        conf["graph"]["pathNodes"],
        conf["graph"]["pathEdges"],
        conf["graph"]["pathTubing"],
        conf["solutionHandler"]["stockSolutions"],
        conf["solutionHandler"]["chemicals"],
        ]:
        filename = Path(file).name
        os.popen(f"copy {file} {str(Path(conf['runFolder']).joinpath('inputs', filename))}")


    # Prepare the Cetoni device
    pumps, valves, channels = CetoniDevice_driver.cetoni.prepareCetoni()
    # Generate the graph
    G, positions = graph.generateGraph(save=graphSave, show=graphShow)
    # If the refPos parameter is set to true, got to the start reference position
    if refPos:
        # Go to the reference position for the start
        goToRefPos(pumpsDict=pumps, valvesDict=valves, mode='start')
    # Generate the chemicalsDict and the solutionsDict
    chemicalsDict = solutionHandler.generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'])
    solutionsDict = solutionHandler.generate_solutionsDict(solutionsDef=conf['solutionHandler']['stockSolutions'], pumps=pumps, valves=valves)
    # Collect all the information in a dictionary and return it
    resultDict = {"pumps": pumps,
                  "valves": valves,
                  "channels": channels,
                  "graph": G,
                  "positions": positions,
                  "chemicalsDict": chemicalsDict,
                  "solutionsDict": solutionsDict}
    logger_CetoniDevice_action.info(f"{prepareRun.__name__}\n"
                                    "The setup is done. The following objects were created:\n"
                                    f"{resultDict}"
                                   )
    return resultDict 

def flushSyringe(pumps:dict, valves:dict, pump:str, reservoir:str, waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"], repeat:int=3) -> None:
    ''' This function flushes the syringe with the fluid, which will be aspirated in the syringe in order to dilute remainders from previous fluids
    and reduce cross-contaminations.
    
    Inputs:
    pumps: a dictionary containing all the pumps in the system with the names of the pumps as keys and the pump objects as values
    valves: a dictionary containing all the valves in the system with the names of the valves as keys and the valve objects as values
    pump: a string representing the name of the pump, which shall be flushed
    reservoir: a string specifying the reservoir, from which the liquid shall be aspirated
    waste: a string giving the name of the node corresponding to the the waste
    flow: a float indicating the flow to be used for the aspiration
    repeat: an integer indicating the number of iterations to use 

    Outputs:
    This function has no outputs. '''  

    ## Check the input types
    typeCheck(func=flushSyringe, locals=locals())   # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

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
        # Aspirate 15 % of the max. volume to the pump
        pumps[pump].set_fill_level(level=0.15*pumps[pump].get_volume_max(), flow=flow)
        # Wait until the pump has finished pumping
        timer.wait_until(pumps[pump].is_pumping, False)
        # Wait additional 10 seconds, because lower viscous liquids need more time to flow into the syringe
        time.sleep(10)
        # Switch valves according to pathPW
        switchValves(nodelist=pathPW, valvesDict=valves)
        # Dispense the content of the syringe to the waste
        pumps[pump].set_fill_level(level=0.0, flow=flow)
        # Wait until the pump has finished pumping
        timer.wait_until(pumps[pump].is_pumping, False)

def mix(mixingRatio:dict, fraction:str, pumps:dict, valves:dict, via:list=[],
        chemicalsDict:Union[str, dict, None]=conf['solutionHandler']['chemicalsDict'],
        solutionsDict:Union[str, dict, None]=conf['solutionHandler']['solutionsDict'],
        endpoint:str=conf["CetoniDevice"]["waste"],
        setup:Union[str,dict, nx.DiGraph]=conf["graph"]["savePath_graph"],
        flow:float=conf["CetoniDeviceDriver"]["flow"]) -> Tuple[dict, dict, dict, dict]:
    ''' This function mixes solutions from reservoirs according to the given mixing ratio. The mixing ratio must be given as fractions summing up to unity and the fraction
    parameter denotes, which kind of fraction is given. Currently volume fraction and morar fractions are accepted. For the mixing process, the mixing ratio is transformed
    to a volume fraction, if it is not already a volume fraction.

    Inputs:
    mixRatio: a dictionary representing the mixing ratio with the keys being the names of the stock solutions and the values being their volume fraction or the keys being
              names of chemicals with the values being their molar fractions. The values need to sum to unity in any case.
    fraction: a string specifying, whether the given mixing ratio is in volume fractions (volumePerVolume) or molar fractions (molPerMol); Use the string "direct" here to
              indicate, that the given ratio refers to volume fractions of stock solutions
    pumps: a dictionary containing all the pumps in the system with the names of the pumps as keys and the pump objects as values
    valves: a dictionary containing all the valves in the system with the names of the valves as keys and the valve objects as values
    via: a list of strings specifying nodes, which shall be passed on the way to the endpoint. This may be useful when wanting to mix the solution and directly have it in
         a device
    chemicalsDict: a dictionary containing chemical objects as values, or a string specifying the path to a chemicalsDict, or None to newly generate it
    solutionsDict: a dictionary containing solution objects as values, or a string specifying the path to a solutionsDict, or None to newly generate it
    Sendpoint: a string giving the name of a node, where the sample shall end up. This could be the waste or another node representing an additional reservoir, which can be reached.
    setup: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a file, which contains a dict[dict] describing the graph.
    flow: a float giving the total flow used for the experiment

    Outputs:
    mixRatio_request: a dictionary representing the requested mixing ratio
    mixRatio_vol: a dictionary representing the given or calculated mixing ratio in volume fractions of the stock solutions
    calcMix_request: a dictionary representing the mixing ratios as they result from the mixRatio_vol in molar fractions, if the mixing ratio was given in molar fracitons,
                   or an empty dictionary, if the mixing ratio was given in volume fractions '''

    # Check the input types
    typeCheck(func=mix, locals=locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    # Get the graph
    setup, positions = graph.getGraph(graph=setup, positions=None)

    # Get the chemicalsDict and the solutionsDict
    chemicalsDict = solutionHandler.get_chemicalsDict(chemicalsDict=chemicalsDict)
    if solutionsDict == None:
        solutionsDict = solutionHandler.generate_solutionsDict(solutionsDef=conf['solutionHandler']['stockSolutions'], pumps=pumps, valves=valves)
    solutionsDict = solutionHandler.get_solutionsDict(solutionsDict=solutionsDict)

    ## Check the mixing ratio and convert it to volume fractions, if it is not already given as volume fractions
    if fraction == 'direct':
        mixRatio_request = mixingRatio.copy()
        mixRatio_vol = mixingRatio.copy()
        calcMix_request = {}
        minSquaredError = 0.0
    elif fraction in ['molPerMol']: # TODO: expand this to account for other inputs
        mixRatio_request, mixRatio_vol, calcMix_request, minSquaredError = solutionHandler.get_fractions_2(mixingRatio=mixingRatio, chemicalsDict=chemicalsDict, solutionsDict=solutionsDict, input_fraction=fraction, output_fraction="volPerVol")

    logger_CetoniDevice_action.info(f"{mix.__name__} Mixing\n"
                                f"mixing ratio: {mixingRatio}\n"
                                f"fraction: {fraction}\n"
                                f"requested mixing ratio [mol/mol]:\t{mixRatio_request}\n"
                                f"volumetric mixing ratio [vol/vol]:\t{mixRatio_vol}\n"
                                f"calculated mixing ratio based on volumetric mixing ratio [mol/mol]:\t{calcMix_request}\n"
                                f"minimum squared error between the two:\n {minSquaredError}\n")


    ## Determine the flows required to get the mixture
    # Initialize a dict of flows
    flows = {}
    # Initialize a dict containing the evaluation of the flows, whether these are above the minimum and below the maximum
    # flow of the syringe
    flowsOK = {True: [], False: {}}
    mixRatio_vol_keys = list(mixRatio_vol.keys())
    for sol in mixRatio_vol_keys:
        # flows[stockSolutionsReservoirs[sol]] = mixRatio_vol[sol]*flow
        # Get the solution object
        solution = solutionsDict[sol]
        spumpName = solution.pump
        spump = pumps[spumpName]
        sreservoir = solution.reservoir
        print("\n Mixratio_vol:", mixRatio_vol, "\n Flow:", flow)
        if mixRatio_vol[sol]*flow > 0.0:
            # Add the flow to the flows dictionary using the related reservoir as key
            flows[sol] = mixRatio_vol[sol]*flow
            # Check, if the flow is ok and save the result to the flowsOK dictionary
            if (flows[sol] > spump.syringe.minimum_flow_mL_per_sec) and (flows[sol] < spump.syringe.maximum_flow_mL_per_sec):
                flowsOK[True].append(sol)
            elif not (flows[sol] > spump.syringe.minimum_flow_mL_per_sec):
                flowsOK[False][sol] = 'too low'
            elif not (flows[sol] < spump.syringe.maximum_flow_mL_per_sec):
                flowsOK[False][sol] = 'too high'
            else:
                raise ValueError(f"Something seems to be wrong with the flow for stock soltuion {sol}, which is {mixRatio_vol[sol]*flow} with the syringe lower limit {spump.syringe.minimum_flow_mL_per_sec} and higher limit {spump.syringe.maximum_flow_mL_per_sec}.")
            ## Fill the pump with its respective fluid
            # Find a path from the reservoir to the pump
            pathRP = graph.findPath(start_node=sreservoir, end_node=spumpName)
            # Switch valves according to pathRP
            switchValves(nodelist=pathRP, valvesDict=valves)
            # Fill the syringe up to maximum volume
            print("Filling syringe")
            print('solution', sol, 'flow', flows[sol])
            _ = fillSyringe(pump=spump, volume=spump.get_volume_max(), reservoir=sreservoir, valvesDict=valves)
            logger_CetoniDevice_action.info(f"{mix.__name__}\nSyringe filled. Solution: {sol}, flow: {flows[sol]}")
        else:
            del mixRatio_vol[sol]

    ## Check, that all flows are above the minimum flow of their syringe(future plan: adjust them otherwise and raise a Warning)
    if not (flowsOK[False] == {}):
        raise ValueError(f"The following flows are outside of the syringe limits: {flowsOK}")
        # TODO: Include the adjustment of the flows and raise warning below instead of the error above.
        # warnings.warn(f"The flows for the following reservoirs are wrong: {flowsOK}.", category=RuntimeWarning)

    # everything is working in mL per second as per standard, the units need to be changed based on the flow rates in mL/s and the values need to be adjusted
    # reverse the mapping of the unit prefixes in the QmixSDK with the respective exponents
    exp_prefix = dict([(qmixbus.UnitPrefix._member_map_[prefix].value, getattr(qmixbus.UnitPrefix, prefix)) for prefix in qmixbus.UnitPrefix._member_map_])
    print(exp_prefix)
    # get a list of the exponents related to prefixes and sort them in descending order to assure, that the highest exponents are first and no too small
    # unit is selected
    exp_list = list(exp_prefix.keys())
    exp_list.sort(reverse=True)

    # Collect the dead volume of each path to the endpoint in dV
    dV = []

    # for pu in involvedPumps:
    for sol in mixRatio_vol.keys():
        solution = solutionsDict[sol]
        spumpName = solution.pump
        spump = pumps[spumpName]
        # Find a path from pump to endpoint
        pathPE = graph.findPath(start_node=spumpName, end_node=endpoint, via=via)
        # Append the dead volume of pathPE to dV
        dV.append(graph.getTotalQuantity(nodelist=pathPE, quantity="dead_volume"))
        # Switch the valves according to pathPE
        switchValves(nodelist=pathPE, valvesDict=valves)
        ## Adjust the flow units according to the flows prior to generating the flow as the flow will not be set correctly, if the unit is not suitable
        # get the flow unit prior to the change and save it for later
        flow_unit_prior = spump.get_flow_unit()
        # remove the 'milli' prefix by multiplication by 10^-3
        flow_noPrefix = flows[sol]*(1e-3)
        print('flow', flows[sol], 'flow_noPrefix', flow_noPrefix)
        # find the prefix, which is suitable for the magnitude of the flow.
        if flow_noPrefix <= 10**(-7):
            unitPrefix = exp_prefix[-6]
            factor = 10**(3)
        elif (flow_noPrefix > 10**(-7)) and (flow_noPrefix <= 10**(-3)):
            unitPrefix = exp_prefix[-3]
            factor = 1.0
        elif (flow_noPrefix > 10**(-3)) and (flow_noPrefix <= 10**(-2)):
            unitPrefix = exp_prefix[-2]
            factor = 10**(-1)
        elif (flow_noPrefix > 10**(-2)) and (flow_noPrefix <= 10**(-1)):
            unitPrefix = exp_prefix[-1]
            factor = 10**(-2)
        elif flow_noPrefix > 10**(-1):
            unitPrefix = exp_prefix[0]
            factor = 10**(-3)

        setFlow = flows[sol] * factor
        spump.set_flow_unit(unitPrefix, flow_unit_prior.unitid, flow_unit_prior.time_unitid)
        print('flow_unit_prior', flow_unit_prior)
        print('newFlowUnit', spump.get_flow_unit())
        # Generate the flow required for the respective reservoir working with the temporarily changed flow unit; the value is adjusted according to the flow unit
        print('flow', flows[sol], 'setflow', setFlow)
        spump.generate_flow(setFlow)
    
    # Wait for 3 seconds
    timer2 = qmixbus.PollingTimer(period_ms = 3000.)
    timer2.wait_until(timer2.is_expired, True)

    # Return to mL/s flow units to revert to standard settings
    spump.set_flow_unit(prefix=flow_unit_prior.prefix, volume_unit=flow_unit_prior.unitid, time_unit=flow_unit_prior.time_unitid)

    # Collect the actual flows
    logmsg = []
    flows_actual = {}
    pumpsFlows = {}
    for sol in flows.keys():
        solutionPump = solutionsDict[sol].pump
        flows_actual[sol] = pumps[solutionPump].get_flow_is()
        pumpsFlows[solutionPump] = flows_actual[sol]
        print('actual flow', pumps[solutionPump].get_flow_is())
        print('target flow', flows[sol])
        logmsg.append(f"{sol}: \n actual flow: {pumps[solutionPump].get_flow_is()} \n target flow as calculated: {flows[sol]}")
    logmsg = "\n".join(logmsg)
    logger_CetoniDevice_action.info(f"{mix.__name__}\n{logmsg}")
    logger_CetoniDevice_action.info(f"{mix.__name__} Results"
                                    f"requested mixing ratio [mol/mol]:\t{mixRatio_request}\n"
                                    f"volumetric mixing ratio [vol/vol]:\t{mixRatio_vol}\n"
                                    f"calculated mixing ratio based on volumetric mixing ratio [mol/mol]:\t{calcMix_request}\n"
                                    f"minimum squared error between the input and the calculated values: {minSquaredError}\n"
                                    f"actual flows as set: {flows_actual}\n"
                                    f"total flow: {flow}"
                                    )

    # Stop the pumps to hinder dripping of the system when providing the sample
    # to a device
    CetoniDevice_driver.pumpObj.stop_all_pumps()
    return mixRatio_request, mixRatio_vol, calcMix_request, flows_actual, pumpsFlows

def provideSample(
                measurementtype:Union[str,None],
                sample_node:str,
                pumpsFlows:dict,
                pumps:dict,
                valves:dict,
                volume:Union[float,None]=None,
                endpoint:str=conf["CetoniDevice"]["waste"]
                ) -> dict:
    ''' This function moves the sample to the requested device.
    
    Inputs:
    measurementtype: a string specifying the device, to which the sample shall be supplied, e.g. densiVisco, nmr, uvVis
    volume: a float giving the volume to be pumped in mL; this is only used, if the measurementtype is None
    sample_node: a string giving the name of the node, from where the sample shall be directed towards the device
    pumpsFlows: a dictionary containing all the flows to be set when providing the 
                sample; keys are names of pumps, values are the flows
    pumps: a dictionary containing all the pumps in the system with the names of the pumps as keys and the pump objects as values
    valves: a dictionary containing all the valves in the system with the names of the valves as keys and the valve objects as values
    endpoint: a string giving the name of a node, where the sample shall end up. This could be the waste or another node representing an additional reservoir, which can be reached.

    Outputs:
    actualFlows: a dictionary containing the actual flow for each pump. The key is the
                name fo the pump and the value is the flow. '''
    
    ## Check the input types
    typeCheck(func=provideSample, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    if measurementtype is not None:
        # Find a path from the sample_node to the endpoint via the device
        path = graph.findPath(start_node=sample_node, end_node=endpoint,
                                via=[f"{measurementtype}IN", f"{measurementtype}OUT"])
        # Get only the part to the inlet of the instrument for later determination of
        # the waiting time
        pathSIN = graph.findPath(start_node=sample_node, end_node=f"{measurementtype}IN")
    else:
        # Find a path from the sample_node to the endpoint
        path = graph.findPath(start_node=sample_node, end_node=endpoint, weight="length")
        
    # Switch the valves to the path from the sample point to the endpoint if applicable through the device
    switchValves(nodelist=path, valvesDict=valves)
    ## Switch the valves from the pumps, which are involved, to the sample_node
    # to provide the sample to the endpoint
    for p in pumpsFlows.keys():
        # find a path from the pump to the sample_node
        pathPN = graph.findPath(start_node=p, end_node=sample_node)
        # switch the valves for this pump so that it pumps towards the sample_node
        switchValves(nodelist=pathPN, valvesDict=valves)
    # Restart the pumps and collect their flows to report them
    actualFlows = {}
    for pump in pumpsFlows.keys():
        pumps[pump].generate_flow(pumpsFlows[pump])
        actualFlows[pump] = pumps[pump].get_flow_is()

    ## Wait until the volume required for the measurement is pumped or the
    # first pump stops pumping and stop all pumps
    if measurementtype is not None:
        volToPump = (graph.getTotalQuantity(nodelist=pathSIN, quantity="dead_volume") +
                    conf["CetoniDevice"]["measureVolumes"][measurementtype])
    else:
        volToPump = (graph.getTotalQuantity(nodelist=path, quantity="dead_volume") +
                    volume)

    # Initialize a timer
    timeToWait = (volToPump)/conf["CetoniDeviceDriver"]["flow"]
    timer = qmixbus.PollingTimer(period_ms = 1000. * timeToWait)
    print("volume to be pumped: ", volToPump)
    print(f"time to be waited: {timer.get_msecs_to_expiration()/1000.} s, {timer.get_msecs_to_expiration()/60000.} min")
    logger_CetoniDevice_action.info(f"{provideSample.__name__}\nProviding sample to {measurementtype}, endpoint: {endpoint}"
                                    f"volume to be pumped: {volToPump}\n"
                                    f"time to be waited: {timer.get_msecs_to_expiration()/1000.} s, {timer.get_msecs_to_expiration()/60000.} min")
    # Wait and check the two conditions
    while ((not timer.is_expired()) and
        (all(
            [pumpKey in
            CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict=pumps)
            for pumpKey in list(pumpsFlows.keys())
            ]))):
        time.sleep(0.1)

    # Stop all pumps
    CetoniDevice_driver.pumpObj.stop_all_pumps()
    # drain the residues from the path, if the sample was not provided to a device
    if measurementtype is None:
        pathPGtoSampleNode = graph.findPath(start_node="pressurizedGas", end_node=sample_node)
        pathAmbienttoSampleNode = graph.findPath(start_node="ambient", end_node=sample_node)
        switchValves(nodelist=path, valvesDict=valves)
        for i in range(3):
            switchValves(nodelist=pathPGtoSampleNode, valvesDict=valves)
            time.sleep(2.)
            switchValves(nodelist=pathAmbienttoSampleNode, valvesDict=valves)
            time.sleep(1.)

    ## Wait a while for the liquid to get stable
    time.sleep(10)
    return actualFlows


def drainSample(measurementtype:str, pump:str, repeats:int, pumps:dict, valves:dict, gas:str=conf["CetoniDevice"]["gas"], waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"]):
    ''' This function drains the sample from a device to the waste after measurement. '''
    # TODO: Test this function

    ## Check the input types
    typeCheck(func=drainSample, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    # find a path from gas to pump
    pathGP = graph.findPath(start_node=gas, end_node=pump)
    # find a path from the pump to through the device to the waste
    pathPW = graph.findPath(start_node=pump, end_node=waste, via=[f'{measurementtype}IN', f'{measurementtype}OUT'])
    # repeat n times
    for n in range(repeats):
        # switch valves to pathGP
        switchValves(nodelist=pathGP, valvesDict=valves)

        # aspirate the maximum volume of gas to the pump
        pumps[pump].set_fill_level(pumps[pump].get_volume_max(), flow)
        # wait for the pump to finish pumping
        timer = PollingTimer(period_ms=300000)
        timer.wait_until(pumps[pump].is_pumping, False)
        # switch the valves to pathPW
        switchValves(nodelist=pathPW, valvesDict=valves)
        # dispense the gas
        pumps[pump].set_fill_level(0.0, flow)
        # wait for the pump to finish pumping
        timer = PollingTimer(period_ms=300000)
        timer.wait_until(pumps[pump].is_pumping, False)
    logger_CetoniDevice_action.info(f"{drainSample.__name__}\nSample drained from device {measurementtype}.")

def switchValves(nodelist:list, valvesDict:dict, settings:dict={}, valvePositionDict:Union[dict,str]=conf["CetoniDeviceDriver"]["valvePositionDict"]):
    ''' This function gets the valve positions required to realize a certain path and switches the valves accordingly. '''
    ## Check the input types
    typeCheck(func=switchValves, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    # Get the valvePositionDict
    valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
    
    # Check, if the function is called with a list of nodes or a list of settings
    if len(settings) == 0:
        # If settings is an empty dict, get the valve settings from "graph.getValveSettings"
        valveSettings = graph.getValveSettings(nodelist, valvePositionDict)
    else:
        # If settings is given, use these settings
        valveSettings = settings
    print("\nValves switched to the following positions:")
    logmsg = ["Valves switched to the following positions:"]
    # For every valve
    for valve in valveSettings.keys():
        if valve in valvePositionDict.keys():
            # Change the valve position according to the settings
            valvesDict[valve].switch_valve_to_position(valveSettings[valve])
            # Print how the valves are switched
            print(f"\t{valve}: {valvesDict[valve].actual_valve_position()}")
            logmsg.append(f"{valve}: {valvesDict[valve].actual_valve_position()}")
    logmsg = "\n".join(logmsg)
    logger_CetoniDevice_action.info(f"{switchValves.__name__}\npath\t{nodelist}\n\n{logmsg}")

def fillSyringe(pump:pumpObj, volume:float, valvesDict:dict, reservoir:str, tolerance:float=3.,  waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"], setup:str=conf["graph"]["savePath_graph"], valvePositionDict:str=conf["CetoniDeviceDriver"]["valvePositionDict"], simulateBalance:bool=conf["CetoniDeviceDriver"]["simulateBalance"]):
    ''' This function ensures that the syringe does not contain gas, but only liquid. '''
        
    ## Check the input types
    typeCheck(func=fillSyringe, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    logger_CetoniDevice_action.info(msg=f"{fillSyringe.__name__}\nFilling syringe {pump.name} from {reservoir}")

    # Get the valvePositionDict
    valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
    # Get the setup
    setup, positions = graph.getGraph(graph=setup, positions=None)
        
    # Initialise a balance object
    bal = balance_driver.balance()
    # Save the current valve positions
    origValvePos = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    # Initialise the timer
    duration = (volume/flow) * 1000 * 1.2
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
    # initialize filling_full
    filling_full = 0.0
    # As long as the syringe is not sufficiently filled, repeat the process of filling and dispensing liquid.
    while filling_full < volume-tolerance:
        # Switch the valves according to pathRP
        switchValves(nodelist=pathRP, settings={}, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
        # Aspirate vol into the syringe
        pump.set_fill_level(level=vol, flow=flow)
        # Wait until the pump has finished pumping and wait some additional time to let the liquid flow
        print("Waiting")
        timer.restart()
        timer.wait_until(fun=pump.is_pumping, expected_result=False)
        timer2 = qmixbus.PollingTimer(period_ms=200000)
        timer2.wait_until(fun=timer2.is_expired, expected_result=True)
        # Switch the valves according to pathPW
        switchValves(nodelist=pathPW, settings={}, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
        # Get the current volume in the syringe of the pump
        currentVol = pump.get_fill_level()
        # Dispense two times the dead volume of the path to the waste
        new_level = currentVol - 2.0*graph.getTotalQuantity(nodelist=pathPW, quantity="dead_volume")
        pump.set_fill_level(level=new_level, flow=flow)
        # Wait until the pump has finished pumping
        print("Waiting2")
        timer.restart()
        print("starting timer")
        timer.wait_until(fun=pump.is_pumping, expected_result=False)
        print("done waiting")
        # Initialise the balance readings list with the current reading of the balance
        readingsBalance = [balance_action.readBalance(bal)]
        filling = pump.get_fill_level()
        # Set the limit for dispensing to 0.1*the volume contained in the syringe
        limit_level = filling*0.1
        # Start dispensing
        pump.set_fill_level(level=limit_level, flow=flow)
        # While the pump is pumping
        while pump.is_pumping():
            while len(readingsBalance) < 50:
                # Read the balance
                currentMass = balance_action.readBalance(bal)
                # Add the new value to the list of readings
                readingsBalance.append(currentMass)
            # Read the balance
            currentMass = balance_action.readBalance(bal)
            # Add the new value to the list of readings
            readingsBalance.append(currentMass)
            # Determine the gradient in a linear fit
            gradient = np.polyfit(x=range(30),y=readingsBalance[-30::],deg=1)[0]  #https://numpy.org/doc/stable/reference/generated/numpy.polyfit.html
            print(gradient) # Consider using print(f"\033[K {gradient} \r") https://stackoverflow.com/questions/45263205/python-how-to-print-on-same-line-clearing-previous-text to not explode the output
            # Check, if the gradient exceeds a threshold
            if gradient>0.003:
                # Stop pumping after certain increase is reached -> TODO: Add something to make sure that the dead volume is still pumped through the tube!!!
                pump.stop_pumping()
        # Check, if the pump stopped due to the lower volume limit
        if pump.get_fill_level() <= limit_level:
            # Print a message, if the lower limit was hit
            raise ValueError(
                f"The syringe of pump {pump.name} seems to be empty. "
                "Please check the cause for that. "
                f"Likely reservoir {reservoir} is empty.")
        # Get the current fill level of the pump
        filling_full = pump.get_fill_level()

    # Switch the valves back to the initial positions
    switchValves(nodelist=[], settings=origValvePos, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    logger_CetoniDevice_action.info(f"{fillSyringe.__name__}\nSyringe filled up to the level {filling_full}.")
    # Return the fill level of the pump
    return filling_full

def goToRefPos(pumpsDict:dict, valvesDict:dict, mode:str,
               gas:str=conf["CetoniDevice"]["gas"],
               waste:str=conf["CetoniDevice"]["waste"],
               flow:float=conf["CetoniDeviceDriver"]["flow"]):
    ''' This function moves the syringes to their reference positions. This means that
    they move to 2 mL or half their size, depending on what is the smaller value. This
    is done before leaving the machine in order to have remaining fluid inside the
    syringes as much as possible and keeping it away from other components like valves,
    if it is avoidable. '''
    # TODO: add a check to ensure, that paths are not affecting each other
    
    ## Check the input types
    typeCheck(func=goToRefPos, locals=locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    
    for p in list(pumpsDict.keys()):
        levelNow = pumpsDict[p].get_fill_level()
        try:
            if mode == "end":
                level = np.min([2.0, pumpsDict[p].get_volume_max()/2.])
                path = graph.findPath(gas, p)
            elif mode == "start":
                level = 0.0
                path = graph.findPath(p, waste)
            levelDifference = level - levelNow
            directionality = graph.getDirectionality(path=path, node=p)
            if (((directionality == "in") and (levelDifference >= 0))
                or ((directionality == "out") and (levelDifference <= 0))):
                switchValves(nodelist=path, valvesDict=valvesDict)
            elif ((directionality == "in") and (levelDifference < 0)):
                correctedPath_in = graph.findPath(start_node=p, end_node=waste)
                switchValves(nodelist=correctedPath_in, valvesDict=valvesDict)
            elif ((directionality == "out") and (levelDifference > 0)):
                correctedPath_out = graph.findPath(start_node=gas, end_node=p)
                switchValves(nodelist=correctedPath_out, valvesDict=valvesDict)
            pumpsDict[p].set_fill_level(level, flow)
        except (NodeNotFound, NetworkXNoPath) as e:
            print(e)
            pass
    # One time waiting is enough as now each pump has its own waste and gas line
    # It needs to be waited until the last pump (the pump with the largest volume change
    # to do is done pumping)
    while len(CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict = pumpsDict)) > 0:
        time.sleep(0.1)

def singlePumpClean(pumpsPathsDict:dict, medium:str, pumpsDict:dict, valvesDict:dict,
                    goToRef:bool=True, repeats:int=3,
                    flow:float=conf["CetoniDeviceDriver"]["flow"],
                    setup:str=conf["graph"]["savePath_graph"]) -> Tuple[list,list]:
    ''' This function allows to clean paths using a single pump drivign the flow.
    
    Inputs:
    pumpsPathsDict: a dictionary with the names of pumps as keys and the path to clean
    with this pump as a value
    medium: the name of a node, from where the cleaning medium shall be aspirated
    pumpsDict: a dictionary containing the names of the pumps as keys and the pump
    objects present in the setup as values
    valvesDict: a dictionary containing valve names as keys and valves as values
    goToRef: a boolean specifying, whether all pumps in the system shall go to the
    start position (piston all the way in) prior to starting the cleaning
    repeats: an integer defining the number of cleaning cycles
    flow: a floating point number defining the volume flow to be used in the system
    during the cleaning
    setup: a string, dictionary, or a graph object representing the graph to be used
    to determine the paths

    Outputs:
    pathsNotCleaned: a list of the paths, which were not cleaned
    pathsCleaned: a list of the paths, which were cleaned '''


    # Check the input types
    typeCheck(func=singlePumpClean, locals=locals())

    # Initialize a timer
    timer = PollingTimer(period_ms=60000)

    # Get the graph
    setup, pos = graph.getGraph(graph=setup, positions=None)

    # Go to the reference position, if this is requested
    if goToRef:
        goToRefPos(pumpsDict=pumpsDict, valvesDict=valvesDict, mode="start")

    if not graph.pathsCompatible(pathsList=list(pumpsPathsDict.values())):
        raise ValueError("The paths are not compatible and cannot be cleaned in one"
                         "step. Please request them in separate groups.")

    # check, if the requested medium is gas or not
    nodesWithGas = [conf["CetoniDevice"]["gas"], "pressurizedGas"]
    mediumNoGas = medium not in nodesWithGas
    logger_CetoniDevice_action.info(f"{singlePumpClean.__name__} \n"
                                    f"Medium is not a gas: {mediumNoGas}")

    # Find all the open ends in the graph
    openEnds = graph.getOpenEnds(graph=setup)
    # Filter out pumps, the medium itself and nodes connected to gas
    openEndsReduced = [oE for oE in openEnds if (
                                    (oE not in pumpsDict.keys())
                                    and (oE != medium)
                                    and (oE not in nodesWithGas))]
    # If the medium is not gas, also filter out the open ends at valves to
    # avoid pumping solvent to these ends
    if mediumNoGas:
        openEndsReduced = [oeNoGas for oeNoGas in openEndsReduced
                            if ((type(graph.getValveFromName(oeNoGas))!=str))]
    # Collect the not cleaned paths
    pathsNotCleaned = []
    # Collect the cleaned paths
    pathsCleaned = []
    # Restructure the pumpsPathsDict so it can also store the path from the medium to
    # the pump
    pumpsPaths = {}
    for k in pumpsPathsDict.keys():
        pumpsPaths[k] = {"path": pumpsPathsDict[k]}

    for i in range(repeats):
        print(f"\n\n single pump clean {i+1}/{repeats} \n\n")
        for pump in pumpsPathsDict.keys():
            # find a path to aspirate the medium
            pathMP = graph.findPath(medium, pump)
            pumpsPaths[pump]["mediumPath"] = pathMP
            logger_CetoniDevice_action.info(f"{singlePumpClean.__name__}\n"
                                            f"Repeat: {i+1}/{repeats}\n"
                                            f"Pump: {pump}\n"
                                            f"Path from medium to pump: {pathMP}")
            originalPath = pumpsPaths[pump]["path"]
            # ensure, that the final node of the path is not an open end or if it is,
            # the open end is a waste
            # This is redundant when this function is called from clean, but it is
            # relevant, if the function is used independently of clean
            if mediumNoGas:
                lastNode = originalPath[-1]
                if (("waste" not in lastNode) and ("Reservoir" not in lastNode)):
                    try:
                        pathImproved = graph.findPath(start_node=pump,
                                            end_node=conf["CetoniDevice"]["waste"],
                                            via=pumpsPaths[pump]["path"],
                                            graph=setup)
                        warnings.warn(f"The path {originalPath} is changed to end in a "
                                "waste. The following path will be cleaned instead: "
                                f"{pathImproved}.")
                    except NetworkXNoPath:
                        warnings.warn(f"The path {originalPath} does not end in "
                                        "a waste. Changing it to end in "
                                        f"{conf['CetoniDevice']['waste']} "
                                        "was not successful. Trying to change it "
                                        "to end in an open end at a reservoir or "
                                        "another waste.")
                        try:
                            oEcands = [oec for oec in openEndsReduced
                                    if (("waste" in oec) or ("Reservoir" in oec))]
                            closestOpenEnd, pathToClosestOpenEnd = graph.findClosest(
                                                                    node=lastNode,
                                                                    candidates=oEcands,
                                                                    graph=setup)
                            pathImproved = graph.findPath(start_node=pump,
                                            end_node=closestOpenEnd,
                                            via=pumpsPaths[pump]["path"],
                                            graph=setup)
                            warnings.warn(f"The path {originalPath} is changed "
                                        f"to end in {closestOpenEnd} and is now "
                                        f"{pathImproved}.")
                        except NetworkXNoPath:
                            pathImproved = None
                            pathsNotCleaned.append(originalPath)
                            warnings.warn(f"The path {originalPath} does not "
                                            "end in a waste or a reservoir. "
                                            "Changing it to end in a waste or "
                                            "an appropriate open end was not "
                                            "successful. It will be skipped.")
                    pumpsPaths[pump]["path"] = pathImproved
            logger_CetoniDevice_action.info(f"{singlePumpClean.__name__}\n"
                                            "Path to clean: "
                                            f"{pumpsPaths[pump]['path']}")
            # switch the valves to the medium
            switchValves(pumpsPaths[pump]["mediumPath"], valvesDict=valvesDict)
            # aspirate the medium
            if mediumNoGas:
                dV = graph.getTotalQuantity(nodelist=pumpsPaths[pump]["path"],
                                            quantity="dead_volume")
                if dV*1.5 <= pumpsDict[pump].get_volume_max():
                    level = max(dV*1.5, 0.3)
                else:
                    level = pumpsDict[pump].get_volume_max()
            else:
                level = pumpsDict[pump].get_volume_max()
            print("volume_to_aspirate:", level)
            pumpsDict[pump].set_fill_level(level, flow=flow)
        # wait until the last pump is finished pumping
        while len(CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict = pumpsDict)) > 0:
            time.sleep(0.1)
        # wait longer, if the medium is not a gas
        if mediumNoGas:
            timer.wait_until(timer.is_expired, True)
        for pump in pumpsPaths.keys():
            # switch the valves to the path, which needs to be cleaned
            switchValves(pumpsPaths[pump]["path"], valvesDict=valvesDict)
            # dispense the medium
            pumpsDict[pump].set_fill_level(0.0, flow=flow)
            pathsCleaned.append(pumpsPaths[pump]["path"])
        # wait until the last pump is done pumping
        while len(CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict = pumpsDict)) > 0:
            time.sleep(0.1)
    return pathsNotCleaned, pathsCleaned

def multiPumpClean(path:list, medium:str, pumpsDict:dict, valvesDict:dict,
                   pumps:Union[list,None]=None, goToRef:bool=True, repeats:int=3,
                   flow:float=conf["CetoniDeviceDriver"]["flow"],
                   setup:str=conf["graph"]["savePath_graph"]) -> Tuple[list, list]:
    ''' This function enables the cleaning of a path using multiple pumps. This is
    mainly aimed for cleaning of instruments.
    
    Inputs:
    path: a list of strings specifying the path to be cleaned. The path needs to start
    at a node, which can be reached by all pumps
          listed in the pumps parameter at the same time (without switching a valve
          away from another pump).
    medium: the name of a node, from where the cleaning medium shall be aspirated
    pumps: a list of strings of pump names defining, which pumps shall be used for
    the cleaning
    pumpsDict: a dictionary containing the names of the pumps as keys and the pump
    objects present in the setup as values
    valvesDict: a dictionary containing valve names as keys and valves as values
    goToRef: a boolean specifying, whether all pumps in the system shall go to the
    start position (piston all the way in) prior to starting the cleaning
    repeats: an integer defining the number of cleaning cycles
    flow: a floating point number defining the volume flow to be used in the system
    during the cleaning
    setup: a string, dictionary, or a graph object representing the graph to be used
    to determine the paths

    Outputs:
    pathsNotCleaned: a list of the paths, which were not cleaned
    pathsCleaned: a list of the paths, which were cleaned '''

    # Check the input types
    typeCheck(func=multiPumpClean, locals=locals())

    # Initialize two timers
    timer = PollingTimer(period_ms=60000)

    # Get the graph
    setup, pos = graph.getGraph(graph=setup, positions=None)

    # Go to the reference position, if this is requested
    if goToRef:
        goToRefPos(pumpsDict=pumpsDict, valvesDict=valvesDict, mode="start")

    # check, if the requested medium is gas or not
    nodesWithGas = [conf["CetoniDevice"]["gas"], "pressurizedGas"]
    mediumNoGas = medium not in nodesWithGas
    logger_CetoniDevice_action.info(f"{multiPumpClean.__name__} \n Medium is not a gas: {mediumNoGas}")

    # Find all the open ends in the graph
    openEnds = graph.getOpenEnds(graph=setup)
    # Filter out pumps, the medium itself and nodes connected to gas
    openEndsReduced = [oE for oE in openEnds if (
                                    (oE not in pumpsDict.keys())
                                    and (oE != medium)
                                    and (oE not in nodesWithGas))]
    # If the medium is not gas, also filter out the open ends at valves to
    # avoid pumping solvent to these ends
    if mediumNoGas:
        openEndsReduced = [oeNoGas for oeNoGas in openEndsReduced
                            if ((type(graph.getValveFromName(oeNoGas))!=str))]

    pathsCleaned = []
    pathsNotCleaned = []

    if mediumNoGas:
        # ensure, that the final node of the path is not an open end or if it is,
        # the open end is a waste
        # This is redundant when this function is called from clean, but it is
        # relevant, if the function is used independently of clean
        lastNode = path[-1]
        if (("waste" not in lastNode) and ("Reservoir" not in lastNode)):
            try:
                pathImproved = graph.findPath(start_node=path[0],
                                    end_node=conf["CetoniDevice"]["waste"],
                                    via=path[1:],
                                    graph=setup)
                warnings.warn(f"The path {path} is changed to end in a "
                        "waste. The following path will be cleaned instead: "
                        f"{pathImproved}.")
            except NetworkXNoPath:
                warnings.warn(f"The path {path} does not end in "
                                "a waste. Changing it to end in "
                                f"{conf['CetoniDevice']['waste']} "
                                "was not successful. Trying to change it "
                                "to end in an open end at a reservoir or "
                                "another waste.")
                try:
                    oEcands = [oec for oec in openEndsReduced
                            if (("waste" in oec) or ("Reservoir" in oec))]
                    closestOpenEnd, pathToClosestOpenEnd = graph.findClosest(
                                                            node=lastNode,
                                                            candidates=oEcands,
                                                            graph=setup)
                    pathImproved = graph.findPath(start_node=path[0],
                                    end_node=closestOpenEnd,
                                    via=path[1:],
                                    graph=setup)
                    warnings.warn(f"The path {path} is changed "
                                f"to end in {closestOpenEnd} and is now "
                                f"{pathImproved}.")
                except NetworkXNoPath:
                    pathImproved = None
                    pathsNotCleaned.append(path)
                    warnings.warn(f"The path {path} does not "
                                    "end in a waste or a reservoir. "
                                    "Changing it to end in a waste or "
                                    "an appropriate open end was not "
                                    "successful. It cannot be cleaned.")
            path = pathImproved
            logger_CetoniDevice_action.info(f"{multiPumpClean.__name__}\n"
                                    "Path to clean: "
                                    f"{path}")

    # get the dead volume of the path to clean
    dV_toClean = graph.getTotalQuantity(nodelist=path, quantity="dead_volume")

    if path is None:
        return pathsNotCleaned, pathsCleaned

    if pumps is None:
        pumpsList = list(pumpsDict.keys())
    else:
        pumpsList = pumps

    # Initialize the counter and the flow
    i=0
    # group the pumps into two groups
    groupA = pumpsList[0:(int(np.ceil(len(pumpsList)/2)))]
    groupB = pumpsList[(int(np.ceil(len(pumpsList)/2))):]
    # get the number of pumps in each group
    noMembersGroupA = len(groupA)
    noMembersGroupB = len(groupB)
    logger_CetoniDevice_action.info(f"{multiPumpClean.__name__} \n group A: {groupA}, group B: {groupB}")
    # Collect the path to the medium and the path to clean for each pump
    pumpsPaths = {}
    for pump in pumpsList:
        # get the maximum volume of the pump
        Vmax = pumpsDict[pump].get_volume_max()
        # get the fraction of the volume, this pump needs to deliver based on the
        # group size
        if pump in groupA:
            fraction = 1./noMembersGroupA
        else:
            fraction = 1./noMembersGroupB
        # if the medium is not a gas, reduce the filling level to not waste
        # the cleaning medium
        if mediumNoGas and ((dV_toClean*fraction) <= Vmax):
            level = dV_toClean*fraction
        else:
            level = Vmax
        pumpsPaths[pump]={
            "pathMP": graph.findPath(start_node=medium, end_node=pump),
            "pathClean": graph.findPath(start_node=pump,
                                        end_node=path[-1],
                                        via=path[0:-2]),
            "level": level,
            "flow": flow*fraction}

    # Ensure, that the paths from the medium and the paths to clean in each group
    # can be set simultaneously without intersections
    for group in [groupA, groupB]:
        pathsToMedium = [pumpsPaths[k]["pathMP"] for k in group]
        pathsToClean = [pumpsPaths[k]["pathClean"] for k in group]
        if ((not graph.pathsCompatible(pathsList=pathsToMedium))
            or
            (not graph.pathsCompatible(pathsList=pathsToClean))
        ):
            raise ValueError(f"The paths are not compatible for group {group}."
                             "Please change them and try again.")

    # If the medium is not a gas, use the number of repeats as a counter, otherwise do
    # 5 times the number of repeats
    if mediumNoGas:
        count = repeats
    else:
        count = 5 * repeats

    while i in range(count):
        # print the number of the cleaning cycle
        print(f"\n\n multi pump clean {i+1}/{count} \n\n")
        # aspirate the medium to the pumps assigned to group A
        for pump in groupA:
            # switch the valves to the path found from the medium to the pump
            switchValves(nodelist=pumpsPaths[pump]["pathMP"], valvesDict=valvesDict)
            # fill the pump with the cleaning medium
            pumpsDict[pump].set_fill_level(pumpsPaths[pump]["level"],
                                           flow=pumpsPaths[pump]["flow"])
            logger_CetoniDevice_action.info(f"{multiPumpClean.__name__} "
                                        f"\n Fill level: {pumpsPaths[pump]['level']}")
        # dispense the medium from the pumps assigned to group B
        for pump in groupB:
            # switch the valves according to the path to clean
            switchValves(nodelist=pumpsPaths[pump]["pathClean"], valvesDict=valvesDict)
            logger_CetoniDevice_action.info(f"{multiPumpClean.__name__} \n "
                                f"Path to clean: {pumpsPaths[pump]['pathClean']}")
            # dispense all the contents of the pump to the path to clean
            pumpsDict[pump].set_fill_level(0.0, flow=pumpsPaths[pump]["flow"])
        # wait until all pumps have finished pumping
        while len(CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict = pumpsDict)) > 0:
            time.sleep(0.1)
        # wait longer, if the medium is not a gas
        if mediumNoGas:
            timer.wait_until(timer.is_expired, True)
        
        pathsCleaned.append(path)
        groupA, groupB = groupB, groupA
        i+=1

    return pathsNotCleaned, pathsCleaned

def pressurizedGasClean(nodesToClean:list,
                        valvesDict:dict,
                        endNodePath:str=conf["CetoniDevice"]["waste"],
                        endNodeDrying:str=conf["CetoniDevice"]["wasteForDrying"],
                        gasNode:str="pressurizedGas",
                        repeats:int=3,
                        setup:str=conf["graph"]["savePath_graph"]) -> Tuple[list,list]:
  
    # TODO: Find a smart way to identify the node to pass for switching off the gas.

    # Check input types
    typeCheck(func=pressurizedGasClean, locals=locals())

    # Get the graph
    setup, pos = graph.getGraph(graph=setup, positions=None)


    # try to find a path to the requested node and skip it, if there is no path to this
    # node
    pathsCleaned = []
    pathsNotCleaned = []
    try:
        print("check")
        pathToClean = graph.findPath(
                        start_node=gasNode,
                        end_node=endNodePath,
                        via=nodesToClean)

        pathGasOff = graph.findPath(
            start_node="ambient",
            end_node=endNodePath,
            via=["ArdV_0_1_0.0"] + nodesToClean
        )

        logger_CetoniDevice_action.info(
            f"{pressurizedGasClean.__name__} \n"
            f"Cleaning {nodesToClean} using {pathToClean}."
            )

        # Switch the valves and turn the flow on
        for j in range(repeats):
            print(f"\n\n pressurized gas clean {j+1}/{repeats} \n\n")
            for i in range(5):
                switchValves(nodelist=pathToClean, valvesDict=valvesDict)
                time.sleep(1)
                switchValves(nodelist=pathGasOff, valvesDict=valvesDict)
                time.sleep(1)
            time.sleep(30.)
            switchValves(nodelist=pathToClean, valvesDict=valvesDict)
            time.sleep(60.)
            for i in range(5):
                switchValves(nodelist=pathToClean, valvesDict=valvesDict)
                time.sleep(1)
                switchValves(nodelist=pathGasOff, valvesDict=valvesDict)
                time.sleep(1)
            time.sleep(30.)
        # Dry the path
        try:
            pathToDry = graph.findPath(start_node=gasNode,
                end_node=endNodeDrying,
                via=nodesToClean)
        except NetworkXNoPath:
            pathToDry = pathToClean
        switchValves(nodelist=pathToDry, valvesDict=valvesDict)
        time.sleep(180.)
        switchValves(nodelist=pathGasOff, valvesDict=valvesDict)
        pathsCleaned.append(pathToClean)
    except NetworkXNoPath:
        pathsNotCleaned.append(nodesToClean)

    return pathsNotCleaned, pathsCleaned

def clean(medium:str, pumpsDict:dict, valvesDict:dict, pumps:Union[list, None]=None,
          nodes:list=['all'], repeats:int=3, goToRef:bool=True,
          endNode_drying:str=conf["CetoniDevice"]["wasteForDrying"],
          setup:str=conf["graph"]["savePath_graph"],
          flow:float=conf["CetoniDeviceDriver"]["flow"]) -> None:
    ''' This function provides cleaning capabilities of the system. The parameter parts specifies, what shall be cleaned.
    
    Inputs:
    medium: the name of a node, from where the cleaning medium shall be aspirated
    pumpsDict: a dictionary containing the names of the pumps as keys and the pump objects present in the setup as values
    valvesDict: a dictionary containing valve names as keys and valves as values
    pumps: a list of strings of pump names defining, which pumps shall be used for the
    cleaning. If pumps is None, all pumps will be used for cleaning.
    nodes: a list of the node names, to where paths need to be cleaned
    repeats: an integer defining the number of cleaning cycles
    goToRef: a boolean specifying, whether all pumps in the system shall go to the start position (piston all the way in) prior to starting the cleaning
    setup: a string, dictionary, or a graph object representing the graph to be used to determine the paths
    flow: a floating point number defining the volume flow to be used in the system during the cleaning

    Outputs:
    total_notCleaned: a list of the not cleaned nodes
    total_cleaned: a list of the cleaned nodes '''

    # TODO: Check for intersections of paths

    # Check the input types
    typeCheck(func=clean, locals=locals())

    # Initialize a timer
    timer = PollingTimer(period_ms=200000)

    # Get the graph
    setup_graph, setup_positions = graph.getGraph(graph=setup, positions=None)

    logger_CetoniDevice_action.info(f"{clean.__name__} \n Cleaning procedure started.")

    # check, if the requested medium is gas or not
    nodesWithGas = [conf["CetoniDevice"]["gas"], "pressurizedGas"]
    mediumNoGas = medium not in nodesWithGas
    logger_CetoniDevice_action.info(f"{clean.__name__} \n"
                                    f"Medium is not a gas: {mediumNoGas}")

    # Find all the open ends in the graph
    openEnds = graph.getOpenEnds(graph=setup)
    # Filter out pumps, the medium itself and nodes connected to gas
    openEndsReduced = [oE for oE in openEnds if ((oE not in pumpsDict.keys())
                                                    and (oE != medium)
                                                    and (oE not in nodesWithGas))]
    # If the medium is not gas, also filter out the open ends at valves to avoid
    # pumping solvent to these ends
    if mediumNoGas:
        openEndsReduced = [oeNoGas for oeNoGas in openEndsReduced
                            if ((type(graph.getValveFromName(oeNoGas))!=str))]
    # Candidates for nodes acceptable as endpoints for the cleaning
    oEcands = [oec for oec in openEndsReduced
                if (("waste" in oec) or ("Reservoir" in oec))]

    # Collect the not cleaned nodes
    nodesNotCleaned = []

    if "all" in nodes:
        nodes = setup_graph.nodes

    # Filter for the accepted pumps only
    if pumps is None:
        pumps = list(pumpsDict.keys())

    # Remove all the nodes related to pumps, the medium itself and the gas
    # connections
    nodes_reduced = [n for n in nodes if ((n not in pumpsDict.keys())
                                                and (n != medium)
                                                and (n not in nodesWithGas))]
    # If the medium is not a gas, filter the open ends at valves out, too.
    if mediumNoGas:
        nodes_reduced = [n1 for n1 in nodes_reduced if (
                                (n1 not in openEnds) or
                                (n1 in openEndsReduced))]

    nodePumpPath = {}
    instruments = set()

    total_cleaned = set()
    total_notCleaned = set()

    for node in nodes_reduced:
        if any(
            [inst in node for inst in conf['CetoniDevice']['measureVolumes'].keys()]
            ):
            instrumentsList = list(instruments)
            instrumentsList.append(node.rstrip("IN").rstrip("OUT"))
            instruments = set(instrumentsList)
        if node in openEndsReduced:
            closestPump, pathToClosestPump = graph.findClosest(node=node,
                                                candidates=pumps,
                                                graph=setup, weight="dead_volume",
                                                direction="in")
            if not ((closestPump is None) or (pathToClosestPump is None)):
                nodePumpPath[node] = {"pump": closestPump,
                                    "path": pathToClosestPump}
            else:
                nodesNotCleaned.append(node)
        elif (node in openEnds) and not (node in openEndsReduced):
            nodesNotCleaned.append(node)
        else:
            closestPump, pathToClosestPump = graph.findClosest(node=node,
                                                candidates=pumps,
                                                graph=setup, weight="dead_volume",
                                                direction="in")
            try:
                fullPath = graph.findPath(start_node=closestPump,
                                                end_node=conf["CetoniDevice"]["waste"],
                                                via=[node],
                                                graph=setup)
            except NetworkXNoPath:
                try:
                    closestOpenEnd, pathToClosestOpenEnd = graph.findClosest(
                                                                node=node,
                                                                candidates=oEcands,
                                                                graph=setup)
                    fullPath = graph.findPath(start_node=closestPump,
                                            end_node=closestOpenEnd,
                                            via=[node],
                                            graph=setup)
                except NetworkXNoPath:
                    fullPath = None
            if fullPath is None:
                nodesNotCleaned.append(node)
            else:
                nodePumpPath[node] = {"pump": closestPump, "path": fullPath}

    if medium != "pressurizedGas":
        pending = list(nodePumpPath.keys())
        logger_CetoniDevice_action.info(f"{clean.__name__} \n Single pump cleaning. \n"
            f"pending: {pending}")
        while len(pending) > 0:
            cleanInThisRound = {}
            pendingCopy = pending.copy()
            for n in pendingCopy:
                # Since pending is updated in every iteration, but pendingCopy is not, it
                # is checked to avoid to cover the same nodes several times
                if n not in pending:
                    continue
                # There is no point in searching for pumps, if all pumps are already busy
                # for this round
                if all(
                        [pump in list(cleanInThisRound.keys()) for pump in pumps]
                    ) and (
                        list(cleanInThisRound.keys()) != []
                    ):
                    break
                closestPump = nodePumpPath[n]['pump']
                if closestPump in cleanInThisRound.keys():
                    candidates = [cand for cand in pumps if
                                (cand not in cleanInThisRound.keys())]
                    closestPump_new, pathToClosestPump_new = graph.findClosest(node=n,
                                            candidates=candidates,
                                            graph=setup, weight="dead_volume",
                                            direction="in")
                    if not ((closestPump_new is None) or (pathToClosestPump_new is None)):
                        if n == nodePumpPath[n]["path"][-1]:
                            newPump = closestPump_new
                            newPath = pathToClosestPump_new
                        else:
                            try:
                                fullPath_new = graph.findPath(start_node=closestPump_new,
                                    end_node=nodePumpPath[n]["path"][-1],
                                    via=[n],
                                    graph=setup)
                                newPump = closestPump_new
                                newPath = fullPath_new
                            except NetworkXNoPath:
                                continue
                    else:
                        continue
                elif (closestPump not in cleanInThisRound.keys()):
                    newPump = nodePumpPath[n]['pump']
                    newPath = nodePumpPath[n]['path']

                allPaths = [newPath] + list(cleanInThisRound.values())
                if graph.pathsCompatible(pathsList=allPaths):
                    nodePumpPath[n]["pump"] = newPump
                    nodePumpPath[n]["path"] = newPath
                    cleanInThisRound[nodePumpPath[n]["pump"]] = nodePumpPath[n]['path']
                    # Remove all the nodes involved in the path from the list of pending
                    # nodes
                    for np in nodePumpPath[n]['path']:
                        try:
                            pending.remove(np)
                        except ValueError:
                            continue

            print(f"\n\n clean in this round {cleanInThisRound} \n\n")
            logger_CetoniDevice_action.info(
                f"{clean.__name__} \n clean in this round {cleanInThisRound} \n"
            )
            notCleanedSP, cleanedSP = singlePumpClean(pumpsPathsDict=cleanInThisRound,
                                                    medium=medium, pumpsDict=pumpsDict,
                                                    valvesDict=valvesDict,
                                                    goToRef=goToRef,
                                                    repeats=repeats,
                                                    flow=flow,
                                                    setup=setup)
            # Bookkeeping about what is already cleaned and what is not
            currentCleaned = list(total_cleaned)
            currentNotCleaned = list(total_notCleaned)
            for pathClean in cleanedSP:
                currentCleaned.extend(pathClean)
            for pathNotClean in notCleanedSP:
                currentNotCleaned.extend(pathNotClean)
            total_cleaned = set(currentCleaned)
            total_notCleaned = set(currentNotCleaned)

    ### Clean the instruments
    print("not mediumNoGas",  not mediumNoGas)
    print(instruments)
    if not mediumNoGas:
        logger_CetoniDevice_action.info(f"{clean.__name__} \n "
            f"Cleaning instruments with pressurized gas.")

        for node in instruments:
            print(node)
            nodesToPass = [f"{node}IN", f"{node}OUT"]
            notCleanedPG, cleanedPG = pressurizedGasClean(
                nodesToClean=nodesToPass,
                valvesDict=valvesDict,
                endNodeDrying=endNode_drying,
                repeats=repeats
                )

            currentCleaned = list(total_cleaned)
            currentNotCleaned = list(total_notCleaned)
            for pathClean in cleanedPG:
                currentCleaned.extend(pathClean)
            for pathNotClean in notCleanedPG:
                currentNotCleaned.extend(pathNotClean)
            total_cleaned = set(currentCleaned)
            total_notCleaned = set(currentNotCleaned)
    return total_notCleaned, total_cleaned