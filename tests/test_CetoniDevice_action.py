from tests.filesForTests import config_test
from utility.helpers import doAppends, loadFile
conf = config_test.config
doAppends(conf)

import unittest
from testfixtures import compare
import os

from driver import CetoniDevice_driver
from driver.CetoniDevice_driver import pumpObj, valveObj
from action import CetoniDevice_action
from utility.syringes import syringe
from qmixsdk import qmixbus


class test_CetoniDevice_action(unittest.TestCase):
    
    def test_mix(self):
        i = 0
        Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=conf["utility"]["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], pums=conf["CetoniDeviceDriver"]["pumps"], vals=conf["CetoniDeviceDriver"]["valves"], channls=conf["CetoniDeviceDriver"]["channels"])
        mixPump_result, mixPumpLevel_result = CetoniDevice_action.mix(mixRatio=conf["CetoniDevice"]["testInputMix"][i]["mixRatio"], waste=conf["CetoniDevice"]["testInputMix"][i]["waste"], gas=conf["CetoniDevice"]["testInputMix"][i]["gas"], setup=loadFile(conf["CetoniDeviceDriver"]["setup"]), pumps=Ps, valves=Vs)
        
        mixPump_target = "B0.0"
        mixPumpLevel_target = sum(conf["CetoniDevice"]["testInputMix"][i]["mixRatio"][key] for key in conf["CetoniDevice"]["testInputMix"][i]["mixRatio"].keys())*1.5

        self.assertEqual(first=mixPump_result, second=mixPump_target, msg="Wrong pump for mixture.")
        self.assertAlmostEqual(first=mixPumpLevel_result, second=mixPumpLevel_target, delta=0.0001, msg="Volume of mixture not as expected.")

    def test_switchValves(self):
        i = 0
        Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=conf["utility"]["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], pums=conf["CetoniDeviceDriver"]["pumps"], vals=conf["CetoniDeviceDriver"]["valves"], channls=conf["CetoniDeviceDriver"]["channels"])

        initPos = {'V1': 8, 'V2': 2, 'V3': 7, 'V4': 9, 'V5': 3, 'V6': 9, 'Av': 1, 'Bv': 0, 'Cv': 0, 'Dv': 0, 'Ev': 1, 'Fv': 1}
        for val in Vs.keys():
            if val in loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]).keys():
                Vs[val].switch_valve_to_position(initPos[val])

        CetoniDevice_action.switchValves(nodelist=[], settings=conf["CetoniDevice"]["testInputFillSyringe"][i]["valvePos"], valvesDict=Vs, valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]))
        
        valves_after = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]))
        valves_target = conf["CetoniDevice"]["testInputFillSyringe"][i]["valvePos"]

        self.assertDictEqual(d1=valves_after, d2=valves_target, msg="The valve settings after switching are not as expected.")

    def test_fillSyringe(self):
        i = 0
        Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=conf["utility"]["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], pums=conf["CetoniDeviceDriver"]["pumps"], vals=conf["CetoniDeviceDriver"]["valves"], channls=conf["CetoniDeviceDriver"]["channels"])
        p = Ps[conf["CetoniDevice"]["testInputFillSyringe"][i]["pump"]]
        CetoniDevice_action.switchValves(nodelist=[], settings=conf["CetoniDevice"]["testInputFillSyringe"][i]["valvePos"], valvesDict=Vs, valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]))
        valves_before = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]))
        level_before = p.get_fill_level()
        level_after = CetoniDevice_action.fillSyringe(pump=p, volume=conf["CetoniDevice"]["testInputFillSyringe"][i]["volume"], waste=conf["CetoniDevice"]["testInputFillSyringe"][i]["waste"], valvesDict=Vs, flow=conf["CetoniDeviceDriver"]["flow"], setup=loadFile(conf["CetoniDeviceDriver"]["setup"]), valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]), simulateBalance=conf["CetoniDeviceDriver"]["simulateBalance"])
        valves_after = CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"]))

        print("level_before", level_before)
        print("level_after", level_after)
        print("valves_before", valves_before)
        print("valves_after", valves_after)

        self.assertGreater(a=level_after, b=level_before, msg=f"Fill level after filling {level_after} is not larger than level before {level_before}.")
        self.assertDictEqual(d1=valves_before, d2=valves_after, msg="The valve settings before and after the filling of the pump do not match.")

if __name__ == "__main__":
    unittest.main(verbosity=2)