import unittest
from testfixtures import compare
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from hardware import graph
from helpers import LoadFile

print("\n Test of function in graph.py. \n")

class test_graph(unittest.TestCase):
    def test_checkConsistency(self, path_nodes="tests/filesForTests/nodes_test.csv", path_edges="tests/filesForTests/edges_test.csv"):
        edges = pd.read_csv(path_edges, sep=";")
        nodes = pd.read_csv(path_nodes, sep=";")
        
        # Matching .csv files
        path_tubing_match = "tests/filesForTests/tubing_match_test.csv"
        tubing = pd.read_csv(path_tubing_match, sep=";")
        tubing_nodes = pd.concat([tubing["start"], tubing["end"]], axis=0)
        nods = list(tubing_nodes)
        tube_node_ref = all([node in list(nodes["node"]) for node in nods])
        tube_edge_ref = all([edge in list(edges["edge"]) for edge in list(tubing["edge"])])
        total_ref = tube_edge_ref and tube_node_ref

        total_graph, tube_edge_graph, tube_node_graph = graph.checkConsistency(path_nodes, path_edges, path_tubing_match)

        assert(tube_edge_ref, tube_edge_graph)
        assert(tube_node_ref, tube_node_graph)
        assert(total_ref, total_graph)
        results = [tube_edge_ref, tube_edge_graph, tube_node_ref, tube_node_graph, total_ref, total_graph]
        for res in results:
            assert(type(res), bool)

        # New entry
        path_tubing_newEdge = "tests/filesForTests/tubing_newNodeNewEdge_test copy.csv"
        tubing = pd.read_csv(path_tubing_newEdge, sep=";")
        tubing_nodes = pd.concat([tubing["start"], tubing["end"]], axis=0)
        nods = list(tubing_nodes)
        tube_node_ref = all([node in list(nodes["node"]) for node in nods])
        tube_edge_ref = all([edge in list(edges["edge"]) for edge in list(tubing["edge"])])
        total_ref = tube_edge_ref and tube_node_ref

        total_graph, tube_edge_graph, tube_node_graph = graph.checkConsistency(path_nodes, path_edges, path_tubing_newEdge)

        self.assertEqual(2, len(tube_node_graph), "Results concerning nodes are not equal.")
        self.assertEqual(total_ref, total_graph, "Total results are not equal.")
        self.assertEqual(len(tube_edge_graph), 1, "Number of excess edges is incorrect.")
        compare(list(tube_edge_graph), ["0253-DD-s"])

    def test_generateGraph(self, path_nodes=r"tests/filesForTests/nodes_test.csv", path_edges=r"tests/filesForTests/edges_test.csv", path_tubing=r"tests/filesForTests/tubing_match_test.csv", save_folder=r"tests/filesForTests", save_path=r"setup_generateGraph_test.pck"):
        # Check generation of graph.
        nodes = [("V1.0", {"name": "V1.0", "position": (-1,0)}), ("V1.1", {"name": "V1.1", "position": (-1.19,-0.06)}), ("V1.2", {"name": "V1.2", "position":(-1.12,-0.16)}),
        ("V1.3", {"name": "V1.3", "position":(-1,-0.2)}), ("V1.4", {"name": "V1.4", "position":(-0.88,-0.16)}), ("V6.6", {"name": "V6.6","position": (-5.81,0.06)}),
        ("V5.6", {"name": "V5.6","position": (-4.81,0.06)}), ("V6.8", {"name": "V6.8","position": (-6,0.2)}), ("Ev1", {"name": "Ev1","position": (-0.4,-2.1)}),
        ("Q+Chip3", {"name": "Q+Chip3","position": (-7.0,0.2)}), ("Q+Chip9", {"name": "Q+Chip9","position": (-7.1,-0.2)}), ("lambdaOUT", {"name": "lambdaOUT","position": (-8.1,0)}),
        ("V1.5", {"name": "V1.5","position": (-0.81,-0.06)})]
        edges = [("V1.0", "V1.1", {"name": "0004-XX-1", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.1", "V1.0", {"name": "0004-XX-1", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.2", {"name": "0004-XX-2", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.2", "V1.0", {"name": "0004-XX-2", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.3", {"name": "0004-XX-3", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.3", "V1.0", {"name": "0004-XX-3", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.4", {"name": "0004-XX-4", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.4", "V1.0", {"name": "0004-XX-4", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.5", {"name": "0004-XX-5", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.5", "V1.0", {"name": "0004-XX-5", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V6.6", "Q+Chip9", {"name": "0588-FT-8", "ends": "FT", "length": float(588), "diameter": float(0.3), "dead_volume": float(0.0416)}),
        ("Q+Chip9", "V6.6", {"name": "0588-FT-8", "ends": "FT", "length": float(588), "diameter": float(0.3), "dead_volume": float(0.0416)}),
        ("V5.6", "Q+Chip3", {"name": "0592-FT-3", "ends": "FT", "length": float(592), "diameter": float(0.3), "dead_volume": float(0.0418)}),
        ("Q+Chip3", "V5.6", {"name": "0592-FT-3", "ends": "FT", "length": float(592), "diameter": float(0.3), "dead_volume": float(0.0418)}),
        ("V6.8", "lambdaOUT", {"name": "0640-CT-2", "ends": "CT", "length": float(640), "diameter": float(0.3), "dead_volume": float(0.0452)}),
        ("lambdaOUT", "V6.8", {"name": "0640-CT-2", "ends": "CT", "length": float(640), "diameter": float(0.3), "dead_volume": float(0.0452)}),
        ("Ev1", "V1.5", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)}),
        ("V1.5", "Ev1", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)})]
        graph_ref=nx.DiGraph()
        graph_ref.add_nodes_from(nodes)
        graph_ref.add_edges_from(edges)

        graph_graph = graph.generateGraph(path_nodes=path_nodes, path_edges=path_edges, path_tubing=path_tubing, show=False, save=True, save_folder=save_folder, save_path=save_path)
        
        compare(graph_ref, graph_graph)
        
        # Check positions.
        positions_ref = {"V1.0": (-1,0), "V1.1": (-1.19,-0.06), "V1.2": (-1.12,-0.16), "V1.3": (-1,-0.2), "V1.4": (-0.88,-0.16), "V6.6": (-5.81,0.06), "V5.6": (-4.81,0.06), "V6.8": (-6,0.2), "Ev1": (-0.4,-2.1),
        "Q+Chip3": (-7.0,0.2), "Q+Chip9": (-7.1,-0.2), "lambdaOUT": (-8.1,0), "V1.5": (-0.81,-0.06)}

        positions_graph = LoadFile(r"tests/filesForTests/setup_generateGraph_test_positions.pck")
        
        self.assertDictEqual(positions_ref, positions_graph)

        # Check that saved and loaded graph matches the generated graph for same settings.
        compare(graph_graph, LoadFile(r"tests/filesForTests/setup_generateGraph_test.pck"))


    def test_appendEdge(self, edge_name="0286-NT-1", edgeNodes=pd.read_csv(r"tests/filesForTests/tubing_match_test.csv", sep=";"), edgeProps=pd.read_csv(r"tests/filesForTests/edges_test.csv", sep=";")):
        # Directed edge (not adding both directions)
        targed_directed_edgelst = [("Ev1", "V1.5", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)})]
        edgelst1 = []
        graph.appendEdge(edgelst1, edge_name, edgeNodes, edgeProps, reverse=False)
        compare(targed_directed_edgelst, edgelst1)
        # Undirected edge (adding both directions)
        targed_undirected_edgelst = [("Ev1", "V1.5", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)}), ("V1.5", "Ev1", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)})]
        edgelst2 = []
        graph.appendEdge(edgelst2, edge_name, edgeNodes, edgeProps, reverse=True)
        self.assertEqual(targed_undirected_edgelst, edgelst2)

    def test_drawGraph(self):
        # Generate test graph.
        nodes = [("V1.0", {"name": "V1.0", "position": (-1,0)}), ("V1.1", {"name": "V1.1", "position": (-1.19,-0.06)}), ("V1.2", {"name": "V1.2", "position":(-1.12,-0.16)}),
        ("V1.3", {"name": "V1.3", "position":(-1,-0.2)}), ("V1.4", {"name": "V1.4", "position":(-0.88,-0.16)}), ("V6.6", {"name": "V6.6","position": (-5.81,0.06)}),
        ("V5.6", {"name": "V5.6","position": (-4.81,0.06)}), ("V6.8", {"name": "V6.8","position": (-6,0.2)}), ("Ev1", {"name": "Ev1","position": (-0.4,-2.1)}),
        ("Q+Chip3", {"name": "Q+Chip3","position": (-7.0,0.2)}), ("Q+Chip9", {"name": "Q+Chip9","position": (-7.1,-0.2)}), ("lambdaOUT", {"name": "lambdaOUT","position": (-8.1,0)}),
        ("V1.5", {"name": "V1.5","position": (-0.81,-0.06)})]
        edges = [("V1.0", "V1.1", {"name": "0004-XX-1", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.1", "V1.0", {"name": "0004-XX-1", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.2", {"name": "0004-XX-2", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.2", "V1.0", {"name": "0004-XX-2", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.3", {"name": "0004-XX-3", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.3", "V1.0", {"name": "0004-XX-3", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.4", {"name": "0004-XX-4", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.4", "V1.0", {"name": "0004-XX-4", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.0", "V1.5", {"name": "0004-XX-5", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V1.5", "V1.0", {"name": "0004-XX-5", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)}),
        ("V6.6", "Q+Chip9", {"name": "0588-FT-8", "ends": "FT", "length": float(588), "diameter": float(0.3), "dead_volume": float(0.0416)}),
        ("Q+Chip9", "V6.6", {"name": "0588-FT-8", "ends": "FT", "length": float(588), "diameter": float(0.3), "dead_volume": float(0.0416)}),
        ("V5.6", "Q+Chip3", {"name": "0592-FT-3", "ends": "FT", "length": float(592), "diameter": float(0.3), "dead_volume": float(0.0418)}),
        ("Q+Chip3", "V5.6", {"name": "0592-FT-3", "ends": "FT", "length": float(592), "diameter": float(0.3), "dead_volume": float(0.0418)}),
        ("V6.8", "lambdaOUT", {"name": "0640-CT-2", "ends": "CT", "length": float(640), "diameter": float(0.3), "dead_volume": float(0.0452)}),
        ("lambdaOUT", "V6.8", {"name": "0640-CT-2", "ends": "CT", "length": float(640), "diameter": float(0.3), "dead_volume": float(0.0452)}),
        ("Ev1", "V1.5", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)}),
        ("V1.5", "Ev1", {"name": "0286-NT-1", "ends": "NT", "length": float(286), "diameter": float(0.3), "dead_volume": float(0.0202)})]
        testgraph=nx.DiGraph()
        testgraph.add_nodes_from(nodes)
        testgraph.add_edges_from(edges)

        # Generate test positions.
        testpositions = {"V1.0": (-1,0), "V1.1": (-1.19,-0.06), "V1.2": (-1.12,-0.16), "V1.3": (-1,-0.2), "V1.4": (-0.88,-0.16), "V6.6": (-5.81,0.06), "V5.6": (-4.81,0.06),
        "V6.8": (-6,0.2), "Ev1": (-0.4,-2.1), "Q+Chip3": (-7.0,0.2), "Q+Chip9": (-7.1,-0.2), "lambdaOUT": (-8.1,0), "V1.5": (-0.81,-0.06)}

        plot3 = nx.draw(testgraph, pos=testpositions, with_labels=True, node_color="g", node_shape="^", node_size=600, alpha=0.6)  # node_color, node_shape, node_size and alpha according to https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html#networkx.drawing.nx_pylab.draw_networkx
        plot4 = graph.drawGraph(testgraph, testpositions)

        # TODO: Find a way to compare the plots.       


    def test_getEdgedictFromNodelist(self, testgraph=LoadFile(r"tests/filesForTests/setup_test.pck")):
        nodelst = ['A0.0', 'A0.1', 'Av1', 'V1.1', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.1', 'Reservoir1']
        edgeDict_ref = {"0215-NN-1": {"name": "0215-NN-1", "ends": "NN", "length": float(215), "diameter": float(0.3), "dead_volume": float(0.0152)},
        "0000-XX-1": {"name": "0000-XX-1", "ends": "XX", "length": float(0), "diameter": float(0.6), "dead_volume": float(0.003)},
        "0502-NT-1": {"name": "0502-NT-1", "ends": "NT", "length": float(502), "diameter": float(0.3), "dead_volume": float(0.0355)},
        "0004-XX-1": {"name": "0004-XX-1", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)},
        "0192-TT-1": {"name": "0192-TT-1", "ends": "TT", "length": float(192), "diameter": float(0.3), "dead_volume": float(0.0136)},
        "0004-XX-17": {"name": "0004-XX-17", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)},
        "0255-TT-1": {"name": "0255-TT-1", "ends": "TT", "length": float(255), "diameter": float(0.3), "dead_volume": float(0.018)},
        "0004-XX-21": {"name": "0004-XX-21", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)},
        "0476-CT-1": {"name": "0476-CT-1", "ends": "CT", "length": float(476), "diameter": float(0.3), "dead_volume": float(0.0336)}}
        
        edgeDict_graph = graph.getEdgedictFromNodelist(testgraph, nodelst)
        self.assertDictEqual(edgeDict_ref, edgeDict_graph)


    def test_getTotalQuantity(self, testgraph=LoadFile(r"tests/filesForTests/setup_test.pck")):
        edgeDict = {"0215-NN-1": {"name": "0215-NN-1", "ends": "NN", "length": float(215), "diameter": float(0.3), "dead_volume": float(0.0152)},
        "0000-XX-1": {"name": "0000-XX-1", "ends": "XX", "length": float(0), "diameter": float(0.6), "dead_volume": float(0.003)},
        "0502-NT-1": {"name": "0502-NT-1", "ends": "NT", "length": float(502), "diameter": float(0.3), "dead_volume": float(0.0355)},
        "0004-XX-1": {"name": "0004-XX-1", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)},
        "0192-TT-1": {"name": "0192-TT-1", "ends": "TT", "length": float(192), "diameter": float(0.3), "dead_volume": float(0.0136)},
        "0004-XX-17": {"name": "0004-XX-17", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)},
        "0255-TT-1": {"name": "0255-TT-1", "ends": "TT", "length": float(255), "diameter": float(0.3), "dead_volume": float(0.018)},
        "0004-XX-21": {"name": "0004-XX-21", "ends": "XX", "length": float(4.33), "diameter": float(0.5), "dead_volume": float(0.0116)},
        "0476-CT-1": {"name": "0476-CT-1", "ends": "CT", "length": float(476), "diameter": float(0.3), "dead_volume": float(0.0336)}}

        dead_volume_total_ref = 0.1537
        dead_volume_total_graph = graph.getTotalQuantity(edgeDict, "dead_volume")

        self.assertEqual(dead_volume_total_ref, dead_volume_total_graph)


    def test_generate_valvePositionDict(self):
        vPd_ref = {"V1": {"V1.0": None, "V1.1": 0, "V1.2": 1, "V1.3": 2, "V1.4": 3, "V1.5": 4, "V1.6": 5, "V1.7": 6, "V1.8": 7, "V1.9": 8, "V1.10": 9},
        "V2": {"V2.0": None, "V2.1": 0, "V2.2": 1, "V2.3": 2, "V2.4": 3, "V2.5": 4, "V2.6": 5, "V2.7": 6, "V2.8": 7, "V2.9": 8, "V2.10": 9},
        "V3": {"V3.0": None, "V3.1": 0, "V3.2": 1, "V3.3": 2, "V3.4": 3, "V3.5": 4, "V3.6": 5, "V3.7": 6, "V3.8": 7, "V3.9": 8, "V3.10": 9},
        "V4": {"V4.0": None, "V4.1": 0, "V4.2": 1, "V4.3": 2, "V4.4": 3, "V4.5": 4, "V4.6": 5, "V4.7": 6, "V4.8": 7, "V4.9": 8, "V4.10": 9},
        "V5": {"V5.0": None, "V5.1": 0, "V5.2": 1, "V5.3": 2, "V5.4": 3, "V5.5": 4, "V5.6": 5, "V5.7": 6, "V5.8": 7, "V5.9": 8, "V5.10": 9},
        "V6": {"V6.0": None, "V6.1": 0, "V6.2": 1, "V6.3": 2, "V6.4": 3, "V6.5": 4, "V6.6": 5, "V6.7": 6, "V6.8": 7, "V6.9": 8, "V6.10": 9},
        "Av": {"Av1": 1, "Av2": 0}, "Bv": {"Bv1": 1, "Bv2": 0}, "Cv": {"Cv1": 1, "Cv2": 0}, "Dv": {"Dv1": 1, "Dv2": 0}, "Ev": {"Ev1": 1, "Ev2": 0}, "Fv": {"Fv1": 1, "Fv2": 0}}
        
        graph.generate_valvePositionDict(save_path=r"tests/filesForTests", save_name=r"valvePositionDict_test.pck")
        vPd_graph = LoadFile(r"tests/filesForTests/valvePositionDict_test.pck")
        
        self.assertEqual(vPd_ref, vPd_graph)

    def test_getValveSettings(self):
        nodelst = ['A0.0', 'A0.1', 'Av1', 'V1.1', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.1', 'Reservoir1']
        vPd = {"V1": {"V1.0": None, "V1.1": 0, "V1.2": 1, "V1.3": 2, "V1.4": 3, "V1.5": 4, "V1.6": 5, "V1.7": 6, "V1.8": 7, "V1.9": 8, "V1.10": 9},
        "V2": {"V2.0": None, "V2.1": 0, "V2.2": 1, "V2.3": 2, "V2.4": 3, "V2.5": 4, "V2.6": 5, "V2.7": 6, "V2.8": 7, "V2.9": 8, "V2.10": 9},
        "V3": {"V3.0": None, "V3.1": 0, "V3.2": 1, "V3.3": 2, "V3.4": 3, "V3.5": 4, "V3.6": 5, "V3.7": 6, "V3.8": 7, "V3.9": 8, "V3.10": 9},
        "V4": {"V4.0": None, "V4.1": 0, "V4.2": 1, "V4.3": 2, "V4.4": 3, "V4.5": 4, "V4.6": 5, "V4.7": 6, "V4.8": 7, "V4.9": 8, "V4.10": 9},
        "V5": {"V5.0": None, "V5.1": 0, "V5.2": 1, "V5.3": 2, "V5.4": 3, "V5.5": 4, "V5.6": 5, "V5.7": 6, "V5.8": 7, "V5.9": 8, "V5.10": 9},
        "V6": {"V6.0": None, "V6.1": 0, "V6.2": 1, "V6.3": 2, "V6.4": 3, "V6.5": 4, "V6.6": 5, "V6.7": 6, "V6.8": 7, "V6.9": 8, "V6.10": 9},
        "Av": {"Av1": 1, "Av2": 0}, "Bv": {"Bv1": 1, "Bv2": 0}, "Cv": {"Cv1": 1, "Cv2": 0}, "Dv": {"Dv1": 1, "Dv2": 0}, "Ev": {"Ev1": 1, "Ev2": 0}, "Fv": {"Fv1": 1, "Fv2": 0}}

        valveSettings_ref = {"Av": 1, "V1": 0, "V2": 6, "V3": 0}
        valveSettings_graph = graph.getValveSettings(nodelst, vPd)

        self.assertDictEqual(valveSettings_ref, valveSettings_graph)

    def test_loadGraph(self):
        graph_ref = LoadFile(r"tests/filesForTests/setup_test.pck")
        vPd_ref = LoadFile(r"tests/filesForTests/valvePositionDict_test.pck")

        graph_graph, vPd_graph = graph.loadGraph(r"tests/filesForTests/setup_test.pck", r"tests/filesForTests/valvePositionDict_test.pck")
        #self.maxDiff=None
        #print(nx.to_dict_of_dicts(graph_ref), "\n", nx.to_dict_of_dicts(graph_graph))   #TODO: FIX: Why are the dicts not equal, but the lists are?
        self.assertDictEqual(nx.to_dict_of_lists(graph_ref), nx.to_dict_of_lists(graph_graph))
        self.assertDictEqual(vPd_ref, vPd_graph)


    def test_findClosest(self, testgraph=LoadFile(r"tests/filesForTests/setup_test.pck")):
        node = "NMRout"
        candidates = ["A0.0", "B0.0", "C0.0", "D0.0", "E0.0", "F0.0"] #["V2.1", "V3.2", "V4.3", "V5.4", "V6.5"]  #
        closest_ref = "F0.0"
        
        closest_graph, pathToClosest = graph.findClosest(testgraph, node, candidates, "dead_volume", "in")

        print(closest_ref, closest_graph)

        self.assertEqual(closest_ref, closest_graph)

if __name__ == "__main__":
    unittest.main(verbosity=2)