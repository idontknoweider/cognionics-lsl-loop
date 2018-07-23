# EEG experiment set up with Cognionics data capture using Lab Streaming Layer and stimuli presentation with PsychoPy

## Table of contents

- Introduction
- Installing
- Files explanation
  - Existing experiment
- Getting help
- Contributing
- License

## Introduction

This library contains classes that help create a BCI Speller using an EEG kit that works with LabStreamingLayer.

The main intended use was a BCI Speller using emojis as characters, but this libraries (in particular, its classes) can be easily used for other experimeriments involving measurements with EEG kits.

## Installing

Due to having main scripts apart from libraries that can be used for other purposes, the only way of installing for now is by clonning the repository:

```bash
git clone https://github.com/Hroddric/cognionics-lsl-loop.git
```

The requirements are (latest release if no version is explicitly written down):

- Python 3.x
- Numpy
- Scipy
- Pylsl (LabStreamingLayer's Python Interface)
- PsychoPy
- Pytorch
- Scikit-Learn
  - Qt and PyQtPlot only if `plot_main.py` is going to be used.

## Files explanation

The main features of the library can be found in the `classes.py` file. This file contains several classes that help with the handling of the LSL Data Streams, the buffering of data, the creation and listing of stimuli and the handling of some specific datasets (that are given with the library).

Apart from that, the `functions.py` file contains some functions that are used within the classes and some other funtions that can be useful when working with spellers (`rowcol_paradigm` for example creates the array of character of a 36 character speller).

The file `debug_funcs.py` contains functions that help with the debugging and testing of scripts. The main function here is `virtual_cognionics`, which creates a virtual data stream of several channels with the same format that a Cognionics Quick-20 EEG headset would, sending different kinds of signals (which are not EEG related).

The file `main.py` contains the emoji speller experiment, using the classes used. `plot_main.py` is a real time plotter of the signal received from the data stream using Qt. This plotting file is not optimized and has some errors. It is currently discontinued.

The last file, `erp.py`, is a file to train an LDA model with the BNCI dataset (also in the repository). It processes this dataset according to the way it is formated and then uses it to train and test a model using scikit-learn.

### Existing experiment
The Cognionics, Inc. EEG headset connects to a computer via Bluetooth using the USB Stick provided with the headset and the Cognionics Data Acquistion Software (DAQ) as software that reads the bluetooth signal. This software can export the data to the laboratory network using Lab Streaming Layer (LSL). These data streams on the network can be found with the different Lab Streaming Layer interfaces. In this case, we use the Python interface. With it we get the data from the stream and process it, both in real time and saving in files (.npz).

While the acquisition of data happens, the stimuli are shown on the screen: images that are augmented at different times. These stimuli provoke the appearance of event related potentials (ERP), which when read with the EEG are shown as P300 waves. Using different techniques (like Linear Discrimination Analysis (LDA) or Neural Networks (NNs)) one can process these signals and detect when the P300 happened and relate that to one of the augmentations of the images. All this can be done in real time, as mentioned before, thanks to the "real time" streaming of the data obtained by the headset throught LSL. After processing the signals and finding which image was the user looking at, the result is displayed and a choice can be made by the user, showing if that result coincides with the actual Ground Truth.

## Getting help

For any issues, requests or questions, please contact me via email to: rodrigo.perezordoyobellido@gmail.com

## Contributing

If you want to contribute, fixing issues or expanding upon the work done here, fork the repository and make pull requests when you want. Any help is greatly appreciated.

## License

I have still to check this one but for now I want this to be private so please don't do anything with it until we have stuff done. Later I would like it to be accesible by everyone so they can have the code for the experiment and replicate it in their own laboratory.