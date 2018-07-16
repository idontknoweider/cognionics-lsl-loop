## IMPORT LIBRARIES ##
import numpy as np
import torch
from classes import ERPDatasetCustom as ERPDC
import glob
import sklearn
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from functions import rowcol_paradigm

## MAIN ##
# First we are going to load every ERP data file
erp_data_list = []
path_list = glob.glob("Visual ERP BNCI\\*.mat")
for file_ in path_list:
    erp = ERPDC(file_)
    erp_data_list.append(ERPDC(file_))

# Create a list containing the characters used in the speller
chars = rowcol_paradigm()


erp1 = erp_data_list[1]
erp_ = erp1.train_data
data = erp_["features"]
rowcol = erp_["rowcol"]
flags = erp_["flags"]
# print("Type of the erp1 train data: {0}".format(type(erp_)))
# print("This should be lenght 3 for having features, rowcol and flag: {0}".format(len(erp_)))
# print("This should be the length of the feature stuff: {0}".format(len(data)))
# print("This should be the length of the rowcol and labels stuff which should be similar to the thing before: {0} ; {1}".format(len(rowcol), len(flags)))
# print("This is the length of a single feature array: {0} {1}".format(len(data), len(data[0])))
# print("Last item of rowcol and flags are: {0}, {1}".format(rowcol[-1], flags[-1]))

# for i in range(12):
#     print("Data item number {0} has length {1}".format(i, len(data[i])))

# sum_ = sum(num > 12 for num in rowcol)
# sum_2 = sum(num == 0 for num in rowcol)
# print("There are {0} values inside rowcol that are larger than 12. WHAT. \n But there also are {1} values that are 0.".format(sum_, sum_2))
# zeros = [len(data[i+1]) for i in range(len(rowcol)-1) if rowcol[i+1] == 0]
# avg_len = sum(zeros)/len(zeros)
# print("The avg length of the items with zeroes as rowcol is {0}".format(avg_len))

# triggers = sum(flags)
# print("The number of target triggers is: {0}".format(triggers))
# print("Len last data: {0}".format(len(data[-1])))
triggers_ = np.asarray(rowcol)[np.asarray(flags) == 1]

print(triggers_)
print(len(triggers_))


string = ""

for i in np.arange(0, len(triggers_), 2):
    inda = int(triggers_[i])
    indb = int(triggers_[i+1])
    if inda <= indb:
        string_ex = chars[indb-7][inda-1]
    else:
        string_ex = chars[inda-7][indb-1]
    if string == "" or string[-1] != string_ex:
        string += string_ex
print(string)

# Choose train data
boolarray = (np.asarray([len(item) for item in data]) == 396)

print([len(item) for item in data[2::2]])
print(sum(np.asarray([len(item) for item in data[2::2]]) > 400))


train_data = np.asarray(data)[boolarray]
train_flags = np.asarray(flags)[boolarray]

print(sum(np.asarray([len(item) for item in train_data]) != 396))

erp_tst = erp1.test_data
tstdata = erp_tst["features"]
tstrowcol = erp_tst["rowcol"]
tstflags = erp_tst["flags"]

print("Type of the erp1 train data: {0}".format(type(erp_tst)))
print("This should be lenght 3 for having features, rowcol and flag: {0}".format(
    len(erp_tst)))
print("This should be the length of the feature stuff: {0}".format(
    len(tstdata)))
print("This should be the length of the rowcol and labels stuff which should be similar to the thing before: {0} ; {1}".format(
    len(tstrowcol), len(tstflags)))
print("This is the length of a single feature array: {0} {1}".format(
    len(tstdata), len(tstdata[0])))
print("Last item of rowcol and flags are: {0}, {1}".format(
    tstrowcol[-1], tstflags[-1]))

for i in range(12):
    print("Data item number {0} has length {1}".format(i, len(tstdata[i])))

print("data len: {0} ; data flags: {1}".format(
    len(train_data), len(train_flags)))
# LDA STUFF
lda = LDA()
bla = np.asarray(train_data)
ble = np.asarray(train_flags)
lda.fit(train_data, train_flags)
