config = dict()

projectFolder = "<path to project>" # edited prior to publication
auxiliaryFolderHardware = "filesForOperation\\hardware"
experimentFolder = "experiments\\Hackathon"

config["utility"] = {"ASAB": projectFolder + "...\\ASAB", # edited prior to publication
                    "QmixSDK_python": projectFolder + "...\\QmixSDK\\lib\\python", # edited prior to publication
                    "QmixSDK": projectFolder + "...\\ASAB\\QmixSDK"} # edited prior to publication

config["balanceDriver"] = {"serialPort": "<COM port>",
                    "settings": {'baudrate': 115200, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 0, 'write_timeout': None, 'inter_byte_timeout': None},
                    "simulated": True}

config["balance"] = {"simulated": True}

config["CetoniDeviceDriver"] = {"availableSyringes": auxiliaryFolderHardware + "\\syringes.pck",
                    "configPath": projectFolder + "...\\ASAB_Conf1_sim", # edited prior to publication
                    "syringeConfig": {"A0.0": "10_ml", "B0.0": "10_ml", "C0.0": "25_ml", "D0.0": "25_ml", "E0.0": "25_ml", "F0.0": "25_ml"},
                    "pumps": experimentFolder + "\\Pumps.pck",
                    "valves": experimentFolder + "\\Valves.pck",
                    "channels": experimentFolder + "\\Channels.pck",
                    "valvePositionDict": experimentFolder + "\\valvePositionDict.pck",
                    "setup": experimentFolder + "\\setup.pck",
                    "flow": 0.01,
                    "simulateBalance": True}

config["CetoniDevice"] = {"waste": "Reservoir5",
                    "gas": "Reservoir3",
                    "pathsToClean": [],
                    "measureVolumes": {"densioVisco": 3.0, "uvVis": 0.0182},
                    "assignment": {"A0.0": "Reservoir1", "B0.0": "Reservoir2", "C0.0": "Reservoir3", "D0.0": "Reservoir4", "E0.0": "Reservoir6"},
                    "compoundsReservoirs": {"LiPF6_salt_in_EC_DMC_1:1": "Reservoir1", "EC_DMC_1:1": "Reservoir2", "LiPF6_salt_in_EC_EMC_3:7": "Reservoir3", "EC_EMC_3:7": "Reservoir4", "Hexane": "Reservoir6"}}

config["densioVisco"] = {"measure": {"inputFolder": "...\\input"}} # edited prior to publication

config["syringes"] = {"savePath": auxiliaryFolderHardware + "\\syringes.pck"}

config["graph"] = {"pathNodes": experimentFolder + "\\nodes.csv",
                    "pathEdges": experimentFolder + "\\edges.csv",
                    "pathTubing": experimentFolder + "\\tubing.csv",
                    "savePath": experimentFolder + "\\setup.pck",
                    "saveNameValvePositionDict": experimentFolder + "\\valvePositionDict.pck"}