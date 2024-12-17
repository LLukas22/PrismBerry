#!/bin/bash

# Define the name of the virtual environment and the Python script to run
VENV_DIR=".venv"
PYTHON_SCRIPT="./src/main.py"
REQUIREMENTS_FILE="requirements.txt"

# Function to handle script interruption
handle_interrupt() {
    echo "Script interrupted. Cleaning up..."
    deactivate 2>/dev/null
    exit 1
}

# Trap SIGINT (Ctrl + C) signal
trap handle_interrupt SIGINT

# Check for Git updates
echo "Checking for Git updates..."
git fetch
if [ $(git rev-parse HEAD) != $(git rev-parse @{u}) ]; then
    echo "There are updates available. Pulling the latest changes..."
    git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
    echo "Setting executable permission for the script..."
    chmod +x "$0"
    echo "Rerunning the script..."
    exec "$0" "$@"
else
    echo "Your branch is up to date."
fi

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