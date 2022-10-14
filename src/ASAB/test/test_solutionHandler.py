from ASAB.driver.CetoniDevice_driver import cetoni
from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.configuration import config
cf = config.configASAB

from ASAB.utility import solutionHandler

from glob import glob
from os import remove
import numpy as np

print("\n Test of functions in soltuionHandler.py. \n")

### Chemicals #############################################################################################################################################################

def test_chemical_init():
    test_chemical = conf['test_solutionHandler']['chemical_test']

    # Collect the target values
    name_target = test_chemical['name']
    molarMass_target = test_chemical['molarMass']
    molarMassUncertainty_target = test_chemical['molarMassUncertainty']
    molarMassUnit_target = conf['solutionHandler']['units']['molarMass']
    density_target = test_chemical['density']
    densityUncertainty_target = test_chemical['densityUncertainty']
    densityUnit_target = conf['solutionHandler']['units']['density']

    chem = solutionHandler.Chemical(name=test_chemical['name'], molarMass=test_chemical['molarMass'], molarMassUncertainty=test_chemical['molarMassUncertainty'], molarMassUnit=conf['solutionHandler']['units']['molarMass'], density=test_chemical['density'], densityUncertainty=test_chemical['densityUncertainty'], densityUnit=conf['solutionHandler']['units']['density'])

    assert name_target == chem.name, f"The name is {chem.name} instead of {name_target}."
    assert molarMass_target == chem.molarMass, f"The molar mass is {chem.molarMass} instead of {molarMass_target}."
    assert molarMassUncertainty_target == chem.molarMassUncertainty, f"The molar mass uncertainty is {chem.molarMassUncertainty} instead of {molarMassUncertainty_target}."
    assert molarMassUnit_target == chem.molarMassUnit, f"The molar mass unit is {chem.molarMassUnit} instead of {molarMassUnit_target}."
    assert density_target == chem.density, f"The density is {chem.density} instead of {density_target}."
    assert densityUncertainty_target == chem.densityUncertainty, f"The density uncertainty is {chem.densityUncertainty} instead of {densityUncertainty_target}."
    assert densityUnit_target == chem.densityUnit, f"The density unit is {chem.densityUnit} instead of {densityUnit_target}."

def test_generateChemicalsDict():
    # Get the target dictionary
    chemicalsDict_target_dict = conf['test_solutionHandler']['chemicalsDict_target']
    chemicalsDict_target = {}
    for chem in chemicalsDict_target_dict.keys():
        chemicalInfo = chemicalsDict_target_dict[chem]
        chemicalsDict_target[chem] = solutionHandler.Chemical(name=chemicalInfo['name'], molarMass=chemicalInfo['molarMass'], molarMassUncertainty=chemicalInfo['molarMassUncertainty'], molarMassUnit=chemicalInfo['molarMassUnit'], density=chemicalInfo['density'], densityUncertainty=chemicalInfo['densityUncertainty'], densityUnit=chemicalInfo['densityUnit'])

    # Get the resulting dictionary
    chemicalsDict_result = solutionHandler.generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'], savePath=conf['solutionHandler']['chemicalsDict'])
    
    for c in chemicalsDict_result.keys():
        for a in chemicalsDict_target_dict[c].keys():
            assert getattr(chemicalsDict_target[c], a) == getattr(chemicalsDict_result[c], a), f"The {a} is {getattr(chemicalsDict_result[c], a)} instead of {getattr(chemicalsDict_target[c], a)}."

def test_chemicalFromDict():
    # Get the dictionary of the target
    chemicalsDict_target_dict2 = conf['test_solutionHandler']['chemicalsDict_target']

    # Get the target object directly from generation
    chemicalsDict_generated_target = solutionHandler.generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'], savePath=conf['solutionHandler']['chemicalsDict'])

    # Get the resulting objects from a dictionary
    chemicalsDict_dictionary_result = {}
    for key in chemicalsDict_target_dict2.keys():
        chemicalsDict_dictionary_result[key] = solutionHandler.chemical_from_dict(chemicalsDict_target_dict2[key])

    for c in chemicalsDict_dictionary_result.keys():
        for a in chemicalsDict_target_dict2[c].keys():
            assert getattr(chemicalsDict_generated_target[c], a) == getattr(chemicalsDict_dictionary_result[c], a), f"The {a} is {getattr(chemicalsDict_dictionary_result[c], a)} instead of {getattr(chemicalsDict_generated_target[c], a)}."

def test_loadChemicalsDict():
    # Get the dictionary of the target
    chemicalsDict_target_dict2 = conf['test_solutionHandler']['chemicalsDict_target']

    # Get the target object directly from generation
    chemicalsDict_generated_target2 = solutionHandler.generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'], savePath=conf['solutionHandler']['chemicalsDict'])

    # Get the resulting objects from loading the dictionary
    chemicalsDict_loaded_result = solutionHandler.loadChemicalsDict(chemicalsDict_path=conf['solutionHandler']['chemicalsDict'])

    for c in chemicalsDict_loaded_result.keys():
        for a in chemicalsDict_target_dict2[c].keys():
            assert getattr(chemicalsDict_generated_target2[c], a) == getattr(chemicalsDict_loaded_result[c], a), f"The {a} is {getattr(chemicalsDict_loaded_result[c], a)} instead of {getattr(chemicalsDict_generated_target2[c], a)}."

def test_getChemicalsDict():
    # Get the dictionary of the target
    chemicalsDict_target_dict3 = conf['test_solutionHandler']['chemicalsDict_target']

    # Get the target object directly from generation
    chemicalsDict_generated_target3 = solutionHandler.generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'], savePath=conf['solutionHandler']['chemicalsDict'])

    # Get the resulting object when passing a dict
    chemicalsDict_dict_result = solutionHandler.get_chemicalsDict(chemicalsDict=chemicalsDict_generated_target3)

    # Get the resulting object when passing a str
    chemicalsDict_str_result = solutionHandler.get_chemicalsDict(chemicalsDict=conf['solutionHandler']['chemicalsDict'])

    for c in chemicalsDict_dict_result.keys():
        for a in chemicalsDict_target_dict3[c].keys():
            assert getattr(chemicalsDict_generated_target3[c], a) == getattr(chemicalsDict_dict_result[c], a), f"The {a} is {getattr(chemicalsDict_dict_result[c], a)} instead of {getattr(chemicalsDict_generated_target3[c], a)}."

    for c in chemicalsDict_str_result.keys():
        for a in chemicalsDict_target_dict3[c].keys():
            assert getattr(chemicalsDict_generated_target3[c], a) == getattr(chemicalsDict_str_result[c], a), f"The {a} is {getattr(chemicalsDict_str_result[c], a)} instead of {getattr(chemicalsDict_generated_target3[c], a)}."


### Solutions #############################################################################################################################################################

def test_solution_init():
    test_solution = conf['test_solutionHandler']['solution_test']

    # Collect the target values
    name_target = test_solution['name']
    chemicalMasses_target = test_solution['chemicalMasses']
    chemicalMassesUncertainties_target = test_solution['chemicalMassesUncertainties']
    mass_target = test_solution['mass']
    massUncertainty_target = test_solution['massUncertainty']
    massUnit_target = test_solution['massUnit']
    reservoir_target = test_solution['reservoir']
    pump_target = test_solution['pump']
    density_target = test_solution['density']
    densityUncertainty_target = test_solution['densityUncertainty']
    densityUnit_target = test_solution['densityUnit']

    # Generate test object substanceAmountPerVolume = None
    substanceAmountPerVolume1 = None
    sol_None = solutionHandler.Solution(name=test_solution['name'], chemicalMasses=test_solution['chemicalMasses'], chemicalMassesUncertainties=test_solution['chemicalMassesUncertainties'], mass=test_solution['mass'], massUncertainty=test_solution['massUncertainty'], massUnit=test_solution['massUnit'], reservoir=test_solution['reservoir'], pump=test_solution['pump'], densityUncertainty=test_solution['densityUncertainty'], density=test_solution['density'], densityUnit=test_solution['densityUnit'], substanceAmountPerVolume=substanceAmountPerVolume1)

    assert name_target == sol_None.name, f"The name is {sol_None.name} instead of {name_target}."
    assert chemicalMasses_target == sol_None.chemicalMasses, f"The chemical masses are {sol_None.chemicalMasses} instead of {chemicalMasses_target}."
    assert chemicalMassesUncertainties_target == sol_None.chemicalMassesUncertainties, f"The uncertainties of the chemical masses are {sol_None.chemicalMassesUncertainties} instead of {chemicalMassesUncertainties_target}."
    assert mass_target == sol_None.mass, f"The mass is {sol_None.mass} instead of {mass_target}."
    assert massUncertainty_target == sol_None.massUncertainty, f"The uncertainty of the mass is {sol_None.massUncertainty} instead of {massUncertainty_target}."
    assert massUnit_target == sol_None.massUnit, f"The unit of the mass is {sol_None.massUnit} instead of {massUnit_target}."
    assert reservoir_target == sol_None.reservoir, f"The reservoir is {sol_None.reservoir} instead of {reservoir_target}."
    assert pump_target == sol_None.pump, f"the pump is {sol_None.pump} instead of {pump_target}."
    assert density_target == sol_None.density, f"The density is {sol_None.density} instead of {density_target}."
    assert densityUncertainty_target == sol_None.densityUncertainty, f"The density uncertainty is {sol_None.densityUncertainty} instead of {densityUncertainty_target}."
    assert densityUnit_target == sol_None.densityUnit, f"The density unit is {sol_None.densityUnit} instead of {densityUnit_target}."
    assert test_solution['chemicals'] == sol_None.chemicals, f"The chemicals are {sol_None.chemicals} instead of {test_solution['chemicals']}"
    assert {} == sol_None.substanceAmountPerVolume, f"The substanceAmountPerVolume is {sol_None.substanceAmountPerVolume} instead of an empty dictionary."

    # Generate test object substanceAmountPerVolume = substanceAmountPerVolume
    substanceAmountPerVolume2 = conf['test_solutionHandler']['substanceAmountPerVolume_target']
    sol_sapv = solutionHandler.Solution(name=test_solution['name'], chemicalMasses=test_solution['chemicalMasses'], chemicalMassesUncertainties=test_solution['chemicalMassesUncertainties'], mass=test_solution['mass'], massUncertainty=test_solution['massUncertainty'], massUnit=test_solution['massUnit'], reservoir=test_solution['reservoir'], pump=test_solution['pump'], densityUncertainty=test_solution['densityUncertainty'], density=test_solution['density'], densityUnit=test_solution['densityUnit'], substanceAmountPerVolume=substanceAmountPerVolume2)

    assert name_target == sol_sapv.name, f"The name is {sol_sapv.name} instead of {name_target}."
    assert chemicalMasses_target == sol_sapv.chemicalMasses, f"The chemical masses are {sol_sapv.chemicalMasses} instead of {chemicalMasses_target}."
    assert chemicalMassesUncertainties_target == sol_sapv.chemicalMassesUncertainties, f"The uncertainties of the chemical masses are {sol_sapv.chemicalMassesUncertainties} instead of {chemicalMassesUncertainties_target}."
    assert mass_target == sol_sapv.mass, f"The mass is {sol_sapv.mass} instead of {mass_target}."
    assert massUncertainty_target == sol_sapv.massUncertainty, f"The uncertainty of the mass is {sol_sapv.massUncertainty} instead of {massUncertainty_target}."
    assert massUnit_target == sol_sapv.massUnit, f"The unit of the mass is {sol_sapv.massUnit} instead of {massUnit_target}."
    assert reservoir_target == sol_sapv.reservoir, f"The reservoir is {sol_sapv.reservoir} instead of {reservoir_target}."
    assert pump_target == sol_sapv.pump, f"the pump is {sol_sapv.pump} instead of {pump_target}."
    assert density_target == sol_sapv.density, f"The density is {sol_sapv.density} instead of {density_target}."
    assert densityUncertainty_target == sol_sapv.densityUncertainty, f"The density uncertainty is {sol_sapv.densityUncertainty} instead of {densityUncertainty_target}."
    assert densityUnit_target == sol_sapv.densityUnit, f"The density unit is {sol_sapv.densityUnit} instead of {densityUnit_target}."
    assert test_solution['chemicals'] == sol_sapv.chemicals, f"The chemicals are {sol_sapv.chemicals} instead of {test_solution['chemicals']}"
    assert substanceAmountPerVolume2 == sol_sapv.substanceAmountPerVolume, f"The substanceAmountPerVolume is {sol_sapv.substanceAmountPerVolume} instead of {substanceAmountPerVolume}."

    # Prepare the Cetoni device
    Ps, Vs, Cs = cetoni.prepareCetoni()

    # Generate test object substanceAmountPerVolume = substanceAmountPerVolume
    substanceAmountPerVolume3 = conf['test_solutionHandler']['parameterDict']
    substanceAmountPerVolume3['pumps'] = Ps
    substanceAmountPerVolume3['valves'] = Vs
    substanceAmountPerVolume3['endpoint'] = conf["CetoniDevice"]["waste"]

    sol_sapv = solutionHandler.Solution(name=test_solution['name'], chemicalMasses=test_solution['chemicalMasses'], chemicalMassesUncertainties=test_solution['chemicalMassesUncertainties'], mass=test_solution['mass'], massUncertainty=test_solution['massUncertainty'], massUnit=test_solution['massUnit'], reservoir=test_solution['reservoir'], pump=test_solution['pump'], densityUncertainty=test_solution['densityUncertainty'], density=test_solution['density'], densityUnit=test_solution['densityUnit'], substanceAmountPerVolume=substanceAmountPerVolume3)

    # Close the bus communication of the Cetoni device
    cetoni.quitCetoni()

    assert name_target == sol_sapv.name, f"The name is {sol_sapv.name} instead of {name_target}."
    assert chemicalMasses_target == sol_sapv.chemicalMasses, f"The chemical masses are {sol_sapv.chemicalMasses} instead of {chemicalMasses_target}."
    assert chemicalMassesUncertainties_target == sol_sapv.chemicalMassesUncertainties, f"The uncertainties of the chemical masses are {sol_sapv.chemicalMassesUncertainties} instead of {chemicalMassesUncertainties_target}."
    assert mass_target == sol_sapv.mass, f"The mass is {sol_sapv.mass} instead of {mass_target}."
    assert massUncertainty_target == sol_sapv.massUncertainty, f"The uncertainty of the mass is {sol_sapv.massUncertainty} instead of {massUncertainty_target}."
    assert massUnit_target == sol_sapv.massUnit, f"The unit of the mass is {sol_sapv.massUnit} instead of {massUnit_target}."
    assert reservoir_target == sol_sapv.reservoir, f"The reservoir is {sol_sapv.reservoir} instead of {reservoir_target}."
    assert pump_target == sol_sapv.pump, f"the pump is {sol_sapv.pump} instead of {pump_target}."
    assert density_target == sol_sapv.density, f"The density is {sol_sapv.density} instead of {density_target}."
    assert densityUncertainty_target == sol_sapv.densityUncertainty, f"The density uncertainty is {sol_sapv.densityUncertainty} instead of {densityUncertainty_target}."
    assert densityUnit_target == sol_sapv.densityUnit, f"The density unit is {sol_sapv.densityUnit} instead of {densityUnit_target}."
    assert test_solution['chemicals'] == sol_sapv.chemicals, f"The chemicals are {sol_sapv.chemicals} instead of {test_solution['chemicals']}"
    assert conf['test_solutionHandler']['substanceAmountPerVolume_target'] == sol_sapv.substanceAmountPerVolume, f"The substanceAmountPerVolume is {sol_sapv.substanceAmountPerVolume} instead of {substanceAmountPerVolume}."


def test_getSubstanceAmountPerVolume():
    # Get the chemicalsDict
    chemicalsDict = conf['solutionHandler']['chemicalsDict']

    # Get the definition of the test solution and instantiate the solution object
    test_solution2 = conf['test_solutionHandler']['solution_test']

    sol2 = solutionHandler.Solution(name=test_solution2['name'], chemicalMasses=test_solution2['chemicalMasses'], chemicalMassesUncertainties=test_solution2['chemicalMassesUncertainties'], mass=test_solution2['mass'], massUncertainty=test_solution2['massUncertainty'], massUnit=test_solution2['massUnit'], reservoir=test_solution2['reservoir'], pump=test_solution2['pump'], densityUncertainty=test_solution2['densityUncertainty'], density=test_solution2['density'], densityUnit=test_solution2['densityUnit'], substanceAmountPerVolume=None)

    assert sol2.substanceAmountPerVolume == {}, f"The substance amount per volume is {sol2.substanceAmountPerVolume} instead of an empty dictionary."

    # Get the substanceAmountPerVolume
    sol2.get_substanceAmountPerVolume(chemicalsDict=chemicalsDict)

    print(sol2.substanceAmountPerVolume)

    assert  sol2.substanceAmountPerVolume == conf['test_solutionHandler']['substanceAmountPerVolume_target'], f"The substance amount per volume is {sol2.substanceAmountPerVolume} instead of {conf['test_solutionHandler']['substanceAmountPerVolume_target']}."

#TODO: FIX THIS!!!
# def test_getSolutionDensity():
#     # delete all .lims files in the target directory to avoid the tests finding these files and checking those instead of the newly created one
#     for f in glob(f'{conf["densiViscoDriver"]["inputFolder"]}\\*.lims'):
#         remove(f)

#     # Get the definition of the test solution and instantiate the solution object
#     test_solution3 = conf['test_solutionHandler']['solution_test']

#     sol3 = solutionHandler.Solution(name=test_solution3['name'], chemicalMasses=test_solution3['chemicalMasses'], chemicalMassesUncertainties=test_solution3['chemicalMassesUncertainties'], mass=test_solution3['mass'], massUncertainty=test_solution3['massUncertainty'], massUnit=test_solution3['massUnit'], reservoir=test_solution3['reservoir'], pump=test_solution3['pump'], densityUncertainty=test_solution3['densityUncertainty'], density=test_solution3['density'], densityUnit=test_solution3['densityUnit'], substanceAmountPerVolume=None)

#     # Prepare the cetoni device to get the pumps and valves
#     Ps, Vs, Cs = cetoni.prepareCetoni()

#     density, density_std = sol3.get_SolutionDensity(pumps=Ps, valves=Vs)

#     # Close the cetoni BUS communication
#     cetoni.quitCetoni()

#     print(density, density_std)

#     assert density == conf['test_solutionHandler']['density_target'], f"The density is {density} instead of {conf['test_solutionHandler']['density_target']}."
#     assert density_std == conf['test_solutionHandler']['density_std_target'], f"The standard deviation of the density is {density_std} instead of {conf['test_solutionHandler']['density_std_target']}."

def test_generateSolutionsDict():
    # Get the target dictionarytest_solution3
    solutionsDict_target_dict = conf['test_solutionHandler']['solutionsDict_target']
    solutionsDict_target = {}
    for sol in solutionsDict_target_dict.keys():
        solutionInfo = solutionsDict_target_dict[sol]
        solutionsDict_target[sol] = solutionHandler.Solution(name=solutionInfo['name'], chemicalMasses=solutionInfo['chemicalMasses'], chemicalMassesUncertainties=solutionInfo['chemicalMassesUncertainties'], mass=solutionInfo['mass'], massUncertainty=solutionInfo['massUncertainty'], massUnit=solutionInfo['massUnit'], reservoir=solutionInfo['reservoir'], pump=solutionInfo['pump'], densityUncertainty=solutionInfo['densityUncertainty'], density=solutionInfo['density'], densityUnit=solutionInfo['densityUnit'], substanceAmountPerVolume=solutionsDict_target_dict[sol]['substanceAmountPerVolume'])
        #solutionsDict_target[sol].substanceAmountPerVolume = solutionsDict_target_dict[sol]['substanceAmountPerVolume']

    # Prepare the cetoni device to get the pumps and valves
    Ps, Vs, Cs = cetoni.prepareCetoni()

    # Get the resulting dictionary
    solutionsDict_result = solutionHandler.generate_solutionsDict(solutionsDef=conf['solutionHandler']['stockSolutions'], pumps=Ps, valves=Vs, savePath=conf['solutionHandler']['solutionsDict'])

    # Close the cetoni BUS communication
    cetoni.quitCetoni()

    for c in solutionsDict_result.keys():
        for a in solutionsDict_target_dict[c].keys():
            assert getattr(solutionsDict_target[c], a) == getattr(solutionsDict_result[c], a), f"The {a} is {getattr(solutionsDict_result[c], a)} instead of {getattr(solutionsDict_target[c], a)}."

def test_solutionFromDict():
    # Get the definition of the test solution and instantiate the solution object
    test_solution4 = conf['test_solutionHandler']['solution_test']

    sol4_target = solutionHandler.Solution(name=test_solution4['name'], chemicalMasses=test_solution4['chemicalMasses'], chemicalMassesUncertainties=test_solution4['chemicalMassesUncertainties'], mass=test_solution4['mass'], massUncertainty=test_solution4['massUncertainty'], massUnit=test_solution4['massUnit'], reservoir=test_solution4['reservoir'], pump=test_solution4['pump'], densityUncertainty=test_solution4['densityUncertainty'], density=test_solution4['density'], densityUnit=test_solution4['densityUnit'], substanceAmountPerVolume=test_solution4['substanceAmountPerVolume'])
    #sol4_target.substanceAmountPerVolume = test_solution4['substanceAmountPerVolume']

    # Get the resulting object
    sol4_result = solutionHandler.solution_from_dict(dict=conf['test_solutionHandler']['solution_test'])

    for a in test_solution4.keys():
        assert getattr(sol4_target, a) == getattr(sol4_result, a), f"The {a} is {getattr(sol4_result, a)} instead of {getattr(sol4_target, a)}."

def test_loadSolutionsDict():
    # Get the target dictionarytest_solution3
    solutionsDict_target_dict2 = conf['test_solutionHandler']['solutionsDict_target']
    solutionsDict_target2 = {}
    for sol in solutionsDict_target_dict2.keys():
        solutionInfo = solutionsDict_target_dict2[sol]
        solutionsDict_target2[sol] = solutionHandler.Solution(name=solutionInfo['name'], chemicalMasses=solutionInfo['chemicalMasses'], chemicalMassesUncertainties=solutionInfo['chemicalMassesUncertainties'], mass=solutionInfo['mass'], massUncertainty=solutionInfo['massUncertainty'], massUnit=solutionInfo['massUnit'], reservoir=solutionInfo['reservoir'], pump=solutionInfo['pump'], densityUncertainty=solutionInfo['densityUncertainty'], density=solutionInfo['density'], densityUnit=solutionInfo['densityUnit'], substanceAmountPerVolume=solutionsDict_target_dict2[sol]['substanceAmountPerVolume'])
        # solutionsDict_target2[sol].substanceAmountPerVolume = solutionsDict_target_dict2[sol]['substanceAmountPerVolume']

    # Load the solution
    solutionsDict_result2 = solutionHandler.loadSolutionsDict(solutionsDict_path=conf['solutionHandler']['solutionsDict'])

    for c in solutionsDict_result2.keys():
        for a in solutionsDict_target_dict2[c].keys():
            assert getattr(solutionsDict_target2[c], a) == getattr(solutionsDict_result2[c], a), f"The {a} is {getattr(solutionsDict_result2[c], a)} instead of {getattr(solutionsDict_target2[c], a)}."

def test_getSolutionsDict():
    # Get the dictionary of the target
    solutionsDict_target_dict3 = conf['test_solutionHandler']['solutionsDict_target']

    # Prepare the cetoni device to get the pumps and valves
    Ps, Vs, Cs = cetoni.prepareCetoni()

    # Get the target object directly from generation
    solutionsDict_generated_target3 = solutionHandler.generate_solutionsDict(solutionsDef=conf['solutionHandler']['stockSolutions'], pumps=Ps, valves=Vs, savePath=conf['solutionHandler']['solutionsDict'])

    # Close the cetoni BUS communication
    cetoni.quitCetoni()

    # Get the resulting object when passing a dict
    solutionsDict_dict_result = solutionHandler.get_solutionsDict(solutionsDict=solutionsDict_generated_target3)

    # Get the resulting object when passing a str
    solutionsDict_str_result = solutionHandler.get_solutionsDict(solutionsDict=conf['solutionHandler']['solutionsDict'])

    for c in solutionsDict_dict_result.keys():
        for a in solutionsDict_target_dict3[c].keys():
            assert getattr(solutionsDict_generated_target3[c], a) == getattr(solutionsDict_dict_result[c], a), f"The {a} is {getattr(solutionsDict_dict_result[c], a)} instead of {getattr(solutionsDict_generated_target3[c], a)}."

    for c in solutionsDict_str_result.keys():
        for a in solutionsDict_target_dict3[c].keys():
            assert getattr(solutionsDict_generated_target3[c], a) == getattr(solutionsDict_str_result[c], a), f"The {a} is {getattr(solutionsDict_str_result[c], a)} instead of {getattr(solutionsDict_generated_target3[c], a)}."

def test_getVolFracs():
    # Get the chemicalsDict
    chemicalsDict = solutionHandler.get_chemicalsDict(conf['solutionHandler']['chemicalsDict'])
    # Get the solutionsDict
    solutionsDict = solutionHandler.get_solutionsDict(conf['solutionHandler']['solutionsDict'])


    ## mixing ratio as molar fraction
    # Get the mixing ratios
    mixingRatios = conf['test_solutionHandler']['mixingRatios']['molarFractions']

    for ratio in mixingRatios.keys():
        print('\n', ratio, '\n')
        # Get the target values for the outputs of get_volFracs
        requestedRatio_target = mixingRatios[ratio]
        volumeFractions_target = conf['test_solutionHandler']['volFrac_targets'][ratio]['volumeFractions']
        setRatio_target = conf['test_solutionHandler']['volFrac_targets'][ratio]['setRatio']
        minSquaredError_target = conf['test_solutionHandler']['volFrac_targets'][ratio]['minSquaredError']
        # Get the current mixing ratio
        mRat = mixingRatios[ratio]

        # Get the actual outputs
        requestedRatio_result, volumeFractions_result, setRatio_result, minSquaredError_result = solutionHandler.get_volFracs(mixingRatio=mRat, chemicalsDict=chemicalsDict, solutionsDict=solutionsDict, fraction='molPerMol')

        assert requestedRatio_target == requestedRatio_result, f"The requested ratio of {ratio} is {requestedRatio_result} instead of {requestedRatio_target}."
        for i in requestedRatio_result.keys():
            assert np.isclose(requestedRatio_target[i],requestedRatio_result[i], rtol=1e-6), f"The {i} of {ratio} is {requestedRatio_result[i]} instead of {requestedRatio_target[i]}."
        for j in volumeFractions_target.keys():
            assert np.isclose(volumeFractions_target[j],volumeFractions_result[j], rtol=1e-6), f"The {j} of {ratio} is {volumeFractions_result[j]} instead of {volumeFractions_target[j]}."
        for k in setRatio_target.keys():
            assert np.isclose(setRatio_target[k],setRatio_result[k], rtol=1e-6), f"The {k} of {ratio} is {setRatio_result[k]} instead of {setRatio_target[k]}."
        assert minSquaredError_target > minSquaredError_result, f"The minimum squared error of {ratio} is {minSquaredError_result} instead of {minSquaredError_target}."