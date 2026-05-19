# boot.py for the AeroMorse receiver (display-only) board.
#
# Copy this file to the second Feather as boot.py.
#
# NORMAL USE — power from a USB power bank or phone charger, not the laptop.
# The receiver gets all its data wirelessly via ESP-NOW and needs no USB
# connection to the host computer during normal operation.
#
# HIDDEN MODE (default below)
# When HIDE_FROM_PC = True the board suppresses its CIRCUITPY drive and serial
# port so Windows/Mac sees nothing when it is plugged into a computer — just
# a USB device drawing power.  No second drive, no extra COM port, no conflict
# with the main AeroMorse board.
#
# MAINTENANCE MODE
# To update receiver code or read the serial console, set HIDE_FROM_PC = False,
# save boot.py, then power-cycle the board.  The CIRCUITPY drive and serial
# port reappear.  Set it back to True when done.

HIDE_FROM_PC = False

if HIDE_FROM_PC:
    import storage
    import usb_cdc
    storage.disable_usb_drive()   # hide CIRCUITPY drive
    usb_cdc.disable()             # hide serial / COM port
    # USB HID is not enabled here — this board is display-only.
