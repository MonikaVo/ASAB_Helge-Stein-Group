from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

import numpy as np
import pandas as pd
from typing import Tuple, Union
from scipy.optimize import minimize
from inspect import getfullargspec
import logging
import matplotlib.pyplot as plt
from itertools import combinations

# create a logger for this module
logger_solutionHandler = logging.getLogger(f"run_logger.{__name__}")

from ASAB.action import CetoniDevice_action
from ASAB.driver import CetoniDevice_driver
from ASAB.utility.graph import findPath

from ASAB.utility.helpers import saveToFile, typeCheck, loadVariable
from ASAB.action import densiVisco_action

### Chemicals #############################################################################################################################################################

class Chemical:
    ''' This class describes a chemical with all its properties relevant to the ASAB system. '''
    def __init__(
        self,
        name:str,
        molar_mass:float,
        molar_mass_uncertainty:float,
        molar_mass_unit:str,
        density:float,
        density_uncertainty:float,
        density_unit:str,
        density_temperature:float,
        InChIKey: str,
        SMILES:str,
        batch:str,
        manufacturer:str,
        manufacturing_date:str,
        references:str
        ) -> None:
        ''' This funciton initializes a Chemical object.
        
        Inputs:
        name: a string giving the name of the chemical, by which it shall be referenced in the experiment
        molar_mass: a float representing the molar mass of the chemical in the unit g/mol
        molar_mass_uncertainty: a float giving the uncertainty or the error of the given molar mass. Currently, this is included for the sake of completeness as it may be
                              useful in the future to do error calculations
        molar_mass_unit: a string documenting the unit of the molar mass. This is currently not used by the code, but serves rather for documentation purposes.
        denstiy: a float representing the density of the chemical in g/cm^3
        density_uncertainty: a float giving the uncertainty or the error of the given density. Currently, this is included for the sake of completeness as it may be
                            useful in the future to do error calculations
        density_unit: a string documenting the unit of the density. This is currently not used by the code, but serves rather for documentation purposes.
        denisty_temperature: a float representing the temperature in Kelvin, at which the density is given
        InChIKey: the InChIKey related to the chemical
        SMILES: the canonical SMILES string of the chemical
        batch: the batch number of the chemical
        manufacturer: the manufacturer of the chemical
        manufacturing_date: the date, at which the chemical was manufactured in the format dd.mm.yy
        references: a string representing the references, if literature values are used for e.g. the denisty and/or molar mass

        Outputs:
        This function has not outputs. '''

        # Check the input types
        typeCheck(func=Chemical.__init__, locals=locals())

        self.name = name
        self.molar_mass = molar_mass
        self.molar_mass_uncertainty = molar_mass_uncertainty
        self.molar_mass_unit = molar_mass_unit
        self.density = density
        self.density_uncertainty = density_uncertainty
        self.density_unit = density_unit
        self.density_temperature = density_temperature
        self.InChIKey = InChIKey
        self.SMILES = SMILES
        self.batch = batch
        self.manufacturer = manufacturer
        self.manufacturing_date = manufacturing_date
        self.references = references

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
    chemicals = pd.read_csv(chemicalsDef, sep=';', index_col="InChIKey")

    # Initialize the chemicalsDict and the save version
    chemicalsDict = {}
    chemicalsDict_save = {}

    ## Go through all the chemicals, generate Chemicals objects and save them to a dictionary
    for chemical in chemicals.index:
        chem = chemicals.loc[[chemical]]
        chem = chem.T.to_dict()[chemical]   # https://stackoverflow.com/questions/26716616/convert-a-pandas-dataframe-to-a-dictionary
        chem["molar_mass_unit"] = conf['solutionHandler']['units']['molar_mass']
        chem["density_unit"] = conf['solutionHandler']['units']['density']
        chem["InChIKey"] = chemical
        C = Chemical(**chem)

        # Add the chemical to the chemicalsDict
        chemicalsDict[chemical] = C

        # assemble the save version of the chemicalsDict
        chemicalsDict_save[chemical] = C.__dict__

    # Save the dictionary to a .py file
    folder = str(Path(savePath).resolve().parent)
    filename = Path(savePath).resolve().stem
    extension = Path(savePath).resolve().suffix.lstrip(".")
    saveToFile(folder=folder, filename=filename, extension=extension, data=f'chemicalsDict = {str(chemicalsDict_save)}')
    logger_solutionHandler.info(f"ChemicalsDict:\n{chemicalsDict_save}")
    return chemicalsDict

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
        chemicalsDict[key] = Chemical(**value)
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
    def __init__(
        self,
        ID:str,
        name:str,
        reservoir:str,
        pump:str,
        mass_total:float,
        mass_total_uncertainty:float,
        mass_unit:str,
        density_unit:str,
        density_temperature:float,
        chemical_masses:dict,
        chemical_masses_uncertainties:dict,
        batch:str,
        manufacturer:str,
        manufacturing_date:str,
        references:str,
        density:Union[float, None]=None,
        density_uncertainty:Union[float, None]=None,
        substance_amount_per_volume:Union[dict, None]=None
        ) -> None:
        ''' This funciton initializes a Solution object.
        
        Inputs:
        ID: a str representing a UUID for the solution
        name: a string giving the name of the solution, by which it shall be referenced in the experiment
        reservoir: a string giving the name of the node belonging to the reservoir, in which the solution is supplied
        pump: a string giving the name of the pump, which belongs to the respective solution
        mass: a float representing the total mass of the mixture resulting from the addition of the masses of chemicals as specified in chemical_masses
        mass_uncertainty: a float reporting the uncertainty of the total mass of the solution
        mass_unit: a string reporting the unit of the mass. This is currently not used by the code, but serves rather for documentation purposes.
        denstiy: a float representing the density of the chemical in g/cm^3
        density_uncertainty: a float giving the uncertainty or the error of the given density. Currently, this is included for the sake of completeness as it may be
                            useful in the future to do error calculations
        density_unit: a string documenting the unit of the density. This is currently not used by the code, but serves rather for documentation purposes.
        denisty_temperature: a float representing the temperature in Kelvin, at which the density is given
        chemical_masses: a dictionary comprising the masses of each chemical in the mixture
        chemical_masses_uncertainties: a dictionary comprising the uncertainties of the mass of each chemical in the mixture
        substance_amount_per_volume: a dictionary giving the substance amount per volume as values with the chemicals' names as keys or a dictionary of the parameters
                                  for a call for get_substance_amount_per_volume() as keys and their values as values
        batch: the batch number of the chemical
        manufacturer: the manufacturer of the chemical
        manufacturing_date: the date, at which the chemical was manufactured in the format dd.mm.yy
        references: a string representing the references, if literature values are used for e.g. the denisty and/or molar mass

        Outputs:
        This function has not outputs. '''

        # Check the input types
        typeCheck(func=Solution.__init__, locals=locals())

        self.ID = ID
        self.name = name
        self.reservoir = reservoir
        self.pump = pump
        self.mass_total = mass_total
        self.mass_total_uncertainty = mass_total_uncertainty
        self.mass_unit = mass_unit
        self.density = density
        self.density_uncertainty = density_uncertainty
        self.density_unit = density_unit
        self.density_temperature = density_temperature
        self.chemical_masses = chemical_masses
        self.chemical_masses_uncertainties = chemical_masses_uncertainties
        self.chemicals = [chem for chem in chemical_masses.keys() if not np.isclose(chemical_masses[chem], 0.0, atol=1e-15, rtol=1e-15)]
        self.batch = batch
        self.manufacturer = manufacturer
        self.manufacturing_date = manufacturing_date
        self.references = references
        self.substance_amount_per_volume = substance_amount_per_volume
        
        # If substance_amount_per_volume is None, it is initialized as an empty dictionary
        if substance_amount_per_volume is None:
            self.substance_amount_per_volume = {}
        elif list(substance_amount_per_volume.keys()) == self.chemicals:
            self.substance_amount_per_volume = substance_amount_per_volume
        # If the keys of substance_amount_per_volume match the arguments of the get_substance_amount_per_volume function, it shall be used to call this function
        elif ['self'] + list(substance_amount_per_volume.keys()) == getfullargspec(self.get_substance_amount_per_volume).args:
            # In this case, call the function to fill the substance_amount_per_volume attribute
            self.get_substance_amount_per_volume(chemicalsDict=substance_amount_per_volume['chemicalsDict'], pumps=substance_amount_per_volume['pumps'], valves=substance_amount_per_volume['valves'], endpoint=substance_amount_per_volume['endpoint'])
        else:
            # If the keys of the substance_amount_per_volume dictionary match the chemicals, it is likely to be a substance_amount_per_volume dictionary
            # If none of the above cases matches, it must be a wrong dictionary
            raise ValueError(f"The substance_amount_per_volume dictionary {substance_amount_per_volume} can neither be used as is nor is is suitable to call get_substance_amount_per_volume.")

    def get_substance_amount_per_volume(self, chemicalsDict:Union[dict, str], pumps:dict={}, valves:dict={}, endpoint:str=conf["CetoniDevice"]["waste"]) -> None:
        ''' This function determines the substance amount per Volume for a stock solution. To do so, it needs the information about the chemicals and the density of the
        solution. If the density is not available, it will be measured. The results will be saved to the self.substance_amount_per_volume attribute, which can then be used
        as the definintion of the solution's composition.
        
        Inputs:
        chemicalsDict: a dictionary of Chemical objects
        
        Outputs:
        This function has no outputs. '''

        # Check the input types
        typeCheck(func=Solution.get_substance_amount_per_volume, locals=locals())

        # Get the chemicalsDict as a dict
        chemicalsDict = get_chemicalsDict(chemicalsDict=chemicalsDict)

        # Check, whether the density of the solution is already contained in the solution object
        if self.density == None:
            # If there is no density given in the object, measure it
            self.density, self.density_uncertainty = self.get_SolutionDensity(pumps=pumps, valves=valves, endpoint=endpoint)
        
        # Determine the substance amount per volume of solution (molarity) for each of the chemicals
        for chemical in self.chemicals:#_masses.keys():
            self.substance_amount_per_volume[chemical] = (self.chemical_masses[chemical] / chemicalsDict[chemical].molar_mass)/(self.mass_total / self.density)
        print(self.ID, self.name, self.substance_amount_per_volume)
        
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

def generate_solutionsDict(
    solutionsDef:str,
    pumps:dict,
    valves:dict,
    chemicalsDict:Union[dict, str]=conf['solutionHandler']['chemicalsDict'],
    savePath:str=conf['solutionHandler']['solutionsDict']
    ) -> dict:
    ''' This function generates a dictionary of solutions from a .csv file in the path specified by solutionsDef, saves it to a .py file and returns a dictionary
    of soltuions.
    
    Inputs:
    solutionsDef: a string specifying the path to a .csv file defining the properties of the solutions
    savePath: a string specifying the path, where the dictionary shall be saved.
    
    Outputs:
    solutionsDict: a dictionary of Solution objects based on the solutionsDef '''


    # Check the input types
    typeCheck(func=generate_solutionsDict, locals=locals())

    chemicalsDict = get_chemicalsDict(chemicalsDict=chemicalsDict)

    # Load the information about the solutions as a dataframe
    solutions = pd.read_csv(solutionsDef, sep=';', index_col="ID")

    # Initialize the solutionsDict and the save version
    solutionsDict = {}
    solutionsDict_save = {}

    ## Go through all the solutions, generate Solutions objects and save them to a dictionary
    for solution in solutions.index:
        sol = solutions.loc[[solution]]

        # Get the chemicals from the column names
        chems = [col for col in sol.columns if col in chemicalsDict.keys()]

        # Initialize chemical_masses and chemical_masses_uncertainties
        chemical_masses = {}
        chemical_masses_uncertainties = {}

        # Get all the properties of the solution and generate the Solution object
        for c in chems:
            if 'uncertainty' not in c:
                chemical_masses[c] = sol[c].values[0]
            else:
                c_split = c.split('_')[0]
                chemical_masses_uncertainties[c_split] = sol[c].values[0]
        sol = sol.T.to_dict()[solution]   # https://stackoverflow.com/questions/26716616/convert-a-pandas-dataframe-to-a-dictionary
        sol['chemical_masses'] = chemical_masses
        sol['chemical_masses_uncertainties'] = chemical_masses_uncertainties
        sol['mass_unit'] = conf['solutionHandler']['units']['mass']
        sol['density_unit'] = conf['solutionHandler']['units']['density']
        sol["ID"] = solution

        for k in chems:
            del sol[k]
            del sol[f"{k}_uncertainty"]

        S = Solution(**sol)
        
        # Get the density from the file or the measurement
        if not np.isnan(sol['density']) and not np.isnan(sol['density_uncertainty']):
            density = sol['density']
            density_uncertainty = sol['density_uncertainty']
        elif np.isnan(sol['density']) and np.isnan(sol['density_uncertainty']):
            density, density_uncertainty = S.get_SolutionDensity(pumps=pumps, valves=valves)

        S.density = density
        S.density_uncertainty = density_uncertainty

        # get the substance amount per volume
        S.get_substance_amount_per_volume(chemicalsDict=chemicalsDict)

        # Add the solution to the solutionsDict
        solutionsDict[solution] = S

        # assemble the save version of the solutionsDict
        solutionsDict_save[solution] = S.__dict__

    # Save the dictionary to a .py file
    folder = str(Path(savePath).resolve().parent)
    filename = Path(savePath).resolve().stem
    extension = Path(savePath).resolve().suffix.lstrip(".")
    saveToFile(folder=folder, filename=filename, extension=extension, data=f'solutionsDict = {str(solutionsDict_save)}')
    logger_solutionHandler.info(f"SolutionsDict:\n{solutionsDict_save}")
    return solutionsDict


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
        del value["chemicals"]
        solutionsDict[key] = Solution(**value)
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


### get_fractions #############################################################################################################################################################

def get_volFracs(mixingRatio:dict, chemicalsDict:Union[dict, str, None], solutionsDict:Union[dict, str], input_fraction:str, output_fraction:str) -> Tuple[dict, dict, dict, float]:
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
        concentrationMatrix_sol = pd.DataFrame.from_dict(data=solutionsDict[stockSolution].substance_amount_per_volume, orient='index', columns=[solutionsDict[stockSolution].ID])
        concentrationMatrix = pd.concat([concentrationMatrix, concentrationMatrix_sol], axis=1, ignore_index=False)

    ## Assemble vector representing the target composition
    # get the amount of substance for each chemical from the mixing ratio depending on the input
    if input_fraction == 'molPerMol':
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
        # Make the start value a pandas Series
        volumes_start = pd.Series(data=volumes_start)
    print("\n volumes start", volumes_start)

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
    if input_fraction == 'molPerMol':
        n_result = concentrations.dot(volFracs)
        setRatio = n_result / np.sum(n_result)

    # Gather all the return values and return them
    requestedRatio = mixingRatio
    # Get only the volFracs, which are non-zero to avoid unnecessary filling of syringes
    volumeFractions = dict(volFracs.drop(volFracs[np.isclose(volFracs, 0.0, rtol=1e-15)].index))
    setRatio = dict(setRatio.drop(setRatio[np.isclose(setRatio, 0.0, rtol=1e-15)].index))
    minSquaredError = vols.fun

    return requestedRatio, volumeFractions, setRatio, minSquaredError
    
def get_fractions(mixingRatio:dict, chemicalsDict:Union[dict, str, None], solutionsDict:Union[dict, str], input_fraction:str, output_fraction:str) -> Tuple[dict, dict, dict, float]:
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
    typeCheck(func=get_fractions, locals=locals())

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
        concentrationMatrix_sol = pd.DataFrame.from_dict(data=solutionsDict[stockSolution].substance_amount_per_volume, orient='index', columns=[solutionsDict[stockSolution].ID])
        concentrationMatrix = pd.concat([concentrationMatrix, concentrationMatrix_sol], axis=1, ignore_index=False)

    if input_fraction != output_fraction:
        ## Assemble vector representing the target composition
        # get the amount of substance for each chemical from the mixing ratio depending on the input
        if (input_fraction == 'molPerMol') and (output_fraction == "volPerVol"):
            # In this case, the mixing ratio is given in mol/mol for each chemical and
            # the output shall be the mixing ratio of the stock solutions in mL/mL
            # We assume to mix 1 mol of total mixture and use the mixing ratio as it is, because only the ratios matter
            targetVector_n = pd.DataFrame.from_dict(data=mixingRatio, orient='index', columns=['target'])

            # Add the target to the matrix to ensure matching indices
            matrix_target = pd.concat([concentrationMatrix, targetVector_n], axis=1, ignore_index=False)
            # Filling NaN values arising due to chemicals not included in the requested mixtures with 0.0
            matrix_target.fillna(value=0.0, inplace=True)

        elif (input_fraction == "volPerVol") and (output_fraction == "molPerMol"):
            # In this case, the mixing ratio is given in mL/mL for each stock solution and
            # the output shall be the mixing ratio of the chemicals in mol/mol
            # We assume to mix 1 L of total mixture and use the mixing ratio as it is, because only the ratios matter
            targetVector_V = pd.DataFrame.from_dict(data=mixingRatio, orient='index', columns=['target'])

            # invert the concentration matrix to account for the equation n/c = V with V being the searched quantity
            # in this case as opposed to V * c = n with n being the searched for quantity in the target volPerVol case
            matrix = pd.DataFrame(data=np.linalg.pinv(concentrationMatrix),
                                              columns=concentrationMatrix.index,
                                              index=concentrationMatrix.columns)  # https://stackoverflow.com/questions/40858835/calculating-the-inverse-of-a-matrix-with-pandas

            # Add the target to the matrix to ensure matching indices
            matrix_target = pd.concat([matrix, targetVector_V], axis=1, ignore_index=False)
            # Filling NaN values arising due to chemicals not included in the requested mixtures with 0.0
            matrix_target.fillna(value=0.0, inplace=True)

        # Get the indices related to the matrix but not the target column
        matrixColumns = list(matrix_target.columns)
        matrixColumns.remove('target')
        # Get the matrix from the matrix_target
        matrix = matrix_target[matrixColumns]
        # Get the target column from the matrix_target
        target = matrix_target['target']

         # Invert the matrix
        matrix_inverse = pd.DataFrame(np.linalg.pinv(matrix), columns=matrix.index, index=matrix.columns)

        # Calculate the desired fractions
        fractions = matrix_inverse.dot(target)

        # Normalize the fractions
        fractions_normalized = fractions / np.sum(fractions)

        # Collect the fractions in a dictionary with the names of the stock solutions or chemicals as keys,
        # which are obtained from the matrix
        fractions = pd.Series(data=fractions, index=matrix.columns)

        # Calculate back to the previous type of fraction to check for the error
        fractions_inputtype = matrix.dot(fractions)

        err = pd.Series(np.zeros(len(target)), index=matrix.index)
        deviation = fractions_inputtype - target
        for i in range(len(target)):
            err[i] = deviation[i]/target[i]
        print("error individual\n", err)
        print("\n\n\n fractions \n", fractions)
        print("\n\n\n fractions_normalized \n", fractions_normalized)

        # Gather all the return values and return them
        requestedRatio = mixingRatio
        # Get only the fractions, which are non-zero to avoid unnecessary filling of syringes
        fractions_output = dict(
            fractions_normalized.drop(
                fractions_normalized[np.isclose(fractions_normalized, 0.0, atol=1e-15)].index
                )
                )
        setRatio = dict(
            fractions_inputtype.drop(
                fractions_inputtype[np.isclose(fractions_inputtype, 0.0, atol=1e-15)].index
                )
                )
        error = err

    else:
        raise ValueError(f"Unsupported input fraction type {input_fraction}. Supporting only 'molPerMol'.")

    return requestedRatio, fractions_output, setRatio, error


def get_fractions_2(mixingRatio:dict, chemicalsDict:Union[dict, str, None], solutionsDict:Union[dict, str], input_fraction:str, output_fraction:str) -> Tuple[dict, dict, dict, float]:
    ''' This function determines the volume fractions of the stock solutions required to get as close as possible to the requested mixing ratio.
    
    Inputs:
    mixingRatio: a dictionary with the names of the relevant chemicals as keys and their molar fraction, mass fraction, volumetric fraction or molarity as values
    chemicalsDict: a dictionary containing chemical objects as values, or a string specifying the path to a chemicalsDict or None
    solutionsDict: a dictionary containing solution objects as values, or a string specifying the path to a solutionsDict
    fraction: a string specifying, whether the fraction is a molar fraction, mass fraction, volumetric fraction or molarity, currently supports molPerMol and volPerVol
    
    Outputs:
    requestedRatio: the mixingRatio as it was input
    volumeFractions: the volume fractions for each stock solution as determined by the minimization of the squared error. The keys are the names of the chemicals and the
                     values are the volumeFractions
    setRatio: a dictionary containing the calculated mixing ratio closest to the desired one. The keys are the names of the chemicals and the values are the mixing ratio
              resulting from the calculated volume fractions in the type of fraction specified by fraction
    minSquaredError: a float representing the minimum squared error of the calculated setRatio compared to the requestedRatio '''

    # Check the input types
    typeCheck(func=get_fractions, locals=locals())

    # Get the chemicalsDict as dictionary
    chemicalsDict = get_chemicalsDict(chemicalsDict=chemicalsDict)
    # Get the chemicalsDict as dictionary
    solutionsDict = get_solutionsDict(solutionsDict=solutionsDict)

    ## Assemble the linear system of equations
    ## Get the matrix of stock solutions containing the concentrations of the chemicals in one of the stock solutions as a column
    concentrationMatrix = pd.DataFrame()
    for stockSolution in solutionsDict.keys():
        concentrationMatrix_sol = pd.DataFrame.from_dict(data=solutionsDict[stockSolution].substance_amount_per_volume, orient='index', columns=[solutionsDict[stockSolution].ID])
        concentrationMatrix = pd.concat([concentrationMatrix, concentrationMatrix_sol], axis=1, ignore_index=False)

    if input_fraction != output_fraction:
        ## Assemble vector representing the target composition
        # get the amount of substance for each chemical from the mixing ratio depending on the input
        if (input_fraction == 'molPerMol') and (output_fraction == "volPerVol"):
            # In this case, the mixing ratio is given in mol/mol for each chemical and
            # the output shall be the mixing ratio of the stock solutions in mL/mL
            # We assume to mix 1 mol of total mixture and use the mixing ratio as it is, because only the ratios matter
            targetVector_n = pd.DataFrame.from_dict(data=mixingRatio, orient='index', columns=['target'])

            # Add the target to the matrix to ensure matching indices
            matrix_target = pd.concat([concentrationMatrix, targetVector_n], axis=1, ignore_index=False)
            # Filling NaN values arising due to chemicals not included in the requested mixtures with 0.0
            matrix_target.fillna(value=0.0, inplace=True)
            start = np.full(len(concentrationMatrix.columns), fill_value=1./len(concentrationMatrix.columns))

        elif (input_fraction == "volPerVol") and (output_fraction == "molPerMol"):
            # TODO: This part needs to be improved. It currently does not yet work.
            # In this case, the mixing ratio is given in mL/mL for each stock solution and
            # the output shall be the mixing ratio of the chemicals in mol/mol
            # We assume to mix 1 L of total mixture and use the mixing ratio as it is, because only the ratios matter
            targetVector_V = pd.DataFrame.from_dict(data=mixingRatio, orient='index', columns=['target'])
            # invert the concentration matrix to account for the equation n/c = V with V being the searched quantity
            # in this case as opposed to c * V = n with n being the searched for quantity in the target volPerVol case
            matrix = {}
            for c in concentrationMatrix.columns:
                matrix[c] = np.reciprocal(concentrationMatrix[c].to_numpy())
            matrix = pd.DataFrame(matrix).T
            matrix = pd.DataFrame(data=matrix,
                columns=concentrationMatrix.index,
                index=concentrationMatrix.columns)  # https://stackoverflow.com/questions/40858835/calculating-the-inverse-of-a-matrix-with-pandas
            # Add the target to the matrix to ensure matching indices
            matrix_target = pd.concat([matrix, targetVector_V], axis=1, ignore_index=False)
            # Filling NaN values arising due to chemicals not included in the requested mixtures with 0.0
            matrix_target.fillna(value=0.0, inplace=True)
            start = np.full(len(matrix.columns), fill_value=1./len(matrix.columns))

        else:
            logger_solutionHandler.error(
                f"Unsupported input fraction type {input_fraction}. Supporting only 'molPerMol'.",
                stack_info=True
            )
            raise ValueError(f"Unsupported input fraction type {input_fraction}. Supporting only 'molPerMol'.")


        # Get the indices related to the concentrations but not the target column
        non_target_columns = list(matrix_target.columns)
        non_target_columns.remove('target')
        # Get the concentration matrix from the concentrationMatrix_target
        non_targets = matrix_target[non_target_columns]
        # Get the target column from the concentrationMatrix_target
        target = matrix_target['target']
        

        ## Solve the system of linear equations; if an exact solution is not possible,
        # which will be mostly the case, get a minimum 2-norm approximation   # -> https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
        # Numeric method suggested by Prof. Dr.-Ing. Helge Stein
        def lgs(x, A, target):
            result = A.dot(x)
            # print('result_n \n', result_n)
            result_normalized = result / np.sum(result)
            # print('result_n_normalized \n', result_n_normalized, np.sum(result_n))
            deviation = np.sqrt(np.sum((result_normalized - target)**2.))
            # print('deviation \n', deviation)
            return deviation

        # Add boundaries to restrict the results to positive values as only addition of volumes is possible and
        # a stock solution cannot be more than purely used
        bounds = [(0,1.) for i in start]
        # Add constraints to limit the ouput to reasonable results
        # each element of the result must be positive (only additions possible)
        ineq = {
            "type": "ineq",
            "fun": lambda x: x
        }
        # fractions must sum to 1.
        eq = {
            "type": "eq",
            "fun": lambda x: np.array(
                [np.sum(x) -1.]
            )
        }

        # Get the optimized volumes for the stock solutions
        result_opt = minimize(lgs, x0=start, bounds=bounds, constraints=[ineq, eq], method="SLSQP", args=(non_targets, target))
        # result_opt = shgo(lgs, bounds=bounds, constraints=[ineq, eq], minimizer_kwargs={"method": "SLSQP"}, args=(non_targets, target), iters=3) # , "args": (non_targets, target)

        if not result_opt.success:
            logger_solutionHandler.error(
                f"The minimization did not succeed. \n {result_opt}",
                stack_info=True
            )
            raise ValueError(f"The minimization did not succeed. \n {result_opt}")

        # Round the result to eliminate very small fractions
        result = np.round(result_opt.x, 2)

        # Collect the resulting fractions in a dictionary with the columns of matrix as keys
        res = pd.Series(data=result, index=non_targets.columns)

        ## Calculate the ratio resulting from the found result in the same type of fraction as the input
        set_ratio = non_targets.dot(res)
        setRatio = set_ratio / np.sum(set_ratio)
        setRatio = np.round(setRatio, 2)


        # Gather all the return values and return them
        requestedRatio = mixingRatio
        # Get only the volFracs, which are non-zero to avoid unnecessary filling of syringes
        fractions_output = dict(res.drop(res[np.isclose(res, 0.0, rtol=1e-15)].index))
        setRatio = dict(setRatio.drop(setRatio[np.isclose(setRatio, 0.0, rtol=1e-15)].index))
        deviation = result_opt.fun

        logger_solutionHandler.info(
            (f"requested_ratio: \n {requestedRatio} \n"
             f"fractions_output: \n {fractions_output} \n"
             f"set_ratio: \n {setRatio} \n"
             f"deviation: \n {deviation}"
            )
        )

        return requestedRatio, fractions_output, setRatio, deviation
