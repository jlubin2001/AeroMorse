# AeroMorse — Recommended Tools & Learning Guides

This document lists every tool and reference you may need to build and
configure AeroMorse. Nothing here is compulsory for every build — read the
notes to understand which items apply to your chosen configuration.

---

## Table of Contents

1. [Software Tools](#1-software-tools)
2. [Soldering Tools](#2-soldering-tools)
3. [General Hardware Tools](#3-general-hardware-tools)
4. [Wiring Supplies](#4-wiring-supplies)
5. [Learning Guides](#5-learning-guides)
6. [Morse Code References](#6-morse-code-references)

---

## 1. Software Tools

All software tools listed here are **free**.

---

### Thonny — Code Editor & Serial Console ⭐ Recommended

**Download:** https://thonny.org
**Platforms:** Windows, macOS, Linux
**Adafruit Thonny guide:** https://learn.adafruit.com/welcome-to-circuitpython/thonny-ide

Thonny is the recommended editor for CircuitPython beginners. In one window it
gives you:

- A code editor for `code.py` and `morse_map.py`
- A file manager for the CIRCUITPY drive (drag, rename, delete files)
- A serial console showing `print()` output and error messages in real time
- A REPL (interactive Python prompt) for testing one line at a time

---

#### Step 1 — Install Thonny

1. Go to https://thonny.org and click the download button for your operating
   system (Windows, macOS, or Linux).
2. Run the installer and follow the prompts. No special options are needed.
3. Launch Thonny after installation completes.

---

#### Step 2 — Connect the Feather

1. Plug your Feather into the computer with a **USB-C data cable** (not a
   charge-only cable — a drive must appear on your computer).
2. Wait a few seconds. The **CIRCUITPY** drive should appear on your desktop
   or in File Explorer / Finder.

> If CIRCUITPY does not appear, CircuitPython may not be installed yet —
> see the Software Installation section of the Build Guide.

---

#### Step 3 — Set the interpreter to CircuitPython

1. In Thonny, click the menu **Run → Configure interpreter…**
   (or click the interpreter name shown at the bottom-right of the Thonny window)
2. In the dropdown at the top, select **CircuitPython (generic)**
3. In the **Port** dropdown, select the port your Feather is on:
   - **Windows:** a COM port, e.g. `COM3` or `COM7` — try each if unsure
   - **macOS:** something like `/dev/cu.usbmodem14101`
   - **Linux:** something like `/dev/ttyACM0`
4. Click **OK**
5. The bottom panel (Shell) should now show `>>>` — this is the REPL prompt,
   confirming Thonny is connected.

> **Can't find the right port?**
> On Windows: open Device Manager → Ports (COM & LPT) — the Feather appears
> as "USB Serial Device" or "CircuitPython CDC Control".
> On Mac: open Terminal and type `ls /dev/cu.*` — look for `usbmodem`.

---

#### Step 4 — Open the AeroMorse files

**Method A — directly from the CIRCUITPY drive (simplest):**
1. In Thonny, click **File → Open…**
2. A dialog asks "Where to open from?" — click **CircuitPython device**
3. Select `code.py` or `morse_map.py` and click **Open**
4. Edit the file and press **Ctrl+S** (Windows/Linux) or **Cmd+S** (Mac) to save
5. The Feather detects the save and **restarts automatically** — no button press needed

**Method B — from the CIRCUITPY drive via File Explorer / Finder:**
1. Open File Explorer (Windows) or Finder (Mac)
2. Navigate to the CIRCUITPY drive
3. Double-click `code.py` — it opens in your default text editor
4. Save the file — the Feather restarts automatically

---

#### Step 5 — Watch the serial console

The **Shell panel** at the bottom of Thonny shows everything AeroMorse prints
while it runs. After saving `code.py` and the Feather restarts, you will see:

```
Calibrating — do not sip or puff ...
Baseline: 1013.241  sip<1008.241  puff>1018.241
```

This confirms the code is running. If you see an error instead, the Shell
shows the exact line number and error type — read it carefully before
troubleshooting.

**Useful serial output during use:**
```
. - .    "r"          ← pattern committed, letter r typed
-> Mouse             ← group changed to Mouse
? . -                ← pattern not found in current group
```

---

#### Step 6 — Use the REPL for quick tests

The REPL (`>>>` prompt) lets you type individual Python commands without
editing a file. Useful for checking sensor readings or pin states:

```python
>>> import board, busio, adafruit_lps35hw
>>> i2c = board.STEMMA_I2C()
>>> lps = adafruit_lps35hw.LPS35HW(i2c)
>>> print(lps.pressure)
1013.44
```

To interrupt a running program and get to the REPL, press **Ctrl+C** in the
Shell panel. To restart the program, press **Ctrl+D**.

---

#### Thonny quick-reference

| Action | Shortcut |
|--------|---------|
| Save file (and trigger Feather restart) | Ctrl+S / Cmd+S |
| Stop running program / go to REPL | Ctrl+C (in Shell) |
| Restart program from REPL | Ctrl+D (in Shell) |
| Open file from CIRCUITPY drive | File → Open → CircuitPython device |
| Open file from computer | File → Open → This computer |
| Increase font size | View → Increase font size |

---

### Visual Studio Code — Advanced Editor (optional)

**Download:** https://code.visualstudio.com
**Extension:** Search for **CircuitPython** in the Extensions panel

VS Code with the CircuitPython extension provides syntax highlighting,
auto-complete, and IntelliSense for CircuitPython. Better suited to users
already comfortable with code editors. Not necessary for AeroMorse.

---

### CircuitPython Downloads

The CircuitPython firmware (.uf2 file) for your Feather board:

**All boards:** https://circuitpython.org/downloads

Search for your board name (e.g. "ESP32-S3 Feather") and download the latest
**stable** release. Do not use pre-release (alpha/beta) builds.

---

### CircuitPython Library Bundle

The collection of CircuitPython libraries (.mpy files) including the display
drivers, HID library, and sensor library used by AeroMorse:

**Library bundle:** https://circuitpython.org/libraries

Download the bundle that matches your CircuitPython version number (shown in
`boot_out.txt` on the CIRCUITPY drive).

---

## 2. Soldering Tools

**Required only if:**
- You are building the soldered TRRS breakout option (Option B2), **or**
- Your Feather board arrived without header pins pre-soldered

The solderless breadboard option (Option B1) needs no soldering at all.

> **New to soldering?** Read Adafruit's free beginner guide before you start:
> https://learn.adafruit.com/adafruit-guide-excellent-soldering
> It covers tools, technique, and common mistakes — takes about 20 minutes
> to read and will save hours of frustration.

---

### Soldering Iron

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Adjustable 60W Pen-Style Soldering Iron (BEST 102C) | #3685 | $19.95 | https://www.adafruit.com/product/3685 |

A **temperature-adjustable** iron is strongly recommended for beginners. Fixed-
temperature irons run too hot for small electronic pads and can damage boards.
The BEST 102C (#3685) is adjustable, affordable, and widely used in the
maker community.

If you already own a soldering iron rated 25–60 W with adjustable temperature,
it will work fine.

---

### Solder

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Solder — 60/40 Rosin Core 0.3 mm, 100 g spool | #145 | $14.95 | https://www.adafruit.com/product/145 |

Use **60/40 rosin-core** solder (60% tin, 40% lead). The thin 0.3 mm gauge is
much easier to control on small pads than thicker solder. The rosin flux core
is built in — do not buy "acid-core" solder (that is for plumbing, not
electronics).

> Lead-free solder (#734) is available if you prefer it, but requires a higher
> iron temperature and is slightly harder to work with for beginners.

---

### Flush Diagonal Cutters

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Flush Diagonal Cutters CHP-170 | #152 | $7.25 | https://www.adafruit.com/product/152 |

Used to trim wire leads flush after soldering. The "flush" cut leaves a flat
end rather than a pointed one, which prevents shorts on nearby pads. Also
useful for cutting tubing and stripping short lengths of insulation.

---

### Helping Hands

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Helping Third Hand Magnifier Tool | #291 | $6.95 | https://www.adafruit.com/product/291 |

A weighted base with two adjustable alligator-clip arms that hold your work
steady while both hands are free to hold the iron and solder. Particularly
useful when soldering wires to the small TRRS breakout pads. The built-in
magnifying glass helps when reading small board labels.

---

### Wire Strippers

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Wire Strippers — 20–30 AWG | #527 | $17.50 | https://www.adafruit.com/product/527 |

Used to remove insulation from the end of hookup wire. The #527 handles 20–30
AWG wire — the range used in almost all electronics projects including AeroMorse.
Basic wire strippers from a hardware store work equally well.

---

## 3. General Hardware Tools

These apply to **all builds**, soldered or not.

---

### Digital Multimeter

A multimeter is not required to build AeroMorse but is invaluable for
troubleshooting wiring problems. Look for one with at minimum:

- **Continuity mode** (beeps when two points are connected) — for testing
  AT switch plugs and checking wiring
- **DC voltage mode** — for confirming 3.3 V on power pins
- **Resistance mode** — for confirming pull-up resistors

Any basic digital multimeter from a hardware store (Bunnings, Home Depot,
Maplin, etc.) for $15–30 will cover all of these. Adafruit also sells
multimeters — search https://www.adafruit.com for "multimeter".

---

### Small Scissors or Craft Knife

For cutting the sip-and-puff tube to length. Any household scissors work.
A straight, clean cut is easier to achieve with scissors than a knife.

---

### Silicone Tape (self-fusing)

If the sip-and-puff tube feels loose on the LPS33HW sensor's pressure port,
wrap one or two layers of silicone tape around the port nipple before pushing
the tube on. Self-fusing silicone tape sticks to itself without adhesive and
comes off cleanly. Available at hardware stores (~$5 for a roll).

---

### Velcro Strips / Cable Ties

For mounting the sensor, display, or Feather to a surface. Adhesive-backed
velcro strips let you reposition without damage. Available at any hardware or
stationery store.

---

## 4. Wiring Supplies

Needed only if connecting a **standalone breakout display** (not a FeatherWing)
or building the **soldered TRRS option**.

---

### Jumper Wires — Male to Male (breadboard builds)

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Breadboarding Wire Bundle (75 wires, 26 AWG) | #153 | $4.95 | https://www.adafruit.com/product/153 |

Pre-cut, pre-stripped solid-core wires in assorted lengths. Push directly into
breadboard holes — no stripping needed. The assorted lengths mean you will
always have a wire that reaches without looping.

---

### Hookup Wire (for soldered builds)

| Product | Adafruit # | Price | URL |
|---------|-----------|-------|-----|
| Hook-Up Wire Spool Set — 6 colours, 22 AWG | #1311 | varies | https://www.adafruit.com/product/1311 |

For cutting custom wire lengths when connecting the TRRS breakout or a
standalone display to the Feather. Use different colours for different signals
(red = power, black = ground, etc.) — it makes tracing and debugging much
easier.

---

## 5. Learning Guides

All guides below are free.

---

### CircuitPython — Getting Started

| Guide | URL |
|-------|-----|
| Welcome to CircuitPython | https://learn.adafruit.com/welcome-to-circuitpython |
| CircuitPython Essentials | https://learn.adafruit.com/circuitpython-essentials |

**Welcome to CircuitPython** is the starting point for anyone new to
CircuitPython. Covers installing CircuitPython, copying files, using the
serial console, and the basics of writing code. Read this before anything
else if you are new to microcontrollers.

**CircuitPython Essentials** goes deeper — analog and digital I/O, I²C, SPI,
NeoPixels, and more. Not required for building AeroMorse but useful background
for understanding how the code works.

---

### Board-Specific Guides (choose yours)

| Board | Guide URL |
|-------|-----------|
| ESP32-S3 Feather #5477 | https://learn.adafruit.com/adafruit-esp32-s3-feather |
| ESP32-S3 TFT Feather #5483 | https://learn.adafruit.com/adafruit-esp32-s3-tft-feather |
| ESP32-S3 Reverse TFT Feather #5691 | https://learn.adafruit.com/adafruit-esp32-s3-reverse-tft-feather |
| ESP32-S2 TFT Feather #5300 | https://learn.adafruit.com/adafruit-esp32-s2-tft-feather |

Each guide covers pinouts, CircuitPython installation, and first-use
instructions specific to that board. Recommended to read alongside this build
guide — the pinout diagram is particularly useful when wiring.

---

### Sip-and-Puff Sensor

| Guide | URL |
|-------|-----|
| CircuitPython Sip & Puff with ST LPS33HW | https://learn.adafruit.com/st-lps33-and-circuitpython-sip-and-puff |

The official Adafruit guide for the LPS33HW pressure sensor used in AeroMorse.
Covers sensor calibration, reading pressure values, setting thresholds, and
breath technique for reliable input. **Read this if you are using sip-and-puff
input** — it explains the physical technique that makes the sensor work well.

---

### Soldering

| Guide | URL |
|-------|-----|
| Adafruit Guide to Excellent Soldering | https://learn.adafruit.com/adafruit-guide-excellent-soldering |

The definitive beginner's soldering guide. Covers tools, preparation, technique,
common mistakes, and how to fix them. Includes clear photos of good and bad
solder joints. **Read this before your first soldering session.**

---

### USB HID with CircuitPython

| Guide | URL |
|-------|-----|
| CircuitPython HID — Keyboard and Mouse | https://learn.adafruit.com/circuitpython-essentials/circuitpython-hid-keyboard-and-mouse |

Explains how CircuitPython's `usb_hid` and `adafruit_hid` libraries work —
the same libraries AeroMorse uses to appear as a keyboard and mouse. Useful
background if you want to understand or customise the key mappings.

---

### Display Guides (choose yours)

| Display | Guide URL |
|---------|-----------|
| 0.96" / 1.3" SSD1306 OLED | https://learn.adafruit.com/monochrome-oled-breakouts |
| 2.4" TFT FeatherWing #3315 | https://learn.adafruit.com/adafruit-2-4-tft-touch-screen-featherwing |
| 3.5" TFT FeatherWing #3651 / #5872 | https://learn.adafruit.com/adafruit-3-5-tft-touch-screen-featherwing |
| 2.8" / 3.2" ILI9341 TFT | https://learn.adafruit.com/adafruit-2-8-and-3-2-color-tft-touchscreen-breakout-v2 |
| 2.0" ST7789 TFT #4311 | https://learn.adafruit.com/2-0-inch-320-x-240-color-ips-tft-display |

---

## 6. Morse Code References

You do not need to memorise Morse code to use AeroMorse — keep a reference
card nearby while you learn. The patterns used by AeroMorse follow standard
ITU Morse for letters and numbers, with a small number of deliberate
variations for high-frequency control keys (documented in `morse_map.py`).

---

### International Morse Code (ITU standard)

```
A  .-      N  -.      1  .----   .  .-.-.-
B  -...     O  ---     2  ..---   ,  --..--
C  -.-.     P  .--.    3  ...--   ?  ..--..
D  -..      Q  --.-    4  ....-   /  -..-.
E  .        R  .-.     5  .....   -  -....-
F  ..-.     S  ...     6  -....   (  -.--.
G  --.      T  -       7  --...   )  -.--.-
H  ....     U  ..-     8  ---..   =  -...-
I  ..       V  ...-    9  ----.   +  .-.-.
J  .---     W  .--     0  -----   @  .--.-.
K  -.-      X  -..-
L  .-..     Y  -.--
M  --       Z  --..
```

> **AeroMorse non-standard patterns:**
> `M` is mapped to `----` (four dashes) — the standard `--` is used for Backspace
> `C` is mapped to `---.` — the standard `-.-.` is used for Left Control

---

### Printable Reference Cards

- **Learn Morse Code — Wikipedia:**
  https://en.wikipedia.org/wiki/Morse_code

- **ITU Recommendation M.1677 (official standard):**
  https://www.itu.int/rec/R-REC-M.1677/en

- **Morse code trainer (browser-based, free):**
  https://morse.withgoogle.com/learn/

---

### AeroMorse-specific Morse map

The complete code table for all groups (keyboard, mouse, macros) is in
`morse_map.py` in the project folder, and documented in `README.md`.

Key patterns to learn first:

| Pattern | Action | Note |
|---------|--------|------|
| `...-. ` (pause) | Switch to Mouse group | From Keyboard group |
| Long sip (≥ 1 s) | Cycle groups backward | 1 → 3 → 2 → 1 |
| Long puff (≥ 1 s) | Cycle groups forward | 1 → 2 → 3 → 1 |
| `........` (8 dots) | Jump to Keyboard group | Works in any group |
| `--------` (8 dashes) | Jump to Mouse group | Works in any group |
| `....----` | Jump to Macro group | Works in any group |
