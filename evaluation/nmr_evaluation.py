from jcamp import JCAMP_reader
import pickle
import os

# method converts jdx files (saved by mnova, not by spinflow) into pickles containing a dict, (x:y)
def convert_jdx_to_pickle(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.jdx'):       # https://stackoverflow.com/questions/59597634/iterate-over-files-in-directory-and-use-file-names-as-variables-and-assign-the
            f = os.path.join(directory, filename)
            if os.path.isfile(f):
                filename_dict = directory+'/dict_'+filename
                filename_dict = filename_dict[:-4]      # remove .jdx ending of file
                dict = {}
                jcamp_dict = JCAMP_reader(f)
                for i in range(len(jcamp_dict['y'])):
                    dict[jcamp_dict['x'][i]] = jcamp_dict['y'][i]
                outfile = open(filename_dict, 'wb')     # https://www.datacamp.com/community/tutorials/pickle-python-tutorial
                pickle.dump(dict, outfile)
                outfile.close()

convert_jdx_to_pickle('jdx_files_EtOH100')