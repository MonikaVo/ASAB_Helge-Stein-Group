from ctypes import c_longlong
from numpy import float64
from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.configuration import config
cf = config.configASAB

# Imports from ASAB
from ASAB.driver import CetoniDevice_driver, Arduino_driver

# Imports from QmixSDK
from qmixsdk import qmixbus, qmixvalve, qmixpump, qmixcontroller

# Other imports
from inspect import getmembers
from pytest import raises
from os import remove
from pathlib import Path

### Methods providing functionalities required to facilitate testing #########################################################################################################################################################################

def referenceObjects(obj, filename:str, result=None) -> None:
    ''' This function helps in defining dictionaries of reference objects, which can be used to compare, whether the attributes are assigned correctly to the objects.
    This function shall only be used for the setup and is not intended to be used in the actual test.
    Inputs:
    filename: a string defining the filename to use when saving the generated reference object
    results: a dictionary of already identified objects, which is used to unravel nested dictionaries. For the top level dictionary, this parameter is None.
    
    Outputs:
    This function returns nothing, but save the files as requested. '''
    
    if result==None:
        result = {}
    for k in obj.keys():
        result[k] = {}
        print('k', k)
        for l in vars(obj[k]).keys():
            if type(vars(obj[k])[l]) in [str, list, dict, int, float, c_longlong, float64]:
                result[k][l] = vars(obj[k])[l]
            else:
                result[k][l] = {}
                referenceObjects(obj={l: vars(obj[k])[l]}, result=result[k], filename=filename)
        print(k, result)
    with open(str(Path(__file__).resolve().parent.joinpath("FilesForTests", f"{filename}_test.txt")), 'w') as f:
        f.write(str(result))

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

def checkObject_vs_dict(obj:object, refDict:dict):
    for key in obj.keys():
        # Assure that all elements are there
        assert key in refDict.keys(), f'The key {key} is not in the reference dictionary with keys {refDict.keys()}.'
        for key2 in vars(obj[key]).keys():
            # Assure that the respective attribute is in both lists
            assert key2 in refDict[key].keys(), f'The key2 {key2} is not in the reference dictionary with keys {refDict[key].keys()}.'
            # Skip the handle as this changes everytime upon renewed connection to the system.
            if key2 != 'handle':
                if type(vars(obj[key])[key2]) in [str, list, dict, int, float, c_longlong, float64]:
                    # assert that the values are identical
                    assert vars(obj[key])[key2] == refDict[key][key2], f'The value of {key2} is {vars(obj[key])[key2]} and not {refDict[key][key2]} as it was expected.'
                else:
                    checkObject_vs_dict(obj={key2: vars(obj[key])[key2]}, refDict={key2: refDict[key][key2]})

### Test functions ###################################################################################################################################################################################################################################

def test_valve_init():
    # create the object to test
    valve_result = CetoniDevice_driver.valveObj(valveType='rotary', name='Test_valve1')
    
    # create a reference object from the Cetoni funciton
    valve_target = qmixvalve.Valve()
    valve_target.name = 'Test_valve1'
    valve_target.valveType = 'rotary'

    # assert the correctness of the name and the type
    assert valve_result.name == valve_target.name, f"The name is {valve_result.name} instead of {valve_target.name}."
    assert valve_result.valveType == valve_target.valveType, f"The name is {valve_result.valveType} instead of {valve_target.valveType}."

    # get the target values from the reference valve
    targets_list = dict(getmembers(valve_target))

    # get the results
    results_list = dict(getmembers(valve_result))

    # ensure, that results and targets have the same keys
    for k in targets_list.keys():
        # check
        assert k in results_list.keys(), f"The member {k} is available in the targets, but not in the results."

def test_valve_open():
    # Open the BUS communication using the test config file
    qmixbus.Bus.open(conf["CetoniDeviceDriver"]["configPath"], cf["QmixSDK"])

    # create a test object as a NemeSys S valve, which has an open position
    valve_withOpen = CetoniDevice_driver.valveObj()
    valve_withOpen.lookup_by_name('Nemesys_S_1_Valve')
    # label it with it's type
    valve_withOpen.type = 'pumpValve_conti'

    # create a second test object as a regular NemeSys low pressure valve, which has no open position
    valve_noOpen = CetoniDevice_driver.valveObj()
    valve_noOpen.lookup_by_name('neMESYS_Low_Pressure_1_Valve')
    valve_noOpen.type = 'pumpValve'

    # set the devices operational
    qmixbus.Bus.start()

    ## Test case 1: The valve has an open position

    # Switch the valve with an open position to position 0
    valve_withOpen.switch_valve_to_position(0)

    # switch the valve with an open position to the open position using the function to test
    valve_withOpen.open()

    # check, that the valve changed it's position to ensure it was not already in the open position
    actualValvePos = valve_withOpen.actual_valve_position()

    # check, that the valve providing an open position is open after switching
    assert actualValvePos == 3, f"The actual valve position after switching is {actualValvePos} instead of 2."

    ## Test case 2: The valve has no open position
    
    # Switch the valve witout an open position to position 0
    valve_noOpen.switch_valve_to_position(0)

    # switch the valve without an open position to the open position using the function to test and make sure it raises an error
    with raises(AttributeError):
        valve_noOpen.open()

    # Stop and close the BUS communication
    qmixbus.Bus.stop()
    qmixbus.Bus.close()

def test_valve_close():
    # Open the BUS communication using the test config file
    qmixbus.Bus.open(conf["CetoniDeviceDriver"]["configPath"], cf["QmixSDK"])

    # create a test object as a NemeSys S valve, which has an close position
    valve_withClose = CetoniDevice_driver.valveObj()
    valve_withClose.lookup_by_name('Nemesys_S_1_Valve')
    # label it with it's type
    valve_withClose.type = 'pumpValve_conti'

    # create a second test object as a regular NemeSys low pressure valve, which has no close position
    valve_noClose = CetoniDevice_driver.valveObj()
    valve_noClose.lookup_by_name('neMESYS_Low_Pressure_1_Valve')
    valve_noClose.type = 'pumpValve'

    # set the devices operational
    qmixbus.Bus.start()

    ## Test case 1: The valve has an close position

    # Switch the valve with an close position to position 0
    valve_withClose.switch_valve_to_position(0)

    # switch the valve with an close position to the close position using the function to test
    valve_withClose.close()

    # check, that the valve changed it's position to ensure it was not already in the close position
    actualValvePos = valve_withClose.actual_valve_position()

    # check, that the valve providing an close position is close after switching
    assert actualValvePos == 0, f"The actual valve position after switching is {actualValvePos} instead of 3."

    ## Test case 2: The valve has no close position
    
    # Switch the valve witout an close position to position 0
    valve_noClose.switch_valve_to_position(0)

    # switch the valve without an close position to the close position using the function to test and make sure it raises an error
    with raises(AttributeError):
        valve_noClose.close()

    # Stop and close the BUS communication
    qmixbus.Bus.stop()
    qmixbus.Bus.close()

def test_pump_init():
    # create the object to test
    pump_result = CetoniDevice_driver.pumpObj(name='Test_pump1', pumpType='test_pump')
    
    # create a reference object from the Cetoni funciton
    pump_target = qmixpump.Pump()
    pump_target.name = 'Test_pump1'
    pump_target.pumpType = 'test_pump'

    # assert the correctness of the name and the type
    assert pump_result.name == pump_target.name, f"The name is {pump_result.name} instead of {pump_target.name}."

    # get the target values from the reference pump
    targets_list = dict(getmembers(pump_target))

    # get the results
    results_list = dict(getmembers(pump_result))

    # ensure, that results and targets have the same keys
    for k in targets_list.keys():
        # check
        assert k in results_list.keys(), f"The member {k} is available in the targets, but not in the results."

def test_loadValvePositionDict():
    # print a hint towards a missing vPd file, in case the test fails
    print("If this fails, the vPd file might be missing in the 'experiment folder'. Run all tests for CDD again to check, if it works after a vPd file is created.")

    # get the test vPd by loading it from the respective file
    vPd_loaded = CetoniDevice_driver.loadValvePositionDict(conf['CetoniDeviceDriver']['valvePositionDict'])

    # get the target vPd
    vPd_target = conf['test_CetoniDeviceDriver']['valvePositionDict_target']

    # check, that the loaded vPd corresponds to the target one
    assert vPd_loaded == vPd_target, f'The loaded valvePositionDict is {vPd_loaded} instead of {vPd_target}.'

def test_getValvePositionDict():
    # print a hint towards a missing vPd file, in case the test fails
    print("If this fails, the vPd file might be missing in the 'experiment folder'. Run all tests for CetoniDevice_driver again to check, if it works after a vPd file is created.")

    # create the target vPd
    vPd_target = conf['test_CetoniDeviceDriver']['valvePositionDict_target']

    # create one str input, one dict input and one with neither of those types
    vPd_str = conf['CetoniDeviceDriver']['valvePositionDict']

    vPd_dict = {'Av': {'Av.0': 1, 'Av.1': 2}, 'V1': {'V1.1': 0, 'V1.2': 1, 'V1.3': 2, 'V1.4': 3, 'V1.5': 4, 'V1.6': 5, 'V1.7': 6, 'V1.8': 7, 'V1.9': 8, 'V1.10': 9}, 'V2': {'V2.1': 0, 'V2.2': 1, 'V2.3': 2, 'V2.4': 3, 'V2.5': 4, 'V2.6': 5, 'V2.7': 6, 'V2.8': 7, 'V2.9': 8, 'V2.10': 9}, 'V3': {'V3.1': 0, 'V3.2': 1, 'V3.3': 2, 'V3.4': 3, 'V3.5': 4, 'V3.6': 5, 'V3.7': 6, 'V3.8': 7, 'V3.9': 8, 'V3.10': 9}, 'V4': {'V4.1': 0, 'V4.2': 1, 'V4.3': 2, 'V4.4': 3, 'V4.5': 4, 'V4.6': 5, 'V4.7': 6, 'V4.8': 7, 'V4.9': 8, 'V4.10': 9}, 'V5': {'V5.1': 0, 'V5.2': 1, 'V5.3': 2, 'V5.4': 3, 'V5.5': 4, 'V5.6': 5, 'V5.7': 6, 'V5.8': 7, 'V5.9': 8, 'V5.10': 9}, 'Bv': {'Bv.0': 0, 'Bv.1': 1}, 'Cv': {'Cv.0': 0, 'Cv.1': 1}, 'ArdV_0_1': {'ArdV_0_1.0': 0, 'ArdV_0_1.1': 1}}

    vPd_wrongType = 1

    vPd_wrongStr = 'This is a test string, but not a path.'

    # get the vPd by loading from a file and check it against the target
    vPd_loaded_result = CetoniDevice_driver.getValvePositionDict(vPd = vPd_str)
    assert vPd_loaded_result == vPd_target, f"The valvePositionDict loaded from the given string is {vPd_loaded_result} instead of {vPd_target}."

    # get the vPd by returning the input and check it against the target
    vPd_returnInput_result = CetoniDevice_driver.getValvePositionDict(vPd= vPd_dict)
    assert vPd_returnInput_result == vPd_target, f"The valvePositionDict returned is {vPd_loaded_result} instead of {vPd_target}."

    # input has the wrong type
    with raises(TypeError):
        CetoniDevice_driver.getValvePositionDict(vPd= vPd_wrongType)

    # input has the wrong type
    with raises(ValueError):
        CetoniDevice_driver.getValvePositionDict(vPd= vPd_wrongStr)

# def test_cetoni__init__():
#     pass

def test_prepareCetoni():
    # clear the vPd file, which will be produced during the prepration prior to starting the test
    if Path(conf['CetoniDeviceDriver']['valvePositionDict']).is_file():
        remove(conf['CetoniDeviceDriver']['valvePositionDict'])

    # call the preparation funciton
    Pumps, Valves, Channels = CetoniDevice_driver.cetoni.prepareCetoni()

    ## Check for existence and correctness of the vPd

    # check, if the vPd is present in the expected directory and with the correct filename
    assert Path(conf['CetoniDeviceDriver']['valvePositionDict']).is_file(), f"The file does not exist"

    # get the target for the vPd
    vPd_prepare_target = conf['test_CetoniDeviceDriver']['valvePositionDict_target']

    # load the created vPd
    vPd_prepare_result = CetoniDevice_driver.loadValvePositionDict(path_to_ValvePositionDict=conf['CetoniDeviceDriver']['valvePositionDict'])

    # check, that the result equals the target
    assert vPd_prepare_result == vPd_prepare_target, f"The valvePositionDict is {vPd_prepare_result} instead of {vPd_prepare_target}."

    ## Ensure, that all pumps, valves and channels in the returned dictionaries have the correct type and the correct setting
    ## for the most important attributes

    ### Pumps
    
    # go through all pumps
    for p in Pumps.keys():
        # ensure that they are of type pumpObj
        assert type(Pumps[p]) == CetoniDevice_driver.pumpObj, f"The type of the entry {p} in the pumps dictionary is {type(Pumps[p])} instead of CetoniDevice_driver.pumpObj."
        # ensure fault state, enabled, syringe parameters, volume unit and flow unit
        assert Pumps[p].is_in_fault_state() == False, f'The pump {p} is in fault state.'
        assert Pumps[p].is_enabled() == True, f'The pump {p} is not enabled.'
        assert str(Pumps[p].get_syringe_param()) == conf['test_CetoniDeviceDriver']['prepareCetoni']['syringeParams'][p]['params'], f"The syringe parameters are {str(Pumps[p].get_syringe_param())} instead of {conf['test_CetoniDeviceDriver']['prepareCetoni']['syringeParams'][p]['params']}."
        assert str(Pumps[p].get_volume_unit()) == conf['test_CetoniDeviceDriver']['prepareCetoni']['syringeParams'][p]['volUnit'], f"The volume unit is {str(Pumps[p].get_volume_unit())} instead of {conf['test_CetoniDeviceDriver']['prepareCetoni']['syringeParams'][p]['volUnit']}."
        assert str(Pumps[p].get_flow_unit()) == conf['test_CetoniDeviceDriver']['prepareCetoni']['syringeParams'][p]['flowUnit'], f"The flow unit is {str(Pumps[p].get_flow_unit())} instead of {conf['test_CetoniDeviceDriver']['prepareCetoni']['syringeParams'][p]['flowUnit']}."

    ### Valves

    # go through all valves
    for v in Valves.keys():
        if ("Ard" not in v):
            # ensure that they are of type valveObj
            assert type(Valves[v]) == CetoniDevice_driver.valveObj, f"The type of the entry {v} in the valves dictionary is {type(Valves[v])} instead of CetoniDevice_driver.valveObj."
        else:
            # ensure, that the valve is of type ArduinoValve
            assert type(Valves[v]) == Arduino_driver.ArduinoValve, f"The type of the entry {v} in the valves dictionary is {type(Valves[v])} instead of CetoniDevice_driver.valveObj."
        # ensure that the valve has the correct valve position
        if Valves[v].valveType != "pump_conti":
            assert Valves[v].actual_valve_position() == 0, f"The valve position of valve {v} is {Valves[v].actual_valve_position()} instead of 0."
        else:
            assert Valves[v].actual_valve_position() == 1, f"The valve position of valve {v} is {Valves[v].actual_valve_position()} instead of 1."

    ### Channels

    for c in Channels.keys():
        # ensure that they are of type qmixcontroller.ControllerChannel
        assert type(Channels[c]) == qmixcontroller.ControllerChannel, f"The type of the entry {c} in the chanels dictionary is {type(Channels[c])} instead of qmixcontroller.ControllerChannel."

    ## Ensure, that the BUS is open
    #TODO: find a way to check, if the BUS is open.

    # disconnect from the device
    qmixbus.Bus.stop()
    qmixbus.Bus.close()

def test_quitCetoni():
    qmixbus.Bus.open(conf["CetoniDeviceDriver"]["configPath"], cf["QmixSDK"])
    qmixbus.Bus.start()

    CetoniDevice_driver.cetoni.quitCetoni()
    # TODO: Find a way to check if the bus communication is closed.

def test_pumpingPumps():
    # prepare the Cetoni device
    Pumps3, Valves3, Channels3 = CetoniDevice_driver.cetoni.prepareCetoni()

    # make some pumps pumping and get the target list of pumps, which should be pumping
    pumpingPs_target = conf['test_CetoniDeviceDriver']['pumpingPumps_target']
    for p in pumpingPs_target:
        Pumps3[p].set_fill_level(Pumps3[p].get_volume_max(), conf['CetoniDeviceDriver']['flow'])

    # apply the function to identify pumping pumps
    pumpingPs_results = CetoniDevice_driver.cetoni.pumpingPumps(Pumps3)

    print(pumpingPs_results)
    # check the result against the target
    assert pumpingPs_results == pumpingPs_target, f"The list of pumping pumps is {pumpingPs_results} instead of {pumpingPs_target}."
    
    # disconnect from the device
    qmixbus.Bus.stop()
    qmixbus.Bus.close()

def test_getValvePositions():
    Pumps2, Valves2, Channels2 = CetoniDevice_driver.cetoni.prepareCetoni()
    vPd = CetoniDevice_driver.getValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"])

    check = {}
    i = 0
    print(Valves2.keys())
    for v in Valves2.keys():
        positionsNo = Valves2[v].number_of_valve_positions()
        if i < positionsNo:
            Valves2[v].switch_valve_to_position(i)
            check[v] = i
        else:
            Valves2[v].switch_valve_to_position(positionsNo-1)
            check[v] = positionsNo-1
        i+=1
    print(check)
    assert CetoniDevice_driver.cetoni.getValvePositions(valvesDict=Valves2, valvePositionDict=vPd) == check, f"Valve positions do not match."

    # disconnect from the device
    qmixbus.Bus.stop()
    qmixbus.Bus.close()
