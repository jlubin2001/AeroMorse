# Bluetooth (BLE) keyboard status

AeroMorse sends **USB HID only**. This page records why Bluetooth is not
offered, and what was tested, so the question can be re-opened when
CircuitPython's Bluetooth support on the ESP32-S3 improves. It used to be the
"BLE HID note" in §3 of the Build Guide.

**Short version:** on CircuitPython 10.3.1 a Bluetooth keyboard on the
ESP32-S3 does not stay connected to an Android phone. For a phone or tablet,
use a **USB-C cable** — AeroMorse works as a wired keyboard and mouse.

## What was tested

**The chip supports it, but CircuitPython's BLE keyboard support on the
ESP32-S3 is still not reliable — tested, see below.** The ESP32-S3 hardware
fully supports Bluetooth LE; the problems are in CircuitPython's ESP32 BLE
code. Several were fixed (issues #9430, #9669, and #10739, the last marked
fixed in 10.3.0), but on CircuitPython 10.3.1 a BLE keyboard still does not
stay connected to an Android phone.

> **Tested 2026-09-26** — #5691 with TinyUF2 0.35.0 + CircuitPython 10.3.1,
> host a Samsung Galaxy A15 (Android 16), using `test_ble.py` from this repo:
> - The board advertises and the phone pairs (`paired=True`).
> - **No keystrokes ever reached the phone** — not on any connection, even
>   while the board reported it was paired — although CircuitPython raised no
>   error when sending them.
> - The link then **drops about 6.5 s after every connection**, and every
>   reconnect starts **unpaired** again — the board doesn't keep the pairing —
>   so it loops connect → pair → drop.
>
> **Result: not usable yet.** Reported upstream on
> [adafruit/circuitpython #10739](https://github.com/adafruit/circuitpython/issues/10739).
> An iPad or Windows host has not been tested.
> Run `test_ble.py` to check a newer CircuitPython or a different host. For a
> phone or tablet today, use a **USB-C cable** — AeroMorse works as a wired
> keyboard/mouse.

**4 MB flash boards include BLE on 10.x.** Earlier builds sometimes left the
BLE stack out of 4 MB firmware images to save space. As of **CircuitPython
10.3.1**, circuitpython.org lists the `_bleio` (BLE) module — together with
`espnow` and `usb_hid` — for the three 4 MB Feathers in the Build Guide (#5691, #5483,
#5477). Always confirm on your board's circuitpython.org page under
"Built-in modules available".

**Before you can use BLE:**
- **You need CircuitPython 10.x** — BLE HID is not reliable on 9.x.
- **An older bootloader may refuse to flash 10.x.** A #5691 with the 2023
  TinyUF2 bootloader (0.12.3) accepted 9.2.9 but silently ignored a 10.x
  `.uf2` — the drive stayed `FTHRS3BOOT` and never rebooted. Update the
  TinyUF2 bootloader first, then flash 10.x.
- **Use the matching 10.x library bundle** in `lib/`.

**AeroMorse status:** `code.py` sends **USB HID only**. BLE HID (pairing with
a phone or iPad) is not implemented, and won't be until the CircuitPython
problem above is resolved. Running the ESP-NOW wireless display and BLE at the
same time shares one 2.4 GHz radio and has not been tested either. iPads and
phones with USB-C already accept AeroMorse as a **wired** USB keyboard/mouse.

## Trying it again

`test_ble.py` in this repo is the test used above. Copy it to `CIRCUITPY`
together with `adafruit_ble/` in `lib/`, stop `code.py`, and run
`import test_ble` — see the README's file table. Use it to check a newer
CircuitPython or a different host.
