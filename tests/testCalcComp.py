import calcComp
import chemicals
import unittest
import numpy as np


#chemList = chemicals.getChemicalsList("Chemicals_database.csv")
chemList = chemicals.loadChemicalsList("chemList")


# https://stackoverflow.com/questions/12136762/assertalmostequal-in-python-unit-test-for-collections-of-floats#12139899
#https://data-flair.training/blogs/python-unittest/

class t_calcComp:
    def test():
        np.testing.assert_almost_equal(calcComp.calcComp(chemList, [1, 1], ["EtOH", "H2O"], 2.0), [1.527549, 0.472451], decimal=5)
        np.testing.assert_almost_equal(calcComp.calcComp(chemList, [0.5, 0.5], ["EtOH", "H2O"], 2.0), [1.527549, 0.472451], decimal=5)
        np.testing.assert_almost_equal(calcComp.calcComp(chemList, [1, 2], ["hexane", "EtOH"], 1.0), [0.52798, 0.47202], decimal=5)
        np.testing.assert_almost_equal(calcComp.calcComp(chemList, [1, 2], ["hexane", "EtOH"], 0.5), [0.26399, 0.23601], decimal=5)
        np.testing.assert_almost_equal(calcComp.calcComp(chemList, [0.2, 0.7, 0.1], ["EtOH", "H2O", "hexane"], 1), [0.312397, 0.338171, 0.349432], decimal=5)
        np.testing.assert_almost_equal(calcComp.calcComp(chemList, [7, 15, 9], ["acetone", "toluene", "hexane"], 18),[2.82555, 8.7222 , 6.45225], decimal=5)


#    def testCalcComp(self):
#        self.assertEqual(calcComp.calcComp(chemList, [0.5, 0.5], ["EtOH", "H2O"], 2.0), [1.527549, 0.472451])
#    def testCalcComp2(self):
#        self.assertEqual(calcComp.calcComp(chemList, [1, 1], ["EtOH", "H2O"], 2.0), [1.527549, 0.472451])
#    def testCalcComp3(self):
#        self.assertEqual(calcComp.calcComp(chemList, [1, 2], ["hexane", "EtOH"], 1.0), [0.52798, 0.47202])
#    def testCalcComp4(self):
#        self.assertEqual(calcComp.calcComp(chemList, [1,2], ["hexane", "EtOH"], 0.5), [0.26399, 0.23601])
#    def testCalcComp5(self):
#        self.assertEqual(calcComp.calcComp(chemList, [0.2, 0.7, 0.1], ["EtOH", "H2O", "hexane"], 1), [0.312397, 0.338171, 0.349432])
#    def testCalcComp6(self):
#        self.assertEqual(calcComp.calcComp(chemList, [7, 15, 9], ["acetone", "toluene", "hexane"], 18), [2.842234, 8.712612, 6.445153])


t_calcComp.test()

#if __name__ == '__main__':
#    unittest.main

"""         https://realpython.com/python-comments-guide/#how-to-write-comments-in-python

amount = 3
M = [18, 46]
rho = [1, 0.8]
mixratio = 0.1


n_1 = amount / (M[0] / rho[0] + ((1 - mixratio) / (mixratio)) * (ethanol.molarMass / ethanol.density))
n_2 = (1 - mixratio) / (mixratio) * n_1
V_1 = n_1 * M[0] / rho[0]
V_2 = n_2 * M[1] / rho[1]
       # https://realpython.com/python-return-statement/

print("Two components")
print("substance amount ", n_1, n_2)
print("volume ", V_1, V_2)
print("total volume ", V_1+V_2)

#print("")
#print("Three components - Test 1")

x_1 = 0.8
x_2 = 2.8
x_3 = 0.4
mixratio = [x_1, x_2, x_3]
print(mixratio)

mixratio = [x_1/sum(mixratio), x_2/sum(mixratio), x_3/sum(mixratio)]

print(mixratio)

M_1 = 18
M_2 = 46
M_3 = 30
M = [M_1, M_2, M_3]

rho_1 = 1
rho_2 = 0.8
rho_3 = 1.3
rho = [rho_1, rho_2, rho_3]

#n_2 = amount / ((x_1*M_1)/((1-x_1)*rho_1) + ((1/x_2-1-(x_1/(1-x_1)))*M_1)/(rho_1*(x_2+x_1/(1-x_1))) + M_2/rho_2 + (1/x_2-1-x_1/(1-x_1)*M_3)/(rho_3*(x_2+x_1/(1-x_1))))
#n_3 = (n_2*(1/x_2-1-x_1/(1-x_1)))/(x_2+x_1/(1-x_1))
#n_1 = (x_1/(1-x_1)*(n_2+n_3))



#volume_1 = n_1*M_1/rho_1
#volume_2 = n_2*M_2/rho_2
#volume_3 = n_3*M_3/rho_3


#print("volume1 ", volume_1)
#print("volume2 ", volume_2)
#print("volume3 ", volume_3)
#print("total Volume ", volume_1+volume_3+volume_2)



print("")
print("Three components - Test 2")

volcalc = 0  # Calculate volume fraction-denominator
for i in range(3):
    volcalc = volcalc + mixratio[i] * M[i] / rho[i]
print(volcalc)

vol = []
for i in range(3):
    vol = vol + [mixratio[i] * M[i] / rho[i] / volcalc * amount]

print(vol)
print("total volume ", sum(vol))

"""