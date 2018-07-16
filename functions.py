# System import
import sys


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


def erp_into_chunks(erp_array, concatenate=False):
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
        concatenate: Take the 9 data channels and concatenate them in each of the
            bins to create a one dimensional feature vector of length 9 x single
            channel feature length
    OUTPUT:
        Dictionary, containing three lists of the same length (number of
            sequences). First one contains lists with the features
    """

    # Initialize the lists that are going to hold all the
    features = []
    rowcol = []
    flags = []

    # Condition to know whether or not create empty lists for temp holding items
    init_loop = True

    # Start the iterations
    for i in range(erp_array.shape[1]):
        # Extract the information from the erp_array
        data = erp_array[0:9, i]
        rowcol_ind = erp_array[9, i]
        flag = erp_array[10, i]

        # If there's data in the temp list and it is a different rowcol, store it as a feature vector
        if rowcol != [] and rowcol_ind != rowcol[-1]:
            # Set flag to reset temp lists
            init_loop = True

            # In case we want the features to be concatenated
            if concatenate == True:
                concatenation = []
                for i in range(len(features_temp)):
                    concatenation.extend(features_temp[i])
                features_temp = concatenation

            # Save temp lists to final lists
            features.append(features_temp)

        # Initialize temporary lists
        if init_loop == True:
            # this is going to hold all the channels
            features_temp = [[] for i in range(9)]
            init_loop = False

            # This is used to not repeat the same rowcol or flag over and over in the list
            first_flag = True

        # Add the data to the temp lists
        for i in range(len(features_temp)):
            features_temp[i].append(data[i])

        # If first data sample in sequence, save rowcol and flag
        if first_flag == True:
            rowcol.append(rowcol_ind)
            flags.append(flag)
            first_flag = False

    # Return a dictionary with the feature vectors and so on. Rowcol and
    #   flags have an extra value due to the implementation.
    return {"features": features, "rowcol": rowcol[:-1], "flags": flags[:-1]}


def rowcol_paradigm():
    """
    This function defines a list containing the rowcol paradigm to make
    it easier to decypher using only indices for the columns and
    rows from 1 to 6 since we have 36 characters.
    """
    char1 = ["A", "B", "C", "D", "E", "F"]
    char2 = ["G", "H", "I", "J", "K", "L"]
    char3 = ["M", "N", "O", "P", "Q", "R"]
    char4 = ["S", "T", "U", "V", "W", "X"]
    char5 = ["Y", "Z", "0", "1", "2", "3"]
    char6 = ["4", "5", "6", "7", "8", "9"]
    return [char1, char2, char3, char4, char5, char6]
