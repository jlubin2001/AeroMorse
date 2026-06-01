# AeroMorse v2 — Build Guide  *(DEPRECATED)*

> **⚠ This v2 build is deprecated as of 2026-06.** It targets a
> 128×64 SSD1306 OLED display and is missing many recent features (config.py
> split, 1- and 3-switch modes, CODE_REPEAT, strong sip/puff,
> ConsumerControl / g5 Media, USE_WIRELESS_DISPLAY, the tuned ACCEPT_DELAY
> default). See [`DEPRECATED.md`](DEPRECATED.md) for the full feature-gap
> table and migration recommendations.
>
> **New builders should use the main `AEROMORSE_BUILD_GUIDE.md` at the repo
> root and the root `code.py`** — pair with a Feather that has a built-in
> TFT (#5691 Reverse TFT, #5483, #5300) or with an EYESPI / FeatherWing TFT.

### STEMMA QT OLED · TRRS AT-Switch · Speaker Edition  *(frozen)*

This guide walks a first-time builder through assembling AeroMorse v2 from scratch.
There are **two build options**:

- **Option A — Solderless (breadboard):** no soldering at all; great for testing first
- **Option B — Soldered (TRRS breakout):** compact and durable for everyday use

Both options produce the same working device. You can start with Option A and migrate
to Option B later.

---

## What AeroMorse Does

AeroMorse lets you type and control a computer using sip-and-puff breath input or AT
(assistive technology) switches, using Morse code patterns. It appears to the computer
as a standard USB keyboard and mouse — no drivers needed on any operating system.

- **Sip** (or press dot-switch) = dot
- **Puff** (or press dash-switch) = dash
- Hold either for 2 seconds to cycle between input groups (keyboard / mouse / macros)
- The OLED display shows the current group, the Morse pattern being built, and the
  last action taken
- The speaker beeps as you sip/puff so you can hear the rhythm in real time

---

## Parts List

### Both versions need these:

| Qty | Description | Adafruit ID |
|-----|-------------|-------------|
| 1 | Adafruit ESP32-S3 Feather 4MB/2MB PSRAM - STEMMA QT | #5477 |
| 1 | STEMMA QT / Qwiic JST SH 4-Pin Cable - 100mm | #4210 |
| 1 | STEMMA QT / Qwiic JST SH 4-Pin Cable - 400mm | #5385 |
| 1 | Adafruit LPS33HW Water Resistant Pressure Sensor - STEMMA QT | #4414 |
| 1 | Monochrome 0.96" 128x64 OLED Graphic Display - STEMMA QT | #326 |
| 1 | Adafruit STEMMA Speaker | #3885 |
| 1 | STEMMA JST PH 2mm 3-Pin to Male Header Cable - 200mm | #3893 |
| 1 | USB-C cable (data + power) | any |
| 1 | Sip-and-puff tube (¼ inch OD) — only needed if using sensor mode | medical / hardware store |

### Option A — Solderless breadboard only:

| Qty | Description | Adafruit ID |
|-----|-------------|-------------|
| 1 | Half Sized Premium Breadboard - 400 Tie Points | #64 |
| 1 | Breadboard-Friendly 3.5mm Stereo Headphone Jack | #1699 |
| 3 | Short male-to-male jumper wires (any colour) | — |

> The Feather's header pins must be soldered before use. If your Feather came
> without headers, solder the included header strip or ask someone to do it for
> you — this is the only soldering needed for Option A.

### Option B — Soldered build only:

| Qty | Description | Adafruit ID |
|-----|-------------|-------------|
| 1 | Adafruit TRRS Jack Breakout Board | #5764 |
| 4 | Short wires ~8 cm (4 different colours helps) | — |

> You need a soldering iron and solder.

---

## AT Switches (your existing switches — not included)

This device accepts standard assistive technology switches with a **3.5mm mono
plug** (also called TS or "tip-sleeve"). Any switch compatible with Ablenet,
Specs, Inclusive Technology, or similar systems will work.

- **One switch** = dot input only (enough to navigate menus slowly)
- **Two switches** = dot + dash — strongly recommended for practical use

---

## Step 1 — Install CircuitPython

1. Go to **circuitpython.org/downloads** and search for **"ESP32-S3 Feather"**.
2. Download the latest stable `.uf2` file.
3. Plug the Feather into your computer with a USB-C **data** cable (not a
   charge-only cable — it must be able to transfer files).
4. **Double-tap** the small Reset button on the Feather (tap twice quickly).
   - The NeoPixel LED turns green and a drive named **FTHRS3BOOT** (or similar)
     appears on your computer.
5. Drag the `.uf2` file onto that drive. The Feather reboots automatically.
6. After a few seconds a drive named **CIRCUITPY** appears. Done.

> If **CIRCUITPY** already appears without double-tapping, CircuitPython is
> already installed — skip straight to Step 2.

---

## Step 2 — Install Libraries

1. Go to **circuitpython.org/libraries** and download the **Bundle** matching
   your CircuitPython version. (The version number is in `boot_out.txt` on the
   CIRCUITPY drive — e.g. "9.2.1" means download the 9.x bundle.)
2. Open the downloaded `.zip` file. Inside is a `lib/` folder.
3. On the **CIRCUITPY** drive, open or create the `lib/` folder.
4. Copy these items from the bundle's `lib/` folder into CIRCUITPY's `lib/`:

   ```
   adafruit_displayio_ssd1306.mpy
   adafruit_lps35hw.mpy
   adafruit_display_text/        ← entire folder
   adafruit_hid/                 ← entire folder
   adafruit_bus_device/          ← entire folder
   adafruit_register/            ← entire folder
   neopixel.mpy
   ```

> You only need the items listed — no need to copy the entire bundle.

---

## Step 3 — Copy the Project Files

Copy these files from the `v2/` folder to the **root** of the CIRCUITPY drive
(not inside any subfolder):

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
    ├── adafruit_displayio_ssd1306.mpy
    ├── adafruit_lps35hw.mpy
    ├── adafruit_display_text/
    ├── adafruit_hid/
    ├── adafruit_bus_device/
    ├── adafruit_register/
    └── neopixel.mpy
```

Safely eject the CIRCUITPY drive. The Feather reboots and runs the code.
(The first boot after installing `boot.py` negotiates USB HID — this is normal.)

---

## Step 4A — Solderless Breadboard Assembly

### How a breadboard works

Each numbered row of holes is electrically connected internally. The two long
rails along the sides are power (+) and ground (−). You connect parts by pushing
their pins into the same row.

### Place the parts

1. **Feather** — press it into the breadboard so the header pins straddle the
   centre gap. Place it near one end, leaving space at the other end for the
   stereo jack.

2. **Stereo jack (#1699)** — press it into the breadboard a few rows from the
   Feather. It has three legs:
   - **TIP** (longest, or marked T)
   - **RING** (middle, or marked R)
   - **SLEEVE** (shortest, or marked S / GND)

### Wire the jack to the Feather

Use short jumper wires — push one end into the breadboard row holding the jack
leg, and the other end into the row holding the Feather pin:

| Jack leg | Feather pin | Wire colour suggestion |
|----------|-------------|------------------------|
| TIP      | D5          | red                    |
| RING     | D6          | blue                   |
| SLEEVE   | GND         | black                  |

Pin labels are printed on the underside of the Feather. **D5** and **D6** are
digital GPIO pins. **GND** is any ground pin (there are several).

### Connect the STEMMA QT chain

The small 4-pin JST connectors click in one way only — do not force them.

```
Feather  ──[100mm cable]──  LPS33HW sensor  ──[400mm cable]──  OLED display
```

1. Plug the **100mm cable** (#4210) into the STEMMA QT port on the Feather.
2. Plug the other end into either STEMMA QT port on the **LPS33HW** (#4414).
3. Plug the **400mm cable** (#5385) into the remaining STEMMA QT port on the LPS33HW.
4. Plug the other end into the STEMMA QT port on the **OLED** (#326).

> Both the LPS33HW and OLED have two STEMMA QT ports so they daisy-chain like this.
> The order (sensor first, display second) doesn't matter — I²C is a shared bus.

### Connect the STEMMA Speaker

The speaker cable (#3893) has a JST PH 2mm plug on one end and three male header
pins on the other. The header pins are labelled or in order: **GND**, **Audio**,
**VIN**.

Push each pin into a breadboard row that also has the matching Feather pin, or
use jumper wires:

| Speaker cable pin | Connect to Feather pin |
|-------------------|------------------------|
| GND               | Any GND pin            |
| Audio             | A0                     |
| VIN               | 3V                     |

> **A0** is the analog output that generates the audio signal. **3V** powers the
> speaker's built-in amplifier. 5V also works if 3V rows are already occupied.

### Full breadboard layout summary

```
[Feather] ─ jumpers ─ [Stereo Jack]
    │
 100mm STEMMA QT cable
    │
[LPS33HW sensor]
    │
 400mm STEMMA QT cable
    │
[OLED display]

[Speaker cable] ─→ GND, A0, 3V on Feather
```

---

## Step 4B — Soldered TRRS Build

### Solder wires to the TRRS breakout

The TRRS Jack Breakout (#5764) has pads labelled **T**, **R1**, **R2**, **S**
(and sometimes **G** for board ground).

Cut four ~8 cm wires. Strip ~3 mm of insulation from each end.
Solder one wire to each pad — use different colours to avoid confusion:

| Pad | Meaning            | Suggested wire colour |
|-----|--------------------|-----------------------|
| T   | Tip (dot switch)   | Red                   |
| R1  | Ring 1 (dash switch) | Blue                |
| S   | Sleeve / GND       | Black                 |
| R2  | Unused — leave bare | —                   |

### Connect the wires to the Feather

Solder or use a connector to attach the wires:

| Wire from TRRS pad | Feather pin |
|--------------------|-------------|
| T (red)            | D5          |
| R1 (blue)          | D6          |
| S (black)          | GND         |

### STEMMA QT chain and Speaker

Same as Option A — plug the 100mm and 400mm cables and the speaker cable exactly
as described in Step 4A. The TRRS breakout replaces only the breadboard stereo
jack; everything else is identical.

---

## Step 5 — Plug In Your AT Switches

### Standard mono AT switch (TS plug)

Each AT switch has a 3.5mm mono (TS) plug. Pressing the switch connects Tip to
Sleeve.

**Option A (breadboard stereo jack):**
A standard 3.5mm stereo Y-splitter lets you plug two mono AT switches into one
stereo socket:
- Switch 1 (dot) → Tip leg of the Y-splitter → TIP of the jack
- Switch 2 (dash) → Ring leg → RING of the jack

**Option B (TRRS jack):**
Use a TRRS cable or make a custom one:
- Switch 1: connects Tip to Sleeve of the TRRS plug (dot)
- Switch 2: connects Ring 1 to Sleeve of the TRRS plug (dash)
Both switches share the Sleeve as common ground.

---

## Step 6 — First Power-On Test

1. Plug the Feather into your computer with the USB-C cable.
2. Wait 3–5 seconds. You should see:
   - The OLED showing **[Keyboard]**
   - The serial console (if connected) printing "Calibrating…"
   - A short beep from the speaker when calibration finishes
3. After calibration (~2 seconds) the device is ready to use.

### Quick test

Open a text editor on your computer.

1. Press your dot switch — the speaker beeps and the OLED shows `.`
2. Press your dash switch — speaker beeps, OLED shows `. -`
3. Wait 0.2 seconds — the letter **N** (dash-dot = `-.`) should appear in the
   text editor

If that works, everything is assembled correctly.

---

## Step 7 — Configuration

Open `code.py` in any text editor and look at the top section:

```python
USE_SENSOR = True   # Change to False to use AT switches instead of sip/puff
```

| Setting | Default | What it does |
|---------|---------|--------------|
| `USE_SENSOR` | `True` | `True` = LPS33HW sip/puff; `False` = AT switches via jack |
| `THRESH_SIP` | `5` | hPa below baseline needed for a dot (lower = more sensitive) |
| `THRESH_PUFF` | `5` | hPa above baseline needed for a dash |
| `ACCEPT_DELAY` | `0.2` | Seconds of silence before a Morse pattern is committed |
| `LONG_PRESS` | `1.0` | Hold seconds to trigger group change |
| `BEEP_FREQ` | `800` | Speaker tone frequency in Hz |

Save the file to CIRCUITPY and the Feather reloads automatically.

---

## Sensor vs. Switch Mode

| | Sensor (sip/puff) | AT Switches |
|--|--|--|
| `USE_SENSOR` | `True` | `False` |
| Dot input | Sip into tube | Press dot switch |
| Dash input | Puff into tube | Press dash switch |
| Connector | LPS33HW via STEMMA QT | TRRS jack or stereo jack |
| Good for | Hands-free use | Users with existing AT switches |

Both modes work with the same OLED display and speaker.

---

## Display Layout

```
┌──────────────────────┐
│ [Keyboard]           │  ← active group
│ . - . .              │  ← Morse pattern building up
│ "n"                  │  ← last character or action
│ Ctrl                 │  ← armed modifier / status
│▓▓▓▓▓░░░░░░░░░░░░░░░░│  ← pressure bar (sensor mode)
└──────────────────────┘
```

Status line can show: **Ctrl / Shift / Alt / GUI** (sticky modifier armed),
**SLOW** / **FAST** / **DRAG** / **RPT** (mouse mode state).

---

## Groups

| Group | Default access | Contents |
|-------|---------------|----------|
| 0 | Always available | Emergency group-switch codes (8-symbol patterns) |
| 1 | Startup default | Letters, numbers, punctuation, function keys |
| 2 | `...-. ` from Group 1 | Mouse movement, clicks, Windows shortcuts |
| 3 | `....----` (8 symbols) | Macro text strings |

Long-sip (2+ s) cycles groups backward; long-puff cycles forward.

---

## Troubleshooting

**OLED is blank**
Check both ends of both STEMMA QT cables click firmly in. If the display
initialises but shows nothing, the I²C address may be 0x3D instead of 0x3C —
change `device_address=0x3C` to `device_address=0x3D` in `code.py`.

**No sound from speaker**
Verify cable wiring: Audio → A0, VIN → 3V, GND → GND.
Check the REPL for "WARNING: audio modules not available" — if you see that,
`audiopwmio` or `synthio` is missing from your CircuitPython build (use a
standard build, not a minimal one).

**AT switches not registering**
Confirm `USE_SENSOR = False` in `code.py`. Test with a multimeter in continuity
mode: pressing the switch should beep, showing Tip connects to Sleeve. Check
that D5 and D6 are wired to the correct jack legs.

**False pressure triggers (sip/puff mode)**
Increase `THRESH_SIP` and `THRESH_PUFF` (e.g. from 5 to 8) to require a
stronger breath before a symbol registers.

**"Calibrating" hangs at startup**
The LPS33HW sensor is not found on I²C. Check the STEMMA QT cable between the
Feather and the sensor — both connectors must click in firmly.

**Pattern commits too early (cuts off a long pattern)**
Increase `ACCEPT_DELAY` (e.g. from 0.2 to 0.3).

**Nothing happens on the host computer**
Unplug and replug the USB cable — the first boot after installing `boot.py`
negotiates USB HID and needs a fresh connection.

**REPL shows ImportError**
A library file is missing from `lib/`. Re-read Step 2 and copy the missing
`.mpy` file from the CircuitPython bundle.

---

## Customising Macros

Open `morse_map.py`. Scroll to Group 3 near the bottom. Replace the empty
strings with your own phrases:

```python
g3[3][0b100] = 'Jane Smith'     # -..   D pattern
g3[4][0b0010] = 'Thank you!'    # ..-.  F pattern
g3[3][0b010] = 'Best regards,'  # .-.   R pattern
```

The Morse pattern that triggers each macro is the same pattern as the letter
shown in the comment (D, F, R, etc.) in Group 1. Save the file — the Feather
reloads automatically.
