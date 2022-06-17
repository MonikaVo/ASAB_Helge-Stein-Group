## THIS FILE SHOULD NOT BE RUN AS MAIN!!!
import uvicorn
from fastapi import FastAPI, Query
from typing import List

from ASAB.utility import graph, helpers
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
def mix(mixratios:str =List[tuple]):#: List[str] = Query([]), ratios: List[float] = Query([])):
    if True:#inputValidation(mix, chemicals=chemicals, ratios=ratios):
        print(mixratios)
        mixRatio = eval(mixratios)# = dict(zip(chemicals, ratios))
        print('mixratioDict', mixRatio)
        assignment = conf["CetoniDevice"]["assignment"]
        mixrat, actualMix = CetoniDevice_action.mix(mixRatio=mixRatio, assignment=assignment, pumps=Ps, valves=Vs, via=['V8.0'])
        return mixrat, actualMix

@app.get("/action/CetoniDevice_action/provideSample")
def provideSample(measurementtype:str, sample_node:str):
    if True:# inputValidation(provideSample, measurementtype=measurementtype, sample_node=sample_node):
        CetoniDevice_action.provideSample(measurementtype=measurementtype, sample_node=sample_node, pumps=Ps, valves=Vs)

@app.get("/action/CetoniDevice_action/drainSample")
def drainSample(measurementtype:str, pump:str, repeats:int):
    if True:# TODO: add working input validation here.
        CetoniDevice_action.drainSample(measurementtype=measurementtype, pump=pump, repeats=repeats, pumps=Ps, valves=Vs)

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

# TODO:
# - get emergency button (stop all pumps IMMEDIATELY)
# - check, if the requested chemicals are available -> done
# - check, if the requested flow of each compound can be supplied for a reasonable amount of time with the syringes equipped
# - check, if the required flows are above the minimum flow and below the maximum flow of the respective syringes
# - check, if the requested device is available -> done

# TODO: Fix type checks
def inputValidation(function, **kwargs):
    if function.__name__ == "mix":
        try:
            assert type(kwargs["chemicals"]) == list, "The type of chemicals is not correct." #done     # https://www.w3schools.com/python/ref_keyword_assert.asp
            assert all(type(chemical)==str for chemical in kwargs["chemicals"]), "The type of elements in chemicals is not correct." #done
            assert all([c in conf["CetoniDevice"]["stockSolutionsReservoirs"].keys() for c in kwargs["chemicals"]]), "One or more of the requested chemicals are not available in the setup." #done
            assert type(kwargs["ratios"]) == list, "The type of ratios is not correct." #done
            assert all(type(rat)==float for rat in kwargs["ratios"]), "The type of elements in ratios is not correct." #done
        except AssertionError:
            return False
    elif function.__name__ == "provideSample":
        try:
            assert type(kwargs["measurementtype"]) == str, "The type of measurementtype is not correct." #done
            assert type(kwargs["sample_node"]) == str, "The type of sample_node is not correct." #done
            meastype = kwargs["measurementtype"]
            assert f"{meastype}IN" in list(helpers.loadFile(conf["CetoniDeviceDriver"]["setup"]).nodes) and f"{meastype}OUT" in list(helpers.loadFile(conf["CetoniDeviceDriver"]["setup"]).nodes), "It seems that the requested device is not connected to the system." #done
        except AssertionError:
            return False
    return True