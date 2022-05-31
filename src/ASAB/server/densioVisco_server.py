## THIS FILE SHOULD NOT BE RUN AS MAIN!!!
import uvicorn
from fastapi import FastAPI

try:
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    from config_Hackathon import config as conf

from ASAB.action import densioVisco_action

app = FastAPI(title="densioVisco server V1.0",
            description="This server offers interfaces to use the functionalities of the density meter and viscosimeter.",
            version="V1.0")

@app.get("/action/densioVisco_action/measure")
def measure(sampleName:str, method:str):
    densioVisco_action.measure(sampleName=sampleName, method=method)

@app.get("/action/densioVisco_action/retrieveData")
def retrieveData(sampleName:str, method:str, methodtype:str, savePath:str):
    result = densioVisco_action.retrieveData(sampleName=sampleName, method=method, methodtype=methodtype, savePath=savePath)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="<host IP>", port="<port>") # edited prior to publication

# TODO:
# - check, if the requested method is available
# - check the data types for all of the inputs