#!/bin/bash

# Define the name of the virtual environment and the Python script to run
VENV_DIR=".venv"
PYTHON_SCRIPT="./src/main.py"

# Create the virtual environment
python3 -m venv $VENV_DIR

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Run the Python script
python $PYTHON_SCRIPT

# Deactivate the virtual environment
deactivate