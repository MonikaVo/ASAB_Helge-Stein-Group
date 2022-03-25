import utility


config = dict()

projectFolder = "<path to project>" # edited prior to publication
auxiliaryFolderHardware = "filesForOperation\\hardware"

config["utility"] = {"ASAB": projectFolder + "...\\ASAB", # edited prior to publication
                    "QmixSDK_python": projectFolder + "...\\QmixSDK\\lib\\python", # edited prior to publication
                    "QmixSDK": projectFolder + "...\\QmixSDK"} # edited prior to publication

config["balanceDriver"] = {"serialPort": "<COM port>",
                    "settings": {'baudrate': 115200, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 0, 'write_timeout': None, 'inter_byte_timeout': None},
                    "simulated": False}

config["balance"] = {"simulated": False}

config["CetoniDeviceDriver"] = {"availableSyringes": auxiliaryFolderHardware + "\\syringes.pck",
                    "configPath": projectFolder + "...\\ASAB_Conf1", # edited prior to publication
                    "syringeConfig": {"A0.0": "10_ml", "B0.0": "10_ml", "C0.0": "2_5_ml", "D0.0": "2_5_ml", "E0.0": "1_ml", "F0.0": "1_ml"},
                    "pumps": auxiliaryFolderHardware + "\\Pumps.pck",
                    "valves": auxiliaryFolderHardware + "\\Valves.pck",
                    "channels": auxiliaryFolderHardware + "\\Channels.pck",
                    "valvePositionDict": auxiliaryFolderHardware + "\\valvePositionDict.pck",
                    "setup": auxiliaryFolderHardware + "\\setup.pck",
                    "flow": 0.03,
                    "simulateBalance": False}

config["CetoniDevice"] = {"waste": "Reservoir8",
                    "gas": "Reservoir7",
                    "pathsToClean": [['A0.0', 'A0.1', 'Av1', 'V1.1', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.1', 'Reservoir1'],
                        ['B0.0', 'B0.1', 'Bv1', 'V1.2', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.2', 'Reservoir2'],
                        ['C0.0', 'C0.1', 'Cv1', 'V1.3', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.3', 'Reservoir3'],
                        ['D0.0', 'D0.1', 'Dv1', 'V1.4', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.4', 'Reservoir4'],
                        ['E0.0', 'E0.1', 'Ev1', 'V1.5', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.5', 'Reservoir5'],
                        ['F0.0', 'F0.1', 'Fv1', 'V1.6', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.6', 'Reservoir6'],
                        ['F0.0', 'F0.1', 'Fv1', 'V1.6', 'V1.0', 'V2.0', 'V2.1', 'AY2', 'AY1', 'Av2', 'A0.1', 'A0.0'],
                        ['A0.0', 'A0.1', 'Av1', 'V1.1', 'V1.0', 'V2.0', 'V2.2', 'BY2', 'BY1', 'Bv2', 'B0.1', 'B0.0'],
                        ['B0.0', 'B0.1', 'Bv1', 'V1.2', 'V1.0', 'V2.0', 'V2.3', 'CY2', 'CY1', 'Cv2', 'C0.1', 'C0.0'],
                        ['C0.0', 'C0.1', 'Cv1', 'V1.3', 'V1.0', 'V2.0', 'V2.4', 'DY2', 'DY1', 'Dv2', 'D0.1', 'D0.0'],
                        ['D0.0', 'D0.1', 'Dv1', 'V1.4', 'V1.0', 'V2.0', 'V2.5', 'EY2', 'EY1', 'Ev2', 'E0.1', 'E0.0'],
                        ['E0.0', 'E0.1', 'Ev1', 'V1.5', 'V1.0', 'V2.0', 'V2.6', 'FY2', 'FY1', 'Fv2', 'F0.1', 'F0.0']],
                    "measureVolumes": {"densioVisco": 5.0, "uvVis": 0.0182}}

config["densioVisco"] = {"measure": {"inputFolder": "...\\input"}} # edited prior to publication

config["syringes"] = {"savePath": auxiliaryFolderHardware + "\\syringes.pck"}

config["graph"] = {"pathNodes": auxiliaryFolderHardware + "\\nodes.csv",
                    "pathEdges": auxiliaryFolderHardware + "\\edges.csv",
                    "pathTubing": auxiliaryFolderHardware + "\\tubing.csv",
                    "savePath": auxiliaryFolderHardware + "\\setup.pck",
                    "saveNameValvePositionDict": auxiliaryFolderHardware + "\\valvePositionDict.pck",
                    "pumpList": ["A0.0", "B0.0", "C0.0", "D0.0", "E0.0", "F0.0"]}