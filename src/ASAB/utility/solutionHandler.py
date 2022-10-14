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

import numpy as np
import pandas as pd
from typing import Tuple, Union
from scipy.optimize import minimize
from pathlib import Path
from inspect import getfullargspec


from ASAB.action import CetoniDevice_action
from ASAB.driver import CetoniDevice_driver
from ASAB.utility.graph import findPath

from ASAB.utility.helpers import saveToFile, typeCheck, loadVariable
from ASAB.action import densiVisco_action

### Chemicals #############################################################################################################################################################

class Chemical:
    ''' This class describes a chemical with all its properties relevant to the ASAB system. '''
    def __init__(self, name:str, molarMass:float, molarMassUncertainty:float, molarMassUnit:str, density:float, densityUncertainty:float, densityUnit:str) -> None:
        ''' This funciton initializes a Chemical object.
        
        Inputs:
        name: a string giving the name of the chemical, by which it shall be referenced in the experiment
        molarMass: a float representing the molar mass of the chemical in the unit g/mol
        molarMassUncertainty: a float giving the uncertainty or the error of the given molar mass. Currently, this is included for the sake of completeness as it may be
                              useful in the future to do error calculations
        molarMassUnit: a string documenting the unit of the molar mass. This is currently not used by the code, but serves rather for documentation purposes.
        denstiy: a float representing the density of the chemical in g/cm^3
        densityUncertainty: a float giving the uncertainty or the error of the given density. Currently, this is included for the sake of completeness as it may be
                            useful in the future to do error calculations
        densityUnit: a string documenting the unit of the density. This is currently not used by the code, but serves rather for documentation purposes.
        
        Outputs:
        This function has not outputs. '''

        # Check the input types
        typeCheck(func=Chemical.__init__, locals=locals())

        self.name = name
        self.molarMass = molarMass
        self.molarMassUncertainty = molarMassUncertainty
        self.molarMassUnit = molarMassUnit
        self.density = density
        self.densityUncertainty = densityUncertainty
        self.densityUnit = densityUnit

def generate_chemicalsDict(chemicalsDef:str, savePath:str=conf['solutionHandler']['chemicalsDict']) -> dict:
    ''' This function generates a dictionary of chemicals from a .csv file in the path specified by chemicalsDef, saves it to a .py file and returns a dictionary
    of chemicals.
    
    Inputs:
    chemicalsDef: a string specifying the path to a .csv file defining the properties of the chemicals
    savePath: a string specifying the path, where the dictionary shall be saved.
    
    Outputs:
    chemicalsDict: a dictionary of Chemical objects based on the chemicalsDef '''

    # Check the input types
    typeCheck(func=generate_chemicalsDict, locals=locals())

    # Load the information about the chemicals as a dataframe
    chemicals = pd.read_csv(chemicalsDef, sep=';')

    # Initialize the chemicalsDict and the save version
    chemicalsDict = {}
    chemicalsDict_save = {}

    ## Go through all the chemicals, generate Chemicals objects and save them to a dictionary
    for chemical in chemicals['chemicalName']:
        chem = chemicals.loc[chemicals['chemicalName']==chemical]

        # Get all the properties of the chemical and create a Chemical object
        molarMass = chem['molarMass'].values[0]
        molarMassUncertainty = chem['molarMass_uncertainty'].values[0]
        molarMassUnit = conf['solutionHandler']['units']['molarMass']
        density = chem['density'].values[0]
        densityUncertainty = chem['density_uncertainty'].values[0]
        densityUnit = conf['solutionHandler']['units']['density']
        C = Chemical(name=chemical, molarMass=molarMass, molarMassUncertainty=molarMassUncertainty, molarMassUnit=molarMassUnit, density=density, densityUncertainty=densityUncertainty, densityUnit=densityUnit)

        # Add the chemical to the chemicalsDict
        chemicalsDict[chemical] = C

        # assemble the save version of the chemicalsDict
        chemicalsDict_save[chemical] = C.__dict__

    # Save the dictionary to a .py file
    folder = '\\'.join(savePath.split('\\')[:-1])
    filename = savePath.split('\\')[-1].split('.')[0]
    extension = savePath.split('\\')[-1].split('.')[1]
    saveToFile(folder=folder, filename=filename, extension=extension, data=f'chemicalsDict = {str(chemicalsDict_save)}')

    return chemicalsDict

def chemical_from_dict(dict:dict) -> Chemical:
    ''' This function initializes a chemical based on a dictionary containing the attributes as keys and their respective values as value
    
    Inputs:
    dict: a dictionary containing the attributes of a chemical as keys and their respective values as values
    
    Outputs:
    chemicalFromDict: a chemical object with the attributes as defined in dict '''

    # Check the input types
    typeCheck(func=chemical_from_dict, locals=locals())


    # instantiate a chemical based on the information in dict
    chemicalFromDict = Chemical(name=dict['name'], molarMass=dict['molarMass'], molarMassUncertainty=dict['molarMassUncertainty'], molarMassUnit=dict['molarMassUnit'], density=dict['density'], densityUncertainty=dict['densityUncertainty'], densityUnit=dict['densityUnit'])
    return chemicalFromDict

def loadChemicalsDict(chemicalsDict_path:str) -> dict:
    ''' This function initializes an empty chemicalsDict and loads chemicals from a file
    
    Inputs:
    chemicalsDict_path: a string specifying, where the file containing the dictionary of chemicals is stored

    Outputs:
    chemicalsDict: a dictionary containing chemical objects as values '''

    # Check the input types
    typeCheck(func=loadChemicalsDict, locals=locals())

    # instantiate an empty dictionary
    chemicalsDict = {}
    # load the file from the given path
    dataDict = loadVariable(loadPath=chemicalsDict_path, variable='chemicalsDict')
    # Make the values in the dict to chemicals
    for key, value in dataDict.items():
        chemicalsDict[key] = chemical_from_dict(value)
    return chemicalsDict

def get_chemicalsDict(chemicalsDict:Union[dict, str, None]) -> dict:
    ''' This function checks the type of the chemicalsDict and returns a dictionary of chemicals objects, if the input is not alread a dictionary.
    
    Inputs:
    chemicalsDict: a dictionary of chemicals objects or a string specifying the path to a .py file containing a chemicalsDict
    
    Outputs:
    chemicalsDict: a dictionary containing chemical objects as values '''

    # Check the input types
    typeCheck(func=get_chemicalsDict, locals=locals())

    # Check the type of the chemicalsDict, which is used as the input
    if chemicalsDict == None:
        chemicalsDict_dict = generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'])
    if (type(chemicalsDict) == dict):
        chemicalsDict_dict = chemicalsDict
    elif (type(chemicalsDict) == str):
        if Path(chemicalsDict).is_file:
            chemicalsDict_dict = loadChemicalsDict(chemicalsDict_path=chemicalsDict)
        else:
            raise ValueError(f"The string given as chemicalsDict {chemicalsDict} does not correspond to a path.")
    else:
        raise TypeError(f"The chemicalsDict used as an input is of type {type(chemicalsDict)} instead of str or dict.")
    
    return chemicalsDict_dict


### Solutions #############################################################################################################################################################

class Solution:
    ''' This class describes a solution with the properties relevant to ASAB. '''
    def __init__(self, name:str, chemicalMasses:dict, chemicalMassesUncertainties:dict, mass:float, massUncertainty:float, massUnit:str, reservoir:Union[str, None], pump:str, densityUncertainty:Union[float, None], densityUnit:str, substanceAmountPerVolume:Union[dict, None], density:Union[float, None]=None) -> None:
        ''' This funciton initializes a Chemical object.
        
        Inputs:
        name: a string giving the name of the solution, by which it shall be referenced in the experiment
        chemicalMasses: a dictionary comprising the masses of each chemical in the mixture
        chemicalMassesUncertainty: a dictionary comprising the uncertainties of the mass of each chemical in the mixture
        mass: a float representing the total mass of the mixture resulting from the addition of the masses of chemicals as specified in chemicalMasses
        massUncertainty: a float reporting the uncertainty of the total mass of the solution
        massUnit: a string reporting the unit of the mass. This is currently not used by the code, but serves rather for documentation purposes.
        reservoir: a string giving the name of the node belonging to the reservoir, in which the solution is supplied
        pump: a string giving the name of the pump, which belongs to the respective solution
        denstiy: a float representing the density of the chemical in g/cm^3
        densityUncertainty: a float giving the uncertainty or the error of the given density. Currently, this is included for the sake of completeness as it may be
                            useful in the future to do error calculations
        densityUnit: a string documenting the unit of the density. This is currently not used by the code, but serves rather for documentation purposes.
        substanceAmountPerVolume: a dictionary giving the substance amount per volume as values with the chemicals' names as keys or a dictionary of the parameters
                                  for a call for get_substanceAmountPerVolume() as keys and their values as values
        
        Outputs:
        This function has not outputs. '''

        # Check the input types
        typeCheck(func=Solution.__init__, locals=locals())

        self.name = name
        self.chemicalMasses = chemicalMasses
        self.chemicalMassesUncertainties = chemicalMassesUncertainties
        self.chemicals = list(chemicalMasses.keys())
        self.mass = mass
        self.massUncertainty = massUncertainty
        self.massUnit = massUnit
        self.density = density
        self.densityUncertainty = densityUncertainty
        self.densityUnit = densityUnit
        self.reservoir = reservoir
        self.pump = pump
        self.substanceAmountPerVolume = {}
        # If substanceAmountPerVolume is None, it is initialized as an empty dictionary
        if substanceAmountPerVolume == None:
            pass
        # If the keys of the substanceAmountPerVolume dictionary match the chemicals, it is likely to be a substanceAmountPerVolume dictionary
        elif list(substanceAmountPerVolume.keys()) == self.chemicals:
            self.substanceAmountPerVolume = substanceAmountPerVolume
        # If the keys of substanceAmountPerVolume match the arguments of the get_substanceAmountPerVolume function, it shall be used to call this function
        elif ['self'] + list(substanceAmountPerVolume.keys()) == getfullargspec(self.get_substanceAmountPerVolume).args:
            # In this case, call the function to fill the substanceAmountPerVolume attribute
            self.get_substanceAmountPerVolume(chemicalsDict=substanceAmountPerVolume['chemicalsDict'], pumps=substanceAmountPerVolume['pumps'], valves=substanceAmountPerVolume['valves'], endpoint=substanceAmountPerVolume['endpoint'])
        else:
            # If none of the above cases matches, it must be a wrong dictionary
            raise ValueError(f"The substanceAmountPerVolume dictionary {substanceAmountPerVolume} can neither be used as is nor is is suitable to call get_substanceAmountPerVolume.")

    def get_substanceAmountPerVolume(self, chemicalsDict:Union[dict, str], pumps:dict={}, valves:dict={}, endpoint:str=conf["CetoniDevice"]["waste"]) -> None:
        ''' This function determines the substance amount per Volume for a stock solution. To do so, it needs the information about the chemicals and the density of the
        solution. If the density is not available, it will be measured. The results will be saved to the self.substanceAmountPerVolume attribute, which can then be used
        as the definintion of the solution's composition.
        
        Inputs:
        chemicalsDict: a dictionary of Chemical objects
        
        Outputs:
        This function has no outputs. '''

        # Check the input types
        typeCheck(func=Solution.get_substanceAmountPerVolume, locals=locals())

        # Get the chemicalsDict as a dict
        chemicalsDict = get_chemicalsDict(chemicalsDict=chemicalsDict)

        # Check, whether the density of the solution is already contained in the solution object
        if self.density == None:
            # If there is no density given in the object, measure it
            self.density, self.densityUncertainty = self.get_SolutionDensity(pumps=pumps, valves=valves, endpoint=endpoint)
        
        # Determine the substance amount per volume of solution (molarity) for each of the chemicals
        for chemical in self.chemicalMasses.keys():
            self.substanceAmountPerVolume[chemical] = (self.chemicalMasses[chemical] / chemicalsDict[chemical].molarMass)/(self.mass / self.density)
        print(self.name, self.substanceAmountPerVolume)
        
    def get_SolutionDensity(self, pumps:dict, valves:dict, endpoint:str=conf["CetoniDevice"]["waste"]) -> Tuple[float, float]:
        ''' This function measures the density of a stock solution, which is provided in one of the reservoirs.
        
        Inputs:
        pumps: a dictionary containing all the pumps in the system with the names of the pumps as keys and the pump objects as values
        valves: a dictionary containing all the valves in the system with the names of the valves as keys and the valve objects as values
        endpoint: a string giving the name of the node, where the sample should leave the system

        Outputs:
        density: a float representing the density of the solution
        densityStandardDev: a float reporting the standard deviation of the density measurement '''

        # Check the input types
        typeCheck(func=Solution.get_SolutionDensity, locals=locals())

        ## aspirate the solution to the syringe of hte respective pump
        # find a path from the reservoir to the pump
        pathRP = findPath(start_node=self.reservoir, end_node=self.pump)
        # switch the valves according to pathRP
        CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=valves)
        # fill the syringe
        print('filling....')
        _ = CetoniDevice_action.fillSyringe(pump=pumps[self.pump], volume=pumps[self.pump].get_volume_max(), valvesDict=valves, reservoir=self.reservoir)
        print('filled')

        ## switch the valves to the waste through the device
        # find a path from the pump to the waste via the device
        pathPE = findPath(start_node=self.pump, end_node=endpoint)
        # switch the valves according to pathPE
        CetoniDevice_action.switchValves(nodelist=pathPE, valvesDict=valves)

        # generate a flow
        print('flow...')
        pumps[self.pump].generate_flow(conf['CetoniDeviceDriver']['flow'])
        print('flowing')

        # provide sample for density measurement
        print('providing....')
        CetoniDevice_action.provideSample(measurementtype='densiVisco', sample_node=self.pump, pumps=pumps, valves=valves, endpoint=endpoint)
        print('provided')

        # define the sample name
        sampleName=f"Pre-measureStockSolution_{self.name}"

        # perform the density measurement
        print('measure...')
        densiVisco_action.measure(sampleName=sampleName, method='Density')
        print('measured')

        # retrieve the resulting data
        print('retrieving....')
        densityData = densiVisco_action.retrieveData(sampleName=sampleName, method='Density', methodtype='measurement', savePath=conf['experimentFolder'])
        print('retrieved')

        # drain the sample
        print('draining...')
        CetoniDevice_action.drainSample(measurementtype='densiVisco', pump=self.pump, repeats=3, pumps=pumps, valves=valves)
        print('drained')

        # extract the density and determine the standard deviation
        density = np.mean(densityData['density']['values'])
        densityStandardDeviation = np.std(densityData['density']['values'])

        return density, densityStandardDeviation

def generate_solutionsDict(solutionsDef:str, pumps:dict, valves:dict, chemicalsDict:Union[dict, str]=conf['solutionHandler']['chemicalsDict'], savePath:str=conf['solutionHandler']['solutionsDict']) -> dict:
    ''' This function generates a dictionary of solutions from a .csv file in the path specified by solutionsDef, saves it to a .py file and returns a dictionary
    of soltuions.
    
    Inputs:
    solutionsDef: a string specifying the path to a .csv file defining the properties of the solutions
    savePath: a string specifying the path, where the dictionary shall be saved.
    
    Outputs:
    solutionsDict: a dictionary of Solution objects based on the solutionsDef '''

    # Check the input types
    typeCheck(func=generate_solutionsDict, locals=locals())

    # Load the information about the solutions as a dataframe
    solutions = pd.read_csv(solutionsDef, sep=';')

    # Initialize the solutionsDict and the save version
    solutionsDict = {}
    solutionsDict_save = {}

    ## Go through all the solutions, generate Solutions objects and save them to a dictionary
    for solution in solutions['solutionName']:
        sol = solutions.loc[solutions['solutionName']==solution]

        # Get the chemicals from the column names
        chems = [col for col in sol.columns if col not in conf['solutionHandler']['nonChemicalCols']]

        # Initialize chemicalMasses and chemicalMassesUncertainties
        chemicalMasses = {}
        chemicalMassesUncertainties = {}

        # Get all the properties of the solution and generate the Solution object
        for c in chems:
            if 'uncertainty' not in c:
                chemicalMasses[c] = sol[c].values[0]
            else:
                c_split = c.split('_')[0]
                chemicalMassesUncertainties[c_split] = sol[c].values[0]
        mass = sol['massTotal'].values[0]
        massUncertainty = sol['massTotal_uncertainty'].values[0]
        massUnit = conf['solutionHandler']['units']['mass']
        reservoir = sol['reservoir'].values[0]
        pump = sol['pump'].values[0]
        densityUnit = conf['solutionHandler']['units']['density']

        S = Solution(name=solution, chemicalMasses=chemicalMasses, chemicalMassesUncertainties=chemicalMassesUncertainties, mass=mass, massUncertainty=massUncertainty, massUnit=massUnit, reservoir=reservoir, pump=pump, density=None, densityUncertainty=None, densityUnit=densityUnit, substanceAmountPerVolume=None)

        # Get the density from the file or the measurement
        if not np.isnan(sol['density'].values[0]) and not np.isnan(sol['density_uncertainty'].values[0]):
            density = sol['density'].values[0]
            densityUncertainty = sol['density_uncertainty'].values[0]
        elif np.isnan(sol['density'].values[0]) and np.isnan(sol['density_uncertainty'].values[0]):
            density, densityUncertainty = S.get_SolutionDensity(pumps=pumps, valves=valves)

        S.density = density
        S.densityUncertainty = densityUncertainty

        # get the substance amount per volume
        S.get_substanceAmountPerVolume(chemicalsDict=chemicalsDict)

        # Add the solution to the solutionsDict
        solutionsDict[solution] = S

        # assemble the save version of the solutionsDict
        solutionsDict_save[solution] = S.__dict__

    # Save the dictionary to a .py file
    folder = '\\'.join(savePath.split('\\')[:-1])
    filename = savePath.split('\\')[-1].split('.')[0]
    extension = savePath.split('\\')[-1].split('.')[1]
    print(savePath)
    saveToFile(folder=folder, filename=filename, extension=extension, data=f'solutionsDict = {str(solutionsDict_save)}')

    return solutionsDict

def solution_from_dict(dict:dict) -> Solution:
    ''' This function initializes a solution based on a dictionary containing the attributes as keys and their respective values as value
    
    Inputs:
    dict: a dictionary containing the attributes of a solution as keys and their respective values as values
    
    Outputs:
    solutionFromDict: a solution object with the attributes as defined in dict '''

    # Check the input types
    typeCheck(func=solution_from_dict, locals=locals())


    # instantiate a chemical based on the information in dict
    solutionFromDict = Solution(name=dict['name'], chemicalMasses=dict['chemicalMasses'], chemicalMassesUncertainties=dict['chemicalMassesUncertainties'], mass=dict['mass'], massUncertainty=dict['massUncertainty'], massUnit=dict['massUnit'], reservoir=dict['reservoir'], pump=dict['pump'], density=dict['density'], densityUncertainty=dict['densityUncertainty'], densityUnit=dict['densityUnit'], substanceAmountPerVolume=dict['substanceAmountPerVolume'])
    #solutionFromDict.substanceAmountPerVolume = dict['substanceAmountPerVolume']
    return solutionFromDict

def loadSolutionsDict(solutionsDict_path:str) -> dict:
    ''' This function initializes an empty solutionsDict and loads solutions from a file
    
    Inputs:
    solutionsDict_path: a string specifying, where the file containing the dictionary of solutions is stored

    Outputs:
    solutionsDict: a dictionary containing solution objects as values '''

    # Check the input types
    typeCheck(func=loadSolutionsDict, locals=locals())

    # instantiate an empty dictionary
    solutionsDict = {}
    # load the file from the given path
    dataDict = loadVariable(loadPath=solutionsDict_path, variable='solutionsDict')
    # Make the values in the dict to chemicals
    for key, value in dataDict.items():
        solutionsDict[key] = solution_from_dict(value)
    return solutionsDict

def get_solutionsDict(solutionsDict:Union[dict, str]) -> dict:
    ''' This function checks the type of the solutionsDict and returns a dictionary of solution objects, if the input is not alread a dictionary.
    
    Inputs:
    solutionsDict: a dictionary of solution objects or a string specifying the path to a .py file containing a solutionsDict
    
    Outputs:
    solutionsDict: a dictionary containing solution objects as values '''

    # Check the input types
    typeCheck(func=get_solutionsDict, locals=locals())

    # Check the type of the solutionsDict, which is used as the input
    if (type(solutionsDict) == dict):
        solutionsDict_dict = solutionsDict
    elif (type(solutionsDict) == str):
        if Path(solutionsDict).is_file:
            solutionsDict_dict = loadSolutionsDict(solutionsDict_path=solutionsDict)
        else:
            raise ValueError(f"The string given as solutionsDict {solutionsDict} does not correspond to a path.")
    else:
        raise TypeError(f"The solutionsDict used as an input is of type {type(solutionsDict)} instead of str or dict.")
    
    return solutionsDict_dict


### get_volFracs #############################################################################################################################################################

def get_volFracs(mixingRatio:dict, chemicalsDict:Union[dict, str, None], solutionsDict:Union[dict, str], fraction:str) -> Tuple[dict, dict, dict, float]:
    ''' This function determines the volume fractions of the stock solutions required to get as close as possible to the requested mixing ratio.
    
    Inputs:
    mixingRatio: a dictionary with the names of the relevant chemicals as keys and their molar fraction, mass fraction, volumetric fraction or molarity as values
    chemicalsDict: a dictionary containing chemical objects as values, or a string specifying the path to a chemicalsDict or None
    solutionsDict: a dictionary containing solution objects as values, or a string specifying the path to a solutionsDict
    fraction: a string specifying, whether the fraction is a molar fraction, mass fraction, volumetric fraction or molarity
    
    Outputs:
    requestedRatio: the mixingRatio as it was input
    volumeFractions: the volume fractions for each stock solution as determined by the minimization of the squared error. The keys are the names of the chemicals and the
                     values are the volumeFractions
    setRatio: a dictionary containing the calculated mixing ratio closest to the desired one. The keys are the names of the chemicals and the values are the mixing ratio
              resulting from the calculated volume fractions in the type of fraction specified by fraction
    minSquaredError: a float representing the minimum squared error of the calculated setRatio compared to the requestedRatio '''

    # Check the input types
    typeCheck(func=get_volFracs, locals=locals())

    if chemicalsDict == None:
        chemicalsDict = generate_chemicalsDict(chemicalsDef=conf['solutionHandler']['chemicals'])
    else:
        # Get the chemicalsDict as dictionary
        chemicalsDict = get_chemicalsDict(chemicalsDict=chemicalsDict)
    # Get the chemicalsDict as dictionary
    solutionsDict = get_solutionsDict(solutionsDict=solutionsDict)

    ## Assemble the linear system of equations
    ## Get the matrix of stock solutions containing the concentrations of the chemicals in one of the stock solutions as a column
    concentrationMatrix = pd.DataFrame()
    for stockSolution in solutionsDict.keys():
        concentrationMatrix_sol = pd.DataFrame.from_dict(data=solutionsDict[stockSolution].substanceAmountPerVolume, orient='index', columns=[solutionsDict[stockSolution].name])
        concentrationMatrix = pd.concat([concentrationMatrix, concentrationMatrix_sol], axis=1, ignore_index=False)

    ## Assemble vector representing the target composition
    # get the amount of substance for each chemical from the mixing ratio depending on the input
    if fraction == 'molPerMol':
        # In this case, the mixing ratio is given in mol/mol for each chemical
        # We assume to mix 1 mol of total mixture and use the mixing ratio as it is, because only the ratios matter
        targetVector_n = pd.DataFrame.from_dict(data=mixingRatio, orient='index', columns=['target'])
        
        ## Define start values for the optimization
        # calculate V = n/c for each element n in the targetVector_n with the concentrations c for each solution and
        # sum them up
        volumes_start = {}
        for s in concentrationMatrix.columns:
            volumes_start[s] = 0.0
            for n in targetVector_n.index:
                if concentrationMatrix.at[n, s] > 0.0:
                    volumes_start[s] += (targetVector_n.at[n, 'target'])/(concentrationMatrix.at[n, s])
                else:
                    volumes_start[s] += 0
        # Make the start value a dataframe
        volumes_start = pd.DataFrame.from_dict(data=volumes_start, orient='index')

    # Add the target to the matrix to ensure matching indices
    concentrationMatrix_target = pd.concat([concentrationMatrix, targetVector_n], axis=1, ignore_index=False)
    # Filling NaN values arising due to chemicals not included in the requested mixtures with 0.0
    concentrationMatrix_target.fillna(value=0.0, inplace=True)

    # Get the indices related to the concentrations but not the target column
    concentrationColumns = list(concentrationMatrix_target.columns)
    concentrationColumns.remove('target')
    # Get the concentration matrix from the concentrationMatrix_target
    concentrations = concentrationMatrix_target[concentrationColumns]
    # Get the target column from the concentrationMatrix_target
    target_n = concentrationMatrix_target['target']

    ## Solve the system of linear equations; if an exact solution is not possible, which will be mostly the case, get a minimum 2-norm approximation   # -> https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
    # Numeric method suggested by Prof. Dr.-Ing. Helge Stein
    def lgs(volumes, concentrations=concentrations, mix=target_n):
        result_n = concentrations.dot(volumes)
        # print('result_n \n', result_n)
        result_n_normalized = result_n / np.sum(result_n)
        # print('result_n_normalized \n', result_n_normalized, np.sum(result_n))
        squaredError = np.sum((result_n_normalized - mix)**2.)
        # print('squaredError \n', squaredError)
        return squaredError

    # Add boundaries to restrict the results to positive values as only addition of volumes is possible
    bounds = [(0,None) for i in volumes_start.index]
    # Get the optimized volumes for the stock solutions; The tolerance is very relevant for the accuracy of the output
    vols = minimize(lgs, x0=volumes_start, bounds=bounds, tol=1e-15)

    # Get the volume fractions by division by the total volume
    volFracs = vols.x / (np.sum(vols.x))

    # Collect the volume fractions in a dictionary with the names of the stock solutions as keys, which are obtained from
    # concentrations
    volFracs = pd.Series(data=volFracs, index=concentrations.columns)

    ## Calculate the ratio resulting from the volume fractions in the same type of fraction as the input
    if fraction == 'molPerMol':
        n_result = concentrations.dot(volFracs)
        setRatio = n_result / np.sum(n_result)

    # Gather all the return values and return them
    requestedRatio = mixingRatio
    # Get only the volFracs, which are non-zero to avoid unnecessary filling of syringes
    volumeFractions = dict(volFracs.drop(volFracs[np.isclose(volFracs, 0.0, rtol=1e-15)].index))
    setRatio = dict(setRatio.drop(setRatio[np.isclose(setRatio, 0.0, rtol=1e-15)].index))
    minSquaredError = vols.fun

    return requestedRatio, volumeFractions, setRatio, minSquaredError
