import uvicorn
import sys
sys.path.append("...\\ASAB\\server") # edited prior to publication
import initASAB_SWenv

from experiments.Hackathon import config_Hackathon_sim

conf = config_Hackathon_sim.config

from utility import graph
from driver import CetoniDevice_driver
from action import CetoniDevice_action, densioVisco_action

## Generate the graph and its valvePositionDict
graph.generateGraph(show=True)
## Prepare the Cetoni device
Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()
## Pumps go to reference positions
CetoniDevice_action.goToRefPos(pumpsDict=Ps, valvesDict=Vs, mode="start", gas="Reservoir5")
## Define the assignment
assignment = conf["CetoniDevice"]["assignment"]
# ## Flush the syringes
# for p in assignment.keys():
#     CetoniDevice_action.flushSyringe(pumps=Ps, valves=Vs, pump=p, reservoir=assignment[p])

# ## Hexane check
# # Flush the syringe connected to the hexane reservoir (Reservoir6)
# #CetoniDevice_action.flushSyringe(pumps=Ps, valves=Vs, pump="E0.0", reservoir="Reservoir6")
# # Fill the syringe
# CetoniDevice_action.fillSyringe(pump=Ps["E0.0"], volume=10., valvesDict=Vs, reservoir="Reservoir6")
# # Switch valves to waste
# CetoniDevice_action.switchValves(nodelist=graph.findPath(start_node="E0.0", end_node=conf["CetoniDevice"]["waste"]), valvesDict=Vs)
# # Generate a flow
# Ps["E0.0"].generate_flow(conf["CetoniDeviceDriver"]["flow"])
# # Provide hexane to the device (densioVisco)
# CetoniDevice_action.provideSample(measurementtype="densioVisco", sample_node="M1.0", pumps=Ps, valves=Vs)
# # Perform the check
# densioVisco_action.check(sampleName="20220202_hexaneCheck", checktype="hexaneCheck_20", method="Lovis-DMA_MultiMeasure_20")


from server import CetoniDevice_server_sim, densioVisco_server_sim
uvicorn.run(CetoniDevice_server_sim.app, host="<host IP>", port=<port>) # edited prior to publication

# for p in Ps.keys():
#     Ps[p].calibrate()

# CetoniDevice_action.goToRefPos(Ps, Vs, "end")
#path = graph.findPath(start_node="A0.0", end_node="Reservoir1")
#CetoniDevice_action.switchValves(path, Vs)
#Ps["A0.0"].set_fill_level(0.0, 0.1)
# Ps["E0.0"].calibrate()

# ## Cleaning

# from qmixsdk import qmixbus
# from networkx.exception import NodeNotFound, NetworkXNoPath
# import time


# for p in Ps.keys():
#     print(p)
#     try:
#         timer = qmixbus.PollingTimer(300000)
#         pathRP = graph.findPath(start_node=assignment[p], end_node=p)
#         pathPW = graph.findPath(start_node=p, end_node="densioViscoIN") + graph.findPath(start_node="densioViscoOUT", end_node=conf["CetoniDevice"]["waste"])
#         # pathPW2 = graph.findPath(start_node=p, end_node=conf["CetoniDevice"]["waste"])
#         # CetoniDevice_action.switchValves(nodelist=pathPW2, valvesDict=Vs)
#         # Ps[p].set_fill_level(0.0, 0.1)
#         # timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
#         Ps[p].set_fill_level(Ps[p].get_volume_max(), 0.3)
#         timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
#         Ps[p].set_fill_level(0.0, 0.3)
#         timer.wait_until(Ps[p].is_pumping, False)
#     except (NodeNotFound, NetworkXNoPath, KeyError) as e:
#         pass
# pathRP = graph.findPath(start_node="Reservoir6", end_node="E0.0")
# pathPW = graph.findPath(start_node="E0.0", end_node=conf["CetoniDevice"]["waste"])
# # pathPW2 = graph.findPath(start_node=p, end_node=conf["CetoniDevice"]["waste"])
# # CetoniDevice_action.switchValves(nodelist=pathPW2, valvesDict=Vs)
# # Ps[p].set_fill_level(0.0, 0.1)
# # timer.wait_until(Ps[p].is_pumping, False)
# CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
# Ps["E0.0"].set_fill_level(Ps["E0.0"].get_volume_max(), 0.3)
# timer.wait_until(Ps["E0.0"].is_pumping, False)
# CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
# Ps["E0.0"].set_fill_level(0.0, 0.3)
# timer.wait_until(Ps["E0.0"].is_pumping, False)

# for p in Ps.keys():
#     print(p)
#     try:
#         timer = qmixbus.PollingTimer(300000)
#         pathRP = graph.findPath(start_node=assignment[p], end_node=p)
#         pathPW = graph.findPath(start_node=p, end_node=conf["CetoniDevice"]["waste"])
#         # CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
#         # Ps[p].set_fill_level(0.0, 0.1)
#         # timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
#         Ps[p].set_fill_level(Ps[p].get_volume_max(), 0.3)
#         timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
#         Ps[p].set_fill_level(0.0, 0.3)
#         timer.wait_until(Ps[p].is_pumping, False)
#     except (NodeNotFound, NetworkXNoPath, KeyError) as e:
#         pass

# timer = qmixbus.PollingTimer(300000)
# pathRP = graph.findPath(start_node="Reservoir1", end_node="A0.0")
# CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
# Ps["A0.0"].set_fill_level(Ps["A0.0"].get_volume_max(), 0.1)
# timer.wait_until(Ps["A0.0"].is_pumping, False)
# path = graph.findPath(start_node="A0.0", end_node=f"V3.1")
# Ps["A0.0"].set_fill_level(0.0, 0.05)
# for i in range(11):
#     if i not in [7,8]:
#         path = graph.findPath(start_node="A0.0", end_node=f"V3.{i}")
#         CetoniDevice_action.switchValves(nodelist=path, valvesDict=Vs)
#         time.sleep(10)
# Ps["A0.0"].stop_pumping()

# pathPW = graph.findPath(start_node="A0.0", end_node="densioViscoIN") + graph.findPath(start_node="densioViscoOUT", end_node=conf["CetoniDevice"]["waste"])
# CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
# Ps["A0.0"].set_fill_level(0.0, 0.1)
# timer.wait_until(Ps["A0.0"].is_pumping, False)
#CetoniDevice_action.goToRefPos(pumpsDict=Ps, valvesDict=Vs, mode="end", gas="Reservoir5")
# CetoniDevice_driver.cetoni.quitCetoni()