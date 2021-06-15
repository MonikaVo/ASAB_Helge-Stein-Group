import networkx as nx   # https://networkx.org/documentation/stable/tutorial.html
import matplotlib.pyplot as plt
import pandas as pd
import pickle

# TODO: make graph a directed graph
# TODO: Remove this after definintion of helper function!!!
def SaveToFile(filename, data):
    with open(filename, 'wb') as out_file:
        pickle.dump(data, out_file) # https://stackoverflow.com/questions/20101021/how-to-close-the-file-after-pickle-load-in-python

# # Define the paths to the files nodes.csv, edges.csv and current tubing.csv valid for the configuration
# nodes_path = "hardware/nodes.csv"
# edges_path = "hardware/edges.csv"
# tubing_path = "hardware/tubing.csv"

def generateGraph(graph_name="setup", path_nodes="hardware/nodes.csv", path_edges="hardware/edges.csv", path_tubing="hardware/tubing.csv", show=True, save=True, save_path="hardware/graph.pck"):
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
        edges.append((edges_info.loc[edges_info["edge"] == edge, "start_fixed"].values[0], edges_info.loc[edges_info["edge"] == edge, "end_fixed"].values[0],
        {"name": edge, "ends": edges_info.loc[edges_info["edge"] == edge, "ends"].values[0], "length": float(edges_info.loc[edges_info["edge"] == edge, "length"].values[0]),
        "diameter": float(edges_info.loc[edges_info["edge"] == edge, "diameter"].values[0]), "dead_volume": float(edges_info.loc[edges_info["edge"] == edge, "dead_volume"].values[0])}))
        # Add the second direction of the edge, if the edge is undirected.
        if edges_info.loc[edges_info["edge"] == edge, "restriction"].values[0] == "undirected":
            edges.append((edges_info.loc[edges_info["edge"] == edge, "end_fixed"].values[0], edges_info.loc[edges_info["edge"] == edge, "start_fixed"].values[0],
            {"name": edge, "ends": edges_info.loc[edges_info["edge"] == edge, "ends"].values[0], "length": float(edges_info.loc[edges_info["edge"] == edge, "length"].values[0]),
            "diameter": float(edges_info.loc[edges_info["edge"] == edge, "diameter"].values[0]), "dead_volume": float(edges_info.loc[edges_info["edge"] == edge, "dead_volume"].values[0])}))
    for edge in tubing_config["edge"]:
        edges.append((tubing_config.loc[tubing_config["edge"] == edge, "start_node"].values[0], tubing_config.loc[tubing_config["edge"] == edge, "end_node"].values[0],
        {"name": edge, "ends": edges_info.loc[edges_info["edge"] == edge, "ends"].values[0], "length": float(edges_info.loc[edges_info["edge"] == edge, "length"].values[0]),
        "diameter": float(edges_info.loc[edges_info["edge"] == edge, "diameter"].values[0]), "dead_volume": float(edges_info.loc[edges_info["edge"] == edge, "dead_volume"].values[0])}))
        # Add the second direction of the edge, if the edge is undirected.
        if edges_info.loc[edges_info["edge"] == edge, "restriction"].values[0] == "undirected":
            edges.append((tubing_config.loc[tubing_config["edge"] == edge, "end_node"].values[0], tubing_config.loc[tubing_config["edge"] == edge, "start_node"].values[0],
            {"name": edge, "ends": edges_info.loc[edges_info["edge"] == edge, "ends"].values[0], "length": float(edges_info.loc[edges_info["edge"] == edge, "length"].values[0]),
            "diameter": float(edges_info.loc[edges_info["edge"] == edge, "diameter"].values[0]), "dead_volume": float(edges_info.loc[edges_info["edge"] == edge, "dead_volume"].values[0])}))

    # Generate a graph named graph_name based on the data contained in tubing_info.
    graph_name = nx.DiGraph()
    graph_name.add_nodes_from(nodes)
    graph_name.add_edges_from(edges)

    if show==True:
        drawGraph(graph_name, positions, wlabels=True)

    # If the parameter is set accordingly, save the graph to a pickle file. Else return the graph.
    if save==True:
        # TODO: Generate helper functions file and import it in order to save the graph as a pickle file.
        SaveToFile(save_path, graph_name)
    elif save==False:
        return graph_name

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
    ''' Based on a list of nodes describing a path in the graph, this function returns the required settings of the valves needed to realise this path. '''
    valveSettings = {}
    for node in nodelist:
        print("node", str(node), node[0:2])
        valve = node[0:2]
        if valve in valvePositionDict.keys():
            print("valve", valve)
            print(node[-1])
            if node[-1] != str(0):
                valveSettings[valve] = valvePositionDict[valve][node]
            elif node[-1] == str(0):
                print("node_here", node)
                pass
            elif valve in valveSettings.keys() and node[-1] != str(0):
                print("This path is not valid, because it passes the same valve multiple times.")
    return valveSettings

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
print(valvePositionDict)



setup = generateGraph(show=True, save=False)
#myPath = getEdgedictFromNodelist(setup, nx.dijkstra_path(setup, "A0.0", "Reservoir2", "dead_volume"))   # https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html

print(nx.dijkstra_path(setup, "A0.0", "Reservoir1", "dead_volume"))
print(getValveSettings(nx.dijkstra_path(setup, "A0.0", "Reservoir1", "dead_volume")))


# TODO: dict with valve settings qmix_valve
# TODO: Add function to load a graph