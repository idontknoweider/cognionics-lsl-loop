# System import
import sys
import numpy as np


def dict_bash_kwargs():
    """
    This function returns a dictionary containing the keyword arguments given in bash as 
    a dictionary for better handling. The arguments in bash should have the following 
    form: argument1=something . If there are ANY spaces there, the computer will interpret
    it as different arguments. One can also put strings like arg="here we can use spaces".
    """

    args = []
    for i in range(len(sys.argv) - 1):
        arg = str(sys.argv[i+1]).split("=")
        args.append(arg)
    return dict(args)


def rowcol_paradigm():
    """
    This function defines a list containing the rowcol paradigm 
    of BCI spellers to make it easier to decypher using only 
    indices for the columns and rows from 1 to 6 since we have 
    36 characters.
    """
    char1 = ["A", "B", "C", "D", "E", "F"]
    char2 = ["G", "H", "I", "J", "K", "L"]
    char3 = ["M", "N", "O", "P", "Q", "R"]
    char4 = ["S", "T", "U", "V", "W", "X"]
    char5 = ["Y", "Z", "0", "1", "2", "3"]
    char6 = ["4", "5", "6", "7", "8", "9"]
    return [char1, char2, char3, char4, char5, char6]


def dataset_probe(dataset):
    print("! DATASET: !")

    feat = dataset["features"]
    rc = dataset["rowcol"]
    flg = dataset["flags"]

    # Check the dataset's characteristics and print them out
    print("Length of features, rowcol and flags: {0}, {1}, {2}".format(
        len(feat), len(rc), len(flg)))
    print("Length of the first 5 feature arrays:")
    i = 0
    for i in range(5):
        print("\t Data item number {0} has length {1}".format(i, len(feat[i])))
        print("\t \t and rowcol {0} and flag {1}".format(rc[i], flg[i]))
    print("\t Last data item number has length {0}".format(len(feat[-1])))
    print("Each item of the flags has a type {0}".format(type(flg[0])))
    print("\n")


def preprocess_erp(erp_array):
    """
    This function is used to change the format of the ERP data from the
    dataset used to train LDA and networks. It takes the (#channels
    + rowcol + flag) x # features array and turns it into 3 lists, that
    contain different lists for different packets of row/column augmentations.

    INPUT:
        erp_array: An array shape 11 x # data points, being channels 10 the 
            rowcol indicator (6 rows and 6 columns ==> 1 to 12) and the channel
            11 the trigger indicator (whether the augmented rowcol is the one
            the user is focusing on (1) or not (0)).
    OUTPUT:
        Dictionary, containing three lists of the same length (number of
            sequences). First one contains lists with the features
    """

    # Initialize the lists that are going to hold all the arrays and values
    features = []
    rowcol = []
    flags = []

    # Start the iterations
    first_index = 0
    for i in range(erp_array.shape[1]):
        # If there's data in the temp list and it is a different rowcol, store it as a feature vector
        if i+1 == erp_array.shape[1] or erp_array[9, i] != erp_array[9, i+1]:
            # Save features of this chunk to list
            features.append(erp_array[0:9, first_index:i+1])
            rowcol.append(erp_array[9, i])
            flags.append(erp_array[10, i])

            # First index for next chunk is next index
            first_index = i+1

    ## Here we standarise the features' vectors to have the same
    ##  normal lengths, because we can find anomalous vectors.

    # Define standard lengths
    std_len_1 = features[3].shape[1]
    std_len_2 = features[4].shape[1]

    # Check which elements have length equal to the standar length
    index = 0
    while np.all(features[index] != features[-1]):
        iter_len = features[index].shape[1]

        # If elements have different length remove them
        if iter_len != std_len_1 and iter_len != std_len_2:
            del(features[index])
            del(rowcol[index])
            del(flags[index])
        else:   # Deletion puts the next item in the deleted spot, this else avoids missing items
            index += 1

    ## Compacting and making feature vectors for the training and testing
    # Start iterating over all the items in the lists
    iter_ = 0   
    while np.all(features[iter_] != features[-1]):
        # The flatten does the channel concatenation
        features[iter_] = np.append(features[iter_], features[iter_ + 1], axis = 0).flatten() 
        del(features[iter_ + 1])
        del(rowcol[iter_ + 1])
        del(flags[iter_ + 1])
        iter_ += 1

    # Transform into an array
    features = np.asarray(features)
    rowcol = np.asarray(rowcol)
    flags = np.asarray(flags)

    # Return a dictionary with the feature vectors and labels.
    return {"features": features, "rowcol": rowcol, "flags": flags}