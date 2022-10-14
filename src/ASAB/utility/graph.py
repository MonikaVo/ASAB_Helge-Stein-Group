## Get the configuration
try:
    # if there is a main file, get conf from there
    from __main__ import conf   # https://stackoverflow.com/questions/6011371/python-how-can-i-use-variable-from-main-file-in-module
except ImportError as ie:
    # if the import fails, check, if it is a test, which means, that a file in a pytest folder will be main and thus it will be in the path returned in the error message of the ImportError.
    if ('pytest' in str(ie)):
        # the software will produce a warning, which reports the switch to the testing configuration. This warning is always shown.
        import warnings
        warnings.filterwarnings('always')
        warnings.warn('Configuration from main not available, but this looks like a test. Loading test configuration instead.', category=ImportWarning)
        # the filtering funcitons are set to default again
        warnings.filterwarnings('default')
        # the test configuration is imported
        from ASAB.test.FilesForTests import config_test
        conf = config_test.config
    # if "pytest" is not in the error message, it is assumed, that the call did not originate from a test instance and it therefore raises the ImportError.
    else:
        raise ie

## Imports from ASAB
from ASAB.utility.helpers import loadVariable, saveToFile, typeCheck
from ASAB.driver.CetoniDevice_driver import getValvePositionDict

## Other imports
from typing import Union, Tuple, List
import networkx as nx   # https://networkx.org/documentation/stable/tutorial.html
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path


def generateGraph(show:bool=False, save:bool=True, path_nodes:str=conf["graph"]["pathNodes"], path_edges:str=conf["graph"]["pathEdges"], path_tubing:str=conf["graph"]["pathTubing"], save_path:str=conf["graph"]["savePath_graph"]) -> Tuple[nx.DiGraph, dict]:
    ''' This function generates a graph including the corresponding node positions and it can save both to the save_path according to the setting of the save parameter.
    
    Inputs:
    show: a boolean stating, whether a plot of the graph shall be shown after the graph is generated
    save: a boolean stating, whether the graph shall be saved after it is generated
    path_nodes: a string giving a path to the .csv file listing the nodes of the graph
    path_edges: a string giving a path to the .csv file listing available edges, which can be used in the graph
    path_tubing: a string giving a path to the .csv file listing the tubings acutally relevant for the graph
    save_path: a string representing the path, to which the graph shall be saved including the filename and the extension. The savename and path of the positions-file
               will be deduced from this path.
               
    Outputs:
    graph: the graph object (type networkX.DiGraph) generated based on the inputs
    postitions: a dictionary with the node names as keys and the positions as values '''

    ## Check input types
    typeCheck(func=generateGraph, locals=locals())
    # # check show, save, path_nodes, path_edges, path_tubing and save_path

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
        pos_str = nodes_info.loc[nodes_info["node"] == node, "position_node"].values[0]
        pos_list = [float(koord) for koord in pos_str.strip('()').split(',')]
        positions[node] = tuple(pos_list)
        nodes.append((node, {"name": node,"position": tuple(pos_list)}))
    # Group information regarding edges.
    edges = []
    # Go through all the fixed edges in edges.csv and the edges contained in tubing.csv in order to generate the required dictionary containing the edges and their
    # properties.
    for edge in edges_info.loc[edges_info["flexibility"] == "fixed", "edge"]:
        appendEdge(edges, edge, edges_info, edges_info, reverse=(edges_info.loc[edges_info["edge"] == edge, "restriction"].values[0] == "undirected"))
    for edge in tubing_config["edge"]:
        appendEdge(edges, edge, tubing_config, edges_info, reverse=(edges_info.loc[edges_info["edge"] == edge, "restriction"].values[0] == "undirected"))

    # Generate a graph named graph based on the data contained in tubing_info.
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    if show==True:
        drawGraph(graph, positions, wlabels=True)

    # If the parameter is set accordingly, save the graph and the positions to a pickle file. Else return the graph.
    if save==True:
        folder = '\\'.join(save_path.split('\\')[:-1])
        filename = save_path.split('\\')[-1].split('.')[0]
        saveToFile(folder=folder, filename=filename, extension="py", data=f'graph = {str(nx.to_dict_of_dicts(graph))}')
        saveToFile(folder=folder, filename=f"{filename}_positions", extension="py", data=f'graph_positions = {str(positions)}')
        drawGraph(graph, positions, wlabels=True, save=True)
        return graph, positions
    elif save==False:
        return graph, positions


def loadGraph(path_to_graphDict:str=conf["graph"]["savePath_graph"]) -> Tuple[nx.DiGraph, dict]:
    ''' This function loads a graph and the corresponding positions from a .py file.
    
    Inputs:
    path_to_graphDict: a string representing the path, where the graph is saved including a filename and a file extension
    
    Output:
    graph: a graph object (type networkX.DiGraph) based on the dictionary saved in the path_to_graphDict
    postitions: a dictionary with the node names as keys and the positions as values '''

    # Check the type of the input
    typeCheck(func=loadGraph, locals=locals())

    # Check, if the path_to_graphDict corresponds to a file
    if Path(path_to_graphDict).is_file():
        # Load the dictionary representing the graph from the file
        graph_dict = loadVariable(loadPath=path_to_graphDict, variable='graph')
        # Cast the dictionary to a graph object
        graph = nx.from_dict_of_dicts(d=graph_dict, create_using=nx.DiGraph)
    else:
        raise ValueError(f"The given path to the graph {path_to_graphDict} does not correspond to a file.")
    
    # Check, if the path_to_graphDict corresponds to a file
    if Path(f"{str(path_to_graphDict.split('.')[0])}_positions.py").is_file():
        # Load the positions
        positions = loadVariable(loadPath=f"{str(path_to_graphDict.split('.')[0])}_positions.py", variable='graph_positions')
    else:
        raise ValueError(f"The given path to the positions {str(path_to_graphDict.split('.')[0])}_positions.py does not correspond to a file.")
    return graph, positions

def getGraph(graph:Union[str,dict,nx.DiGraph], positions:Union[dict, str, None]) -> Tuple[nx.DiGraph, dict]:
    ''' This function does a type check of the given graph and if it is not yet a graph object, it loads a graph object from the given file. If graph is of the wrong type
    or a given string does not correspond to a path to a file, a TypeError is raised.
    
    Inputs:
    graph: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a file, which contains a dict[dict] describing the graph.
    positions: a dictionary containing the names of the nodes as keys and their positions as values, or a string giving the path to a file, where the positions are saved,
               or None, which means the location of the positions file is inferred based on the path given as a string for graph.
    
    Outputs:
    graph: a graph object (type networkX.DiGraph) based on the inputs
    positions: a dictionary containing the positions of the nodes in the graph; node names are keys, positions are values '''

    # Check the input types
    typeCheck(func=getGraph, locals=locals())

    ## Get the graph
    # Do not change the graph, if it already is a graph object
    if isinstance(graph, nx.DiGraph):
        graph = graph
    # If the graph given is a string
    elif isinstance(graph, str):
        # check, if this string corresponds to a file
        if Path(graph).is_file():
            # if the string can be interpreted as a path to a file, load the graph from the respective file
            graph, positions = loadGraph(graph)
        else:
            # if the string is not a path to a file, raise a Value error
            raise ValueError(f"The given string {graph} does not correspond to a file.")
    # If the graph is a dictionary
    elif isinstance(graph, dict):
        # load the graph from the dictionary
        graph = nx.from_dict_of_dicts(graph, create_using=nx.DiGraph)
    else:
        # If graph is none of the above types, raise a TypeError
        raise TypeError(f'The type of the given graph {graph} is {type(graph)} instead of str, dict or nx.classes.digraph.DiGraph.')

    ## Get the positions
    # If the positions are given as a dictionary, they can be used directly
    if isinstance(positions, dict):
        positions = positions
    # If the positions are given as a string, check, if this string corresponds to the path to a file
    elif isinstance(positions, str):
        # If the string can be interpreted as a path, load the positions from there
        if Path(positions).is_file() and not (isinstance(graph, str) and Path(graph).is_file()):
            positions = loadVariable(loadPath=positions, variable='graph_positions')
        elif Path(positions).is_file() and (isinstance(graph, str) and Path(graph).is_file()):
            pass
        # Otherwise raise a ValueError
        else:
            # if the string is not a path to a file, raise a Value error
            raise ValueError(f"The given string {positions} does not correspond to a file.")
    # If None is given for the positions, but the graph variable is not a string, which can be interpreted as a path, raise a ValueError
    elif (positions == None) and not (isinstance(graph, str) and Path(graph).is_file()):
        raise ValueError(f"Since the given graph {graph} is not a valid path, the location of positions cannot be inferred.")

    return graph, positions

def findClosest(node:str, candidates:list, graph:Union[str,nx.DiGraph]=conf["graph"]["savePath_graph"], valvePositionDict:Union[str,dict]=conf["CetoniDeviceDriver"]["valvePositionDict"], weight:str="dead_volume", direction:str="out") -> Tuple[str, list]:
    ''' This function finds the closest candidate to a given node regarding a specified weight for the path. The direction of the search can be either
    incoming to the node (in) or outgoing from the node (out). The default is outgoing (out). The function returns the closest node among the given candidates
    and the path from the specified node to this candidate node. candidates is of type "list".
    
    Inputs:
    node: a string giving the name of the node, to which the closest candidate is searched
    candidates: a list of strings giving the names of the nodes, among which the closest one shall be found
    graph: a string giving the path to a file, from where the graph shall be loaded or a graph object
    valvePositionDict: a string to a file, from which the valvePositionDict can be loaded or a dictionary representing the valvePositionDict
    weight: a string naming the metric to use to find minimum distances
    direction: a string specifying, whether the given node shall be the starting point (out) or the end point (in) of the path
    
    Outputs:
    closest: a string giving the name of the closest node
    pathToClosest: a list of strings giving the nodes to pass on the shortest connection between the closest candidate and the node or vice versa depending on the
                   direction parameter '''

    ## Check the input types
    typeCheck(func=findClosest, locals=locals())

    # Get the graph object from the respective input

    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions = positionsName)
    # check valvePositionDict
    valvePositionDict = getValvePositionDict(valvePositionDict)
    # Put together a dataframe to store the path lengths
    startingData = np.zeros((len(candidates), 3), dtype=object)
    startingData[:,0] = candidates
    shortest_distances = pd.DataFrame(startingData, columns=["candidate", "shortestPathLength", "shortestPath"], dtype=object)
    # Calculate for each candidate the shortest path with respect to the given weight
    for candidate in candidates:
        # If the direction is outgoing from the node, check the paths starting from the node and ending in the candidate
        if direction=="out":
            try:
                # Get a valid path
                path_out = findPath(start_node=node, end_node=candidate, valvePositionDict=valvePositionDict, graph=graph, weight=weight)
                # Get the total weight of the path
                length_out = getTotalQuantity(nodelist=path_out, quantity=weight)
                # Store the values in the prepared dataframe
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPathLength"] = length_out
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPath"] = str(path_out)
            except (IndexError, nx.exception.NetworkXNoPath):   # https://stackoverflow.com/questions/6095717/python-one-try-multiple-except
                # Store infinite length and the string 'no path' in the prepared dataframe
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPathLength"] = np.inf
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPath"] = 'no path'
        # If the direction is incoming to the node, check the paths starting from the candidate and ending in the node
        elif direction=="in":
            try:
                # Get a valid path
                path_in = findPath(start_node=candidate, end_node=node, valvePositionDict=valvePositionDict, graph=graph, weight=weight)
                # Get the total weight of the path
                length_in = getTotalQuantity(nodelist=path_in, quantity=weight)
                # Store the values in the prepared dataframe
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPathLength"] = length_in
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPath"] = str(path_in)
            except (IndexError, nx.exception.NetworkXNoPath):   # https://stackoverflow.com/questions/6095717/python-one-try-multiple-except
                # Store infinite length and the string 'no path' in the prepared dataframe
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPathLength"] = np.inf
                shortest_distances.loc[shortest_distances["candidate"]==candidate, "shortestPath"] = 'no path'

    # Find the closest candidate in the dataframe
    closest = shortest_distances.loc[shortest_distances["shortestPathLength"]==min(shortest_distances["shortestPathLength"]), "candidate"].values[0]
    # Extract the path to the closest candidate from the dataframe
    pathToClosest = eval(shortest_distances.loc[shortest_distances["candidate"]==closest, "shortestPath"].values[0])
    return closest, pathToClosest

def findPathAB(start_node:str, end_node:str, valvePositionDict:Union[str,dict]=conf["CetoniDeviceDriver"]["valvePositionDict"], graph:Union[str, dict,nx.DiGraph]=conf["graph"]["savePath_graph"], weight:str="dead_volume") -> List[str]:
    ''' This function finds a path in the graph representing the setup. It uses the function "pathIsValid" to make sure that no more than two nodes belonging to the same
    valve are included in the path. If this condition is not met by the suggestion obtained by the Dijkstra algorithm, it removes connections in a copy of the graph until
    it finds a valid path. The path is searched from start_node to end_node.
    
    Inputs:
    start_node: a string giving the name of the node to start from
    end_node: a string giving the name of the node to end with
    valvePositionDict: a string giving the path to a file, from where to load the valvePositionDict, or a dictionary representing the valvePositionDict
    graph: a string giving the path to a file, from where the dictionary for the graph can be loaded, or a graph object or a dictionary representing the graph
    weight: a metric to minimize to find the shortest connection
    
    Outputs:
    selected_path: a list of strings representing the path with the minimum weight between the start_node and the end_node ''' # TODO: Add conditions for the path other than just minimal weight.

    ## Check the input types
    typeCheck(func=findPathAB, locals=locals())

    # Get the graph object from the respective input
    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions=positionsName)
    # Get the valvePositionDict from the respective input
    valvePositionDict = getValvePositionDict(valvePositionDict)
    # Find the initial path using the Dijkstra-algorithm.
    initial_path = nx.dijkstra_path(graph, start_node, end_node, weight=weight)
    # Get the valves for the nodes in the path
    valveList_orig = [getValveFromName(node, valvePositionDict) for node in initial_path]
    # Transfer the path to a pandas dataframe
    valveList = pd.DataFrame(valveList_orig)
    # Drop the NaN values originating from nodes not belonging to valves
    valveList = valveList.dropna()
    # Get number of occurences of each valve in valveList
    occurance = valveList.value_counts()    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.value_counts.html
    if pathIsValid(initial_path, valvePositionDict):
        # If the initial path is valid, return the path
        return initial_path
    else:
        # Transfer the initial path to a numpy array
        path = np.array(initial_path)
        # Generate an empty dataframe for the candidates for alternative paths
        candidate_graphs = pd.DataFrame(columns=["removed_edge", "new_graph", "new_path", "total_weight", "validity", "valveCount"])
        # Go through all entries in the occurance
        for occ in occurance:
            # If the occurance exceeds 2, meaning that one valve is contained more than two times in the graph
            if occ > 2:
                # For every occurance above 2, get the valve
                valves = occurance[occurance.values==occ].index
                for valv in valves:
                    # Get the index, where the original valve list has the valve
                    idx =  np.where(np.array(valveList_orig)==valv[0])
                    # Get the node at these indices in the path
                    nodeOcc = path[idx]
                    for j in range(len(nodeOcc)-1):
                        # For the the nodes identified in the path, copy the graph
                        new_graph = graph.copy()
                        # Remove one edge from the copied graph between the selected node and its subsequent node
                        new_graph.remove_edge(nodeOcc[j], nodeOcc[j+1])
                        # Save the start and end node of the removed edge
                        removed_edge = (nodeOcc[j], nodeOcc[j+1])
                        try:    # https://stackoverflow.com/questions/26059424/on-error-resume-next-in-python
                            # Try to find an alternative path in the new graph using the Dijkstra algorithm and calculate the relevant measures
                            new_path = nx.dijkstra_path(new_graph, start_node, end_node, weight)
                            total_weight = getTotalQuantity(nodelist=new_path, quantity=weight)
                            validity = pathIsValid(path=new_path, valvePositionDict=valvePositionDict)
                            valvesNewPath = pd.DataFrame([getValveFromName(node_name=nod, valvePositionDict=valvePositionDict) for nod in new_path]).dropna()
                            valveCount = valvesNewPath.shape[0]
                        except: #KeyError: TODO: Be more specific on the Type of error!!!
                            # If an error occurs, assume that no path could be found and set the measures accordingly
                            new_path = "noPath"
                            total_weight = np.inf
                            validity = False
                            valveCount = np.inf
                        # Put the relevant measures in a dataframe and name its columns according to the candidate_graphs dataframe
                        candidate = pd.DataFrame(data=np.array([removed_edge, new_graph, new_path, total_weight, validity, valveCount], dtype=object)).transpose()
                        candidate.columns=["removed_edge", "new_graph", "new_path", "total_weight", "validity", "valveCount"]
                        # Add the new candidate to the candidate_graphs dataframe
                        candidate_graphs = pd.concat([candidate_graphs, candidate], axis=0, ignore_index=True)
        # Select the row in the dataframe, which contains a valid path.
        selection = candidate_graphs.loc[(candidate_graphs["validity"]==True)]
        # If the selection is not empty
        if len(selection.index) != 0:
            # Among the valid paths select the one with minimum weight and subsequently the one with minimum valveCount.
            fineSelection = selection.loc[selection["total_weight"]==np.min(selection["total_weight"])]
        else:
            raise ValueError(f"No path is found between the nodes {start_node} and {end_node}.")
        if len(fineSelection.index) != 0:
            fineSelection = fineSelection.loc[selection["valveCount"]==np.min(selection["valveCount"])]
        else:
            raise ValueError(f"No path is found between the nodes {start_node} and {end_node}.")
        if len(fineSelection.index) != 0:
            # Get the path of one of the optimum valid paths
            selected_path = fineSelection.get("new_path").array[0]
            return selected_path
        else:
            raise ValueError(f"No path is found between the nodes {start_node} and {end_node}.")

def findPath(start_node:str, end_node:str, via:list=[], valvePositionDict:Union[str,dict]=conf["CetoniDeviceDriver"]["valvePositionDict"], graph:Union[str,nx.DiGraph]=conf["graph"]["savePath_graph"], weight:str="dead_volume") -> List[str]:
    ''' This function finds a path from the start node to the end node and if applicable passes the nodes given as a list in 'via' in the sequence given.

    Inputs:
    start_node: a string giving the name of the node to start from
    end_node: a string giving the name of the node to end with
    via: a list of strings representing the nodes to pass in the given sequence on the way
    valvePositionDict: a string giving the path to a file, from where to load the valvePositionDict, or a dictionary representing the valvePositionDict
    graph: a string giving the path to a file, from whre the dictionary for the graph can be loaded, or a graph object
    weight: a metric to minimize to find the shortest connection
    
    Outputs:
    totalPath: a list of strings representing the path with the minimum weight between the start_node and the end_node passing the nodes in via in the given order  '''

    # Check the input types
    typeCheck(func=findPath, locals=locals())

    ## If no additional nodes to pass are given, search for a path between start_node and end_node.
    # check, if no additional nodes are given
    if via == []:
        # call the function, which finds a path from start_node to end_node and return its result
        return findPathAB(start_node=start_node, end_node=end_node, valvePositionDict=valvePositionDict, graph=graph, weight=weight)
    else:
        ## If there are additional nodes, find a path to pass them all in the given order
        # add the start_node to the beginning of the list and the end_node to the end of the list
        nodesToPass = [start_node] + via + [end_node]
        # prepare a list to save the total path
        totalPath = []
        ## Find a path from each node in the list of nodes to pass to its successor and assemble the paths to the total path
        # iterate over all nodes that need to be passed
        for i in range((len(nodesToPass) - 1)):
            print(nodesToPass[i],nodesToPass[i+1])
            # get the path from this node to its successor
            path = findPathAB(start_node=nodesToPass[i], end_node=nodesToPass[i+1], valvePositionDict=valvePositionDict, graph=graph, weight=weight)
            # add this path to the total path omitting its end node
            totalPath.extend(path[:-1]) # https://stackoverflow.com/questions/252703/what-is-the-difference-between-pythons-list-methods-append-and-extend 
        # add the final end_node to the total Path, because it is omitted in the for-loop
        totalPath.append(end_node)
        ## Return the path, if it is valid
        if pathIsValid(totalPath):
            return totalPath
        # else raise a ValueError
        else:
            raise ValueError('No path is found, which passes all the nodes in the given order. Please check the requirements.')

def checkConsistency(path_nodes:str=conf["graph"]["pathNodes"], path_edges:str=conf["graph"]["pathEdges"], path_tubing:str=conf["graph"]["pathTubing"]) -> Tuple[bool, Union[bool, list], Union[bool, list]]:
    ''' This function checks, if the setup files for the graph are consistent. It checks, whether all the edges given in
    tubing.csv are contained in edges.csv and if all nodes referenced in tubing.csv are contained in nodes.csv. It returns
    three results for edgs and nods, edgs, and nods or edgs and nods, new_edges, new_nodes, depending on whether all nodes and edges in tubing are covered by the other
    two files or not.
    
    Inputs:
    path_nodes: a string giving the path to the .csv file, which contains the nodes and their positions
    path_edges: a string giving the path to the .csv file, which contains the available edges and their properties
    path_tubing: a string giving the path to the .csv file, which contains the tubing and the nodes, it connects
    
    Outputs:
    edgs and nods: a boolean value stating, whether the edges AND the nodes, which are in tubing.csv are also in the edges and nodes file, respectively
    edgs: a boolean value giving information, whether the edges in tubing.csv are also in edges.csv
    nods: a boolean value giving information, whether the nodes in tubing.csv are also in nodes.csv
    new_edges: a DataFrame listing the edges, which are in tubing.csv, but not in edges.csv
    new_nodes: a DataFrame listing the nodes, which are in tubing.csv, but not in nodes.csv '''

    # Read each file, for edges, nodes and tubing in to a Pandas DataFrame
    edges_frame = pd.read_csv(path_edges, sep=";")
    nodes_frame = pd.read_csv(path_nodes, sep=";")
    tubing_frame = pd.read_csv(path_tubing, sep=";")
    # Collect all the start_nodes and all the end_nodes from the tubing.csv file in a separate DataFrame with only one column
    tubing_nodes_frame = pd.concat([tubing_frame["start"], tubing_frame["end"]], axis=0)
    # Isolate all the edges from the tubing file in a new DataFrame
    tubing_edges_frame = tubing_frame["edge"]

    # Get a list of all available edges and one for the nodes
    edges = list(edges_frame["edge"])
    nodes = list(nodes_frame["node"])
    # Get lists for the edges and nodes from the tubing file
    edges_tubing = list(tubing_frame["edge"])
    nodes_tubing = list(tubing_nodes_frame)

    # Check, if all edges mentioned in the tubing file are present in the edges file
    edgs = all([edge in edges for edge in edges_tubing])
    # Check, if all nodes mentioned in the tubing file are present in the nodes file
    nods = all([node in nodes for node in nodes_tubing])

    # If all edges are in edges.csv and all nodes are in nodes.csv
    if (edgs and nods) and edgs and nods:
        # Return the result for each of the evaluations
        return edgs and nods, edgs, nods
    # Otherwise
    else:
        # Get the nodes and edges, which are in tubing.csv, but not in nodes.csv or edges.csv, respectively
        new_nodes = tubing_nodes_frame[[node not in nodes for node in nodes_tubing]]
        new_edges = tubing_edges_frame[[edge not in edges for edge in edges_tubing]]
        # Return the result for the evaluation of (edges and nodes) and the additional elements
        return edgs and nods, list(new_edges), list(new_nodes)

def appendEdge(edgeLst:list, edgeName:str, edgeNodes:pd.DataFrame, edgeProps:pd.DataFrame, reverse:bool=False) -> None:
    ''' This function adds an edge to a list of edges. The edge is defined according to the format required by the graph. Data is taken from pandas dataframes containing
    nodes and properties of the edges. If the option reverse is set to True, then the edge is considered to be undirected and the reverse edge is also added to the list.
    This enables the passage of the path in both directions while keeping the graph a directed graph.
    
    Inputs:
    edgeLst: a list, to which the edge shall be added
    edgeName: a string giving the name of the edge to look for in the DataFrames
    edgeNodes: a DataFrame containing information regarding which nodes are connected via which edge
    edgeProps: a DataFrame containing the properties of the edges
    reverse: a boolean stating, whether the edge is directed (False) or undirected (True)
    
    Outputs:
    This function has no outputs. '''
    
    # Check the input types
    typeCheck(func=appendEdge, locals=locals())
    
    # Append the new edge including the nodes it connects and the edge properties to the list of edges (edgeLst)
    edgeLst.append((edgeNodes.loc[edgeNodes["edge"] == edgeName, "start"].values[0], edgeNodes.loc[edgeNodes["edge"] == edgeName, "end"].values[0],
            {"name": edgeName, "designation": tuple((edgeNodes.loc[edgeNodes["edge"] == edgeName, "start"].values[0], edgeNodes.loc[edgeNodes["edge"] == edgeName, "end"].values[0])),
            "ends": edgeProps.loc[edgeProps["edge"] == edgeName, "ends"].values[0], "length": float(edgeProps.loc[edgeProps["edge"] == edgeName, "length"].values[0]), 
            "diameter": float(edgeProps.loc[edgeProps["edge"] == edgeName, "diameter"].values[0]), "dead_volume": float(edgeProps.loc[edgeProps["edge"] == edgeName, "dead_volume"].values[0]),
            "status": edgeProps.loc[edgeProps["edge"] == edgeName, "status"].values[0]}))
    # If the reverse parameter is True, add also the reverse of this edge. This is needed to specify some connections as directed to avoid paths in non-reasonable
    # directions are found
    if reverse == True:
        edgeLst.append((edgeNodes.loc[edgeNodes["edge"] == edgeName, "end"].values[0], edgeNodes.loc[edgeNodes["edge"] == edgeName, "start"].values[0],
            {"name": edgeName, "designation": tuple((edgeNodes.loc[edgeNodes["edge"] == edgeName, "end"].values[0], edgeNodes.loc[edgeNodes["edge"] == edgeName, "start"].values[0])),
            "ends": edgeProps.loc[edgeProps["edge"] == edgeName, "ends"].values[0], "length": float(edgeProps.loc[edgeProps["edge"] == edgeName, "length"].values[0]),
            "diameter": float(edgeProps.loc[edgeProps["edge"] == edgeName, "diameter"].values[0]), "dead_volume": float(edgeProps.loc[edgeProps["edge"] == edgeName, "dead_volume"].values[0]),
            "status": edgeProps.loc[edgeProps["edge"] == edgeName, "status"].values[0]}))

def drawGraph(graph:Union[str, dict, nx.DiGraph], positions:dict, wlabels:bool=True, save:bool =True) -> None:
    ''' This function draws and shows or saves a graph.
    
    Inputs:
    graph: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a  file, which contains a dict[dict]
           describing the graph
    positions: a dictionary containing the names of the nodes as keys and their positions as values
    wlabels: a boolean value specifying, whether the graph shall be plotted including labels for the nodes
    save: a boolean value specifying, whether the graph shall be saved. If this is true, the graph is saved, but now shown, otherwise it is only shown.

    Outputs:
    This function has no outputs. '''
    
    # Check input types
    typeCheck(func=drawGraph, locals=locals())

    # Get the graph object based on the input graph
    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions=positionsName)

    nx.draw(graph, pos=positions, with_labels=wlabels)
    if not save:
        plt.show()
    else:
        folder = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+['\\'])
        plt.savefig(fname=f"{folder}graphVisualized.png")

def getValveFromName(node_name:str, valvePositionDict:Union[str,dict]=conf["CetoniDeviceDriver"]["valvePositionDict"]) -> Union[str, None]:
    ''' This function takes a name of a node (as a string) as an input and returns the valve it belongs to. If the node does not belong to a valve. None is returned.
    
    Inputs:
    node_name: a string specifying the name of the node to check, to which valve it belongs.
    valvePositionDict: a string giving the path to a file, from where to load the valvePositionDict, or a dictionary representing the valvePositionDict
    
    Outputs:
    valve: a string giving the name of the valve, to which the node belongs or np.NaN, if the node does not belong to a valve '''

    ## Check input types
    typeCheck(func=getValveFromName, locals=locals())
    # Get the valvePositionDict
    valvePositionDict = getValvePositionDict(valvePositionDict)
    # Get the valve from the node name
    valve = node_name.split('.')[0]
    if valve in valvePositionDict.keys():
        # If valve corresponds to a valve, return it
        return valve
    else:
        # If the node does not belong to a valve, return NaN
        return np.NaN

def getEdgedictFromNodelist(nodelist:list, graph:Union[str, dict, nx.DiGraph]=conf["graph"]["savePath_graph"]) -> dict:
    ''' This function generates a dictionary of edges from a list of nodes.
    
    Inputs:
    nodelist: a list of node names
    graph: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a  file, which contains a dict[dict]
           describing the graph
    
    Output:
    edgeDict: a dictionary of the edges connecting the nodes in the list in the given sequence with the names of the edges as keys '''

    ## Chec input types
    typeCheck(func=getEdgedictFromNodelist, locals=locals())

    # Get the graph
    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions=positionsName)

    edgesDict = {}
    # Go through all the nodes in the nodelist
    for nd in nodelist:
        # If the node is not the last one in the list
        if (nodelist.index(nd)+1) < (len(nodelist)):
            # Assign the edge connecting this node and its subsequent one in the list to the name of the edge as a key in the edgeDict
            edgesDict[graph[nd][nodelist[nodelist.index(nd)+1]]["name"]] = graph[nd][nodelist[nodelist.index(nd)+1]]    # https://networkx.org/documentation/stable/reference/classes/generated/networkx.Graph.get_edge_data.html
    return edgesDict

def getTotalQuantity(nodelist:list, quantity:str) -> float:   # Corresponds to networkx.path_weight.
    ''' This function calculates a total quantity (e.g. dead volume) for a list of nodes.
    
    Inputs:
    nodelist: a list of node names
    quantity: a sting giving the quantity to sum up

    Outputs:
    quantityTotal: a float representing the sum of all the values for the given quantity in the edgeDict corresponding to the nodelist '''
    
    ## Check input types
    typeCheck(func=getTotalQuantity, locals=locals())

    # Get the edgeDict corresponding to the nodelist
    edgedict = getEdgedictFromNodelist(nodelist=nodelist)

    # Initialise quantityTotal as 0.0
    quantityTotal = 0.0
    # Go through all the edges in the edgedict
    for edg in edgedict.keys():
        # Add the value for the quantity for each edge to quantityTotal
        quantityTotal += edgedict[edg][quantity]
    return quantityTotal

def getValveSettings(nodelist:list, valvePositionDict:Union[str,dict]=conf["CetoniDeviceDriver"]["valvePositionDict"]):
    ''' This fuction returns the required settings of the valves needed to realise this path based on a list of nodes describing a path in the graph and a dict of valve
    positions, in case there are valves included in the path. Otherwise, an empty dict will be returned.
    
    Inputs:
    nodelist: a list of node names
    valvePositionDict: a string giving the path to a file, from where to load the valvePositionDict, or a dictionary representing the valvePositionDict
    
    Outputs:
    valveSettings: a dictionary with the valve names as keys and their required positions as values '''

    ## Check input types
    typeCheck(func=getValveSettings, locals=locals())

    # Get the valvePositionDict
    valvePositionDict = getValvePositionDict(valvePositionDict)

    valveSettings = {}
    # Go through all nodes in the nodelist
    for node in nodelist:
        # split the node at the '.' to separate the valve designation from the position
        valve_pos = node.split('.')
        # if the list after the split has two elements,
        if len(valve_pos) == 2:
            # the valve is the first element
            valve = valve_pos[0]
            # the position is the second element
            pos = valve_pos[1]
            # if the valve is in the keys of the valvePositionDict, (this excludes nodes, which are not valves)
            if valve in valvePositionDict.keys():
                # if the valve is already included in the valve settings and the position is not 0
                if (valve in valveSettings.keys()) and (pos != "0"):
                    # the valve is passed a second time, which leads to an invalid path -> raise an error
                    raise ValueError(f"This path {nodelist} is not valid, because it passes the same valve {valve} multiple times.")
                # if the position is non-zero,
                elif pos != "0":
                    # add the position to the valve settings for the respective valve
                    valveSettings[valve] = valvePositionDict[valve][node]
                # if the position is zero, but not for a rotary valve,
                elif ('V' not in valve) and (pos == '0'):
                    # add the position to the valve settings for the respective valve
                    valveSettings[valve] = valvePositionDict[valve][node]
                # if the valve is a rotary valve and the position is zero, skip it
                elif ('V' in valve) and (pos == "0"):
                    pass
        # if the length of valve_pos is not two, skip this node, because it is not a valve with a position
        else:
            pass
    # return the valve settings
    return valveSettings

def pathIsValid(path:list, valvePositionDict:Union[str,dict]=conf["CetoniDeviceDriver"]["valvePositionDict"]):
    ''' This function checks a given path regarding its validity. If the path does not pass more than two nodes belonging to the same valve, it is considered being valid.
    
    Inputs:
    path: a list of nodes describing a path
    valvePositionDict: a string giving the path to a file, from where to load the valvePositionDict, or a dictionary representing the valvePositionDict

    Outputs:
    validity: a boolean, which is True, if the path does not cross three nodes assigned to the same valve, or False, if it does. '''

    ## Check input types
    typeCheck(func=pathIsValid, locals=locals())

    # Get the valvePositionDict
    valvePositionDict = getValvePositionDict(valvePositionDict)
    
    # Get the valves from the node names and save them in a list.
    valveList_orig = [getValveFromName(node, valvePositionDict) for node in path]
    # Transfer list to pandas dataframe.
    valveList = pd.DataFrame(valveList_orig)
    # Remove NaN values from the dataframe. These values originate from nodes that do not belong to a valve.
    valveList = valveList.dropna()
    # Get number of occurences of each valve in valveList
    occurance = valveList.value_counts()    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.value_counts.html
    if any([occ > 2 for occ in occurance]):
        # If any valve occures more than two times, the path is invalid.
        return False
    else:
        # Else it is valid.
        return True

def getSystemStatus(path:list=[], full:bool=True, graph:Union[str, dict, nx.DiGraph]=conf["graph"]["savePath_graph"]) -> dict:
    ''' This function returns the status of all edges in the system. The output is a dictionary, which tells, if a certain edge is empty or filled with some liquid.
    If full is True, the status of all edges is returned, otherwise only the status of the edges in the requested path are returned.
    
    Inputs:
    path: a list of nodes describing a path
    full: a boolean indicating, whether the system status for the full setup shall be generated
    graph: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a  file, which contains a dict[dict]
           describing the graph

    Outputs:
    status: a dictionary with the name of the edges as keys and their status as values. '''

    ## Check input types
    typeCheck(func=getSystemStatus, locals=locals())

    # get the graph
    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions=positionsName)
    
    # Get the status of the full system
    statFull = nx.get_edge_attributes(graph, "status")    # https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.get_edge_attributes.html#networkx.classes.function.get_edge_attributes

    # If the status is requested for the full system
    if full:
        # The status corresponds to the status for each edge
        status = statFull
    # If the status is only requested for a certain path
    else:
        # Initialize the status
        status = {}
        # Get the edges involved in the relevant path
        edges = getEdgedictFromNodelist(nodelist=path, graph=graph)
        for edge in edges:
            # Assign the status for each edge in the path to a respective entry in the status dictionary
            status[edges[edge]["designation"]] = statFull[edges[edge]["designation"]]
    return status

def updateSystemStatus(path:list, graph:Union[str, dict, nx.DiGraph]=conf["graph"]["savePath_graph"]) -> None:
    ''' This function updates the status of edges in a path by setting the name of the start node of the path as the status of all involved edges.
    The resulting status can be requested using the getSystemStatus function.
    
    Inputs:
    path: a list of nodes describing a path
    graph: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a  file, which contains a dict[dict]
           describing the graph
    
    Outputs:
    This function has no outputs. '''

    ## Check input types
    typeCheck(func=updateSystemStatus, locals=locals())

    # Get the graph
    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions=positionsName)
    
    # Get the edges of the relevant path
    edges = getEdgedictFromNodelist(nodelist=path, graph=graph)
    # Go through all the edges in the graph
    for edge in edges.keys():
        # Assign the origin of the path as the new status for each edge
        graph.edges[edges[edge]["designation"]]["status"] = path[0]
        try:
            # Try to update the status for the edge in the opposite direction in order to keep the status matching for the same edge
            graph[edges[edge]["designation"][1]][edges[edge]["designation"][0]]["status"] = path[0]
        except KeyError:
            # If there is no edge in the opposite direction, continue
            pass

# TODO: Move to CetoniDevice_driver
# def findPumps(pumps:dict, **conditions:str) -> dict:
#     ''' This function searches for a pump according to criteria given as arguments. The returned dictionary has the pump names as keys and the pump objects (pumpObj) as
#     values.
#     The conditions are kwargs and must be of the format: key=column label in the dataframe (one of ["pumpName", "pump", "maximumVolume", "minimumVolume", "status"]),
#     value contains the condition to meet.
#     Secondary filtering requirements can be given in a key "secondary" in the conditions, which contains a dict. The keys of this dict must match the column names
#     in the dataframe (one of ["pumpName", "pump", "maximumVolume", "minimumVolume", "status"]) and the values must be functions like np.min or np.max.
    
#     Inputs:
#     pumps: a dictionary containing pump objects
#     conditions: kwargs of with keys ["pumpName", "pump", "maximumVolume", "minimumVolume", "status"] and values as np.min or np.max.

#     Outputs:
#     output: a dictionary of pumps, which fulfil the requirements '''

#     ## Check input types
#     typeCheck(func=findPumps, locals=locals())

#     # TODO: Test this function!!!
#     # Gather the current information on all the pumps and their syringes
#     pump_candidates = pd.DataFrame(columns=["pumpName", "pump", "maximumVolume", "minimumVolume", "status"])
#     for pum in list(pumps.keys()):
#         pcand = pd.DataFrame(data=np.array([pumps[pum].name, pumps[pum], pumps[pum].get_volume_max(), pumps[pum].syringe.minimum_volume_mL, pumps[pum].status], dtype=object)).transpose()
#         pcand.columns = ["pumpName", "pump", "maximumVolume", "minimumVolume", "status"]
#         pump_candidates = pd.concat([pump_candidates, pcand], axis=0, ignore_index=True)
#     print(pump_candidates)
#     # Initialise the found pumps as all candidates
#     foundPumps = pump_candidates.copy()
#     # Go through all the conditions keys
#     for key in conditions.keys():
#         if key != "secondary":
#             # Define the target column, which is supposed to fulfill the respective condition. The label of the target column corresponds to the respective key of the condition
#             target = foundPumps[key]
#             # Filter foundPumps according to the condition at key. The evaluation uses the target definition from above
#             foundPumps = foundPumps.loc[eval(conditions[key])]
#     # If there are secondary conditions given (must be a dict type), meaning if there is a key named "secondary" in conditions
#     if "secondary" in conditions.keys():
#         # Go through all the keys in the secondary conditions
#         for secKey in conditions["secondary"].keys():
#             # Filter according to the secondary conditions
#             foundPumps = foundPumps.loc[foundPumps[secKey]==conditions["secondary"][secKey](foundPumps[secKey])]
#     # If there are no results remaining in foundPumps, print a message
#     if len(foundPumps)==0:
#         raise ValueError(f"No pump fulfills the requirements {conditions}.")
#     # Reset the index of the resulting filtered dataframe
#     foundPumps = foundPumps.reset_index()
#     # Get the pumps column of the filtered dataframe and choose the element at index 0
#     foundPumps = foundPumps.get("pump").array
#     # Bring foundPumps into dict format for output
#     output = {}
#     for p in foundPumps:
#         output[p.name] = p
#     # Return the dictionary of the found pumps
#     return output

def findCandidate(candidates:dict, **conditions:str) -> dict:
    ''' This function searches for a candidate according to criteria given as arguments. The returned dictionary has the candidate names as keys and the candidate objects as
    values.
    The conditions are kwargs and must be of the format: key= attribute (column label in the dataframe), value contains the condition to meet.
    Secondary filtering requirements can be given in a key "secondary" in the conditions, which contains a dict. The keys of this dict must match the attributes of the candidate
    objects (column names in the dataframe) and the values must be callable functions, like np.min or np.max.
    
    Inputs:
    candidates: a dictionary containing candidate objects with the keys being the names of the objects (each object needs to have a name attribute)
    conditions: kwargs with keys as the attribute and values as callable functions, like np.min or np.max.

    Outputs:
    output: a dictionary of candidate objects, which fulfil the requirements '''

    ## Check input types
    typeCheck(func=findCandidate, locals=locals())

    # Get the attributes of the candidates
    attributes = list(vars(candidates[list(candidates.keys())[0]]).keys())

    # Gather the current information on all the pumps and their syringes
    cols = ['candidate_key', 'candidate']+attributes
    candidatesDF = pd.DataFrame(columns=cols)
    for cand in list(candidates.keys()):
        candDF = pd.DataFrame(data=np.array([cand, candidates[cand]]+[getattr(candidates[cand], i) for i in attributes], dtype=object)).transpose()
        candDF.columns = cols
        candidatesDF = pd.concat([candidatesDF, candDF], axis=0, ignore_index=True)
    # Initialise the found candidates as all candidates
    foundCandidates = candidatesDF.copy()
    # Go through all the conditions keys
    for key in conditions.keys():
        if key != "secondary":
            # Filter foundCandidates according to the condition at key. The evaluation uses the label of the target column corresponding to the respective key of the condition definition from above.
            foundCandidates = foundCandidates.loc[foundCandidates[key]==conditions[key](foundCandidates[key])]
    # If there are secondary conditions given (must be a dict type), meaning if there is a key named "secondary" in conditions
    if "secondary" in conditions.keys():
        # Go through all the keys in the secondary conditions
        for secKey in conditions["secondary"].keys():
            # Filter according to the secondary conditions
            foundCandidates = foundCandidates.loc[foundCandidates[secKey]==conditions["secondary"][secKey](foundCandidates[secKey])]
    # If there are no results remaining in foundCandidates, raise an error
    if len(foundCandidates)==0:
        raise ValueError(f"No candidate fulfills the requirements {conditions}.")
    # Set the candidate_key as index of the resulting filtered dataframe
    foundCandidates = foundCandidates.set_index('candidate_key')
    # Bring foundCandidates into dict format for output
    output = {}
    for k in foundCandidates.index:
        output[k] = foundCandidates.at[k, 'candidate']
    # Return the dictionary of the found candidates
    return output


def getOpenEnds(graph:Union[str, dict, nx.DiGraph]=conf["graph"]["savePath_graph"]) -> list:
    ''' This function finds the open ends in a graph. An open end is characterized by either the lack of incoming or outgoing edges or they have only one other node,
    they are connected to with an incoming and an outgoing edge. Since the graph is directed, but allows for bidirectional connections, some edges are added twice to
    cover both directions. Hence, an open end has two edges with the same label or is lacking either the incoming or the outgoing or both kinds of edges. The function
    returns a list of the nodes, which are open ends.
    
    Inputs:
    graph: a string, dictionary or a DiGraph object. If a string is given, this string should represent the path to a  file, which contains a dict[dict]
           describing the graph

    Outputs:
    openEnds: a list of nodes representing open ends in the graph '''

    # ensure that graph is a graph
    positionsFile = conf['graph']['savePath_graph'].split('\\')[-1].split('.')[0]
    positionsName = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+[positionsFile])
    positionsName = f"{positionsName}_positions.py"
    graph, positions = getGraph(graph, positions=positionsName)

    # initialise the list to collect the open edges
    openEnds = []

    ## Find all nodes with degree 2 or less
    # get all the degrees for all nodes in the graph
    degrees = pd.DataFrame(columns=['node', 'in_degree', 'out_degree', 'total_degree'])
    degrees.set_index('node', inplace=True)
    for n in graph.nodes:
        # assemble all the degrees for one node in a dataframe
        degree_node = pd.DataFrame(columns=['node', 'in_degree', 'out_degree', 'total_degree'])
        degree_node.at[0,'node'] = n
        degree_node.at[0, 'in_degree'] = graph.in_degree(n)
        degree_node.at[0, 'out_degree'] = graph.out_degree(n)
        degree_node.at[0, 'total_degree'] = graph.in_degree(n) + graph.out_degree(n)
        degree_node.set_index('node', inplace=True)
        # append this dataframe to the total dataframe collecting the data for all the nodes
        degrees = pd.concat([degrees, degree_node], axis=0)

    # Initialize the list of open ends to populate it
    openEnds = []

    ## Open ends either lack incoming or outgoing edges or they have only one other node, they are connected to with an incoming and an outgoing edge
    # Get the nodes with no incoming edges
    noIn = list(degrees.loc[degrees['in_degree']==0].index)
    # Add all nodes without incoming edges to the open ends
    openEnds.extend(noIn)
    # Get the nodes with no outgoing edges
    noOut = list(degrees.loc[degrees['out_degree']==0].index)
    # Add all nodes without outgoing edges to the open ends
    openEnds.extend(noOut)

    ## Get the nodes with connections to only on neighbour
    # Get all the nodes with only two edges connected and the number of incoming edges equals the outcoming edges
    degrees2 = degrees.loc[(degrees['total_degree']==2) & (degrees['in_degree']==degrees['out_degree'])]
    for n in degrees2.index:
        # append the node to the list of open ends, if the name of its incoming edge equals its outgoing edge
        if list(graph.out_edges(n))[0] == (list(graph.in_edges(n))[0][1], list(graph.in_edges(n))[0][0]):
            openEnds.append(n)
    
    # Get rid of duplicated entries, which fulfil several criteria
    openEnds = list(pd.Series(openEnds).unique())
    return openEnds
