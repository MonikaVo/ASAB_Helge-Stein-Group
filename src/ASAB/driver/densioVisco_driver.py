## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    # if the import was not successful, go to default config
    from ASAB.configuration import default_config
    conf = default_config.config

## Imports from ASAB
from ASAB.utility.helpers import typeCheck

## Other imports
import numpy as np
import pandas as pd
import time

def measure(sampleName:str, method:str="Density"):
    ''' This function performs a measurement in the defined method on the density meter and viscosimeter. '''
    # TODO: Test this function!!!
    ## Check the input types
    inputTypes = {'sampleName': str, 'method': str}
    inputObjects = dict(**locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    typeCheck(inputObjects=inputObjects, inputTypes=inputTypes)

    # Get the folder, where to place the .lims file
    inputFolder = conf["densioVisco"]["measure"]["inputFolder"]
    # Generate a .lims file according to protocol V100 in order to trigger a measurement
    with open(f"{inputFolder}\\{sampleName}.lims", "w") as defFile:
        defFile.write(f"#V100\n1;{sampleName};;;;{method}")    # https://stackoverflow.com/questions/29223246/how-do-i-save-data-in-a-text-file-python

def check(sampleName:str, checktype:str, method:str="Density"):
    ''' This function provides a functionality for automatically running nitrogen and hexane checks. '''
    # TODO: Test this function!!!
    ## Check the input types
    inputTypes = {'sampleName': str, 'checktype': str, 'method': str}
    inputObjects = dict(**locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    typeCheck(inputObjects=inputObjects, inputTypes=inputTypes)

    # Get the folder, where to place the .lims file
    inputFolder = conf["densioVisco"]["measure"]["inputFolder"]
    # Generate a .lims file according to protocol V200 in order to trigger a check
    with open(f"{inputFolder}\\{checktype}.lims", "w") as defFile:
        defFile.write(f"#V200\n1;{sampleName};;;;{method};Type;C (Check);Check Type;{checktype}")    # https://stackoverflow.com/questions/29223246/how-do-i-save-data-in-a-text-file-python

def retrieveData(sampleName:str, method:str, methodtype:str, savePath:str):
    ''' This funciton retrieves data from density and viscosity measurements and saves them in a dict data format to a .json file in the specified folder (savePath). '''
    # TODO: Adjust for retrieval of checks. They have other fields.
    ## Check the input types
    inputTypes = {'sampleName': str, 'method': str, 'methodtype': str, 'savePath': str}
    inputObjects = dict(**locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary
    typeCheck(inputObjects=inputObjects, inputTypes=inputTypes)

    data = 0
    while type(data)==int:
        try:
            data = pd.read_csv(f"Y:\\output\\{sampleName}_{method}_{methodtype}.csv", sep=";")
        except FileNotFoundError:
            time.sleep(1)
    extractedData = {"sampleName": sampleName,
                    "density":
                        {"status": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Density Condition"].values[1:]),
                        "quality": np.NaN,
                        "values": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Density"].values[1:])},
                    "viscosity":
                        {"status": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Lovis Condition"].values[1:]),
                        "quality": np.NaN,
                        "values": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Lovis Dyn. Viscosity"].values[1:])}}
    for key, value in extractedData.items():
        if key != "sampleName":
            try:
                # Get floats for the values
                values = np.array(value["values"], dtype=np.float64)
            except ValueError:
                # If not all values can be casted to float
                values = np.full((len(value['values']),), np.NaN)
                # Iterate over all values
                for i in range(len(value["values"])):
                    # Try to convert each value to float
                    try:
                        values[i] = float(value["values"][i])
                    # if the conversion fails
                    except ValueError:
                        # check, if the value is ---
                        if value["values"][i].encode('ascii', 'ignore') == b'': # https://www.w3schools.com/python/ref_string_encode.asp
                            # if so, replace it by NaN
                            values[i] = np.NaN
            # try:
            # Mark the values according to their validity
            markedValues = np.ma.masked_array(values, mask=[stat != "valid" for stat in value["status"]])
            # Replace the invalid values by np.NaN
            markedValues[markedValues.mask] = np.NaN
            # Assign processed values to the extractedData
            extractedData2 = extractedData.copy()
            extractedData2[key]["values"] = list(markedValues.data)
            # Add the quality to the extractedData
            extractedData2[key]["quality"] = 10. - ((np.sum(markedValues.mask)/float(len(value["values"]))) * 10.)
            print('reductionQuality:', (np.sum(markedValues.mask)/float(len(value["values"]))) * 10.)
            print('sumMask:', np.sum(markedValues.mask), 'mask:', markedValues.mask, [stat != "valid" for stat in value["status"]])
    with open(f"{savePath}\\{sampleName}_raw.json", "w") as file:
        file.write(str(extractedData))   # https://stackoverflow.com/questions/29223246/how-do-i-save-data-in-a-text-file-python
    with open(f"{savePath}\\{sampleName}_result.json", "w") as file:
        file.write(str(extractedData2))
    return extractedData2