# https://realpython.com/linear-regression-in-python/

import numpy as np
from numpy import log as ln     # https://www.delftstack.com/howto/numpy/natural-log-python/
from sklearn.linear_model import LinearRegression
import math
import pandas as pd

gyromagn_ratio = 2.675*10**8        # rad*T^(-1)*s^(-1)
gradient_length = 0.004     # sec, D71
diffusion_time = 0.025      # sec, D74
maximum_gradient = 0.2977       # T*m^(-1)
relative_gradient = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

# import values to evaluate
values = pd.read_csv("values.csv", sep=",")

# print(values)
# print(values.loc[1, "triplet"])


def find_D(values):
    # calculate the values of the x-axis
    x = np.array([None]*len(relative_gradient))
    for i in range(10):
        # formula from excel sheet
        x[i] = 2*(gyromagn_ratio**2)*((gradient_length*(2/math.pi))**2)*((maximum_gradient*relative_gradient[i])**2)*(diffusion_time/2-(gradient_length*(2/math.pi))/3)*(10**(-9))
    x = x.reshape((-1, 1))
    print(x)

    y_trip = []
    # calculate the values of the y-axis
    for i in range(11):
        y_trip = y_trip + [values.loc[i, "triplet"]]
    # print(y_trip)
    y_quart = []
    for i in range(11):
        y_quart = y_quart + [values.loc[i, "quartet"]]
    # print(y_quart)
    y_trip_fin = []
    y_quart_fin = []


    for i in range(len(y_trip)-1):
        y_trip_fin = y_trip_fin + [ln(y_trip[i+1]/y_trip[0])]
    print(y_trip_fin)

    for i in range(len(y_quart)-1):
        y_quart_fin = y_quart_fin + [ln(y_quart[i+1]/y_quart[0])]
    # print(y_quart_fin)
    # fit

    trip = LinearRegression().fit(x, y_trip_fin)
    print("r_sq: ", trip.score(x, y_trip_fin))
    print("intercept: ", trip.intercept_)
    print("slope: ", trip.coef_[0])

    quart = LinearRegression().fit(x, y_quart_fin)
    print("r_sq: ", quart.score(x, y_quart_fin))
    print("intercept: ", quart.intercept_)
    print("slope: ", quart.coef_[0])


    return(trip.coef_[0], quart.coef_[0])

print(find_D(values))
