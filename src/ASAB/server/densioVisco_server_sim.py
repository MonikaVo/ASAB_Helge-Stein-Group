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
    print("measure")

@app.get("/action/densioVisco_action/retrieveData")
def retrieveData(sampleName:str, method:str, methodtype:str, savePath:str):
    result = {'sampleName': sampleName, 'density': {'status': ['valid', 'valid', 'valid'], 'values': ['1.25', '1.25', '1.25']}, 'viscosity': {'status': ['FW/BW dev. too high', 'FW/BW dev. too high', 'FW/BW dev. too high'], 'values': ['1.25', '1.25', '1.25']}}
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="<host IP>", port="<port>") # edited prior to publication