# EEG

# General imports
import numpy as np
import random as rand
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import time

# Networking imports
from pylsl import StreamInlet, resolve_stream
from pylsl import StreamInfo, StreamOutlet, local_clock

# Stimuli Imports
import psychopy as pp

# Function that allows the software to simulate a Lab Streaming Layer streaming output
def virtual_cognionics(channels = 8, frequency = 500, chunk_size = 1, buffer_size = 360):
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

    OUTPUT: There's no output.
    """

    # Here we define some metadata of the stream (Name, type, number of channels,
    # frequency, data type and serial number/unique identifier).
    stream_info = StreamInfo("Virtual Cognionics Quick-20", "EEG", channels + 5, frequency, "float32", "myuid000000")

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
        sample = list(np.random.rand(channels + 5))
        # Now we send it and wait to send the next one
        outlet.push_sample(sample, stamp)
        time.sleep(1/frequency)
    

# Define some functions that allow the software to connect to the server
def connect_by_lsl(**kwargs):

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
    stream_info = tuple(stream_info)

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
    print("The channels' labels are as follows:")
    chan = metainfo.desc().child("chanels").child("channel")
    for _ in range(metainfo.channel_count()):
        print(" " + chan.child_value("label"))
        chan = chan.next_sibling()

    # Return said inlet
    return inlet 


# To execute if script is executed as main (direct execution, not as an import)
if __name__ == "__main__":

    # Connect via LSL to data stream
    print("Searching for stream...")
    inlet = connect_by_lsl(type = "EEG")

    # Get the number of channels from the inlet to use later
    channelsn = inlet.info().channel_count()

    # Create the figure we're going. We're going to use a different subplot
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
        
