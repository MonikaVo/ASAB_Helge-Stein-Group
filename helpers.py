''' General implementation of functions, which are needed by different components of the software. '''
import pickle
import numpy as np
import json
import sys
import os


def SaveToFile(saveFile, data, path=r"filesForOperation"):
    ''' This function saves an object passed as data to a pickle file in the path given in saveFile. '''
    with open(str(path+"/"+saveFile), 'wb') as out_file:
        pickle.dump(data, out_file) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

def LoadFile(loadFile):
    ''' This function loads an object from a pickle file from the path stated as loadFile. '''
    with open(loadFile, 'rb') as load_file:
        out = pickle.load(load_file)
    return out

def ListToDict(list):
    ''' This funtion transfers a list of values to a dict with indices as keys starting from 0 until len(list). '''
    keys = np.arange(0, len(list), 1)   # https://thispointer.com/numpy-arange-create-a-numpy-array-of-evenly-spaced-numbers-in-python/
    values = list
    dictionary = dict(zip(keys, values))    # https://www.geeksforgeeks.org/python-convert-a-list-to-dictionary/
    return dictionary

def LoadConfig(configFile=r"config.json"):
    ''' This function loads a .json format configuration file, appends the sys.paths, changes the current working directory to
    ASAB and returns an object containing the information of the configuration file. '''
    # Load the configuration file.
    with open(configFile, "r") as conf:
        info = conf.read()
    config = json.loads(info)   # https://pythonbasics.org/read-json-file/

    # Append paths from config file to path.
    sys.path.append(config["paths"]["ASAB"])
    sys.path.append(config["paths"]["QmixSDK_python"])

    # Set the current working directory to ASAB.
    os.chdir(config["paths"]["ASAB"])
    
    return config