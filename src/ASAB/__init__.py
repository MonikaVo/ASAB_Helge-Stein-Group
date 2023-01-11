import sys
import logging
from ASAB.configuration.config import configASAB
cf = configASAB

# Create a logger
ASABlogger = logging.getLogger("run_logger.ASAB_logger")

# Append paths from config to path, if they are not yet included.
if configASAB["ASAB"] not in sys.path:
    sys.path.append(configASAB["ASAB"])
if configASAB["QmixSDK_python"] not in sys.path:
    sys.path.append(configASAB["QmixSDK_python"])
if configASAB["QmixSDK"] not in sys.path:
    sys.path.append(configASAB["QmixSDK"])

ASABlogger.info(msg=f"The following paths were added to the system path:\n"
                    f"{configASAB['ASAB']}\n"
                    f"{configASAB['QmixSDK_python']}\n"
                    f"{configASAB['QmixSDK']}")

## Stop the pumps, if the software raises an error
# import the function to stop all pumps from the qmixpump module in the QmixSDK
# (needs to be imported after adding the path to the system path)
from qmixsdk.qmixpump import Pump
from ASAB.driver.CetoniDevice_driver import cetoni


# Define a new exceptHook, which stops the pumps prior to exiting the script
def new_exceptHook(type, value, traceback): # https://stackoverflow.com/questions/6598053/python-global-exception-handling, https://docs.python.org/3/library/sys.html
    ''' This is a modified excepthook, which stops all pumps prior to exiting. '''
    ASABlogger.error("!!!!!!!!!!!!--------------An ERROR occurred--------------!!!!!!!!!!!!")
    ASABlogger.exception("The following exception caused the interruption:", exc_info=(type, value, traceback))
    Pump.stop_all_pumps()
    ASABlogger.error("All pumps are stopped.")
    cetoni.quitCetoni()
    # manualIntervention = input(f"Please enter how the error was handled manually to log this in the log of the run: ")
    # ASABlogger.info(f"Comments on the ERROR:\n{manualIntervention}")
    sys.__excepthook__(type, value, traceback)

# Assign the new_exceptHook to the excepthook of sys
sys.excepthook = new_exceptHook

ASABlogger.info(msg="The new exceptHook is set.")