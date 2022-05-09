# def _findPath(*args):
#     ''' This function finds a path from the start node to the end node and if applicable passees the nodes given as a list in *kwargs in the sequence given. '''
#     print(list(args))

# _findPath()

from ASAB.configuration import default_config
conf = default_config.config

from ASAB.utility import graph
with open(r'src\ASAB\filesForOperation\hardware\setup_positions.txt', 'r') as a:
    posfile = a.read()
pos=eval(posfile)
#print(dict(posfile))
graph.drawGraph(graph=conf["CetoniDeviceDriver"]["setup"], positions= pos)

print(graph.findPathAB(start_node="densioViscoIN", end_node="V6.0"))
print(graph.findPath(start_node="A0.0", end_node="D0.0", valvePositionDict=conf["CetoniDeviceDriver"]["valvePositionDict"], graph=conf["CetoniDeviceDriver"]["setup"], weight="dead_volume", via=['densioViscoIN', 'V6.0']))