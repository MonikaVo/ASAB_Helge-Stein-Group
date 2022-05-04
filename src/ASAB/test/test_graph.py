from ASAB.test.FilesForTests import config_test
conf = config_test.config

import networkx as nx
import pandas as pd
import numpy as np
from ASAB.utility import graph
from ASAB.utility.helpers import loadTxtFile
from ASAB.driver.CetoniDevice_driver import loadValvePositionDict


print("\n Test of functions in graph.py. \n")

# TODO: Fix this test
def test_findClosest(testgraph=loadTxtFile(conf["CetoniDeviceDriver"]["setup"])):
    node = conf["graph"]["testInput"]["findClosest"]["node"]
    candidates = conf["graph"]["testInput"]["findClosest"]["candidates"]
    closest_target = conf["graph"]["testOutput"]["findClosest"]["closest_target"]
    
    closest_graph, pathToClosest = graph.findClosest(graph=testgraph, node=node, candidates=candidates, weight="dead_volume", direction="out")
    assert closest_target==closest_graph

def test_findPath():
    path_target = conf["graph"]["testInput"]["getEdgeDict"]["nodelist"]
    pathValidity_target = graph.pathIsValid(path=path_target, valvePositionDict=loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))

    path_result = graph.findPath(start_node=path_target[0], end_node=path_target[-1], valvePositionDict=loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]), graph=graph.loadGraph(conf["CetoniDeviceDriver"]["setup"]))
    pathValidity_result = graph.pathIsValid(path=path_result, valvePositionDict=loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"]))

    assert path_target == path_result
    assert pathValidity_target == True
    assert pathValidity_result == True

def test_checkConsistency(path_nodes=conf["graph"]["testInput"]["checkConsistency"]["path_nodes"], path_edges=conf["graph"]["testInput"]["checkConsistency"]["path_edges"], path_tubing_match=conf["graph"]["testInput"]["checkConsistency"]["path_tubing_match"], path_tubing_newEdge=conf["graph"]["testInput"]["checkConsistency"]["path_tubing_newEdge"]):
    edges = pd.read_csv(path_edges, sep=";")
    nodes = pd.read_csv(path_nodes, sep=";")
    
    # Matching .csv files
    tubing = pd.read_csv(path_tubing_match, sep=";")
    tubing_nodes = pd.concat([tubing["start"], tubing["end"]], axis=0)
    nods = list(tubing_nodes)
    tube_node_ref = all([node in list(nodes["node"]) for node in nods])
    tube_edge_ref = all([edge in list(edges["edge"]) for edge in list(tubing["edge"])])
    total_ref = tube_edge_ref and tube_node_ref

    total_graph, tube_edge_graph, tube_node_graph = graph.checkConsistency(path_nodes, path_edges, path_tubing_match)

    assert tube_edge_ref == tube_edge_graph
    assert tube_node_ref == tube_node_graph
    assert total_ref == total_graph
    results = [tube_edge_ref, tube_edge_graph, tube_node_ref, tube_node_graph, total_ref, total_graph]
    for res in results:
        assert type(res) == bool

    # New entry
    tubing = pd.read_csv(path_tubing_newEdge, sep=";")
    tubing_nodes = pd.concat([tubing["start"], tubing["end"]], axis=0)
    nods = list(tubing_nodes)
    tube_node_ref = all([node in list(nodes["node"]) for node in nods])
    tube_edge_ref = all([edge in list(edges["edge"]) for edge in list(tubing["edge"])])
    total_ref = tube_edge_ref and tube_node_ref

    total_graph, tube_edge_graph, tube_node_graph = graph.checkConsistency(path_nodes, path_edges, path_tubing_newEdge)

    assert 2 == len(tube_node_graph)
    assert total_ref == total_graph
    assert len(tube_edge_graph) == 1
    assert list(tube_edge_graph) == ["0253-DD-s"]

def test_appendEdge(edge_name="0286-NT-1", edgeNodes=pd.read_csv(conf["graph"]["testInput"]["checkConsistency"]["path_tubing_match"], sep=";"), edgeProps=pd.read_csv(conf["graph"]["testInput"]["checkConsistency"]["path_edges"], sep=";")):
    # Directed edge (not adding both directions)
    target_directed_edgelst = [("Ev1", "V1.5", {"name": "0286-NT-1", "designation": ("Ev1", "V1.5"), "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202), "status": "empty"})]
    edgelst1 = []
    graph.appendEdge(edgelst1, edge_name, edgeNodes, edgeProps, reverse=False)
    assert target_directed_edgelst == edgelst1
    # Undirected edge (adding both directions)
    target_undirected_edgelst = [("Ev1", "V1.5", {"name": "0286-NT-1", "designation": ("Ev1", "V1.5"), "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202), "status": "empty"}), ("V1.5", "Ev1", {"name": "0286-NT-1", "designation": ("V1.5", "Ev1"), "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202), "status": "empty"})]
    edgelst2 = []
    graph.appendEdge(edgelst2, edge_name, edgeNodes, edgeProps, reverse=True)
    assert target_undirected_edgelst == edgelst2

def test_drawGraph():
    # Generate test graph.
    nodes = conf["graph"]["testInput"]["drawGraph"]["nodes"]
    edges = conf["graph"]["testInput"]["drawGraph"]["edges"]
    testgraph=nx.DiGraph()
    testgraph.add_nodes_from(nodes)
    testgraph.add_edges_from(edges)

    # Generate test positions.
    testpositions = conf["graph"]["testInput"]["drawGraph"]["testpositions"]

    plot3 = nx.draw(testgraph, pos=testpositions, with_labels=True, node_color="g", node_shape="^", node_size=600, alpha=0.6)  # node_color, node_shape, node_size and alpha according to https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html#networkx.drawing.nx_pylab.draw_networkx
    plot4 = graph.drawGraph(testgraph, testpositions)

    # TODO: Find a way to compare the plots.

# def test_generateValvePositionDict(self):
#     vPd_target = loadFile(conf["CetoniDeviceDriver"]["valvePositionDict"])

#     graph.generateValvePositionDict(save_name=conf["graph"]["testInput"]["generateValvePositionDict"]["savePath"])
#     vPd_result = loadFile(conf["graph"]["testInput"]["generateValvePositionDict"]["savePath"])
    
#     self.assertDictEqual(d1=vPd_target, d2=vPd_result, msg="Valve position dictionaries do not match.")

# TODO: Fix this test. Not passed due to nan != nan
def test_loadGraph():
    graph_target = graph.loadGraph(conf["CetoniDeviceDriver"]["setup"])
    vPd_target = loadValvePositionDict(conf["CetoniDeviceDriver"]["valvePositionDict"])

    graph_graph= graph.loadGraph(conf["CetoniDeviceDriver"]["setup"])
    for k in nx.to_dict_of_dicts(graph_target).keys():
        assert graph_target[k] == graph_graph[k]
    # print(nx.to_dict_of_dicts(graph_target)["lambdaIN"], "\n", nx.to_dict_of_dicts(graph_graph)["lambdaIN"])   #TODO: FIX: Why are the dicts not equal, but the lists are?
    # for key in nx.to_dict_of_dicts(graph_target):
    #     print(key)
    #     self.assertDictEqual(nx.to_dict_of_dicts(graph_target)[key], nx.to_dict_of_dicts(graph_graph)[key])
    #self.assertDictEqual(nx.to_dict_of_lists(graph_target), nx.to_dict_of_lists(graph_graph))
    #self.assertDictEqual(vPd_target, vPd_graph)

def test_getValveFromName():
    valves_target = conf["graph"]["testOutput"]["getValveFromName"]["valves"]
    valveNames = conf["graph"]["testInput"]["getValveFromName"]["names"]

    valves_result = []
    for name in valveNames:
        valve = graph.getValveFromName(node_name=name, valvePositionDict=loadValvePositionDict(conf["graph"]["testInput"]["generateValvePositionDict"]["savePath"]))
        valves_result.append(valve)

    assert valves_target == valves_result

def test_getEdgedictFromNodelist(testgraph=graph.loadGraph(conf["CetoniDeviceDriver"]["setup"])):
    nodelst = conf["graph"]["testInput"]["getEdgeDict"]["nodelist"]
    edgeDict_target = conf["graph"]["testOutput"]["getEdgeDict"]["edgeDict_target"]
    
    edgeDict_graph = graph.getEdgedictFromNodelist(graph=testgraph, nodelist=nodelst)
    print(edgeDict_graph)
    assert edgeDict_target == edgeDict_graph

# TODO: Fix this test. Not passed due to nan != nan
def test_generateGraph(path_nodes=conf["graph"]["testInput"]["checkConsistency"]["path_nodes"], path_edges=conf["graph"]["testInput"]["checkConsistency"]["path_edges"], path_tubing=conf["graph"]["testInput"]["checkConsistency"]["path_tubing_match"], save_path=conf["graph"]["testInput"]["generateGraph"]["savePath"]):
    # Check generation of graph.
    # Generate test graph.
    # TODO: fix edges according to new definition in target values.
    nodes = conf["graph"]["testInput"]["drawGraph"]["nodes"]
    edges = conf["graph"]["testInput"]["drawGraph"]["edges"]
    graph_target=nx.DiGraph()
    graph_target.add_nodes_from(nodes)
    graph_target.add_edges_from(edges)

    graph_graph = graph.generateGraph(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing, show=False, save=True, save_path=save_path)
    for k in nx.to_dict_of_dicts(graph_target):
        assert nx.to_dict_of_dicts(graph_target)[k] == nx.to_dict_of_dicts(graph_graph)[k]
    
    # Check positions.
    positions_target = conf["graph"]["testInput"]["drawGraph"]["testpositions"]

    # Load the positions file
    with open(f"{str(save_path[0:-4])}_positions.txt", "r", encoding="utf-8") as file2:
        rawString = file2.read()
    # Make the rawString string to a dict
    positions_graph = eval(rawString)

    assert positions_target == positions_graph

def test_getTotalQuantity():
    nodelst = conf["graph"]["testInput"]["getEdgeDict"]["nodelist"]
    dead_volume_total_target = 0.1807
    dead_volume_total_graph = graph.getTotalQuantity(nodelist=nodelst, quantity="dead_volume")
    assert np.isclose(dead_volume_total_target, dead_volume_total_graph, 0.00001)

def test_getValveSettings():
    nodelst = conf["graph"]["testInput"]["getEdgeDict"]["nodelist"]
    vPd = conf["graph"]["testInput"]["getValveSettings"]["vPd"]

    valveSettings_target = {"Av": 1, "V1": 0, "V2": 6, "V3": 0}
    valveSettings_graph = graph.getValveSettings(nodelst, vPd)

    assert valveSettings_target == valveSettings_graph

def test_pathIsValid():
        path_wrong = conf["graph"]["testInput"]["pathIsValid"]["path"]["wrong"]
        pathValidityWrong_target = False
        pathValidityWrong_result = graph.pathIsValid(path=path_wrong, valvePositionDict=loadValvePositionDict(conf["graph"]["testInput"]["generateValvePositionDict"]["savePath"]))

        path_correct = conf["graph"]["testInput"]["pathIsValid"]["path"]["correct"]
        pathValidityCorrect_target = True
        pathValidityCorrect_result = graph.pathIsValid(path=path_correct, valvePositionDict=loadValvePositionDict(conf["graph"]["testInput"]["generateValvePositionDict"]["savePath"]))

        assert pathValidityWrong_target == pathValidityWrong_result
        assert pathValidityCorrect_target == pathValidityCorrect_result

def test_getSystemStatus(path=conf["graph"]["testInput"]["getEdgeDict"]["nodelist"], graph_path=conf["graph"]["testInput"]["getSystemStatus"]):
    # With a given path
    setup1 = graph.loadGraph(graph_path)
    edict = graph.getEdgedictFromNodelist(nodelist=path, graph=setup1)
    status_target1 = {}
    for edge in edict.keys():
        edict[edge]["status"] = "A0.0"
        status_target1[edict[edge]["designation"]] = "A0.0"
    status_result1 = graph.getSystemStatus(path=path, full=False, graph=setup1)
    
    assert status_target1 == status_result1

    # Without a given path
    setup2 = graph.loadGraph(graph_path)
    nx.set_edge_attributes(G=setup2, values="new_status", name="status")   # https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.set_edge_attributes.html
    status_target2 = nx.get_edge_attributes(G=setup2, name="status")
    status_result2 = graph.getSystemStatus(path=[], full=True, graph=setup2)

    assert status_target2 == status_result2


def test_updateSystemStatus(path=conf["graph"]["testInput"]["getEdgeDict"]["nodelist"], graph_path=conf["graph"]["testInput"]["getSystemStatus"]):
    setup  = graph.loadGraph(graph_path)
    edict = graph.getEdgedictFromNodelist(nodelist=path, graph=setup)
    
    graph.updateSystemStatus(path=path, graph=setup)
    status_result = graph.getSystemStatus(path=path, full=False,graph=setup)
    
    status_target = {}
    for edge in edict.keys():
        status_target[edict[edge]["designation"]] = "A0.0"

    assert status_target == status_result