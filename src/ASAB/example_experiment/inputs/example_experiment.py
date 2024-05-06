'''
This is an example of a minimalistic experiment script, which may be used as a template
for more advanced experiment scripts.
'''
from experiment_config_template import config
conf = config

import ASAB

from ASAB.driver import CetoniDevice_driver
from ASAB.action import CetoniDevice_action
from ASAB.action import densiVisco_action

from qmixsdk.qmixbus import PollingTimer

# Prepare the Cetoni device
setupData = CetoniDevice_action.prepareRun(graphSave=True, graphShow=False, refPos=True)
pumpsDict = setupData["pumps"]
valvesDict = setupData["valves"]
chemicalsDict = setupData["chemicalsDict"]
solutionsDict = setupData["solutionsDict"]

# initialise a timer
timer = PollingTimer(period_ms=900000)

# formulate
mix_rat_req, mix_rat_vol, mix_rat_calc, actual_flows_mix, pumps_flows = CetoniDevice_action.mix(
    mixingRatio={
            "<InChIKey_component": "<fraction of the component in the type of fraction given "
            "in the parameter 'fraction'>"
        },
    fraction="molPerMol",
    pumps=pumpsDict,
    valves=valvesDict
)

# provide sample e.g. to a density measurement
actual_flows_provide = CetoniDevice_action.provideSample(
    measurementtype="densiVisco",
    sample_node="<the node, from where the formulated sample is obtained>",
    pumpsFlows=pumps_flows,
    pumps=pumpsDict,
    valves=valvesDict
)

# measure
densiVisco_action.measure(
    sampleName="example_measurement",
    method="<the measurement protocol to use>"
)

# since density measurements are non-blocking in ASAB, the results need to be retrieved
densiVisco_action.retrieveData(
    sampleName="example_measurement",
    method="<the measurement protocol used>",
    methodtype="measurement",
    savePath="<path, where to save the output>"
)

# drain sample
CetoniDevice_action.drainSample(
        measurementtype="densiVisco",
        pump="<the name of the pump node, which shall be used to drain the sample>",
        repeats= "<number of repeats>",
        pumps=pumpsDict,
        valves=valvesDict
)

# clean the relevant nodes
CetoniDevice_action.clean(
    medium="<the name of the node, from where the cleaning medium may be obtained>",
    pumps=["<the name of the pump nodes, which are involved in the cleaning>"],
    pumpsDict=pumpsDict,
    valvesDict=valvesDict,
    nodes=["<the nodes. which shall be cleaned>"],
    repeats="<number of repeats>",
    goToRef=True
)

# move syringe pumps to rest position
CetoniDevice_action.goToRefPos(
    valvesDict=valvesDict,
    pumpsDict=pumpsDict,
    mode='end'
    )

# disconnect from formulation unit
CetoniDevice_driver.cetoni.quitCetoni()