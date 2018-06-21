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
    # If extra arguments have been written when calling the script
    args = dict_bash_kwargs()

    # Window size for processing (in seconds)
    if "window_size" in args:
        sampling_window_size = args["window_size"]
    else:
        sampling_window_size = 500  # Supposing 500 Hz srate

    # Connect to the stream and create the stream handle
    data_stream = lsl_stream(type="EEG")

    # Get the number of channels from the inlet to use later
    channelsn = data_stream.inlet.channel_count
    print("Number of channels on the stream: {0}".format(channelsn))

    # Get the nominal sampling rate (rate at which the server sends information)
    srate = data_stream.inlet.info().nominal_srate()
    print("The sampling rate is: {0}".format(srate))

    # Initialise the stimulus
    estimulus = emoji_stimulus()
    estimulus.experiment_setup()

    print("Emoji stimuli shuffling sequence:")
    print(estimulus.aug_shuffle)

    # Create a buffer to hold the samples
    buffer = lsl_buffer()

    # Start the experiment
    # For virtual_cognionics notify the stream
    _ = data_stream.chunk()
    ammount = int(np.floor(estimulus.sequence_duration * srate))

    pp.clock.wait(1)
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
        print(np.shape(data))
        #_, flag = identity(data[:,-1], data[:,:-1])

        # Wait the Inter Sequence Interval time
        pp.clock.wait(estimulus.iseqi)

    buffer.zip()
    estimulus.quit()
