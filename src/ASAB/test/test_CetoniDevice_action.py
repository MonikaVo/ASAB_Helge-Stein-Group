from ASAB.test.FilesForTests import config_test
# from ASAB.utility.helpers import loadFile
conf = config_test.config

from ASAB.configuration import config
cf = config.configASAB

from ASAB.driver import CetoniDevice_driver
from ASAB.action import CetoniDevice_action

# Other imports
import numpy as np

# TODO: Test new mixing function. This test is outdated
# def test_mix():
#     i = 0
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"], save_name_pumps=conf["CetoniDeviceDriver"]["pumps"], save_name_valves=conf["CetoniDeviceDriver"]["valves"], save_name_channels=conf["CetoniDeviceDriver"]["channels"])
#     mixPump_result, mixPumpLevel_result = CetoniDevice_action.mix(mixRatio=conf["CetoniDevice"]["testInputMix"][i]["mixRatio"], waste=conf["CetoniDevice"]["testInputMix"][i]["waste"], gas=conf["CetoniDevice"]["testInputMix"][i]["gas"], setup=loadFile(conf["CetoniDeviceDriver"]["setup"]), pumps=Ps, valves=Vs)
    
#     mixPump_target = "B0.0"
#     mixPumpLevel_target = sum(conf["CetoniDevice"]["testInputMix"][i]["mixRatio"][key] for key in conf["CetoniDevice"]["testInputMix"][i]["mixRatio"].keys())*1.5

#     assert(mixPump_result == mixPump_target, "Wrong pump for mixture.")
#     assert(np.isclose(mixPumpLevel_result, mixPumpLevel_target, 0.0001), "Volume of mixture not as expected.")

def test_switchValves():
    i = 0
    Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"], save_name_pumps=conf["CetoniDeviceDriver"]["pumps"], save_name_valves=conf["CetoniDeviceDriver"]["valves"], save_name_channels=conf["CetoniDeviceDriver"]["channels"])

    initPos = {'V1': 8, 'V2': 2, 'V3': 7, 'V4': 9, 'V5': 3, 'V6': 9, 'Av': 1, 'Bv': 0, 'Cv': 0, 'Dv': 0, 'Ev': 1, 'Fv': 1}
    for val in Vs.keys():
        if val in CetoniDevice_driver.getValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]).keys():
            Vs[val].switch_valve_to_position(initPos[val])

    CetoniDevice_action.switchValves(nodelist=[], settings=conf["CetoniDevice"]["testInputFillSyringe"][i]["valvePos"], valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
    
    valves_after = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
    valves_target = conf["CetoniDevice"]["testInputFillSyringe"][i]["valvePos"]

    assert valves_after == valves_target, "The valve settings after switching are not as expected."
    CetoniDevice_driver.cetoni.quitCetoni()

# def test_fillSyringe():
#     i = 0
#     Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"], save_name_pumps=conf["CetoniDeviceDriver"]["pumps"], save_name_valves=conf["CetoniDeviceDriver"]["valves"], save_name_channels=conf["CetoniDeviceDriver"]["channels"])
#     p = Ps[conf["CetoniDevice"]["testInputFillSyringe"][i]["pump"]]
#     CetoniDevice_action.switchValves(nodelist=[], settings=conf["CetoniDevice"]["testInputFillSyringe"][i]["valvePos"], valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
#     valves_before = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))
#     level_before = p.get_fill_level()
#     level_after = CetoniDevice_action.fillSyringe(pump=p, volume=conf["CetoniDevice"]["testInputFillSyringe"][i]["volume"], waste=conf["CetoniDevice"]["testInputFillSyringe"][i]["waste"], valvesDict=Vs, flow=conf["CetoniDeviceDriver"]["flow"], setup=loadFile(conf["CetoniDeviceDriver"]["setup"]), valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]), simulateBalance=conf["CetoniDeviceDriver"]["simulateBalance"])
#     valves_after = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=CetoniDevice_driver.loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))

#     print("level_before", level_before)
#     print("level_after", level_after)
#     print("valves_before", valves_before)
#     print("valves_after", valves_after)

#     assert(level_after > level_before, f"Fill level after filling {level_after} is not larger than level before {level_before}.")
#     assert(valves_before == valves_after, "The valve settings before and after the filling of the pump do not match.")
#     CetoniDevice_driver.cetoni.quitCetoni()