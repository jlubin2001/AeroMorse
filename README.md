# AeroMorse

A USB HID keyboard and mouse device controlled entirely by sip-and-puff breath
input or two momentary switches.  Characters and commands are entered using
Morse code: a short sip (or switch 1) is a **dot**, a short puff (or switch 2)
is a **dash**.  The device appears to the host computer as a standard USB
keyboard and mouse — no drivers required on any operating system.

---

## Hardware

### Required

| Part | Description | Adafruit Product |
|------|-------------|-----------------|
| **Adafruit ESP32-S3 Reverse TFT Feather** | Microcontroller with built-in 240×135 px colour TFT display, USB-C, STEMMA QT port, 4 MB Flash, 2 MB PSRAM | [#5691](https://www.adafruit.com/product/5691) |
| **Adafruit LPS33HW Water Resistant Pressure Sensor** | Differential pressure sensor with STEMMA QT connector | [#4414](https://www.adafruit.com/product/4414) |
| **STEMMA QT cable** | 4-pin JST SH cable to connect the sensor to the feather | [#4210](https://www.adafruit.com/product/4210) |
| **USB-C cable** | Connects device to host computer (data + power) | any |
| **Sip-and-puff tube** | Standard ¼ inch OD tubing connected to the LPS33HW port | medical supply / hardware store |

### Optional — Switch Mode

If a pressure sensor is not available, two momentary normally-open switches
can be wired instead.  Set `USE_SENSOR = False` in `code.py`.

| Pin | Function |
|-----|----------|
| D5 (default) | Dot switch (sip equivalent) |
| D6 (default) | Dash switch (puff equivalent) |

Wire each switch between the GPIO pin and GND.  The firmware enables internal
pull-up resistors, so no external resistors are needed.

---

## Wiring

With the sensor option, wiring is a single cable:

```
ESP32-S3 Reverse TFT Feather   ←—— STEMMA QT cable ——→   LPS33HW sensor
      STEMMA QT port                                       STEMMA QT port
```

No soldering required.  The STEMMA QT cable carries power, ground, and I²C
data.  Plug the sip-and-puff tubing into the small port on top of the LPS33HW.

---

## Files on the Device (CIRCUITPY drive)

The CIRCUITPY drive is the FAT filesystem that appears when the feather is
connected to a computer.

| File | Purpose |
|------|---------|
| `boot.py` | Runs once at power-on before `code.py`.  Enables USB HID keyboard and mouse devices. **Must be present or the device will not appear as a keyboard/mouse.** |
| `code.py` | Main program.  Reads input, runs the state machine, executes actions, drives the display. |
| `morse_map.py` | All Morse code assignments for every group.  Edit this file to remap keys. |

### Required Libraries (in `lib/` folder on CIRCUITPY)

These are pre-compiled `.mpy` files from the
[Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases).
Download the bundle matching your CircuitPython version (9.x) and copy the
listed items from its `lib/` folder.

| Library | Type | Purpose |
|---------|------|---------|
| `adafruit_hid/` | folder | USB HID keyboard and mouse (keyboard, mouse, keycodes, layout) |
| `adafruit_display_text/` | folder | Text labels for the TFT display |
| `adafruit_lps35hw.mpy` | file | Driver for the LPS33HW pressure sensor |
| `adafruit_register/` | folder | Required by `adafruit_lps35hw` |
| `adafruit_bus_device/` | folder | Required by `adafruit_lps35hw` |

---

## Setup

1. Install **CircuitPython 9.x** on the feather by following
   [Adafruit's guide](https://learn.adafruit.com/esp32-s3-reverse-tft-feather).
2. Copy the required libraries (listed above) into the `lib/` folder on CIRCUITPY.
3. Copy `boot.py`, `code.py`, and `morse_map.py` to the root of CIRCUITPY.
4. Eject / safely remove the drive and press the Reset button (or unplug and
   replug).
5. On power-up the device will calibrate for one second (hold the tube still
   and do not sip or puff), then the TFT display will show **[ Keyboard ]** and
   the device is ready.

---

## How Input Works

### Dot and Dash

| Input mode | Dot | Dash |
|------------|-----|------|
| Sensor | Sip (pressure drops ≥ 5 hPa) | Puff (pressure rises ≥ 5 hPa) |
| Switches | Press DOT switch (D5) | Press DASH switch (D6) |

### Morse Detection State Machine

The firmware uses a three-state machine that matches standard Morse timing:

- **DIT** — sensor is below sip threshold
- **DAH** — sensor is above puff threshold
- **IDLE** — pressure is within the neutral band

Each time the sensor transitions **from DIT or DAH back to IDLE**, that element
(dot or dash) is recorded.  After **0.2 seconds of continuous IDLE** with at
least one element recorded, the accumulated pattern is looked up in the code
table and the matching action fires.

### Long Press — Group Cycling

Holding a sip or puff for **2 or more seconds** cycles through groups 1–3
instead of recording an element (Group 0 is skipped — its 8-symbol emergency
patterns remain available in the background at all times):

| Long press | Effect |
|------------|--------|
| Long sip | Cycle groups **backward** (3 → 2 → 1 → 3 …) |
| Long puff | Cycle groups **forward**  (1 → 2 → 3 → 1 …) |

---

## Groups

The device has four groups.  The active group determines which code table is
used for pattern lookup.  **Group 0 is always checked first**, regardless of
the active group — its 8-symbol patterns are available at all times.

### Group 0 — Always Available (Emergency Group Switch)

These 8-symbol patterns work in any group and jump directly to the named group.

| Pattern | Symbols | Destination |
|---------|---------|-------------|
| `........` | 8 dots | Group 1 — Keyboard |
| `--------` | 8 dashes | Group 2 — Mouse / Shortcuts |
| `....----` | 4 dots then 4 dashes | Group 3 — Macros |
| `----....` | 4 dashes then 4 dots | Group 2 — Mouse / Shortcuts (second shortcut) |

### Group 1 — Keyboard

The default group after power-on.  Provides letters, numbers, punctuation,
function keys, navigation keys, and modifier keys.

**Two non-standard patterns** free up codes for high-frequency control keys:

| Letter | Standard ITU | AeroMorse | Freed code used for |
|--------|-------------|-----------|---------------------|
| M | `--` | `----` | `--` → Backspace |
| C | `-.-.` | `---.` | `-.-.` → Left Control |

#### Letters

| Letter | Pattern | Letter | Pattern |
|--------|---------|--------|---------|
| A | `.-` | N | `-.` |
| B | `-...` | O | `---` |
| C | `---.` *(non-std)* | P | `.--.` |
| D | `-..` | Q | `--.-` |
| E | `.` | R | `.-.` |
| F | `..-.` | S | `...` |
| G | `--.` | T | `-` |
| H | `....` | U | `..-` |
| I | `..` | V | `...-` |
| J | `.---` | W | `.--` |
| K | `-.-` | X | `-..-` |
| L | `.-..` | Y | `-.--` |
| M | `----` *(non-std)* | Z | `--..` |

#### Numbers

| Number | Pattern | Number | Pattern |
|--------|---------|--------|---------|
| 1 | `.----` | 6 | `-....` |
| 2 | `..---` | 7 | `--...` |
| 3 | `...--` | 8 | `---..` |
| 4 | `....-` | 9 | `----.` |
| 5 | `.....` | 0 | `-----` |

#### Punctuation

| Character | Pattern | Character | Pattern |
|-----------|---------|-----------|---------|
| `+` | `-...-` | `!` | `.-....` |
| `-` | `.---.` | `@` | `---..-` |
| `=` | `---.-` | `#` | `..---.` |
| `*` | `-..--` | `$` | `..----` |
| `.` | `.-----` | `%` | `...-.-` |
| `,` | `-.....` | `^` | `-...--` |
| `:` | `.----.` | `&` | `.---..` |
| `;` | `-....-` | `?` | `-.----` |
| `)` | `...---` | `/` | `....--` |
| `(` | `---...` | `\` | `----..` |
| `]` | `-..---` | `\|` | `....-. ` |
| `[` | `.--...` | `_` | `----.-` |
| `}` | `--..-` | `"` | `...--.` |
| `{` | `..--.` | `'` | `..-...` |
| `<` | `--..--` | `` ` `` | `--.---` |
| `>` | `..--..` | `~` | `---.--` |

#### Function Keys

7-symbol patterns.  The dash/dot boundary shifts one step per key:

| Key | Pattern | Key | Pattern |
|-----|---------|-----|---------|
| F1 | `--.----` | F7 | `----...` |
| F2 | `--..---` | F8 | `-----..` |
| F3 | `--...--` | F9 | `------.` |
| F4 | `--....-` | F10 | `-------` |
| F5 | `--.....` | F11 | `.------` |
| F6 | `---....` | F12 | `..-----` |

#### Navigation & Editing Keys

| Key | Pattern | Code |
|-----|---------|------|
| Up Arrow | `.-..-` | `au` |
| Down Arrow | `.--..` | `ad` |
| Left Arrow | `.-.-..` | `al` |
| Right Arrow | `.-.-.` | `ar` |
| Home | `.......` (7 dots) | |
| End | `...-...` | |
| Page Up | `.....-` | `su` |
| Page Down | `...-..` | `sd` |
| Enter | `.-.-` | |
| Escape | `--....` | |
| Delete | `-.--..` | `kd` |
| Insert | `-.-..` | `ki` |
| Backspace | `--` | |
| Space | `..--` | |
| Tab | `---..-.` | `of` |

#### Modifier Keys (Sticky)

Modifier keys are **sticky**: press the pattern once to **arm** the modifier.
The modifier symbol will appear on the TFT display.  The next key pressed fires
with that modifier held, then the modifier automatically releases.  Press the
modifier pattern again while it is armed to **disarm** it without firing.

| Modifier | Pattern |
|----------|---------|
| Left Control | `-.-.` |
| Left Shift | `--...-` |
| Left Alt | `--.--` |
| Left GUI (Win/Cmd) | `.--.--` |
| Caps Lock | `-----.` |
| Scroll Lock | `--.-..` |
| Num Lock | `---...-` |
| Print Screen | `--.--. ` |

#### Group Switch

| Action | Pattern |
|--------|---------|
| Switch to Group 2 (Mouse) | `...-. ` |

### Group 2 — Mouse & Shortcuts

Mouse movements follow the **numeric keypad layout**: the nine directions
(up-left through down-right) map to the same positions as numpad 7–9, 4–6, 1–3.
Each cardinal direction has a short pattern (2–3 symbols) and a large-step
pattern (5 symbols).

#### Mouse Movement

| Direction | Short pattern | Large pattern |
|-----------|--------------|---------------|
| ↑ Up | `--` | `---..` |
| ↓ Down | `---` | `..---` |
| ← Left | `..` | `....-` |
| → Right | `...` | `-....` |
| ↖ Up-Left | `--...` | — |
| ↗ Up-Right | `----.` | — |
| ↙ Down-Left | `.----` | — |
| ↘ Down-Right | `...--` | — |
| Scroll ↑ | `.....-` | — |
| Scroll ↓ | `...-..` | — |

Mouse speed is controlled by three modes:

| Mode | Speed multiplier | How to activate |
|------|-----------------|-----------------|
| Normal | ×2 | Default; also restored by `mslow` / `mfast` toggle |
| Slow | ×1 | `mslow` pattern `--..` (toggle) |
| Fast | ×3 | `mfast` pattern — (see morse_map.py for assignment) |

The effective pixels moved per step = **raw direction value × speed × 2**.

#### Mouse Buttons

| Action | Pattern |
|--------|---------|
| Left click | `.-` |
| Right click | `.--` |
| Double-click left | `..-` |
| Double-click right | `..--` |
| Toggle left-button drag | `-.` |

#### Repeat

| Action | Pattern |
|--------|---------|
| Toggle repeat | `.` (numpad 5) |
| Toggle repeat (alternate) | `..-..` |

**Repeat** re-fires the last action continuously until toggled off:
- After a **mouse move**: cursor glides smoothly using pixel-accurate
  time-based interpolation at 40 ms intervals.
- After a **key, combo, or text**: fires that action every 40 ms.
- After switching groups, repeat is **cleared** — you must make a mouse
  move before repeat will activate in Group 2.

Any new sip or puff while repeating immediately **stops** the repeat.

#### Drag

The drag toggle holds the left mouse button down.  Send the drag pattern again
to release it.  The TFT status row shows **DRAG** while drag is active.

#### Other Controls

| Action | Pattern | Effect |
|--------|---------|--------|
| `mslow` | `--..` | Toggle slow-step mouse speed |
| `mreset` | `-.-..-. ` | Release drag, stop repeat, restore normal speed |

#### Arrow & Keypad Keys

Group 2 also provides arrow keys and a full numeric keypad, using the same
patterns as Group 1:

| Key | Pattern |
|-----|---------|
| Up / Down / Left / Right Arrow | same as Group 1 |
| Keypad 0–9 | — (see morse_map.py) |
| Keypad Enter | `.-.-` |
| Keypad +  −  ×  ÷  .| same patterns as their Group 1 text equivalents |
| Application (context menu) | `----..` |

#### Windows Shortcuts

| Shortcut | Pattern | Action |
|----------|---------|--------|
| `.....` | Alt + Tab | Switch windows |
| `-----` | Win + Tab | Task View |
| `--....` | Ctrl + Alt + Left Arrow | Release mouse capture from VM |

#### Modifier Keys (Right-side, Sticky)

Group 2 provides the right-hand modifier keys using the same patterns as their
Group 1 left-hand equivalents.

| Modifier | Pattern |
|----------|---------|
| Right Control | `-.-.` |
| Right Shift | `--...-` |
| Right Alt | `--.--` |
| Right GUI | `.--.--` |

#### Group Switch

| Action | Pattern |
|--------|---------|
| Switch to Group 1 (Keyboard) | `...-. ` |

### Group 3 — Macros

Macro patterns mirror the Group 1 alphabet so the same muscle memory that
types a letter also fires a macro phrase.  Strings are typed through the
keyboard layout writer; the host sees ordinary keystrokes.

Edit the placeholder entries in `morse_map.py` to set your own phrases.
Some example entries are pre-filled:

| Pattern | Letter equivalent | Default macro |
|---------|------------------|---------------|
| `.-` | A | `name` |
| `-...` | B | `address` |
| `---.` | C | `phone` |
| `.` | E | `email` |
| All other letter patterns | D, F–Z | *(empty — fill in)* |

Numbers 0–9 and Enter / Backspace work the same as in Group 1.

---

## TFT Display

The 240 × 135 px display shows four text rows and a pressure bar:

| Row | Content | Colour |
|-----|---------|--------|
| 1 | Active group name, e.g. `[ Keyboard ]` | Group colour (blue / green / orange / grey) |
| 2 | Morse pattern being entered, e.g. `. - . .` | Cyan |
| 3 | Last action fired, e.g. `"hello"` or `mmove 0 -1 0` | Yellow |
| 4 | Status: armed modifiers, or SLOW / FAST / RPT / DRAG | Orange |
| Bar | Pressure level — green for puff, red for sip | Green / Red |

---

## REPL Output

Every action that fires is printed to the serial console (REPL) in the format:

```
<pattern>  <action>
```

Examples:
```
. - . .   "b"
. - .     KEY 82
- -       KEY 42
- - . .   mmove 0 -1 0
. - .     ?
GROUP -> 2 (Mouse)
```

`?` means the pattern was not found in any code table.  Connect a terminal
(Mu editor, Thonny, PuTTY, or `screen`) at 115200 baud to see this output.

---

## Configuration

All tunable values are at the top of `code.py`:

| Constant | Default | Effect |
|----------|---------|--------|
| `USE_SENSOR` | `True` | `True` = LPS33HW sensor; `False` = two switches |
| `THRESH_SIP` | `5` | hPa below baseline required to detect a sip (dot) |
| `THRESH_PUFF` | `5` | hPa above baseline required to detect a puff (dash) |
| `ACCEPT_DELAY` | `0.2` | Seconds of idle after the last element before the pattern fires |
| `LONG_PRESS` | `2.0` | Seconds of continuous sip/puff to trigger a group cycle |
| `POINTS_TO_AVERAGE` | `8` | Pressure readings averaged for smoothing |
| `DOT_PIN` | `board.D5` | GPIO pin for dot switch (switch mode only) |
| `DASH_PIN` | `board.D6` | GPIO pin for dash switch (switch mode only) |
| `MOUSE_SPEED_NORMAL` | `2` | Normal speed multiplier |
| `MOUSE_SPEED_SLOW` | `1` | Slow speed multiplier |
| `MOUSE_SPEED_FAST` | `3` | Fast speed multiplier |
| `MOUSE_SPEED_FACTOR` | `2` | Additional scale applied to all mouse moves |
| `MOUSE_REPEAT_DELAY` | `0.040` | Seconds between repeat ticks (40 ms) |
| `DISPLAY_ROTATION` | `0` | Display orientation in degrees — `0` = USB on left, `180` = USB on right; also `90`, `270` |

---

## Customising the Code Tables

All key assignments live in `morse_map.py`.  The file uses a simple dictionary
structure:

```python
g1[<length>][<binary_pattern>] = <action>
```

- **length** — number of symbols (1–8)
- **binary\_pattern** — bits representing the pattern, MSB first; `0` = dot,
  `1` = dash
- **action** — one of:
  - A string like `'a'` or `'hello world'` — typed as keystrokes
  - A `Keycode` constant — pressed and released as a hardware key
  - A tuple of `Keycode` constants — all pressed simultaneously (combo)
  - A command string — `group N`, `mmove dx dy scroll`, `mclick left N`,
    `mdrag left`, `repeat`, `mslow`, `mfast`, `mreset`

### Adding a Macro (Group 3 example)

```python
g3[3][0b010] = 'John Smith'   # .-.  (R pattern)
```

### Changing a Mouse Move Step

```python
g2[2][0b11] = "mmove 0 -2 0"  # double the up-step
```

---

## Project Files

### Device files (copy these to CIRCUITPY)

| File | Purpose |
|------|---------|
| `code.py` | Main firmware — Morse state machine, USB HID, display, ESP-NOW sender |
| `morse_map.py` | All Morse code assignments for every group — edit to remap keys |
| `boot.py` | Runs once at power-on; enables USB HID keyboard and mouse |
| `receiver.py` | Wireless display mirror firmware (copy to the second #5691 receiver board) |
| `receiver_boot.py` | boot.py for the receiver board — does not enable USB HID |

### Documentation

| File | Purpose |
|------|---------|
| `AEROMORSE_BUILD_GUIDE.md` | Full build guide covering hardware options, wiring, soldering, wireless display setup, library installation, troubleshooting, and parts lists |
| `TOOLS_AND_GUIDES.md` | Reference for development tools: Mu editor, Thonny, PuTTY, CircuitPython installer |
| `Morse Code Cheat Sheet.pdf` | Printable one-page reference card for all AeroMorse patterns |

### Development tools (run on your PC, not on the device)

| File | Purpose |
|------|---------|
| `aeromorse_visualizer.htm` | Interactive browser-based cheat sheet — open in any browser, no install needed. Shows every pattern for the active group as animated dots and dashes; click any row to hear the timing. |
| `morse_map_analyzer.py` | Python 3 script that reads `morse_map.py` and reports duplicate codes, conflicts with the always-on Group 0 patterns, and unused code slots for lengths 2–7. Run with `python morse_map_analyzer.py`; output is saved to `morse_map_report.txt`. |
| `morse_map_report.txt` | Latest output from `morse_map_analyzer.py` |
| `test_pressure.py` | Diagnostic script — copy to CIRCUITPY, run via REPL; prints live pressure readings for 30 s to help set sip/puff thresholds |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| No keyboard/mouse on host | `boot.py` missing or not yet run | Copy `boot.py` to CIRCUITPY, press Reset |
| Nothing happens when sipping/puffing | Wrong library or sensor not found | Check serial REPL for error messages; confirm `adafruit_lps35hw.mpy` is in `lib/` |
| Letters misfire (e.g. `b` types `n`) | Thresholds too low — pressure not returning to neutral between dots | Increase `THRESH_SIP` / `THRESH_PUFF` |
| False triggers at rest | Thresholds too low | Increase `THRESH_SIP` / `THRESH_PUFF` |
| Multi-element patterns too slow | `ACCEPT_DELAY` too long | Decrease `ACCEPT_DELAY` (try `0.15`) |
| Pattern commits before finished | `ACCEPT_DELAY` too short | Increase `ACCEPT_DELAY` |
| Pattern shows `?` on display | Pattern not mapped in current group | Check `morse_map.py`; REPL shows the exact pattern received |
| Calibration message at startup then hangs | Sensor not found on I²C | Check STEMMA QT cable connection |
