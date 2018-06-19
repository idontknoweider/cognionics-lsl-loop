# General imports
import numpy as np
import scipy as sp
import glob
from win32api import GetSystemMetrics

# Plotting imports
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

# Networking imports
from pylsl import StreamInlet, resolve_stream, local_clock

# Visual imports
from psychopy import visual, core, clock


class stimuli(object):
    """
    Class used as a container for the stimuli of the experiment. The advantage
    of using this object mainly comes in the form of using a single draw() method
    to update all of them and being able to see which stimuli the experiment has.
    """

    # When the object initializes, it creates an empty list to contain stimuli
    def __init__(self):
        self.stimuli = []
        self.labels = []

    # Method to add stimuli
    def add(self, stimulus, label):
        if type(stimulus) == type([]):
            self.stimuli.extend(stimulus)
            self.labels.extend(label)
        else:
            self.stimuli.append(stimulus)
            self.labels.append(label)

    # Method to update all stimuli "simultaneously"
    def draw(self):
        for i in range(len(self.stimuli)):
            self.stimuli[i].draw()

    def draw_int(self, imin, imax):
        for i in range(len(self.stimuli[imin:imax])):
            self.stimuli[imin+i].draw()

    # See which stimuli are contained
    def see(self):
        print("Labels (in order): {0}".format(self.labels))

    # Swap the place of two stimuli, since the drawing is done from first to last

    def swap(self, pos1, pos2):
        self.stimuli[pos1], self.stimuli[pos2] = self.stimuli[pos2], self.stimuli[pos1]
        self.labels[pos1], self.labels[pos2] = self.labels[pos2], self.labels[pos1]


class lsl_stream(object):
    """
    This class creates the basic connection between the computer and a Lab Streaming
    Layer data stream. With it connecting is made simpler and pulling and processing
    information directly is made trivial.

    METHODS:
        __init__: Initiates a connection when the class is called
        connect: Connects to a data stream in the network given defined by the keyword args
        pull: Pulls a chunk of data from the connected data stream

    ATTRIBUTES:
        streams: List of found LSL streams in the network
        inlet: Stream inlet used to pull data from the stream
        metainfo: Metadata from the stream
    """

    def __init__(self, **stream_info):
        self.connect(**stream_info)

    def connect(self, **stream_info):
        """
        This method connects to a LSL data stream. It accepts keyword arguments that define
        the data stream we are searching. Normally this would be (use keywords given between 
        quotes as key for the argument) "name" (e.g. "Cognionics Quick-20"), "type" (e.g. "EEG"),
        "channels" (e.g. 8), "freq" (from frequency, e.g. 500), "dtype" (type of data, e.g. 
        "float32"), "serialn" (e.g. "quick_20").

        After receiving the information of the stream, the script searches for it in the network
        and resolves it, and then connects to it (or the first one in case there are many, that's
        the reason why one has to be as specific as possible if many instances of LSL are being used
        in the lab). It prints some of the metadata of the data stream to the screen so the user
        can check if it is right, and returns the inlet to be used in other routines.

        INPUT:
            **kwargs: Keyword arguments defining the data stream

        RELATED ATTRIBUTES:
            streams, inlet, metainfo
        """
        # Put the known information of the stream in a tuple. It is better to know as much
        # as possible if more than one kit is running LSL at the same time.
        stream_info_list = []
        for key, val in stream_info.items():
            stream_info_list.append(key)
            stream_info_list.append(val)

        # Resolve the stream from the lab network
        self.streams = resolve_stream(*stream_info_list)

        # Create a new inlet to read from the stream
        self.inlet = StreamInlet(self.streams[0])

        # Get stream information (including custom meta-data) and break it down
        self.metainfo = self.inlet.info()

    def pull(self, **kwargs):
        """
        This method pulls data from the connected stream (using more information 
        for the pull as given by kwargs).

        INPUT:
            kwargs: Extra specifications for the data pull from the stream

        OUTPUT:
            the data from the stream
        """
        # Retrieve data from the data stream
        return self.inlet.pull_sample(**kwargs)

    def chunk(self, **kwargs):
        """
        This method pulls chunks. Uses sames formating as .pull
        """
        return self.inlet.pull_chunk(**kwargs)


class pseudo_buffer(object):
    def __init__(self):
        self.buffer = []

    def extend(self, new):
        self.buffer.extend(new)

    def append(self, new):
        self.buffer.append(new)

    def take_old(self, ammount):
        return_ = self.buffer[:ammount]
        self.buffer = self.buffer[ammount:]
        return return_

    def take_new(self, ammount):
        return_ = self.buffer[ammount:]
        self.buffer = self.buffer[:ammount]
        return return_

    def flag(self, size):
        return len(self.buffer) == size

    def clear(self):
        self.buffer = []


class emoji_stimulus(object):
    """ This object is created to handle every aspect of the visual representation
    of the emoji speller stimulus. It is created to simplify its use in other scripts
    making the readability skyrocket (due to reasons like: not having 200 lines on a
    main script) 

    Methods:
        __init__(self, **kwargs): Initialises the window and the emoji images and places
            everything where it is supposed to go. Also initialises the augmentation (blue
            rectangle). Accepts scalings (window_scaling, motion_scaling, stimulus_scaling)
            as keyword arguments to change the relative size of those parameters with respect
            to the screen size.
        quit(self): Closes the PsychoPy's window and quits the PsychoPy's core


    Attributes:
        self.window: The window object of PsychoPy
        self.stimuli: The stimuli object (class defined in this file) 
            containing all the stimuli from PsychoPy.
        self.num_emojis: Number of emoji images found
        self.imXaxis: Yeah, that. 



    """

    def __init__(self, **kwargs):
        # Get monitor dimensions directly from system and define window
        monitor_dims = np.array([GetSystemMetrics(0),
                                 GetSystemMetrics(1)])  # Monitor dimensions (px)
        refresh_rate = 60                               # Monitor refresh rate in Hz
        print(monitor_dims)
        # Number of frames per ms
        min_refresh = ((1000/refresh_rate)/100)
        print("Min refresh rate: {0} ms".format(min_refresh))

        if "window_scaling" in kwargs:
            window_scaling = kwargs["window_scaling"]
        else:
            window_scaling = 0.8

        # Stimuli window dimensions (px)
        window_dims = window_scaling * monitor_dims

        # Distance of Stimulus square movement, rounded for draw() method
        if "motion_scaling" in kwargs:
            motion_scaling = kwargs["motion_scaling"]
        else:
            motion_scaling = 0.19

        motion_dim = np.round(window_dims[0] * motion_scaling)
        print("Motion dim: {0}".format(motion_dim))

        if "stimulus_scaling" in kwargs:
            stimulus_scaling = kwargs["stimulus_scaling"]
        else:
            stimulus_scaling = 0.19

        # Dimensions of the stimuli
        stimulus_dim = np.round(window_dims[0] * stimulus_scaling)
        print("Stimulus dim: {0}". format(stimulus_dim))

        # Create window
        self.window = visual.Window(
            window_dims, monitor="testMonitor", units="deg")

        ## Stimuli parameters ##
        # Stimuli holder
        self.stimuli = stimuli()

        # Emoticon images
        # Get a list with the path to the emoticon image files
        emoji_path_list = glob.glob("1D Scale-Swaney-Stueve\\*.png")
        num_emojis = len(emoji_path_list)
        self.num_emojis = num_emojis
        emoji_size = stimulus_dim/2

        # Iterate over them to create the stimuli and the labels corresponding to the filename
        for i in range(len(emoji_path_list)):
            # Unpack the path string to get just filename without file format
            label = emoji_path_list[i].split("\\")[1].split(".")[0]

            # Create the stimuli
            self.stimuli.add(visual.ImageStim(
                win=self.window, image=emoji_path_list[i], units="pix", size=emoji_size), label)

        # Order the negative emojis correctly
        self.stimuli.swap(0, 2)

        # Blue Augmentation Square Stim Parameters
        self.stimuli.add(visual.Rect(win=self.window, units="pix", width=emoji_size,
                                     height=emoji_size, fillColor=[-1, -1, 1], lineColor=[0, 0, 0]), "rectBlue")

        ## Positioning ##
        # Position across x-axis
        emoji_pos = window_dims[0] * 0.8
        imXaxis = np.linspace(0 - emoji_pos/2, 0 + emoji_pos/2, num_emojis)
        self.imXaxis = imXaxis

        for i in range(num_emojis):
            self.stimuli.stimuli[i].pos = (imXaxis[i], 0)

    def quit(self):
        self.window.close()
        core.quit()
