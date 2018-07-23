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

The experiment all these files are intended for is a Brain Computer Interface based speller using emojis instead of character for faster communcation of emotions.

I this experiment the Cognionics Inc,. EEG headset is connected to a computer via Bluetooth using the USB stick provided with the headset and the Cognionics Data Acquisition Software (DAQ) as software that reads the signal. It is important to know that the DAQ software only is available for the OS Windows. This software can create a data stream over the Lab Network using Lab Streaming Layer (LSL). This data stream also has a buffer, that will hold samples that are not being pulled by a client. These data streams in the network can be found with different LSL interfaces. In this case, the Python interface is being use. With it, we get the data from the stream. The data obtained from the stream will later be processed to have online interaction in the experiment and also saved, to be able to work with it online.

While the acquisition of data happens, stimuli are shown on the screen. In this case, using the PsychoPy library a visual interface consisting of an array of one row and seven columns of emojis was created. The stimulus consists in the augmentation of one of those emojis via the flashing of a blue box on top of one of them for a short amount of time *augmentation time). After that, a time passes without any other boxes, called the Inter-Stimuli Interval (ISI). This augmentation happens in a random order for all the emojis several full sequences.

The augmentation of the emojis elicits a Event Related Potential (ERP) using the oddball paradigm. This ERP is usually found in the form of a P300 wave that appears around 300ms after the presence of the augmentation. Measuring this P300 and creating a system to be able to detect whether or not these P300 are found or not in a chunk of data, can point at which emoji the user was looking at and thus, know what the user wanted to spell. This choice is presented at the user who, in the experiments, will be able to serve as a ground truth to say whether or not the emoji corresponds to the actual target.

The way this detection works is by feature detection or machine learning. In our case, we use Linear Discriminant Analysis, which separates the data that does a does not have P300 waves in them. Further work with other kinds of processing systems will be done. For example, Neural Networks seem like a good candidate for offline and online usage with theses systems for their flexibility and speed.

## Getting help

For any issues, requests or questions, please contact me via email to: rodrigo.perezordoyobellido@gmail.com

## Contributing

If you want to contribute, fixing issues or expanding upon the work done here, fork the repository and make pull requests when you want. Any help is greatly appreciated.

## License

I have still to check this one but for now I want this to be private so please don't do anything with it until we have stuff done. Later I would like it to be accesible by everyone so they can have the code for the experiment and replicate it in their own laboratory.