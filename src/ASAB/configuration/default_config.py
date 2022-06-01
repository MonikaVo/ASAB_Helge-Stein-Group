config = dict()

projectFolder = ".." # edited prior to publication
experimentFolder = "src\\ASAB\\hardware" # edited prior to publication

config["balanceDriver"] = {"serialPort": "<COM port>",
                    "settings": {'baudrate': 115200, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 0, 'write_timeout': None, 'inter_byte_timeout': None},
                    "simulated": True}

config["balance"] = {"simulated": True}

config["CetoniDeviceDriver"] = {"availableSyringes": experimentFolder + "\\syringes.txt",
                    "configPath": projectFolder + "...\\ASAB_Conf4_sim", # edited prior to publication
                    "syringeConfig": {"A0.0": "10_mL", "B0.0": "10_mL", "C0.0": "10_mL", "D0.0": "10_mL", "E0.0": "10_mL", "F0.0": "10_mL"},
                    "valvePositionDict": experimentFolder + "\\valvePositionDict.txt",
                    "setup": experimentFolder + "\\setup.txt",
                    "flow": 0.05,
                    "simulateBalance": True}

config["CetoniDevice"] = {"waste": "waste_1",
                    "gas": "ambient",
                    "pathsToClean": [],
                    "measureVolumes": {"densioVisco": 3.0, "uvVis": 0.0182},
                    "assignment": {"A0.0": "Reservoir6", "B0.0": "Reservoir5", "C0.0": "Reservoir4", "D0.0": "Reservoir3", "E0.0": "Reservoir2", "F0.0": "Reservoir1"},
                    "compoundsReservoirs": {"LiPF6_salt_in_EC_DMC_1:1": "Reservoir6", "EC_DMC_1:1": "Reservoir5", "LiPF6_salt_in_EC_EMC_3:7": "Reservoir4", "EC_EMC_3:7": "Reservoir3", "Hexane": "Reservoir2", 'EMC': 'Reservoir1'}}

config["densioVisco"] = {"measure": {"inputFolder": "...\\input"}} # edited prior to publication

config["syringes"] = {"savePath": experimentFolder + "\\syringes.txt"}

config["graph"] = {"pathNodes": experimentFolder + "\\nodes.csv",
                    "pathEdges": experimentFolder + "\\edges.csv",
                    "pathTubing": experimentFolder + "\\tubing.csv",
                    "savePath": experimentFolder + "\\setup.txt",
                    "saveNameValvePositionDict": experimentFolder + "\\valvePositionDict.txt"}