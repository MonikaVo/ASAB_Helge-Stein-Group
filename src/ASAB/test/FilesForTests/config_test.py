config = dict()

#####################
### regular config###
#####################

projectFolder = ".." # edited prior to publication
experimentFolder = "ASAB\\test\\FilesForTests" # edited prior to publication

config['projectFolder'] = projectFolder

config['experimentFolder'] = experimentFolder

config["balanceDriver"] =   {
                                "serialPort": "<COM port>",
                                "settings": {'baudrate': 115200, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 0, 'write_timeout': None, 'inter_byte_timeout': None},
                                "simulated": True
                            }

config["balance"] = {
                        "simulated": True
                    }

config["CetoniDeviceDriver"] =  {
                                    "availableSyringes": experimentFolder + "\\syringes_test.txt",
                                    "configPath": projectFolder + "...\\Config_Test_sim",   # edited prior to publication
                                    "syringeConfig": {"A0.0": "1_mL", "B0.0": "5_mL", "C0.0": "2_5_mL"},#{"A0.0": "10_mL", "B0.0": "10_mL", "C0.0": "10_mL"},
                                    "valvePositionDict": experimentFolder + "\\valvePositionDict_test.py",
                                    "flow": 0.03,
                                    "simulateBalance": True
                                }

config["CetoniDevice"] =    {
                                "waste": "waste_1",
                                "gas": "ambient",
                                "pathsToClean": [],
                                "measureVolumes": {"densiVisco": 3.0, "uvVis": 0.0182},
                            }

config["densiViscoDriver"] = {
                            "inputFolder": "FilesForTests\\densiVisco",   # edited prior to publication
                            "outputFolder": "FilesForTests\\densiVisco"   # edited prior to publication
                        }


config["densiVisco"] = {
                            "inputFolder": "FilesForTests\\densiVisco",   # edited prior to publication
                            "outputFolder": "FilesForTests\\densiVisco"   # edited prior to publication
                        }

config["syringes"] =    {
                            "savePath": experimentFolder + "\\syringes_test.py",
                        }

config["graph"] =   {
                        "pathNodes": experimentFolder + "\\nodes_test.csv",
                        "pathEdges": experimentFolder + "\\edges_test.csv",
                        "pathTubing": experimentFolder + "\\tubing_test.csv",
                        "savePath_graph": experimentFolder + "\\graph_test.py",
                        "saveNameValvePositionDict": experimentFolder + "\\valvePositionDict_test.py",
                    }

config["ArduinoDriver"] =   {
                                "Arduino":  [{
                                                "ArduinoNo": 0,
                                                "serialPort": '<COM port>', # edited prior to publication
                                                "settings": {'baudrate': 9600, 'timeout': 1},
                                                "simulated": True
                                            }],
                                "ArduinoRelay": [{
                                                    "relayNo": 1,
                                                    "ArduinoNo": 0
                                                }],
                                "ArduinoValve": [{
                                                    "name": 'Va1',
                                                    "positions": [0,1],
                                                    "ArduinoNo": 0,
                                                    "relayNo": 1
                                                }]
                            }

config["solutionHandler"] = {
                                'stockSolutions': experimentFolder + "\\stockSolutions.csv",
                                'chemicals': experimentFolder + "\\chemicals.csv",
                                'units': {'molarMass': 'g/mol', 'density': 'g/cm^3', 'mass': 'g'},
                                'chemicalsDict': experimentFolder + "\\chemicalsDict.py",
                                'nonChemicalCols': ['solutionName', 'reservoir', 'pump', 'references', 'massTotal', 'massTotal_uncertainty', 'density', 'density_uncertainty'],
                                'solutionsDict': experimentFolder + "\\solutionsDict.py"
                            }

############################
### specific test config ###
############################
''' This part of this config file defines inputs and outputs, which are not included in the regular operational config file
as they are specifically needed by the tests. '''


config['test_balanceDriver'] =  {
                                'inputs': {},
                                'targets': {}
                                }

config['test_balance'] =    {
                            'inputs': {},
                            'targets': {}
                            }

config['test_CetoniDevice'] =   {
                                'inputs':    {
                                                "fillSyringe": [{"pump": "A0.0", "volume": 0.3, "waste": "Reservoir7", "valvePos":{'V1': 5, 'V2': 4, 'V3': 3, 'V4': 9, 'V5': 7, 'V6': 8, 'V7': 5, 'V8': 3, 'V9': 9, 'V10': 1, 'Av': 3, 'Bv': 1, 'Cv': 0, 'Dv': 1, 'Ev': 0, 'Fv': 0}}],
                                                "mix":[{"mixRatio": {"Reservoir1": 0.150, "Reservoir2": 0.400, "Reservoir3": 0.600}, "waste": "Reservoir6", "gas": "Reservoir5"}],
                                            },
                                'targets':  {}
                                }

config['test_ArduinoDriver'] =  {
                                'inputs':   {
                                                'nameArduino': 'Test_Arduino',
                                                'nameRelay': 'Test_Relay',
                                                'setRelayState': {'initState': 0},
                                                'switchToPosition': {'initPosition': 0}
                                            },
                                'targets':  {
                                                'setRelayState': {'targetState': 1},
                                                'init': {'handle': 123456}, 
                                                'noOfValvePositions': {'noOfValvePositions': 2},
                                                'switchToPosition': {'targetPosition': 1}
                                            }
                                }

config['test_densiViscoDriver'] =   {
                                        'outputFile': 'FilesForTests\\densiVisco\\OutputTest_Density_measurement.csv',   # edited prior to publication
                                        'rawFile': 'FilesForTests\\densiVisco\\Raw_test.json',   # edited prior to publication
                                        'resultFile': 'FilesForTests\\densiVisco\\Result_test.json',   # edited prior to publication
                                        'savePath': 'FilesForTests\\densiVisco'   # edited prior to publication
                                    }

config['test_densiVisco'] =   {
                                        'outputFile': 'FilesForTests\\densiVisco\\OutputTest_Density_measurement.csv',   # edited prior to publication
                                        'rawFile': 'FilesForTests\\densiVisco\\Raw_test.json',   # edited prior to publication
                                        'resultFile': 'FilesForTests\\densiVisco\\Result_test.json',   # edited prior to publication
                                        'savePath': 'FilesForTests\\densiVisco'   # edited prior to publication
                                    }

config['test_helpers'] =    {
                                'savePath': r"FilesForTests",   # edited prior to publication
                                'filename': "test_save",
                                'extension': "txt",
                                'variableFile': 'loadVariable_test',
                                'variableExtension': 'py'
                            }

config['test_syringes'] =   {
                                'testInit': [{'designation': 'a', 'innerDia': 12.0, 'pistonStroke': 55.0}, {'designation': '2_5_mL', 'innerDia': 7.28366, 'pistonStroke': 60}],
                                'testFromDict': {'dict': {'desig': 'test', 'inner_dia_mm': 15.0, 'piston_stroke_mm': 70.0}}
                            }

config['test_CetoniDeviceDriver'] =    {
                                            'valvePositionDict_target': {'Av': {'Av.0': 0, 'Av.1': 1}, 'V1': {'V1.1': 0, 'V1.2': 1, 'V1.3': 2, 'V1.4': 3, 'V1.5': 4, 'V1.6': 5, 'V1.7': 6, 'V1.8': 7, 'V1.9': 8, 'V1.10': 9}, 'V2': {'V2.1': 0, 'V2.2': 1, 'V2.3': 2, 'V2.4': 3, 'V2.5': 4, 'V2.6': 5, 'V2.7': 6, 'V2.8': 7, 'V2.9': 8, 'V2.10': 9}, 'V3': {'V3.1': 0, 'V3.2': 1, 'V3.3': 2, 'V3.4': 3, 'V3.5': 4, 'V3.6': 5, 'V3.7': 6, 'V3.8': 7, 'V3.9': 8, 'V3.10': 9}, 'V4': {'V4.1': 0, 'V4.2': 1, 'V4.3': 2, 'V4.4': 3, 'V4.5': 4, 'V4.6': 5, 'V4.7': 6, 'V4.8': 7, 'V4.9': 8, 'V4.10': 9}, 'V5': {'V5.1': 0, 'V5.2': 1, 'V5.3': 2, 'V5.4': 3, 'V5.5': 4, 'V5.6': 5, 'V5.7': 6, 'V5.8': 7, 'V5.9': 8, 'V5.10': 9}, 'Bv': {'Bv.0': 0, 'Bv.1': 1}, 'Cv': {'Cv.0': 0, 'Cv.1': 1}, 'ArdV_0_1': {'ArdV_0_1.0': 0, 'ArdV_0_1.1': 1}},
                                            "prepareCetoni":    {"syringeParams":
                                                                    {
                                                                        "A0.0": {"params": "syringe(inner_diameter_mm=4.60659, max_piston_stroke_mm=60.0)", "volUnit": "unit(prefix=<UnitPrefix.milli: -3>, unitid=<VolumeUnit.litres: 68>)", "flowUnit": "unit(prefix=<UnitPrefix.milli: -3>, unitid=<VolumeUnit.litres: 68>, time_unitid=<TimeUnit.per_second: 1>)"},
                                                                        "B0.0": {"params": "syringe(inner_diameter_mm=10.3006, max_piston_stroke_mm=60.0)", "volUnit": "unit(prefix=<UnitPrefix.milli: -3>, unitid=<VolumeUnit.litres: 68>)", "flowUnit": "unit(prefix=<UnitPrefix.milli: -3>, unitid=<VolumeUnit.litres: 68>, time_unitid=<TimeUnit.per_second: 1>)"},
                                                                        "C0.0": {"params": "syringe(inner_diameter_mm=7.283659999999999, max_piston_stroke_mm=60.0)", "volUnit": "unit(prefix=<UnitPrefix.milli: -3>, unitid=<VolumeUnit.litres: 68>)", "flowUnit": "unit(prefix=<UnitPrefix.milli: -3>, unitid=<VolumeUnit.litres: 68>, time_unitid=<TimeUnit.per_second: 1>)"},
                                                                    },
                                                                },
                                            'pumpingPumps_target': ['A0.0', 'C0.0']
                                        }

config['test_graph'] =  {
                            'graph_target': r'FilesForTests\graph_target.py',   # edited prior to publication
                            'positions':experimentFolder + "\\graph_test_positions.py",
                            'findClosest': {'node': 'densiViscoIN', 'candidates': ['A0.0', 'B0.0', 'C0.0'], 'closest_target': 'A0.0', 'pathToClosest_target': ['A0.0', 'A0.1', 'Av.1', 'M1.1', 'M1.0', 'ArdV_0_1.0', 'ArdV_0_1_0.0', 'V4.0', 'V4.8', 'densiViscoIN']},
                            'findPath': {'start_node': 'A0.0', 'end_node': 'waste_1', 'path_direct_target': ['A0.0', 'A0.1', 'Av.0', 'V1.0', 'V1.10', 'waste_1'], 'via': ['densiViscoIN', 'V5.0'], 'path_via_target': ['A0.0', 'A0.1', 'Av.1', 'M1.1', 'M1.0', 'ArdV_0_1.0', 'ArdV_0_1_0.0', 'V4.0', 'V4.8', 'densiViscoIN', 'densiViscoOUT', 'V5.8', 'V5.0', 'waste_1']},
                            'checkConsistency': {"path_nodes": experimentFolder + "\\nodes_test.csv", "path_edges": experimentFolder + "\\edges_test.csv", "path_tubing_match": experimentFolder + "\\tubing_test.csv", "path_tubing_newNode": experimentFolder + "\\tubing_test_newNode.csv", "path_tubing_newEdge": experimentFolder + "\\tubing_test_newEdge.csv", "path_tubing_newEdgeAndNode": experimentFolder + "\\tubing_test_newEdgeAndNode.csv"},
                            'appendEdge': {'edgeName': "0488-CC-2"},
                            'valveNames': ["V1.0", "V5.3", "V3.4", "V4.2", "V2.9", "V3.1", "V5.6", "V4.8", "V2.10"],
                            'valves': ["V1", "V5", "V3", "V4", "V2", "V3", "V5", "V4", "V2"],
                            'nodelist': ['A0.0', 'A0.1', 'Av.1', 'M1.1', 'M1.0', 'ArdV_0_1.0', 'ArdV_0_1_0.0', 'V4.0', 'V4.9', 'nmrIN', 'nmrOUT', 'V5.9', 'V5.0', 'waste_1'],
                            'edgeDict_target': {'0215-NN-1': {'name': '0215-NN-1', 'designation': ('A0.0', 'A0.1'), 'ends': 'NN', 'length': 215.0, 'diameter': 0.3, 'dead_volume': 0.0152, 'status': 'empty'},
                                                '0000-XX-1': {'name': '0000-XX-1', 'designation': ('A0.1', 'Av.1'), 'ends': 'XX', 'length': 106.1, 'diameter': 0.6, 'dead_volume': 0.03, 'status': 'empty'},
                                                '0289-NN-3': {'name': '0289-NN-3', 'designation': ('Av.1', 'M1.1'), 'ends': 'NN', 'length': 289.0, 'diameter': 0.3, 'dead_volume': 0.0204, 'status': 'empty'},
                                                '0004-XX-101': {'name': '0004-XX-101', 'designation': ('M1.1', 'M1.0'), 'ends': 'XX', 'length': 14.77, 'diameter': 1.0, 'dead_volume': 0.0116, 'status': 'empty'},
                                                '0052-YY-1': {'name': '0052-YY-1', 'designation': ('M1.0', 'ArdV_0_1.0'), 'ends': 'YY', 'length': 52.0, 'diameter': 0.3, 'dead_volume': 0.0037, 'status': 'empty'},
                                                '0000-YY-1': {'name': '0000-YY-1', 'designation': ('ArdV_0_1.0', 'ArdV_0_1_0.0'), 'ends': 'XX', 'length': 106.1, 'diameter': 0.6, 'dead_volume': 0.03, 'status': 'empty'},
                                                '0404-NT': {'name': '0404-NT', 'designation': ('ArdV_0_1_0.0', 'V4.0'), 'ends': 'NT', 'length': 404.0, 'diameter': 0.3, 'dead_volume': 0.0286, 'status': 'empty'},
                                                '0004-XX-39': {'name': '0004-XX-39', 'designation': ('V4.0', 'V4.9'), 'ends': 'XX', 'length': 14.77, 'diameter': 1.0, 'dead_volume': 0.0116, 'status': 'empty'},
                                                '2622-NT-2': {'name': '2622-NT-2', 'designation': ('V4.9', 'nmrIN'), 'ends': 'NT', 'length': 2622.0, 'diameter': 1.6, 'dead_volume': 5.2718, 'status': 'empty'},
                                                '0116-FF-1': {'name': '0116-FF-1', 'designation': ('nmrIN', 'nmrOUT'), 'ends': 'FF', 'length': 116.0, 'diameter': 2.4, 'dead_volume': 0.4373, 'status': 'empty'},
                                                '5264-NT-1': {'name': '5264-NT-1', 'designation': ('nmrOUT', 'V5.9'), 'ends': 'NT', 'length': 5264.0, 'diameter': 1.6, 'dead_volume': 10.5839, 'status': 'empty'},
                                                '0004-XX-49': {'name': '0004-XX-49', 'designation': ('V5.9', 'V5.0'), 'ends': 'XX', 'length': 14.77, 'diameter': 1.0, 'dead_volume': 0.0116, 'status': 'empty'},
                                                '0488-CC-3': {'name': '0488-CC-3', 'designation': ('V5.0', 'waste_1'), 'ends': 'CC', 'length': 488.0, 'diameter': 1.6, 'dead_volume': 0.9812, 'status': 'empty'}},
                            'quantity': 'dead_volume',
                            'totalQuantity_target': 17.4369,
                            'valveSettings_target': {'Av': 1, 'V4': 8, 'V5': 8},
                            'nodelist_noValve': ['M1.1', 'M1.0', 'V4.0'],
                            'nodelist_wrongPath': ['nmrIN', 'nmrOUT', 'V5.9', 'V5.0', 'V5.8', 'densiViscoIN'],
                            'openEnds': ['ambient', 'waste_1', 'waste_2',
                                        'A0.0', 'B0.0', 'C0.0',
                                        'V1.3', 'V1.4', 'V1.5', 'V1.6', 'V1.7', 'V1.8',
                                        'V2.3', 'V2.4', 'V2.5', 'V2.6', 'V2.7', 'V2.8',
                                        'V3.3', 'V3.4', 'V3.5', 'V3.6', 'V3.7', 'V3.8',
                                        'V4.1', 'V4.2', 'V4.3', 'V4.4', 'V4.5', 'V4.6', 'V4.7', 'V4.10',
                                        'V5.1', 'V5.2', 'V5.3', 'V5.4', 'V5.5', 'V5.6', 'V5.7',
                                        'Reservoir1', 'Reservoir2', 'Reservoir3',
                                        'Solvent1', 'Solvent2', 'Solvent3'],
                        }

config['test_solutionHandler'] =    {
                                        'chemical_test': {'name': 'LiPF6', 'molarMass': 151.91, 'molarMassUncertainty': 0.0, 'density': 2.83, 'densityUncertainty': 0.0},
                                        'chemicalsDict_target': {'LiPF6': {'name': 'LiPF6', 'molarMass': 151.91, 'molarMassUncertainty': 0, 'molarMassUnit': 'g/mol', 'density': 2.83, 'densityUncertainty': 0, 'densityUnit': 'g/cm^3'}, 'EC': {'name': 'EC', 'molarMass': 88.06, 'molarMassUncertainty': 0, 'molarMassUnit': 'g/mol', 'density': 1.320, 'densityUncertainty': 0, 'densityUnit': 'g/cm^3'}, 'EMC': {'name': 'EMC', 'molarMass': 104.1, 'molarMassUncertainty': 0, 'molarMassUnit': 'g/mol', 'density': 1.010, 'densityUncertainty': 0, 'densityUnit': 'g/cm^3'}, 'DMC': {'name': 'DMC', 'molarMass': 90.08, 'molarMassUncertainty': 0, 'molarMassUnit': 'g/mol', 'density': 1.070, 'densityUncertainty': 0, 'densityUnit': 'g/cm^3'}},
                                        'solution_test': {'name': '1M_LiPF6_EC-EMC', 'chemicalMasses': {'LiPF6': 30.38, 'EC': 63.086, 'EMC': 146.734, 'DMC': 0.0}, 'chemicalMassesUncertainties': {'LiPF6': 0.001, 'EC': 0.001, 'EMC': 0.001, 'DMC': 0.0}, 'chemicals': ['LiPF6', 'EC', 'EMC', 'DMC'], 'mass': 240.203, 'massUncertainty': 0.001, 'massUnit': 'g', 'density': 1.2, 'densityUncertainty': 0.01, 'densityUnit': 'g/cm^3', 'reservoir': 'Reservoir1', 'pump': 'A0.0', 'substanceAmountPerVolume': {'LiPF6': 0.0009990891086778535, 'EC': 0.0035789623469260124, 'EMC': 0.007041786377590972, 'DMC': 0.0}},
                                        'substanceAmountPerVolume_target': {'LiPF6': 0.0009990891086778535, 'EC': 0.0035789623469260124, 'EMC': 0.007041786377590972, 'DMC': 0.0},
                                        'parameterDict': {'chemicalsDict': 'FilesForTests\\chemicalsDict.py'},  # edited prior to publication
                                        'density': 1.57,
                                        'density_std': 0.03,
                                        'solutionsDict_target': {'1M_LiPF6_EC-EMC': {'name': '1M_LiPF6_EC-EMC', 'chemicalMasses': {'LiPF6': 30.38, 'EC': 63.086, 'EMC': 146.734, 'DMC': 0.0}, 'chemicalMassesUncertainties': {'LiPF6': 0.001, 'EC': 0.001, 'EMC': 0.001, 'DMC': 0.0}, 'chemicals': ['LiPF6', 'EC', 'EMC', 'DMC'], 'mass': 240.203, 'massUncertainty': 0.001, 'massUnit': 'g', 'density': 1.2, 'densityUncertainty': 0.01, 'densityUnit': 'g/cm^3', 'reservoir': 'Reservoir1', 'pump': 'A0.0', 'substanceAmountPerVolume': {'LiPF6': 0.0009990891086778535, 'EC': 0.0035789623469260124, 'EMC': 0.007041786377590972, 'DMC': 0.0}}, '1M_LiPF6_DMC': {'name': '1M_LiPF6_DMC', 'chemicalMasses': {'LiPF6': 30.38, 'EC': 0.0, 'EMC':0.0, 'DMC': 205.62}, 'chemicalMassesUncertainties': {'LiPF6': 0.001, 'EC': 0, 'EMC': 0, 'DMC': 0.001}, 'chemicals': ['LiPF6', 'EC', 'EMC', 'DMC'], 'mass': 236.003, 'massUncertainty': 0.001, 'massUnit': 'g', 'density': 1.18, 'densityUncertainty': 0.01, 'densityUnit': 'g/cm^3', 'reservoir': 'Reservoir2', 'pump': 'B0.0', 'substanceAmountPerVolume': {'LiPF6': 0.0009999214606829178, 'EC': 0.0, 'EMC': 0.0, 'DMC': 0.011413043196029458}}, '1M_LiPF6_EC-DMC': {'name': '1M_LiPF6_EC-DMC', 'chemicalMasses': {'LiPF6': 30.38, 'EC': 114.81, 'EMC': 0.0, 'DMC': 114.81}, 'chemicalMassesUncertainties': {'LiPF6': 0.001, 'EC': 0.001, 'EMC': 0.0, 'DMC': 0.001}, 'chemicals': ['LiPF6', 'EC', 'EMC', 'DMC'], 'mass': 260.003, 'massUncertainty': 0.001, 'massUnit': 'g', 'density': 1.3, 'densityUncertainty': 0.01, 'densityUnit': 'g/cm^3', 'reservoir': 'Reservoir3', 'pump': 'C0.0', 'substanceAmountPerVolume': {'LiPF6': 0.0009999226339800899, 'EC': 0.006518775566915509, 'EMC': 0.0, 'DMC': 0.006372595208954038}}},
                                        'mixingRatios': {'molarFractions': {'A':  {'LiPF6': 0.079102705, 'EC': 0.096164075, 'EMC': 0.016712457, 'DMC': 0.808020763},
                                                                            'B':  {'LiPF6': 0.078999358, 'EC': 0.268490408, 'EMC': 0.183642672, 'DMC': 0.468867561},
                                                                            'C':  {'LiPF6': 0.083178421, 'EC': 0.148919892, 'EMC': 0.293007292, 'DMC': 0.474894395},
                                                                            'D':  {'LiPF6': 0.08598133, 'EC': 0.3080045, 'EMC': 0.60601417},
                                                                            'E':  {'LiPF6': 0.080866727, 'EC': 0.221809771, 'EMC': 0.239269797, 'DMC': 0.458053705},
                                                                            'F':  {'LiPF6': 0.07373814, 'EC': 0.376180277, 'EMC': 0.003048239, 'DMC': 0.547033344}}},
                                        'volFrac_targets': {'A': {'volumeFractions': {'1M_LiPF6_EC-EMC': 0.03, '1M_LiPF6_DMC': 0.8, '1M_LiPF6_EC-DMC': 0.17},
                                                                 'setRatio': {'LiPF6': 0.079102705, 'EC': 0.096164075, 'EMC': 0.016712457, 'DMC': 0.808020763},
                                                                 'minSquaredError': 1e-06},
                                                            'B': {'volumeFractions': {'1M_LiPF6_EC-EMC': 0.33, '1M_LiPF6_DMC': 0.33, '1M_LiPF6_EC-DMC': 0.34},
                                                                 'setRatio': {'LiPF6': 0.078999358, 'EC': 0.268490408, 'EMC': 0.183642672, 'DMC': 0.468867561},
                                                                 'minSquaredError': 1e-06},
                                                            'C': {'volumeFractions': {'1M_LiPF6_EC-EMC': 0.5, '1M_LiPF6_DMC': 0.5},
                                                                 'setRatio': {'LiPF6': 0.083178421, 'EC': 0.148919892, 'EMC': 0.293007292, 'DMC': 0.474894395},
                                                                 'minSquaredError': 1e-06},
                                                            'D': {'volumeFractions': {'1M_LiPF6_EC-EMC': 1.0},
                                                                 'setRatio': {'LiPF6': 0.08598133, 'EC': 0.3080045, 'EMC': 0.60601417},
                                                                 'minSquaredError': 1e-06},
                                                            'E': {'volumeFractions': {'1M_LiPF6_EC-EMC': 0.42, '1M_LiPF6_DMC': 0.39, '1M_LiPF6_EC-DMC': 0.19},
                                                                 'setRatio': {'LiPF6': 0.080866727, 'EC': 0.221809771, 'EMC': 0.239269797, 'DMC': 0.458053705},
                                                                 'minSquaredError': 1e-06},
                                                            'F': {'volumeFractions': {'1M_LiPF6_EC-EMC': 0.00587, '1M_LiPF6_DMC': 0.214821, '1M_LiPF6_EC-DMC': 0.779309},
                                                                 'setRatio': {'LiPF6': 0.07373814, 'EC': 0.376180277, 'EMC': 0.003048239, 'DMC': 0.547033344},
                                                                 'minSquaredError': 1e-06}
                                                           }
                                    }
