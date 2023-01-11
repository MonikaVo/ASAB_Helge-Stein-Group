from ASAB.utility.helpers import importConfig
from pathlib import Path

conf = importConfig(str(Path(__file__).stem))

import logging  # https://docs.python.org/3/howto/logging.html
from datetime import datetime

def prepareMainLogger(logFolder:str=conf["runFolder"], run_time:datetime=datetime.now()) -> logging.Logger:
    """ This function creates a logger.
    Inputs:
    logFolder: a string defining the folder, where the log fila shall be saved.
    runID: an addition to the filename to identify the current run.
    
    Outputs:
    runLogger: a logger object with the necessary settings to act as a basis for
               other loggers deduced from it.
    """

    # Transform the runID to an string, which can be used in a filename, if it is a datetime object
    run_time = run_time.strftime("%Y%m%d_%H%M%S")
    Path(f"{logFolder}").joinpath("logs").mkdir(parents=True, exist_ok=True)
    # Configure the logging on experiment level
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s -%(name)s \n \t %(message)s \n",
        filename=str(Path(f"{logFolder}").joinpath("logs", f"{run_time}_logFile.log")),
        encoding="utf-8",
        force=True  # https://stackoverflow.com/questions/12158048/changing-loggings-basicconfig-which-is-already-set
        )
    # Create the logger
    runLogger = logging.getLogger("run_logger")
    # Log an information about the started run
    runLogger.info(msg=f"Run {conf['run_ID']} started at {run_time}.")
    return runLogger

# def endLogging(filepath):
# """ Set the log file to read only."""
#     with open(filepath, "x"):
#         chmod(filepath, mode=S_IREAD)   # https://docs.python.org/2/library/os.html#os.chmod