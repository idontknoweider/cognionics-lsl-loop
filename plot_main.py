# EEG

# General imports
import numpy as np
import scipy as sp

# Plotting imports
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

# Networking imports
from pylsl import StreamInlet, resolve_stream, local_clock

# Custom imports
import debug_funcs as dfun
from objects import lsl_stream, stimuli, lsl_buffer


def pull_process(stream, func, chunk_size, **kwargs):
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
    chunk, timestamps = stream.chunk(**kwargs)

    # Only does something if data arrives
    if timestamps:
         # Initialize simple buffers if they haven't been already
        global data_buffer
        global stamp_buffer
        if not "data_buffer" in globals():
            data_buffer = lsl_buffer()
            stamp_buffer = lsl_buffer()

        # Add data chunk to buffer and compare the size to the required size
        data_buffer.add(chunk)
        stamp_buffer.add(timestamps)

        # Create a flag to see whether or not to output processed data
        output_proc = False

        # Compare size of buffer to that required size for processing.
        # If large enough or larger, process and continue storing extra data.
        if len(data_buffer) >= chunk_size:
            data = np.array(data_buffer)[:chunk_size]
            time = np.array(stamp_buffer)[:chunk_size]

            # Process data channel by channel
            processed_data = []
            for i in range(stream.inlet.channel_count):
                processed_temp = func(time, data_buffer.items[:, i])
                processed_data.append(processed_temp)

            # Get rid of already used data
            # stamp_buffer = stamp_buffer[chunk_size:]
            # data_buffer = data_buffer[chunk_size:]

            # Order the function to output the processed data
            output_proc = True

        # Return raw and processed data with timestamps
        if output_proc:
            return timestamps, data, processed_data, output_proc
        else:
            return timestamps, data, [], output_proc

# Main
# To execute if script is executed as main (direct execution, not as an import)
if __name__ == "__main__":

    # Connect via LSL to data stream
    data_stream = lsl_stream(type="EEG")

    # Get the number of channels from the inlet to use later
    channelsn = data_stream.inlet.channel_count
    print("Number of channels on the stream: {0}".format(channelsn))

    # Create the PyQtGraph window
    plot_duration = 1
    win = pg.GraphicsWindow()
    win.setWindowTitle("LSL Plot " + data_stream.inlet.info().name())
    plt = win.addPlot()
    plt.setLimits(xMin = 0.0, xMax = plot_duration, yMin = -1.0 * \
        (data_stream.inlet.channel_count - 1), yMax = 1.0)
    
    t0 = [local_clock()] * data_stream.inlet.channel_count
    curves = []
    for ch_ix in range(data_stream.inlet.channel_count):
        curves += [plt.plot()]
    inlet = data_stream.inlet

    def update():
        # Be able to modify this global variables
        global curves, t0
        chunk, timestamps = data_stream.chunk(timeout = 0.0)
        print("LONG:" + str(len(timestamps)))
        if timestamps:
            # print(chunk)
            timestamps = np.asarray(timestamps)
            y = np.asarray(chunk)

            for ch_ix in range(data_stream.inlet.channel_count):
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
    timer.start(5) # Let some time for the source to create data
    QtGui.QApplication.instance().exec_()
