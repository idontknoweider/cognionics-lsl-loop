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
from objects import lsl_stream, stimuli, lsl_buffer, emoji_stimulus
from functions import dict_bash_kwargs, identity

## Main ##
if __name__ == "__main__":
    ## CONNECTION TO STREAM ##
    print("-- STREAM CONNECTION --")
    # Connect to the stream and create the stream handle
    print("Connecting to data stream...")
    data_stream = lsl_stream(type="EEG")

    # Get the number of channels from the inlet to use later
    channelsn = data_stream.inlet.channel_count
    print("Number of channels on the stream: {0}".format(channelsn))

    # Get the nominal sampling rate (rate at which the server sends information)
    srate = data_stream.inlet.info().nominal_srate()
    print("The sampling rate is: {0} \n".format(srate))

    ## STIMULUS INITIALISATION ##
    print("-- STIMULUS SETUP -- ")
    # Initialise the stimulus
    estimulus = emoji_stimulus()
    estimulus.experiment_setup()

    # Print the shuffling sequence
    print("Emoji stimuli shuffling sequence:")
    print(estimulus.aug_shuffle)

    # Print some useful values
    print("Duration of each sequence: {0}".format(estimulus.sequence_duration))
    ammount = int(np.ceil(estimulus.sequence_duration * srate))
    print("Ammount of samples per sequence: {0}".format(ammount))

    ## CREATE THE BUFFER ##
    # Create a buffer to hold the samples
    buffer = lsl_buffer()

    ## VIRTUAL COGNIONICS EXCEPTION ##
    # For virtual_cognionics notify the stream
    if data_stream.inlet.info().name() == "Virtual Cognionics Quick-20":
        print("Stream is Virtual Cognionics Quick-20")
        start = data_stream.chunk()
        wait_text = pp.visual.TextStim(win=estimulus.window, pos=[0, 0],
                                       text="Wait please...")
        wait_text.draw()
        estimulus.window.flip()
        pp.clock.wait(2)
        pretty = data_stream.chunk(max_samples=2)
        please = data_stream.chunk(max_samples=2)
        print("Is {0} this {1} working {2}?".format(
            np.shape(start), np.shape(pretty), np.shape(please)))

    ## START THE EXPERIMENT ##
    print("-- EXPERIMENT STARTING --")
    # Tell the stream to start
    for s in range(estimulus.num_seq):
        for e in range(estimulus.num_emojis):
            # Move blue rectangle and draw everything
            estimulus.stimuli.items[-1].pos = (
                estimulus.imXaxis[estimulus.aug_shuffle[s, e]], 0)
            estimulus.stimuli.draw()

            # Window flip
            estimulus.window.flip()

            # Wait the aug_dur time
            pp.clock.wait(estimulus.aug_dur)

            # Draw just the emojis, getting rid of the rectangle
            estimulus.stimuli.draw_int(0, -1)

            # Window flip
            estimulus.window.flip()

            # Pause aug_wait time
            pp.clock.wait(estimulus.aug_wait)

        # Read the data during the sequence (giving some room for error)
        buffer.add(data_stream.chunk(max_samples=ammount))

        # Save just the last part of the data (the one that has to belong to the trial)
        data = np.asarray(buffer.take_new(ammount))
        print("The shape of the data array {0}: {1}".format(
            s + 1, np.shape(data)))

        # Here we would have the part where the sequence is processed to find the choice
        choice = 4

        # Wait the Inter Sequence Interval time
        pp.clock.wait(estimulus.iseqi)

    # Here we would cramp al the single choices into a final one
    final_choice = choice

    # Confirm the choice
    estimulus.confirm(final_choice)

    # Close everything
    buffer.zip()
    estimulus.quit()
