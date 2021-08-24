## THIS FILE SHOULD NOT BE RUN AS MAIN!!!
import uvicorn
from fastapi import FastAPI, Query, Body
from typing import List, Dict
import initASAB_SWenv

from utility import graph
from driver import CetoniDevice_driver
from action import CetoniDevice_action

try:
    from __main__ import conf, Ps, Vs, Cs   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError:
    from experiments.Hackathon import config_Hackathon
    conf = config_Hackathon.config

app = FastAPI(title="CetoniDevice server V1.0",
            description="This server offers interfaces to use the CetoniDevice functionalities.",
            version="V1.0")

@app.get("/action/CetoniDevice_action/mix")
def mix(compounds: List[str] = Query([]), ratios: List[float] = Query([])):
    print("mix")
    # mixrat = dict(zip(compounds, ratios))
    # assignment = conf["CetoniDevice"]["assignment"]
    # compoundsReservoirs = conf["CetoniDevice"]["compoundsReservoirs"]
    # mixRatio = dict([(compoundsReservoirs[compound], mixrat[compound]) for compound in mixrat.keys()])
    # print(mixRatio)
    # CetoniDevice_action.mix(mixRatio=mixRatio, assignment=assignment, pumps=Ps, valves=Vs)

@app.get("/action/CetoniDevice_action/provideSample")
def provideSample(measurementtype:str, sample_node:str):
    print("provide")
    #CetoniDevice_action.provideSample(measurementtype=measurementtype, sample_node=sample_node, pumps=Ps, valves=Vs)

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
    uvicorn.run(app, host="<host IP>", port=<port>) # edited prior to publication