#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Please use 'sudo' to run the script."
    exit 1
fi

# Check if xinput is installed
if ! command -v xinput &>/dev/null; then
    echo "xinput command not found. Installing xinput package..."
    apt update
    apt install -y xinput
fi

# Check again if xinput is installed
if ! command -v xinput &>/dev/null; then
    echo "Failed to install xinput package. Please install it manually and try again."
    exit 1
fi

# Function to get USB ID of the clicked mouse
get_usb_id() {
    echo "Waiting for a left mouse click..."
    local event_id
    while true; do
        event_id=$(xinput test-xi2 --root | grep "EVENT type 13 (RawButtonPress)" -m 1 | awk '{print $8}')
        if [[ "$event_id" ]]; then
            local usb_id=$(xinput list --long "$event_id" | grep -oP 'id=\K\d+')
            echo "$usb_id"
            break
        fi
    done
}

# Function to prompt for mouse clicks and save USB IDs to team_config.txt
prompt_mouse_click() {
    local team_name=$1
    echo "Please click the left mouse button for the $team_name team..."
    local usb_id=$(get_usb_id)
    echo "Team $team_name: $usb_id" >> team_config.txt
    echo "USB ID $usb_id for $team_name team saved to team_config.txt"
    echo
}

# Check if team_config.txt already exists
if [ -e "team_config.txt" ]; then
    echo "team_config.txt already exists. Please delete it and run the script again."
    exit 1
fi

# Main script
echo "This script will prompt you to click the left mouse button for each team."
echo "Please make sure all the mice are connected and ready."
echo

# Create an empty team_config.txt file
touch team_config.txt

# Prompt for mouse clicks for each team
prompt_mouse_click "Red"
prompt_mouse_click "White"
prompt_mouse_click "Yellow"
prompt_mouse_click "Green"
prompt_mouse_click "Blue"

echo "Setup complete. team_config.txt file has been generated with the USB IDs for each team."
