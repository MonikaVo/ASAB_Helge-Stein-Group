from ASAB.test.FilesForTests import config_test
from ASAB.utility.helpers import loadTxtFile
conf = config_test.config

from ASAB.configuration import config
cf = config.configASAB

from ASAB.driver import CetoniDevice_driver
from qmixsdk import qmixbus

def attributeComp(result, target):
    for key in result.keys():
        attr = vars(result[key]).copy()
        attr.pop("handle")
        if "syringe" in attr:
            attr.pop("syringe")
        for attribute in attr:  # https://stackoverflow.com/questions/31368056/get-all-attributes-of-a-class-in-python#31368099
            if attribute in vars(target[key]):
                if attribute in vars(target[key]):
                    assert getattr(target[key], attribute) == getattr(result[key], attribute)    # https://stackoverflow.com/questions/2157035/accessing-an-attribute-using-a-variable-in-python
                else:
                    assert 1 == 0

# #TODO_ Generate new reference objects for pumps, valves and channels
# def test_prepareCetoni():
#     Pumps_target = loadFile(conf["CetoniDeviceDriver"]["pumps"])
#     Valves_target = loadFile(conf["CetoniDeviceDriver"]["valves"])
#     Channels_target = loadFile(conf["CetoniDeviceDriver"]["channels"])

#     Pumps_result, Valves_result, Channels_result = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"], save_name_pumps=conf["CetoniDeviceDriver"]["pumps"], save_name_valves=conf["CetoniDeviceDriver"]["valves"], save_name_channels=conf["CetoniDeviceDriver"]["channels"])

#     attributeComp(Pumps_result, Pumps_target)
#     attributeComp(Valves_result, Valves_target)
#     attributeComp(Channels_result, Channels_target)

#     for key in Pumps_result.keys():
#         assert(Pumps_result[key].syringe.desig == Pumps_target[key].syringe.desig)
#         assert(Pumps_result[key].syringe.inner_dia_mm == Pumps_target[key].syringe.inner_dia_mm)
#         assert(Pumps_result[key].syringe.piston_stroke_mm == Pumps_target[key].syringe.piston_stroke_mm)
#         assert(Pumps_result[key].syringe.minimum_volume_mL == Pumps_target[key].syringe.minimum_volume_mL)
#         assert(Pumps_result[key].is_in_fault_state() == conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["faultState"])
#         assert(Pumps_result[key].is_enabled() == conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["enabled"])
#         assert(str(Pumps_result[key].get_syringe_param()) == conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["syringeParams"][key]["params"])
#         assert(str(Pumps_result[key].get_volume_unit()) == conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["syringeParams"][key]["volUnit"], "Volume units are not matching.")
#         assert(str(Pumps_result[key].get_flow_unit()) == conf["CetoniDeviceDriver"]["outputTarget"]["prepareCetoni"]["syringeParams"][key]["flowUnit"], "Flow units are not matching.")

#     for key in Valves_result.keys():
#         assert(Valves_result[key].actual_valve_position() == 0, f"Valve positions are not matching.")

#     qmixbus.Bus.stop()
#     qmixbus.Bus.close()

def test_quitCetoni():
    qmixbus.Bus.open(conf["CetoniDeviceDriver"]["configPath"], cf["QmixSDK"])
    qmixbus.Bus.start()

    CetoniDevice_driver.cetoni.quitCetoni()
    # TODO: Find a way to check if the bus communication is closed.

def test_getValvePositions():
    Vs = CetoniDevice_driver.cetoni.prepareCetoni(config_path=conf["CetoniDeviceDriver"]["configPath"], QmixSDK_path=cf["QmixSDK"], available_syringes=conf["CetoniDeviceDriver"]["availableSyringes"], syringe_config=conf["CetoniDeviceDriver"]["syringeConfig"], save_name_VdP=conf["CetoniDeviceDriver"]["valvePositionDict"])[1]
    vPd = CetoniDevice_driver.getValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"])

    check = {}
    i = 0
    for v in Vs.keys():
        Vs[v].switch_valve_to_position(i)
        check[v] = i
        i+=1
    assert CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Vs, valvePositionDict=vPd) == check, f"Valve positions do not match."

    qmixbus.Bus.stop()
    qmixbus.Bus.close()

def test_valve__init__():
    valv = CetoniDevice_driver.valveObj()
    functions = dir(valv)
    funcs = []
    for func in functions:
        if func[0:2] != "__":
            funcs.append(func)

    print(funcs)

    assert funcs == conf["CetoniDeviceDriver"]["outputTarget"]["valveInit"]["target"], f"Attributes and methods do not match."

def test_pump__init__():
    pum = CetoniDevice_driver.pumpObj()
    functions = dir(pum)
    funcs = []
    for func in functions:
        if func[0:2] != "__":
            funcs.append(func)

    assert funcs == conf["CetoniDeviceDriver"]["outputTarget"]["pumpInit"]["target"], f"Attributes and methods do not match."