''' General implementation of functions, which are needed by different components of the software. '''

def saveToFile(savePath:str, data:str):
    ''' This function saves an object passed as data to a pickle file in the path given in savePath. The file must be .txt. '''
    with open(savePath, 'w') as out_file:
       out_file.write(str(data)) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

def loadTxtFile(loadPath:str):
    ''' This function loads a .txt file and returns the evaluation of the content. '''
    # Open and read the file containing the data
    with open(loadPath, "r", encoding="utf8") as file:
        # Assuming there is only one line in the file, the element at positions zero of the list is used
        rawString = file.readlines()[0]
    # Evaluate the rawString
    dataEval = eval(rawString)
    return dataEval
