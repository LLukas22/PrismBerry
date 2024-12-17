#!/bin/bash

# Define the name of the virtual environment and the Python script to run
VENV_DIR=".venv"
PYTHON_SCRIPT="./src/main.py"
REQUIREMENTS_FILE="requirements.txt"

if [ ! -d "$VENV_DIR" ]; then
    # Create the virtual environment
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing required packages..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "Requirements file not found!"
fi

# Run the Python script
echo "Running Python script..."
python $PYTHON_SCRIPT

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate