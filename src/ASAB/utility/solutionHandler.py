# ## Get the configuration
# try:
#     # if there is a main file, get conf from there
#     from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
# except ImportError:
#     # if the import was not successful, go to default config
#     from ASAB.configuration import default_config
#     conf = default_config.config

import numpy as np
import pandas as pd
from scipy.optimize import nnls # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.nnls.html#scipy.optimize.nnls

conf={}
conf["solutionHandler"] = {'chemicals': [{'shortName': 'LiPF6', 'name': 'lithium hexafluorophosphate', 'molarMass': 151.90, 'molarMassUnit': 'g/mol'},
                                            {'shortName': 'EC', 'name': 'ethylene carbonate', 'molarMass': 88.06, 'molarMassUnit': 'g/mol'},
                                            {'shortName': 'EMC', 'name': 'ethyl methyl carbonate', 'molarMass': 104.10, 'molarMassUnit': 'g/mol'},
                                            {'shortName': 'DMC', 'name': 'dimethyl carbonate', 'molarMass': 90.08, 'molarMassUnit': 'g/mol'}],
                            'solutions':[{'name': "LiPF6_salt_in_EC_DMC_1:1", 'mix': {'LiPF6': {'value': 1., 'unit': 'mol/L'}, 'EC': {'value': 0.50, 'unit': 'g/g'}, 'DMC': {'value': 0.50, 'unit': 'g/g'}}, 'density': 1.2879, 'reservoir': 'Reservoir6'},
                                        {'name': "EC_DMC_1:1", 'mix': {'EC': {'value': 0.50, 'unit': 'g/g'}, 'DMC': {'value': 0.50, 'unit': 'g/g'}}, 'density': 1.2011, 'reservoir': 'Reservoir5'},
                                        {'name': "LiPF6_salt_in_EC_EMC_3:7", 'mix': {'LiPF6': {'value': 1., 'unit': 'mol/L'}, 'EC': {'value': 0.30, 'unit': 'g/g'}, 'EMC': {'value': 0.70, 'unit': 'g/g'}}, 'density': 1.1964, 'reservoir': 'Reservoir4'},
                                        {'name': "EC_EMC_3:7", 'mix': {'EC': {'value': 0.30, 'unit': 'g/g'}, 'EMC': {'value': 0.70, 'unit': 'g/g'}}, 'density': 1.1013, 'reservoir': 'Reservoir3'}]}

class Chemical:
    ''' This class describes a chemical with all its properties relevant to the ASAB system. '''
    def __init__(self, shortName: str, name:str, molarMass:float, molarMassUnit:str):
        self.shortName = shortName
        self.name = name
        self.molarMass = molarMass
        self.molarMassUnit = molarMassUnit

class Solution:
    ''' This class describes a solution with the properties relevant to ASAB. '''
    def __init__(self, name:str, mix:dict, density:float, reservoir:str, chemicalsDict:dict):
        self.name = name
        self.chemicals = {k: chemicalsDict[k] for k in mix.keys()}
        self.mix = mix
        self.density = density
        self.reservoir = reservoir
        self.concentrations = {}

def getStockSolutions(solutionconfig=conf['solutionHandler']):
    ''' This function generates solutions based on the entries in the config file. '''
    chemicals = {}
    for chem in solutionconfig['chemicals']:
        chemicals[chem['shortName']] = Chemical(shortName=chem['shortName'], name=chem['name'], molarMass=chem['molarMass'], molarMassUnit=chem['molarMassUnit'])
    
    solutions = {}
    for sol in solutionconfig['solutions']:
        solutions[sol['name']] = Solution(name=sol['name'], mix=sol['mix'], density=sol['density'], reservoir=sol['reservoir'], chemicalsDict=chemicals)
    
    return solutions

def getVolFracs(mixingRatio:dict, config:dict=conf['solutionHandler']):
    ''' This function calculates the volume fractions for each solution in the reservoirs to obtain the correct mixing ratio requested or at least a mixture as similar as
    possible. The composition of the mixture is entered as a dict of mole fractions. Mixing volumes are disregarded.
    input:
    mixingRatio: dict of mole fractions for each chemical
    config: dict containing the information regarding the available stock solutions

    output:
    volFracs: dict of volume fractions for each stock solution
    vols_residual: float representing the residual of the solution of the linear equation system
    '''
    ## Get the stock solutions
    stockSolutions = getStockSolutions(solutionconfig=config)
  
    for stocksol in stockSolutions.keys():
        print(stocksol)
        sol = stockSolutions[stocksol]
        ## Get the mass of 1L of the solution, factor 1000, because density is expected to be given in the unit g/cm^3
        m_1L = sol.density * 1000.
        try:
            sol.concentrations['LiPF6'] = sol.mix['LiPF6']['value']
            ## Get the mass of the solvent by subtracting the mass of the concentration of the salt (the amount of salt in 1 L of the solution)
            m_solv = m_1L - sol.mix['LiPF6']['value'] * sol.chemicals['LiPF6'].molarMass
        except KeyError:
            sol.concentrations['LiPF6'] = 0.0
            m_solv = m_1L
        ## Get the masses and the concentrations of the solvent components based on the solvent mass ratio
        m_solvComp = {}
        for c in sol.mix.keys():
            if c != 'LiPF6':
                m_solvComp[c] = sol.mix[c]['value'] * m_solv
                sol.concentrations[c] = m_solvComp[c] / sol.chemicals[c].molarMass
        # totalMolPerLiter = np.sum(list(sol.concentrations.values()))
        # for c in sol.concentrations.keys():
        #     sol.concentrations[c] = sol.concentrations[c] / totalMolPerLiter
        # print(sol.concentrations)
    
    ## Assemble the linear system of equations
    ## Get the matrix of stock solutions containing the concentrations of the chemicals in one of the stock solutions as a column
    # get all chemicals contained in any of the solutions
    chems = []
    for s in stockSolutions.values():
        chems.extend(s.concentrations.keys())
    # remove duplicates
    chems = pd.Series(chems).unique()
    # get the number of stock solutions
    noStockSols = len(stockSolutions.keys())
    # initialize a numpy array representing the concentrations of each chemical in a stock solution in a column
    concentrationArray = pd.DataFrame(np.zeros((len(chems), noStockSols)), columns=stockSolutions.keys(), index=chems)
    # fill the concentration array
    for s in stockSolutions.values():
        for ch, c in s.concentrations.items():
            concentrationArray.loc[ch, s.name] = c
    print('C_Array', concentrationArray)
    
    
    ## Assemble vector representing the target composition
    # extend the vector to contain all chemicals, if this is not the case to match the dimensions of the matrix
    for item in chems:
        if not item in mixingRatio.keys():
            mixingRatio[item] = 0.0
    targetComp = pd.Series(mixingRatio, name='target', index=mixingRatio.keys())

    ## Solve the system of linear equations; if an exact solution is not possible, which will be mostly the case, get a minimum 2-norm approximation   # -> https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html
    vols, vols_residual = nnls(np.array(concentrationArray), np.array(targetComp), maxiter=None)
    # vols, vols_residuals, concentrationArray_rank, concentrationArray_singularValues = np.linalg.lstsq(np.array(concentrationArray), np.array(targetComp), rcond=None)
    print('vols', vols)
    volFracs = [(v/(np.sum(vols))) for v in vols]
    print('volfracs', volFracs)
    volFracs = pd.Series(volFracs, index=stockSolutions.keys())
    volFracs = dict(volFracs)
    return volFracs, vols_residual

S = getStockSolutions()

VF, V_res = getVolFracs(mixingRatio={'LiPF6': 0.039, 'EC': 0.444, 'EMC': 0.166, 'DMC': 0.352})
print(VF, V_res)

# # # TODO: Move this fuction to compositionHandler.py
# # def getVolFracs(fracs:tuple, labels:tuple, density:dict, molarMass:dict, mode:str="mole"):
# #     ''' This function calculates volume fractions from molar fractions. Further options will be available as needed. Implemented for ternary only! It negelects the mixing volume. '''
# #     # TODO: Test this function!!!
    
# #     ## Check the input types
# #     inputTypes = {'fracs':tuple, 'labels':tuple, 'density':dict, 'molarMass':dict, 'mode':str}
# #     inputObjects = dict(**locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
# #     typeCheck(inputObjects=inputObjects, inputTypes=inputTypes)
    
# #     fracs = dict(zip(labels, fracs))
# #     # Prepare a dataframe for the ratios of each relevant quantity
# #     empty = np.full((len(fracs), len(fracs)), fill_value=np.NaN)
# #     # Generate the dataframes
# #     moleRatios = pd.DataFrame(data=empty.copy(), columns=labels, index=labels)
# #     densityRatios = pd.DataFrame(data=empty.copy(), columns=labels, index=labels)
# #     massRatios = pd.DataFrame(data=empty.copy(), columns=labels, index=labels)
# #     # Get the positions of the relevant ratios
# #     permutations = list(it.permutations(labels, 2))
# #     # Fill the dataframes with the relevant ratios
# #     for p in permutations:
# #         # If the fraction would require to divide by zero, the value shall be set to NaN. Zero cannot be used, because this will lead to the calculation of the volume fraction to 1.0.
# #         try:
# #             moleRatios.loc[p[0], p[1]] = fracs[p[0]]/fracs[p[1]]
# #         except ZeroDivisionError:
# #             moleRatios.loc[p[0], p[1]] = np.nan
# #         densityRatios.loc[p[0], p[1]] = density[p[0]]/density[p[1]]
# #         massRatios.loc[p[0], p[1]] = molarMass[p[0]]/molarMass[p[1]]
# #     # Initialize dictionary to store the volume fractions
# #     volFracs = {}
# #     # Calculate the volume fractions
# #     volFracs[labels[0]] = 1./(moleRatios.loc[labels[2], labels[0]]*densityRatios.loc[labels[0], labels[2]]*massRatios.loc[labels[2],labels[0]] + 1. + moleRatios.loc[labels[1], labels[0]]*densityRatios.loc[labels[0], labels[1]]*massRatios.loc[labels[1],labels[0]])
# #     volFracs[labels[1]] = 1./(moleRatios.loc[labels[0], labels[1]]*densityRatios.loc[labels[1], labels[0]]*massRatios.loc[labels[0],labels[1]] + 1. + moleRatios.loc[labels[2], labels[1]]*densityRatios.loc[labels[1], labels[2]]*massRatios.loc[labels[2],labels[1]])
# #     volFracs[labels[2]] = 1./(moleRatios.loc[labels[1], labels[2]]*densityRatios.loc[labels[2], labels[1]]*massRatios.loc[labels[1],labels[2]] + 1. + moleRatios.loc[labels[0], labels[2]]*densityRatios.loc[labels[2], labels[0]]*massRatios.loc[labels[0],labels[2]])
# #     # Replace nan values by 0.0 in order to get numeric values for all volume fractions
# #     for key in volFracs.keys():
# #         volFracs[key] = np.nan_to_num(volFracs[key], nan=0.0)
# #     return volFracs