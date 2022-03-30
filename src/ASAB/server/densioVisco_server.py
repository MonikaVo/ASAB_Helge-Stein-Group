## THIS FILE SHOULD NOT BE RUN AS MAIN!!!
import uvicorn
from fastapi import FastAPI

import initASAB_SWenv

try:
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    from experiments.Hackathon import config_Hackathon
    conf = config_Hackathon.config

from action import densioVisco_action

app = FastAPI(title="densioVisco server V1.0",
            description="This server offers interfaces to use the functionalities of the density meter and viscosimeter.",
            version="V1.0")

@app.get("/action/densioVisco_action/measure")
def measure(sampleName:str, method:str):
    #print("measure")
    densioVisco_action.measure(sampleName=sampleName, method=method)


@app.get("/action/densioVisco_action/retrieveData")
def retrieveData(sampleName:str, method:str, methodtype:str, savePath:str):
    #result = {'sampleName': sampleName, 'density': {'status': ['valid', 'valid', 'valid'], 'values': ['1.25', '1.25', '1.25']}, 'viscosity': {'status': ['FW/BW dev. too high', 'FW/BW dev. too high', 'FW/BW dev. too high'], 'values': ['1.25', '1.25', '1.25']}}
    result = densioVisco_action.retrieveData(sampleName=sampleName, method=method, methodtype=methodtype, savePath=savePath)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="<host IP>", port="<port>") # edited prior to publication

# TODO:
# - check, if the requested method is available
# - check the data types for all of the inputs