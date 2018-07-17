## IMPORT LIBRARIES ##
import numpy as np
import torch
from classes import ERPDatasetCustom as ERPDC
import glob
import sklearn
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from functions import rowcol_paradigm, dataset_probe, compact_dataset
import random

## MAIN ##
# First we are going to load every ERP data file
erp_data_list = []
path_list = glob.glob("Visual ERP BNCI\\*.mat")
for file_ in path_list:
    erp = ERPDC(file_)
    erp_data_list.append(ERPDC(file_))

# Create a list containing the characters used in the speller
chars = rowcol_paradigm() 

# Load random dataset from the list and probe the training and test sets
erp_set = erp_data_list[random.randint(0,len(erp_data_list))]

trdat = compact_dataset(erp_set.train_data)
dataset_probe(trdat)

tsdat = compact_dataset(erp_set.test_data)
dataset_probe(tsdat)

# Separate features, rowcol and flags
trfeat = trdat["features"]
trrc = trdat["rowcol"]
trflg = trdat["flags"]

tsfeat = tsdat["features"]
tsrc = tsdat["rowcol"]
tsflg = tsdat["flags"]

# Select the correct data from the features list. Take the ones with the largest ammount of features
std_len = len(trfeat[2])    # Standard length
std_bool_list = np.asarray([len(item) for item in trfeat]) == std_len
std_trfeat = np.asarray(trfeat)[std_bool_list]
std_trflg = np.asarray(trflg)[std_bool_list]
std_tsfeat = np.asarray(tsfeat)[std_bool_list]
std_tsflg = np.asarray(tsflg)[std_bool_list]

std_trfeat = np.array([np.array(item) for item in std_trfeat])
std_tsfeat = np.array([np.array(item) for item in std_tsfeat])

# Check the length of these fellow arrays
print("Length of the standarised training feature and flags arrays: {0} ; {1}".format(len(std_trfeat), len(std_trflg)))
print("Length of the first item of the std training feature list: {0}".format(len(std_trfeat[0])))
print("Type of the features: {0}, {1}, {2}".format(type(std_trfeat), type(std_trfeat[0]), type(std_trfeat[0][0])))
print("Type of the flags: {0}".format(type(std_trflg[0])))
print("Length of the standarised test feature and flags arrays: {0} ; {1}".format(len(std_tsfeat), len(std_tsflg)))
print("Length of the first item of the std test feature list: {0}".format(len(std_tsfeat[0])) + "\n")
print("Size of this stuff: {1}, {0}".format(std_trflg.shape, std_trfeat.shape))

for i in range(len(std_trfeat)):
    if len(std_trfeat[i]) != std_len:
        raise ValueError("WARNING: SOMETHING IS WRONG WITH DIMENSIONS")
    if type(std_trflg[i]) != np.float64:
        raise ValueError("nonfloat")

# Create LDA model
lda = LDA()
lda.fit(std_trfeat, std_trflg)
prediction = lda.predict(std_tsfeat)
print(prediction - std_tsflg)
print(trflg)