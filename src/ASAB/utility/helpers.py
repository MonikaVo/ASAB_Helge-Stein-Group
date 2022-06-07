''' General implementation of functions, which are needed by different components of the software. '''

def saveToFile(savePath:str, data:str):
    ''' This function saves an object passed as data to a pickle file in the path given in savePath. The file must be .txt. '''
    with open(savePath, 'w', encoding='utf-8') as out_file:
       out_file.write(str(data)) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

def loadTxtFile(loadPath:str):
    ''' This function loads a .txt file and returns the evaluation of the content. '''
    # Open and read the file containing the data
    with open(loadPath, "r", encoding='utf-8') as file:
        rawString = file.read()
    # Evaluate the rawString
    dataEval = eval(rawString)
    return dataEval

# TODO:Test this function
def typeCheck(inputObjects:dict, inputTypes:dict):
    ''' This function checks the type for several input parameters passed as a dict. It passes, if the types match and raises a ValueError, if one of the types is incorrect. '''
    for inputParam in inputTypes.keys():
        if (not isinstance(inputObjects[inputParam], inputTypes[inputParam])):
            raise ValueError(f'Incorrect type of {inputParam} {type(inputParam)} instead of {inputTypes[inputParam]}.')    # https://stackoverflow.com/questions/20844347/how-would-i-make-a-custom-error-message-in-python
