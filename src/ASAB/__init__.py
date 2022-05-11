import sys
from ASAB.configuration.config import configASAB
cf = configASAB

# Append paths from config to path, if they are not yet included.
if configASAB["ASAB"] not in sys.path:
    sys.path.append(configASAB["ASAB"])
if configASAB["QmixSDK_python"] not in sys.path:
    sys.path.append(configASAB["QmixSDK_python"])
if configASAB["QmixSDK"] not in sys.path:
    sys.path.append(configASAB["QmixSDK"])

# # Set the current working directory to ASAB.
# os.chdir(configASAB["ASAB"])