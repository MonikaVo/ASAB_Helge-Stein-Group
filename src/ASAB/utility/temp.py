# def _findPath(*args):
#     ''' This function finds a path from the start node to the end node and if applicable passees the nodes given as a list in *kwargs in the sequence given. '''
#     print(list(args))

# _findPath()

from ASAB.configuration import default_config
conf = default_config.config

from ASAB.utility import graph

graph.findPathAB("Reservoir1", "A0.0")