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
        self.denisty = density
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

# # TODO: put this into config
# # Set the assumed errors for error calculation
# errors = pd.DataFrame(data={'mass':{'EMC': 0.0005, 'EC': 0.0005, 'LiTDI': 0.0005, 'LiTDI+LiPF6': 0.0005, 'LiPDI': 0.0005, 'LiPDI+LiPF6': 0.0005, 'LiHDI': 0.0005, 'LiHDI+LiPF6': 0.0005, 'LiPF6': 0.0005, '1M_LiPF6': 0.0005, 'none': 0.0},
#                             'molarMass': {'EMC': 0.0, 'EC': 0.0, 'LiTDI': 0.0, 'LiTDI+LiPF6': 0.0, 'LiPDI': 0.0, 'LiPDI+LiPF6': 0.0, 'LiHDI': 0.0, 'LiHDI+LiPF6': 0.0, 'LiPF6': 0.0, '1M_LiPF6': 0.0, 'none': 0.0},
#                             'amountOfSubstance':{'EMC': 0.0, 'EC': 0.0, 'LiTDI': 0.0, 'LiTDI+LiPF6': 0.0, 'LiPDI': 0.0, 'LiPDI+LiPF6': 0.0, 'LiHDI': 0.0, 'LiHDI+LiPF6': 0.0, 'LiPF6': 0.0, '1M_LiPF6': 0.0, 'none': 0.0},
#                             'massFractions': {'EMC': 0.0, 'EC': 0.0, 'LiTDI': 0.0, 'LiTDI+LiPF6': 0.0, 'LiPDI': 0.0, 'LiPDI+LiPF6': 0.0, 'LiHDI': 0.0, 'LiHDI+LiPF6': 0.0, 'LiPF6': 0.0, '1M_LiPF6': 0.0, 'none': 0.0},
#                             'moleFractions': {'EMC': 0.0, 'EC': 0.0, 'LiTDI': 0.0, 'LiTDI+LiPF6': 0.0, 'LiPDI': 0.0, 'LiPDI+LiPF6': 0.0, 'LiHDI': 0.0, 'LiHDI+LiPF6': 0.0, 'LiPF6': 0.0, '1M_LiPF6': 0.0, 'none': 0.0},
#                             'density': {'EMC': 0.0, 'EC': 0.0, 'LiTDI': 0.0, 'LiTDI+LiPF6': 0.0, 'LiPDI': 0.0, 'LiPDI+LiPF6': 0.0, 'LiHDI': 0.0, 'LiHDI+LiPF6': 0.0, 'LiPF6': 0.0, '1M_LiPF6': 0.0, 'none': 0.0}})

# ## Define a function to calculate weight fractions
# def get_mass_fraction(substance:str, massesDict:dict, errors:pd.DataFrame):
#     ''' This funciton takes a key for the substance, for which the mass fraction shall be calculated and a dictionary of all the masses involved as
#     input and returns the mass fraction of the requested substance. '''
#     # Get an array of all the masses
#     ms = np.array(list(massesDict.values()))
#     # Get an array of all the errors
#     errs = np.array(errors['mass'].values)
#     # Calculate the mass fraction
#     w = float(massesDict[substance]) / np.sum(ms)
#     # Calculate the error of the mass fraction
#     dw = np.abs((np.sum(ms) - massesDict[substance]) / ((np.sum(ms))**2)) * errors.loc[substance, 'mass'] + np.abs(-((massesDict[substance]) / ((np.sum(ms))**2.))) * (np.sum(errs) - errors.loc[substance, 'mass'])
#     return w, dw

# def get_amount_of_substance(substance:str, molarMassesDict:dict, massesDict:dict, errors:pd.DataFrame):
#     ''' This function takes the label of a substance, a dict of molar masses and a dict of masses as input and returns the amount of substance for
#     the substance requested. '''
#     # Only, if the substance has a non-zero molar mass, the evaluation is possible. Otherwise, the substance is assumed not to be present in the mixture.
#     if molarMasses[substance] != 0.0:
#         # Calculate the amount of substance
#         n = massesDict[substance] / molarMassesDict[substance]
#         # Calculate the error of the amount of substance
#         dn = np.abs(1./molarMassesDict[substance]) * errors.loc[substance, 'mass'] + np.abs(- (massesDict[substance] / (molarMassesDict[substance])**2.)) * errors.loc[substance, 'molarMass']
#     else:
#         n = 0.0
#         dn = 0.0
#     return n, dn

# def get_mole_fraction(substance:str, amountsOfSubstanceDict:dict, errors:pd.DataFrame):
#     ''' This function tabes the label of a substance and a dict of the amounts of substances to output the mole fraction for the substance requested. '''
#     # Get an array of all the amounts of substance
#     ns = np.array(list(amountsOfSubstanceDict.values()))
#     # Get an array of the errors of the amounts of substance
#     errs = np.array(list(errors["amountOfSubstance"].values))
#     # Calculate the mole fraction
#     x = float(amountsOfSubstanceDict[substance]) / np.sum(ns)
#     # Calculate the error of the mole fraction
#     dx = np.abs((np.sum(ns) - amountsOfSubstanceDict[substance]) / ((np.sum(ns))**2.)) * errors.loc[substance, 'amountOfSubstance'] + np.abs(-((amountsOfSubstanceDict[substance]) / ((np.sum(ns))**2.))) * (np.sum(errs) - errors.loc[substance, 'amountOfSubstance'])
#     return x, dx

# ## calculate mole fractions for the chemicals in each stock solution
# errors_stockSol = errors.copy()
# # iterate over the salts
# for salt in massData.loc[massData["concentration"] == 1.5, "salt"].unique():
#     # exclude LiPF6, because this stock solution is based on a commercial solution
#     if salt != "LiPF6":
#         # get the masses of EMC and EC
#         mEMC = massData.loc[(salt, 1.5), "mass of EMC / g"]
#         mEC = massData.loc[(salt, 1.5), "mass of EC / g"]
#         # try to get the mass of the salt
#         try:
#             mSalt = massData.loc[(salt, 1.5), "mass of salt / g"]
#         except KeyError:
#             # if the salt is "none" for the pure solvent solution, set mSalt to 0.0
#             mSalt = 0.0
        
#         # collect the masses in a dict
#         massesStockSol = {'EMC': mEMC, 'EC': mEC, salt: mSalt}

#         # calculate the mass fractions and amount of substance for each chemical in the stock soltuions and the respective errors
#         wEMC, d_wEMC = get_mass_fraction('EMC', massesStockSol, errors_stockSol.loc[list(massesStockSol.keys()),:])
#         nEMC, d_nEMC = get_amount_of_substance('EMC', molarMasses, massesStockSol, errors_stockSol.loc[list(massesStockSol.keys()),:])
#         wEC, d_wEC = get_mass_fraction('EC', massesStockSol, errors_stockSol.loc[list(massesStockSol.keys()),:])
#         nEC, d_nEC = get_amount_of_substance('EC', molarMasses, massesStockSol, errors_stockSol.loc[list(massesStockSol.keys()),:])
#         # the values for LiPF6 are zero, because only the stock solution derived from the commercial solution contains LiPF6
#         nLiPF6, d_nLiPF6 = 0.0, 0.0
#         wTotalLiPF6, d_wTotalLiPF6 = 0.0, 0.0

#         wSalt, d_wSalt = get_mass_fraction(salt, massesStockSol, errors_stockSol.loc[list(massesStockSol.keys()),:])
#         # for the salt "none", no molar mass is found, this is caught by try and except
#         try:
#             nSalt, d_nSalt = get_amount_of_substance(salt, molarMasses, massesStockSol, errors_stockSol.loc[list(massesStockSol.keys()),:])
#         except KeyError:
#             nSalt, d_nSalt = 0.0, 0.0

#     # calculate amounts of substances for LiPF6 solution with commercial 1M solution, meaning salt == "LiPF6"
#     elif salt == "LiPF6":
#         # copy the dataframe of the errors
#         errors_LiPF6 = errors_stockSol.copy()
#         # calculate the masses of chemicals in 1 L of the commercial solution
#         mEMC = (rho_1MLiPF6*1000. - molarMasses["LiPF6"] * 1.)*0.7
#         mEC = (3./7.) * mEMC
#         mLiPF6 = molarMasses["LiPF6"] * 1.

#         # collect the masses in a dict
#         massesLiPF6 = {'EMC': mEMC, 'EC': mEC, 'LiPF6': mLiPF6}

#         # get the errors for all the masses and generate an error dataframe
#         d_mEMC = np.abs(700.) * errors_stockSol.loc['1M_LiPF6', 'density'] + np.abs(0.7) * errors_stockSol.loc['LiPF6', 'molarMass']
#         d_mEC = np.abs((3./7.)) * d_mEMC
#         d_mLiPF6 = 1. * errors_stockSol.loc['LiPF6', 'molarMass']

#         # save the errors to the new dataframe
#         errors_LiPF6.loc['EMC', 'mass'] = d_mEMC
#         errors_LiPF6.loc['EC', 'mass'] = d_mEC
#         errors_LiPF6.loc['LiPF6', 'mass'] = d_mLiPF6

#         # calculate mass fractions and their errors
#         wEMC, d_wEMC = get_mass_fraction('EMC', massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         wEC, d_wEC = get_mass_fraction('EC', massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         wLiPF6, d_wLiPF6 = get_mass_fraction('LiPF6', massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])

#         # calculate masses for actual amount of commercial solution
#         mActualEMC = wEMC * massData.loc[('LiPF6', 1.5), "mass of 1 M LiPF6 / g"]
#         mActualEC = wEC * massData.loc[('LiPF6', 1.5), "mass of 1 M LiPF6 / g"]
#         mActualLiPF6 = wLiPF6 * massData.loc[('LiPF6', 1.5), "mass of 1 M LiPF6 / g"]

#         # calculate the errors for the actual masses
#         d_mActualEMC = np.abs(wEMC) * errors_LiPF6.loc['1M_LiPF6', 'mass'] + np.abs(massData.loc[('LiPF6', 1.5), "mass of 1 M LiPF6 / g"]) * d_wEMC
#         d_mActualEC = np.abs(wEC) * errors_LiPF6.loc['1M_LiPF6', 'mass'] + np.abs(massData.loc[('LiPF6', 1.5), "mass of 1 M LiPF6 / g"]) * d_wEC
#         d_mActualLiPF6 = np.abs(wLiPF6) * errors_LiPF6.loc['1M_LiPF6', 'mass'] + np.abs(massData.loc[('LiPF6', 1.5), "mass of 1 M LiPF6 / g"]) * d_wLiPF6

#         # add the additional LiPF6 added as a salt
#         mTotalLiPF6 = mActualLiPF6 + massData.loc[('LiPF6', 1.5), "mass of salt / g"]

#         # recalculate the mass error for LiPF6
#         d_mTotalLiPF6 = d_mActualLiPF6 + errors_LiPF6.loc['LiPF6', 'mass']

#         # update the error dataframe
#         errors_LiPF6.loc['EMC', 'mass'] = d_mActualEMC
#         errors_LiPF6.loc['EC', 'mass'] = d_mActualEC
#         errors_LiPF6.loc['LiPF6', 'mass'] = d_mActualLiPF6

#         # update the masses in massesLiPF6
#         massesLiPF6 = {'EMC': mActualEMC, 'EC': mActualEC, 'LiPF6': mTotalLiPF6}

#         # recalculate mass fractions for new mass of LiPF6 and new errors
#         wEMC, d_wEMC = get_mass_fraction('EMC', massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         wEC, d_wEC = get_mass_fraction('EC', massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         wTotalLiPF6, d_wTotalLiPF6 = get_mass_fraction('LiPF6', massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         # calculate the molar fractions
#         nEMC, d_nEMC = get_amount_of_substance('EMC', molarMasses, massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         nEC, d_nEC = get_amount_of_substance('EC', molarMasses, massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])
#         nLiPF6, d_nLiPF6 = get_amount_of_substance('LiPF6', molarMasses, massesLiPF6, errors_LiPF6.loc[list(massesLiPF6.keys()),:])

#         # no salt other than LiPF6 is contained
#         nSalt, d_nSalt = 0.0, 0.0
#         wSalt, d_wSalt = 0.0, 0.0    

#     # collect all the amounts of substance in a dictionary
#     amounts = {'EMC': nEMC, 'EC': nEC, salt: nSalt, 'LiPF6': nLiPF6}
#     ## update the error dataframe with the new errors for each substance
#     # mass fractions
#     errors_stockSol.loc['EMC', 'massFractions'] = d_wEMC
#     errors_stockSol.loc['EC', 'massFractions'] = d_wEC
#     errors_stockSol.loc[salt, 'massFractions'] = d_wSalt
#     errors_stockSol.loc['LiPF6', 'massFractions'] = d_wTotalLiPF6
#     # amount of substance
#     errors_stockSol.loc['EMC', 'amountOfSubstance'] = d_nEMC
#     errors_stockSol.loc['EC', 'amountOfSubstance'] = d_nEC
#     errors_stockSol.loc[salt, 'amountOfSubstance'] = d_nSalt
#     errors_stockSol.loc['LiPF6', 'amountOfSubstance'] = d_nLiPF6

#     # calculate and save the mole fraction and the corresponding error
#     massData.loc[(salt, 1.50), "x_EMC"], massData.loc[(salt, 1.50), "d_x_EMC"] = get_mole_fraction('EMC', amounts, errors_stockSol.loc[amounts.keys(),:])
#     massData.loc[(salt, 1.50), "x_EC"], massData.loc[(salt, 1.50), "d_x_EC"] = get_mole_fraction('EC', amounts, errors_stockSol.loc[amounts.keys(),:])
#     if salt != 'LiPF6':
#         massData.loc[(salt, 1.50), "x_salt"], massData.loc[(salt, 1.50), "d_x_salt"] = get_mole_fraction(salt, amounts, errors_stockSol.loc[amounts.keys(),:])
#     else:
#         massData.loc[(salt, 1.50), "x_salt"], massData.loc[(salt, 1.50), "d_x_salt"] = 0.0, 0.0
#     massData.loc[(salt, 1.50), "x_LiPF6"], massData.loc[(salt, 1.50), "d_x_LiPF6"] = get_mole_fraction('LiPF6', amounts, errors_stockSol.loc[amounts.keys(),:])

#     # save the mass fraction and the corresponding error
#     massData.loc[(salt, 1.50), "w_EMC"], massData.loc[(salt, 1.50), "d_w_EMC"] = wEMC, d_wEMC
#     massData.loc[(salt, 1.50), "w_EC"], massData.loc[(salt, 1.50), "d_w_EC"] = wEC, d_wEC
#     massData.loc[(salt, 1.50), "w_salt"], massData.loc[(salt, 1.50), "d_w_salt"] = wSalt, d_wSalt
#     massData.loc[(salt, 1.50), "w_LiPF6"], massData.loc[(salt, 1.50), "d_w_LiPF6"] = wTotalLiPF6, d_wTotalLiPF6

# # # Save the results
# # massData.to_csv(f"{folder}\\tables\\{saveFileMassData}", index=False, sep=";")

# def get_mole_fractions(salt, concentration):
#     # copy the error dataframe
#     errors_moleFractions = errors.copy()
#     # get masses of stock solutions
#     mSolSalt = massData.loc[(salt, concentration), "mass of stock solution of salt / g"]
#     mSolSolvent = massData.loc[(salt, concentration), "mass of stock solution of solvent / g"]
#     mSolLiPF6 = massData.loc[(salt, concentration), "mass of stock solution of LiPF6 / g"]

#     # get mass of chemicals
#     # salt[0:5] to get the LiTDI... salt from the ones + LiPF6
#     mEMC = massData.loc[(salt[0:5], 1.50), "w_EMC"] * mSolSalt + massData.loc[("none", 1.50), "w_EMC"] * mSolSolvent + massData.loc[("LiPF6", 1.50), "w_EMC"] * mSolLiPF6
#     d_mEMC = massData.loc[(salt[0:5], 1.50), "d_w_EMC"] * mSolSalt + massData.loc[(salt[0:5], 1.50), "w_EMC"] * errors_moleFractions.loc['EMC', 'mass'] + massData.loc[("none", 1.50), "d_w_EMC"] * mSolSolvent + massData.loc[("none", 1.50), "w_EMC"] * errors_moleFractions.loc['EMC', 'mass'] + massData.loc[("LiPF6", 1.50), "d_w_EMC"] * mSolLiPF6 + massData.loc[("LiPF6", 1.50), "w_EMC"] * errors_moleFractions.loc['EMC', 'mass']
#     mEC = massData.loc[(salt[0:5], 1.50), "w_EC"] * mSolSalt + massData.loc[("none", 1.50), "w_EC"] * mSolSolvent + massData.loc[("LiPF6", 1.50), "w_EC"] * mSolLiPF6
#     d_mEC = massData.loc[(salt[0:5], 1.50), "d_w_EC"] * mSolSalt + massData.loc[(salt[0:5], 1.50), "w_EC"] * errors_moleFractions.loc['EC', 'mass'] + massData.loc[("none", 1.50), "d_w_EC"] * mSolSolvent + massData.loc[("none", 1.50), "w_EC"] * errors_moleFractions.loc['EC', 'mass'] + massData.loc[("LiPF6", 1.50), "d_w_EC"] * mSolLiPF6 + massData.loc[("LiPF6", 1.50), "w_EC"] * errors_moleFractions.loc['EC', 'mass']
#     mSalt = massData.loc[(salt[0:5], 1.50), "w_salt"] * mSolSalt + massData.loc[("none", 1.50), "w_salt"] * mSolSolvent + massData.loc[("LiPF6", 1.50), "w_salt"] * mSolLiPF6
#     d_mSalt = massData.loc[(salt[0:5], 1.50), "d_w_salt"] * mSolSalt + massData.loc[(salt[0:5], 1.50), "w_salt"] * errors_moleFractions.loc[salt, 'mass'] + massData.loc[("none", 1.50), "d_w_salt"] * mSolSolvent + massData.loc[("none", 1.50), "w_salt"] * errors_moleFractions.loc[salt, 'mass'] + massData.loc[("LiPF6", 1.50), "d_w_salt"] * mSolLiPF6 + massData.loc[("LiPF6", 1.50), "w_salt"] * errors_moleFractions.loc[salt, 'mass']
#     mLiPF6 = massData.loc[(salt[0:5], 1.50), "w_LiPF6"] * mSolSalt + massData.loc[("none", 1.50), "w_LiPF6"] * mSolSolvent + massData.loc[("LiPF6", 1.50), "w_LiPF6"] * mSolLiPF6
#     d_mLiPF6 = massData.loc[(salt[0:5], 1.50), "d_w_LiPF6"] * mSolSalt + massData.loc[(salt[0:5], 1.50), "w_LiPF6"] * errors_moleFractions.loc['LiPF6', 'mass'] + massData.loc[("none", 1.50), "d_w_LiPF6"] * mSolSolvent + massData.loc[("none", 1.50), "w_LiPF6"] * errors_moleFractions.loc['LiPF6', 'mass'] + massData.loc[("LiPF6", 1.50), "d_w_LiPF6"] * mSolLiPF6 + massData.loc[("LiPF6", 1.50), "w_LiPF6"] * errors_moleFractions.loc['LiPF6', 'mass']

#     # save the masses of the chemicals in a dictionary
#     masses = {'EMC': mEMC, 'EC': mEC, salt[0:5]: mSalt, 'LiPF6': mLiPF6}
#     # collect the errors of the masses in a dataframe
#     errors_moleFractions.loc['EMC', 'mass'] = d_mEMC
#     errors_moleFractions.loc['EC', 'mass'] = d_mEC
#     errors_moleFractions.loc[salt, 'mass'] = d_mSalt
#     errors_moleFractions.loc['LiPF6', 'mass'] = d_mLiPF6

#     # get amount of substance
#     nEC, d_nEC = get_amount_of_substance('EC', molarMasses, masses, errors_moleFractions.loc[masses.keys(),:]) # mEC / molarMasses["EC"]
#     nEMC, d_nEMC = get_amount_of_substance('EMC', molarMasses, masses, errors_moleFractions.loc[masses.keys(),:]) # mEMC / molarMasses["EMC"]
#     nLiPF6, d_nLiPF6 = get_amount_of_substance('LiPF6', molarMasses, masses, errors_moleFractions.loc[masses.keys(),:]) # mLiPF6 / molarMasses["LiPF6"]
#     # lookup in molarMasses does not work for salt "none", this is caught by try and except
#     # try:
#     nSalt, d_nSalt = get_amount_of_substance(salt[0:5], molarMasses, masses, errors_moleFractions.loc[masses.keys(),:]) # mSalt / molarMasses[salt[0:5]]
#     # except KeyError:
#     #     nSalt, d_nSalt = 0.0, 0.0

#     # save amountsOfSubstance
#     amountOfSubstance = {'EMC': nEMC, 'EC': nEC, salt[0:5]: nSalt, 'LiPF6': nLiPF6}
#     # update the errors of the amount of substance
#     errors_moleFractions.loc['EMC', 'amountOfSubstance'] = d_nEMC
#     errors_moleFractions.loc['EC', 'amountOfSubstance'] = d_nEC
#     errors_moleFractions.loc[salt[0:5], 'amountOfSubstance'] = d_nSalt
#     errors_moleFractions.loc['LiPF6', 'amountOfSubstance'] = d_nLiPF6

#     # get mole fractions
#     xEC, d_xEC = get_mole_fraction('EC', amountOfSubstance, errors_moleFractions.loc[masses.keys(),:]) # nEC / (nEC + nEMC + nSalt + nLiPF6)
#     xEMC, d_xEMC = get_mole_fraction('EMC', amountOfSubstance, errors_moleFractions.loc[masses.keys(),:]) # nEMC / (nEC + nEMC + nSalt + nLiPF6)
#     xLiPF6, d_xLiPF6 = get_mole_fraction('LiPF6', amountOfSubstance, errors_moleFractions.loc[masses.keys(),:]) # nLiPF6 / (nEC + nEMC + nSalt + nLiPF6)

#     if salt != 'LiPF6':
#         xSalt, d_xSalt = get_mole_fraction(salt[0:5], amountOfSubstance, errors_moleFractions.loc[masses.keys(),:]) # nSalt / (nEC + nEMC + nSalt + nLiPF6)
#     else:
#         xSalt, d_xSalt = 0.0, 0.0

#     return {"EC": xEC, "error_EC": d_xEC, "EMC": xEMC, "error_EMC": d_xEMC, "salt": xSalt, "error_salt": d_xSalt, "LiPF6": xLiPF6, "error_LiPF6": d_xLiPF6}

# # calculate the mole fractions for all solutions
# # iterate i over all salts
# for i in massData["salt"].unique():
#     # j iterates over all concentrations available for the respective salt
#     for j in massData.loc[massData["salt"] == i, "concentration"]:
#         # exclude the salt "none" and the concentration 1.5, because these are the stock solutions, for which the values are already calculated above
#         if i != "none" and j != 1.5:
#             fractions = get_mole_fractions(i, j)
#             massData.loc[(i,j), "x_EC"], massData.loc[(i,j), "d_x_EC"] = fractions["EC"], fractions["error_EC"]
#             massData.loc[(i,j), "x_EMC"], massData.loc[(i,j), "d_x_EMC"] = fractions["EMC"], fractions["error_EMC"]
#             massData.loc[(i,j), "x_salt"], massData.loc[(i,j), "d_x_salt"] = fractions["salt"], fractions["error_salt"]
#             massData.loc[(i,j), "x_LiPF6"], massData.loc[(i,j), "d_x_LiPF6"] = fractions["LiPF6"], fractions["error_LiPF6"]

# # Save the results
# massData.to_csv(f"{folder}\\tables\\{saveFileMassData}", index=False, sep=";")

# ## Save the mole fractions and their errors to the total results file
# with open(inputFileResults, "r") as file_res:
#     results = pd.read_csv(file_res, sep=";")
# ## Assign a multiindex to the results
# results = results.set_index(["salt", "concentration"])

# ## Set the index of massData to salt and concentration
# massData = massData.set_index(["salt", "concentration"])

# # iterate through all combinations of salts and concentrations in massData
# for salt, concentration in massData.index:
#     print(salt, concentration)
#     # Put the compositions and the errors to the results
#     results.loc[(salt,float(concentration)), "x_salt"] = massData.loc[(salt, float(concentration)), "x_salt"]
#     results.loc[(salt,float(concentration)), "d_x_salt"] = massData.loc[(salt, float(concentration)), "d_x_salt"]

#     results.loc[(salt,float(concentration)), "x_LiPF6"] = massData.loc[(salt, float(concentration)), "x_LiPF6"]
#     results.loc[(salt,float(concentration)), "d_x_LiPF6"] = massData.loc[(salt, float(concentration)), "d_x_LiPF6"]

#     results.loc[(salt,float(concentration)), "x_EC"] = massData.loc[(salt, float(concentration)), "x_EC"]
#     results.loc[(salt,float(concentration)), "d_x_EC"] = massData.loc[(salt, float(concentration)), "d_x_EC"]

#     results.loc[(salt,float(concentration)), "x_EMC"] = massData.loc[(salt, float(concentration)), "x_EMC"]
#     results.loc[(salt,float(concentration)), "d_x_EMC"] = massData.loc[(salt, float(concentration)), "d_x_EMC"]

#     results.loc[(salt,float(concentration)), "m_EC/m_EMC"] = (massData.loc[(salt, float(concentration)), "x_EC"]*molarMasses["EC"])/(massData.loc[(salt, float(concentration)), "x_EMC"]*molarMasses["EMC"])
#     results.loc[(salt,float(concentration)), "d_m_EC/m_EMC"] = np.abs((molarMasses["EC"])/(massData.loc[(salt, float(concentration)), "x_EMC"]*molarMasses["EMC"])) * massData.loc[(salt, float(concentration)), "d_x_EC"] + \
#                                                                 np.abs((massData.loc[(salt, float(concentration)), "x_EC"])/(massData.loc[(salt, float(concentration)), "x_EMC"]*molarMasses["EMC"])) * errors.loc['EC', 'density'] + \
#                                                                 np.abs(-(massData.loc[(salt, float(concentration)), "x_EC"] * molarMasses["EC"])/(((massData.loc[(salt, float(concentration)), "x_EMC"])**2.)*molarMasses["EMC"])) * massData.loc[(salt, float(concentration)), "d_x_EMC"] + \
#                                                                 np.abs(-(massData.loc[(salt, float(concentration)), "x_EC"] * molarMasses["EC"])/(massData.loc[(salt, float(concentration)), "x_EMC"]*((molarMasses["EMC"])**2.))) * errors.loc['EMC', 'density']   # https://stackoverflow.com/questions/53162/how-can-i-do-a-line-break-line-continuation-in-python

#     if "+LiPF6" in salt:
#         results.loc[(salt,float(concentration)), "n_salt/n_LiPF6"] = massData.loc[(salt, float(concentration)), "x_salt"]/massData.loc[(salt, float(concentration)), "x_LiPF6"]
#         results.loc[(salt,float(concentration)), "d_n_salt/n_LiPF6"] = np.abs(1./massData.loc[(salt, float(concentration)), "x_LiPF6"]) * massData.loc[(salt, float(concentration)), "d_x_salt"] + \
#                                                                         np.abs(-massData.loc[(salt, float(concentration)), "x_salt"]/((massData.loc[(salt, float(concentration)), "x_LiPF6"])**2.)) * massData.loc[(salt, float(concentration)), "d_x_LiPF6"]

# # Save the results
# results.to_csv('\\'.join(inputFileResults.split('\\')[0:-1] + [outputFileNameResults]), index=True, sep=";")  # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

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


def getVolFracs(mixingRatio:dict, config:dict=conf['solutionHandler']):
    ''' This function calculates the volume fractions for each solution in the reservoirs to obtain the correct mixing ratio requested or at least a mixture as similar as
    possible. The composition of the mixture is entered as a dict of mole fractions.
    input:
    mixingRatio: dict of mole fractions for each chemical
    config: dict containing the information regarding the available stock solutions
    '''
    ## Get the stock solutions
    stockSolutions = getStockSolutions(solutionconfig=config)
  
    for stocksol in stockSolutions.keys():
        sol = stockSolutions[stocksol]
        sol.concentrations['LiPF6'] = sol.mix['LiPF6']['value']
        ## Get the mass of 1L of the solution
        m_1L = sol.density
        ## Get the mass of the solvent by subtracting the mass of the concentration of the salt (the amount of salt in 1 L of the solution)
        m_solv = m_1L - sol.mix['LiPF6']['value'] * sol.chemicals['LiPF6'].molarMass
        ## Get the masses and the concentrations of the solvent components based on the solvent mass ratio
        m_solvComp = {}
        for c in sol.mix.keys():
            if c != 'LiPF6':
                m_solvComp[c] = sol.mix[c]['value'] * m_solv
                sol.concentrations[c] = m_solvComp[c] / sol.chemicals[c].molarMass
    
    ## Assemble the linear system of equations
    ## Get the matrix of stock solutions containing the concentrations of the components in one of the stock solutions as a column
    # get the longest list of concentrations among the stock solutions
    # concentrationArray = np.