# boot.py — single file for every AeroMorse board (sender + receivers).
#
# AeroMorse boot.py — version 1.19 (released 2026-10-03)
# Official source (always get the latest here): https://github.com/jlubin2001/AeroMorse
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
# ── Device name shown by the computer ────────────────────────────────────
# Sender: DEVICE_NAME from config.py (e.g. "AeroMorse Green"). If that is
# missing or still the default "AeroMorse", a label file on the drive is used
# instead: AeroMorse-Green.txt -> "AeroMorse Green".
# Receiver: its label file (AeroMorse-Display.txt -> "AeroMorse Display"),
# or "AeroMorse Display" if there is none. Applies after unplug/replug.
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


def _device_name():
    """DEVICE_NAME from config.py — the name the computer shows for this
    device (e.g. "AeroMorse Green" in Windows Bluetooth & devices). Read as
    plain text, NOT imported, so a mistake in config.py can never stop the
    board from starting; anything unexpected just keeps the default name."""
    try:
        with open("/config.py") as f:
            for line in f:
                s = line.strip()
                if not (s.startswith("DEVICE_NAME") and "=" in s):
                    continue
                v = s.split("=", 1)[1].strip()
                if v[:1] in ("'", '"'):
                    end = v.find(v[0], 1)
                    if end > 1:
                        name = "".join(c for c in v[1:end] if 32 <= ord(c) < 127).strip()
                        return name[:40] or None
                return None
    except Exception:
        pass
    return None


def _label_name():
    """Name from a label file on the drive, e.g. AeroMorse-Display.txt ->
    "AeroMorse Display". Used when config.py has no DEVICE_NAME (a display
    board has no config.py at all)."""
    try:
        for fn in os.listdir("/"):
            if fn.startswith("AeroMorse-") and fn.endswith(".txt"):
                tag = fn[10:-4].replace("-", " ").replace("_", " ").strip()
                if tag:
                    return ("AeroMorse " + tag)[:40]
    except Exception:
        pass
    return None


def _set_usb_name(name):
    """Tell the computer this device's name (shown in e.g. Windows Bluetooth
    & devices). Must run in boot.py, before the USB connection starts."""
    try:
        import supervisor
        supervisor.set_usb_identification(product=name)
        print("boot.py: USB device name = %s" % name)
    except Exception as e:
        print("boot.py: could not set USB device name (%s)" % e)


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
    # ── Name shown by the computer: config.py DEVICE_NAME, else label file
    # (a label file wins over the unchanged default "AeroMorse").
    _name = _device_name()
    if not _name or _name == "AeroMorse":
        _name = _label_name() or _name
    if _name:
        _set_usb_name(_name)
else:
    # ── Receiver: name it (label file, else "AeroMorse Display") ────────
    _set_usb_name(_label_name() or "AeroMorse Display")
    # ── Receiver: hide drive/serial only if /hide flag is present ───────
    if _exists("/hide"):
        import storage
        import usb_cdc
        storage.disable_usb_drive()
        usb_cdc.disable()
        # No print — serial is gone anyway.
    else:
        print("boot.py: receiver — CIRCUITPY visible (no /hide flag).")
