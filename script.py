# EEG

# General imports
import numpy as np
import random as rand
import time
import sys

# Plotting imports
# import matplotlib.pyplot as plt
# import matplotlib.animation as anim
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

# Networking imports
from pylsl import StreamInlet, resolve_stream
from pylsl import StreamInfo, StreamOutlet, local_clock

# Stimuli Imports
import psychopy as pp

# Custom functions import (used for analysis for example)
# import functions

## Debugging functions
# Function that allows the software to simulate a Lab Streaming Layer streaming output
def virtual_cognionics(channels = 8, frequency = 500, chunk_size = 1, buffer_size = 360, \
    dtype = "random"):

    """ 
    Here we create a data stream output so that we can test the rest of the networking
    properties without having a proper output, like the one from Cognionics DAQ software.
    This function will output random data to a number of channels given as an argument
    (8 by default) at a given frequency in Hertz (100 by default).

    For the purpose of being close to the actual cognionics signal, the data sent will be
    formatted with metada as if it came from the actual cognionics headset. 5 more channels
    are added normally appart from the channels for the sensors.

    There are no required arguments for the function to work, but some keyword arguments
    with default values exist in order for the function to be flexible.

    INPUT:
        channels: The number of sensor that the supposed Cognionics EEG would have working
        frequency: The amount of samples sent per second
        chunk_size: If the samples are going to be sent in chunks of data, then change this
            number to how many samples per chunk
        buffer_size: The size of the buffer (in seconds) that will hold the data
        dtype: "random" or "sinusoid" to choose which type of data will be sent (random is 
            the default)

    OUTPUT: There's no output.
    """

    # Here we define some metadata of the stream (Name, type, number of channels,
    # frequency, data type and serial number/unique identifier).
    stream_info = StreamInfo("Virtual Cognionics Quick-20", "EEG", channels + 5, frequency,\
        "float32", "myuid000000")

    # Attach some extra meta-data (accordance with XDF format)
    channels_handle = stream_info.desc().append_child("channels")
    channels_labels = ["P8", "P7", "Pz", "P4", "P3", "O1", "O2", "A2",\
         "ACC8", "ACC9", "ACC10", "Packet Counter", "TRIGGER"]
    for label in channels_labels:
        ch = channels_handle.append_child("channel")
        ch.append_child_value("label", label)
        ch.append_child_value("unit", "microvolts")
        ch.append_child_value("type", "EEG")
    stream_info.desc().append_child_value("extra info", "none")

    # Here we create an outlet with our information, sending information in chunks of
    # 1 sample and the outgoing buffer size being 360 seconds (max.)
    chunk_size = 1
    buffer_size = 20
    outlet = StreamOutlet(stream_info, chunk_size, buffer_size)

    # Now here we create the samples and push them to the network
    print("Now sending data...")
    t0 = local_clock()
    while True:
        # Get the timestamp with t0 as a reference for initial time
        stamp = local_clock() - t0

        # Here we create the sample with random data
        if dtype == "random":
            sample = list(np.random.rand(channels + 5))
        elif dtype == "sinusoid":
            sample = [np.sin(500*stamp)] * (channels + 5)

        # Now we send it and wait to send the next one
        outlet.push_sample(sample, stamp)
        time.sleep(1/frequency)
    
## Job functions
# Define some functions that allow the software to connect to the server
def lsl_connect(**kwargs):

    """
    This function connects the computer to a Lab Streaming Layer data stream, either
    in the network or in the same computer.
    
    The function accepts keyword arguments that define the data stream we are searching.
    Normally this would be (use keywords given between quotes as key for the argument) 
    "name" (e.g. "Cognionics Quick-20"), "type" (e.g. "EEG"), "channels" (e.g. 8), "freq"
    (from frequency, e.g. 500), "dtype" (type of data, e.g. "float32"), "serialn" 
    (e.g. "quick_20")

    After receiving the information of the stream, the script searchs for it in the network
    and resolves it, and then connects to it (or the first one in case there are many, that's
    the reason why one has to be as specific as possible if many instances of LSL are being used
    in the lab). It prints some of the metadata of the data stream to the screen so the user
    can check if it is right, and returns the inlet to be used in other routines

    INPUT:
        **kwargs: Keyword arguments defining the data stream

    OUTPUT:
        inlet: Inlet for the software to retrieve that from the LSL data stream.
    """

    # Put the known information of the stream in a tuple. It is better to know as much
    # as possible if more than one kit is running LSL at the same time.
    stream_info = []
    for key, val in kwargs.items():
        stream_info.append(key)
        stream_info.append(val)

    # Resolve the stream on the lab network
    print("Looking for data stream...")
    stream = resolve_stream(*stream_info)
    print("Data stream found. Retrieving data...")

    # Create a new inlet tor read from the stream
    inlet = StreamInlet(stream[0])

    # Get stream information (including custom meta-data) and break it down
    metainfo = inlet.info()
    print("The stream's XML meta-data is: ")
    print(metainfo.as_xml())

    # Return said inlet
    return inlet 

# Define a function to collect data via given data inlet and process it
def pull_process(inlet, func, chunk_size, **kwargs):
    """ 
    This function is meant to be the function used to iterate over when pulling 
    and processing is needed.

    The way the function works is collecting the data in the stream and checking
    if there is enough data to process it (amount needed defined by chunk_size).
    If there is not, data is buffered to use when there is. When there is enough
    (either instantly got or buffered) data will be used.

    INPUT:
        inlet: The data stream inlet handle
        fun: The function used for processing. It should have a format of function(time, data)
        chunk_size: The amount of data points used for the processing
        kwargs: Keyword arguments to put into the inlet.pull_chunk method
    
    OUTPUT:
        timestamps: A numpy array containing the timestamps for the collected data.
        data: Collected data in this iteration.
        processed_data OR []: Note that sometimes due to having low amounts of data to process
            the function might return an empty list. Additional exceptions must be made in 
            the programs this is implemented to not overwrite actual data with useless lists.
            It is implemented this way to keep having the same number of outputs.
        output_proc: A flag used to signal if there is an output of processed data. This might
            make things easier to avoid issues with using the function.
    """
    # Retrieve data from the data stream
    chunk, timestamps = inlet.pull_chunk(**kwargs)

    # Only does something if data arrives
    if timestamps:
         # Initialize simple buffers if they haven't been already
        global data_buffer
        global stamp_buffer
        if not "data_buffer" in globals():
            data_buffer = []
            stamp_buffer = []

        # Add data chunk to buffer and compare the size to the required size
        data_buffer.append(chunk)
        stamp_buffer.append(timestamps)

        # Create a flag to see whether or not to output processed data
        output_proc = False

        # Compare size of buffer to that required size for processing.
        # If large enough or larger, process and continue storing extra data.
        if len(data_buffer) >= chunk_size:
            data = np.array(data_buffer)[:chunk_size]
            time = np.array(stamp_buffer)[:chunk_size]

            # Process data channel by channel
            processed_data = []
            for i in range(inlet.channel_count):
                processed_temp = func(time, data_buffer[:, i])
                processed_data.append(processed_temp)

            # Get rid of already used data
            stamp_buffer = stamp_buffer[chunk_size:]
            data_buffer = data_buffer[chunk_size:]

            # Order the function to output the processed data
            output_proc = True

        # Return raw and processed data with timestamps
        if output_proc:
            return timestamps, data, processed_data, output_proc
        else:
            return timestamps, data, [], output_proc

## Main
# To execute if script is executed as main (direct execution, not as an import)
if __name__ == "__main__":

    # Connect via LSL to data stream
    print("Searching for stream...")
    inlet = lsl_connect(type = "EEG")

    # Get the number of channels from the inlet to use later
    channelsn = inlet.info().channel_count()

    # Create the PyQtGraph window
    plot_duration = 5
    win = pg.GraphicsWindow()
    win.setWindowTitle("LSL Plot " + inlet.info().name())
    plt = win.addPlot()
    plt.setLimits(xMin = 0.0, xMax = plot_duration, yMin = -1.0 * \
        (inlet.channel_count - 1), yMax = 1.0)
    
    t0 = [local_clock()] * inlet.channel_count
    curves = []
    for ch_ix in range(inlet.channel_count):
        curves += [plt.plot()]

    def update():
        # Be able to modify this global variables
        global inlet, curves, t0
        chunk, timestamps = inlet.pull_chunk(timeout = 0.0)
        if timestamps:
            timestamps = np.asarray(timestamps)
            y = np.asarray(chunk)

            for ch_ix in range(inlet.channel_count):
                old_x, old_y = curves[ch_ix].getData()
                if old_x is not None:
                    old_x += t0[ch_ix]
                    this_x = np.hstack((old_x, timestamps))
                    this_y = np.hstack((old_y, y[:, ch_ix] - ch_ix))
                else:
                    this_x = timestamps
                    this_y = y[:, ch_ix] - ch_ix
                t0[ch_ix] = this_x[-1] - plot_duration
                this_x -= t0[ch_ix]
                b_keep = this_x >= 0
                curves[ch_ix].setData(this_x[b_keep], this_y[b_keep])

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(2)
    QtGui.QApplication.instance().exec_()




    """  Create the figure we're going. We're going to use a different subplot
    #   for each channel.
    fig, ax = plt.subplots(channelsn, 1, facecolor = "white", figsize = (12, 10))        

    # Generate holders for data
    data = np.zeros([channelsn, 100])
    X = np.linspace(0, 100, data.shape[-1])

    # Generate line plots
    lines = []
    for i in range(len(data)):
        line, = ax[i].plot(X, 5*i + data[i], color = "black", lw = 2)
        lines.append(line)

    # Set y limit (or first line will be cropped)
    # ax.set_ylim(-1, 60)

    # No ticks
    for i in range(channelsn):
        ax[i].set_xticks([])
        ax[i].set_yticks([])

    # Define updater
    def pull_and_draw(*args):
        sample, _ = inlet.pull_sample()
        
        # Shift all data to the right
        data[:, 1:] = data[:, :-1]

        # Fill-in new values
        data[:,0] = sample[:]

        # Update data
        for i in range(len(data)):
            lines[i].set_ydata(5*i + data[i])

        # Return modified artists
        return lines

    animation = anim.FuncAnimation(fig, pull_and_draw, interval = 2)
    plt.show()
        
 """