# boot.py — runs once before code.py; must enable USB HID before the
# USB stack is negotiated with the host.
import usb_hid

usb_hid.enable((usb_hid.Device.KEYBOARD, usb_hid.Device.MOUSE))
