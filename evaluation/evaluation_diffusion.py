# https://realpython.com/linear-regression-in-python/

import numpy as np
from numpy import log as ln     # https://www.delftstack.com/howto/numpy/natural-log-python/
from sklearn.linear_model import LinearRegression
import math

gyromagn_ratio = 2.675*10**8        # rad*T^(-1)*s^(-1)
gradient_length = 0.004     # sec, D71
diffusion_time = 0.025      # sec, D74
maximum_gradient = 0.2977       # T*m^(-1)
relative_gradient = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

x = np.array([None]*len(relative_gradient))
for i in range(10):
    # formula from excel sheet
    x[i] = 2*(gyromagn_ratio**2)*((gradient_length*(2/math.pi))**2)*((maximum_gradient*relative_gradient[i])**2)*(diffusion_time/2-(gradient_length*(2/math.pi))/3)*(10**(-9))
x = x.reshape((-1, 1))
print(x)

y_int = [1800000, 1800000, 1720000, 1610000, 1470000, 1310000, 1140000, 971595, 807925, 655689, 519834]
y = []
for i in range(len(y_int)-1):
    y = y + [ln(y_int[i+1]/y_int[0])]
print(y)


model = LinearRegression().fit(x, y)
print("r_sq: ", model.score(x, y))
print("intercept: ", model.intercept_)
print("slope: ", model.coef_[0])