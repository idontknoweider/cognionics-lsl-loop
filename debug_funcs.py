### Debug functions ###

## IMPORTS ##
# General imports
import numpy as np
import scipy as sp
import scipy.fftpack as fft
import random as rand
import time

# Networking imports
from pylsl import StreamInfo, StreamOutlet, local_clock

## FUNCTIONS ##
# Function that allows the software to simulate a Lab Streaming Layer streaming output
def virtual_cognionics(channels = 8, frequency = 500, chunk_size = 1, buffer_size = 360, \
    stype = "random"):

    """ 
    Here we create a data stream output so that we can test the rest of the networking
    properties without having a proper output, like the one from Cognionics DAQ software.
    This function will output random data to a number of channels given as an argument
    (8 by default) at a given frequency in Hertz (500 by default).

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
        stype: "random", "sinusoid" or "noisy_sin" to choose which type of data will be 
            sent (random is the default)

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
    t0, step = local_clock(), 0 # Used for the stamps and the sample signals
    interval = 1 / frequency
    while True:
        # Get the timestamp with t0 as a reference for initial time
        stamp = local_clock() - t0

        # Here we create the sample with random data
        if stype == "random":
            sample = list(np.random.rand(channels + 5))

        elif stype == "sinusoid": # Frequency of 10 Hz
            sample = [np.sin(10 * 2 * np.pi * step)] * (channels + 5)

        elif stype == "noisy_sin": # Frequencies of 5 and 15 Hz
            sample = [np.sin(5 * 2 * np.pi * step) + 0.2 * \
                np.sin(15 * 2 * np.pi * step) + 0.2 * np.random.rand()] * \
                (channels + 5)
        else:
            raise TypeError("Wrong signal type. Please check documentation")
            
        # Update the step
        step += interval

        # Now we send it and wait to send the next one
        outlet.push_sample(sample, stamp)
        time.sleep(interval)
    
# Function that does a FFT
def process_rfft(time, signal):
    """ This function calculates the real fast Fourier transform of a given signal
    and exports the frequency and the signal as obtained in magnitude and in dB, all
    in the same list.

    INPUT:
        time: an iterable with the timestamps of the different values of the signal
        signal: an iterable with the values of the signal

    OUTPUT:
        LIST containing freq, fsignal and dBsignal
            freq: array containing the frequency range over which the transformation
                has been calculated
            fsignal: magnitude of the signal at the different frequencies
            dBsignal: magnitude of the signal at the different frequencies, in dB
    """

    freq = fft.fftfreq(len(time), time[1] - time[0])
    fsignal = fft.rfft(signal)

    # Transform into dB
    dBsignal = 20 * sp.log10(fsignal)

    return [freq, fsignal, dBsignal]