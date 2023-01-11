from ASAB.test.FilesForTests import config_test
from ASAB.utility.helpers import loadVariable
conf = config_test.config

# Imports from ASAB
from ASAB.utility import syringes

# Other imports
import numpy as np

def test__init__():
    # initialise test syringe
    syr1 = syringes.Syringe(desig=conf["test_syringes"]["testInit"][0]["designation"], inner_dia_mm=conf["test_syringes"]["testInit"][0]["innerDia"], piston_stroke_mm=conf["test_syringes"]["testInit"][0]["pistonStroke"])
    
    # get the target attributes
    desig_target = conf["test_syringes"]["testInit"][0]["designation"]
    innerDia_target = conf["test_syringes"]["testInit"][0]["innerDia"]
    pistonStroke_target = conf["test_syringes"]["testInit"][0]["pistonStroke"]
    minVol_target = np.around(((np.pi*(syr1.inner_dia_mm/2.)**2.*syr1.piston_stroke_mm)/1000.) * 0.15, 4)
    minFlow_target = (np.pi * (syr1.inner_dia_mm/2.)**2. * (1.042/1000.))/1000.
    maxFlow_target = ((np.pi * (syr1.inner_dia_mm/2.)**2. * (6.33))/1000.)

    # check all the attributes
    assert syr1.desig == desig_target, f"The designation is {syr1.desig} instead of {desig_target}."
    assert syr1.inner_dia_mm == innerDia_target, f"IThe iner diameter is {syr1.inner_dia_mm} instead of {innerDia_target}."
    assert syr1.piston_stroke_mm == pistonStroke_target, f"The piston Stroke is {syr1.piston_stroke_mm} instead of {pistonStroke_target}."
    assert syr1.minimum_volume_mL == minVol_target, f"The minimum volume is {syr1.minimum_volume_mL} instead of {minVol_target}."
    assert syr1.minimum_flow_mL_per_sec == minFlow_target, f"The minimum flow is {syr1.minimum_flow_mL_per_sec} instead of {minFlow_target}."
    assert syr1.maximum_flow_mL_per_sec == maxFlow_target, f"The maximum flow is {syr1.maximum_flow_mL_per_sec} instead of {maxFlow_target}."

def test_from_dict():
    # instantiate the syringe object to be tested
    syr = syringes.from_dict(dict=conf["test_syringes"]['testFromDict']['dict'])

    # get the target attributes
    desig_target = conf["test_syringes"]['testFromDict']['dict']['desig']
    innerDia_target = conf["test_syringes"]['testFromDict']['dict']['inner_dia_mm']
    pistonStroke_target = conf["test_syringes"]['testFromDict']['dict']['piston_stroke_mm']
    minVol_target = np.around(((np.pi*(syr.inner_dia_mm/2.)**2.*syr.piston_stroke_mm)/1000.) * 0.15, 4)
    minFlow_target = (np.pi * (syr.inner_dia_mm/2.)**2. * (1.042/1000.))/1000.
    maxFlow_target = (np.pi * (syr.inner_dia_mm/2.)**2. * (6.33))/1000.

    # check all the attributes
    assert syr.desig == desig_target, f"The designation is {syr.desig} instead of {desig_target}."
    assert syr.inner_dia_mm == innerDia_target, f"IThe iner diameter is {syr.inner_dia_mm} instead of {innerDia_target}."
    assert syr.piston_stroke_mm == pistonStroke_target, f"The piston Stroke is {syr.piston_stroke_mm} instead of {pistonStroke_target}."
    assert syr.minimum_volume_mL == minVol_target, f"The minimum volume is {syr.minimum_volume_mL} instead of {minVol_target}."
    assert syr.minimum_flow_mL_per_sec == minFlow_target, f"The minimum flow is {syr.minimum_flow_mL_per_sec} instead of {minFlow_target}."
    assert syr.maximum_flow_mL_per_sec == maxFlow_target, f"The maximum flow is {syr.maximum_flow_mL_per_sec} instead of {maxFlow_target}."


def test_loadSyringeDict():
    # instantiate the syringe object to be tested
    syrDict_result = syringes.loadSyringeDict(path_to_syringeDict=conf["syringes"]["savePath"])

    # get the dictionary for each syringe by loading the file and reading it as a dictionary
    syrDict_target = loadVariable(loadPath=conf["syringes"]["savePath"], variable='Syringes')

    # check, that all keys are present in the dicitionary
    assert syrDict_result.keys() == syrDict_target.keys(), f"The keys are {syrDict_result.keys()} instead of {syrDict_target.keys()}."

    # check each element in the syrDict_result
    for k in syrDict_result.keys():
        # get the respective syringe object
        syr = syrDict_result[k]

        # get the target attributes
        desig_target = syrDict_target[k]['desig']
        innerDia_target = syrDict_target[k]['inner_dia_mm']
        pistonStroke_target = syrDict_target[k]['piston_stroke_mm']
        minVol_target = syrDict_target[k]['minimum_volume_mL']
        minFlow_target = syrDict_target[k]['minimum_flow_mL_per_sec']
        maxFlow_target = syrDict_target[k]['maximum_flow_mL_per_sec']

        # check all the attributes
        assert syr.desig == desig_target, f"The designation is {syr.desig} instead of {desig_target}."
        assert syr.inner_dia_mm == innerDia_target, f"IThe iner diameter is {syr.inner_dia_mm} instead of {innerDia_target}."
        assert syr.piston_stroke_mm == pistonStroke_target, f"The piston Stroke is {syr.piston_stroke_mm} instead of {pistonStroke_target}."
        assert syr.minimum_volume_mL == minVol_target, f"The minimum volume is {syr.minimum_volume_mL} instead of {minVol_target}."
        assert syr.minimum_flow_mL_per_sec == minFlow_target, f"The minimum flow is {syr.minimum_flow_mL_per_sec} instead of {minFlow_target}."
        assert syr.maximum_flow_mL_per_sec == maxFlow_target, f"The maximum flow is {syr.maximum_flow_mL_per_sec} instead of {maxFlow_target}."

