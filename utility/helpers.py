''' General implementation of functions, which are needed by different components of the software. '''
import pickle
import numpy as np
import json
import sys
import os


def saveToFile(saveFile, data):
    ''' This function saves an object passed as data to a pickle file in the path given in saveFile. '''
    with open(saveFile, 'wb') as out_file:
        pickle.dump(data, out_file) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

def loadFile(loadFile:str):
    ''' This function loads an object from a pickle file from the path stated as loadFile. '''
    with open(loadFile, 'rb') as load_file:
        out = pickle.load(load_file)
    return out

def doAppends(conf):
    ''' This function loads a .json format configuration file, appends the sys.paths, changes the current working directory to
    ASAB and returns an object containing the information of the configuration file. '''
    # Append paths from config file to path.
    sys.path.append(conf["utility"]["ASAB"])
    sys.path.append(conf["utility"]["QmixSDK_python"])
    sys.path.append(conf["utility"]["QmixSDK"])

    # Set the current working directory to ASAB.
    os.chdir(conf["utility"]["ASAB"])