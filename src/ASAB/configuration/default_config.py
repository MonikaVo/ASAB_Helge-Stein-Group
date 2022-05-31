config = dict()

baseFolder = ".." # edited prior to publication
experimentFolder = "..." # edited prior to publication

config["balanceDriver"] = {"serialPort": "<COM port>",
                    "settings": {'baudrate': 115200, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 0, 'write_timeout': None, 'inter_byte_timeout': None},
                    "simulated": True}

config["balance"] = {"simulated": True}

config["CetoniDeviceDriver"] = {"availableSyringes": experimentFolder + "\\syringes.txt",
                    "configPath": baseFolder + "...\\ASAB_Conf1_sim", # edited prior to publication
                    "syringeConfig": {"A0.0": "10_mL", "B0.0": "10_mL", "C0.0": "10_mL", "D0.0": "10_mL", "E0.0": "10_mL", "F0.0": "10_mL"},
                    "valvePositionDict": experimentFolder + "\\valvePositionDict.txt",
                    "setup": experimentFolder + "\\setup.txt",
                    "flow": 0.03,
                    "simulateBalance": True}

config["CetoniDevice"] = {"waste": "waste_1",
                    "gas": "ambient",
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
                        ['E0.0', 'E0.1', 'Ev1', 'V1.5', 'V1.0', 'V2.0', 'V2.6', 'FY2', 'FY1', 'Fv2', 'F0.1', 'F0.0']],  # TODO: Should not be necessary anymore
                    "measureVolumes": {"densioVisco": 5.0, "uvVis": 0.0182},
                    "assignment": {"A0.0": "Reservoir6", "B0.0": "Reservoir5", "C0.0": "Reservoir4", "D0.0": "Reservoir3", "E0.0": "Reservoir2", "F0.0": "Reservoir1"},   # TODO: Needs adjustment to allow for more flexibility
                    "compoundsReservoirs": {"LiPF6_salt_in_EC_DMC_1:1": "Reservoir1", "EC_DMC_1:1": "Reservoir2", "LiPF6_salt_in_EC_EMC_3:7": "Reservoir3", "EC_EMC_3:7": "Reservoir4", "Hexane": "Reservoir6"}}

config["densioVisco"] = {"measure": {"inputFolder": "...\\input"}} # edited prior to publication

config["syringes"] = {"savePath": experimentFolder + "\\syringes.txt"}

config["graph"] = {"pathNodes": experimentFolder + "\\nodes.csv",
                    "pathEdges": experimentFolder + "\\edges.csv",
                    "pathTubing": experimentFolder + "\\tubing.csv",
                    "savePath": experimentFolder + "\\setup.txt",
                    "saveNameValvePositionDict": experimentFolder + "\\valvePositionDict.txt"}