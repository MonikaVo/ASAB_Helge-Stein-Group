''' General implementation of functions, which are needed by different components of the software. '''
import pickle

def saveToFile(saveFile, data):
    ''' This function saves an object passed as data to a pickle file in the path given in saveFile. '''
    with open(saveFile, 'wb') as out_file:
        pickle.dump(data, out_file) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

def loadFile(loadFile:str):
    ''' This function loads an object from a pickle file from the path stated as loadFile. '''
    with open(loadFile, 'rb') as load_file:
        out = pickle.load(load_file)
    return out