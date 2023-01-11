from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

## Imports from ASAB
from ASAB.utility.helpers import typeCheck

## Other imports
import numpy as np
import pandas as pd
import time

def measure(sampleName:str, method:str="Density") -> None:
    ''' This function performs a measurement in the defined method on the densimeter and viscosimeter. It triggers the measurement by writing a 
    .lims file to the directory, which is defined in conf["densiViscoDriver"]["inputFolder"]. This folder needs to be set as the input
    directory to check by the LIMS of the densimeter and viscosimeter.
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample for the measurement
    method: a string defining the method to be used as defined on the measuring device
    
    Outputs:
    This function has no outputs. '''

    ## Check the input types
    typeCheck(func=measure, locals=locals())

    # Get the folder, where to place the .lims file
    inputFolder = conf["densiViscoDriver"]["inputFolder"]
    # Generate a .lims file according to protocol V100 in order to trigger a measurement
    with open(f"{inputFolder}\\{sampleName}.lims", "w") as defFile:
        defFile.write(f"#V100\n1;{sampleName};;;;{method}")    # https://stackoverflow.com/questions/29223246/how-do-i-save-data-in-a-text-file-python

def check(sampleName:str, checktype:str, method:str="Density") -> None:
    ''' This function performs a check in the defined method on the densimeter and viscosimeter. It triggers the check by writing a 
    .lims file to the directory, which is defined in conf["densiViscoDriver"]["inputFolder"]. This folder needs to be set as the input
    directory to check by the LIMS of the densimeter and viscosimeter.
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample for the check
    checktype: a string defining the type of check to be performed. This label needs to be defined in the device
    method: a string defining the method to be used as defined on the measuring device
    
    Outputs:
    This function has no outputs. '''

    ## Check the input types
    typeCheck(func=check, locals=locals())

    # Get the folder, where to place the .lims file
    inputFolder = conf["densiViscoDriver"]["inputFolder"]
    # Generate a .lims file according to protocol V200 in order to trigger a check
    with open(f"{inputFolder}\\{checktype}.lims", "w") as defFile:
        defFile.write(f"#V200\n1;{sampleName};;;;{method};Type;C (Check);Check Type;{checktype}")    # https://stackoverflow.com/questions/29223246/how-do-i-save-data-in-a-text-file-python

def retrieveData(sampleName:str, method:str, methodtype:str, savePath:str, outputPath:str=conf['densiViscoDriver']['outputFolder']) -> dict:
    ''' This funciton retrieves data from density and viscosity measurements and saves them in a dict data format to a .json file in the specified folder (savePath).
    It generates one file with the data as retrieved from the instrument files and one file with invalid measurements/datapoints replaced by NaN.
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample for the measurement
    method: a string defining the method to be used as defined on the measuring device
    methodtype: a string defining the type of the method. This can be a check or a measurement.
    savePath: a string giving the path to which the output files shall be saved. I does not include the file name.
    outputPath: a string giving the path, in which the output file of the measuring device is expected once the measurement is done.
    
    Outputs:
    results: a dictionary containing the status, value, quality and sample name of the individual results. Invalid results are replaced by NaN. '''
    # TODO: Adjust for retrieval of checks. They have other fields.
    ## Check the input types
    typeCheck(func=retrieveData, locals=locals()) # https://stackoverflow.com/questions/28371042/get-function-parameters-as-dictionary

    # as long as no data file is available in the output folder, sleep
    while not Path(f"{outputPath}\\{sampleName}_{method}_{methodtype}.csv").is_file():
        time.sleep(1)
    # once a file is there, read the file
    data = pd.read_csv(f"{outputPath}\\{sampleName}_{method}_{methodtype}.csv", sep=";")
    # extract the validity/status, and values for density and viscosity from the measurements and save them to a dictionary
    extractedData = {"sampleName": sampleName,
                    "density":
                        {"status": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Density Condition"].values[1:]),
                        "quality": np.NaN,
                        "values": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Density"].values[1:])},
                    "viscosity":
                        {"status": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Lovis Condition"].values[1:]),
                        "quality": np.NaN,
                        "values": list(data.loc[data["Results::Measurement Level"]!="Master", "Results::Lovis Dyn. Viscosity"].values[1:])}}
    # iterate through the key, value pairs in the extracted data
    for key, value in extractedData.items():
        # for all keys, which are not the sample name
        if key != "sampleName":
            try:
                # Get floats for the values
                values = np.array(value["values"], dtype=np.float64)
            except ValueError:
                # If not all values can be casted to float, initialize an array of NaN values with the length of the values
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
    # save the extracted data to a raw file in .json format
    with open(f"{savePath}\\{sampleName}_raw.json", "w") as file:
        file.write(str(extractedData))   # https://stackoverflow.com/questions/29223246/how-do-i-save-data-in-a-text-file-python
    # save the processed data with the NaN values and the quality measure to a results file in .json format
    with open(f"{savePath}\\{sampleName}_result.json", "w") as file:
        file.write(str(extractedData2))
    # return the processed dictionary
    return extractedData2