# boot.py — single file for every AeroMorse board (sender + receivers).
#
# Behavior is auto-detected from the filesystem, so you can drop this same
# file on any board (Reverse TFT Feather sender, Reverse TFT Feather
# receiver, MagTag receiver) without editing.
#
# ┌─────────────────────────────────────────────────────────────────────┐
# │ Role        │ Detection                  │ What boot.py does          │
# ├─────────────┼────────────────────────────┼────────────────────────────┤
# │ SENDER      │ /morse_map.py exists       │ Enables USB HID (keyboard, │
# │             │                            │ mouse, consumer-control).  │
# ├─────────────┼────────────────────────────┼────────────────────────────┤
# │ RECEIVER    │ /morse_map.py absent       │ Nothing — board appears as │
# │ (default)   │ AND /hide absent           │ a normal CIRCUITPY drive.  │
# ├─────────────┼────────────────────────────┼────────────────────────────┤
# │ RECEIVER    │ /morse_map.py absent       │ Hides CIRCUITPY drive and  │
# │ (hidden)    │ AND /hide present          │ serial port from host PC.  │
# └─────────────────────────────────────────────────────────────────────┘
#
# ── Switching a receiver to "hidden" mode ────────────────────────────────
# Create an empty file called /hide on the receiver and reboot. The PC
# will then see the board only as a powered USB device — no CIRCUITPY
# drive, no COM port.
#
# ── Un-hiding a receiver ─────────────────────────────────────────────────
# A hidden board cannot be edited normally (no drive, no REPL). Boot it
# into CircuitPython safe mode (board-specific — usually press reset once,
# then again during the brief yellow-LED window), delete /hide, then
# power-cycle.

import os


def _exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


# ── Role detection ───────────────────────────────────────────────────────
# morse_map.py is the sender's keyboard/mouse/macro lookup table.
# Receivers never carry it, so its presence is a reliable role signal.
IS_SENDER = _exists("/morse_map.py")


if IS_SENDER:
    # ── Sender: enable USB HID before host enumeration ──────────────────
    import usb_hid
    usb_hid.enable((usb_hid.Device.KEYBOARD,
                    usb_hid.Device.MOUSE,
                    usb_hid.Device.CONSUMER_CONTROL))
    print("boot.py: sender — USB HID enabled.")
else:
    # ── Receiver: hide drive/serial only if /hide flag is present ───────
    if _exists("/hide"):
        import storage
        import usb_cdc
        storage.disable_usb_drive()
        usb_cdc.disable()
        # No print — serial is gone anyway.
    else:
        print("boot.py: receiver — CIRCUITPY visible (no /hide flag).")
