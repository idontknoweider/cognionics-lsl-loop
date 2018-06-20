# ERP Stimulus Code with stimulus square motion
# Based on code from Joshua J. Podmore

# Imports
from psychopy import visual, core, clock
import numpy as np
from objects import stimuli, emoji_stimulus
import glob  # File handling

# Create the object
estimulus = emoji_stimulus()

# Set up the experiment with the default values
estimulus.experiment_setup()

# Play the experiment
estimulus.play()

# Quit the PsychoPy instances
estimulus.quit()