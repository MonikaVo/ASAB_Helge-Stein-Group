from ASAB.utility.helpers import importConfig, loadVariable, saveToFile, typeCheck
from pathlib import Path
from typing import Callable
import logging
import clr

conf = importConfig(str(Path(__file__).stem))

from ASAB.configuration import config
cf = config.configASAB

## Imports from PalmsensSDK
import sys
sys.path.append(conf["PalmsensDriver"]["PalmsensSDK_python"])
from pspython.pspyinstruments import InstrumentManager, Instrument
from pspython import pspymethods

# Add the dll file of the Palmsens SDK to import the required enums to make it work with Python >3.8
clr.AddReference(str(Path(conf["PalmsensDriver"]["PalmsensSDK_python"]).joinpath("pspython", "PalmSens.Core.dll")))
from PalmSens.Techniques.Impedance import enumScanType, enumFrequencyType
from PalmSens.Techniques import ImpedimetricMethod, LinearSweep
from PalmSens import CurrentRange, CurrentRanges

# create a logger for this module
logger_Palmsens_driver = logging.getLogger(f"run_logger.{__name__}")

def get_electrochemistry_method(method_instance, **kwargs):
    method = method_instance
    for k in kwargs.keys():
        # For nested attributes
        if "." in k:
            # Get the nesting
            key_list = k.split(".")
            current_attr = getattr(method, key_list[0])
            last_key = key_list[-1]
            # Go through the attribute's nesting and get to the second lowest level
            for i in range(1,len(key_list)-1):
                current_attr = getattr(current_attr, key_list[i])
        else:
            current_attr = method
            last_key = k
        setattr(current_attr, last_key, kwargs[k])
    return method

    
class PalmsensDevice():
    """
    This class comprises the low level functionalities
    a Palmsens 4 device.
    """
    def __init__(self, callback_func:Callable) -> None:
        """
        This function initializes an instance of the PalmsensDevice class.

        Inputs:
        self: an instance of the PalmsensDevice class
        callback_func: a callback function, which is executed after every acquisition
            of a new datapoint.

        Outputs:
        This function has no outputs.
        """

        typeCheck(self.__init__, locals=locals())
        self.callback = callback_func
        self.instrument_manager = InstrumentManager(new_data_callback=self.callback)
        self.instrument = None

    def find_instruments(self) -> list[Instrument]:
        """
        This function detects connected Palmsens devices.

        Inputs:
        self: an instance of the PalmsensDevice class

        Outputs:
        found_instruments: a list of instruments, which were detected
        """

        found_instruments = self.instrument_manager.discover_instruments()
        return found_instruments

    def connect(self, instrument:Instrument) -> None:
        """
        This function opens a connection to the given Palmsens device.

        Inputs:
        instrument: the Instrument object associated with the instrument to which the
        connection shall be established

        Outputs:
        This function has not outputs.
        """

        # Check the input types
        typeCheck(func=self.connect, locals=locals())

        print(f"Connecting to instrument {instrument.name}.")
        status = self.instrument_manager.connect(instrument)
        if status==1:
            self.instrument = instrument
            logger_Palmsens_driver.info(f"Successfully connected to {instrument.name}.")
            print(f"Successfully connected to {instrument.name}.")
        else:
            raise ValueError(f"Connection to {instrument.name} failed.")

    def disconnect(self) -> None:
        """
        This function closes a connection to the Palmsens device associated with the
        respective instance of the PalmsensDevice class.

        Inputs:
        self: an instance of the PalmsensDevice class

        Outputs:
        This function has not outputs.
        """

        # Check the input types
        typeCheck(func=self.disconnect, locals=locals())

        status = self.instrument_manager.disconnect()
        if status==1:
            logger_Palmsens_driver.info("Successfully disconnected "
                f"from {self.instrument.name}.")
            print(f"Successfully disconnected from {self.instrument.name}.")
        else:
            raise ValueError(f"Disconnecting from {self.instrument.name} failed.")

    def measure(
                self,
                sampleName:str,
                method:str,
                parameters:dict,
                save_folder:str=conf["PalmsensDriver"]["savepath_raw"]
               ) -> None:
        ''' This function performs a measurement in the defined method on the 
        Palmsens device. It saves the results to the path specified.
        Inputs:
        sampleName: a string defining the sample name to be used to label the sample
            for the measurement
        method: a string defining the method to be used as defined in the SDK of the
            device. Currently, this accepts "electrochemical_impedance_spectroscopy"
        parameters: a dictionary comrising the input parameters required to trigger the
            chosen method; the name of the parameter needs to be a string and be used as
            a key, while the parameter values are the values in the dictionary
        save_folder: The path to the folder, where the results shall be saved

        Outputs:
        This function has no outputs.
        '''

        ## Check the input types
        typeCheck(func=self.measure, locals=locals())

        # If an impedance measurement shall be made, transfer the parameters for the
        # scanType and the freqType to the relevant enums
        if method == "EIS":
            method_instance = ImpedimetricMethod()
            method_params = {}
            method_params["Ranging.MaximumCurrentRange"] = CurrentRange(CurrentRanges(parameters["maxCurrent"]))
            method_params["Ranging.MinimumCurrentRange"] = CurrentRange(CurrentRanges(parameters["minCurrent"]))
            for k in parameters.keys():
                if k == "ScanType":
                    method_params[k] = enumScanType(parameters[k])
                elif k == "FreqType":
                    method_params[k] = enumFrequencyType(parameters[k])
                else:
                    method_params[k] = parameters[k]

        # Get the requested method
        method_parameterized = get_electrochemistry_method(
            method_instance=method_instance,
            **method_params
        )

        # Trigger the measurement
        result = self.instrument_manager.measure(method_parameterized)

        # Save the results
        save_folder = Path(save_folder)
        
        if not save_folder.resolve().exists():
            save_folder.mkdir(parents=True)
        
        saveToFile(
                   folder=str(save_folder),
                   filename=f"{method}_{sampleName}",
                   extension="py",
                   data=f"result = {str(result.__dict__)}"
                   )
        logger_Palmsens_driver.info(f"result:\n{str(result.__dict__)}")
        print("Measurement finished \n"
             f"result:\n{str(result.__dict__)}")

def retrieveData(
                sampleName:str,
                method:str,
                save_folder:str=conf["PalmsensDriver"]["savepath_raw"]
                ) -> dict:
    ''' This function loads the data of a measurement and returns it as a dict. 
    Inputs:
    sampleName: a string defining the sample name to be used to label the sample
        for the measurement
    method: a string defining the method to be used as defined in the SDK of the
        device
    save_folder: The path to the folder, where the results shall be saved

    Outputs:
    loaded_result: the dictionary containing the results of a measruement
    '''

    # Check the input types
    typeCheck(func=retrieveData, locals=locals())

    # Load the results from the file
    file_path = str(Path(save_folder).joinpath(f"{method}_{sampleName}.py"))
    loaded_result = loadVariable(loadPath=file_path, variable="result")

    return loaded_result
