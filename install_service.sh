#!/bin/bash

# Define variables
SERVICE_NAME="prismberry.service"
SCRIPT_PATH="$(pwd)/run.sh"
WORKING_DIRECTORY="$(pwd)"
USERNAME="$(whoami)"

chmod +x $SCRIPT_PATH

# Create the systemd service file
echo "Creating systemd service file..."
cat <<EOF > $SERVICE_NAME
[Unit]
Description=Run PrismBerry script on startup
After=network.target

[Service]
ExecStart=$SCRIPT_PATH
WorkingDirectory=$WORKING_DIRECTORY
StandardOutput=journal
StandardError=journal
Restart=always
User=$USERNAME

[Install]
WantedBy=multi-user.target
EOF

# Move the service file to the systemd directory
echo "Installing systemd service..."
sudo mv $SERVICE_NAME /etc/systemd/system/

# Reload systemd manager configuration
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service to run on startup
echo "Enabling service..."
sudo systemctl enable $SERVICE_NAME

# Start the service immediately
echo "Starting service..."
sudo systemctl start $SERVICE_NAME

# Check the status of the service
echo "Checking service status..."
sudo systemctl status $SERVICE_NAME