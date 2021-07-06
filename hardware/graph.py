import networkx as nx   # https://networkx.org/documentation/stable/tutorial.html
import matplotlib.pyplot as plt
import pandas as pd
import pickle

#TODO: Remove this after definintion of helper function!!!
def SaveToFile(filename, data):
    with open(filename, 'wb') as out_file:
        pickle.dump(data, out_file) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

def appendEdge(edgelst, edge_name, edgeNodes, edgeProps, reverse=False):
    edgelst.append((edgeNodes.loc[edgeNodes["edge"] == edge_name, "start"].values[0], edgeNodes.loc[edgeNodes["edge"] == edge_name, "end"].values[0],
            {"name": edge_name, "ends": edgeProps.loc[edgeProps["edge"] == edge_name, "ends"].values[0], "length": float(edgeProps.loc[edgeProps["edge"] == edge_name, "length"].values[0]),
            "diameter": float(edgeProps.loc[edgeProps["edge"] == edge_name, "diameter"].values[0]), "dead_volume": float(edgeProps.loc[edgeProps["edge"] == edge_name, "dead_volume"].values[0])}))
    if reverse == True:
        edgelst.append((edgeNodes.loc[edgeNodes["edge"] == edge_name, "end"].values[0], edgeNodes.loc[edgeNodes["edge"] == edge_name, "start"].values[0],
            {"name": edge_name, "ends": edgeProps.loc[edgeProps["edge"] == edge_name, "ends"].values[0], "length": float(edgeProps.loc[edgeProps["edge"] == edge_name, "length"].values[0]),
            "diameter": float(edgeProps.loc[edgeProps["edge"] == edge_name, "diameter"].values[0]), "dead_volume": float(edgeProps.loc[edgeProps["edge"] == edge_name, "dead_volume"].values[0])}))

def generateGraph(path_nodes="hardware/nodes.csv", path_edges="hardware/edges.csv", path_tubing="hardware/tubing.csv", show=True, save=True, save_path="hardware/setup.pck"):
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
        appendEdge(edges, edge, tubing_config, edges_info, reverse=(edges_info.loc[edges_info["edge"] == edge, "restriction"].values[0] == "undirected"))
     
    # Generate a graph named graph based on the data contained in tubing_info.
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    if show==True:
        drawGraph(graph, positions, wlabels=True)

    # If the parameter is set accordingly, save the graph to a pickle file. Else return the graph.
    if save==True:
        # TODO: Generate helper functions file and import it in order to save the graph as a pickle file.
        SaveToFile(save_path, graph)
        return graph
    elif save==False:
        return graph
   

def drawGraph(graph, positions, wlabels=True):
    ''' This function draws and shows a graph. '''
    nx.draw(graph, pos=positions, with_labels=wlabels)
    plt.show()

def getEdgedictFromNodelist(graph, nodelist):
    ''' This function generates a dictionary of edges from a list of nodes.
    It takes a list of nodes as an input and returns a dictionary of edges with the name of the edge as a key. '''
    edgesDict = {}
    for nd in nodelist:
        if (nodelist.index(nd)+1) <= (len(nodelist)-1):
            edgesDict[graph[nd][nodelist[nodelist.index(nd)+1]][0]["name"]] = graph[nd][nodelist[nodelist.index(nd)+1]]    # https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.get_edge_data.html
    return edgesDict

def getTotalQuantity(edgedict, quantity):
    ''' This function calculates the total dead volume for a list of edges. It takes a dictionary of edges including their attributes
    as an input and returns the dead volume as a float. '''
    deadVolTotal = 0.0    
    for edg in edgedict.keys():
        deadVolTotal += edgedict[edg][quantity]
    return deadVolTotal

def getValveSettings(nodelist):
    ''' Based on a list of nodes describing a path in the graph, this function returns the required settings of the valves needed to realise
    this path, in case there are valves included in the path. Otherwise, an empty list will be returned. '''
    valveSettings = {}
    for node in nodelist:
        valve = node[0:2]
        if valve in valvePositionDict.keys():
            if node[-1] != str(0):
                valveSettings[valve] = valvePositionDict[valve][node]
            elif node[-1] == str(0):
                pass
            elif valve in valveSettings.keys() and node[-1] != str(0):
                print("This path is not valid, because it passes the same valve multiple times.")
    return valveSettings

def loadGraph(graphFile=r"hardware/setup.pck"):
    # TODO: Define helper functions and include it here
    with open(graphFile, 'rb') as load_file:
        out = pickle.load(load_file)
    return out


# Definiton of valvePositionDict correlating the valve position taken by the Cetoni API to the label of the respective node in the graph.
def generate_valvePositionDict():
    valvePositionDict = {}
    for j in range(1,7):
        valvePositionDict["V{}".format(j)] = {}
        for i in range(0,11):
            key = "V{}.{}".format(j,i)
            valvePositionDict["V{}".format(j)][key] = i-1 if i != 0 else None
    for p in ["Av", "Bv", "Cv", "Dv", "Ev", "Fv"]:
        valvePositionDict["{}".format(p)] = {}
        for z in [1,2]:
            key2 = "{}{}".format(p,z)
            valvePositionDict[p][key2] = 0 if z==1 else 1
    SaveToFile(r"hardware/valvePositionDict.pck", valvePositionDict)



# setup1 = generateGraph1(show=True, save=True)#loadGraph()
# setup2 = loadGraph()#generateGraph2(show=True, save=True)
# print(setup1.number_of_edges())
# print(setup2.number_of_edges())

# print(nx.dijkstra_path(setup1, "A0.0", "Reservoir1", "dead_volume"))
# print(nx.dijkstra_path(setup2, "A0.0", "Reservoir1", "dead_volume"))
# print(getValveSettings(nx.dijkstra_path(setup1, "A0.0", "Reservoir1", "dead_volume")))
# print(getValveSettings(nx.dijkstra_path(setup2, "A0.0", "Reservoir1", "dead_volume")))