# test_ble.py — AeroMorse Bluetooth LE keyboard test  (CircuitPython 10.x)
#
# Checks whether this board can pair with a phone, iPad, or PC over Bluetooth
# LE and type as a WIRELESS keyboard. It does not use the sip-and-puff sensor
# and does not change code.py — AeroMorse itself stays USB-only.
#
# Needs in lib/:  adafruit_ble/  and  adafruit_hid/   (from the 10.x bundle)
#
# Run it from the REPL, the same way as test_pressure.py:
#   1. Press Ctrl-C to stop code.py, then press Enter to get the >>> prompt.
#   2. Type:   import test_ble
#   3. On the phone/iPad: open a notes app, then Settings > Bluetooth and tap
#      "AeroMorse Blue". Once connected it types a few test lines by itself.
#   4. Press Ctrl-C to stop. Press RESET (or Ctrl-D) to go back to AeroMorse.
#
# Status messages print to the serial console and on the board's own screen.

import time
import _bleio
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

NAME  = "AeroMorse Blue"   # what shows up in the phone's Bluetooth list
LINES = 5                  # test lines typed after each (re)connection
GAP_S = 3.0                # seconds between test lines
CLEAR_BONDS = True         # forget old pairings on this board at start, so a
                           # half-finished earlier attempt can't get in the way

if CLEAR_BONDS:
    try:
        _bleio.adapter.erase_bonding()
        print("Cleared old Bluetooth pairings on this board.")
    except Exception as e:
        print("(could not clear old pairings: %r)" % (e,))

hid = HIDService()
device_info = DeviceInfoService(software_revision=adafruit_ble.__version__,
                                manufacturer="AeroMorse")
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961          # 961 = "keyboard" icon on the host
scan_response = Advertisement()
scan_response.complete_name = NAME

ble = adafruit_ble.BLERadio()
ble.name = NAME
kbd = Keyboard(hid.devices)
layout = KeyboardLayoutUS(kbd)

print("BLE keyboard test -", NAME)
connections = 0
t_conn = time.monotonic()
while True:
    if not ble.connected:
        print("Advertising. On the phone/iPad: Settings > Bluetooth > tap", NAME)
        ble.start_advertising(advertisement, scan_response)
        while not ble.connected:
            time.sleep(0.2)
        connections += 1
        t_conn = time.monotonic()
        conn = ble.connections[0] if ble.connections else None
        print("CONNECTED (connection #%d)  paired=%s"
              % (connections, getattr(conn, "paired", "?")))
        # A phone only accepts keystrokes from a PAIRED (bonded) keyboard.
        # If the phone didn't start pairing itself, ask it to.
        if conn is not None and not conn.paired:
            print("Asking the phone to pair - tap PAIR on the phone if it asks...")
            try:
                conn.pair()
                print("pair() finished  paired=%s" % conn.paired)
            except Exception as e:
                print("PAIR FAILED: %r" % (e,))
        for _ in range(6):              # let the host finish setting up the keyboard
            time.sleep(0.5)
            if not ble.connected:
                break
        print("before typing: connected=%s  paired=%s"
              % (ble.connected, getattr(conn, "paired", "?")))
        for i in range(1, LINES + 1):
            if not ble.connected:
                break
            msg = "AeroMorse BLE test %d/%d (connection %d)" % (i, LINES, connections)
            try:
                layout.write(msg + "\n")
                print("typed:", msg)
            except Exception as e:        # report, don't crash, so we learn why
                print("TYPE FAILED:", repr(e))
            time.sleep(GAP_S)
        print("Test lines done. To test reconnecting: turn the phone's Bluetooth")
        print("off and on again - it should reconnect and type more lines.")
    while ble.connected:
        time.sleep(0.5)
    print("DISCONNECTED after %.1f s" % (time.monotonic() - t_conn))
