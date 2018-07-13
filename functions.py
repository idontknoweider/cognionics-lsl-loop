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


def erp_into_chunks(erp_array, concatenate = False):
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

        # Create a list to hold each set of features if required
        if init_loop == True:
            features_temp = [[] for i in range(9)] # this is going to hold all the channels
            rowcol_temp = []
            flags_temp = []
            init_loop = False

        # Extract the information from the erp_array
        data = erp_array[0:9, i]
        rowcol_ind = erp_array[9, i]
        flag = erp_array[10, i]

        # If there's data in the temp list and it is a different rowcol, store it as a feature vector
        if rowcol_temp != [] and rowcol_ind != rowcol_temp[-1]:
            init_loop = True
            # In case we want the features to be concatenated
            if concatenate == True:
                concatenation = []
                for i in range(len(features_temp)):
                    concatenation.extend(features_temp[i])
                features_temp = concatenation
            
            features.append(features_temp)
            rowcol.append(rowcol_temp)
            flags.append(flags_temp)
        else:
            for i in range(len(features_temp)):
                features_temp[i].append(data[i])
            rowcol_temp.append(rowcol_ind)
            flags_temp.append(flag)

    # Return a dictionary with the feature vectors and so on.
    return {"features": features, "rowcol": rowcol, "flags": flags}
