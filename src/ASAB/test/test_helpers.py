from ASAB.test.FilesForTests import config_test
conf = config_test.config

from ASAB.configuration import config
cf = config.configASAB

# Imports from ASAB
import ASAB.utility.helpers

# Other imports
from pathlib import Path
from glob import glob
from os import remove
from typing import Union, get_type_hints
from inspect import getfullargspec
from pytest import raises

def test_saveToFile():
    # delete the textfile with the expected name from the target directory to avoid the tests finding this file and checking this instead of the newly created one
    for f in glob(str(Path(conf['test_helpers']['savePath']).joinpath(f"{conf['test_helpers']['filename']}.txt"))):
        remove(f)

    # generate the test dictionary to save
    testDict_save = {"this": 1, "is": "two", "1": "a", "test": {"of": 5, "the": "save"}}
    # call the function to generate the file
    ASAB.utility.helpers.saveToFile(folder=conf['test_helpers']['savePath'], filename=conf['test_helpers']['filename'], extension=conf['test_helpers']['extension'], data=str(testDict_save))
    
    # check, if the file is generated
    assert Path(conf['test_helpers']['savePath']).joinpath(f"{conf['test_helpers']['filename']}.txt").is_file(), f'The file does not exist in the expected directory.'

    # open the generated file and load its contents
    with open (Path(conf['test_helpers']['savePath']).joinpath(f"{conf['test_helpers']['filename']}.txt"), "r") as file:
        loaded_save = file.readlines()[0]
    dict_loaded = eval(loaded_save)
    # check the evaluated content of the saved file
    assert testDict_save == dict_loaded, f"The saved and loaded dictionary is {dict_loaded} instead of {testDict_save}."

def test_loadVariable():
    # define the test variable
    v = {'this': 1, 'is': 'my', 3: 'test', 'for': {'variable': 'which', 1: 'is', 5: 'great'}}

    # save the variable to a python file
    ASAB.utility.helpers.saveToFile(folder=f"{conf['test_helpers']['savePath']}", filename=f"{conf['test_helpers']['variableFile']}", extension= conf['test_helpers']['variableExtension'], data=f"myVar = {v}")

    # load the variable
    v_loaded = ASAB.utility.helpers.loadVariable(loadPath=str(Path(conf['test_helpers']['savePath']).joinpath(f"{conf['test_helpers']['variableFile']}.{conf['test_helpers']['variableExtension']}")), variable='myVar')
    print(v_loaded)
    assert v_loaded == v, f"The loaded variable is {v_loaded} instead of {v}."

def test_loadTxtFile():
    # Use helper function to load and evaluate
    withHelper = ASAB.utility.helpers.loadTxtFile(loadPath=str(Path(conf['test_helpers']['savePath']).joinpath(f"{conf['test_helpers']['filename']}.txt")))

    # Read and evaluate for reference
    with open (Path(conf['test_helpers']['savePath']).joinpath(f"{conf['test_helpers']['filename']}.txt"), "r") as file:
        loaded_save = file.readlines()[0]
    read = eval(loaded_save)
    assert read == withHelper, f"The content of the file loaded using the helper function is {withHelper} instead of {read}."

def test_typeCheck():
    # define the functions to check
    def function_a_correctType(x:Union[int,str], y:float) -> float:
        loc = locals()
        # get the input objects and types as they result from the locals() and the get_type_hints() methods
        arguments = getfullargspec(function_a_correctType).args
        inputObjects_a_result = dict([(arguments[i],loc[arguments[i]]) for i in range(len(arguments))])
        inputTypes_a_result = get_type_hints(function_a_correctType)

        # assemble the targets for input objects and types
        inputObjects_a_target = {'x':x, 'y':y}
        inputTypes_a_target = {'x':Union[int,str], 'y':float, 'return':float}

        # ensure, that the obtained inputObjects and inputTypes are identical with the targets
        assert inputObjects_a_result==inputObjects_a_target, f'The resulting inputObjects is {inputObjects_a_result} instead of {inputObjects_a_target}.'
        assert inputTypes_a_result==inputTypes_a_target, f'The resulting inputTypes is {inputTypes_a_result} instead of {inputTypes_a_target}.'

        # apply the function
        check = ASAB.utility.helpers.typeCheck(func=function_a_correctType, locals=locals())

        # check, that the function returns True
        assert check, f'The result is {check} instead of True.'

        return float(x)+y
    
    function_a_correctType(x=3, y=7.345)

    def function_b_correctType(x:Union[dict,list], y:str) -> str:
        loc = locals()
        # get the input objects and types as they result from the locals() and the get_type_hints() methods
        arguments = getfullargspec(function_b_correctType).args
        inputObjects_a_result = dict([(arguments[i],loc[arguments[i]]) for i in range(len(arguments))])
        inputTypes_a_result = get_type_hints(function_b_correctType)

        # assemble the targets for input objects and types
        inputObjects_a_target = {'x':x, 'y':y}
        inputTypes_a_target = {'x':Union[dict,list], 'y':str, 'return':str}

        # ensure, that the obtained inputObjects and inputTypes are identical with the targets
        assert inputObjects_a_result==inputObjects_a_target, f'The resulting inputObjects is {inputObjects_a_result} instead of {inputObjects_a_target}.'
        assert inputTypes_a_result==inputTypes_a_target, f'The resulting inputTypes is {inputTypes_a_result} instead of {inputTypes_a_target}.'

        # apply the function
        check = ASAB.utility.helpers.typeCheck(func=function_b_correctType, locals=locals())

        # check, that the function returns True
        assert check, f'The result is {check} instead of True.'

        return str(x)+y

    function_b_correctType(x={'a':4, 'second': 'time', 'number': 3, 'float':7.345}, y='this_is_a_string')

    def function_c_wrongType(x:float, y:int, z:str) -> str:
        loc = locals()
        # get the input objects and types as they result from the locals() and the get_type_hints() methods
        arguments = getfullargspec(function_c_wrongType).args
        inputObjects_a_result = dict([(arguments[i],loc[arguments[i]]) for i in range(len(arguments))])
        inputTypes_a_result = get_type_hints(function_c_wrongType)

        # assemble the targets for input objects and types
        inputObjects_a_target = {'x':x, 'y':y, 'z':z}
        inputTypes_a_target = {'x':float, 'y':int, 'z':str, 'return':str}

        # ensure, that the obtained inputObjects and inputTypes are identical with the targets
        assert inputObjects_a_result==inputObjects_a_target, f'The resulting inputObjects is {inputObjects_a_result} instead of {inputObjects_a_target}.'
        assert inputTypes_a_result==inputTypes_a_target, f'The resulting inputTypes is {inputTypes_a_result} instead of {inputTypes_a_target}.'

        # pytest.raises checks, that the respective error is raised
        with raises(TypeError): # https://pytest.org/en/latest/getting-started.html#assert-that-a-certain-exception-is-raised
            # apply the function
            ASAB.utility.helpers.typeCheck(func=function_c_wrongType, locals=locals())
        return str(x)+str(y)+str(z)