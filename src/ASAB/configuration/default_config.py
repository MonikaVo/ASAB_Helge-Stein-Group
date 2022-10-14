config = dict()

projectFolder = ".." # edited prior to publication
experimentFolder = "src\\ASAB\\hardware" # edited prior to publication

config["balanceDriver"] =   {
                                "serialPort": "<COM port>", # edited prior to publication
                                "settings": {'baudrate': 115200, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'xonxoff': False, 'dsrdtr': False, 'rtscts': False, 'timeout': 0, 'write_timeout': None, 'inter_byte_timeout': None},
                                "simulated": True
                            }

config["balance"] = {
                        "simulated": True
                    }

config["CetoniDeviceDriver"] =  {
                                    "availableSyringes": experimentFolder + "\\syringes.txt",
                                    "configPath": projectFolder + "...\\ASAB_Conf4_sim", # edited prior to publication
                                    "syringeConfig": {"A0.0": "10_mL", "B0.0": "10_mL", "C0.0": "10_mL", "D0.0": "10_mL", "E0.0": "10_mL", "F0.0": "10_mL"},
                                    "valvePositionDict": experimentFolder + "\\valvePositionDict.txt",
                                    "setup": experimentFolder + "\\setup.txt",
                                    "flow": 0.05,
                                    "simulateBalance": True
                                }

config["CetoniDevice"] =    {
                                "waste": "waste_1",
                                "gas": "ambient",
                                "pathsToClean": [],
                                "measureVolumes": {"densiVisco": 3.0, "uvVis": 0.0182},
                                "assignment": {"A0.0": "Reservoir6", "B0.0": "Reservoir5", "C0.0": "Reservoir4", "D0.0": "Reservoir3", "E0.0": "Reservoir2", "F0.0": "Reservoir1"},
                                "compoundsReservoirs": {"LiPF6_salt_in_EC_DMC_1:1": "Reservoir6", "EC_DMC_1:1": "Reservoir5", "LiPF6_salt_in_EC_EMC_3:7": "Reservoir4", "EC_EMC_3:7": "Reservoir3", "Hexane": "Reservoir2", 'EMC': 'Reservoir1'},
                                "stockSolutionsReservoirs": {"LiPF6_salt_in_EC_DMC_1:1": "Reservoir6", "DMC": "Reservoir5", "LiPF6_salt_in_EC_EMC_3:7": "Reservoir4", "EC_EMC_3:7": "Reservoir3", "Hexane": "Reservoir2", 'EMC': 'Reservoir1'}
                            }

config["densioVisco"] = {
                            "measure": {"inputFolder": "...\\input"} # edited prior to publication
                        }

config["syringes"] =    {
                            "savePath": experimentFolder + "\\syringes.txt"
                        }

config["graph"] =   {
                        "pathNodes": experimentFolder + "\\nodes.csv",
                        "pathEdges": experimentFolder + "\\edges.csv",
                        "pathTubing": experimentFolder + "\\tubing.csv",
                        "savePath": experimentFolder + "\\setup.txt",
                        "saveNameValvePositionDict": experimentFolder + "\\valvePositionDict.txt"
                    }

config["ArduinoDriver"] =   {
                                "serialPort": '<COM port>',
                                "settings": {'baudrate': 9600, 'timeout': 1},
                                "simulated": False
                            }

config["solutionHandler"] = {
                                'chemicals': [{'shortName': 'LiPF6', 'name': 'lithium hexafluorophosphate', 'molarMass': 151.90, 'molarMassUnit': 'g/mol'},
                                                {'shortName': 'EC', 'name': 'ethylene carbonate', 'molarMass': 88.06, 'molarMassUnit': 'g/mol'},
                                                {'shortName': 'EMC', 'name': 'ethyl methyl carbonate', 'molarMass': 104.10, 'molarMassUnit': 'g/mol'},
                                                {'shortName': 'DMC', 'name': 'dimethyl carbonate', 'molarMass': 90.08, 'molarMassUnit': 'g/mol'}],
                                'solutions':[{'name': "LiPF6_salt_in_EC_DMC_1:1", 'mix': {'LiPF6': {'value': 1., 'unit': 'mol/L'}, 'EC': {'value': 0.50, 'unit': 'g/g'}, 'DMC': {'value': 0.50, 'unit': 'g/g'}}, 'density': 1.2879, 'reservoir': 'Reservoir6'},
                                            {'name': "DMC", 'mix': {'DMC': {'value':1., 'unit': 'g/g'}}, 'density': 1.07, 'reservoir': 'Reservoir5'}, # TODO: Adjust the density!!!!! References: https://www.chemspider.com/Chemical-Structure.11526.html, https://www.sigmaaldrich.com/DE/en/sds/sial/517127
                                            {'name': "LiPF6_salt_in_EC_EMC_3:7", 'mix': {'LiPF6': {'value': 1., 'unit': 'mol/L'}, 'EC': {'value': 0.30, 'unit': 'g/g'}, 'EMC': {'value': 0.70, 'unit': 'g/g'}}, 'density': 1.1964, 'reservoir': 'Reservoir4'},
                                            {'name': "EC_EMC_3:7", 'mix': {'EC': {'value': 0.30, 'unit': 'g/g'}, 'EMC': {'value': 0.70, 'unit': 'g/g'}}, 'density': 1.1013, 'reservoir': 'Reservoir3'}]
                            }
