## IMPORT LIBRARIES ##
import numpy as np
import torch
from classes import ERPDatasetCustom as ERPDC
import glob
import sklearn
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA

## MAIN ##
# First we are going to load every ERP data file
erp_data_list = []
path_list = glob.glob("Visual ERP BNCI\\*.mat")
for file_ in path_list:
    erp = ERPDC(file_)
    erp_data_list.append(ERPDC(file_))

erp1 = erp_data_list[0]
erp_ = erp1.train_data
data = erp_["features"]
rowcol = erp_["rowcol"]
flags = erp_["flags"]
print("Type of the erp1 train data: {0}".format(type(erp_)))
print("This should be lenght 3 for having features, rowcol and flag: {0}".format(len(erp_)))
print("This should be the length of the feature stuff: {0}".format(len(data)))
print("This should be the length of the rowcol and labels stuff which should be similar to the thing before: {0} ; {1}".format(len(rowcol), len(flags)))
print("This is the length of a single feature array: {0} {1}".format(len(data), len(data[0])))
print("Don't mess with me: {0} {1}".format(len(data[1]), len(data[2])))
print("Don't fuck this up: {0} {1}".format(len(data[3]), len(data[4])))
print("This is the length of a single feature array: {0} {1}".format(len(data[5]), len(data[6])))
for i in range(len(data)):
    if i%2 == 0:
        stri = "even"
    else:
        stri = "odd"
    print("{0} is {1} and len: {2}".format(i, stri, len(data[i])))

print("This is the shitty rowcol for the first stuff features: {0}".format(set(rowcol[0])))



