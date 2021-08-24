import unittest
from tests.filesForTests import config_test
from utility.helpers import doAppends, loadFile
conf = config_test.config
doAppends(conf)

import unittest
from testfixtures import compare
import os

from driver import CetoniDevice_driver
from utility.syringes import syringe
from driver.CetoniDevice_driver import pumpObj, valveObj
from qmixsdk import qmixbus

class test_CetoniDevice_driver(unittest.TestCase):

    def attributeComp(self, result, target):
        for key in result.keys():
            attr = vars(result[key]).copy()
            attr.pop("handle")
            if "syringe" in attr:
                attr.pop("syringe")
            for attribute in attr:  # https://stackoverflow.com/questions/31368056/get-all-attributes-of-a-class-in-python#31368099
                if attribute in vars(target[key]):
                    if attribute in vars(target[key]):
                        self.assertEqual(first=getattr(target[key], attribute), second=getattr(result[key], attribute), msg=f"Attribute {attribute} is not correct.")    # https://stackoverflow.com/questions/2157035/accessing-an-attribute-using-a-variable-in-python
                    else:
                        self.assertEqual(first=1, second=0, msg=f"{target[key].name} does not have an attribute {attribute}.")
    
    def test_prepareCetoni(self):
        Pumps_target = loadFile(conf["CetoniDeviceDriver"]["pumps"])
        Valves_target = loadFile(conf["CetoniDeviceDriver"]["valves"])
        Channels_target = loadFile(conf["CetoniDeviceDriver"]["channels"])

        Pumps_result, Valves_result, Channels_result = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=conf["utility"]["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], pums=conf["CetoniDeviceDriver"]["pumps"], vals=conf["CetoniDeviceDriver"]["valves"], channls=conf["CetoniDeviceDriver"]["channels"])

        self.attributeComp(Pumps_result, Pumps_target)
        self.attributeComp(Valves_result, Valves_target)
        self.attributeComp(Channels_result, Channels_target)

        for key in Pumps_result.keys():
            self.assertEqual(first=Pumps_result[key].syringe.desig, second=Pumps_target[key].syringe.desig, msg="Designations do not match.")
            self.assertEqual(first=Pumps_result[key].syringe.inner_dia_mm, second=Pumps_target[key].syringe.inner_dia_mm, msg="Inner diameters do not match.")
            self.assertEqual(first=Pumps_result[key].syringe.piston_stroke_mm, second=Pumps_target[key].syringe.piston_stroke_mm, msg="Piston strokes do not match.")
            self.assertEqual(first=Pumps_result[key].syringe.minimum_volume_mL, second=Pumps_target[key].syringe.minimum_volume_mL, msg="Minimum volumes do not match.")
            self.assertEqual(first=Pumps_result[key].is_in_fault_state(), second=conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["faultState"], msg=f"Pump {key} is in fault state.")
            self.assertEqual(first=Pumps_result[key].is_enabled(), second=conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["enabled"], msg=f"Pump {key} is not enabled.")
            self.assertEqual(first=str(Pumps_result[key].get_syringe_param()), second=conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["syringeParams"][key]["params"], msg="Syringe parameters are not matching.")
            self.assertEqual(first=str(Pumps_result[key].get_volume_unit()), second=conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["syringeParams"][key]["volUnit"], msg="Volume units are not matching.")
            self.assertEqual(first=str(Pumps_result[key].get_flow_unit()), second=conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["syringeParams"][key]["flowUnit"], msg="Flow units are not matching.")

        for key in Valves_result.keys():
            self.assertEqual(first=Valves_result[key].actual_valve_position(), second=0, msg=f"Valve positions are not matching.")

        qmixbus.Bus.stop()
        qmixbus.Bus.close()

    def test_quitCetoni(self):
        qmixbus.Bus.open(conf["CetoniDeviceDriver"]["configPath"], conf["utility"]["QmixSDK"])
        qmixbus.Bus.start()

        CetoniDevice_driver.cetoni.quitCetoni()
        # TODO: Find a way to check if the bus communication is closed.

    def test_getValvePositions(self):
        Vs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=conf["utility"]["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], pums=conf["CetoniDeviceDriver"]["pumps"], vals=conf["CetoniDeviceDriver"]["valves"], channls=conf["CetoniDeviceDriver"]["channels"])[1]
        vPd = loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"])

        check = {}
        i = 0
        for v in Vs.keys():
            Vs[v].switch_valve_to_position(i)
            check[v] = i
            i+=1
        self.assertDictEqual(d1=CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=vPd), d2=check, msg=f"Valve positions do not match.")

        qmixbus.Bus.stop()
        qmixbus.Bus.close()

    def test_valve__init__(self):
        valv = CetoniDevice_driver.valveObj()
        functions = dir(valv)
        funcs = []
        for func in functions:
            if func[0:2] != "__":
                funcs.append(func)

        self.assertEqual(first=funcs, second=conf["CetoniDeviceDriver"]["outputTarget"]["valveInit"]["target"], msg=f"Attributes and methods do not match.")

    def test_pump__init__(self):
        pum = CetoniDevice_driver.pumpObj()
        functions = dir(pum)
        funcs = []
        for func in functions:
            if func[0:2] != "__":
                funcs.append(func)

        self.assertEqual(first=funcs, second=conf["CetoniDeviceDriver"]["outputTarget"]["pumpInit"]["target"], msg=f"Attributes and methods do not match.")


if __name__ == "__main__":
    unittest.main(verbosity=2)