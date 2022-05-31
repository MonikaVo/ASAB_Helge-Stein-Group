## THIS FILE SHOULD NOT BE RUN AS MAIN!!!
import uvicorn
from fastapi import FastAPI, Query, Body
from typing import List, Dict

from ASAB.utility import graph
from ASAB.driver import CetoniDevice_driver
from ASAB.action import CetoniDevice_action

try:
    from __main__ import conf, Ps, Vs, Cs   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    from config_Hackathon import config as conf

app = FastAPI(title="CetoniDevice server V1.0",
            description="This server offers interfaces to use the CetoniDevice functionalities.",
            version="V1.0")

@app.get("/action/CetoniDevice_action/mix")
def mix(compounds: List[str] = Query([]), ratios: List[float] = Query([])):
    print("mix")

@app.get("/action/CetoniDevice_action/provideSample")
def provideSample(measurementtype:str, sample_node:str):
    print("provide")

@app.on_event("shutdown")
def quitCetoni():
    CetoniDevice_driver.pumpObj.stop_all_pumps()
    CetoniDevice_driver.cetoni.quitCetoni()

if __name__ == "__main__":
    ## Generate the graph and its valvePositionDict
    graph.generateGraph()
    ## Prepare the Cetoni device
    Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()
    ## Define the assignment
    assignment = conf["CetoniDevice"]["assignment"]
    ## Flush the syringes
    for p in assignment.keys():
        CetoniDevice_action.flushSyringe(pumps=Ps, valves=Vs, pump=p, reservoir=assignment[p])
    uvicorn.run(app, host="<host IP>", port="<port>") # edited prior to publication