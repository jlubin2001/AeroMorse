# AeroMorse — Complete Build Guide
### USB HID Keyboard & Mouse via Sip-and-Puff or Accessibility Switches

This guide walks a first-time, non-technical builder through every decision and
every step needed to assemble a working AeroMorse device. Read the whole guide
once before buying anything — your hardware choices affect each other.

---

## Table of Contents

1. [What AeroMorse Does](#1-what-aeromorse-does)
2. [How This Guide Works](#2-how-this-guide-works)
3. [Compatible Feather Boards](#3-compatible-feather-boards)
4. [Display Options](#4-display-options)
   - [Wireless Display — ESP-NOW Remote Mirror](#wireless-display--esp-now-remote-mirror)
5. [Input Method Options](#5-input-method-options)
6. [Speaker Options](#6-speaker-options)
7. [Complete Parts Lists](#7-complete-parts-lists)
8. [Step-by-Step Assembly](#8-step-by-step-assembly)
9. [Software Installation](#9-software-installation)
10. [Configuration](#10-configuration)
11. [First Power-On Test](#11-first-power-on-test)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. What AeroMorse Does

AeroMorse is an open-source CircuitPython project by Jim Lubin — a
ventilator-dependent quadriplegic who has used Morse code for computer access
since 1989 — that turns an Adafruit Feather microcontroller into a USB HID
keyboard and mouse. Inspired by
[AirTalker](https://github.com/ATMakersOrg/AirTalker), it connects via USB-C
and appears to the host as a standard keyboard and mouse with no drivers
required. Works on **Windows, macOS, Linux, iPadOS, Android, and ChromeOS**.

Input is by **sip-and-puff** (LPS33HW pressure sensor) or **two standard AT
switches**. A short sip (or switch 1) is a dot; a short puff (or switch 2) is
a dash. A small OLED display shows the active group, the Morse pattern as it
builds, and the last action. An optional speaker beeps for every dot and dash.

Four groups organize all functions:

- **Group 0** — always-available emergency group-switch patterns
- **Group 1** — keyboard: letters, numbers, punctuation, function keys,
  navigation, sticky modifiers
- **Group 2** — mouse movement, clicks, drag, repeat, and Windows shortcuts
- **Group 3** — user-defined macro text strings

Groups cycle with a long sip or puff. An optional **ESP-NOW wireless display**
mirrors the main screen on a second board up to ~30 m away — useful when the
sensor is mounted behind the user.

Existing **Darci USB** users can drop in `morse_map_darci.py` to use their
familiar code set. All Morse assignments are fully customizable in
`morse_map.py`. Parts cost approximately **$50–$100** in off-the-shelf
components.

### Morse code basics

| Symbol | Input | Display |
|--------|-------|---------|
| Dot | Short sip or press | `.` |
| Dash | Short puff or press | `-` |
| Letter gap | Pause ≥ 0.2 s | (pattern fires) |

Example: sip · puff · puff = `. - -` = the letter **W**

You do not need to know Morse code from memory to begin — the device can be used
with a printed reference card while you learn.

---

## 2. How This Guide Works

AeroMorse has modular hardware. You pick:

1. **A Feather microcontroller board** (the brain)
2. **A display** (what you see)
3. **An input method** (sip-and-puff sensor or AT switches)
4. **A speaker** (optional audio feedback)

Once you have chosen each, jump to the relevant wiring section in Step 8.

> **Recommended combination for most builders (USB HID, display included):**
> ESP32-S3 Reverse TFT Feather #5691 · LPS33HW sensor #4414 · STEMMA Speaker #3885
>
> **If you want a separate, repositionable display without jumper wires:**
> ESP32-S3 EYESPI Feather #5613 · 2.0" EYESPI TFT #5800 · EYESPI cable #5240
> · LPS33HW sensor #4414 · STEMMA Speaker #3885
>
> **If you need Bluetooth wireless HID:**
> Metro ESP32-S3 #5500 · 1.3" OLED #938 · LPS33HW sensor #4414 · STEMMA Speaker #3885

---

## 3. Compatible Feather Boards

### Why not every Feather works

AeroMorse uses **USB HID** — the USB standard that lets keyboards and mice talk
to computers. Only Feather boards with **native USB** support this. Classic
ESP32 boards (including Adafruit #5900 Feather ESP32 V2) use a separate USB-to-
serial chip that cannot emulate a keyboard. Those boards will not work.

### BLE HID note — CircuitPython 10.x

BLE HID on ESP32-S3 was unreliable in CircuitPython 9.x due to two known
bugs. Both were fixed (issues #9430 and #9669, resolved in late 2024) and the
fixes carry through CircuitPython 10.x (current stable: **10.2.0, April 2026**).

**Important flash size requirement:** The ESP32-S3 CircuitPython firmware
build must be large enough to include the BLE stack. Boards with **4 MB flash**
(#5477, #5483, #5691) may ship with BLE omitted from their firmware image to
fit. Boards with **8 MB flash or more** have room for the full build including
BLE. Check circuitpython.org for your specific board — the download page lists
exactly which features are included.

---

### Boards that work

| Board | Adafruit # | USB HID | BLE HID | PSRAM | WiFi | Notes |
|-------|-----------|---------|---------|-------|------|-------|
| ESP32-S3 Feather 4MB/2MB PSRAM | [#5477](https://www.adafruit.com/product/5477) | ✓ | ※ | ✓ 2MB | ✓ | **Recommended — see below** |
| ESP32-S3 Feather w/ EYESPI Connector | [#5613](https://www.adafruit.com/product/5613) | ✓ | ※ | ✓ 2MB | ✓ | No built-in display; **18-pin EYESPI FPC connector** drives any EYESPI TFT with one flex cable |
| ESP32-S3 TFT Feather | [#5483](https://www.adafruit.com/product/5483) | ✓ | ※ | ✓ 2MB | ✓ | Built-in 1.14" TFT — screen faces up (normal) |
| ESP32-S3 Reverse TFT Feather | [#5691](https://www.adafruit.com/product/5691) | ✓ | ※ | ✓ 2MB | ✓ | Built-in 1.14" TFT — screen faces down (panel mount) |
| ESP32-S2 TFT Feather | [#5300](https://www.adafruit.com/product/5300) | ✓ | — | ✓ 2MB | ✓ | Built-in 1.14" TFT — older S2 chip; no BLE |
| ESP32-S2 Feather w/ BME280 | [#5303](https://www.adafruit.com/product/5303) | ✓ | — | ✓ 2MB | ✓ | S2 chip (no BLE); BME280 sensor not used by AeroMorse |
| Feather nRF52840 Express | [#4062](https://www.adafruit.com/product/4062) | ✓ | ✓ | — | — | Most mature BLE HID; no PSRAM |
| Feather Sense (nRF52840) | [#4516](https://www.adafruit.com/product/4516) | ✓ | ✓ | — | — | nRF52840 + onboard sensors; no PSRAM |
| Feather RP2040 | [#4884](https://www.adafruit.com/product/4884) | ✓ | — | — | — | No wireless; very capable USB HID |
| Feather M4 Express (SAMD51) | [#3857](https://www.adafruit.com/product/3857) | ✓ | — | — | — | Fast; no wireless |

※ BLE HID bugs fixed in CircuitPython 10.x, but requires 8MB+ flash firmware
build to include the BLE stack. Verify at circuitpython.org before relying on
BLE from a 4MB flash board.

### Metro form factor boards

Metro boards use the Arduino Uno footprint (68×53 mm) — larger than a Feather.
They work for AeroMorse but with one key difference: **FeatherWing displays
will not plug directly onto them.** Use a standalone TFT breakout (SPI wires)
or the STEMMA QT OLED instead. The pressure sensor plugs straight in via
STEMMA QT with no wiring change.

| Board | Adafruit # | USB HID | BLE HID | PSRAM | WiFi | Notes |
|-------|-----------|---------|---------|-------|------|-------|
| Metro ESP32-S3 | [#5500](https://www.adafruit.com/product/5500) | ✓ | ✓ | ✓ **8MB** | ✓ | **Only board with USB HID + BLE HID + PSRAM**; built-in LiPoly charging + battery monitor |
| Metro RP2350 w/ PSRAM | [#6267](https://www.adafruit.com/product/6267) | ✓ | — | ✓ **8MB** | — | No wireless; 8MB PSRAM + reliable USB HID |

> The Metro ESP32-S3 #5500 (16MB flash) has room for the full CircuitPython
> firmware including BLE. It is the only board in this guide that combines
> reliable USB HID, reliable BLE HID (CircuitPython 10.x), and 8MB PSRAM.

---

### Boards that do NOT work for USB HID

| Board | Reason |
|-------|--------|
| Feather ESP32 V2 #5400 | No native USB — uses CP2102N serial chip |
| Feather ESP32 Huzzah #3405 | No native USB |
| Feather ESP8266 #2821 | No native USB |

---

### Recommended board: Adafruit ESP32-S3 Reverse TFT Feather #5691

**Why this one:**

- **Display already built in** — the 240×135 colour TFT is soldered to the
  board, facing down for panel mounting; no separate display to buy or wire
- Has **PSRAM** (2 MB extra RAM) — handles all display and sensor work without
  running out of memory
- Has a **STEMMA QT** port — the LPS33HW pressure sensor plugs straight in with
  no soldering
- **WiFi + ESP-NOW** built in — supports the wireless remote display option
  (Section 4) without any extra hardware on the main board
- USB HID works out of the box — appears as keyboard and mouse to any computer
- CircuitPython support is excellent and actively maintained
- Available from Adafruit:
  https://www.adafruit.com/product/5691

---

**If you want the same simplicity with the screen facing up (not panel-mounted):**

The **ESP32-S3 TFT Feather #5483** is identical to #5691 except the display
faces the same side as the components. Everything else — PSRAM, STEMMA QT,
ESP-NOW, USB HID — is the same.
https://www.adafruit.com/product/5483

---

**If you want a separate display without messy wiring (EYESPI):**

The **ESP32-S3 Feather with EYESPI Connector #5613** has the same ESP32-S3
brain as #5691 (USB HID, ESP-NOW, STEMMA QT, 2 MB PSRAM) but with an **18-pin
EYESPI FPC connector** instead of a built-in display. EYESPI replaces the 5–7
jumper wires normally needed for an SPI TFT with a single flat flex cable —
plug, plug, done. Choose this if you want the display physically separated
from the Feather (e.g. on an arm at eye level, in a cleaner enclosure, or
swappable between display sizes) without the soldering and jumper-wiring
that the standalone-breakout path requires. See §4 "EYESPI displays" for
compatible screens.
https://www.adafruit.com/product/5613

---

**If you want BLE HID + PSRAM + the most memory (Metro form factor):**

The **Metro ESP32-S3 #5500** is the only board in this guide that combines all
three: reliable USB HID, reliable BLE HID, and 8 MB PSRAM. Use this board if
you need to control a phone, iPad, or PC wirelessly over Bluetooth without a
USB cable. BLE HID on the ESP32-S3 was unreliable in earlier CircuitPython
versions but is fully fixed in CircuitPython 10.x (current stable: 10.2.0).

The #5500 has no built-in display — connect the STEMMA QT OLED or a standalone
TFT breakout. The ESP-NOW wireless display (Section 4) works on it identically
to the Feather boards.
https://www.adafruit.com/product/5500

---

**If you want wireless HID (BLE) and do not need a large colour display:**

The **nRF52840 Feather #4062** has the most mature and battle-tested BLE HID
implementation in CircuitPython — it predates the ESP32-S3 fixes by years and
works reliably on iOS, Android, and Windows.
https://www.adafruit.com/product/4062

**What PSRAM is and why it matters for display choice:**

PSRAM is extra RAM soldered onto the board alongside the main chip. The
ESP32-S3 chip itself has 512 KB of built-in RAM. A colour TFT display needs a
*framebuffer* — a block of RAM that holds every pixel on screen before sending
it to the display. Here is how the numbers work out:

| Display | Resolution | Framebuffer RAM needed |
|---------|-----------|----------------------|
| 128×64 OLED (monochrome) | 8,192 pixels | ~1 KB |
| 240×135 TFT (built-in on #5691) | 32,400 pixels × 2 bytes | ~63 KB |
| 320×240 TFT FeatherWing | 76,800 pixels × 2 bytes | ~150 KB |
| 480×320 TFT FeatherWing #3651 | 153,600 pixels × 2 bytes | ~300 KB |

The nRF52840 has **256 KB** of total RAM — shared between your code, variables,
and the display framebuffer. A 128×64 OLED uses only ~1 KB of that, leaving
plenty for everything else. A 480×320 colour TFT at ~300 KB would leave
nothing for the program itself and simply won't fit.

The ESP32-S3 boards with PSRAM have **2 MB** (or 8 MB on the #5500) of extra
RAM on top of the 512 KB built-in. The framebuffer lives in PSRAM, leaving the
main 512 KB free for code. Any display size works.

**Practical rule:**
- Using the **STEMMA QT OLED** (128×64)? → nRF52840 has more than enough RAM.
  The OLED is a fine choice here and gives you the most mature BLE HID.
- Using the **built-in 240×135 TFT** or any FeatherWing colour display? →
  You need PSRAM. Choose the #5500 (Metro) or an ESP32-S3 Feather.
- Using the **ESP-NOW wireless display** option? → The main board's display
  is just the small built-in TFT or an OLED, so nRF52840 could work — but
  it has no WiFi or ESP-NOW, so the wireless display feature is unavailable.

---

**Quick decision guide:**

| I want… | Choose |
|---------|--------|
| Simplest build, colour TFT included, USB only | #5691 Reverse TFT Feather |
| Same but screen faces up | #5483 TFT Feather |
| Separate display, single flex cable, no jumper wires | **#5613 + EYESPI display** |
| BLE HID + colour TFT or large display | #5500 Metro ESP32-S3 |
| BLE HID + OLED only (no large display needed) | #4062 nRF52840 Feather |
| No wireless needed, just USB HID | #4884 RP2040 Feather or #3857 M4 Feather |

---

### Building with no header pins — what works

Many Feather boards ship as bare PCBs with no header pins soldered. If you
don't want to solder headers (and your supplier didn't pre-install them),
some build paths still work via STEMMA QT plug-and-play, some require
soldering a few wires directly to the Feather's PCB pads, and some
fundamentally need headers.

| Component / option | Works without headers? | What's needed |
|---|---|---|
| **#5691 built-in TFT display** | ✓ Plug-and-play | Display soldered to board — nothing to wire |
| **#5613 + EYESPI display** | ✓ Plug-and-play | One flex cable, both ends plug-in |
| **STEMMA QT OLED (#326, #938)** | ✓ Plug-and-play | STEMMA QT cable, no Feather wiring |
| **STEMMA QT sensor (#4414 LPS33HW)** | ✓ Plug-and-play | STEMMA QT cable |
| **FeatherWing displays (#3651, #5872, #3315)** | ✗ Not possible | The wing's holes can't grip bare pads — headers required |
| **Standalone TFT breakouts (#2050, #1770…)** | ⚠ Solder 5–7 wires | Solder display wires directly to Feather pads |
| **AT switches — Option B1 breadboard** | ✗ Not possible | Feather must sit *in* the breadboard via headers |
| **AT switches — Option B2 TRRS breakout** | ⚠ Solder 3 wires | Solder breakout output wires to D5/D6/GND pads |
| **AT switches — Option B3 #2915 Terminal Block** | ⚠ Solder 3 wires | Solder terminal-block wires to D5/D6/GND pads |
| **Speaker — #3885 STEMMA Speaker** | ⚠ Solder 3 wires | Cut JST PH plug off, solder to A0/3V/GND pads |
| **Speaker — Piezo (#1740/#1739)** | ⚠ Solder 2 wires | Solder leads to A0/GND pads |
| **Speaker — PAM8302 amp (#2130)** | ⚠ Solder 3 wires | Solder amp board to A0/3V/GND pads |

**STEMMA QT does not solve every problem.** STEMMA QT carries I²C, 3 V, and
GND only — that is enough for sensors and I²C displays (OLEDs), but **not
for audio** (analog signal must come from A0) or **arbitrary switches**
(digital inputs need GPIO pins).

> An I²C GPIO expander board (AW9523 #4886, MCP23017 #5346, PCF8575 #5611)
> *could* host AT switches via STEMMA QT, but you still need to wire jacks
> to the expander's GPIO pads — and `code.py` would need a new library and
> rewritten input routines. **More work, no benefit** vs. soldering three
> wires directly to D5/D6/GND on the Feather.

**Recommended fully-header-less build:**

- Feather: **#5691** (built-in TFT — no wiring) or **#5613 + EYESPI** display
- Sensor: **#4414 LPS33HW** via STEMMA QT (or skip if using AT switches)
- AT switches: **#2915 Terminal Block** + 3 wires soldered to D5/D6/GND pads
- Speaker: 3 wires soldered to A0/3V/GND pads (or skip — display alone is fine)

Total soldering for the full build: **3–6 wires to Feather pads** (skip the
sensor row if you use switches, skip both if you don't want a speaker).
Each pad is ~1.5 mm — much easier to solder than the pin holes for headers.

> **No soldering at all?** Skip the speaker and use the **#5691 + sensor
> only** combination. The OLED/TFT shows every dot and dash visually. Cost:
> a #5691 + #4414 + STEMMA QT cable, ~$30, zero solder joints. Add a
> third-party 3.5 mm Y-splitter and your existing AT switches won't work
> in this config — sensor mode is the no-solder path.

---

## 4. Display Options

All displays below are supported by CircuitPython's `displayio` system and work
with AeroMorse. The code must be updated to match the display driver you choose.

### Understanding the columns

- **Form factor:** FeatherWing plugs directly onto the Feather (no wiring).
  Breakout/standalone requires 5 wires.
- **Interface:** SPI displays have no I²C address conflicts with the sensor.
- **Resolution:** Higher = more text/detail. The Morse buffer, group name, last
  action, and status line all fit comfortably on 320×240 or larger.

---

### Built-in display — no separate display needed

| Board | # | Display size | Resolution | Screen orientation | URL |
|-------|---|-------------|-----------|-------------------|-----|
| ESP32-S3 TFT Feather | [5483](https://www.adafruit.com/product/5483) | 1.14" | 240×135 colour | Faces up — same side as components | https://www.adafruit.com/product/5483 |
| ESP32-S3 Reverse TFT Feather | [5691](https://www.adafruit.com/product/5691) | 1.14" | 240×135 colour | Faces down — opposite side to components | https://www.adafruit.com/product/5691 |
| ESP32-S2 TFT Feather | [5300](https://www.adafruit.com/product/5300) | 1.14" | 240×135 colour | Faces up — same side as components | https://www.adafruit.com/product/5300 |

All three have the display soldered onto the board and accessed via
`board.DISPLAY` — no wiring, no extra purchase, no library to add.

**Which orientation to choose:**
- **#5483 (standard)** — screen faces the same direction as the USB port and
  pins. Best for handheld use or when you want to see the display while working
  with the board.
- **#5691 (reverse)** — screen faces the opposite side. Designed for mounting
  behind a panel with a cutout so only the screen shows through. Useful if you
  want to build AeroMorse into an enclosure.
- **#5300 (ESP32-S2)** — same orientation as #5483 but older chip. Only choose
  it if #5483 and #5691 are both unavailable.

All three are functionally identical for AeroMorse.

> **Code file:** #5483, #5691, and #5300 all use **`v1/code.py`**, not
> `v2/code.py`. Copy `v1/code.py` to the CIRCUITPY drive instead. Everything
> else (libraries, `boot.py`, `morse_map.py`) is the same.

---

### FeatherWing displays (plug directly on Feather — easiest)

| Display | # | Size | Resolution | Interface | URL |
|---------|---|------|-----------|-----------|-----|
| 3.5" TFT Resistive Touch | [3651](https://www.adafruit.com/product/3651) | 3.5" | 480×320 colour | SPI | https://www.adafruit.com/product/3651 |
| 3.5" TFT Capacitive Touch | [5872](https://www.adafruit.com/product/5872) | 3.5" | 480×320 colour | SPI | https://www.adafruit.com/product/5872 |
| 2.4" TFT Resistive Touch | [3315](https://www.adafruit.com/product/3315) | 2.4" | 320×240 colour | SPI | https://www.adafruit.com/product/3315 |

> FeatherWings have a touchscreen controller that uses I²C. You will not use
> touch input with AeroMorse — the display portion works via SPI independently
> and will not conflict with the pressure sensor.

**Recommended for table mounting: #3651** — largest FeatherWing, bright colour,
plugs straight on with no wiring.

---

### Standalone / breakout displays (5 wires required)

| Display | # | Size | Resolution | Driver | URL |
|---------|---|------|-----------|--------|-----|
| 3.5" TFT with Touch | [2050](https://www.adafruit.com/product/2050) | 3.5" | 480×320 colour | HX8357D | https://www.adafruit.com/product/2050 |
| 3.2" TFT with Touch | [1743](https://www.adafruit.com/product/1743) | 3.2" | 320×240 colour | ILI9341 | https://www.adafruit.com/product/1743 |
| 2.8" TFT with Touch | [1770](https://www.adafruit.com/product/1770) | 2.8" | 320×240 colour | ILI9341 | https://www.adafruit.com/product/1770 |
| 2.0" IPS TFT | [4311](https://www.adafruit.com/product/4311) | 2.0" | 320×240 colour | ST7789 | https://www.adafruit.com/product/4311 |

Standalone displays are useful when you want the display mounted separately from
the Feather — for example, a display on an arm at eye level with the Feather
tucked out of the way.

---

### EYESPI displays (one flex cable, no jumper wires) — paired with #5613

EYESPI is Adafruit's standardised **18-pin FPC connector** for SPI displays.
Combined with the **ESP32-S3 Feather w/ EYESPI Connector #5613**, an entire
SPI TFT — power, ground, MOSI, MISO, SCK, CS, DC, reset, backlight — runs
through a single flat flex cable. No breadboard, no jumper wires, no soldering
once both ends are plugged in.

This is the **easiest non-built-in display path** in this guide — simpler
than the FeatherWing displays (no full-board stack required) and dramatically
simpler than the standalone breakout displays (no 5–7 wires to track).

| Display | # | Size | Resolution | Driver | URL |
|---------|---|------|-----------|--------|-----|
| 2.0" 320×240 IPS TFT EYESPI | [5800](https://www.adafruit.com/product/5800) | 2.0" | 320×240 colour | ST7789 | https://www.adafruit.com/product/5800 |
| 1.3" 240×240 IPS TFT EYESPI | [5393](https://www.adafruit.com/product/5393) | 1.3" | 240×240 colour | ST7789 | https://www.adafruit.com/product/5393 |
| 1.14" 240×135 IPS TFT EYESPI | [5394](https://www.adafruit.com/product/5394) | 1.14" | 240×135 colour | ST7789 | https://www.adafruit.com/product/5394 |
| 1.54" 240×240 round IPS TFT EYESPI | [5610](https://www.adafruit.com/product/5610) | 1.54" round | 240×240 colour | GC9A01A | https://www.adafruit.com/product/5610 |
| 1.5" 128×128 OLED EYESPI | [5398](https://www.adafruit.com/product/5398) | 1.5" | 128×128 colour OLED | SSD1351 | https://www.adafruit.com/product/5398 |

**Also required: one EYESPI cable.** Adafruit sells them in several lengths so
the display can be mounted where it is most visible:

| Cable | # | Length | URL |
|-------|---|--------|-----|
| EYESPI Cable 50 mm | [5239](https://www.adafruit.com/product/5239) | 50 mm | https://www.adafruit.com/product/5239 |
| EYESPI Cable 100 mm | [5240](https://www.adafruit.com/product/5240) | 100 mm | https://www.adafruit.com/product/5240 |
| EYESPI Cable 200 mm | [5241](https://www.adafruit.com/product/5241) | 200 mm | https://www.adafruit.com/product/5241 |

**Recommended EYESPI display: #5800 (2.0" 320×240).** Largest of the EYESPI
options, easy to read across a desk, and the ST7789 driver is the same one
used by the built-in TFT on #5691 — minimal code changes.

> **Code file:** The EYESPI displays are not built-in displays — `board.DISPLAY`
> is not auto-populated. You must initialise the display manually in `code.py`
> using `displayio` and the appropriate driver library (e.g.
> `adafruit_st7789`). This is the same one-time setup used by the standalone
> breakout displays above; an example is provided in §10 "Configuration".

---

### OLED displays (STEMMA QT plug-and-play, monochrome, no colour)

| Display | # | Size | Resolution | Driver | URL |
|---------|---|------|-----------|--------|-----|
| 0.96" Monochrome OLED | [326](https://www.adafruit.com/product/326) | 0.96" | 128×64 | SSD1306 | https://www.adafruit.com/product/326 |
| 1.3" Monochrome OLED | [938](https://www.adafruit.com/product/938) | **1.3"** | 128×64 | SSD1306 | https://www.adafruit.com/product/938 |

Both connect via STEMMA QT — no soldering. Both use the same SSD1306 driver, the
same library, and the same I²C address (0x3C). The v2 code works with either
with **no changes at all** — simply swap the physical display.

**#326 (0.96")** is the v2 default — compact, easy to mount on a tube holder.
**#938 (1.3")** is a direct plug-in upgrade — 35% larger, identical wiring and
code. A better choice if you want a slightly bigger display without any of the
complexity of a TFT.

---

---

### Wireless Display — ESP-NOW Remote Mirror

Use this option when the **sensor must be behind you** (tube runs behind the
wheelchair, head support, or mounting arm) but you need to **see the display
in front of you**. A second small board receives the display state wirelessly
and shows it on its own screen — no cable runs between them.

**How it works:** The main board broadcasts the four display fields (group name,
Morse buffer, last action, status) over **ESP-NOW** once every 100 ms. ESP-NOW
is a fast, connectionless wireless protocol built into every ESP32 chip — it
requires no router, no pairing, no configuration. The second board just
listens. Range is approximately 30 m indoors.

**CircuitPython versions — each board is completely independent:**
The two boards do not share code or libraries. ESP-NOW sends plain bytes over
the air with no awareness of CircuitPython versions. Each board runs its own
CircuitPython and its own `/lib` folder. You can have CP9 on the main board
and CP10 on the receiver, or any combination — no steps are needed to make
them work together. The only requirement is that each board runs **at least
CP9** (earlier versions did not include the `espnow` module). There is no need
to match versions, update one when you update the other, or do anything
differently when the versions differ.

> **If you copy the `/lib` folder from the main board to the receiver**, make
> sure both boards are running the **same major version** (both CP9 or both
> CP10) — `.mpy` library files compiled for CP9 will not load under CP10 and
> vice versa. If the boards are on different major versions, download the
> matching library bundle for each board separately from circuitpython.org
> and copy the files individually. The receiver only needs one folder from
> the bundle: `adafruit_display_text/`.

---

#### Option W1 — Second ESP32-S3 Reverse TFT Feather #5691 ⭐ Recommended

**https://www.adafruit.com/product/5691 — $34.95**

This is the exact same board as the main AeroMorse unit. The built-in
240×135 colour TFT mirrors the main display perfectly — same four rows, same
font size, same group colours (blue for Keyboard, green for Mouse, orange for
Macro). No extra display hardware to buy or wire.

| Advantages | Notes |
|-----------|-------|
| Identical display to the main board | Each board runs its own CircuitPython independently |
| No extra display purchase or wiring | See library note above if versions differ |
| Full colour with group indicator colours | Can run from USB-C charger/power bank or LiPoly battery |
| No new libraries needed | Does **not** act as a keyboard (has its own `boot.py`) |

**Powering the receiver wirelessly — LiPoly battery options:**

The #5691 has a built-in JST-PH battery connector and charges over USB-C. Plug in any of the batteries below and the receiver runs completely cable-free.

| Adafruit # | Capacity | Est. runtime | Size / notes | Price | URL |
|-----------|---------|-------------|-------------|-------|-----|
| #3898 | 400 mAh | ~3–5 hrs | **Slim flat pack** — designed to sit flush against the back of a Feather; thinnest option | $6.95 | https://www.adafruit.com/product/3898 |
| #1578 | 500 mAh | ~4–6 hrs | Small pouch, slightly thicker than #3898; good balance of size and runtime for half-day use | $7.95 | https://www.adafruit.com/product/1578 |
| #258 | 1200 mAh | ~9–14 hrs | Full-day runtime; fits in a small case or pouch; recommended for all-day use | $9.95 | https://www.adafruit.com/product/258 |

> Runtime estimates assume ~80–130 mA active draw (ESP32-S3 + TFT on + ESP-NOW receiving).
> Recharging happens automatically when the USB-C cable is plugged back in — no separate charger needed.

**Files needed on the second board:**

| File on your computer | Copy to second board as |
|----------------------|------------------------|
| `receiver.py` | `code.py` |
| `receiver_boot.py` | `boot.py` |
| `adafruit_display_text/` from the matching CP bundle | `/lib/adafruit_display_text/` |

> `receiver_boot.py` deliberately does **not** enable USB HID. This prevents
> Windows from seeing the second board as a second keyboard or mouse.

---

#### Option W2 — Seeed XIAO ESP32C3 + SSD1306 OLED

A cheaper alternative using a small third-party board and a 128×64
monochrome OLED. Same ESP32-C3 chip as the Adafruit QT Py ESP32-C3 (if that
had been available), fully supported by CircuitPython 9.x or later and ESP-NOW.

**XIAO ESP32C3:** ~$7 — DigiKey (ships same day) or Amazon Prime  
**SSD1306 128×64 I2C OLED:** ~$4 — Amazon (search "SSD1306 128x64 I2C OLED")

| Advantages | Notes |
|-----------|-------|
| Lower cost (~$11 vs $35) | Monochrome display — no group colours |
| Amazon Prime shipping | Requires soldering 4 wires to OLED |
| Smaller form factor | One line of code must change (see below) |

The XIAO has no STEMMA QT connector. Solder four short wires between the XIAO
and the OLED's 4-pin header:

| OLED pin | XIAO pin |
|----------|---------|
| VCC | 3V3 |
| GND | GND |
| SCL | SCL (D3) |
| SDA | SDA (D2) |

**One code change in `receiver.py`** (before copying to the XIAO as `code.py`):

```python
# Change this line:
i2c = board.STEMMA_I2C()

# To this:
import busio
i2c = busio.I2C(board.SCL, board.SDA)
```

**Libraries needed on the XIAO's `/lib` folder** (not needed for Option W1):

```
adafruit_displayio_ssd1306.mpy
adafruit_display_text/
```

> **Option W2 is not recommended for first-time builders** due to the
> soldering requirement. Option W1 is plug-and-play.

---

#### Wireless display comparison

| | Option W1 — Second #5691 | Option W2 — XIAO + OLED |
|--|--|--|
| Cost | $35 | ~$11 |
| Display | 240×135 colour TFT | 128×64 mono OLED |
| Group colours | ✓ Yes | ✗ No |
| Assembly | Plug USB-C in | Solder 4 wires |
| Code change | None | 1 line |
| Libraries to add | None (reuse existing) | 2 files |
| Availability | adafruit.com | Amazon / DigiKey |
| Wireless power | ✓ LiPoly battery (#3898 / #1578 / #258) | ✗ No battery connector |

---

### Display driver library required per display chip

| Chip | Library | Used by |
|------|---------|---------|
| Built-in (board.DISPLAY) | *(none — built in)* | #5691 Reverse TFT Feather — use `v1/code.py` |
| SSD1306 | `adafruit_displayio_ssd1306` | #326 (0.96" OLED) and #938 (1.3" OLED) |
| ILI9341 | `adafruit_ili9341` | #3315, #1770, #1743 |
| HX8357D | `adafruit_hx8357` | #3651, #5872, #2050 |
| ST7789 | `adafruit_st7789` | #4311 |

> **Note:** Adding a larger TFT display requires updating the display
> initialisation section at the top of `code.py`. Ask for help with this step if
> needed.

---

## 5. Input Method Options

### Option A — Sip-and-Puff (LPS33HW pressure sensor)

A small barometric pressure sensor detects the tiny pressure change when you
breathe into or out of a short plastic tube. No hand movement required.

**Sensor:** Adafruit LPS33HW Water-Resistant Pressure Sensor — STEMMA QT
https://www.adafruit.com/product/4414

> **Adafruit learn guide — LPS33 sip-and-puff with CircuitPython:**
> https://learn.adafruit.com/st-lps33-and-circuitpython-sip-and-puff
> Recommended reading before your first use. Covers sensor calibration,
> threshold tuning, and breath technique.

**Tube options:**

| Option | ID | OD | Material | Source |
|--------|----|----|----------|--------|
| Adafruit Silicone Tubing #3659 | 2.5 mm | 4.7 mm | Food-safe silicone | https://www.adafruit.com/product/3659 |
| Aquarium airline tubing | 4.8 mm (3/16") | 7.9 mm (5/16") | PVC or silicone | Pet store / hardware store |
| Medical sip-and-puff tubing | 4.8 mm (3/16") | 7.9 mm (5/16") | Medical PVC | Medical supply |

**Adafruit #3659** is the easiest option — sold on the same site as the sensor,
food-safe silicone, fits snugly over the sensor's pressure port. Order at least
30 cm (12 inches); 1 m gives you plenty to cut to length and retry.

**Aquarium airline tubing** is the budget alternative, available at any pet
store for ~$3–5 per metre. The larger outer diameter grips the sensor port
slightly differently — wrap a thin layer of silicone tape around the port nipple
first if the fit feels loose.

Cut to a comfortable length — most users prefer 20–40 cm (8–16 inches).

> The tube pushes over the small nipple on the LPS33HW breakout board. No
> adhesive is needed; friction holds it securely during normal use.

---

### Option B — Accessibility (AT) Switches via TRRS Jack

Standard assistive technology switches with a **3.5 mm mono plug** connect to
the Feather through a TRRS jack breakout. Pressing the dot switch = dot;
pressing the dash switch = dash.

Any AT switch compatible with Ablenet, Inclusive Technology, Specs Switches, or
similar systems will work. One switch (dot only) is enough to navigate slowly;
two switches (dot + dash) are strongly recommended for practical use.

**Two wiring options for the TRRS jack:**

#### Option B1 — Solderless breadboard

A no-soldering build using a half-size breadboard, a single TRRS jack (#1699),
and three jumper wires. Lowest-cost path and reversible, but bulky and best
suited to bench testing rather than long-term use.

**Detailed step-by-step breadboard instructions are in
[Appendix D — Breadboard Wiring Walkthrough](#appendix-d--breadboard-wiring-walkthrough)
at the end of this guide.**

For most builders Option B3 (#2915 Terminal Block) is simpler and tidier — try
that first.

#### Option B2 — Soldered TRRS breakout (compact, durable)

Solders four short wires to an Adafruit TRRS Jack Breakout board.

> **Can I use clips instead of soldering on the #5764?**
>
> | Clip type | On the #5764 | On the Feather | Verdict |
> |-----------|-------------|----------------|---------|
> | IC hooks (dual hook-to-hook) | Flat pads — hooks slip off | Flat pads or header pins | ✗ Not reliable |
> | Alligator clip to female jumper | TRRS jack **legs** (round metal, grippable) — **not** flat pads | Female slides onto Feather header pin directly | ✓ Works if jack legs protrude and Feather has header pins |
> | Alligator clip to female jumper | Flat pads only (no protruding legs) | Any | ✗ Not reliable |
>
> **How to check:** Look at the bottom of the #5764. If the TRRS jack's metal
> legs stick out 1–2 mm below the PCB, alligator clips can grip them. Clip
> one jaw onto each leg — T, R1, S — and plug the female end directly onto
> the matching Feather header pin. No male-to-male cable needed if the Feather
> has soldered header pins.
>
> Secure the wires with a cable tie or tape so they cannot be tugged loose
> during use.
>
> **If the Feather has no header pins** the chain becomes alligator→female→
> male-to-male→alligator→Feather pad, which adds two extra connection points
> and is too unreliable for daily use.
>
> **For guaranteed no-solder reliability** use **Option B1** with two #1699
> jacks — each switch gets its own dedicated jack, no clips, no Y-splitter.

Parts needed:
- Adafruit TRRS Jack Breakout #5764 https://www.adafruit.com/product/5764
- 4 short wires ~8 cm (different colours help)
- Soldering iron + solder

| TRRS pad | Feather pin | Wire colour suggestion |
|----------|-------------|----------------------|
| T (Tip) | D5 | Red |
| R1 (Ring 1) | D6 | Blue |
| S (Sleeve) | GND | Black |
| R2 | Not used | — |

> **Both switch options work with the same `code.py`** — set `USE_SENSOR = False`
> in the configuration section.

---

#### Option B3 — #2915 TRRS Terminal Block (no breadboard, minimal soldering) ⭐ Recommended for #5691

**Adafruit #2915 — $2.50**
https://www.adafruit.com/product/2915

A 3.5 mm TRRS jack with **built-in screw terminals** — no PCB, no soldering on the jack side at all. Strip a wire, insert it, tighten the screw with a small screwdriver. This is the best option for the #5691 Reverse TFT Feather because it avoids the breadboard entirely and does not require the #2926 Terminal Block FeatherWing (which is incompatible with the Reverse TFT Feather).

| #2915 terminal | Feather pin | Function |
|----------------|-------------|----------|
| Tip | D5 | Dot switch |
| Ring | D6 | Dash switch |
| Sleeve | GND | Ground |
| Ring 2 | — | Leave empty |

**If your #5691 has header pins soldered** — use female-to-female jumper wires. One end screws into the #2915 terminal; the other end plugs directly onto the Feather pin. **Zero soldering.**

**If your #5691 has no header pins** — solder the three wires directly to the D5, D6, and GND pads on the Feather. The jack side still needs no soldering. Only 3 solder joints total.

Parts needed:

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | TRRS Jack Terminal Block | #2915 | https://www.adafruit.com/product/2915 |
| 3 | Female-to-female jumper wires (if Feather has pins) | #266 | https://www.adafruit.com/product/266 |
| — | *or* 3 short wires ~15 cm + soldering iron (if no header pins) | — | — |

> **Note:** The #2915 accepts both mono and TRRS plugs. Most AT switches use
> a 3.5 mm mono plug (tip + sleeve only), which connects the Tip and Sleeve
> terminals when pressed — exactly what AeroMorse expects.

---

## 6. Speaker Options

The speaker gives audio feedback — a tone for every dot and dash, and a
different tone when a pattern fires. It is optional but strongly recommended:
hearing the rhythm helps with timing.

> **All speaker options connect to the same three Feather signals: A0
> (audio), 3V (power — S1/S3 only), and GND.** If your Feather has header
> pins they plug in via breadboard or jumper wires. If your Feather has bare
> PCB pads, the speaker wires are soldered directly to those pads. See
> §8D for the full wiring procedure including the no-headers path.

### Option S1 — STEMMA Speaker (easiest) ⭐ Recommended

**Adafruit STEMMA Speaker #3885**
https://www.adafruit.com/product/3885

- 1.2 W built-in amplifier, 8 Ω driver, JST PH 3-pin connector
- Comes with a 200 mm cable that plugs in directly — no soldering
- Powered from the Feather's 3.3 V or 5 V pin
- Loud enough to hear across a quiet room

Wiring (cable already attached):

| Speaker cable pin | Feather pin |
|-------------------|-------------|
| GND | GND |
| Audio | A0 |
| VIN | 3V (or 5V) |

---

### Option S2 — Passive piezo buzzer (simplest, quietest)

A passive piezo connected between **A0** and **GND**. No amplifier, no extra
parts. The tone is quieter than Option S1 but audible in a quiet room.

> **Important:** Buy a *passive* piezo, not an *active* one. An active buzzer
> has a built-in oscillator and will only click, not produce a tone.
> The two options below are confirmed passive and work directly from the
> Feather's A0 pin.

- **Small Enclosed Piezo with Leads #1740** — $0.95
  https://www.adafruit.com/product/1740
  Compact, pre-wired leads, good for breadboard or tucking inside an enclosure.

- **Large Enclosed Piezo with Leads #1739** — $0.95
  https://www.adafruit.com/product/1739
  Same price, slightly larger housing, a little louder.

Connect: red/+ lead → A0, black/− lead → GND. No resistor needed.

---

### Option S3 — Small speaker + separate amplifier board

For louder output or a specific speaker size:

- **Adafruit Mono 2.5 W Class D Amplifier PAM8302 #2130**
  https://www.adafruit.com/product/2130
- Any small 4 Ω or 8 Ω speaker (3 W or less)
- Amplifier A+ → A0, A− → GND, VIN → 3V, GND → GND
- Speaker connects to the amplifier output terminals

---

## 7. Complete Parts Lists

Pick one item from each section. Everything in **Core hardware** is always
required.

---

### Core hardware (always required)

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | Feather microcontroller (see Section 3) | #5477 recommended | https://www.adafruit.com/product/5477 |
| 1 | USB-C cable — **data + power** (not charge-only) | any | — |

> To confirm a USB cable transfers data: plug it in; if a drive appears on your
> computer, it is a data cable. Charge-only cables show nothing.

---

### Input method — choose ONE

#### Sip-and-Puff sensor parts

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | LPS33HW Water-Resistant Pressure Sensor — STEMMA QT | #4414 | https://www.adafruit.com/product/4414 |
| 1 | STEMMA QT 4-pin cable 100 mm | #4210 | https://www.adafruit.com/product/4210 |
| 1 m | Silicone Tubing — 2.5 mm ID, 4.7 mm OD (recommended) | #3659 | https://www.adafruit.com/product/3659 |
| — | *or* Aquarium airline tubing — 3/16" ID, 5/16" OD | — | pet store / hardware store |

#### AT switch — solderless breadboard

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | Half-Size Breadboard | #64 | https://www.adafruit.com/product/64 |
| 1 | Breadboard-Friendly 3.5 mm Stereo Jack | #1699 | https://www.adafruit.com/product/1699 |
| 3 | Short male-to-male jumper wires | — | — |

**Alternative — two jacks, no Y-splitter:**
Instead of one jack + a Y-splitter, you can use **two #1699 jacks** — one per
switch. Each switch plugs directly into its own dedicated jack. This is
slightly simpler to wire and removes the Y-splitter from the parts list.

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | Half-Size Breadboard | #64 | https://www.adafruit.com/product/64 |
| **2** | Breadboard-Friendly 3.5 mm Stereo Jack | #1699 | https://www.adafruit.com/product/1699 |
| 4 | Short male-to-male jumper wires | — | — |

Wiring with two jacks:

| Jack | Leg | Feather pin |
|------|-----|-------------|
| Jack 1 (dot switch) | TIP | D5 |
| Jack 1 (dot switch) | SLEEVE | GND |
| Jack 2 (dash switch) | TIP | D6 |
| Jack 2 (dash switch) | SLEEVE | GND |

The RING leg on each jack is left unconnected. Both SLEEVE legs can share the
same GND pin on the Feather, or use two separate GND holes (the Feather has
several GND pins — any of them work).

#### AT switch — soldered TRRS breakout

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | TRRS Jack Breakout Board | #5764 | https://www.adafruit.com/product/5764 |
| 4 | Short wires ~8 cm | — | — |

#### AT switch — #2915 TRRS Terminal Block (no breadboard) ⭐ Recommended for #5691

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | TRRS Jack Terminal Block | #2915 | https://www.adafruit.com/product/2915 |
| 3 | Female-to-female jumper wires (if Feather has header pins) | #266 | https://www.adafruit.com/product/266 |
| — | *or* 3 short wires ~15 cm + soldering iron (if no header pins) | — | — |

---

### Display — choose ONE

> **If you chose the #5691 Reverse TFT Feather, skip this section entirely —
> the display is already part of that board.**

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | 3.5" TFT FeatherWing Resistive (recommended for table) | #3651 | https://www.adafruit.com/product/3651 |
| — | *or* 3.5" TFT FeatherWing Capacitive | #5872 | https://www.adafruit.com/product/5872 |
| — | *or* 2.4" TFT FeatherWing Resistive | #3315 | https://www.adafruit.com/product/3315 |
| — | *or* 3.5" TFT Breakout (standalone, needs 5 wires) | #2050 | https://www.adafruit.com/product/2050 |
| — | *or* 2.8" TFT Breakout (standalone) | #1770 | https://www.adafruit.com/product/1770 |
| — | *or* 1.3" OLED — STEMMA QT (larger OLED, no code change) | #938 | https://www.adafruit.com/product/938 |
| — | *or* 0.96" OLED — STEMMA QT (v2 code default, compact) | #326 | https://www.adafruit.com/product/326 |

**If you choose the OLED #326**, you also need:

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | STEMMA QT 4-pin cable 400 mm | #5385 | https://www.adafruit.com/product/5385 |

**If you chose the #5613 EYESPI Feather**, pick ONE EYESPI display and ONE
EYESPI cable:

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | 2.0" 320×240 IPS TFT EYESPI ⭐ recommended | #5800 | https://www.adafruit.com/product/5800 |
| — | *or* 1.3" 240×240 IPS TFT EYESPI | #5393 | https://www.adafruit.com/product/5393 |
| — | *or* 1.14" 240×135 IPS TFT EYESPI | #5394 | https://www.adafruit.com/product/5394 |
| — | *or* 1.54" 240×240 round IPS TFT EYESPI | #5610 | https://www.adafruit.com/product/5610 |
| — | *or* 1.5" 128×128 colour OLED EYESPI | #5398 | https://www.adafruit.com/product/5398 |
| 1 | EYESPI Cable 100 mm (typical) | #5240 | https://www.adafruit.com/product/5240 |
| — | *or* EYESPI Cable 50 mm (display close to Feather) | #5239 | https://www.adafruit.com/product/5239 |
| — | *or* EYESPI Cable 200 mm (display on a separate arm) | #5241 | https://www.adafruit.com/product/5241 |

---

### Wireless display — choose ONE (optional, for remote viewing)

> **Skip this section if you will view the display on the main board.**
> Only needed when the sensor is mounted out of sight and you need a
> separate display in front of you.

#### Option W1 — Second Reverse TFT Feather (recommended)

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | ESP32-S3 Reverse TFT Feather | #5691 | https://www.adafruit.com/product/5691 |
| 1 | USB-C cable + power bank or charger | — | Powers the display board (if not using a battery) |

**Optional — run the receiver completely wireless (choose one battery):**

| Qty | Item | Adafruit # | Est. runtime | URL |
|-----|------|-----------|-------------|-----|
| 1 | LiPoly Battery 400 mAh — slim flat pack | #3898 | ~3–5 hrs | https://www.adafruit.com/product/3898 |
| — | *or* LiPoly Battery 500 mAh | #1578 | ~4–6 hrs | https://www.adafruit.com/product/1578 |
| — | *or* LiPoly Battery 1200 mAh | #258 | ~9–14 hrs | https://www.adafruit.com/product/258 |

#### Option W2 — XIAO ESP32C3 + OLED (budget)

| Qty | Item | Source | Approx. price |
|-----|------|--------|--------------|
| 1 | Seeed XIAO ESP32C3 | DigiKey / Amazon | $5–7 |
| 1 | SSD1306 128×64 I2C OLED (4-pin header) | Amazon | $3–5 |
| 4 | Short wires ~8 cm | — | — |

---

### Speaker — choose ONE (optional but recommended)

| Qty | Item | Adafruit # | URL |
|-----|------|-----------|-----|
| 1 | STEMMA Speaker | #3885 | https://www.adafruit.com/product/3885 |
| — | *or* STEMMA JST PH 3-pin cable (if speaker came without) | #3893 | https://www.adafruit.com/product/3893 |
| — | *or* Small Enclosed Piezo with Leads (passive) | #1740 | https://www.adafruit.com/product/1740 |
| — | *or* Large Enclosed Piezo with Leads (passive, louder) | #1739 | https://www.adafruit.com/product/1739 |
| — | *or* PAM8302 Amplifier + small 8 Ω speaker | #2130 | https://www.adafruit.com/product/2130 |

---

### Tools

#### Software tools (always needed — free)

| Tool | Purpose | Download |
|------|---------|---------|
| **Thonny** | Edit `code.py`, view serial output, REPL | https://thonny.org |
| **Any text editor** | Edit `code.py` and `morse_map.py` | Notepad (Windows), TextEdit (Mac) |

**Thonny** is the recommended editor for CircuitPython beginners. It shows the
serial console (error messages and `print()` output) in the same window as the
code editor, has a built-in file manager for the CIRCUITPY drive, and runs on
Windows, macOS, and Linux at no cost.

> Mu Editor was previously recommended by Adafruit but has announced
> end-of-life in 2026. Thonny is the current recommended alternative.

---

#### Hardware tools — solderless build (Option B1 breadboard)

**If your Feather already has header pins soldered:** No special tools needed —
the pins press straight into the breadboard.

**If your Feather has no header pins (bare holes):** You have three options:

| Option | What to do | Cost |
|--------|-----------|------|
| **Test hook clips** | Clip onto the copper pads on the back of the Feather — one clip per pin you need (only 3 for AT switch mode: D5, D6, GND). The male pin end goes into the breadboard. The Goupchn clips you found work for this. | Clips you already have |
| **Get headers soldered** | Take the Feather and the included loose header strip to a local makerspace, library maker lab, or electronics repair shop — most will solder headers for free or a few dollars. This is the most reliable long-term solution. | Free–$5 |
| **Order with headers pre-installed** | Adafruit sells some Feather boards with headers already soldered. When reordering, look for the listing that says "with headers" in the title. | Same price as bare board |

For AT switch mode with test hook clips, you only ever need 3 clips (D5, D6, GND).
The Feather sits on the table face-down; clip onto the copper ring around each
pin hole on the back; the male pin end of each clip goes into the breadboard
hole next to the jack leg it connects to. USB power still comes from the cable.

---

#### Hardware tools — soldered build (Option B2 TRRS breakout, or soldering headers)

| Tool | Notes | Adafruit # | URL |
|------|-------|-----------|-----|
| Soldering iron — 40–60 W adjustable | Temperature-controlled irons are easier for beginners | #3685 | https://www.adafruit.com/product/3685 |
| Solder — 60/40 rosin-core 0.3 mm | Standard electronics solder; the thin gauge is easier for small pads | #145 | https://www.adafruit.com/product/145 |
| Flush cutters | For trimming wire leads flush after soldering | #152 | https://www.adafruit.com/product/152 |
| Helping hands | Holds small parts steady while soldering | #291 | https://www.adafruit.com/product/291 |
| Wire strippers | For stripping insulation from wire ends | any | hardware store |

> **New to soldering?** Adafruit has a free beginner's guide:
> https://learn.adafruit.com/adafruit-guide-excellent-soldering

---

#### Useful for any build (optional but handy)

| Tool | Purpose | Notes |
|------|---------|-------|
| Digital multimeter | Test switch continuity, check wiring | Any basic model; ~$10–20 at hardware stores |
| Small scissors | Cut sip-and-puff tubing to length | Any pair |
| Silicone tape | Seal tube to sensor if fit is loose | Hardware store; stretchy self-fusing tape |
| Velcro strips | Mount display or sensor to a surface | Any brand |

---

## 8. Step-by-Step Assembly

### Before you start

Lay out all your parts. Do not plug anything in yet.

The Feather's header pins must be soldered before use if your board came
without headers. If your board has header pins already attached, skip this note.
Soldering only the headers is straightforward and many local makerspaces or
electronics shops will do this for free if you ask.

---

### Step 8A — Connect the display

#### If you chose a FeatherWing display (#3651, #5872, or #3315)

1. Hold the FeatherWing above the Feather with the display facing up.
2. Line up the two rows of holes on the FeatherWing with the two rows of header
   pins on the Feather.
3. Press firmly and evenly downward until the FeatherWing sits flush on the
   Feather. The pins should click through all the way.

That is all — no wires needed.

#### If you chose the OLED #326

1. Plug one end of the **100 mm STEMMA QT cable** into the STEMMA QT port on
   the Feather. The connector is keyed and only fits one way — do not force it.
2. Plug the other end into either STEMMA QT port on the **LPS33HW sensor**.
3. Plug one end of the **400 mm STEMMA QT cable** into the remaining port on the
   LPS33HW.
4. Plug the other end into the STEMMA QT port on the **OLED** (#326).

Chain: **Feather → 100 mm cable → LPS33HW → 400 mm cable → OLED**

#### If you chose a standalone TFT breakout (#2050, #1770, etc.)

You need 5 short wires. Solder or use header connectors:

| Display pin | Feather pin |
|-------------|-------------|
| SCK | SCK |
| MOSI (or SI) | MOSI |
| CS | D9 |
| DC | D10 |
| RST | D11 |
| GND | GND |
| VIN | 3V |

> Pin labels vary slightly between breakout boards. Match by function name, not
> physical position. Refer to the Adafruit product guide for your specific board.

#### If you chose the #5613 EYESPI Feather + EYESPI display

This is the simplest non-built-in path — no wires, no soldering.

1. Locate the **18-pin EYESPI connector** on the Feather (#5613). It is the
   small black ribbon-cable socket near the edge of the board.
2. Flip up the small black tab on the connector — it pivots ~90° away from the
   board to unlock the socket.
3. Slide one end of the **EYESPI flex cable** into the socket with the gold
   contacts facing **down** (toward the board). The cable goes in about
   2 mm — stop when it sits naturally; do not force.
4. Press the black tab back down flat to lock the cable in place.
5. Repeat steps 2–4 on the **display board's** EYESPI connector with the other
   end of the cable.
6. **Check the cable orientation:** both ends must have the gold contacts
   facing the same way relative to the board. If colours appear inverted or
   the screen stays dark after power-on, the cable is in backwards on one end —
   unlock, flip, relock.

That is all — power, ground, and all SPI signals run through the single flex
cable.

> The EYESPI connector is fragile. Do not pull the cable while the tab is
> locked, and do not flex the cable sharply at the connector.

---

### Step 8B — Connect the pressure sensor (sip-and-puff only)

If you are using AT switches instead, skip this step.

**If you also have the OLED** the sensor is already in the STEMMA QT chain from
Step 8A. No extra wiring needed.

**If you are using a TFT FeatherWing or standalone TFT** (no OLED in the chain):

1. Plug the **100 mm STEMMA QT cable** into the Feather's STEMMA QT port.
2. Plug the other end into either port on the **LPS33HW sensor**.

The sensor I²C address is 0x5C — it will not conflict with any display.

**Attach the sip-and-puff tube:**

Push one end of the aquarium airline tubing over the small raised nipple on the
top of the LPS33HW board. The fit should be snug. Cut the other end at a
comfortable length and place it where you can sip and puff into it naturally.

---

### Step 8C — Connect the AT switches (switch mode only)

If you are using the sip-and-puff sensor instead, skip this step.

#### Option B1 — Breadboard

See [Appendix D — Breadboard Wiring Walkthrough](#appendix-d--breadboard-wiring-walkthrough)
for the full step-by-step procedure with diagrams.

#### Option B2 — TRRS breakout (soldered)

1. Solder a short wire to each pad: T (red), R1 (blue), S (black). Leave R2
   bare.
2. Connect the other ends:

| Wire colour | Feather pin |
|-------------|-------------|
| Red (T) | D5 |
| Blue (R1) | D6 |
| Black (S) | GND |

3. Plug AT switches directly into the TRRS jack:
   - Dot switch: tip-to-sleeve connection = D5 goes low = dot
   - Dash switch: ring1-to-sleeve connection = D6 goes low = dash

#### Option B3 — #2915 TRRS Terminal Block

**If your #5691 has header pins (no soldering at all):**

1. Cut 3 female-to-female jumper wires to a comfortable length (~15 cm).
2. On the #2915, loosen the Tip, Ring, and Sleeve screws with a small
   flathead screwdriver.
3. Insert one wire end into each terminal and tighten the screw firmly.
4. Plug the other (female) ends directly onto the Feather header pins:
   - Tip wire → D5
   - Ring wire → D6
   - Sleeve wire → GND
5. Plug AT switches into the #2915 jack.

**If your #5691 has no header pins (3 solder joints):**

1. Cut 3 short wires (~15 cm), strip both ends.
2. Screw one end of each wire into the Tip, Ring, and Sleeve terminals on
   the #2915.
3. Solder the other ends directly to the D5, D6, and GND pads on the
   Feather.
4. Plug AT switches into the #2915 jack.

---

### Step 8D — Connect the speaker

All three speaker options end at the same three Feather signals: **A0**
(audio), **3V** (power, only for S1 and S3), and **GND**. How those three
signals are connected depends entirely on whether your Feather has header
pins.

#### If your Feather has header pins (or sits in a breadboard)

**STEMMA Speaker #3885** — the cable ends in three male header pins. Push
them into the breadboard rows that line up with A0, 3V, and GND on the
Feather. With a FeatherWing stack instead of a breadboard, use three short
female-to-female jumper wires from the FeatherWing's bottom pins to the
speaker cable.

| Speaker cable wire | Feather pin |
|-------------------|-------------|
| Black (GND) | GND |
| White (Audio) | A0 |
| Red (VIN) | 3V |

**Passive piezo (#1740 / #1739)** — push the two bare wire ends into the
breadboard rows for A0 and GND. Red/+ → A0, Black/− → GND. No resistor.

**PAM8302 amplifier (#2130) + speaker** — same pin mapping as the STEMMA
Speaker (A0, 3V, GND), but soldered to the amp's A+ / VIN / GND pads first.
Speaker connects to the amp's two output terminals (polarity not critical).

#### If your Feather has no header pins (bare PCB pads)

The male pins on the STEMMA Speaker cable have nothing to plug into. You
have two practical paths — pick one. Both require a small soldering job
**on the Feather**, but neither is harder than soldering header pins.

**Path 1 — Solder the speaker wires directly to the Feather (recommended)**

Cleanest, lowest profile, and the most permanent.

1. Identify the **A0**, **3V**, and **GND** pads on the Feather (printed on
   the underside).
2. Cut the JST PH connector off the speaker end of the #3885 cable so you
   have ~15 cm of three coloured wires. (For the piezo, the leads are
   already bare; for the PAM8302, solder the wires to the amp first.)
3. Strip ~3 mm of insulation from each free wire end.
4. Tin each wire end and each Feather pad with a touch of solder.
5. Press each tinned wire onto its matching pad and reflow with the iron:
   - Black (GND) → GND pad
   - White / Audio → A0 pad
   - Red (VIN) → 3V pad   *(#3885 and PAM8302 only — piezo skips this)*
6. Tug each wire gently to confirm it is fixed.

> A 30 W iron, 0.5 mm solder, and a steady hand are plenty. The pads are
> larger and more forgiving than header-pin holes.

**Path 2 — Solder header pins to the Feather first**

Use this path if you also want headers for the AT switch jumper wires, or
to make the speaker removable later.

1. Solder header pins onto the Feather's A0, 3V, and GND positions only —
   you don't need a full row of pins, just the three the speaker needs.
2. Then follow the "header pins" instructions above:
   - #3885 STEMMA Speaker — male pins plug into a breadboard, or use three
     female-to-female jumpers from the speaker cable to the Feather pins.
   - Piezo — solder the bare leads to two female jumper wires (or solder
     to short pin headers), then plug onto A0 and GND.
   - PAM8302 — wire the amp board to A0 / 3V / GND via female jumpers.

> A local makerspace, library maker lab, or electronics repair shop will
> usually solder a few pins for free or a few dollars. See §8 "Before you
> start" for more on getting headers done if you don't own an iron.

**Path 3 — Skip the speaker entirely**

The speaker is optional. The OLED / TFT display already shows every dot,
dash, group, and last action — many users do not miss the audio at all.
Set up the rest of the device first; add the speaker later if you decide
you want it.

#### Quick reference — all paths, all options

| Feather has headers? | #3885 STEMMA Speaker | Piezo #1740/#1739 | PAM8302 + speaker |
|---|---|---|---|
| **Yes (breadboard)** | Push 3 male pins into breadboard rows for A0/3V/GND | Push 2 bare leads into A0 + GND rows | Wire amp to A0/3V/GND via breadboard |
| **Yes (FeatherWing only)** | 3 F-F jumpers from FeatherWing pins to speaker cable | Solder leads to F-F jumper, plug onto A0+GND | Wire amp via F-F jumpers |
| **No (bare pads)** | Cut connector off, solder 3 wires to A0/3V/GND pads | Solder 2 leads to A0+GND pads | Solder amp board to A0/3V/GND pads |

---

### Step 8E — Set up the wireless display board (optional)

Skip this step if you are not using a wireless display.

#### Option W1 — Second Reverse TFT Feather

No hardware assembly needed. Simply:

1. Flash the latest stable CircuitPython onto the second Feather (same procedure
   as Step 9.1 below).
2. Copy the files listed under **Option W1** in Section 4 (receiver.py → code.py,
   receiver_boot.py → boot.py, morse_map.py, and your /lib folder).
3. Power the second board from any USB-C phone charger or USB power bank.

Mount the second Feather face-up where you can see the TFT. It starts
displaying within one second of the main board powering on.

#### Option W2 — XIAO ESP32C3 + OLED

1. Solder four short wires between the XIAO and the OLED 4-pin header:

   | OLED pin | XIAO pin |
   |----------|---------|
   | VCC | 3V3 |
   | GND | GND |
   | SCL | D3 (SCL) |
   | SDA | D2 (SDA) |

2. Flash the latest stable CircuitPython onto the XIAO (see circuitpython.org/downloads,
   search "XIAO ESP32C3").
3. Make the one-line code change described in Section 4 (Option W2).
4. Copy `receiver.py` as `code.py`, `receiver_boot.py` as `boot.py`, and the
   two library files listed in Section 4 into `/lib`.
5. Power the XIAO from any USB-C power source.

---

## 9. Software Installation

### Step 9.1 — Install CircuitPython on the Feather

1. Go to **https://circuitpython.org/downloads**
2. Search for your Feather board name (e.g. "ESP32-S3 Feather").
3. Download the latest **stable** `.uf2` file (not a pre-release).
4. Plug the Feather into your computer with the USB-C **data** cable.
5. **Double-tap** the small Reset button on the Feather quickly (two taps within
   about half a second).
   - The NeoPixel LED on the Feather turns **green**.
   - A drive named **FTHRS3BOOT** (or similar) appears on your computer.
6. Drag the `.uf2` file you downloaded onto that drive.
7. The Feather reboots automatically. After a few seconds a drive named
   **CIRCUITPY** appears. Done.

> If **CIRCUITPY** already appears when you plug in (without double-tapping),
> CircuitPython is already installed — skip straight to Step 9.2.

> If you see **FTHRS3BOOT** (or similar) every time you plug in without
> double-tapping, the Feather has no code loaded — this is normal, continue
> with Step 9.2.

---

### Step 9.2 — Install the required libraries

1. Go to **https://circuitpython.org/libraries**
2. Download the **Bundle** that matches your CircuitPython version.
   - To find your version: look at the file `boot_out.txt` on the CIRCUITPY
     drive. It will say something like `Adafruit CircuitPython 10.2.0` —
     download the bundle that matches your major version number (9.x or 10.x).
3. Open the downloaded `.zip` file. Inside is a folder called `lib`.
4. On the **CIRCUITPY** drive, open (or create) the `lib` folder.
5. Copy these items from the bundle's `lib` folder into CIRCUITPY's `lib` folder:

**Always copy these (all builds):**

```
adafruit_hid/                 ← entire folder
adafruit_bus_device/          ← entire folder
adafruit_register/            ← entire folder
neopixel.mpy
```

**Copy these if using the sip-and-puff sensor:**

```
adafruit_lps35hw.mpy
```

**Copy these for your chosen display:**

| Display | Files to copy |
|---------|--------------|
| OLED #326 or #938 | `adafruit_displayio_ssd1306.mpy` and `adafruit_display_text/` |
| TFT #3651, #5872, #2050 | `adafruit_hx8357.mpy` and `adafruit_display_text/` |
| TFT #3315, #1770, #1743 | `adafruit_ili9341.mpy` and `adafruit_display_text/` |
| TFT #4311 | `adafruit_st7789.mpy` and `adafruit_display_text/` |

> You only need the items listed above — you do not need to copy the entire
> bundle, which is very large.

---

### Step 9.3 — Copy the AeroMorse project files

**Which `code.py` to use depends on your Feather board:**

| Board | Copy `code.py` from |
|-------|-------------------|
| #5483 ESP32-S3 TFT Feather | `v1/` folder — uses built-in display |
| #5691 ESP32-S3 Reverse TFT Feather | `v1/` folder — uses built-in display |
| #5300 ESP32-S2 TFT Feather | `v1/` folder — uses built-in display |
| #5613 ESP32-S3 EYESPI Feather + EYESPI display | `v2/` folder — see EYESPI init below |
| All other boards | `v2/` folder — uses external display |

**EYESPI display init (only for #5613 + EYESPI display):**

The EYESPI displays are SPI displays — `board.DISPLAY` is not auto-populated.
Near the top of `v2/code.py`, replace the existing OLED initialisation block
with the snippet matching your EYESPI display's driver chip:

```python
# Example for #5800 (2.0" 320x240) and #5393 / #5394 — all ST7789
import board, busio, displayio, fourwire
from adafruit_st7789 import ST7789

displayio.release_displays()
spi = busio.SPI(board.SCK, MOSI=board.MOSI)
bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9,
                        reset=board.D11)
display = ST7789(bus, width=320, height=240, rowstart=0, colstart=0)
```

Drivers per display:

| Display | Library file in `lib/` | Driver class |
|---------|----------------------|--------------|
| #5800, #5393, #5394 | `adafruit_st7789.mpy` | `ST7789` |
| #5610 (round) | `adafruit_gc9a01a/` | `GC9A01A` |
| #5398 (OLED) | `adafruit_ssd1351.mpy` | `SSD1351` |

Add the matching driver library to `lib/` from the Adafruit CircuitPython
Bundle (see §9.2).

Copy these three files to the **root** of the CIRCUITPY drive (not inside any
subfolder). Take `code.py` from the correct folder for your board (above), and
`boot.py` and `morse_map.py` from either folder — they are identical:

```
boot.py
code.py
morse_map.py
```

The CIRCUITPY drive should now look like this:

```
CIRCUITPY/
├── boot.py
├── code.py
├── morse_map.py
└── lib/
    ├── adafruit_hid/
    ├── adafruit_bus_device/
    ├── adafruit_register/
    ├── adafruit_lps35hw.mpy       (sensor builds)
    ├── adafruit_displayio_ssd1306.mpy  (OLED builds)
    ├── adafruit_display_text/
    └── neopixel.mpy
```

**Safely eject the CIRCUITPY drive** before unplugging. The Feather reboots and
runs the code automatically.

> The first boot after copying `boot.py` takes a few extra seconds. This is
> normal — the board is negotiating USB HID with the host. If nothing seems to
> happen, unplug and replug the USB cable once.

---

## 10. Configuration

Open `code.py` in any plain-text editor (Notepad, TextEdit, VS Code, or the
Mu Editor). Look for the configuration section near the top of the file.

### Key settings

| Setting | Default | What to change |
|---------|---------|----------------|
| `USE_SENSOR` | `True` | Change to `False` if using AT switches |
| `THRESH_SIP` | `5` | Raise to `8` or `10` if getting false triggers; lower to `3` if light sips are missed |
| `THRESH_PUFF` | `5` | Same as above but for puff/dash |
| `ACCEPT_DELAY` | `0.2` | Raise to `0.3` if patterns commit before you finish |
| `LONG_PRESS` | `1.0` | Hold time in seconds to cycle groups. Raise if accidentally cycling |
| `DISPLAY_ROTATION` | `180` | `0` = USB port on left; `180` = USB port on right |
| `BEEP_DOT_FREQ` | `1200` | Pitch in Hz for dot (sip) beeps — higher pitch |
| `BEEP_DASH_FREQ` | `800` | Pitch in Hz for dash (puff) beeps — lower pitch |

Save the file to the CIRCUITPY drive. The Feather reloads automatically within
a few seconds.

---

## 11. First Power-On Test

1. Plug the Feather into your computer.
2. Wait 3–5 seconds. You should see:
   - The display showing **[Keyboard]**
   - If using the sensor: the message "Calibrating…" in the serial console
   - A short beep from the speaker when calibration finishes (sensor mode only)
3. Open a plain-text editor on your computer (Notepad, TextEdit).
4. Click inside the editor so it is focused.

### Quick test — sensor mode

Gently sip (dot) · pause · gently puff (dash) · pause · puff (dash).
Wait 0.3 seconds. The letter **W** (`.--`) should appear in the text editor and
the speaker should have beeped three times.

### Quick test — switch mode

Press dot switch · dot switch · dash switch (`. . -`). Wait 0.3 seconds. The
letter **U** (`..-`) should appear.

### If nothing appears

- Make sure the text editor window is focused (click in it).
- Unplug and replug the USB cable — the first connection after installing
  `boot.py` sometimes needs a fresh plug.
- In sensor mode: make sure the tube is pushed onto the sensor and you are
  breathing into it, not blowing from the side.
- In switch mode: confirm `USE_SENSOR = False` is set in `code.py`.

---

## 12. Troubleshooting

**Display is blank or white**
- Check that you are running the correct version of `code.py` for your display.
  The v2 code expects the OLED #326 by default. If you have a TFT FeatherWing,
  the display initialisation in `code.py` must be updated.
- For the OLED: check both ends of both STEMMA QT cables are fully clicked in.
- Try changing `device_address=0x3C` to `device_address=0x3D` if the OLED
  stays blank.

**No sound from the STEMMA Speaker**
- Verify wiring: Audio → A0, VIN → 3V, GND → GND.
- Open the serial console in Mu Editor. If you see
  `WARNING: audio modules not available`, your CircuitPython build is missing
  `audiopwmio` — download a standard build (not a minimal one) from
  circuitpython.org/downloads.

**AT switches not registering**
- Confirm `USE_SENSOR = False` in `code.py`.
- Test the switch with a multimeter in continuity mode: pressing the switch
  should beep, confirming Tip connects to Sleeve.
- Confirm D5 (dot) and D6 (dash) wires are connected to the correct jack pins.

**False pressure triggers (random dots/dashes while not sipping or puffing)**
- Raise `THRESH_SIP` and `THRESH_PUFF` to 8 or 10.

**"Calibrating" message hangs at startup**
- The LPS33HW was not found. Check the STEMMA QT cable between the Feather and
  the sensor — both connectors must click in firmly.

**Pattern fires too early (cuts off long patterns)**
- Raise `ACCEPT_DELAY` from `0.2` to `0.3` or `0.4`.

**Groups cycle when you did not mean to**
- Raise `LONG_PRESS` from `1.0` to `1.5` or `2.0` to require a longer hold.

**Wireless display shows "No signal"**
- Confirm both boards are powered and running CircuitPython 9.x or later.
- Both boards must be on the same ESP-NOW channel. If neither is connected to
  WiFi, both default to channel 1 automatically — no action needed.
- Check the serial console on the main board. It should print
  `ESP-NOW: wireless display active (broadcast)` at startup. If it prints
  `ESP-NOW: disabled` the `espnow` module is not present — confirm the board
  is an ESP32-S3 and running CircuitPython 9.x or later.
- Range is approximately 30 m indoors. Move the boards closer to test.

**Wireless display is frozen / not updating**
- The receiver updates whenever a packet arrives (10× per second). If the
  display updates briefly then freezes, the main board may have restarted.
  Check the main board's serial console for errors.

**Main board serial console shows `ESP-NOW: init failed`**
- The `wifi` module initialisation failed. Try power-cycling the main board.
  Rarely, the WiFi radio needs a cold boot (unplug power completely rather
  than pressing Reset).

**Wireless display acts as a second keyboard on Windows**
- The `receiver_boot.py` file was not copied as `boot.py` on the second board,
  or the original `boot.py` (which enables USB HID) is still on the second board.
  Replace `boot.py` on the second board with the contents of `receiver_boot.py`.

**Option W2 OLED stays blank**
- Check all four wires are connected to the correct pins on both the XIAO and
  the OLED.
- Try changing the I2C address in `receiver.py`: look for `device_address=0x3C`
  and change it to `device_address=0x3D`. Some OLEDs use 0x3D.
- Confirm `adafruit_displayio_ssd1306.mpy` and `adafruit_display_text/` are in
  the `/lib` folder on the XIAO.

**REPL shows `ImportError`**
- A library file is missing from `lib/`. Re-read Step 9.2 and copy the missing
  file from the CircuitPython bundle.

**Nothing happens on the computer at all**
- Unplug and replug the USB cable.
- Confirm the cable is a data cable (a drive should appear when plugged in).
- Confirm `boot.py` is on the root of the CIRCUITPY drive.

---

## Appendix A — Groups and Group Cycling

AeroMorse has four groups. Group 0 is always available in the background (its
8-symbol patterns work in any group). Groups 1–3 cycle with long-press:

| Group | Contents | How to reach |
|-------|---------|-------------|
| 0 | Emergency group-jump patterns (8 symbols) | Always active |
| 1 | Letters, numbers, punctuation, function keys | Power-on default |
| 2 | Mouse movement, clicks, Windows shortcuts | Long-puff from Group 1 |
| 3 | Macro text strings | Long-puff from Group 2 |

**Long sip** (hold ≥ `LONG_PRESS` seconds) → cycle backward (3→2→1→3…)
**Long puff** (hold ≥ `LONG_PRESS` seconds) → cycle forward (1→2→3→1…)

---

## Appendix B — Display Layout

```
┌──────────────────────┐
│ [Keyboard]           │  ← active group name
│ . - . .              │  ← Morse pattern building up
│ "n"                  │  ← last character or action
│ Ctrl                 │  ← armed modifier / status
│▓▓▓▓▓░░░░░░░░░░░░░░░░│  ← pressure bar (sensor mode only)
└──────────────────────┘
```

Status line shows: **Ctrl / Shift / Alt / GUI** (sticky modifier armed),
**SLOW / FAST / DRAG / RPT** (mouse state).

---

## Appendix C — Customising Macros

Open `morse_map.py`. Find Group 3 near the bottom. Replace the empty strings
with your own phrases:

```python
g3[3][0b100]  = 'Jane Smith'      # -..   same pattern as letter D
g3[4][0b0010] = 'Thank you!'      # ..-.  same pattern as letter F
g3[3][0b010]  = 'Best regards,'   # .-.   same pattern as letter R
```

Save the file — the Feather reloads automatically.

---

## Appendix D — Breadboard Wiring Walkthrough

Detailed step-by-step instructions for **§5 Option B1 — Solderless breadboard**.
Skip this appendix if you chose Option B2 (TRRS breakout) or Option B3 (#2915
Terminal Block).

### Parts — exactly what to buy

| Qty | Item | URL | Notes |
|-----|------|-----|-------|
| 1 | Half-Size Breadboard | https://www.adafruit.com/product/64 | Any equivalent generic breadboard also works |
| 1 | Breadboard-Friendly 3.5 mm Stereo Jack | https://www.adafruit.com/product/1699 | **1 jack only** — the stereo jack handles both switches |
| 1 pack | Male-to-male jumper wires | https://www.adafruit.com/product/153 | You will use 3 of them |
| 1 | 3.5 mm mono Y-splitter | any store | Needed only if you use 2 switches |

No soldering iron. No solder. No stripped wires. All connections are push-in.

### Understanding the breadboard

A breadboard is a plastic block full of small holes. Metal clips inside connect
certain holes together so you can make circuits by pushing wires into holes
instead of soldering.

```
   ← column numbers →
    1  2  3  4  5  6  7  8  9 ...
a  [ ][ ][ ][ ][ ][ ][ ][ ][ ]
b  [ ][ ][ ][ ][ ][ ][ ][ ][ ]   ← holes a–e in the SAME column
c  [ ][ ][ ][ ][ ][ ][ ][ ][ ]      are all connected to each other
d  [ ][ ][ ][ ][ ][ ][ ][ ][ ]      (5 holes share one clip inside)
e  [ ][ ][ ][ ][ ][ ][ ][ ][ ]
   ─────────────────────────── ← CENTER GAP (nothing crosses here)
f  [ ][ ][ ][ ][ ][ ][ ][ ][ ]   ← holes f–j in the SAME column
g  [ ][ ][ ][ ][ ][ ][ ][ ][ ]      are connected to each other
h  [ ][ ][ ][ ][ ][ ][ ][ ][ ]      (separate from the a–e group)
i  [ ][ ][ ][ ][ ][ ][ ][ ][ ]
j  [ ][ ][ ][ ][ ][ ][ ][ ][ ]
```

**Key rule:** Holes sharing the same column number AND same side (a–e, or f–j)
are connected. Push a wire into column 5 row c and a pin into column 5 row e —
they are now electrically connected without any other wire needed.

The center gap is a physical break — nothing crosses it automatically. That is
where the Feather board will sit, bridging the two sides.

### Step 1 — Place the Feather in the breadboard

The Feather is a long narrow board with a row of pins along each long edge.
Press it firmly into the breadboard so it sits across the center gap like a
bridge. One row of pins will be in the **e** row, the other in the **f** row.

```
        USB-C port
           ↑
  ┌────────────────────┐
  │                    │
e ●  ●  ●  ●  ●  ●  ●  ●   ← left-edge pins press into row e
  ════ FEATHER BOARD ══════
f ●  ●  ●  ●  ●  ●  ●  ●   ← right-edge pins press into row f
  │                    │
  └────────────────────┘
```

The board should sit level and firm. Every pin in row e now has 4 open holes
(a, b, c, d in the same column) you can use to connect to it. Same for row f.

**Finding pin D5, D6, and GND on the Feather:**
Pin names are printed on the *underside* of the Feather board. Before pressing
it into the breadboard, flip it over and look. You will see small text next to
each pad. On the #5691, D5 and D6 are on the right-side column of pins; GND
appears on both sides. Make a small note of which column numbers they land in
once the board is inserted.

> **Tip:** Photograph the underside before inserting so you can refer back to
> the pin names while looking at the top.

### Step 2 — Place the 3.5 mm stereo jack (#1699)

The jack has 4 short metal legs underneath it. Press it into an empty area of
the breadboard, several columns away from the Feather so there is room to work.
Each leg goes into a different row.

```
  jack  ┌──────┐
        │ [  ] │  ← socket hole (where the switch plug goes)
        └──┬┬┬┬┘
    legs:  TI RI SL (4th leg — not used)
           P  N  EE
           │  G  VE
```

The three legs you will use are labelled on the jack's product page:
- **TIP** — dot switch (switch 1)
- **RING** — dash switch (switch 2)
- **SLEEVE** — ground (common return for both switches)

Because each leg is in its own row, you have 4 open holes in that row to
connect to.

### Step 3 — Connect with jumper wires

The jumper wires from Adafruit #153 have a male pin on each end that pushes
into a breadboard hole. You are going to connect three pairs of holes:

| From (jack side) | To (Feather side) |
|-----------------|------------------|
| Any open hole in the TIP leg's row | Any open hole in D5's column, row a–d |
| Any open hole in the RING leg's row | Any open hole in D6's column, row a–d |
| Any open hole in the SLEEVE leg's row | Any open hole in GND's column, row a–d |

Push one end of a jumper wire into the jack's TIP row, and the other end into
D5's column. The wire can be any length — just pick one short enough to lie
flat without flopping around. Repeat for RING→D6 and SLEEVE→GND.

```
Example layout (column numbers illustrative):

col:  5   6   7  ...  18  19  20
a    [ ] [ ] [ ]      [ ] [ ] [ ]
b    [ ] [ ] [ ]      [ ] [ ] [ ]
c    [J] [J] [J]      [ ] [ ] [ ]   ← jack legs in cols 5, 6, 7 at row c
d    [─────────────────────] [ ]   ← jumper wires run across
e    [D5][D6][GN]     [ ] [ ] [ ]  ← Feather pins in same cols at row e
     ════════════ GAP ════════════
f    [D5][D6][GN]     [ ] [ ] [ ]  ← (Feather right-edge, mirror of above)
```

The exact column numbers do not matter — what matters is:
- The jack leg and the Feather pin you want to connect are at **opposite ends
  of the same jumper wire**
- No two wires accidentally share a hole

### Step 4 — Connect your AT switches

You need **one Y-splitter** (3.5 mm mono-to-stereo) to plug two standard AT
switches into the single stereo jack:

- Switch 1 (dot) → plugs into the **Tip** side of the splitter
- Switch 2 (dash) → plugs into the **Ring** side of the splitter

If you only have one switch, plug it directly into the jack — it will be your
dot (.) switch.

---

*AeroMorse is open-source. Project files at:*
*https://github.com/jlubin2001/AeroMorse*
