from ASAB.test.FilesForTests import config_test
conf = config_test.config

import networkx as nx
import pandas as pd
import numpy as np
from os import remove
from pathlib import Path
from pytest import raises
from matplotlib.pyplot import savefig
from matplotlib.testing import compare

from ASAB.utility import graph
from ASAB.utility.helpers import loadVariable
from ASAB.driver.CetoniDevice_driver import loadValvePositionDict
from ASAB.driver.CetoniDevice_driver import cetoni


print("\n Test of functions in graph.py. \n")

def test_generateGraph():
    
    path_nodes=conf["graph"]["pathNodes"]
    path_edges=conf["graph"]["pathEdges"]
    path_tubing=conf["graph"]["pathTubing"]
    save_path=conf["graph"]["savePath_graph"]

    # Delete the graph file and the positions file, if they are already in the target directory to avoid them being checked instead of the newly created ones
    if Path(conf['graph']['savePath_graph']).is_file():
        remove(conf['graph']['savePath_graph'])
    if Path(conf['test_graph']['positions']).is_file():
        remove(conf['test_graph']['positions'])

    ### Check the graph

    # Get the target graph
    graph_target = loadVariable(loadPath=conf['test_graph']['graph_target'], variable='graph')

    # Get the test object
    graph_result, positions_result = graph.generateGraph(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing, show=False, save=True, save_path=save_path)

    # Make sure, that the graph file was created as expected
    assert Path(conf['graph']['savePath_graph']).is_file(), f"The graph file was not created in the expected location {conf['graph']['savePath_graph']}."

    # Ensure, that the graph is of type nx.DiGraph
    assert type(graph_result) == nx.DiGraph, f"The type of the graph is {type(graph_result)} instead of networkx.DiGraph."
    
    # Check each entry in the dict of the graphs
    for k in graph_target:
        assert graph_target[k] == nx.to_dict_of_dicts(graph_result)[k], f"The entry {k} is {nx.to_dict_of_dicts(graph_result)[k]} instead of {graph_target[k]}."

    # Check positions.
    positions_target = pd.read_csv(conf["graph"]["pathNodes"], sep=';')
    positions_target = positions_target.set_index('node')

    for n in positions_target.index:
        # Get a tuple from the position in the dataframe
        position_target = tuple([float(pos) for pos in positions_target.loc[n, 'position_node'].strip('()').split(',')])

        # Check for each node in the nodes file, that the position matches the one in the graph; a space needs to be added after the comma, so that the strings are equal.
        assert position_target == positions_result[n], f"The node {n} has position {positions_result[n]} instead of {position_target}."

def test_loadGraph():
    # get the target graph
    graph_target = nx.from_dict_of_dicts(loadVariable(loadPath=conf['test_graph']['graph_target'], variable='graph'), create_using=nx.DiGraph)
    positions_target = loadVariable(loadPath=conf['test_graph']['positions'], variable='graph_positions')

    # get the result of the loadGraph function
    graph_result, positions_result = graph.loadGraph(conf['graph']['savePath_graph'])

    # Ensure, that the graph is of type nx.DiGraph
    assert type(graph_result) == nx.DiGraph, f"The type of the graph is {type(graph_result)} instead of networkx.DiGraph."

    # Assert, that all nodes are the same
    for i in range(len(graph_target.nodes)):
        assert list(graph_target.nodes)[i] == list(graph_result.nodes)[i], f"The node with index {i} is {list(graph_result.nodes)[i]} instead of {list(graph_target.nodes)[i]}."

    # Assert, that all edges are the same
    for j in range(len(graph_target.edges)):
        assert list(graph_target.edges)[j] == list(graph_result.edges)[j], f"The edge with index {j} is {list(graph_result.edges)[j]} instead of {list(graph_target.edges)[j]}."

    # Assert, that the loaded positions are correct
    for k in positions_target.keys():
        assert positions_target[k] == positions_result[k], f"The position of {k} is {positions_result[k]} instead of {positions_target[k]}."

def test_getGraph():
    # get the target graph
    graph_target = nx.from_dict_of_dicts(loadVariable(loadPath=conf['test_graph']['graph_target'], variable='graph'), create_using=nx.DiGraph)
    positions_target = loadVariable(loadPath=conf['test_graph']['positions'], variable='graph_positions')

    ## Get graph from a graph positions as str
    graph_graph_result, positions_graph_result = graph.getGraph(graph=graph_target, positions=conf['test_graph']['positions'])
    # Assert, that a DiGraph object is returned
    assert type(graph_graph_result) == nx.DiGraph, f"The type of the graph is {type(graph_graph_result)} instead of networkx.DiGraph"
    # Assert, that all nodes are the same
    for i in range(len(graph_target.nodes)):
        assert list(graph_target.nodes)[i] == list(graph_graph_result.nodes)[i], f"The node with index {i} is {list(graph_graph_result.nodes)[i]} instead of {list(graph_target.nodes)[i]}."
    # Assert, that all edges are the same
    for j in range(len(graph_target.edges)):
        assert list(graph_target.edges)[j] == list(graph_graph_result.edges)[j], f"The edge with index {j} is {list(graph_graph_result.edges)[j]} instead of {list(graph_target.edges)[j]}."
    # Assert the correct positions
    for k in positions_target.keys():
        assert positions_target[k] == positions_graph_result[k], f"The position of node {k} is {positions_graph_result[k]} instead of {positions_target[k]}."

    # get the graph from a string
    graph_str_result, positions_str_result = graph.getGraph(graph=conf['test_graph']['graph_target'], positions=conf['test_graph']['positions'])
    # Assert, that a DiGraph object is returned
    assert type(graph_str_result) == nx.DiGraph, f"The type of the graph is {type(graph_str_result)} instead of networkx.DiGraph"
    # Assert, that all nodes are the same
    for l in range(len(graph_target.nodes)):
        assert list(graph_target.nodes)[l] == list(graph_str_result.nodes)[l], f"The node with index {l} is {list(graph_str_result.nodes)[l]} instead of {list(graph_target.nodes)[l]}."
    # Assert, that all edges are the same
    for m in range(len(graph_target.edges)):
        assert list(graph_target.edges)[m] == list(graph_str_result.edges)[m], f"The edge with index {m} is {list(graph_str_result.edges)[m]} instead of {list(graph_target.edges)[m]}."
    # Assert the correct positions
    for n in positions_target.keys():
        assert positions_target[n] == positions_graph_result[n], f"The position of node {n} is {positions_graph_result[n]} instead of {positions_target[n]}."

    # get the graph from a dictionary
    g = loadVariable(loadPath=conf['test_graph']['graph_target'], variable='graph')
    graph_dict_result, positions_dict_result = graph.getGraph(graph=g, positions=conf['test_graph']['positions'])
    # Assert, that a DiGraph object is returned
    assert type(graph_dict_result) == nx.DiGraph, f"The type of the graph is {type(graph_dict_result)} instead of networkx.DiGraph"
    # Assert, that all nodes are the same
    for o in range(len(graph_target.nodes)):
        assert list(graph_target.nodes)[o] == list(graph_dict_result.nodes)[o], f"The node with index {o} is {list(graph_dict_result.nodes)[o]} instead of {list(graph_target.nodes)[o]}."
    # Assert, that all edges are the same
    for p in range(len(graph_target.edges)):
        assert list(graph_target.edges)[p] == list(graph_dict_result.edges)[p], f"The edge with index {p} is {list(graph_dict_result.edges)[p]} instead of {list(graph_target.edges)[p]}."
    # Assert the correct positions
    for q in positions_target.keys():
        assert positions_target[q] == positions_graph_result[q], f"The position of node {q} is {positions_graph_result[q]} instead of {positions_target[q]}."

    # wrong string graph
    with raises(ValueError):
        graph.getGraph(graph="This is not a path.", positions=conf['test_graph']['positions'])

    # wrong type of graph variable
    with raises(TypeError):
        graph.getGraph(graph=123, positions=conf['test_graph']['positions'])

    # graph as graph, but None for positions
    with raises(ValueError):
        graph.getGraph(graph=g, positions=None)

    # graph as string and None for positions
    graph_strStr_result, positions_strStr_result = graph.getGraph(graph=conf['test_graph']['graph_target'], positions=None)
    # Assert, that a DiGraph object is returned
    assert type(graph_strStr_result) == nx.DiGraph, f"The type of the graph is {type(graph_strStr_result)} instead of networkx.DiGraph"
    # Assert, that all nodes are the same
    for r in range(len(graph_target.nodes)):
        assert list(graph_target.nodes)[r] == list(graph_strStr_result.nodes)[r], f"The node with index {r} is {list(graph_strStr_result.nodes)[r]} instead of {list(graph_target.nodes)[r]}."
    # Assert, that all edges are the same
    for s in range(len(graph_target.edges)):
        assert list(graph_target.edges)[s] == list(graph_strStr_result.edges)[s], f"The edge with index {s} is {list(graph_strStr_result.edges)[s]} instead of {list(graph_target.edges)[s]}."
    # Assert the correct positions
    for t in positions_target.keys():
        assert positions_target[t] == positions_strStr_result[t], f"The position of node {t} is {positions_strStr_result[t]} instead of {positions_target[t]}."

def test_findClosest():
    # get the graph
    graph_to_check, positions_to_check = graph.loadGraph(path_to_graphDict=conf['test_graph']['graph_target'])

    # get the inpust for the function from the configuration file
    node = conf["test_graph"]["findClosest"]["node"]
    candidates = conf["test_graph"]["findClosest"]["candidates"]

    # get the target node from the configuration file
    closest_target = conf["test_graph"]["findClosest"]["closest_target"]
    pathToClosest_target = conf["test_graph"]["findClosest"]["pathToClosest_target"]

    # use the function to get the results
    closest_result, pathToClosest_result = graph.findClosest(graph=graph_to_check, node=node, candidates=candidates, weight="dead_volume", direction="in")
 
    assert closest_target==closest_result, f'The closest node found in the graph is {closest_result}, but the target is {closest_target}.'
    assert pathToClosest_target==pathToClosest_result, f'The oath to the closest node found in the graph is {pathToClosest_result}, but the target is {pathToClosest_target}.'

def test_findPathAB():
    # get the target path
    pathAB_target = conf["test_graph"]["findClosest"]["pathToClosest_target"]

    # find the path
    pathAB_result = graph.findPathAB(start_node=conf["test_graph"]["findClosest"]["closest_target"], end_node=conf["test_graph"]["findClosest"]["node"])
    # check the type of the found path
    assert type(pathAB_result) == list, f"The type of the obtained path is {type(pathAB_result)} instead of list."

    assert pathAB_target == pathAB_result, f"The found path is {pathAB_result} instead of {pathAB_target}."

def test_findPath():
    ## No additional nodes

    # get the target path
    path_direct_target = conf["test_graph"]["findPath"]["path_direct_target"]

    # find the path
    path_direct_result = graph.findPath(start_node=conf["test_graph"]["findPath"]["start_node"], end_node=conf["test_graph"]["findPath"]["end_node"], via=[])
    # check the type of the found path
    assert type(path_direct_result) == list, f"The type of the obtained path is {type(path_direct_result)} instead of list."
    print(path_direct_result)
    assert path_direct_target == path_direct_result, f"The found path is {path_direct_result} instead of {path_direct_target}."

    ## With additional nodes
    # get the target path
    path_via_target = conf["test_graph"]["findPath"]["path_via_target"]

    # find the path
    path_via_result = graph.findPath(start_node=conf["test_graph"]["findPath"]["start_node"], end_node=conf["test_graph"]["findPath"]["end_node"], via=conf["test_graph"]["findPath"]["via"])
    # check the type of the found path
    assert type(path_via_result) == list, f"The type of the obtained path is {type(path_via_result)} instead of list."
    print(path_via_result)
    assert path_via_target == path_via_result, f"The found path is {path_via_result} instead of {path_via_target}."

def test_checkConsistency():
    # get the paths from the configuration file
    path_nodes = conf["test_graph"]["checkConsistency"]["path_nodes"]
    path_edges = conf["test_graph"]["checkConsistency"]["path_edges"]
    path_tubing_match = conf["test_graph"]["checkConsistency"]["path_tubing_match"]
    path_tubing_additionalNode = conf["test_graph"]["checkConsistency"]["path_tubing_newNode"]
    path_tubing_additionalEdge = conf["test_graph"]["checkConsistency"]["path_tubing_newEdge"]
    path_tubing_additionalEdgeAndNode = conf["test_graph"]["checkConsistency"]["path_tubing_newEdgeAndNode"]

    edges = pd.read_csv(path_edges, sep=";")
    nodes = pd.read_csv(path_nodes, sep=";")
    
    ## Matching .csv files
    tubing = pd.read_csv(path_tubing_match, sep=";")
    tubing_nodes = pd.concat([tubing["start"], tubing["end"]], axis=0)
    nods = list(tubing_nodes)
    tube_node_ref = all([node in list(nodes["node"]) for node in nods])
    tube_edge_ref = all([edge in list(edges["edge"]) for edge in list(tubing["edge"])])
    total_ref = tube_edge_ref and tube_node_ref

    total_result, tube_edge_result, tube_node_result = graph.checkConsistency(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing_match)

    results = [tube_edge_ref, tube_edge_result, tube_node_ref, tube_node_result, total_ref, total_result]
    for res in results:
        assert type(res) == bool

    assert tube_edge_ref == tube_edge_result, f"The consistency of the matching edges is {tube_edge_result} instead of {tube_edge_ref}."
    assert tube_node_ref == tube_node_result, f"The consistency of the matching nodes is {tube_node_result} instead of {tube_node_ref}."
    assert total_ref == total_result, f"The total consistency of the matching scenario is {total_result} instead of {total_ref}."

    ## New node
    tubing2 = pd.read_csv(path_tubing_additionalNode, sep=";")
    tubing_nodes2 = pd.concat([tubing2["start"], tubing2["end"]], axis=0)
    nods2 = list(tubing_nodes2)
    tube_node_ref2 = all([node in list(nodes["node"]) for node in nods2])
    tube_edge_ref2 = all([edge in list(edges["edge"]) for edge in list(tubing2["edge"])])
    total_ref2 = tube_edge_ref2 and tube_node_ref2

    total_result2, tube_edge_result2, tube_node_result2 = graph.checkConsistency(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing_additionalNode)

    results = [tube_edge_ref2, tube_node_ref2, total_ref2, total_result2]
    for res in results:
        assert type(res) == bool

    for res in [tube_edge_result2, tube_node_result2]:
        assert type(res) == list

    assert 0 == len(tube_edge_result2), f"The consistency of the additional node edges is {tube_edge_result2} instead of 0."
    for l in range(len(tube_node_result2)):
        assert ['ZZ'][l] == tube_node_result2[l], f"The consistency of the  additional node nodes is {tube_node_result2} instead of ['ZZ']."
    assert total_ref2 == total_result2, f"The total consistency of the  additional node scenario is {total_result2} instead of {total_ref2}."

    ## New edge
    tubing3 = pd.read_csv(path_tubing_additionalEdge, sep=";")
    tubing_nodes3 = pd.concat([tubing3["start"], tubing3["end"]], axis=0)
    nods3 = list(tubing_nodes3)
    tube_node_ref3 = all([node in list(nodes["node"]) for node in nods3])
    tube_edge_ref3 = all([edge in list(edges["edge"]) for edge in list(tubing3["edge"])])
    total_ref3 = tube_edge_ref3 and tube_node_ref3

    total_result3, tube_edge_result3, tube_node_result3 = graph.checkConsistency(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing_additionalEdge)

    results = [tube_edge_ref3, tube_node_ref3, total_ref3, total_result3]

    for res in results:
        assert type(res) == bool

    for res in [tube_edge_result3, tube_node_result3]:
        assert type(res) == list

    for k in range(len(tube_edge_result3)):
        assert ['1234-CC-6'][k] == tube_edge_result3[k], f"The consistency of the additional edge edges is {tube_edge_result3} instead of ['1234-CC-6']."
    assert 0 == len(tube_node_result3), f"The consistency of the additional edge nodes is {tube_node_result3} instead of {tube_node_ref3}."
    assert total_ref3 == total_result3, f"The total consistency of the additional edge scenario is {total_result3} instead of {total_ref3}."

    ## New edge and new node
    tubing4 = pd.read_csv(path_tubing_additionalEdgeAndNode, sep=";")
    tubing_nodes4 = pd.concat([tubing4["start"], tubing4["end"]], axis=0)
    nods4 = list(tubing_nodes4)
    tube_node_ref4 = all([node in list(nodes["node"]) for node in nods4])
    tube_edge_ref4 = all([edge in list(edges["edge"]) for edge in list(tubing4["edge"])])
    total_ref4 = tube_edge_ref4 and tube_node_ref4

    total_result4, tube_edge_result4, tube_node_result4 = graph.checkConsistency(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing_additionalEdgeAndNode)

    results = [tube_edge_ref4, tube_node_ref4, total_ref4, total_result4]
    for res in results:
        assert type(res) == bool

    for res in [tube_edge_result4, tube_node_result4]:
        assert type(res) == list

    for i in range(len(tube_edge_result4)):
        assert ['1234-WW-5', '1245-UU-9'][i] == tube_edge_result4[i], f"The consistency of the additional edge and nodes edges is {tube_edge_result4} instead of ['1234-WW-5', '1245-UU-9']."
    for j in tube_node_result4:
        assert j in ['ZZ', 'XY', 'UV', 'AA'], f"The node {j} in the additional edge and node scenario is in {tube_node_result4} but not in ['ZZ', 'XY', 'UV', 'AA']."
    assert total_ref4 == total_result4, f"The total consistency of the additional edge scenario is {total_result4} instead of {total_ref4}."

def test_appendEdge():
    # get the inputs from the configuration
    edgeName = conf['test_graph']['appendEdge']['edgeName']
    edgeNodes = pd.read_csv(conf["test_graph"]["checkConsistency"]["path_tubing_match"], sep=';')
    edgeProps = pd.read_csv(conf["test_graph"]["checkConsistency"]["path_edges"], sep=";")
    
    # Directed edge (not adding both directions)
    edgelst_directed_target = [("V1.1", "Reservoir1", {"name": "0488-CC-2", "designation": ("V1.1", "Reservoir1"), "ends": "CC", "length": float(488), "diameter": float(0.3), "dead_volume": float(0.0345), "status": "empty"})]
    edgelst_directed_result = []
    graph.appendEdge(edgeLst=edgelst_directed_result, edgeName=edgeName, edgeNodes=edgeNodes, edgeProps=edgeProps, reverse=False)
    assert edgelst_directed_target == edgelst_directed_result, f"The resulting edge list is {edgelst_directed_result} instead of {edgelst_directed_target}."

    # Undirected edge (adding both directions)
    edgelst_undirected_target = [("V1.1", "Reservoir1", {"name": "0488-CC-2", "designation": ("V1.1", "Reservoir1"), "ends": "CC", "length": float(488), "diameter": float(0.3), "dead_volume": float(0.0345), "status": "empty"}), ("Reservoir1", "V1.1", {"name": "0488-CC-2", "designation": ("Reservoir1", "V1.1"), "ends": "CC", "length": float(488), "diameter": float(0.3), "dead_volume": float(0.0345), "status": "empty"})]
    edgelst_undirected_result = []
    graph.appendEdge(edgelst_undirected_result, edgeName, edgeNodes, edgeProps, reverse=True)
    assert edgelst_undirected_target == edgelst_undirected_result, f'The edgelist is {edgelst_undirected_result} instead of {edgelst_undirected_target}.'

def test_drawGraph():
    # Get the folder where to save the images and the filename for the test and target graphs
    folder = '\\'.join(conf['graph']['savePath_graph'].split('\\')[:-1]+['\\'])
    filename_test = f"{folder}graph_test.png"
    filename_target = f"{folder}graph_target.png"

    # Delete the graph image files, if they are already in the target directory to avoid them being checked instead of the newly created ones
    if Path(filename_test).is_file():
        remove(filename_test)
    if Path(filename_target).is_file():
        remove(filename_target)

    # Generate test graph and the respective positions.
    graph_test, positions_test = graph.loadGraph(path_to_graphDict=conf['test_graph']['graph_target'])

    plot3 = nx.draw(graph_test, pos=positions_test, with_labels=True)#, node_color="g", node_shape="^", node_size=600, alpha=0.6)  # node_color, node_shape, node_size and alpha according to https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html#networkx.drawing.nx_pylab.draw_networkx
    plot4 = graph.drawGraph(graph=graph_test, positions=positions_test, save=True, wlabels=True)

    # Save the images
    savefig(fname=filename_test)
    savefig(fname=filename_target)

    # compare the saved graphs
    x = compare.compare_images(f"{folder}graph_target.png", f"{folder}graph_test.png", tol=0)
    assert x == None, f'The result of the image comparison is {x} instead of None.'

def test_getValveFromName():
    valves_target = conf["test_graph"]["valves"]
    valveNames = conf["test_graph"]["valveNames"]

    valves_result = []
    for name in valveNames:
        valve = graph.getValveFromName(node_name=name, valvePositionDict=loadValvePositionDict(conf["graph"]["saveNameValvePositionDict"]))
        valves_result.append(valve)

    assert valves_target == valves_result, f'The list of valves is {valves_result} instead of {valves_target}.'

def test_getEdgedictFromNodelist():
    # Get the test graph
    graph_test, positions_test=graph.loadGraph(path_to_graphDict=conf['test_graph']['graph_target'])

    # Get the node list and the target edgeDict
    nodelst = conf["test_graph"]["nodelist"]
    edgeDict_target = conf["test_graph"]["edgeDict_target"]
    
    edgeDict_result = graph.getEdgedictFromNodelist(graph=graph_test, nodelist=nodelst)
    print(edgeDict_result)
    assert edgeDict_target == edgeDict_result, f'The edgeDict is {edgeDict_result} instead of {edgeDict_target}.'

def test_getTotalQuantity():
    # Get the nodelist, the quantity and its target value
    nodelst = conf["test_graph"]["nodelist"]
    quantity = conf["test_graph"]['quantity']
    totalQuantity_target = conf["test_graph"]['totalQuantity_target']

    totalQuantity_result = graph.getTotalQuantity(nodelist=nodelst, quantity=quantity)
    assert np.isclose(totalQuantity_result, totalQuantity_target, 0.00001), f"The total {quantity} is {totalQuantity_result} instead of {totalQuantity_target}."

# TODO: fix this test
def test_getValveSettings():

    ### A valid path including valves

    # Get the nodelist and the valvePositionDict
    nodelst = conf["test_graph"]["nodelist"]
    vPd = conf["graph"]["saveNameValvePositionDict"]

    # Get the target valveSettings
    valveSettings_target = conf["test_graph"]['valveSettings_target']
    # Get the resulting valveSettings
    valveSettings_result = graph.getValveSettings(nodelist=nodelst, valvePositionDict=vPd)

    assert valveSettings_target == valveSettings_result, f"The valveSettings are {valveSettings_result} instead of {valveSettings_target}."

    ### A valid path not including valves

    # Get the nodelist
    nodelst_noValve = conf["test_graph"]["nodelist_noValve"]
    # Get the target valveSettings
    valveSettings_noValve_target = {}
    # Get the resulting valveSettings
    valveSettings_noValve_result = graph.getValveSettings(nodelist=nodelst_noValve, valvePositionDict=vPd)

    assert valveSettings_noValve_target == valveSettings_noValve_result, f"The valveSettings_noValve are {valveSettings_noValve_result} instead of {valveSettings_noValve_target}."


    ### An invalid path

    # Get the nodelist
    nodelst_wrongPath = conf['test_graph']['nodelist_wrongPath']

    with raises(ValueError):
        graph.getValveSettings(nodelist=nodelst_wrongPath, valvePositionDict=vPd)

def test_pathIsValid():
    # Get an invalid path
    path_wrong = conf["test_graph"]["nodelist_wrongPath"]
    pathValidityWrong_target = False
    pathValidityWrong_result = graph.pathIsValid(path=path_wrong, valvePositionDict=loadValvePositionDict(conf["graph"]["saveNameValvePositionDict"]))

    assert pathValidityWrong_target == pathValidityWrong_result, f"The path validity is {pathValidityWrong_result} instead of {pathValidityWrong_target}."

    # Get a valid path
    path_correct = conf["test_graph"]["nodelist"]
    pathValidityCorrect_target = True
    pathValidityCorrect_result = graph.pathIsValid(path=path_correct, valvePositionDict=loadValvePositionDict(conf["graph"]["saveNameValvePositionDict"]))

    assert pathValidityCorrect_target == pathValidityCorrect_result, f"The path validity is {pathValidityCorrect_result} instead of {pathValidityCorrect_target}."

def test_getSystemStatus():

    # Get a path and a graph
    path = conf["test_graph"]["nodelist"]
    G, positions = graph.loadGraph(path_to_graphDict=conf['test_graph']['graph_target'])

    # With a given path
    edict = graph.getEdgedictFromNodelist(nodelist=path, graph=G)
    status_path_target = {}
    for edge in edict.keys():
        edict[edge]["status"] = "updatedStatus"
        status_path_target[edict[edge]["designation"]] = "updatedStatus"
    status_path_result = graph.getSystemStatus(path=path, full=False, graph=G)
    assert status_path_target == status_path_result, f"The status for the path is {status_path_result} instead of {status_path_target}."

    # Without a given path
    nx.set_edge_attributes(G=G, values="new_status", name="status")   # https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.set_edge_attributes.html
    status_full_target = nx.get_edge_attributes(G=G, name="status")
    status_full_result = graph.getSystemStatus(path=[], full=True, graph=G)

    assert status_full_target == status_full_result, f"The status for the path is {status_full_result} instead of {status_full_target}."

def test_updateSystemStatus():

    # Get a path and a graph
    path = conf["test_graph"]["nodelist"]
    G2, positions = graph.loadGraph(path_to_graphDict=conf['test_graph']['graph_target'])

    edict = graph.getEdgedictFromNodelist(nodelist=path, graph=G2)
    
    graph.updateSystemStatus(path=path, graph=G2)
    status_result = graph.getSystemStatus(path=path, full=False,graph=G2)
    
    status_target = {}
    for edge in edict.keys():
        status_target[edict[edge]["designation"]] = path[0]

    assert status_target == status_result, f"The status is {status_result} instead of {status_target}."

def test_findCandidate():
    # Get the candidates to work with
    Ps, Vs, Cs = cetoni.prepareCetoni()

    # Get all the syringes as test objects
    cands = {}
    for k in Ps.keys():
        cands[k] = Ps[k].syringe

    # Apply the function
    found = graph.findCandidate(candidates=cands, piston_stroke_mm=max, secondary={'minimum_volume_mL': max})
    
    assert list(found.keys())[0] == 'B0.0', f"The found key for the syringe is {list(found.keys())[0]} instead of B0.0."
    assert found['B0.0'].desig == '5_mL', f"The found syringe is {found['B0.0'].desig} instead of B0.0."
    
    # Close the bus communication
    cetoni.quitCetoni()


def test_getOpenEnds():
    # Get the graph
    graph_path = conf['test_graph']['graph_target']

    # Get the target open ends
    openEnds_target = conf['test_graph']['openEnds']

    # Get the open edges
    openEnds_result = graph.getOpenEnds(graph=graph_path)

    for oe in openEnds_target:
        assert oe in openEnds_result, f"The open ends {openEnds_result} do not contain the entry {oe}."
