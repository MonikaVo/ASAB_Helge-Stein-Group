## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError as ie:
    # if the import fails, check, if it is a test, which means, that a file in a pytest folder will be main and thus it will be in the path returned in the error message of the ImportError.
    if ('pytest' in str(ie)):
        # the software will produce a warning, which reports the switch to the testing configuration. This warning is always shown.
        import warnings
        warnings.filterwarnings('always')
        warnings.warn('Configuration from main not available, but this looks like a test. Loading test configuration instead.', category=ImportWarning)
        # the filtering funcitons are set to default again
        warnings.filterwarnings('default')
        # the test configuration is imported
        from ASAB.test.FilesForTests import config_test
        conf = config_test.config
    # if "pytest" is not in the error message, it is assumed, that the call did not originate from a test instance and it therefore raises the ImportError.
    else:
        raise ie

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
from tqdm import tqdm
import networkx as nx
from networkx.exception import NodeNotFound, NetworkXNoPath
import time


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

def mix(mixingRatio:dict, fraction:str, pumps:dict, valves:dict, via=[], chemicalsDict:Union[str, dict, None]=conf['solutionHandler']['chemicalsDict'], solutionsDict:Union[str, dict, None]=conf['solutionHandler']['solutionsDict'], endpoint:str=conf["CetoniDevice"]["waste"], setup:Union[str,dict, nx.DiGraph]=conf["graph"]["savePath_graph"], flow:float=conf["CetoniDeviceDriver"]["flow"]) -> Tuple[dict, dict, dict]:
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
        endpoint: a string giving the name of a node, where the sample shall end up. This could be the waste or another node representing an additional reservoir, which can be reached.
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
        mixRatio_request, mixRatio_vol, calcMix_request, minSquaredError = solutionHandler.get_volFracs(mixingRatio=mixingRatio, chemicalsDict=chemicalsDict, solutionsDict=solutionsDict, fraction=fraction)

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
                raise ValueError(f"Something seems to be wrong with the flow for stock soltuion {sol}, which is {mixRatio_vol[sol]*flow} with the syringe lower limit {spump.minimum_flow_mL_per_sec} and higher limit {maximum_flow_mL_per_sec}.")
            ## Fill the pump with its respective fluid
            # Find a path from the reservoir to the pump
            pathRP = graph.findPath(start_node=sreservoir, end_node=spumpName)
            # Switch valves according to pathRP
            switchValves(nodelist=pathRP, valvesDict=valves)
            # Fill the syringe up to maximum volume
            print("Filling syringe")
            print('solution', sol, 'flow', flows[sol])
            _ = fillSyringe(pump=spump, volume=spump.get_volume_max(), reservoir=sreservoir, valvesDict=valves)
        else:
            del mixRatio_vol[sol]

    ## Check, that all flows are above the minimum flow of their syringe, adjust them otherwise and raise a Warning
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
    
    ## Wait until the dead volume of the path from the pump to the endpoint with the largest dead volume is pumped 1.2 times
    # Get the maximum dead volume
    dV_max = max(dV)
    print('dV_max', dV_max)
    # Wait until dV_max is pumped 1.2 times with flow
    timer2 = qmixbus.PollingTimer(period_ms = (1.2*dV_max/flow)*1000.)
    timer2.wait_until(timer2.is_expired, True)

    # Return to mL/s flow units to revert to standard settings
    spump.set_flow_unit(prefix=flow_unit_prior.prefix, volume_unit=flow_unit_prior.unitid, time_unit=flow_unit_prior.time_unitid)

    # Collect the actual flows
    flows_actual = {}
    for sol in flows.keys():
        solutionPump = solutionsDict[sol].pump
        flows_actual[sol] = pumps[solutionPump].get_flow_is()
        print('actual flow', pumps[solutionPump].get_flow_is())
        print('target flow', flows[sol])

    return mixRatio_request, mixRatio_vol, calcMix_request, flows_actual

def provideSample(measurementtype:str, sample_node:str, pumps:dict, valves:dict, endpoint:str=conf["CetoniDevice"]["waste"]) -> None:
    ''' This function moves the sample to the requested device.
    
    Inputs:
    measurementtype: a string specifying the device, to which the sample shall be supplied, e.g. densiVisco, nmr, uvVis
    sample_node: a string giving the name of the node, from where the sample shall be directed towards the device
    pumps: a dictionary containing all the pumps in the system with the names of the pumps as keys and the pump objects as values
    valves: a dictionary containing all the valves in the system with the names of the valves as keys and the valve objects as values
    endpoint: a string giving the name of a node, where the sample shall end up. This could be the waste or another node representing an additional reservoir, which can be reached.

    Outputs:
    This function has not outputs. '''
    # TODO: Test this function!!!
    
    ## Check the input types
    typeCheck(func=provideSample, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    
    # Find a path from the sample_node to the inlet of the device
    pathSIN = graph.findPath(start_node=sample_node, end_node=f"{measurementtype}IN")
    # Find a path from the outlet of the device to the waste
    pathOUTE = graph.findPath(start_node=f"{measurementtype}OUT", end_node=endpoint)
    # Assemble the total path
    pathTotal = pathSIN + pathOUTE
    # Check the validity of pathTotal and if it is valid, switch the valves accordingly
    if graph.pathIsValid(pathTotal):
        switchValves(nodelist=pathTotal, valvesDict=valves)
    else:
        raise ValueError("The total path is not valid.")
    # Get the currently pumping pumps
    pumpingPs = CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict = pumps)
    ## Switch the valves from the pumps, which are pumping, to the sample_node to avoid the sample to be pumped to the endpoint directly
    for p in pumpingPs:
        # find a path from the pump to the sample_node
        pathPN = graph.findPath(start_node=p, end_node=sample_node)
        # switch the valves for this pump so that it pumps towards the sample_node
        switchValves(nodelist=pathPN, valvesDict=valves)
    ## Wait until the volume required for the measurement is pumped 1.5 times or the first pump stops pumping and stop the flow
    # Initialize a timer
    timer = qmixbus.PollingTimer(period_ms = 1.5 * 1000. *((graph.getTotalQuantity(nodelist=pathSIN, quantity="dead_volume") + conf["CetoniDevice"]["measureVolumes"][measurementtype])/conf["CetoniDeviceDriver"]["flow"]))
    print("volume to be pumped: ", graph.getTotalQuantity(nodelist=pathSIN, quantity="dead_volume") + conf["CetoniDevice"]["measureVolumes"][measurementtype])
    print(f"time to be waited: {timer.get_msecs_to_expiration()/1000.} s, {timer.get_msecs_to_expiration()/60000.} min")
    # Wait and check the two conditions
    while (not timer.is_expired()) and (pumpingPs == CetoniDevice_driver.cetoni.pumpingPumps(pumpsDict=pumps)):
        time.sleep(0.1)
    # Stop all pumps
    CetoniDevice_driver.pumpObj.stop_all_pumps()
    ## Wait a while for the liquid to get stable
    time.sleep(10)

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

def cleanPath(path:list, pumpsDict:dict, mediumReservoir:str=conf["CetoniDevice"]["gas"], waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"], repeats:int=3):
    ''' This function cleans a path entered as a list of nodes using the medium provided in the mediumReservoir. '''
    # TODO: test this function

    ## Check the input types
    typeCheck(func=cleanPath, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary


    # initialise a timer
    timer = PollingTimer(period_ms=60000)
    # find the closest pump to the start node of the path
    p, pathMP = graph.findClosest(node=mediumReservoir, candidates=pumpsDict.keys(), direction='out')
    # find a path from the pump via the path to the waste
    pathPW = graph.findPath(start_node=p, end_node=waste, via=path)
    if graph.pathIsValid(pathPW):
        for i in range(repeats):
            switchValves(pathMP)
            pumpsDict[p].set_fill_level(pumpsDict[p].get_volume_max(), flow)
            timer.wait_until(pumpsDict[p].is_pumping, False)
            switchValves(pathPW)
            pumpsDict[p].set_fill_level(0.0, flow)
            timer.wait_until(pumpsDict[p].is_pumping, False)
        # update the system status to note the current filling of the tubes.
        graph.updateSystemStatus(path=pathPW)
        return True
    else:
        raise ValueError(f'The path from the pump {p} via the path {path} to the waste {waste}: {pathPW} is not valid!')

def clean(pumpsDict:dict, setup:Union[str,nx.DiGraph]=conf["graph"]["savePath_graph"], waste:str=conf["CetoniDevice"]["waste"], gas:str=conf["CetoniDevice"]["gas"], flow:float=conf["CetoniDeviceDriver"]["flow"]):
    ''' This function cleans the whole pumping system including the tubing and the devices. '''
    # TODO: Test this function

    ## Check the input types
    typeCheck(func=clean, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    # Message the user to ensure all open ends are in a container
    input('Please ensure, that all open ends are positioned inside a waste container.')

    # ensure that setup is a graph
    setup, positions = graph.getGraph(graph=setup, positions=None)

    # initialise a timer
    timer = PollingTimer(period_ms=60000)

    ## Drain residues from syringe using gas
    # aspirate gas to all pumps, dispense to waste, do this two times
    for p in pumpsDict.keys():
        # find a path from each pump to the waste
        path = graph.findPath(start_node=p, end_node=waste)
        # clean the path three times using gas
        cleanPath(path=path, pumpsDict=pumpsDict, mediumReservoir='ambient', repeats=3)

    ## Clean the devices
    # identify the devices
    devices = [n[:-2] for n in list(setup.nodes()) if 'IN' in n]
    print('devices', devices)
    ## Iterate through the devices and clean each of them
    for d in devices:
        pathIO = graph.findPath(start_node=f'{d}IN', end_node=f'{d}OUT', repeats=3)
    
    ## Clean the open ends except reservoirs and solvents
    # find the open ends in the graph
    openEnds = graph.getOpenEnds(setup)

    # Exclude solvents and reservoirs to clean them last
    # find a path to each open end
    # for oe in openEnds:
    #     pathPO = graph.findClosest()

    # clean the paths

    ## Clean the solvents

    ## Clean the reservoirs

    # report done

def emptySyringes(pumps:dict, valves:dict, waste:str=conf["CetoniDevice"]["waste"], gas:str=conf["CetoniDevice"]["gas"], repeats:int = 3):
    ''' This function removes remaining liquid from all the pumps in the system, by aspirating it into one pump and dispensing it from there to the waste. '''
    # TODO: Test this function
    
    ## Check the input types
    typeCheck(func=emptySyringes, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    
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
    print("Valves switched to the following positions: \n")
    # For every valve
    for valve in valveSettings.keys():
        if valve in valvePositionDict.keys():
            # Change the valve position according to the settings
            valvesDict[valve].switch_valve_to_position(valveSettings[valve])
            # Print how the valves are switched
            print(f"{valve}: {valvesDict[valve].actual_valve_position()}")

def fillSyringe(pump:pumpObj, volume:float,valvesDict:dict, reservoir:str, tolerance:float=3.,  waste:str=conf["CetoniDevice"]["waste"], flow:float=conf["CetoniDeviceDriver"]["flow"], setup=conf["graph"]["savePath_graph"], valvePositionDict:str=conf["CetoniDeviceDriver"]["valvePositionDict"], simulateBalance:bool=conf["CetoniDeviceDriver"]["simulateBalance"]):
    ''' This function ensures that the syringe does not contain gas, but only liquid. '''
        
    ## Check the input types
    typeCheck(func=fillSyringe, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

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
    # TODO: enter here to add a while loop for the final volume < vol-tolerance
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
            print("The syringe seems to be empty. Please check the cause for that.")
        # Get the current fill level of the pump
        filling_full = pump.get_fill_level()

    # Switch the valves back to the initial positions
    switchValves(nodelist=[], settings=origValvePos, valvesDict=valvesDict, valvePositionDict=valvePositionDict)
    # Return the fill level of the pump
    return filling_full # -> TODO: Define a deviation from the requested volume that is acceptable and repeat the process, if the fill level is lower.

def cleanMixingsystem(pumpsDict:dict, valvesDict:dict, medium1:str, intermediate:bool = True, medium2:str=conf["CetoniDevice"]["gas"], waste=conf["CetoniDevice"]["waste"], paths=conf["CetoniDevice"]["pathsToClean"], valvePositionDict:Union[dict,str]=conf["CetoniDeviceDriver"]["valvePositionDict"], setup:str=conf["graph"]["savePath_graph"], flow:float=conf["CetoniDeviceDriver"]["flow"], repeats:int = 3):
    ''' This function cleans the used paths of an experiment first using solvent and subsequently using gas. It is intended to be used after small experiments, where a cleaning of the full
    system will not be reasonable. The variable intermediate determines, if it is a final cleaning after finishing experiments (False) or if it is an intermediate cleaning in between experiments (True). It requires all the tubing, which is not solvent and not gas to be put to the waste. '''
    # TODO: Test this function!!! TODO: Pump all the remainders in the pumps to one pump and again to the waste in order to reduce the remaining amount of solvent.
    input("Please confirm that all tubes except the ones for the cleaning media are put to the waste.")

    ## Check the input types
    typeCheck(func=cleanMixingsystem, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    
    # Get the valvePositionDict
    valvePositionDict = getValvePositionDict(vPd=valvePositionDict)
    # Get the setup
    setup, positions = graph.getGraph(graph=setup, positions=None)

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
    typeCheck(func=cleanInstrument, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

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
    typeCheck(func=cleanAll, locals=locals())  # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    all = ["densiVisco", "uvVis"]
    for inst in all:
        cleanInstrument(pumpsDict=pumpsDict, valvesDict=valvesDict, instrumenttype=inst, medium1=medium1, medium2=medium2, repeats=repeat)
    cleanMixingsystem(medium1=medium1, intermediate=intermediate, medium2=medium2, pumpsDict=pumpsDict, valvesDict=valvesDict, repeats=repeat)
    emptySyringes(pumps=pumpsDict, valves=valvesDict)
    goToRefPos(pumpsDict=pumpsDict, valvesDict=valvesDict, mode="end")
    return True

def goToRefPos(pumpsDict:dict, valvesDict:dict, mode:str, gas:str=conf["CetoniDevice"]["gas"], waste:str=conf["CetoniDevice"]["waste"]):
    ''' This function moves the syringes to their reference positions. This means that they move to 2 mL or half their size, depending on what is the smaller value. This
    is done before leaving the machine in order to have remaining fluid inside the syringes as much as possible and keeping it away from other components like valves, if
    it is avoidable. '''
    # TODO: Test this function!!!
    
    ## Check the input types
    typeCheck(func=goToRefPos, locals=locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    
    timer = qmixbus.PollingTimer(120000)
    for p in list(pumpsDict.keys()):
        try:
            if mode == "end":
                level = np.min([2.0, pumpsDict[p].get_volume_max()/2.])
                path = graph.findPath(gas, p)
            elif mode == "start":
                level = 0.0
                path = graph.findPath(p, waste)
            switchValves(path, valvesDict=valvesDict)
            pumpsDict[p].set_fill_level(level, pumpsDict[p].get_flow_rate_max()/5.)
        except (NodeNotFound, NetworkXNoPath) as e:
            pass
    # Only wait for the last pump, as now each pump has its own waste and gas line
    timer.wait_until(pumpsDict[p].is_pumping, False)