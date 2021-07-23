''' Test the functionalities of the system status. '''
from helpers import LoadFile
from hardware.graph import loadGraph, drawGraph
import os
os.chdir(r"..") # https://stackoverflow.com/questions/1810743/how-to-set-the-current-working-directory#1810760  # edited prior to publication
from experiment import SystemStatus

testPath = ['A0.0', 'A0.1', 'Av1', 'V1.1', 'V1.0', 'V2.0', 'V2.7', 'V3.0', 'V3.1', 'Reservoir1']
testGraph, valvePositionDict = loadGraph(r"tests/setup_test.pck", r"tests/valvePositionDict_test.pck")
testPositions = LoadFile(r"tests/setup_positions_test.pck")

drawGraph(testGraph, testPositions)