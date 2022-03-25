import sys
import os

config = dict()

projectFolder = "<path to project>" # edited prior to publication
auxiliaryFolderHardware = "filesForOperation\\hardware"

config["utility"] = {"ASAB": projectFolder + "...\\ASAB", # edited prior to publication
                    "QmixSDK_python": projectFolder + "...\\QmixSDK\\lib\\python", # edited prior to publication
                    "QmixSDK": projectFolder + "...\\QmixSDK"} # edited prior to publication

# Append paths from config to path, if they are not yet included.
if config["utility"]["ASAB"] not in sys.path:
    sys.path.append(config["utility"]["ASAB"])
if config["utility"]["QmixSDK_python"] not in sys.path:
    sys.path.append(config["utility"]["QmixSDK_python"])
if config["utility"]["QmixSDK"] not in sys.path:
    sys.path.append(config["utility"]["QmixSDK"])

# Set the current working directory to ASAB.
os.chdir(config["utility"]["ASAB"])