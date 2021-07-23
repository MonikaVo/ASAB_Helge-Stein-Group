import networkx as nx   # https://networkx.org/documentation/stable/tutorial.html
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from helpers import SaveToFile, LoadFile


def checkConsistency(path_nodes="filesForOperation/hardware/nodes.csv", path_edges="filesForOperation/hardware/edges.csv", path_tubing="filesForOperation/hardware/tubing.csv"):
    ''' This function checks, if the setup files for the graph are consistent. It checks whether all the edges given in
    tubing.csv are contained in edges.csv and if all nodes referenced in tubing.csv are contained in nodes.csv. It returns
    three results for edges and nodes, edges and nodes.  '''
    edges_frame = pd.read_csv(path_edges, sep=";")
    nodes_frame = pd.read_csv(path_nodes, sep=";")
    tubing_frame = pd.read_csv(path_tubing, sep=";")
    tubing_nodes_frame = pd.concat([tubing_frame["start"], tubing_frame["end"]], axis=0)
    tubing_edges_frame = tubing_frame["edge"]

    edges = list(edges_frame["edge"])
    nodes = list(nodes_frame["node"])
    edges_tubing = list(tubing_frame["edge"])
    nodes_tubing = list(tubing_nodes_frame)

    edgs = all([edge in edges for edge in edges_tubing])
    nods = all([node in nodes for node in nodes_tubing])

    if (edgs and nods) and edgs and nods:
        return edgs and nods, edgs, nods
    else:
        new_nodes = tubing_nodes_frame[[node not in nodes for node in nodes_tubing]]
        new_edges = tubing_edges_frame[[edge not in edges for edge in edges_tubing]]
        return edgs and nods, new_edges, new_nodes

def generateGraph(path_nodes=r"filesForOperation/hardware/nodes.csv", path_edges=r"filesForOperation/hardware/edges.csv", path_tubing=r"filesForOperation/hardware/tubing.csv", show=True, save=True, save_folder=r"filesForOperation", save_path=r"hardware/setup.pck"):
    # Load the information regarding the nodes from nodes.csv to nodes_info.
    nodes_info = pd.read_csv(path_nodes, sep=";")
    # Load the information regarding the edges from edges.csv to nodes_info.
    edges_info = pd.read_csv(path_edges, sep=";")
    # Load the current configuration file for the tubing tubing.csv.
    tubing_config = pd.read_csv(path_tubing, sep=";")

    # Group information regarding nodes.
    nodes = []
    positions = {}
    # Go through all nodes in nodes.csv and add them and their position to a dictionary in order to add them to the graph lateron.
    for node in nodes_info["node"]:
        nodes.append((node, {"name": node,"position": eval(nodes_info.loc[nodes_info["node"] == node, "position_node"].values[0])})) # https://www.geeksforgeeks.org/python-convert-string-to-tuple/; conversion of str to tuple by using eval
        positions[node] = eval(nodes_info.loc[nodes_info["node"] == node, "position_node"].values[0])

    # Group information regarding edges.
    edges = []
    # Go through all the fixed edges in edges.csv and the edges contained in tubing.csv in order to generate the required dictionary containing the edges and their properties.
    for edge in edges_info.loc[edges_info["status"] == "fixed", "edge"]:
        appendEdge(edges, edge, edges_info, edges_info, reverse=(edges_info.loc[edges_info["edge"] == edge, "restriction"].values[0] == "undirected"))
    for edge in tubing_config["edge"]:
        appendEdge(edges, edge, tubing_config, edges_info, reverse=(edges_info.loc[edges_info["edge"] == edge, "restriction"]).values[0] == "undirected")

    # Generate a graph named graph based on the data contained in tubing_info.
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    if show==True:
        drawGraph(graph, positions, wlabels=True)

    # If the parameter is set accordingly, save the graph and the positions to a pickle file. Else return the graph.
    if save==True:
        SaveToFile(save_path, graph, path=save_folder)
        SaveToFile("{}{}".format(str(save_path[0:-4]), "_positions.pck"), positions, path=save_folder)
        return graph
    elif save==False:
        return graph
   

def appendEdge(edgelst, edge_name, edgeNodes, edgeProps, reverse=False):
    ''' This function adds an edge to a list of edges. The edge is defined according to the format required by the graph. Data is taken from pandas dataframes containing nodes and
    properties of the edges. If the option reverse is set to true, then the edge is considered to be undirected and the reverse edge is also added to the list. This enable passage
    of the path in both directions in a directed graph. '''
    edgelst.append((edgeNodes.loc[edgeNodes["edge"] == edge_name, "start"].values[0], edgeNodes.loc[edgeNodes["edge"] == edge_name, "end"].values[0],
            {"name": edge_name, "ends": edgeProps.loc[edgeProps["edge"] == edge_name, "ends"].values[0], "length": float(edgeProps.loc[edgeProps["edge"] == edge_name, "length"].values[0]),
            "diameter": float(edgeProps.loc[edgeProps["edge"] == edge_name, "diameter"].values[0]), "dead_volume": float(edgeProps.loc[edgeProps["edge"] == edge_name, "dead_volume"].values[0])}))
    if reverse == True:
        edgelst.append((edgeNodes.loc[edgeNodes["edge"] == edge_name, "end"].values[0], edgeNodes.loc[edgeNodes["edge"] == edge_name, "start"].values[0],
            {"name": edge_name, "ends": edgeProps.loc[edgeProps["edge"] == edge_name, "ends"].values[0], "length": float(edgeProps.loc[edgeProps["edge"] == edge_name, "length"].values[0]),
            "diameter": float(edgeProps.loc[edgeProps["edge"] == edge_name, "diameter"].values[0]), "dead_volume": float(edgeProps.loc[edgeProps["edge"] == edge_name, "dead_volume"].values[0])}))


def drawGraph(graph, positions, wlabels=True):
    ''' This function draws and shows a graph. '''
    nx.draw(graph, pos=positions, with_labels=wlabels)
    plt.show()

def getEdgedictFromNodelist(graph, nodelist):
    ''' This function generates a dictionary of edges from a list of nodes. It takes a list of nodes as an input and returns a dictionary of edges with the name of the edge as
    a key. '''
    edgesDict = {}
    for nd in nodelist:
        if (nodelist.index(nd)+1) < (len(nodelist)):
            edgesDict[graph[nd][nodelist[nodelist.index(nd)+1]]["name"]] = graph[nd][nodelist[nodelist.index(nd)+1]]    # https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.get_edge_data.html
    return edgesDict

def getTotalQuantity(edgedict, quantity):   # Corresponds to networkx.path_weight.
    ''' This function calculates a total quantity (e.g. dead volume) for a list of edges. It takes a dictionary of edges including their attributes
    as an input and returns the dead volume as a float. '''
    quantityTotal = 0.0    
    for edg in edgedict.keys():
        quantityTotal += edgedict[edg][quantity]
    return quantityTotal

# Definiton of valvePositionDict correlating the valve position taken by the Cetoni API to the label of the respective node in the graph.
def generate_valvePositionDict(save_path=r"filesForOperation", save_name=r"hardware/valvePositionDict.pck"):
    valvePositionDict = {}
    for j in range(1,7):    # TODO: This is specific for the current equipment! Change for expansion of the setup or include in config file!
        valvePositionDict["V{}".format(j)] = {}
        for i in range(0,11):
            key = "V{}.{}".format(j,i)
            valvePositionDict["V{}".format(j)][key] = i-1 if i != 0 else None
    for p in ["Av", "Bv", "Cv", "Dv", "Ev", "Fv"]:
        valvePositionDict["{}".format(p)] = {}
        for z in [1,2]:
            key2 = "{}{}".format(p,z)
            valvePositionDict[p][key2] = 1 if z==1 else 0
    SaveToFile(save_name, valvePositionDict, path=save_path)

def getValveSettings(nodelist, valvePositionDict):
    ''' Based on a list of nodes describing a path in the graph and a dict of valve positions, this function returns the required settings of the valves needed to realise
    this path, in case there are valves included in the path. Otherwise, an empty dict will be returned. The output is of type dict. '''
    valveSettings = {}
    for node in nodelist:
        valve = node[0:2]
        if valve in valvePositionDict.keys():
            if node[-2::] != ".0":
                valveSettings[valve] = valvePositionDict[valve][node]
            elif node[-2::] == ".0":
                pass
            elif valve in valveSettings.keys() and node[-2::] != ".0":
                print("This path is not valid, because it passes the same valve multiple times.")
    return valveSettings

def loadGraph(graphFile=r"filesForOperation/hardware/setup.pck", valvePositionDictFile=r"filesForOperation/hardware/valvePositionDict.pck"):
    this_graph = LoadFile(graphFile)
    this_valvePositionDict = LoadFile(valvePositionDictFile)
    return this_graph, this_valvePositionDict

def findClosest(graph, node, candidates, weight="dead_volume", direction="out"):
    ''' Finds the closest candidate to a given node regarding a specified weight for the path. The direction of the search can be either
    incoming to the node or outgoing from the node. The default is outgoing. The function returns the closest node among the given candidates
    and the path from the specified node to this candidate node. candidates is of type "list". '''
    # Put together a dataframe to store the path lengths
    startingData = np.zeros((len(candidates), 3), dtype=object)
    print("startingData \n", startingData)
    startingData[:,0] = candidates
    print("startingData \n", startingData)
    shortest_distances = pd.DataFrame(startingData, columns=["candidate", "shortestPathLength", "shortestPath"], dtype=object)
    print("shortest_distances\n", shortest_distances)
    # Calculate for each candidate the shortest path with respect to the given weight
    for candidate in candidates:
        # If the direction is outgoing from the node, check the paths starting from the node and ending in the candidate
        if direction=="out":
            length_out, path_out = nx.single_source_dijkstra(graph, node, candidate, weight=weight)
            shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPathLength"] = length_out
            shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPath"] = str(path_out)
        # If the direction is incoming to the node, check the paths starting from the candidate and ending in the node
        elif direction=="in":
            length_in, path_in = nx.single_source_dijkstra(graph, candidate, node, weight=weight)
            shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPathLength"] = length_in
            shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPath"] = str(path_in)
    print("shortest_distances \n", shortest_distances)
    closest = shortest_distances.loc[shortest_distances["shortestPathLength"]==min(shortest_distances["shortestPathLength"]), "candidate"].values[0]
    pathToClosest = shortest_distances.loc[shortest_distances["candidate"]==closest, "shortestPath"].values[0]
    print(closest)
    print("pathToClosest \n", pathToClosest)
    #print("pathToClosest type \n", type(pathToClosest.tolist()))
    return closest, pathToClosest

# setup1 = generateGraph(show=True, save=True)#loadGraph()
setup2, vPd2 = loadGraph()#generateGraph2(show=True, save=True)
# print(setup1.number_of_edges())
# print(setup2.number_of_edges())
drawGraph(setup2,LoadFile(r"filesForOperation/hardware/setup_positions.pck"))

# print(nx.dijkstra_path(setup2, "A0.0", "Reservoir1", "dead_volume"))
# print(type(nx.dijkstra_path(setup2, "A0.0", "Reservoir1", "dead_volume")))
# print(getValveSettings(nx.dijkstra_path(setup1, "A0.0", "Reservoir1", "dead_volume")))
# print(getValveSettings(nx.dijkstra_path(setup2, "A0.0", "Reservoir1", "dead_volume"), vPd2))
# print(findClosest(setup2, "Reservoir2", ["A0.0", "B0.0", "C0.0", "D0.0", "E0.0", "F0.0"], "dead_volume"))
# drawGraph(setup2, LoadFile(r"hardware/setup_positions.pck"))

# print(getTotalQuantity(getEdgedictFromNodelist(setup1, nx.dijkstra_path(setup1, "A0.0", "Reservoir1", "dead_volume")), "length"))

# TODO: Implement function to automatically find a practical way to realize an experiment. (Pump substance X from A to B via C.) This will require the following subfunctions:
#       - Find the path with the least dead volume from A to B via C and D, where the sequence of C and D may matter or not.
#       - Select a pump between different steps according to its status and the dead volume in the path from the relevant position to the pump
#       - Insert nodes ( e.g. a pump) into a path.
# TODO: Based on the functions mentioned above, implement an improved cleaning routine.
# TODO: Check paths or better: implement that going through three  nodes of one valve is not allowed.