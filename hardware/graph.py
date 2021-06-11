import networkx as nx   # https://networkx.org/documentation/stable/tutorial.html
import matplotlib.pyplot as plt
import pandas as pd

# Load the information regarding the tubing from tubing.csv to tubing_info.
tubing_info = pd.read_csv("hardware/tubing.csv", sep=";")
# https://www.geeksforgeeks.org/python-convert-string-to-tuple/; conversion of str to tuple by using eval

# Group information regarding nodes and edges.
nodes = []
positions = {}
# Go through all sart nodes and add them and their attributes to nodes. Also add their position to positions.
for node_start in tubing_info.loc[tubing_info["usage"] == "used", "start_node"]:
    nodes.append((node_start, {"position": eval(tubing_info.loc[tubing_info["start_node"] == node_start, "position_start"].values[0]), 
    "dead_volume": float(tubing_info.loc[tubing_info["start_node"] == node_start, "dead_volume_start"].values[0])}))
    positions[node_start] = eval(tubing_info.loc[tubing_info["start_node"] == node_start, "position_start"].values[0])
# Go through all end nodes and add them and their attributes to nodes. Also add their position to positions.
for node_end in tubing_info.loc[tubing_info["usage"]== "used", "end_node"]:
    nodes.append((node_end, {"position": eval(tubing_info.loc[tubing_info["end_node"] == node_end, "position_end"].values[0]),
    "dead_volume": float(tubing_info.loc[tubing_info["end_node"] == node_end, "dead_volume_end"].values[0])}))
    positions[node_end] = eval(tubing_info.loc[tubing_info["end_node"] == node_end, "position_end"].values[0])    # https://www.delftstack.com/howto/python-pandas/how-to-get-a-value-from-a-cell-of-a-dataframe/#dfcol_name.values-to-get-value-from-a-cell-of-a-pandas-dataframe; .values[] to get value of cell

edges = []
# Go through all the edges and add them to edges.
for edge in tubing_info.loc[tubing_info["usage"] == "used", "edge"]:
    edges.append((tubing_info.loc[tubing_info["edge"] == edge, "start_node"].values[0], tubing_info.loc[tubing_info["edge"] == edge, "end_node"].values[0], {"length": float(tubing_info.loc[tubing_info["edge"] == edge, "length"].values[0]), "diameter": float(tubing_info.loc[tubing_info["edge"] == edge, "diameter"].values[0]), "ends": tubing_info.loc[tubing_info["edge"] == edge, "ends"].values[0]}))


# Generate a graph named setup based on the data contained in tubing_info.
setup = nx.Graph()
setup.add_nodes_from(nodes)
setup.add_edges_from(edges)

nx.draw(setup, pos=positions, with_labels=True)

plt.show()

# TODO: Check V4.0 to V6.0

''' dijkstra_path(G, source, target[, weight])
	

Returns the shortest weighted path from source to target in G. ref. https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html'''