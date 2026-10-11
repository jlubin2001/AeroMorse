# AeroMorse

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AeroMorse is an open-source CircuitPython project directed by Jim Lubin — a
ventilator-dependent quadriplegic who has used Morse code for computer access
since 1989. Inspired by [AirTalker](https://github.com/ATMakersOrg/AirTalker), it turns an Adafruit Feather
microcontroller into a USB HID keyboard and mouse that connects via USB-C and
appears to the host as a standard keyboard and mouse with no drivers required.
Works on **Windows, macOS, Linux, iPadOS, Android, and ChromeOS**.

> **Sibling project — [MorseKey](https://github.com/jlubin2001/MorseKey):** the
> same Morse engine on an **Adafruit TRRS Trinkey** (thumb-drive sized) for **AT
> switch** input — one or two switches through the headset jack, no pressure
> sensor or display. Use it when you want the smallest possible switch-based
> Morse keyboard/mouse.

**How this project was built — what's confirmed vs documented.** Jim is the
user, project lead, and source of all design decisions: hardware choices,
input-mode requirements, Morse code-set conventions, accessibility trade-offs,
and ongoing user feedback (his own and from other AAC users — Darci USB
veterans in particular). The firmware (`code.py`), the build guide, and the
comparison documents were written by **Claude Opus 4.7** (Anthropic) acting as
the coding assistant — a "vibe coding" workflow in which Jim directs and
Claude writes. Jim does not write the firmware himself, and has not personally
soldered or assembled every hardware combination listed here. Several options
— particularly some board / display / speaker combinations — are documented
from datasheets and Claude's understanding of the parts rather than from a
verified build.

**If you build a configuration, please report back via a GitHub issue —
whether it works or doesn't.** Confirmed-vs-theoretical is the single most
useful signal this project can collect right now.

Input is by **sip-and-puff** (LPS33HW pressure sensor) or **two standard AT
switches**. A short sip (or switch 1) is a **dot**; a short puff (or switch 2)
is a **dash**. A small colour screen shows the active group, the Morse pattern
as it builds, and the last action. An optional speaker beeps for every dot
and dash.

Ten groups organize all functions — `g0` plus `g1–g9`:

- **Group 0** — always-available system layer; 8-symbol patterns jump
  directly to any other group from anywhere
- **Group 1** — **Keyboard**: letters, numbers, punctuation, function keys,
  navigation, sticky modifiers (default group at boot)
- **Group 2** — **Mouse**: movement, clicks, drag, repeat, and Windows
  shortcuts
- **Group 3** — **Macro**: user-defined text strings
- **Group 4** — **Scanning**: Enter, Space and F3–F12 on the 12 shortest
  codes — for iOS / Android Switch Control
- **Group 5** — **Media**: USB HID Consumer Controls — play/pause, volume,
  mute, track skip, brightness, plus launchers for calculator, file
  explorer, browser, and mail
- **Groups 6, 7, 8** — **Placeholders** carrying Group 1's letters and numbers,
  written out line by line in `morse_map.py`, ready for you to customise
- **Group 9** — **Switch**: no Morse — a sip holds Enter and a puff holds
  Space for as long as you keep going, like two real switches (games and
  switch apps). See [AEROMORSE_SWITCH_MODE_GUIDE.md](AEROMORSE_SWITCH_MODE_GUIDE.md).
  (It was Group 7 before v1.24.)

Groups cycle with a long sip or puff. An optional **ESP-NOW wireless display**
mirrors the main screen on a second board up to ~30 m away — useful when the
sensor is mounted behind the user.

Existing **Darci USB users** can drop in
[`morse_map_darci.py`](morse_map_darci.py) to use their familiar code set.
All Morse assignments are fully customizable in `morse_map.py`. Parts cost
approximately **$50–$100** in off-the-shelf components.

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
- ✅ **Active development** — open source, customisable, and supported.
- ✅ **Optional wireless remote display** — see the user's screen from
  across the room (no equivalent on Darci).

Read **[`AEROMORSE_VS_DARCI.md`](AEROMORSE_VS_DARCI.md)** for a full
feature-by-feature comparison, an honest list of what AeroMorse cannot do
(single-switch timed input, 3-switch end-of-character mode), and a migration
checklist.

To preserve Darci muscle memory, rename **`morse_map_darci.py`** to
`morse_map.py` on the CIRCUITPY drive. All codes in that file are
transcribed verbatim from the Darci USB Owner's Manual (P/N 3001508).

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

**Board without a STEMMA QT port?** (e.g. the Feather nRF52840 Express.) Wire
the sensor to the board's I²C pins instead. If the Feather has header pins,
use a STEMMA QT cable with female sockets
([#4397](https://www.adafruit.com/product/4397)) and push it onto the pins;
if the Feather stands in a breadboard, one with male pins
([#4209](https://www.adafruit.com/product/4209)); on a bare Feather with no
header pins, solder the four wires to the pads:

| LPS33HW (STEMMA QT wire) | Feather pin |
|--------------------------|-------------|
| Red — power | **3V** |
| Black — ground | **GND** |
| Blue — SDA (data) | **SDA** |
| Yellow — SCL (clock) | **SCL** |

No config change is needed: `code.py` uses the STEMMA QT port when the board
has one and otherwise falls back to `board.I2C()` on the SDA/SCL pins
(firmware v1.4+). The serial console notes when it does.

---

## Files on the Device (CIRCUITPY drive)

The CIRCUITPY drive is the FAT filesystem that appears when the feather is
connected to a computer.

| File | Purpose |
|------|---------|
| `boot.py` | Runs once at power-on before `code.py`. Enables the USB HID Keyboard, Mouse, and ConsumerControl (media keys) devices. **Must be present or the device will not appear as a keyboard/mouse.** |
| `code.py` | Main program. Reads input, runs the state machine, executes actions, drives the display. You should not need to open this file — all tunable settings live in `config.py`. |
| `config.py` | **All user-tunable settings** — sensor thresholds, switch mode, code repeat, strong sip/puff, audio pitches, timing, etc. Edit this file (on the CIRCUITPY drive, in any text editor) to change behaviour. The Feather auto-reloads on save. |
| `morse_map.py` | All Morse code assignments for every group. Edit this file to remap keys, add macros, or change which Consumer Control codes g5 sends. |
| `macro_secrets.txt` | **Optional, private.** Holds the real values (passwords, phone, address, etc.) for any `_secret()` entries in `morse_map.py`, one `key=value` per line. Not required for the device to run — if absent, those patterns type their placeholder text. Keep it out of any copy you share. See [Storing passwords and secrets safely](#storing-passwords-and-secrets-safely). |

### Required Libraries (in `lib/` folder on CIRCUITPY)

These are pre-compiled `.mpy` files from the
[Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases).
Download the bundle matching your CircuitPython version and copy the
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

The **[Build Guide](AEROMORSE_BUILD_GUIDE.md) §9** has the full walk-through
(with Thonny, the serial console, and troubleshooting). Here's the short
version:

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
   items from the **Required Libraries** table above (from the bundle's `lib`
   folder — you don't need the whole bundle).
   - **Two are easy to miss:** `neopixel.mpy` (a bare file with no `adafruit_`
     prefix, so it sorts to the bottom of the bundle's `lib`) and
     `adafruit_lps35hw.mpy` (your sensor is the **LPS33HW**, but the driver is
     named **`lps35hw`** — the same file covers both).

### 3. Copy the AeroMorse software

Download the four AeroMorse files from the repo — **green `< > Code` button →
Download ZIP**, then unzip. Copy these from the ZIP's **root** to the **root**
of CIRCUITPY:

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
- the AeroMorse version (e.g. **v1.15**),
- the CircuitPython version (e.g. **CP 9.2.9**).

The device is now ready. Your **first** sip, puff or switch press only closes
the start screen — it types nothing — and the display changes to
**[ KEYBOARD ]**. From then on every sip/puff counts. (To see the start screen
again later, use the Mouse-group `version` command, `...-`.)

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

Holding a sip or puff for the `LONG_PRESS` duration cycles through groups 1–9
instead of recording an element (Group 0 is skipped — its 8-symbol patterns
remain available in the background at all times):

| Long press | Effect |
|------------|--------|
| Long sip | Cycle groups **backward** (… 3 → 2 → 1 → 9 → 8 → 6 …) |
| Long puff | Cycle groups **forward**  (1 → 2 → … → 7 → 8 → 1 …) |

The **Switch group (Group 9) is skipped** when cycling: long presses don't
change group inside Switch mode (games need long holds), so cycling into it
would leave you stuck. Enter Switch mode on purpose with `.-------`.

With ten groups, cycling all the way around is slow — use the 8-symbol
**Group 0 jump codes** below to go straight to any group from anywhere.

---

## Groups

The device has ten groups: g0 (always-on) plus g1–g9.  The active group
determines which code table is used for pattern lookup.  **Group 0 is always
checked first**, regardless of the active group — its 8-symbol patterns are
available at all times.

### Group 0 — Always Available (Group Switch)

These 8-symbol patterns work in any group and jump directly to the named
group.  The codes use a "count of trailing dashes" scheme: 8 dots = g1, then
add trailing dashes to reach the higher groups.

| Pattern | Trailing dashes | Destination |
|---------|-----------------|-------------|
| `........` | 0 | Group 1 — Keyboard |
| `.......-` | 1 | Group 4 — Scanning / Switch Control |
| `......--` | 2 | Group 5 — Media (USB HID Consumer Controls) |
| `.....---` | 3 | Group 6 — placeholder |
| `....----` | 4 | Group 3 — Macros |
| `...-----` | 5 | Group 7 — placeholder |
| `..------` | 6 | Group 8 — placeholder |
| `.-------` | 7 | Group 9 — **Switch** (sip holds Enter, puff holds Space) |
| `--------` | 8 | Group 2 — Mouse / Shortcuts |
| `----....` | (alias) | Group 4 — Scanning / Switch Control (second shortcut) |

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
| ↖ Up-Left | — | `--...` |
| ↗ Up-Right | — | `----.` |
| ↙ Down-Left | — | `.----` |
| ↘ Down-Right | — | `...--` |
| Scroll ↑ | — | `.....-` |
| Scroll ↓ | — | `...-..` |

Mouse speed is controlled by three modes:

| Mode | Speed multiplier | How to activate |
|------|-----------------|-----------------|
| Normal | ×2 | Default; also what you return to when `mslow` or `mfast` is sent a second time |
| Slow | ×1 | `mslow`, pattern `--..` (send again for Normal) |
| Fast | ×3 | `mfast`, pattern `--.-` (send again for Normal) |

The effective pixels moved per step = **raw direction value × speed × 2**.

#### Mouse Buttons

| Action | Pattern |
|--------|---------|
| Left click | `.-` |
| Right click | `.--` |
| Double-click left | `..-` |
| Double-click right | `..--` |
| Drag: hold the left button / let it go | `-.` (see *Drag* below) |

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

Dragging with a normal mouse means *press the button, move, let go*. On
AeroMorse the drag pattern `-.` does the pressing and the letting go for
you: send it once and the left button is **held down**; send it again and
the button is **released**. Everything you do with the mouse in between
happens with the button held.

**How to drag something:**

1. Move the pointer onto the thing you want to drag — a window's title
   bar, a file, a scrollbar's sliding block, the start of some text.
2. Send `-.` — the button is now held. The status row shows **DRAG**.
3. Move the pointer to where you want it to go, with the normal movement
   patterns. Repeat (`.`) works here too, for a long glide.
4. Send `-.` again — the button is released and the thing is dropped.
   **DRAG** disappears from the status row.

**What it is for:**

| To do this | Grab here (step 1) | Then move |
|------------|--------------------|-----------|
| Move a window | its title bar | to the new place |
| Resize a window | its edge or corner | outward or inward |
| Move a file or icon | the file or icon | onto the folder or spot |
| Select text | just before the first character | to just after the last |
| Select several files | an empty spot beside them | across them (draws a box) |
| Scroll with a scrollbar | the sliding block | up or down |
| Move a slider (volume, video position) | the slider knob | along the track |

**Good to know:**

- **Use small steps near the end.** Slow speed (`mslow`, `--..`) makes it
  much easier to stop exactly where you want before releasing.
- **Always finish with `-.`.** Until you do, the computer believes the
  button is still pressed, and anything the pointer passes over may be
  selected or moved. If the pointer seems to be selecting things on its
  own, look for **DRAG** on the status row and send `-.`.
- **Changing group does not release the button.** The drag is still on
  when you come back to the Mouse group.
- **A click ends the drag** (v1.28+). If you click while **DRAG** is
  showing, the held button is let go first, **DRAG** disappears, and then
  the click is made as usual. So a drag started by accident does not get
  in the way of your next click. (In earlier versions the click let the
  button go but **DRAG** stayed on the status row until `-.` was sent.)
- **To cancel a drag** in most Windows programs, press Escape (`--....`) before
  releasing, then send `-.`.
- A plain **click** is often enough and less work: clicking the empty part
  of a scrollbar scrolls a page, and the scroll patterns move a page
  without aiming at anything.

**Right-button drag.** The firmware also accepts `mdrag right`, which holds
the right button instead (in Windows, dropping a file this way offers a
Copy / Move menu). It has no pattern in the supplied map; to add one, put a
line such as this in the Group 2 section of `morse_map.py`:

```python
g2[3][0b110] = "mdrag right"       # --.     toggle right-button drag
```

#### Other Controls

| Action | Pattern | Effect |
|--------|---------|--------|
| `mslow` | `--..` | Toggle slow-step mouse speed (slow ↔ normal) |
| `mfast` | `--.-` | Toggle fast mouse speed (fast ↔ normal) |
| Find pointer | `..-.` | Taps Ctrl by itself. If Windows' *Show location of pointer when I press the CTRL key* is on (Control Panel → Mouse → Pointer Options), circles are drawn round the pointer. Does nothing if that option is off |
| Centre pointer | `.-.` | Sends Ctrl+Alt+Home, which a small AutoHotkey script turns into "put the pointer in the middle of the screen". Does nothing unless `AeroMorse.ahk` is running — see Build Guide Appendix G |
| `version` | `...-` | Show the start-up screen again — device name, AeroMorse version, CircuitPython version — until the next sip/puff |
| `devicereset` | `-.-..-.` | Restart the device (same as unplug/replug). Switches to Group 1 and asks **CONFIRM RESET Y/N?** — type `y` (`-.--`) to restart; anything else, or 30 s with no input, cancels and returns to Mouse. Nothing is typed to the computer while it asks |

The three speeds themselves are set in `config.py` (`MOUSE_SPEED_NORMAL`,
`MOUSE_SPEED_SLOW`, `MOUSE_SPEED_FAST`).

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

#### Page Scroll

A scrollbar **track** click pages or line-scrolls depending on the app; these
keys page in almost any app regardless of cursor position — usually the least
effort for moving through a long document.

| Action | Pattern | Effect |
|--------|---------|--------|
| Page Down | `-..` | Scroll down one full page |
| Page Up | `-.-` | Scroll up one full page |
| Home | `.......` | Jump to the top of the page or the start of the line — the same code as in the Keyboard group |

#### Windows Shortcuts

| Shortcut | Pattern | Action |
|----------|---------|--------|
| `.....` | Win + Tab | Task View |
| `-----` | Alt + Tab | Switch windows |
| `--..--` | Ctrl + Alt + Left Arrow | Release mouse capture from VM |
| `---..-.` | Tab | Tab |
| `--....` | Escape | Escape |
| `--.....` | F5 | Refresh |

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

Edit the placeholder entries in `morse_map.py` to set your own phrases. Six
letter patterns come pre-filled as examples. The personal ones pull their real
value from `macro_secrets.txt` via `_secret()` (see
[Storing passwords and secrets safely](#storing-passwords-and-secrets-safely)),
so a shared copy of `morse_map.py` never leaks them:

| Pattern | Letter | Default macro (as shipped in `morse_map.py`) |
|---------|--------|----------------------------------------------|
| `.-`   | A | `name`      — `_secret('name', 'Your Name')` |
| `-...` | B | `address`   — `_secret('address', …)` |
| `---.` | C | `phone`     — `_secret('phone', …)` |
| `.`    | E | `email`     — `_secret('email', …)` |
| `.--.` | P | `password1` — `_secret('password1', …)` |
| `.--`  | W | `wifi`      — `_secret('wifi', …)` |
| `..-`  | U | `unlock` — type your PIN to unlock PIN-locked secrets ([details](#pin-locked-secrets-macro_secretsenc)) |
| `.-..` | L | `lock` — lock PIN-locked secrets again |
| All other letters (D, F–K, M–O, Q–T, V, X–Z) | | `'phrase'` placeholder — fill in your own |

Digits `0`–`9` type the number; `.-.-` = Enter, `--` = Backspace.

### Group 4 — Scanning (Switch Control on iOS / Android)

Group 4 maps the **12 shortest Morse patterns** to Enter, Space and
F3–F12, so the least-effort codes drive the most-used scan actions — a
single sip is **Enter** (Select) and a single puff is **Space** (Next).
This makes AeroMorse usable as a **Switch Control** scanning input on iOS
and Android, where these keys act as switch actions. (Before v1.14 the
single sip / puff were F1 / F2 — re-assign Select and Next in the
device's switch settings if it was set up that way.) The `....` pattern is set to `h`
(labelled "Home"); the remaining letters and numbers are inherited from
Group 1 as a placeholder and can be customised.

| Key | Pattern | Key | Pattern | Key | Pattern |
|-----|---------|-----|---------|-----|---------|
| Enter | `.` | F5 | `-.` | F9 | `.-.` |
| Space | `-` | F6 | `--` | F10 | `.--` |
| F3 | `..` | F7 | `...` | F11 | `-..` |
| F4 | `.-` | F8 | `..-` | F12 | `-.-` |
| Home (`h`) | `....` | | | | |

> **Setting it up on a device:** see the
> **[AeroMorse Switch Control Guide](AEROMORSE_SWITCH_CONTROL_GUIDE.md)** for
> which OS action each F-key triggers and step-by-step setup for **iOS Switch
> Control**, **Android Switch Access**, and **Samsung Universal Switch**.

### Group 5 — Media (USB HID Consumer Controls)

Group 5 sends USB HID Consumer Control codes — media playback, volume,
mute, track skip, brightness, eject, and application launch.
The codes route through a dedicated `ConsumerControl` HID device
(enabled in `boot.py`), so they reach the host as standard media-keyboard
keys that every modern OS understands.

**Media — 12 shortest patterns (1–3 symbol):**

| Pattern | Action | Pattern | Action |
|---------|--------|---------|--------|
| `.` | Play / Pause | `...` | Stop |
| `-` | Mute | `..-` | Rewind |
| `..` | Volume Down | `.-.` | Fast Forward |
| `--` | Volume Up | `.--` | Brightness + |
| `-.` | Previous Track | `-..` | Brightness − |
| `.-` | Next Track | `-.-` | Eject |

**Application Launch (4-symbol patterns; first-letter mnemonics):**

| Pattern | ITU letter | Action |
|---------|-----------|--------|
| `-.-.` | C | **C**alculator — `AL_CALCULATOR` |
| `..-.` | F | **F**ile explorer — `AL_LOCAL_MACHINE_BROWSER` |
| `-...` | B | **B**rowser — `AL_INTERNET_BROWSER` |
| `.-..` | L | mai-**L** — `AL_EMAIL_READER` |

The mnemonic letters above are **standard ITU** Morse. Note that g1's own
`c` is the non-standard `---.` (because `-.-.` is freed there for
`LEFT_CONTROL`), so `-.-.` = C applies to the ITU letter, not to g1's
mapping.

These codes work on **any** `adafruit_hid` bundle. Older bundles don't
define the `AL_*` constants, so `morse_map.py` resolves each one by name and
falls back to its raw usage ID from the USB HID Usage Tables, Consumer Page
(`0x0C`). Those IDs are fixed by the spec, so nothing is skipped and no
warning is needed.

> **System `SLEEP` and `POWER` are deliberately not mapped.** Their
> mnemonic patterns would be `--..` (Z-z-z) and `.--.` (**P**ower), but a
> 4-symbol pattern is too easy to hit by accident in a group whose 1–3
> symbol patterns are routine media keys — and an unintended shutdown is
> far more disruptive than a stray volume change. `--..` and `.--.`
> therefore keep the placeholder letters `z` and `p`. Add them in
> `morse_map.py` if you want them, ideally on a longer pattern.

Whether each code actually does anything is up to the host OS — Windows
generally honours all four; macOS and Linux desktops vary. Many more such keys
exist — browser back / forward / refresh, search, copy / paste, zoom and
others — and any of them can be added to any group with one line, e.g.
`_cc('AC_BACK', 0x224)`. See **Build Guide Appendix J** for a table of the
useful ones and what to expect from them. The remaining
letters and numbers in g5 are inherited from Group 1 as a placeholder and
can be customised.

### Group 9 — Switch (two-button hold mode)

> **Changed in v1.24:** Switch mode moved from Group 7 to **Group 9**, so the
> one group without Morse is the last one. Its Group 0 code is now `.-------`
> (it was `...-----`). To keep it on Group 7, set `SWITCH_GROUP = 7` in
> `config.py`.

In Group 9 AeroMorse stops decoding Morse and behaves like **two plain
switches**: a **sip holds Enter** and a **puff holds Space** from the moment
you start until you stop — the way switch-accessible games and apps expect
(e.g. [Benny's Hub](https://narbehouse.github.io/bennyshub/index.html):
Space = move, Enter = select, and games like NARBE Kart that need a key
*held*). Hard or long sips/puffs never change group here. It returns to
Keyboard **by itself after 20 s** with no sip or puff (or hold one puff for
5 s). Settings: `SWITCH_GROUP`, `SWITCH_SIP_KEY`, `SWITCH_PUFF_KEY`,
`SWITCH_IDLE_EXIT_S`, `SWITCH_EXIT_PUFF_S`, `SWITCH_EXIT_GROUP` in
`config.py`. Full guide: [AEROMORSE_SWITCH_MODE_GUIDE.md](AEROMORSE_SWITCH_MODE_GUIDE.md).

### Groups 6, 7, 8 — Placeholders

Groups 6, 7 and 8 carry Group 1's letters and numbers on the same codes, so
the same muscle memory works while you decide what each group is for. Since
v1.24 they are **written out line by line** in `morse_map.py` (before, a
hidden helper copied them), so to make a code do something else you just
change what is between the quotes on its line — a phrase, `_secret('mykey')`,
a `Keycode`, an app launcher or a command string. Groups 4 and 5 list their
remaining letters and numbers the same way. Reach each group with its Group 0 jump code (table above).

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

**At start-up** row 1 shows the device's name (`DEVICE_NAME` in `config.py`,
e.g. `AeroMorse Green`) in white, row 3 the firmware version (e.g. `v1.11`) and
row 4 the CircuitPython version (e.g. `CP 9.2.9`), so you can see at a glance
which device it is and whether it's up to date. A wireless display mirrors it.
The press that closes the start-up screen is **only** a dismiss — it types
nothing and doesn't change group. The Mouse-group `version` command (`...-`)
brings the screen back. The
first sip, puff or switch press switches to the normal display above.

> **No screen on your board?** Set `USE_DISPLAY = False` in `config.py`. The
> device then skips this local display but keeps typing over USB and keeps
> broadcasting these same four rows to a wireless receiver (see
> `USE_WIRELESS_DISPLAY`). A missing screen is auto-detected too, so a screenless
> board won't crash even if the flag is left on. Handy for a screenless ESP-NOW
> *sender* that mirrors to a #5691 (or MagTag) *receiver*.

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
**Careful:** Thonny interrupts the running program when it connects, and
Ctrl+C in any terminal does the same — AeroMorse then stops typing until it
is restarted (replug the USB cable). If AeroMorse is your only way to use the
computer, read the warning in Build Guide §9.3 first.

---

## Configuration

All tunable values live in **`config.py`** (not `code.py`). Open it from the
CIRCUITPY drive in any text editor, find the setting you want, change the value, save — the Feather
auto-reloads with the new value. Each setting has a comment block above it
explaining what it does. The same Key Settings table also appears in
**§10 Configuration** of `AEROMORSE_BUILD_GUIDE.md` — all three sources
(table below, build guide §10, and `config.py` itself) are kept in sync.

### Input — sensor / switches / thresholds

| Constant | Default | Effect |
|----------|---------|--------|
| `USE_SENSOR` | `True` | `True` = LPS33HW sensor (sip-and-puff); `False` = two AT switches on D5/D6 |
| `THRESH_SIP` | `5` | hPa below baseline required to detect a sip (dot). Raise to `8`/`10` if getting false triggers; lower to `3` if light sips are missed |
| `THRESH_PUFF` | `5` | hPa above baseline required to detect a puff (dash). Same tuning rule |
| `THRESH_SIP_STRONG` | `15` | **Sensor mode only.** hPa below baseline at which a strong sip is detected; fires `STRONG_SIP_ACTION` once per press. Ignored in switch mode |
| `THRESH_PUFF_STRONG` | `15` | Same as above but for puff |
| `STRONG_OFF_IN_GROUPS` | `(4,)` | Groups where strong sip/puff is switched off: a hard sip/puff there counts as a normal dot/dash. Default `(4,)` = Scanning, so a hard sip/puff (Enter/Space) never jumps you out of Switch Control. List several like `(4, 3)`; `()` = strong gestures on in every group |
| `SWITCH_GROUP` | `9` | Group that acts as **two plain switches** (no Morse): sip holds `SWITCH_SIP_KEY`, puff holds `SWITCH_PUFF_KEY` for as long as you keep going. `0` = no Switch group. See `AEROMORSE_SWITCH_MODE_GUIDE.md` |
| `SWITCH_SIP_KEY` | `"ENTER"` | Key held while sipping in the Switch group (a Keycode name) |
| `SWITCH_PUFF_KEY` | `"SPACE"` | Key held while puffing in the Switch group |
| `SWITCH_IDLE_EXIT_S` | `20` | Seconds with no sip/puff before the Switch group returns to `SWITCH_EXIT_GROUP` by itself. `0` = never |
| `SWITCH_EXIT_PUFF_S` | `5.0` | Or hold one puff this many seconds to leave the Switch group |
| `SWITCH_EXIT_GROUP` | `1` | Group you return to when leaving the Switch group (1 = Keyboard) |
| `SWITCH_COUNTDOWN_S` | `10` | (v1.21+) For the last this-many seconds before the Switch group is left the screen counts down, e.g. `MOUSE IN 5` — both for the idle exit and while holding the long exit puff. Any sip/puff clears it. `0` = no countdown |
| `STRONG_SIP_ACTION` | `""` | Command string fired on a strong sip — e.g. `"group 2"` to jump to Mouse. Empty string = disabled. **Switch mode:** triggered by a long-press of the DIT-side switch instead of pressure peak; overrides `LONG_PRESS_CYCLES_GROUP` on that switch |
| `STRONG_PUFF_ACTION` | `""` | Same as above but for puff / DAH-side switch in switch mode |
| `REPEAT_SPLIT_PCT` | `0` | Split on a dip (v1.18+): a sip/puff that drops below this % of its peak and then climbs again by 1 hPa counts as two. Fixes two quick sips/puffs running together. Try `60`; `0` = off |
| `DIAG_LOG_S` | `0` | Diagnostics (v1.19+): every this many seconds one `DIAG ...` line of timing figures (loop speed, longest blind moment, screen / wireless / key-send time, sensor reading rate, shortest sip/puff and rest) goes to the USB serial log. The first / worst / last line are saved on `devicereset`, and automatically every 5 minutes while you type (so they survive an unplug); the next run prints them as `DIAG PREV ...` (and the run before that as `DIAG PREV2 ...`). For tracking down "types badly until restarted". `0` = off; try `10` |
| `DOT_PIN` | `board.D5` | GPIO pin for dot switch (switch mode only) |
| `DASH_PIN` | `board.D6` | GPIO pin for dash switch (switch mode only) |

### Input mode — 1 / 2 / 3 switch

| Constant | Default | Effect |
|----------|---------|--------|
| `SWITCH_MODE` | `2` | `1` = single-switch timed; `2` = paddle (dot + dash); `3` = paddle + explicit Accept. See "Input modes" in build guide §10 for the full model |
| `ONE_SWITCH_INPUT` | `"dot"` | 1-switch mode only — `"dot"` uses the sip / D5 input; `"dash"` uses the puff / D6 input |
| `ONE_SWITCH_DOT_MS` | `200` | 1-switch mode only — press ≤ this many ms is a dot; longer is a dash; ≥ `LONG_PRESS`×1000 cycles group |
| `THIRD_SWITCH_GESTURE` | `"long_dash"` | 3-switch mode only — `"long_dash"` makes long-puff the Accept switch; `"long_dot"` makes long-sip the Accept switch |

### Code repeat (Darci-style hold-to-repeat)

| Constant | Default | Effect |
|----------|---------|--------|
| `CODE_REPEAT` | `False` | `True` enables hold-to-repeat — while DIT/DAH is held, one symbol fires per `DOT_REPEAT_MS` / `DASH_REPEAT_MS`. Release ends the stream. Only honoured when `SWITCH_MODE = 2` |
| `DOT_REPEAT_MS` | `200` | ms between auto-repeated dots (`CODE_REPEAT` only) |
| `DASH_REPEAT_MS` | `600` | ms between auto-repeated dashes (`CODE_REPEAT` only — conventionally 3 × dot) |
| `CODE_REPEAT_MAX` | `8` | Cap on symbols per held stream — prevents buffer overflow on a forgotten hold |
| `LONG_PRESS_CYCLES_GROUP` | `True` | `False` disables the long-press group cycle gesture (DIT-side = cycle back, DAH-side = cycle forward). Switch groups via g0 Morse patterns instead. Recommended `False` alongside `CODE_REPEAT = True` |

### Timing

| Constant | Default | Effect |
|----------|---------|--------|
| `ACCEPT_DELAY` | `0.3` | Idle pause (seconds) after the last element before the pattern fires. Lower (0.2) for fast users; higher (0.7) for sip-and-puff users with slower breath rhythm. In 3-switch mode this is a safety-net timeout |
| `LONG_PRESS` | `1.0` | Hold time (seconds) for the long-gesture (cycle / Accept). Raise if accidentally triggering |

### Audio (speaker pitches)

| Constant | Default | Effect |
|----------|---------|--------|
| `BEEP_DOT_FREQ` | `1200` | Pitch in Hz for dot (sip) beeps — higher pitch |
| `BEEP_DASH_FREQ` | `800` | Pitch in Hz for dash (puff) beeps — lower pitch |

### Mouse

| Constant | Default | Effect |
|----------|---------|--------|
| `MOUSE_SPEED_NORMAL` | `2` | Normal speed multiplier |
| `MOUSE_SPEED_SLOW` | `1` | Slow speed multiplier |
| `MOUSE_SPEED_FAST` | `3` | Fast speed multiplier |
| `MOUSE_SPEED_FACTOR` | `2` | Additional scale applied to all mouse moves |
| `MOUSE_REPEAT_DELAY` | `0.040` | Seconds between repeat ticks (40 ms) |
| `MOUSE_CLICK_MOD_DELAY` | `0.030` | Seconds to let an armed modifier settle before and after a click. Keyboard and mouse are separate USB interfaces, so without this delay the host can see a plain click instead of Ctrl+click. Raise to `0.05` if modified clicks are unreliable |
| `MOUSE_CLICK_KEEPS_MODS` | `True` | `True` = an armed modifier stays armed across mouse clicks, so **Ctrl+click multi-select** works — arm Ctrl once, click each file, then toggle Ctrl off. `False` = one-shot (modifier clears after a single click) |
| `MOUSE_CLICK_HOLD` | `0.060` | Seconds the button is held down per click. A zero-length click (press+release together) is ignored by **Windows scrollbar tracks** and some controls; ~60 ms registers reliably. Raise if scrollbar/track clicks still don't take |
| `MOUSE_CLICK_GAP` | `0.040` | Seconds between the two clicks of a double-click |
| `NO_REPEAT_KEYS` | `("PAGE_UP", "PAGE_DOWN")` | Keys (by `Keycode` name) that must never auto-repeat — pressing `repeat` right after one does nothing. Page keys are excluded so an accidental repeat doesn't scroll far past your place. Add e.g. `"HOME"`, `"END"`, `"ESCAPE"`, `"TAB"`. A key combination can be listed too (v1.20+): join the names with `+`, e.g. `"ALT+TAB"` — that blocks exactly that combination, while the same keys on their own are unaffected. Arrow keys are intentionally omitted — arrow + repeat is a normal way to scroll |

### Display / wireless

| Constant | Default | Effect |
|----------|---------|--------|
| `DEVICE_NAME` | `"AeroMorse"` | Name the computer shows for this device over USB (e.g. `"AeroMorse Green"` in Windows *Bluetooth & devices*, instead of "Feather ESP32-S3 Reverse TFT"), also shown on the screen at start-up. Up to 40 plain characters, in quotes. Applies after an unplug/replug. (It sits at the top of `config.py`.) If it's left as the default `"AeroMorse"`, a label file on the drive is used instead — `AeroMorse-Green.txt` → "AeroMorse Green". A **wireless display** board (no `config.py`) is named from its label file too, e.g. `AeroMorse-Display.txt`, or "AeroMorse Display" if it has none |
| `USE_DISPLAY` | `True` | `True` = this board has a built-in screen (the default #5691 Reverse TFT). Set `False` on a board with **no screen** (e.g. a screenless ESP-NOW sender): the device still types over USB and still broadcasts to a wireless receiver — only the local screen is skipped. A missing `board.DISPLAY` is also **auto-detected**, so a screenless board won't crash even if this is left `True` Also set `False` on a board that **has** a screen when you only watch the wireless display (v1.22+): the built-in screen is blanked and its backlight switched off, removing screen-drawing pauses of 60–100 ms that can swallow a quick sip or puff (the backlight comes back on if the program stops with an error) |
| `DISPLAY_BRIGHTNESS` | `1.0` | Screen backlight, `0.1` (dim) to `1.0` (full). Takes effect when `config.py` is saved. Never goes below `0.1`, so the screen can't be blacked out by mistake. Useful when one board's screen is brighter than another's, or at night |
| `DISPLAY_ROTATION` | `0` | Display orientation in degrees — `0` = USB on left, `180` = USB on right; also `90`, `270` |
| `USE_WIRELESS_DISPLAY` | `False` | `True` enables the ESP-NOW broadcast for an Option W1 / W2 receiver. Default is off — flip to `True` only when you actually have a receiver paired. Adds ~80–100 mA when on |
| `KEYBOARD_LAYOUT` | `"US"` | Keyboard layout the **computer** is set to. If symbols come out wrong on a non-US computer, copy that layout's file into `/lib` and name it here, e.g. `"win_uk"` (v1.28+; Build Guide Appendix I). Falls back to US if the file is missing |
| `PC_DISPLAY` | `False` | `True` = also report the display over USB to the **AeroMorse Display** window on the computer (v1.26+). No extra hardware |
| `USE_SPEAKER` | `True` | `False` = the device's own speaker / buzzer stays silent (v1.29+). Sound through the computer (`PC_SOUND`) is separate and carries on. |
| `PC_SOUND` | `False` | `True` = the AeroMorse Display program also plays the beeps through the **computer's** speakers (v1.27+) — audio feedback with no speaker on the device. Needs `PC_DISPLAY = True` |

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
    `mdrag left`, `repeat`, `mslow`, `mfast`, `unlock`, `lock`, `version`,
    `devicereset` (`mreset` was removed in v1.12 — use `devicereset`)

### Adding a Macro (Group 3 example)

```python
g3[3][0b010] = 'John Smith'   # .-.  (R pattern)
```

### Storing passwords and secrets safely

Group 3 macros are perfect for passwords and logins — but a password
written directly into `morse_map.py` would be exposed the moment you
share that file (for help, in the repo, or in a zip of your drive).

AeroMorse keeps secrets in a **separate plain-text file that is never
shared**, `macro_secrets.txt`, using a deliberately foolproof format —
**one secret per line, `key=value`** (no quotes, commas, colons or
braces, so an editing slip can't break anything):

1. In your work folder (see the [Usage Guide](AEROMORSE_USAGE_GUIDE.md) for
   the full first-time steps), copy **`macro_secrets.example.txt`** to
   **`macro_secrets.txt`** and put your real values in it:
   ```
   password1=my-real-password
   wifi=my-wifi-key
   ```
2. In `morse_map.py`, a pattern pulls a value in by key, with a harmless
   fallback:
   ```python
   g3[4][0b0110] = _secret('password1')  # P
   ```

**Why this is safe:**
- If you ever share `morse_map.py` *without* `macro_secrets.txt`, the
  secret macros type the placeholder text — never your real password.
  `macro_secrets.txt` is `.gitignore`d and is the **only** file holding
  your secrets in plain text.
- **A typo can't take the device down.** If one line in
  `macro_secrets.txt` is malformed, only *that* secret falls back to its
  placeholder — every other secret keeps working, and `morse_map.py`
  always loads. (This matters: `morse_map.py` may be your only means of
  computer access.) A missing or unreadable file just means every secret
  shows its placeholder.

**Format rules:**
- One secret per line: `key=value`. No quotes needed; blank lines and
  lines starting with `#` are ignored.
- Save as **UTF-8** (in Notepad++: Encoding → **UTF-8**, *not*
  “UTF-8-BOM”). A stray byte-order mark is tolerated, but plain UTF-8 is
  cleanest.

**What the value (password) may contain:**
- ✅ Almost anything, with **no escaping** — `=`, `#`, quotes `' "`,
  backslash `\`, and symbols like `@ ! $ % & * ( ) + / ?` all work
  literally. Only the *first* `=` on the line splits key from value, so a
  value may contain further `=` signs (`k=a=b` → value `a=b`). A `#` is
  only special at the very start of a line.
- ✅ Interior spaces are kept (`name=Your Name`).
- ⚠ **Leading and trailing spaces are trimmed.** `pw=  x  ` stores `x`.
  (The trim is deliberate — it removes the invisible carriage-return
  Windows adds to each line.) So a value that must *begin or end with a
  space* can't be stored as-is.
- ⚠ **No newlines** — a value is a single line, so it can't span lines.

**What the key (the name before `=`) may contain:**
- ✅ Letters, digits, and `_` (e.g. `email_pw`, `bank_pin`, `wifi2`).
  The key must match the `_secret('key', …)` spelling in `morse_map.py`
  exactly.
- ❌ **No `=`** (the first `=` ends the key), and a key **can't start with
  `#`** (that line is read as a comment). Avoid spaces in keys.

**Works in any group, not just Group 3.** `_secret()` reads from the same
`macro_secrets.txt` no matter which group calls it, so you can use
`_secret('key', 'placeholder')` on any assignment in **g1–g9** — e.g.
dedicate a placeholder group like g6 to logins:

```python
g6[4][0b0110] = _secret('bank_login')  # P
```

- **Keys are shared across the whole file** — `_secret('email', …)` in
  g3 and in g6 both read the same `email=` line. Use distinct key names
  (`email`, `work_email`) if you want different values.
- In **g4–g8** the letters and numbers are ordinary lines in the file: to put
  a secret on a letter's code, replace the quoted letter on that line with
  `_secret('mykey')`.
- **Short form (v1.24+):** `_secret('mykey')` is enough. The second argument
  (the text typed when the key isn't set) is optional; without it the
  pattern types `(set mykey in AeroMorse Secrets)`.
- The cheat sheet shows a 🔒 lock badge with the key name for
  `_secret(...)` in **any** group, so secrets stay hidden when printed.

> **If you send someone a copy of your whole CIRCUITPY drive, delete
> `macro_secrets.txt` from the copy first.** The `.gitignore` protects
> git and one-file sharing; a full-drive copy still needs that one
> manual step.

#### PIN-locked secrets (`macro_secrets.enc`)

`macro_secrets.txt` is plain text: anyone who plugs the device into a
computer can open it. From **v1.5** you can instead keep your secrets
**encrypted**, like a password manager, and unlock them with a PIN you
type in Morse.

**Set it up (on your PC):**
1. Double-click **`AeroMorse Secrets.exe`** in your work folder (or run
   `python aeromorse_secrets.py`). It opens the secrets in that folder —
   your existing `macro_secrets.txt` is imported automatically.
2. Edit the `key=value` lines (same rules as above), type a **PIN** twice,
   and click **Save (encrypt)**. This writes `macro_secrets.enc` and offers
   to delete the plain `macro_secrets.txt` (recommended). It also warns you
   about any `_secret()` key in `morse_map.py` that has no value.
3. Click **Copy to device**. It copies the file to the CIRCUITPY drive and
   offers to delete the plain `macro_secrets.txt` there too.

**Use it (on the device):**
- The device starts **locked** at every power-up.
- Use any secret pattern (e.g. Macro `P`) and the screen shows
  **ENTER PIN + ENTER**. Type the PIN with the normal **Group 1**
  letters/digits, then **Enter** (`.-.-`). The screen shows `PIN ****`;
  **nothing you type while entering the PIN reaches the computer**.
- Right PIN → **UNLOCKED** (about 1.5 s) and it types the secret you asked
  for. The status line shows `UNLOCKED` while secrets are open — only in groups whose map has
  `_secret()` entries (v1.19+), so it doesn't clutter the other groups.
- Wrong PIN → **WRONG PIN**, stays locked; just use the pattern again.
- **Esc**, or **Backspace** with nothing typed, cancels. Entry also
  cancels itself after 60 s of no input.
- While the PIN is being typed you **stay in Group 1**: a strong sip/puff
  counts as a normal dot/dash, and long presses and group codes don't change
  group. (The same applies to the `devicereset` "CONFIRM RESET Y/N?" prompt.)
- Macro **`U`** (`..-`) unlocks without typing anything; Macro **`L`**
  (`.-..`) locks again. Unplugging or restarting always locks.
- Optional idle auto-lock: `SECRETS_AUTOLOCK_MIN` in `config.py`
  (0 = off).

**Good to know:**
- The PIN is **not case-sensitive**. Use **8 or more** letters/digits: the
  file is strongly encrypted, but a short PIN could be guessed by someone
  who copies the file and tries PINs on a computer.
- **Forgot the PIN?** Only the secrets are affected — keyboard, mouse and
  everything else keep working. Make a new file with the tool.
- Secret values are never shown on the screen, the wireless display or the
  USB log — only `SECRET name`. (Before v1.5 the first 16 characters were
  shown.) While a PIN is typed, the wireless display shows `*` instead of
  dots and dashes.
- If both files are on the device, the encrypted one is used and the USB log
  warns that the plain file should be deleted; the validator warns too.
- Needs CircuitPython's built-in `aesio` module (present on the ESP32-S3
  Feathers). `morse_map.py`, `code.py`, `config.py` and `boot.py` must all be
  **v1.5 or later**.

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
| `config.py` | **All user-tunable settings** — sensor thresholds, switch mode, code repeat, audio pitches, timing, etc. Edit this file instead of `code.py`. |
| `morse_map.py` | All Morse code assignments for every group — edit to remap keys |
| `macro_secrets.example.txt` | Template for your **private** secret macros (passwords, personal details), with a line for every key the standard `morse_map.py` uses. Copy it to `macro_secrets.txt` in your work folder, fill in `key=value` lines, then encrypt it with AeroMorse Secrets — step by step in the [Usage Guide](AEROMORSE_USAGE_GUIDE.md). |
| `macro_secrets.txt` | **Your real passwords / secrets — never share, never committed** (git-ignored). Plain `key=value` lines. Created by you from the `.example` template. If absent or a line is bad, that secret macro just types a placeholder. |
| `macro_secrets.enc` | **Optional, recommended instead of `macro_secrets.txt`** — the same secrets **encrypted**, unlocked with a PIN typed in Morse. Made with `AeroMorse Secrets.exe` (git-ignored). See [PIN-locked secrets](#pin-locked-secrets-macro_secretsenc). |
| `morse_map_darci.py` | Drop-in alternative code map for **Darci USB users** — rename to `morse_map.py` on CIRCUITPY to use Darci's exact code set |
| `boot.py` | Runs once at power-on. **Same file on every board** — auto-detects its role from whether `morse_map.py` is present on the drive. Sender → enables USB HID (Keyboard, Mouse, Consumer Control). Receiver → leaves HID off, and optionally hides CIRCUITPY + serial from the host if an empty `/hide` file is present on the drive. |
| `receiver.py` | Wireless display mirror firmware — Option W1 (second #5691 colour TFT). 240×135 colour display with full live preview. Copy as `code.py` to the receiver board. |
| `receiver_magtag.py` | Wireless display mirror firmware — Option W2 (Adafruit MagTag #4800 e-ink). Bigger, glance-able from across a room, but no live pattern preview / pressure bar due to e-ink refresh limits. **Requires CircuitPython 10.x on the MagTag.** Copy as `code.py` to the MagTag. |
| `receiver_config.py` | **Settings for the wireless display board only** (either type): `ESPNOW_CHANNEL` (must match the main device's `config.py`), and for the colour display `DISPLAY_BRIGHTNESS`, `DISPLAY_ROTATION`, `SLEEP_AFTER_S`; for both `NO_SIGNAL_S`, `AUTO_RESET_S`; for the MagTag `REFRESH_MIN_S`. Copy it next to the display's `code.py`. If it's missing or a value is wrong, the built-in default is used and the display keeps working. |
| `display_setup.example.py` | **Only for a display that is not built into the board** (TFT FeatherWing, breakout, OLED). Copy it to the drive as `display_setup.py` and keep the block for your display; `code.py` and `receiver.py` pick it up by themselves and size the layout to the screen (v1.26+). Not needed — and not to be copied — on the #5691 or any board with a built-in screen. The example blocks are untested |

### Documentation

| File | Purpose |
|------|---------|
| `AEROMORSE_USAGE_GUIDE.md` / `.pdf` | **Start here once your device works.** (It also explains why a second device is worth having when the AeroMorse is your only computer access: a spare, and a safe place to test changes.) How to change it safely: setting up a work folder, what each helper tool does (backup, validator, AeroMorse Secrets, cheat sheet, analyzer), and the recommended step-by-step order for any edit, with a one-page checklist |
| `AEROMORSE_BUILD_GUIDE.md` | Full build guide covering hardware options, wiring, soldering, wireless display setup, library installation, troubleshooting, and parts lists. **Appendix H** covers the enclosure and the air-tube strain relief (not included in the parts lists or prices), with photos of the author's ATMakers-designed box |
| `CAREGIVER_SETUP_GUIDE.md` | Plain-English step-by-step assembly guide for a non-technical caregiver, using a specific recommended parts set |
| `AEROMORSE_VS_DARCI.md` | Feature-by-feature comparison vs. the WesTest Darci USB, with migration guide for Darci users |
| `MORSE_DEVICES_COMPARISON.md` | Side-by-side comparison of AeroMorse vs Adap2U, Darci USB, and morAce — including 1/2/3-switch mode support |
| `AEROMORSE_SWITCH_MODE_GUIDE.md` / `.pdf` | **Switch mode (Group 9)** — AeroMorse as two plain switches: sip holds Enter, puff holds Space, for switch games and apps that need a key held (e.g. [Benny's Hub](https://narbehouse.github.io/bennyshub/index.html)). How to enter/leave, settings, Benny's Hub walkthrough, troubleshooting |
| `AEROMORSE_SWITCH_CONTROL_GUIDE.md` | How to use AeroMorse's Group 4 (F1–F12) with **iOS Switch Control**, **Android Switch Access**, and **Samsung Universal Switch** — Morse-pattern → F-key → OS action tables, with step-by-step OS setup for each platform |
| `TOOLS_AND_GUIDES.md` | Reference for development tools: Thonny, CircuitPython installer |
| `AeroMorse Cheat Sheet.pdf` | Printable cheat sheet — one page per group, showing every pattern as dots/dashes next to its key or action, with a legend on the first page. Printed from `aeromorse_cheatsheet.htm` (load `morse_map.py` and use the browser's Print). |

### Development tools (run on your PC, not on the device)

| File | Purpose |
|------|---------|
| `aeromorse_cheatsheet.htm` | Interactive browser-based cheat sheet — open in any browser, no install needed. Shows every pattern for the active group as animated dots and dashes; click any row to hear the timing. |
| `AeroMorse Help.html` | **The cheat sheet as a help window** — legend at the top and one tab per group, so there is no scrolling through pages; click a tab, press a group's number, or use the arrow keys. A single file with the map inside it, built by `build_pdfs.py` alongside the cheat sheet PDF (the copy in the repo is for the supplied map; build your own from your map with `--folder`). Opened and closed with one Morse code through `AeroMorse.ahk` (next row). |
| `AeroMorse.ahk` | **Ready-made AutoHotkey script (Windows)** for the three things a keyboard device cannot do by itself, each with a Morse code already in the supplied map: **Ctrl+Alt+D** AeroMorse Display window on / off (`.-.-.-`, Group 0), **Ctrl+Alt+H** AeroMorse Help window on / off (`..-..-`, Group 0), **Ctrl+Alt+Home** mouse pointer to the middle of the screen (`.-.`, Mouse group). Keep it in your work folder next to `AeroMorse Display.exe` and `AeroMorse Help.html` — it finds them there, nothing to edit. Needs AutoHotkey v2; set-up in Usage Guide §7 / Build Guide Appendix G. |
| `KEYCODE_REFERENCE.md` / `keycode_reference.htm` / `AeroMorse — Keycode Reference.pdf` | Reference of every valid `Keycode.NAME` for `morse_map.py` (letters, number keys, navigation, punctuation, F-keys, keypad, modifiers), plus how to produce shifted symbols (`:` `{` `}` …). The `.pdf` is the ready-to-print 2-page sheet; the `.htm` is the same styled for the browser; the `.md` opens in the Markdown viewer. Extracted from the `adafruit_hid` 9.x library on the devices. |
| `aeromorse_validator.py` / `aeromorse_validator.exe` | **Safety check — run this before trusting edited device files on the device.** Checks every required file the device needs to boot: **`boot.py`, `code.py`, `config.py`, `morse_map.py`** (plus optional `macro_secrets.txt`). For each it catches the things CircuitPython is fussy about that desktop editors hide: a **UTF-8 BOM** (the classic "lost all access" cause) and a Python **syntax error**. For `config.py` and `morse_map.py` it also reproduces the device's actual import (catching an **import error**), sanity-checks `config.py` settings (missing settings, out-of-range values), and confirms every `_secret()` pattern finds its value in `macro_secrets.txt`. Reports a plain-language **PASS** (safe) or **FAIL** (fix before relying on it — don't replace your working files yet), pointing at the exact line. A file that isn't in the folder shows **SKIP**, not FAIL. **Never prints secret values** — key names and counts only. Put it in the same folder as the file(s) you edited and double-click the `.exe`, or run `python aeromorse_validator.py`. Accepts an optional folder/file argument (e.g. `aeromorse_validator.exe F:\`) to check the device directly. |
| `aeromorse_display.py` / `AeroMorse Display.exe` | **The AeroMorse screen in a window on the computer** (v1.26+) — any size, always-on-top or see-through, no extra hardware. Set `PC_DISPLAY = True` in `config.py`, then start the program; it finds the device, only listens (never sends anything to it) and reconnects by itself. See Build Guide §5. Build Guide **Appendix G** (also Usage Guide §7) shows how to open and close it with one Morse code, using the free AutoHotkey program (where to get it, a sample script, starting it with Windows). **It can also play the device's beeps through the computer's speakers** (`PC_SOUND = True`, v1.27+), for a device with no speaker fitted |
| `aeromorse_secrets.py` / `AeroMorse Secrets.exe` | **Edit your passwords and save them PIN-locked.** Opens `macro_secrets.enc` (asks the PIN) or imports `macro_secrets.txt`, lets you edit the `key=value` lines, saves them encrypted with a PIN you choose, warns about `_secret()` keys in `morse_map.py` with no value, and can copy the file to the CIRCUITPY drive and remove the plain-text file. See [PIN-locked secrets](#pin-locked-secrets-macro_secretsenc). The `.py` needs `pip install cryptography`; the `.exe` needs nothing. |
| `Edit my AeroMorse secrets.bat` | **One-click** launcher for AeroMorse Secrets. Keep it in your work folder next to `AeroMorse Secrets.exe` and `morse_map.py`; double-click it to open the secrets in that folder. |
| `Back up my AeroMorse.bat` | **One-click dated backup.** Keep it in your work folder and double-click with the device plugged in: copies everything on every AeroMorse (CIRCUITPY) drive into `Backups\<name>-<YYYY-MM-DD_HHMM>`, named from a label file such as `AeroMorse-Green.txt` on the device. Read-only on the device. |
| `Check my AeroMorse files.bat` | **One-click** wrapper for the validator. Keep it in your work folder next to `aeromorse_validator.exe` and the files you edited (`boot.py`, `code.py`, `config.py`, `morse_map.py`, `macro_secrets.txt`); double-click it to run the safety check on that folder and see PASS/FAIL. |
| `build_pdfs.py` / `Build PDFs.bat` | **Regenerate the three printable PDFs** (`AEROMORSE_BUILD_GUIDE.pdf`, `AeroMorse Cheat Sheet.pdf`, `AeroMorse — Keycode Reference.pdf`) from their sources. Double-click `Build PDFs.bat` after editing the Build Guide, cheat sheet, `morse_map.py`, or the Keycode reference. Rebuilds all three; add `guide`, `cheatsheet`, or `keycode` to rebuild just one. **Personal cheat sheet:** `python build_pdfs.py --folder <your work folder>` prints `AeroMorse Cheat Sheet.pdf` from *your* `morse_map.py` into that folder (a one-click `Build my cheat sheet.bat` in the edit folder does this). Needs Microsoft Edge and Python. |
| `morse_map_analyzer.py` | Python 3 script that reads `morse_map.py` and reports duplicate codes, conflicts with the always-on Group 0 patterns, and unused code slots for lengths 2–7. Run with `python morse_map_analyzer.py`; output is saved to `morse_map_report.txt`. |
| `morse_map_report.txt` | Latest output from `morse_map_analyzer.py` |
| `test_pressure.py` | Diagnostic script — copy to CIRCUITPY; press Ctrl-C to reach the `>>>` REPL prompt (do **not** reset — that re-runs `code.py`), then `import test_pressure`. To run again: `exec(open('test_pressure.py').read())` (`importlib` is not available in CircuitPython). Prints a live pressure-delta bar chart for 30 s and suggests `THRESH_SIP` / `THRESH_PUFF` values for `config.py`. |
| `test_ble.py` | **Bluetooth keyboard test** (CircuitPython 10.x, needs `adafruit_ble/` in `lib/`). Copy to CIRCUITPY, stop `code.py` (Ctrl-C, then Enter for `>>>`), and run `import test_ble`. It advertises as "AeroMorse Blue"; pair from the phone's Bluetooth settings and it types a few test lines, printing whether it connected, paired, and stayed connected. Doesn't touch `code.py`. **On ESP32-S3 + CircuitPython 10.3.1 a BLE keyboard does not stay connected yet** — see Build Guide §3 BLE HID note. |

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
| Calibration message at startup then hangs | Sensor not found on I²C | Check the STEMMA QT cable connection — or, on a board without a STEMMA QT port, the 3V / GND / SDA / SCL wires |
| Dashes go missing (e.g. `x` `-..-` types `u` `..-`, `q` types `k`) | A quick puff right before a sip doesn't reach `THRESH_PUFF` on this sensor | Lower `THRESH_PUFF` a little (e.g. `2` → `1.5`); leave `THRESH_SIP` alone if dots are fine |
| Two sips or two puffs in a row count as one (`p` `.--.` types `r` `.-.`, space `..--` types `w` `.--`) | The pressure doesn't fall back under the trigger between the two | Set `REPEAT_SPLIT_PCT = 60` in `config.py` (v1.18+), or leave a slightly longer break between the two |
| Screen shows `ERROR - SEE LOG` | One action hit an unexpected problem (v1.6+ keeps running instead of stopping) | Keep using the device; the USB serial log shows which pattern and why. Fix that entry in `morse_map.py` and run the validator |

### Pop-ups on the computer when the device starts or restarts

AeroMorse shows up on the computer as a keyboard, a mouse **and a small USB
drive called `CIRCUITPY`** — that drive is how you edit `config.py` and
`morse_map.py`. Every time the device starts, restarts (`devicereset`, saving a
file, replugging) the drive reconnects, and any program that watches for USB
drives reacts with a pop-up near the clock. Typical ones on Windows:

| Pop-up | Who shows it | What it wants |
|---|---|---|
| **AutoPlay** — "Select to choose what happens with removable drives" | Windows | To know what to do when a USB drive appears |
| **"New device detected"** / an offer to scan the drive | Your antivirus (ESET and others) | To scan the drive |
| An offer to **back up the device** | Google Drive (other cloud-backup tools do the same) | To copy the drive's contents to the cloud |
| "There's a problem with this drive — scan and fix" | Windows | Appears if the drive vanished mid-restart without being ejected |

**They are harmless and safe to ignore.** None of them changes anything unless
you click it, and they have no effect on typing. If you would rather not see
them, switch each one off where it comes from (menu names vary a little
between versions):

- **AutoPlay:** Windows *Settings → Bluetooth & devices → AutoPlay* → turn
  off **Use AutoPlay for all media and devices**.
- **Antivirus:** look in its settings for **Removable media** (sometimes
  under device control or detection) and set the action on inserting a drive
  to **do not scan / do not ask**. In ESET it is under *Setup → Advanced
  setup*. Leave the rest of the antivirus as it is.
- **Google Drive:** Drive icon near the clock → gear → *Preferences* → gear
  again → **USB devices & SD cards** → untick the prompt to back up. The
  pop-up itself may also offer *Don't ask again for this device*. This one is
  worth switching off regardless, so the contents of your device (your key
  map and your encrypted secrets file) are never copied to the cloud.

Do **not** try to stop the pop-ups by hiding or disabling the `CIRCUITPY`
drive — without it you could no longer edit or update the device.

## Credits

Inspired by AirTalker (https://github.com/ATMakersOrg/AirTalker). Thanks Bill!

Vibe coded by Jim Lubin (https://makoa.org/jim) using Gemini Pro 3.1 & Claude Code Opus 4.7.
Jim has been using morse code for computer access since 1989 when he became a ventilator dependent quadriplegic, paralyzed from the neck down and dependent on a ventilator to breathe. See his webpage at (https://makoa.org/jlubin/morsecode.htm).
