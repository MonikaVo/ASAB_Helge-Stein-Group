import nmrglue as ng
#dic,data = ng.jcampdx.read("avg1.jdx")
#print(data)

#import nmrpy
#import os, sysconfig
#fname = os.path.join(sysconfig.get_paths()['purelib'], 'nmrpy', 'tests', 'test_data', 'mytest3.fid')
#fid_array = nmrpy.from_path(fname)
#print(nmrpy.from_path(fname))

import pandas as pd
import matplotlib.pyplot as plt
from jcamp import JCAMP_reader
import pickle
import numpy as np
import os


# class creates objects which have the attribute "dict of spectrum_values"
class spectrum_values():
    def __init__(self, dict):
        self.spectrum = dict

# plot graph from dict
def plot_graph_from_dict(dict):  # https://stackoverflow.com/questions/43431347/python-dictionary-plot-matplotlib
    plt.plot(dict.keys(), dict.values())
    plt.ylabel("Intensity")
    plt.xlabel("Frequency")
    plt.show()

# converts all jdx files in the directory into pickle saved in the same directory, jdx files have to be opened and saved by mnova
def convert_mnova_jdx_to_pickle(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jdx'):       # https://stackoverflow.com/questions/59597634/iterate-over-files-in-directory-and-use-file-names-as-variables-and-assign-the
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                filename_dict = directory+'/dict_'+filename
                filename_dict = filename_dict[:-4]      # remove .jdx
                #print(filename_dict)
                dict = {}
                # print(file)
                jcamp_dict = JCAMP_reader(f)
                for i in range(len(jcamp_dict['y'])):
                    dict[jcamp_dict['x'][i]] = jcamp_dict['y'][i]
                outfile = open(filename_dict, 'wb')     # https://www.datacamp.com/community/tutorials/pickle-python-tutorial
                pickle.dump(dict, outfile)
                outfile.close()
                print(dict)

# convert jdx to pickle which come directly from spinflow and saves them in the same directory
def convert_spinflow_jdx_to_pickle(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jdx'):       # https://stackoverflow.com/questions/59597634/iterate-over-files-in-directory-and-use-file-names-as-variables-and-assign-the
            f = os.path.join(directory, filename)
            print(os.getcwd() + f)
            if os.path.isfile(f):
                filename_dict = directory+'/dict_'+filename
                filename_dict = filename_dict[:-4]      # remove .jdx

                linein = pd.read_csv(directory + '/' + filename, engine = 'python', sep = "  ", names = ["x", "y"], header = None)
                #print(linein)
                x = linein.loc[:, "x"]
                #x = x[85:32854]+x[32856:65624]
                y = linein.loc[:, "y"]
                #y = y[85:32854]+y[32856:65624]

                dict = {}
                for i in range(len(x)):
                    if (i >= 85 and i <32853) or (i >= 32855 and i < 65623):
                        dict[float(x[i])] = y[i]
                print(dict)
                outfile = open(filename_dict, 'wb')  # https://www.datacamp.com/community/tutorials/pickle-python-tutorial
                pickle.dump(dict, outfile)
                outfile.close()



# loads all pickles in the directory into dict named with the filename, each filename is class spectrum_values() and has its spectrum as attribute
def load_pickles(directory):
    dict = {}
    for filename in os.listdir(directory):
        if filename.startswith('dict'):  # https://stackoverflow.com/questions/59597634/iterate-over-files-in-directory-and-use-file-names-as-variables-and-assign-the
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                #print(filename)
                load_file = open(directory+'/'+filename, 'rb')
                out = pickle.load(load_file)
                load_file.close()
                end_of_filename = filename[-4:]
                print(end_of_filename)
                end_of_filename_spectrum = spectrum_values(out)
                dict[end_of_filename] = end_of_filename_spectrum
    return(dict)

# convert dict into numpy array
def dict_into_array(dict):      # https://appdividend.com/2021/01/08/how-to-convert-python-dictionary-to-array/
    keys = np.fromiter(dict.keys(), dtype=float)        # https://stackoverflow.com/questions/23668509/dictionary-keys-and-values-to-separate-numpy-arrays
    vals = np.fromiter(dict.values(), dtype=float)
    return keys, vals

#convert_spinflow_jdx_to_pickle("spinflow_jdx_files_EtOH00")
EtOH30 = load_pickles("spinflow_jdx_files_EtOH30")
print(EtOH30)
plot_graph_from_dict(EtOH30['avg5'].spectrum)
#print(EtOH30['vg10'].spectrum)
# fid_array = dict_into_array(EtOH30['avg1'].spectrum)
# print(fid_array[0])





