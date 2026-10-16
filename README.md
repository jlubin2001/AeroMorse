# AeroMorse

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AeroMorse is a USB keyboard and mouse that you work with Morse code** — by
sip-and-puff, or with one or two switches. A short sip is a dot and a short
puff is a dash. It plugs into the computer with a USB-C cable, needs no
drivers, and works on Windows, macOS, Linux, iPadOS, Android and ChromeOS.

It is an open-source project directed by Jim Lubin, a ventilator-dependent
quadriplegic who has used Morse code for computer access since 1989. It is
his own daily device. It was inspired by
[AirTalker](https://github.com/ATMakersOrg/AirTalker).

![The author's AeroMorse with the enclosure open: the board with its screen on the left, the pressure sensor and air tube on the right](docs/images/enclosure-open.jpg)

- **About $42 in parts** for the standard build (Adafruit prices, October
  2026), plus a USB cable and an enclosure.
- **No soldering** for the standard build: two small boards, one cable
  between them, and a tube.
- **Every code can be changed** in one file. Darci USB users can keep the
  codes they know.

---

## Start here

| I want to… | Read |
|------------|------|
| **Download everything** | The [latest release](https://github.com/jlubin2001/AeroMorse/releases/latest) — one zip (under *Assets*) with the device files, the Windows programs and tools, and the PDF guides in one folder |
| **Build one** | [Build Guide](docs/AEROMORSE_BUILD_GUIDE.md) ([PDF](docs/AEROMORSE_BUILD_GUIDE.pdf)) — one standard build and three choices, then software, first test and troubleshooting |
| **Help someone use one day to day**, as a caregiver | [Caregiver Guide](docs/CAREGIVER_SETUP_GUIDE.md) ([PDF](docs/CAREGIVER_SETUP_GUIDE.pdf)) — plugging it in, the tube, and getting it going again if it stops |
| **Change the codes, settings or passwords safely** once it works | [Usage Guide](docs/AEROMORSE_USAGE_GUIDE.md) ([PDF](docs/AEROMORSE_USAGE_GUIDE.pdf)) — the work folder, the helper tools, and a one-page checklist |
| **Look up a code** | `AeroMorse Cheat Sheet.pdf` to print, or the `AeroMorse Help.html` window |
| **Understand the groups, the mouse, macros and secrets** | [Reference](docs/AEROMORSE_REFERENCE.md) ([PDF](docs/AEROMORSE_REFERENCE.pdf)) |
| **Move from a Darci USB** | [AeroMorse vs Darci](docs/AEROMORSE_VS_DARCI.md), and "Replacing a Darci USB?" below |
| **Play switch games**, or use an app that needs a key held | [Switch Mode Guide](docs/AEROMORSE_SWITCH_MODE_GUIDE.md) ([PDF](docs/AEROMORSE_SWITCH_MODE_GUIDE.pdf)) |
| **Use Switch Control on a phone or tablet** | [Switch Control Guide](docs/AEROMORSE_SWITCH_CONTROL_GUIDE.md) |
| **Compare it with other Morse devices** | [Morse Devices Comparison](docs/MORSE_DEVICES_COMPARISON.md) |
| **Know which key names I can use** in the map | [Keycode Reference](docs/KEYCODE_REFERENCE.md) ([PDF](docs/AeroMorse%20—%20Keycode%20Reference.pdf)) |
| **Set up the developer tools** (Thonny, the CircuitPython installer) | [Tools and Guides](docs/TOOLS_AND_GUIDES.md) |
| **Use it over Bluetooth** | Not supported — see [BLE_STATUS.md](docs/BLE_STATUS.md). Use a USB-C cable |

> **Sibling project — [MorseKey](https://github.com/jlubin2001/MorseKey):** the
> same Morse engine on an Adafruit TRRS Trinkey, thumb-drive sized, for one
> or two switches through its headset jack — no pressure sensor or display.

---

## Features

**What it is**

- An open-source Morse-code keyboard and mouse built from off-the-shelf
  parts, for about $42.
- Plugs in by USB-C and appears as a standard keyboard, mouse and media-key
  device; no drivers.
- Works with Windows, macOS, Linux, iPadOS, Android and ChromeOS.
- USB only; Bluetooth is not supported.

**Input**

- Sip-and-puff through a pressure sensor: a sip is a dot, a puff is a dash.
- Very light sips and puffs: a slight change of pressure in the mouth, not a
  breath. Nothing flows through the tube. Jim is dependent on a ventilator
  to breathe and works his AeroMorse all day.
- Or accessibility switches: one for dot and one for dash.
- One-, two- and three-switch modes (`SWITCH_MODE`).
- Adjustable sip and puff thresholds, with automatic re-zeroing as room
  pressure drifts.
- A strong sip or strong puff can be its own gesture, such as jumping
  straight to a group.
- Two quick sips or puffs that run together can be split into two.
- Optional Darci-style hold-to-repeat for dots and dashes.

**Groups**

- Ten groups of codes, switched by a long sip or puff, or directly by an
  8-symbol code from anywhere.
- Keyboard: letters, numbers, punctuation, function keys, navigation.
- Mouse: movement, clicks, drag, scrolling and Windows shortcuts.
- Macros: your own text strings.
- Scanning: Enter, Space and F3–F12 on the shortest codes, for phone and
  tablet Switch Control.
- Media: play / pause, volume, mute, track skip, brightness, and app
  launchers.
- Switch: no Morse; a sip holds one key and a puff holds another, for switch
  games and scanning apps.
- Three spare groups to customise.

**Keyboard**

- Sticky modifiers: send Shift, Ctrl, Alt or Win once and it applies to the
  next key.
- Shift followed by arrow keys keeps extending a text highlight.
- A repeat command for the last key or mouse move, with a list of keys that
  must never repeat.
- Keyboard-layout support for computers not set to a US layout.

**Mouse**

- Three pointer speeds and smooth repeated movement.
- Single and double clicks with the left, right and middle buttons.
- Drag: one code holds the button, the same code lets it go; a click also
  ends a drag.
- Ctrl+click and Shift+click, with the modifier kept across several clicks.
- Find the pointer (Windows draws circles round it) and jump it to the
  middle of the screen, each on one code.

**Feedback**

- A screen showing the current group, the code as you enter it, and the last
  action.
- Works with no screen at all.
- A window on the computer that shows the same thing, at any size, always on
  top or see-through.
- An optional wireless display on a second board, for when the device is out
  of the user's sight.
- Optional beeps, with different pitches for dot and dash and blips for
  actions and group changes — from a speaker on the device, or through the
  computer's speakers with no extra hardware.

**Customising and safety**

- Every code is editable in one text file, `morse_map.py`; settings live in
  `config.py`.
- A ready-made Darci USB code set for people moving from that device.
- Passwords stored encrypted and unlocked by a PIN typed in Morse, with
  optional auto-lock.
- A validator that checks edited files before they go on the device.
- A printable cheat sheet, and a help window with a tab for each group, both
  built from your own map.
- One-click backup of every plugged-in device.
- A ready-made AutoHotkey script: one Morse code each to open the display
  window, open the help window, and centre the pointer — and a place to add
  your own.

**Hardware**

- The standard build is two small Adafruit boards and one cable, with no
  soldering.
- A no-solder switch build on the Cytron Maker Feather AIoT S3 with Headers
  adds AT switches and a speaker.
- Other boards, displays, switch wiring and speakers are documented in the
  Build Guide's appendices, marked as not tested.

---

## What you build

**The standard build** is the one the project is designed around and tested
on every day:

| Part | Adafruit # | Price |
|------|-----------|-------|
| ESP32-S3 Reverse TFT Feather — the board, with a colour screen built in | [#5691](https://www.adafruit.com/product/5691) | $24.95 |
| LPS33HW pressure sensor | [#4414](https://www.adafruit.com/product/4414) | $12.50 |
| STEMMA QT cable, 100 mm | [#4210](https://www.adafruit.com/product/4210) | $0.95 |
| Silicone tubing, 1 m | [#3659](https://www.adafruit.com/product/3659) | $3.50 |
| USB-C **data** cable | any | — |

Plug the cable between the two boards, push the tube onto the sensor, plug
in the USB cable. Then install the software (below).

**Three things you can choose differently** — the Build Guide covers each:

| Choice | Options |
|--------|---------|
| **Input** | sip-and-puff (standard) · switches, on a board that needs no soldering · switches on the standard board |
| **Display** | built-in screen (standard) · a window on the computer, any size · a wireless display on a second board |
| **Audio feedback** | none (standard) · through the computer's speakers · a speaker on the device |

**Sound volume.** There is no volume setting in `config.py`; it depends on
how the sound is played:

- **Through the computer** (`PC_SOUND = True`): right-click the AeroMorse
  Display window and choose **Sound → Off / Quiet / Medium / Loud**. It also
  follows the computer's own volume.
- **A speaker on the device:** the firmware drives it at one fixed level, so
  the loudness depends on the part. A built-in buzzer or a small piezo can't
  be adjusted. The STEMMA Speaker (#3885) is louder and has a small
  **Volume** screw on its board.

`config.py` sets only the pitches and how long the blips last; those apply
to both.

An enclosure and a strain relief for the tube are not included above; the
Build Guide's Appendix H covers them.

**Will this be someone's only way to use a computer?** Consider building
two — a spare, and a safe place to try changes.

---

## Install the software

The [Build Guide](docs/AEROMORSE_BUILD_GUIDE.md), section 9, has the full
walk-through. The short version:

### 1. Install CircuitPython on the Feather

1. Go to **https://circuitpython.org/downloads**
2. Search for your Feather board name (e.g. "ESP32-S3 Reverse TFT").
3. Download the latest **stable** `.uf2` file — **not** a pre-release / "absolute
   newest" build. (An older Feather bootloader may fail to flash a much newer
   CircuitPython; if the drive won't switch to CIRCUITPY, try the previous
   stable major version.)
4. Plug the Feather into your computer with the USB-C **data** cable (a
   charge-only cable won't show a drive).
5. **Double-tap** the small **Reset** button quickly (two taps within about half
   a second).
   - The NeoPixel LED on the Feather turns **green**.
   - A drive named **FTHRS3BOOT** (or similar) appears on your computer.
6. **Drag** the `.uf2` file you downloaded onto that drive.
7. The Feather reboots automatically. After a few seconds a drive named
   **CIRCUITPY** appears. Done.

> If **CIRCUITPY** already appears when you plug in (without double-tapping),
> CircuitPython is already installed — skip to step 2. If you see
> **FTHRS3BOOT** every time you plug in without double-tapping, the board just
> has no code loaded yet — that's normal, continue.

### 2. Install the required libraries

1. Go to **https://circuitpython.org/libraries**
2. Download the **Bundle** that matches your CircuitPython version. To find your
   version, open `boot_out.txt` on the CIRCUITPY drive — it says something like
   `Adafruit CircuitPython 10.2.0`, so download the matching major version
   (9.x or 10.x).
3. Open the `.zip`; inside is a folder called `lib`.
4. On the CIRCUITPY drive, open (or create) the `lib` folder, and copy in the
   items in the list below (from the bundle's `lib` folder — you don't
   need the whole bundle):

   ```
   adafruit_hid/            adafruit_bus_device/     adafruit_register/
   adafruit_display_text/   neopixel.mpy             adafruit_lps35hw.mpy
   ```

   The last one is only needed with the sip-and-puff sensor.
   - **Two are easy to miss:** `neopixel.mpy` (a bare file with no `adafruit_`
     prefix, so it sorts to the bottom of the bundle's `lib`) and
     `adafruit_lps35hw.mpy` (your sensor is the **LPS33HW**, but the driver is
     named **`lps35hw`** — the same file covers both).

### 3. Copy the AeroMorse software

Download **`AeroMorse-v1.30.zip`** (the number is the version) from the
[latest release](https://github.com/jlubin2001/AeroMorse/releases/latest) — it is under *Assets* — and unzip it. Copy these four
files from that folder to the **root** of CIRCUITPY:

```
boot.py   code.py   config.py   morse_map.py
```

> Always get these from **https://github.com/jlubin2001/AeroMorse** — copies
> posted elsewhere may be older. Each file's header comment shows its version
> and release date; keep all four at the same version.

### 4. Restart and go

Safely eject the drive and press the **Reset** button (or unplug and replug).
On power-up the device calibrates for one second (hold the tube still — do not
sip or puff), then the TFT display shows the **start screen**:

- the device's name (`DEVICE_NAME` in `config.py`, e.g. **AeroMorse Green**),
- the AeroMorse version (e.g. **v1.30**),
- the CircuitPython version (e.g. **CP 9.2.9**).

The device is now ready. Your **first** sip, puff or switch press only closes
the start screen — it types nothing — and the display changes to
**[ KEYBOARD ]**. From then on every sip/puff counts. (To see the start screen
again later, use the Mouse-group `version` command, `...-`.)

---

## Using it

Enter a code as dots and dashes, then pause; after a short pause the code is
accepted and its key is typed. `.--` is **W**.

Everything is arranged in **groups**. The device starts in Keyboard. A long
sip or puff steps through the groups, and an 8-symbol code jumps straight to
one from anywhere.

| Group | Name | What it is for | Jump code |
|-------|------|----------------|-----------|
| 1 | **Keyboard** | letters, numbers, punctuation, function keys, modifiers | `........` |
| 2 | **Mouse** | movement, clicks, drag, scrolling, shortcuts | `--------` |
| 3 | **Macros** | your own phrases, and passwords kept in a separate locked file | `....----` |
| 4 | **Scanning** | Enter, Space and F-keys for iOS / Android Switch Control | `.......-` |
| 5 | **Media** | volume, play / pause, brightness, app launchers | `......--` |
| 6, 7, 8 | *spare* | copies of the Keyboard letters, ready for your own codes | `.....---` `...-----` `..------` |
| 9 | **Switch** | no Morse: sip holds Enter, puff holds Space, for switch games | `.-------` |
| 0 | *always on* | the jump codes above, and two hotkeys | — |

- **Every code**: print `AeroMorse Cheat Sheet.pdf`, or open
  `AeroMorse Help.html` — a window with a tab for each group.
- **How the groups, the mouse, repeat, sticky modifiers and drag work**: the
  [Reference](docs/AEROMORSE_REFERENCE.md).

### On the computer (Windows)

Three optional extras need no hardware:

| | What it does | Morse code |
|---|---|---|
| **AeroMorse Display** | the device's screen in a window on the computer, any size; can also play the beeps through the computer's speakers | `.-.-.-` on / off |
| **AeroMorse Help** | the cheat sheet in a window, one tab per group | `..-..-` on / off |
| **Centre pointer** | puts the mouse pointer in the middle of the screen | `-..--` in the Mouse group |

The codes work through the supplied `AeroMorse.ahk` script and the free
AutoHotkey program. Set-up is in the Usage Guide, section 7.

---

## Changing it

- **Codes** are in `morse_map.py`, one line per code. **Settings** are in
  `config.py`. Both are plain text files on the device's own drive.
- **Follow the [Usage Guide](docs/AEROMORSE_USAGE_GUIDE.md).** It sets up a work
  folder and gives a safe order for any change: back up, edit a copy, run
  the validator, copy to the device only after it says PASS. This matters
  most when the device is your only computer access — a small typing
  mistake in either file can stop it starting.
- **Every setting** is explained in the Build Guide, Appendix E.
- **Passwords** do not go in `morse_map.py`. They go in a separate file that
  can be locked with a PIN you enter in Morse — see the
  [Reference](docs/AEROMORSE_REFERENCE.md#storing-passwords-and-secrets-safely).

---

## Replacing a Darci USB? Start here.

AeroMorse is a modern, open-source alternative to the **WesTest Darci USB**
Morse-code input device (now end-of-life, Windows-only, ~$1000+).

If you are a current Darci user or know someone who is, AeroMorse provides:

- ✅ **The same Morse codes you already know** — letters A–Z, numbers 0–9,
  punctuation, F-keys, navigation, and modifiers can all use Darci's exact
  code set via the included **`morse_map_darci.py`** drop-in code map.
- ✅ **Modern OS support** — works on Windows 10/11, macOS, Linux, ChromeOS,
  iPadOS, and Android. No Windows-only Mouse Keys dependency.
- ✅ **Lower cost** — ~$50–$100 in off-the-shelf parts vs. ~$1000+ commercial
  device.
- ✅ **Built-in sip-and-puff** — no external interface required.
- ✅ **One-, two- and three-switch input** — the same three arrangements Darci
  offers, chosen with `SWITCH_MODE` in `config.py`. The third "switch" is a
  long press on one of the two inputs, not a third jack.
- ✅ **Active development** — open source, customisable, and supported.
- ✅ **Optional wireless remote display** — see the user's screen from
  across the room (no equivalent on Darci).

Read **[`AEROMORSE_VS_DARCI.md`](docs/AEROMORSE_VS_DARCI.md)** for a full
feature-by-feature comparison, an honest list of where Darci may still suit
you better (three separate physical switch jacks, a ruggedized commercial
enclosure with a warranty, a smoother sine-wave tone), and a migration
checklist.

To preserve Darci muscle memory, rename **`morse_map_darci.py`** to
`morse_map.py` on the CIRCUITPY drive. All codes in that file are
transcribed verbatim from the Darci USB Owner's Manual (P/N 3001508).

---

## Project files

### Files that go on the device

| File | Purpose |
|------|---------|
| `code.py` | Main firmware — Morse state machine, USB HID, display, ESP-NOW sender |
| `boot.py` | Runs once at power-on. **Same file on every board** — auto-detects its role from whether `morse_map.py` is present on the drive. Sender → enables USB HID (Keyboard, Mouse, Consumer Control). Receiver → leaves HID off, and optionally hides CIRCUITPY + serial from the host if an empty `/hide` file is present on the drive. |
| `config.py` | **All user-tunable settings** — sensor thresholds, switch mode, code repeat, audio pitches, timing, etc. Edit this file instead of `code.py`. |
| `morse_map.py` | All Morse code assignments for every group — edit to remap keys |
| `morse_map_darci.py` | Drop-in alternative code map for **Darci USB users** — rename to `morse_map.py` on CIRCUITPY to use Darci's exact code set |
| `macro_secrets.example.txt` | Template for your **private** secret macros (passwords, personal details), with a line for every key the standard `morse_map.py` uses. Copy it to `macro_secrets.txt` in your work folder, fill in `key=value` lines, then encrypt it with AeroMorse Secrets — step by step in the [Usage Guide](docs/AEROMORSE_USAGE_GUIDE.md). |
| `macro_secrets.txt` | **Your real passwords / secrets — never share, never committed** (git-ignored). Plain `key=value` lines. Created by you from the `.example` template. If absent or a line is bad, that secret macro just types a placeholder. |
| `macro_secrets.enc` | **Optional, recommended instead of `macro_secrets.txt`** — the same secrets **encrypted**, unlocked with a PIN typed in Morse. Made with `AeroMorse Secrets.exe` (git-ignored). See [PIN-locked secrets](#pin-locked-secrets-macro_secretsenc). |
| `receiver.py` | Wireless display mirror firmware, for a second #5691 colour TFT (Build Guide §5.3). 240×135 colour display with full live preview. Copy as `code.py` to the receiver board. |
| `receiver_config.py` | **Settings for the wireless display board only**: `ESPNOW_CHANNEL` (must match the main device's `config.py`), `DISPLAY_BRIGHTNESS`, `DISPLAY_ROTATION`, `SLEEP_AFTER_S`, `NO_SIGNAL_S` and `AUTO_RESET_S`. Copy it next to the display's `code.py`. If it's missing or a value is wrong, the built-in default is used and the display keeps working. |
| `display_setup.example.py` | **Only for a display that is not built into the board** (TFT FeatherWing, breakout, OLED). Copy it to the drive as `display_setup.py` and keep the block for your display; `code.py` and `receiver.py` pick it up by themselves and size the layout to the screen (v1.26+). Not needed — and not to be copied — on the #5691 or any board with a built-in screen. The example blocks are untested |

### Programs and pages you use on the computer

| File | Purpose |
|------|---------|
| `aeromorse_display.py` / `AeroMorse Display.exe` | **The AeroMorse screen in a window on the computer** (v1.26+) — any size, always-on-top or see-through, no extra hardware. Set `PC_DISPLAY = True` in `config.py`, then start the program; it finds the device, only listens (never sends anything to it) and reconnects by itself. See Build Guide §5.2. Build Guide **Appendix G** (also Usage Guide §7) shows how to open and close it with one Morse code, using the free AutoHotkey program (where to get it, a sample script, starting it with Windows). **It can also play the device's beeps through the computer's speakers** (`PC_SOUND = True`, v1.27+), for a device with no speaker fitted. The `.exe` is for Windows; on a Mac or Linux computer run `aeromorse_display.py` with Python (not tested yet; Build Guide §5.4) |
| `AeroMorse Help.html` | **The cheat sheet as a help window** — legend at the top and one tab per group, so there is no scrolling through pages; click a tab, press a group's number, or use the arrow keys. A single file with the map inside it, built by `build_pdfs.py` alongside the cheat sheet PDF (the copy in the repo is for the supplied map; build your own from your map with `--folder`). Opened and closed with one Morse code through `AeroMorse.ahk` (next row). |
| `AeroMorse.ahk` | **Ready-made AutoHotkey script (Windows)** for the three things a keyboard device cannot do by itself, each with a Morse code already in the supplied map: **Ctrl+Alt+D** AeroMorse Display window on / off (`.-.-.-`, Group 0), **Ctrl+Alt+H** AeroMorse Help window on / off (`..-..-`, Group 0), **Ctrl+Alt+Home** mouse pointer to the middle of the screen (`.-.`, Mouse group). Keep it in your work folder next to `AeroMorse Display.exe` and `AeroMorse Help.html` — it finds them there, nothing to edit. Needs AutoHotkey v2; set-up in Usage Guide §7 / Build Guide Appendix G. |
| `aeromorse_cheatsheet.htm` | Interactive browser-based cheat sheet — open in any browser, no install needed. Shows every pattern for the active group as animated dots and dashes; click any row to hear the timing. |
| `AeroMorse Cheat Sheet.pdf` | Printable cheat sheet — one page per group, showing every pattern as dots/dashes next to its key or action, with a legend on the first page. Printed from `aeromorse_cheatsheet.htm` (load `morse_map.py` and use the browser's Print). |

### Tools for changing your device safely

| File | Purpose |
|------|---------|
| `aeromorse_validator.py` / `aeromorse_validator.exe` | **Safety check — run this before trusting edited device files on the device.** Checks every required file the device needs to boot: **`boot.py`, `code.py`, `config.py`, `morse_map.py`** (plus optional `macro_secrets.txt`). For each it catches the things CircuitPython is fussy about that desktop editors hide: a **UTF-8 BOM** (the classic "lost all access" cause) and a Python **syntax error**. For `config.py` and `morse_map.py` it also reproduces the device's actual import (catching an **import error**), sanity-checks `config.py` settings (missing settings, out-of-range values), and confirms every `_secret()` pattern finds its value in `macro_secrets.txt`. Reports a plain-language **PASS** (safe) or **FAIL** (fix before relying on it — don't replace your working files yet), pointing at the exact line. A file that isn't in the folder shows **SKIP**, not FAIL. **Never prints secret values** — key names and counts only. Put it in the same folder as the file(s) you edited and double-click the `.exe`, or run `python aeromorse_validator.py`. Accepts an optional folder/file argument (e.g. `aeromorse_validator.exe F:\`) to check the device directly. |
| `Check my AeroMorse files.bat` | **One-click** wrapper for the validator. Keep it in your work folder next to `aeromorse_validator.exe` and the files you edited (`boot.py`, `code.py`, `config.py`, `morse_map.py`, `macro_secrets.txt`); double-click it to run the safety check on that folder and see PASS/FAIL. |
| `Back up my AeroMorse.bat` | **One-click dated backup.** Keep it in your work folder and double-click with the device plugged in: copies everything on every AeroMorse (CIRCUITPY) drive into `Backups\<name>-<YYYY-MM-DD_HHMM>`, named from a label file such as `AeroMorse-Green.txt` on the device. Read-only on the device. |
| `aeromorse_secrets.py` / `AeroMorse Secrets.exe` | **Edit your passwords and save them PIN-locked.** Opens `macro_secrets.enc` (asks the PIN) or imports `macro_secrets.txt`, lets you edit the `key=value` lines, saves them encrypted with a PIN you choose, warns about `_secret()` keys in `morse_map.py` with no value, and can copy the file to the CIRCUITPY drive and remove the plain-text file. See [PIN-locked secrets](#pin-locked-secrets-macro_secretsenc). The `.py` needs `pip install cryptography`; the `.exe` needs nothing. |
| `Edit my AeroMorse secrets.bat` | **One-click** launcher for AeroMorse Secrets. Keep it in your work folder next to `AeroMorse Secrets.exe` and `morse_map.py`; double-click it to open the secrets in that folder. |
| `morse_map_comments.py` / `morse_map_comments.exe` / `Fix my map comments.bat` | **Makes the comments in `morse_map.py` match the codes.** Each line shows its pattern twice — the binary number the device uses and dots and dashes in the comment — and the comment is easy to forget when you change the number. Keep the `.exe` and the `.bat` next to your `morse_map.py` and double-click either one (no Python needed; with Python, `python morse_map_comments.py` does the same) and it rewrites the pattern at the start of each comment to say what the number says, lists every change, and keeps the file as it was as a `.bak`. `--check` only lists. It trusts the number: if a new pattern is not the one you meant, the number is what needs fixing. The validator warns about the same mismatches. |
| **On a Mac or Linux** | The `.exe` files and `.bat` tools are for Windows. The `.py` versions of the validator, AeroMorse Secrets, the comment fixer, the analyzer and AeroMorse Display run with Python 3 instead — see the Usage Guide, "On a Mac or a Linux computer" (not tested on a Mac yet). |
| `morse_map_analyzer.py` | Python 3 script that reads `morse_map.py` and reports duplicate codes, conflicts with the always-on Group 0 patterns, and unused code slots for lengths 2–7. Run with `python morse_map_analyzer.py`; output is saved to `morse_map_report.txt`. |
| `morse_map_report.txt` | Latest output from `morse_map_analyzer.py` |
| `KEYCODE_REFERENCE.md` / `keycode_reference.htm` / `AeroMorse — Keycode Reference.pdf` | Reference of every valid `Keycode.NAME` for `morse_map.py` (letters, number keys, navigation, punctuation, F-keys, keypad, modifiers), plus how to produce shifted symbols (`:` `{` `}` …). The `.pdf` is the ready-to-print 2-page sheet; the `.htm` is the same styled for the browser; the `.md` opens in the Markdown viewer. Extracted from the `adafruit_hid` 9.x library on the devices. |

### Guides

The guides and their PDFs are in the [`docs`](docs) folder, with the photos
in `docs/images`. The release zip has the PDFs.

### For developers

| File | Purpose |
|------|---------|
| `make_release_zip.py` | **Builds the release download**, `dist/AeroMorse-v<version>.zip`: one folder with the device files, the Windows programs and tools, the help pages, the PDF guides and a `START HERE.txt`, laid out like a work folder. The version comes from `code.py`. Attach the zip to a GitHub release. |
| `build_pdfs.py` / `Build PDFs.bat` | **Regenerate the three printable PDFs** (`AEROMORSE_BUILD_GUIDE.pdf`, `AeroMorse Cheat Sheet.pdf`, `AeroMorse — Keycode Reference.pdf`) from their sources. Double-click `Build PDFs.bat` after editing the Build Guide, cheat sheet, `morse_map.py`, or the Keycode reference. Rebuilds all three; add `guide`, `cheatsheet`, or `keycode` to rebuild just one. **Personal cheat sheet:** `python build_pdfs.py --folder <your work folder>` prints `AeroMorse Cheat Sheet.pdf` from *your* `morse_map.py` into that folder (a one-click `Build my cheat sheet.bat` in the edit folder does this). Needs Microsoft Edge and Python. |
| `test_pressure.py` | Diagnostic script — copy to CIRCUITPY; press Ctrl-C to reach the `>>>` REPL prompt (do **not** reset — that re-runs `code.py`), then `import test_pressure`. To run again: `exec(open('test_pressure.py').read())` (`importlib` is not available in CircuitPython). Prints a live pressure-delta bar chart for 30 s and suggests `THRESH_SIP` / `THRESH_PUFF` values for `config.py`. |
| `test_ble.py` | **Bluetooth keyboard test** (CircuitPython 10.x, needs `adafruit_ble/` in `lib/`). Results so far: [BLE_STATUS.md](docs/BLE_STATUS.md) — not usable yet. Copy to CIRCUITPY, stop `code.py` (Ctrl-C, then Enter for `>>>`), and run `import test_ble`. It advertises as "AeroMorse Blue"; pair from the phone's Bluetooth settings and it types a few test lines, printing whether it connected, paired, and stayed connected. Doesn't touch `code.py`. **On ESP32-S3 + CircuitPython 10.3.1 a BLE keyboard does not stay connected yet** — see Build Guide Appendix L. |

---

## Troubleshooting

The Build Guide, section 12, is the full troubleshooting chapter, including
the pop-ups Windows and antivirus programs show when the device restarts
(they are harmless). The most common problems:

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| No keyboard/mouse on host | `boot.py` missing or not yet run | Copy `boot.py` to CIRCUITPY, press Reset |
| Nothing happens when sipping/puffing | Wrong library or sensor not found | Check serial REPL for error messages; confirm `adafruit_lps35hw.mpy` is in `lib/` |
| Letters misfire (e.g. `b` types `n`) | Thresholds too low — pressure not returning to neutral between dots | Increase `THRESH_SIP` / `THRESH_PUFF` |
| False triggers at rest | Thresholds too low | Increase `THRESH_SIP` / `THRESH_PUFF` |
| Longer patterns are slow to be accepted | `ACCEPT_DELAY` too long | Decrease `ACCEPT_DELAY` (try `0.15`) |
| Pattern commits before finished | `ACCEPT_DELAY` too short | Increase `ACCEPT_DELAY` |
| Pattern shows `?` on display | Pattern not mapped in current group | Check `morse_map.py`; REPL shows the exact pattern received |
| Calibration message at startup then hangs | Sensor not found on I²C | Check the STEMMA QT cable connection — or, on a board without a STEMMA QT port, the 3V / GND / SDA / SCL wires |
| Dashes go missing (e.g. `x` `-..-` types `u` `..-`, `q` types `k`) | A quick puff right before a sip doesn't reach `THRESH_PUFF` on this sensor | Lower `THRESH_PUFF` a little (e.g. `2` → `1.5`); leave `THRESH_SIP` alone if dots are fine |
| Two sips or two puffs in a row count as one (`p` `.--.` types `r` `.-.`, space `..--` types `w` `.--`) | The pressure doesn't fall back under the trigger between the two | Set `REPEAT_SPLIT_PCT = 60` in `config.py` (v1.18+), or leave a slightly longer break between the two |
| Screen shows `ERROR - SEE LOG` | One action hit an unexpected problem (v1.6+ keeps running instead of stopping) | Keep using the device; the USB serial log shows which pattern and why. Fix that entry in `morse_map.py` and run the validator |

---

## How this project was built

AeroMorse grew out of **AirTalker**. Bill Binko at
[ATMakers](https://github.com/ATMakersOrg/AirTalker) built AirTalker for
Jim, first as a backup for the Adap2U Morse code keyboard and mouse he had
used since 1994, and in time as its replacement. The second version of
AirTalker used an ESP32-S3 Reverse TFT Feather and an LPS33HW pressure
sensor — the same two boards AeroMorse is built on today.

After using it every day, Jim wanted to change some things and add
features. He does not write code himself, so he turned to AI: first Gemini
Pro (Google), then Claude (Anthropic), working through Claude Code.
AeroMorse is the result.

Jim is the user and the project lead, and every design decision is his: the
hardware, the input modes, the code sets, the accessibility trade-offs. They
come from his own daily use and from what other Morse users have told him,
Darci USB veterans in particular. The firmware and the documents are written
by Claude under his direction.

**What is tested.** The standard build is Jim's daily device. The Build
Guide marks every other option as tested or not tested. If you build
something, please report how it went in a GitHub issue, whether it worked or
not.

## Credits

- **Bill Binko and [ATMakers](https://github.com/ATMakersOrg/AirTalker)** —
  for AirTalker, where AeroMorse began. Thanks, Bill!
- **Jim Lubin** — user and project lead. Jim has used Morse code for
  computer access since 1989, when he became a ventilator-dependent
  quadriplegic. His home page is <https://makoa.org/jim>, and his page on
  Morse code is <https://makoa.org/jlubin/morsecode.htm>.
- **Gemini Pro (Google)** and **Claude (Anthropic)**, through Claude Code —
  for the code and the documents, written under Jim's direction.
