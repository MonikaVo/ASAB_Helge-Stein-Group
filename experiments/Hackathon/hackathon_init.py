import uvicorn
import sys
sys.path.append("...\\ASAB\\server") # edited prior to publication
import initASAB_SWenv

from experiments.Hackathon import config_Hackathon

conf = config_Hackathon.config

from utility import graph
from driver import CetoniDevice_driver
from action import CetoniDevice_action, densioVisco_action

## Generate the graph and its valvePositionDict
graph.generateGraph(show=False)
## Prepare the Cetoni device
Ps, Vs, Cs = CetoniDevice_driver.cetoni.prepareCetoni()
## Pumps go to reference positions
CetoniDevice_action.goToRefPos(pumpsDict=Ps, valvesDict=Vs, mode="start", gas="Reservoir5")
## Define the assignment
assignment = conf["CetoniDevice"]["assignment"]
## Flush the syringes
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


from server import CetoniDevice_server, densioVisco_server
uvicorn.run(CetoniDevice_server.app, host="<host IP>", port=<port>) # edited prior to publication

# for p in Ps.keys():
#     Ps[p].calibrate()

# CetoniDevice_action.goToRefPos(Ps, Vs, "end")
#path = graph.findPath(start_node="A0.0", end_node="Reservoir1")
#CetoniDevice_action.switchValves(path, Vs)
#Ps["A0.0"].set_fill_level(0.0, 0.1)
# Ps["A0.0"].calibrate()

# ## Cleaning

# from qmixsdk import qmixbus
# from networkx.exception import NodeNotFound, NetworkXNoPath
# import time

# ## Through densiometer
# # Run once with gas, EMC and once with Hexane then with gas

# print("Clean densio")

# for p in Ps.keys():
#     print(p)
#     try:
#         timer = qmixbus.PollingTimer(300000)
#         pathRP = graph.findPath(start_node=assignment[p], end_node=p)
#         pathPW = graph.findPath(start_node=p, end_node="densioViscoIN") + graph.findPath(start_node="densioViscoOUT", end_node=conf["CetoniDevice"]["waste"])
#         # pathPW2 = graph.findPath(start_node=p, end_node=conf["CetoniDevice"]["waste"])
#         # CetoniDevice_action.switchValves(nodelist=pathPW2, valvesDict=Vs)
#         # Ps[p].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"])
#         # timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
#         Ps[p].set_fill_level(Ps[p].get_volume_max()/3., conf["CetoniDeviceDriver"]["flow"])
#         timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
#         Ps[p].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"])
#         timer.wait_until(Ps[p].is_pumping, False)
#     except (NodeNotFound, NetworkXNoPath, KeyError) as e:
#         pass
# # pathRP = graph.findPath(start_node="Reservoir6", end_node="E0.0")
# # pathPW = graph.findPath(start_node="E0.0", end_node=conf["CetoniDevice"]["waste"])
# # # pathPW2 = graph.findPath(start_node=p, end_node=conf["CetoniDevice"]["waste"])
# # # CetoniDevice_action.switchValves(nodelist=pathPW2, valvesDict=Vs)
# # # Ps[p].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"])
# # # timer.wait_until(Ps[p].is_pumping, False)
# # CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
# # Ps["E0.0"].set_fill_level(Ps["E0.0"].get_volume_max(), conf["CetoniDeviceDriver"]["flow"])
# # timer.wait_until(Ps["E0.0"].is_pumping, False)
# # CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
# # Ps["E0.0"].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"])
# # timer.wait_until(Ps["E0.0"].is_pumping, False)

# ## Directly to waste
# # Run once with EMC and once with Hexane and then with gas

# print('Clean to waste')

# for p in Ps.keys():
#     print(p)
#     try:
#         timer = qmixbus.PollingTimer(300000)
#         pathRP = graph.findPath(start_node=assignment[p], end_node=p)
#         pathPW = graph.findPath(start_node=p, end_node=conf["CetoniDevice"]["waste"])
#         # CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
#         # Ps[p].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"])
#         # timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
#         Ps[p].set_fill_level(Ps[p].get_volume_max()/3., conf["CetoniDeviceDriver"]["flow"])
#         timer.wait_until(Ps[p].is_pumping, False)
#         CetoniDevice_action.switchValves(nodelist=pathPW, valvesDict=Vs)
#         Ps[p].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"])
#         timer.wait_until(Ps[p].is_pumping, False)
#     except (NodeNotFound, NetworkXNoPath, KeyError) as e:
#         pass

# ## Clean the valve
# # Run once with EMC and once with Hexane and finally with gas

# print('Clean valve')

# for i in range(2):
#     timer = qmixbus.PollingTimer(300000)
#     pathRP = graph.findPath(start_node="Reservoir1", end_node="A0.0")
#     CetoniDevice_action.switchValves(nodelist=pathRP, valvesDict=Vs)
#     Ps["A0.0"].set_fill_level(Ps["A0.0"].get_volume_max()/3., conf["CetoniDeviceDriver"]["flow"])
#     timer.wait_until(Ps["A0.0"].is_pumping, False)
#     path = graph.findPath(start_node="A0.0", end_node="V3.1")
#     Ps["A0.0"].set_fill_level(0.0, conf["CetoniDeviceDriver"]["flow"]/3.)
#     for i in range(11):
#         if i not in [7,8]:
#             path = graph.findPath(start_node="A0.0", end_node=f"V3.{i}")
#             CetoniDevice_action.switchValves(nodelist=path, valvesDict=Vs)
#             time.sleep(10)
#     timer.wait_until(Ps["A0.0"].is_pumping, False)

# # CetoniDevice_driver.pumpObj.stop_all_pumps()
