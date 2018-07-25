# BCI Speller using EEG (Quick-20 Dry Headset from Cognionics Inc.)

# System imports
import sys

# General imports
import numpy as np
import scipy as sp

# Networking imports
from pylsl import StreamInlet, resolve_stream, local_clock

# Stimuli Imports
import psychopy as pp

# Custom imports
from classes import LslStream, Stimuli, LslBuffer, EmojiStimulus
from functions import dict_bash_kwargs, save_sequence




## Main ##
if __name__ == "__main__":
    ## CONNECTION TO STREAM ##
    print("-- STREAM CONNECTION --")
    # Connect to the stream and create the stream handle
    print("Connecting to data stream...")
    data_stream = LslStream(type="EEG")

    # Connect to the impedances stream
    # Yeah, whoever wrote the tags in the CogDAQ software wrote this one wrong
    impedances_stream = LslStream(type="Impeadance")

    # Get the number of channels from the inlet to use later
    channelsn = data_stream.inlet.channel_count
    print("Number of channels on the stream: {0}".format(channelsn))

    # Get the nominal sampling rate (rate at which the server sends information)
    srate = data_stream.inlet.info().nominal_srate()
    print("The sampling rate is: {0} \n".format(srate))

    ## STIMULUS INITIALISATION ##
    print("-- STIMULUS SETUP -- ")
    # Initialise the stimulus
    estimulus = EmojiStimulus()
    estimulus.experiment_setup(num_trials = 2)

    # Print the shuffling sequence
    print("Emoji stimuli shuffling sequence:")
    print(estimulus.aug_shuffle)

    # Print some useful values
    print("Duration of each sequence: {0}".format(estimulus.sequence_duration))
    ammount = int(np.ceil(estimulus.sequence_duration * srate))
    print("Ammount of samples per sequence: {0}".format(ammount))

    ## CREATE THE BUFFER ##
    # Create a buffer to hold the samples
    buffer = LslBuffer()
    imp_buffer = LslBuffer()

    ## VIRTUAL COGNIONICS EXCEPTION ##
    # For virtual_cognionics notify the stream
    if data_stream.inlet.info().name() == "Virtual Cognionics Quick-20":
        print("Stream is Virtual Cognionics Quick-20")
        start = data_stream.chunk()
        start_imp = impedances_stream.chunk()
        wait_text = pp.visual.TextStim(win=estimulus.window, pos=[0, 0],
                                       text="Wait please...")
        wait_text.draw()
        estimulus.window.flip()
        pp.clock.wait(5)

    ## START THE EXPERIMENT ##
    print("\n -- EXPERIMENT STARTING --")
    prediction_list = []
    # Tell the stream to start
    for t in range(estimulus.num_trials):
        for s in range(estimulus.num_seq):
            # Play sequence number s according to aug_shuffle
            estimulus.play_seq(s)

            # Read the data during the sequence (giving some room for error)
            buffer.add(data_stream.chunk(max_samples=ammount))
            imp_buffer.add(impedances_stream.chunk(max_samples=ammount))

            # Save just the last part of the data (the one that has to belong to the trial)
            data = np.asarray(buffer.take_new(ammount, filename="voltages_t{0}_s{1}_".format(t+1, s+1)))
            imp_buffer.take_new(ammount, filename="impedances_t{0}_s{1}_".format(t+1, s+1))
            print("The shape of the data array {0}: {1}".format(
                s + 1, np.shape(data)))

            # Here we would have the part where the sequence is processed to find the choice
            # PUT MODEL HERE FOR DATA PROCESSING HAVING data AND estimulus.aug_shuffle INTO ACCOUNT
            prediction_list.append(4)

            # Wait the Inter Sequence Interval time
            pp.clock.wait(estimulus.iseqi)

        # Here we would cramp al the single choices into a final one
        final_prediction = prediction_list[0]

        # Shuffle again the augmentations
        estimulus.shuffle()

        # Confirm the choice
        print("\n -- GROUND TRUTH --")
        confirmation = estimulus.confirm(final_prediction, transform = False)

        # Save the array
        save_file_name = "t{0}_test.txt".format(t+1)
        save_sequence(save_file_name, estimulus.aug_shuffle, prediction_list, final_prediction, confirmation[0], confirmation[1])

        # Zip the EEG data files
        buffer.zip()
        imp_buffer.zip()

        # Clear buffers
        buffer.clear(names=True)
        imp_buffer.clear(names=True)

    # Close everything
    estimulus.quit()
