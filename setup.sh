#!/bin/bash

# Check if the script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root. Please use 'sudo' to run the script."
    exit 1
fi

# Function to find the USB ID of the connected mouse using syslog
find_mouse_id(){
echo "Insert the button with the color $1 into the USB port. You have 10 seconds."
sleep 5
echo "5 seconds remaining..."
sleep 5
echo "0 seconds remaining... Mouse is now being detected."
mousepath=$(tail /var/log/syslog -n 11 | grep hid-generic | awk -F ' ' '{print $NF}' | awk -F '/input0' '{print $1}')
mouseid=$(python3 list_mice.py | grep $mousepath | awk '{ print $4 }')

echo "USB ID has been written to team_config.txt"
echo "$mouseid:Team$1"
echo "$mouseid:Team$1" >> team_config.txt

# Press Enter to continue
read -p "Press Enter to continue..."
}

# Check if team_config.txt already exists
if [ -e "team_config.txt" ]; then
    echo "team_config.txt already exists. Please delete it and run the script again."
    exit 1
fi

# Create an empty team_config.txt file
touch team_config.txt

echo "Make sure all buttons are not connected!!"
read -p "Press Enter to continue..."
echo "Start with mouse configuration"
find_mouse_id "Red"
find_mouse_id "Yellow"
find_mouse_id "Blue"
find_mouse_id "White"
find_mouse_id "Green"
