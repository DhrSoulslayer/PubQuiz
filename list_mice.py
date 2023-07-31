import evdev

def display_connected_mice():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    if not devices:
        print("No mice found.")
        return

    mice_info = []  # List to store mouse details

    print("Connected mice devices:")
    for device in devices:
        if "mouse" in device.name.lower():
            mouse_info = {
                "name": device.name,
                "device_path": device.path,
                "usb_pci_path": device.phys
            }
            mice_info.append(mouse_info)

    # Display the mouse details from the list of dictionaries
    for idx, mouse in enumerate(mice_info, start=1):
        print(f"Mouse{idx}: Device Path: {mouse['device_path']} USB PCI Path: {mouse['usb_pci_path']}")
if __name__ == "__main__":
    display_connected_mice()
