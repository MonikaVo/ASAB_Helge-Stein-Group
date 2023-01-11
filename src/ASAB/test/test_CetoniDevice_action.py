from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.driver import CetoniDevice_driver
from ASAB.action import CetoniDevice_action
from ASAB.utility import graph, solutionHandler

from qmixsdk import qmixbus

# Other imports
import numpy as np


# def test_flushSyringe():

#     G, pos = graph.generateGraph()
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()

#     pump = Ps['A0.0']

#     CetoniDevice_action.flushSyringe(pumps=Ps, valves=Vs, pump=pump.name, reservoir='Reservoir1', flow=pump.get_flow_rate_max())

#     assert pump.get_fill_level() == 0.0, f"The fill level of the pump is {pump.get_fill_level()} instead of 0.0."
#     assert np.isclose(pump.get_dosed_volume(), pump.get_volume_max()*0.15, 0.000001), f"The dosed volume of the pump is {pump.get_dosed_volume()} instead of {pump.get_volume_max()*0.15}."

# def test_mix():
#     # Get the chemicalsDict
#     chemicalsDict = solutionHandler.get_chemicalsDict(conf['solutionHandler']['chemicalsDict'])
#     # Get the solutionsDict
#     solutionsDict = solutionHandler.get_solutionsDict(conf['solutionHandler']['solutionsDict'])

#     # Prepare the Cetoni device
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()

#     ## mixing ratio as molar fraction
#     # Get the mixing ratios
#     mixingRatios = conf['test_solutionHandler']['mixingRatios']['molarFractions']

#     for ratio in mixingRatios.keys():
#         print('\n', ratio, '\n')
#         # Get the target values for the outputs of mix
#         mixRatio_request_target = mixingRatios[ratio]
#         mixRatio_vol_target = conf['test_solutionHandler']['volFrac_targets'][ratio]['volumeFractions']
#         calcMix_request_target = conf['test_solutionHandler']['volFrac_targets'][ratio]['setRatio']
#         # Get the target flows for the involved pumps
#         flows_target = {}
#         for sol in mixRatio_vol_target.keys():
#             pump = solutionsDict[sol].pump
#             flow = conf["CetoniDeviceDriver"]["flow"]
#             flows_target[pump] = mixRatio_vol_target[sol] * flow

#         # Apply the mixing function
#         mixRatio_request_result, mixRatio_vol_result, calcMix_request_result, flows_actual = CetoniDevice_action.mix(mixingRatio=mixRatio_request_target, fraction='molPerMol', pumps=Ps, valves=Vs, chemicalsDict=conf['solutionHandler']['chemicalsDict'], solutionsDict=conf['solutionHandler']['solutionsDict'], endpoint=conf["CetoniDevice"]["waste"], setup=conf["graph"]["savePath_graph"], flow=conf["CetoniDeviceDriver"]["flow"])

#         # Check the outputs
#         for k in mixRatio_request_result.keys():
#             assert np.isclose(mixRatio_request_target[k], mixRatio_request_result[k], rtol=1e-06), f"The requested mixing ratio for {k} is {mixRatio_request_result[k]} instead of {mixRatio_request_target[k]}."
#         for l in mixRatio_vol_result.keys():
#             assert np.isclose(mixRatio_vol_target[l], mixRatio_vol_result[l], rtol=1e-06), f"The volumetric mixing ratio for {l} is {mixRatio_vol_result[l]} instead of {mixRatio_vol_target[l]}."
#         for m in calcMix_request_result.keys():
#             assert np.isclose(calcMix_request_target[m], calcMix_request_result[m], rtol=1e-06), f"The calculated mixing ratio for {m} is {calcMix_request_result[m]} instead of {calcMix_request_target[m]}."

#         # Check the flows
#         flows_result = {}
#         for p in flows_target.keys():
#              flows_result[p] = Ps[p].get_flow_is()

#         print(flows_result)
        
#         for f in flows_result.keys():
#                 print(f, flows_target[f], flows_result[f], Ps[f].syringe.minimum_flow_mL_per_sec, Ps[f].syringe.maximum_flow_mL_per_sec)
#                 assert np.isclose(flows_target[f], flows_result[f], rtol=1e-06), f"The flow of {f} is {flows_result[f]} instead of {flows_target[f]}."

def test_provideSample():
    pass

def test_drainSample():
    pass

def test_emptySyringes():
    pass

def test_switchValves():
    pass
# def test_switchValves():
#     i = 0
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"])

#     initPos = {'V1': 8, 'V2': 2, 'V3': 7, 'V4': 9, 'V5': 3, 'V6': 9, 'V7': 5, 'V8': 3, 'V9': 9, 'V10': 1, 'Av': 1, 'Bv': 0, 'Cv': 0, 'Dv': 0, 'Ev': 1, 'Fv': 1}
#     for val in Vs.keys():
#         if val in CetoniDevice_driver.getValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]).keys():
#             Vs[val].switch_valve_to_position(initPos[val])

#     CetoniDevice_action.switchValves(nodelist=[], settings=conf["test_CetoniDevice"]["input"]["fillSyringe"][i]["valvePos"], valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
    
#     valves_after = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
#     valves_target = conf["test_CetoniDevice"]["input"]["fillSyringe"][i]["valvePos"]

#     assert valves_after == valves_target, "The valve settings after switching are not as expected."
#     CetoniDevice_driver.cetoni.quitCetoni()
    
def test_fillSyringe():
    pass
# def test_fillSyringe():
#     i = 0
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"])
#     p = Ps[conf["test_CetoniDevice"]["input"]["fillSyringe"][i]["pump"]]
#     CetoniDevice_action.switchValves(nodelist=[], settings=conf["test_CetoniDevice"]["input"]["fillSyringe"][i]["valvePos"], valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
#     valves_before = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
#     level_before = p.get_fill_level()
#     level_after = CetoniDevice_action.fillSyringe(pump=p, volume=conf["test_CetoniDevice"]["input"]["fillSyringe"][i]["volume"], waste=conf["test_CetoniDevice"]["input"]["fillSyringe"][i]["waste"], valvesDict=Vs, flow=conf["CetoniDeviceDriver"]["flow"], setup=conf["CetoniDeviceDriver"]["setup"], valvePositionDict=conf["CetoniDeviceDriver"]["valvePositionDict"], simulateBalance=conf["CetoniDeviceDriver"]["simulateBalance"])
#     valves_after = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))

#     print("level_before", level_before)
#     print("level_after", level_after)
#     print("valves_before", valves_before)
#     print("valves_after", valves_after)

#     assert(level_after > level_before, f"Fill level after filling {level_after} is not larger than level before {level_before}.")
#     assert(valves_before == valves_after, "The valve settings before and after the filling of the pump do not match.")
#     CetoniDevice_driver.cetoni.quitCetoni()

# def test_singlePumpClean():
#     # Prepare the graph and the system
#     G, pos = graph.generateGraph()
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()

#     # get the path to clean and the pump to use from the configuration
#     pathToClean = conf["test_CetoniDevice"]["inputs"]["pathsToClean"][0]
#     pump = pathToClean[0]

#     # clean the path using the respective pump and gas
#     CetoniDevice_action.singlePumpClean(pumpsPathsDict={pump: pathToClean}, medium="ambient", pumpsDict=Ps, valvesDict=Vs, repeats=1)

#     # clean the path using the respective pump and solvent
#     CetoniDevice_action.singlePumpClean(pumpsPathsDict={pump: pathToClean}, medium="Solvent", pumpsDict=Ps, valvesDict=Vs, repeats=1)

# def test_multiPumpClean():
#     # Prepare the graph and the system
#     G, pos = graph.generateGraph()
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()

#     # get the path to clean and the pump to use from the configuration
#     pathToClean = conf["test_CetoniDevice"]["inputs"]["pathsToClean"][1]
#     pumps = list(Ps.keys())

#     # clean the path using the respective pump and gas
#     CetoniDevice_action.multiPumpClean(path=pathToClean, medium="ambient", pumps=pumps, pumpsDict=Ps, valvesDict=Vs, repeats=1)

#     # clean the path using the respective pump and solvent
#     CetoniDevice_action.multiPumpClean(path=pathToClean, medium="Solvent", pumps=pumps, pumpsDict=Ps, valvesDict=Vs, repeats=1)


def test_clean():
    # Prepare the graph and the system
    G, pos = graph.generateGraph()
    Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()

    # clean the whole system using gas
    CetoniDevice_action.clean(medium="ambient", pumpsDict=Ps, valvesDict=Vs, pumps=None, repeats=1, nodes=["all"])

    # clean the whole system using solvent
    CetoniDevice_action.clean(medium="Solvent", pumpsDict=Ps, valvesDict=Vs, pumps=None, repeats=1, nodes=["all"])

    # clean a part of the system using gas
    CetoniDevice_action.clean(medium="ambient", pumpsDict=Ps, valvesDict=Vs, pumps=conf["test_CetoniDevice"]["inputs"]["cleaningPumps"], repeats=1, nodes=conf["test_CetoniDevice"]["inputs"]["nodesToClean"])

    # clean a part of the system using solvent
    CetoniDevice_action.clean(medium="Solvent", pumpsDict=Ps, valvesDict=Vs, pumps=conf["test_CetoniDevice"]["inputs"]["cleaningPumps"], repeats=1, nodes=conf["test_CetoniDevice"]["inputs"]["nodesToClean"])

def test_goToRefPos():
    pass