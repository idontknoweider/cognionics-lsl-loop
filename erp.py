## IMPORT LIBRARIES ##
import numpy as np
import torch
from classes import ERPDataset as ERP
import glob
import sklearn
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from functions import dataset_probe, rowcol_paradigm
import random

## MAIN ##
# First we are going to load every ERP data file
erp_data_list = []
path_list = glob.glob("Visual ERP BNCI\\*.mat")
for file_ in path_list:
    erp_data_list.append(ERP(file_))

# Create a list containing the characters used in the speller
chars = rowcol_paradigm()

# Create LDA
lda = LDA(solver="lsqr", shrinkage="auto")

# Score list
train_data = []
test_data = []

# Load random dataset from the list and probe the training and test sets
for i in range(len(erp_data_list)):
    erp_set = erp_data_list[i]

    # Extract train and test sets
    trdat = erp_set.train_data
    # dataset_probe(trdat)

    tsdat = erp_set.test_data
    # dataset_probe(tsdat)

    # Separate features, rowcol and flags
    trfeat = trdat["features"]
    trrc = trdat["rowcol"]
    trflg = trdat["flags"]

    tsfeat = tsdat["features"]
    tsrc = tsdat["rowcol"]
    tsflg = tsdat["flags"]

    # Train LDA and test it
    lda.fit(trfeat, trflg)
    score = lda.score(tsfeat, tsflg)
    print("Set {0}, score = {1}".format(path_list[i].split("\\")[-1].split(".")[-2], score))
