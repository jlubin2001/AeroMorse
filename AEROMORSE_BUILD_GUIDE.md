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
4. [Input Method Options](#4-input-method-options)
5. [Display Options](#5-display-options)
   - [Wireless Display — ESP-NOW Remote Mirror](#wireless-display--esp-now-remote-mirror)
6. [Speaker Options](#6-speaker-options)
7. [Complete Parts Lists](#7-complete-parts-lists)
8. [Step-by-Step Assembly](#8-step-by-step-assembly)
9. [Software Installation](#9-software-installation)
10. [Configuration](#10-configuration)
11. [First Power-On Test](#11-first-power-on-test)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. What AeroMorse Does

AeroMorse is an open-source CircuitPython project directed by Jim Lubin — a
ventilator-dependent quadriplegic who has used Morse code for computer access
since 1989. Inspired by [AirTalker](https://github.com/ATMakersOrg/AirTalker), it turns an Adafruit Feather microcontroller into a
USB HID keyboard and mouse that connects via USB-C and appears to the host as
a standard keyboard and mouse with no drivers required. Works on **Windows,
macOS, Linux, iPadOS, Android, and ChromeOS**.

**How this project was built — what's confirmed vs documented.** Jim is the
user, project lead, and source of all design decisions: hardware choices,
input-mode requirements, Morse code-set conventions, accessibility trade-offs,
and ongoing user feedback (his own and from other AAC users — Darci USB
veterans in particular). The firmware (`code.py`), this build guide, and the
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

1. **A Feather microcontroller board** (the brain — required)
2. **An input method** (sip-and-puff sensor or AT switches — required)
3. **A display** (what you see — optional but recommended)
4. **A speaker** (audio feedback — optional)

Once you have chosen each, jump to the relevant wiring section in Step 8.

> **Recommended combination for most builders (USB HID, display included):**
> ESP32-S3 Reverse TFT Feather #5691 · LPS33HW sensor #4414 · STEMMA Speaker #3885
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
| ESP32-S3 TFT Feather | [#5483](https://www.adafruit.com/product/5483) | ✓ | ※ | ✓ 2MB | ✓ | Built-in 1.14" TFT — screen faces up (normal) |
| ESP32-S3 Reverse TFT Feather | [#5691](https://www.adafruit.com/product/5691) | ✓ | ※ | ✓ 2MB | ✓ | Built-in 1.14" TFT — screen faces down (panel mount) |
| ESP32-S2 TFT Feather | [#5300](https://www.adafruit.com/product/5300) | ✓ | — | ✓ 2MB | ✓ | Built-in 1.14" TFT — older S2 chip; no BLE |
| Feather nRF52840 Express | [#4062](https://www.adafruit.com/product/4062) | ✓ | ✓ | — | — | Most mature BLE HID; no PSRAM |

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
  (Section 5) without any extra hardware on the main board
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

**If you want BLE HID + PSRAM + the most memory (Metro form factor):**

The **Metro ESP32-S3 #5500** is the only board in this guide that combines all
three: reliable USB HID, reliable BLE HID, and 8 MB PSRAM. Use this board if
you need to control a phone, iPad, or PC wirelessly over Bluetooth without a
USB cable. BLE HID on the ESP32-S3 was unreliable in earlier CircuitPython
versions but is fully fixed in CircuitPython 10.x (current stable: 10.2.0).

The #5500 has no built-in display — connect the STEMMA QT OLED or a standalone
TFT breakout. The ESP-NOW wireless display (Section 5) works on it identically
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
| BLE HID + colour TFT or large display | #5500 Metro ESP32-S3 |
| BLE HID + OLED only (no large display needed) | #4062 nRF52840 Feather |

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
| **STEMMA QT OLED (#326, #938)** | ✓ Plug-and-play | STEMMA QT cable, no Feather wiring |
| **STEMMA QT sensor (#4414 LPS33HW)** | ✓ Plug-and-play | STEMMA QT cable |
| **FeatherWing displays (#3651, #5872, #3315)** | ✗ Not possible | The wing's holes can't grip bare pads — headers required |
| **Standalone TFT breakouts (#2050, #1770…)** | ⚠ Solder 5–7 wires | Solder display wires directly to Feather pads |
| **AT switches — Option B1 breadboard** | ✗ Not possible | Feather must sit *in* the breadboard via headers |
| **AT switches — Option B2 TRRS breakout** | ⚠ Solder 3 wires | Solder breakout output wires to D5/D6/GND pads |
| **AT switches — Option B3 #2915 Terminal Block** | ⚠ Solder 3 wires | Solder terminal-block wires to D5/D6/GND pads |
| **Speaker — #3885 STEMMA Speaker** | ⚠ Solder 3 wires | Cut JST PH plug off, solder to A0/3V/GND pads |
| **Speaker — Option S2 piezo (#2915 + #2790 + #1740/#1739)** | ⚠ Solder 2 wires only if no headers | If Feather has headers: 2 F-F jumpers from #2915 → A0/GND (zero soldering). If no headers: solder 2 wires from #2915 → A0/GND pads. Piezo side is screw-terminal either way. |
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

- Feather: **#5691** (built-in TFT — no wiring)
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

## 4. Input Method Options

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

## 5. Display Options

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

### FeatherWing displays (plug directly on Feather — easiest, requires headers)

| Display | # | Size | Resolution | Interface | URL |
|---------|---|------|-----------|-----------|-----|
| 3.5" TFT Resistive Touch | [3651](https://www.adafruit.com/product/3651) | 3.5" | 480×320 colour | SPI | https://www.adafruit.com/product/3651 |
| 3.5" TFT Capacitive Touch | [5872](https://www.adafruit.com/product/5872) | 3.5" | 480×320 colour | SPI | https://www.adafruit.com/product/5872 |
| 2.4" TFT Resistive Touch | [3315](https://www.adafruit.com/product/3315) | 2.4" | 320×240 colour | SPI | https://www.adafruit.com/product/3315 |

> **Header pins required on the Feather.** A FeatherWing has two rows of
> female header sockets on its underside that slide down onto the male pins
> on top of the Feather. If your Feather shipped as a bare PCB with empty
> pin holes, those holes must be filled with soldered male headers before a
> FeatherWing can be used — there is nothing for the wing to grip otherwise.
> Adafruit's standard Feather header kit (#2886) is the right part, or order
> a Feather variant that ships with headers pre-installed. If you cannot or
> would rather not solder, choose a STEMMA QT OLED (#326 / #938) or the
> built-in TFT on #5691 instead — both are plug-and-play with no headers.

> FeatherWings have a touchscreen controller that uses I²C. You will not use
> touch input with AeroMorse — the display portion works via SPI independently
> and will not conflict with the pressure sensor.

**Recommended for table mounting: #3651** — largest FeatherWing, bright colour,
plugs straight on (once headers are in place) with no additional wiring.

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

### EYESPI displays (advanced — SPI wiring via breakout adapter)

EYESPI is Adafruit's standardised **18-pin FPC connector** for SPI displays.
Several Adafruit TFT displays have an EYESPI socket, which makes cabling
cleaner: instead of individual jumper wires for each SPI signal, a single
flat flex cable connects the display to an **EYESPI Breakout Board**.

> **#5613 — Adafruit EYESPI Breakout Board — 18 Pin FPC Connector — $1.95**
> https://www.adafruit.com/product/5613
>
> This is a small passive adapter board. It has an 18-pin EYESPI FPC socket
> on one side and through-hole pads (breadboard-friendly) on the other,
> breaking out all 18 EYESPI signals to individual pins. **It is not a
> microcontroller and cannot run code** — it is purely a wiring adapter.

**How it works with a Feather:**

```
[ Any Feather ]──7 wires──[ #5613 breakout ]──EYESPI cable──[ EYESPI display ]
```

You still need to solder or jumper ~7 wires from the Feather's SPI pins
(MOSI, SCK, CS, DC, RST, 3V, GND) to the #5613 breakout's through-hole
pads. The breakout then sends those signals through the flat flex cable to
the display. This is functionally the same amount of wiring as connecting
any standalone SPI breakout display — the advantage is that the flex cable
is then available for routing the display to a different physical location
more neatly.

**EYESPI-compatible displays:**

| Display | # | Size | Resolution | Driver | URL |
|---------|---|------|-----------|--------|-----|
| 2.0" 320×240 IPS TFT EYESPI | [5800](https://www.adafruit.com/product/5800) | 2.0" | 320×240 colour | ST7789 | https://www.adafruit.com/product/5800 |
| 1.3" 240×240 IPS TFT EYESPI | [5393](https://www.adafruit.com/product/5393) | 1.3" | 240×240 colour | ST7789 | https://www.adafruit.com/product/5393 |

**EYESPI cables** (between #5613 breakout and display):

| Cable | # | Length | URL |
|-------|---|--------|-----|
| EYESPI Cable 50 mm | [5239](https://www.adafruit.com/product/5239) | 50 mm | https://www.adafruit.com/product/5239 |
| EYESPI Cable 100 mm | [5240](https://www.adafruit.com/product/5240) | 100 mm | https://www.adafruit.com/product/5240 |
| EYESPI Cable 200 mm | [5241](https://www.adafruit.com/product/5241) | 200 mm | https://www.adafruit.com/product/5241 |

> **For most builders, a FeatherWing display or the built-in TFT on #5691
> is a simpler choice.** The EYESPI path is useful if you specifically want
> a certain display size/shape and a neat flex-cable run, and you are
> comfortable soldering 7 wires to the #5613 breakout.

> **Code:** EYESPI displays are not auto-initialised — `board.DISPLAY` is not
> populated. You must initialise them in `code.py` with `displayio` and the
> appropriate driver library (same as the standalone breakout displays above).

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

> Each board runs **at least CircuitPython 9** (earlier versions did not
> include the `espnow` module). Beyond that, the two boards are completely
> independent — see §12 "Wireless display → CircuitPython versions on the
> two boards" if you need the full compatibility details.

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

**Files needed on the second board:** See **§9.4.1 Option W1** for the
complete file tree and step-by-step setup. In short: `receiver.py` →
`code.py`, `receiver_boot.py` → `boot.py`, and one library folder
(`adafruit_display_text/`) under `/lib`. No HID library, no Morse map.

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

**Libraries needed on the XIAO's `/lib` folder:** See **§9.4.1 Option W2**
for the complete file tree. In short:
`adafruit_displayio_ssd1306.mpy` (for the OLED driver) plus
`adafruit_display_text/`.

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

**Adafruit STEMMA Speaker #3885** — $5.95
https://www.adafruit.com/product/3885

- 1 W built-in amplifier, 8 Ω driver, 3-pin JST PH 2 mm socket
- Powered from 3 – 5 V (the Feather's 3V or USB pin both work)
- Loud enough to hear across a quiet room

> **Cable is sold separately.** Order **Adafruit #4046 — JST PH 2 mm 3-Pin
> Socket to Color-Coded Cable, 200 mm — $0.95** along with the speaker.
> https://www.adafruit.com/product/4046
> One end is the JST PH socket that plugs into the speaker board; the other
> end is three tinned, color-coded wires that go to the Feather. Without
> this cable, #3885 is just a bare board with a socket on it.

Wiring (#4046 cable to Feather):

| Wire (color) | Feather pin |
|-------------------|-------------|
| Black (GND) | GND |
| White (Audio / signal) | A0 |
| Red (VIN) | 3V (or USB / 5V) |

---

### Option S2 — Passive piezo with detachable 3.5 mm connection (solderless)

A passive piezo wired via a **3.5 mm jack-and-plug pair**, so the piezo
end can be unplugged and swapped. Quieter than Option S1, but every
connection is screw-terminal — no soldering anywhere. Any speaker that
already terminates in a 3.5 mm mono plug also plugs straight into the
same #2915 jack with no adapter.

> **Important:** Buy a *passive* piezo, not an *active* one. An active
> buzzer has a built-in oscillator and will only click, not produce a
> tone. The two piezos below are confirmed passive and work directly
> from the Feather's A0 pin via PWM — no resistor, no capacitor, no
> amplifier (a piezo is a high-impedance capacitive load).

#### Parts

| Qty | Item | Adafruit # | Price | Role |
|-----|------|-----------|-------|------|
| 1 | TRRS Jack Terminal Block | [#2915](https://www.adafruit.com/product/2915) | $2.50 | Jack on the Feather side (screw terminals) |
| 1 | 3.5 mm Stereo Audio Plug Terminal Block | [#2790](https://www.adafruit.com/product/2790) | $2.50 | Plug on the piezo side (screw terminals) |
| 1 | Small Enclosed Piezo with Leads | [#1740](https://www.adafruit.com/product/1740) | $0.95 | Compact piezo, good for tucking in an enclosure |
| — | *or* Large Enclosed Piezo with Leads | [#1739](https://www.adafruit.com/product/1739) | $0.95 | Slightly larger housing, a little louder |
| 2 | Female-to-female jumper wires (if Feather has headers) | [#266](https://www.adafruit.com/product/266) | — | Connect #2915 to Feather A0 / GND |

Total: ~$6 if you already own jumpers.

#### Wiring

```
   Piezo  ──+── red wire ──┐    #2790 plug    #2915 jack
            ──── black ────┤  ┌───────────┐  ┌───────────┐
                           ├──┤ Tip       ╞══╡ Tip       ├─── A0
                           ├──┤ Sleeve    ╞══╡ Sleeve    ├─── GND
                           └──┤ Ring  (—) │  │ Ring/R2(—)│
                              └───────────┘  └───────────┘
                              screw terminals  screw terminals
```

#### Connection table

| Side | Terminal | Connects to | Notes |
|---|---|---|---|
| **#2790 plug** (piezo side) | Tip | Piezo "+" lead (red) | Polarity match |
| | Sleeve | Piezo "−" lead (black) | |
| | Ring | — | Leave empty |
| **#2915 jack** (Feather side) | Tip | Feather **A0** | Audio signal |
| | Sleeve | Feather **GND** | Audio return |
| | Ring | — | Leave empty (mono plug) |
| | Ring 2 | — | Leave empty |

#### Why this works without signal conditioning

The piezo is a capacitive, high-impedance load — direct PWM drive from
A0 (square wave at 800–1200 Hz) makes the piezo flex audibly with no
need for a series resistor, AC-coupling capacitor, or amplifier. Same
electrical path as the bare-lead piezo of older Option S2 builds; the
jack-and-plug pair just adds detachability.

#### Already have a 3.5 mm-plug piezo or speaker?

If your speaker already terminates in a 3.5 mm mono plug, skip the
#2790 plug — the existing plug goes straight into the #2915 jack. You
still need the jack itself wired to A0 / GND on the Feather.

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
| **Option S1** | STEMMA Speaker | #3885 | https://www.adafruit.com/product/3885 |
| | JST PH 3-pin Socket to Color-Coded Cable, 200 mm (required with #3885) | #4046 | https://www.adafruit.com/product/4046 |
| **Option S2** | TRRS Jack Terminal Block (Feather side) | #2915 | https://www.adafruit.com/product/2915 |
| | 3.5 mm Stereo Audio Plug Terminal Block (piezo side) | #2790 | https://www.adafruit.com/product/2790 |
| | Small Enclosed Piezo with Leads (passive) | #1740 | https://www.adafruit.com/product/1740 |
| | *or* Large Enclosed Piezo with Leads (passive, louder) | #1739 | https://www.adafruit.com/product/1739 |
| **Option S3** | PAM8302 Amplifier + small 8 Ω speaker | #2130 | https://www.adafruit.com/product/2130 |

---

### Tools

> **Software tools (Thonny etc.) are covered in §9.3 "Install Thonny" — they
> belong with the software-install steps, not the parts list.**

#### Hardware tools — solderless build (Option B1 breadboard)

**If your Feather already has header pins soldered:** No special tools needed —
the pins press straight into the breadboard.

**If your Feather has no header pins (bare holes):** You have two options:

| Option | What to do | Cost |
|--------|-----------|------|
| **Get headers soldered** | Take the Feather and the included loose header strip to a local makerspace, library maker lab, or electronics repair shop — most will solder headers for free or a few dollars. This is the most reliable long-term solution. | Free–$5 |
| **Order with headers pre-installed** | Adafruit sells some Feather boards with headers already soldered. When reordering, look for the listing that says "with headers" in the title. | Same price as bare board |

> **Why not test hook clips?** Test hook clips (EZ-hook / Goupchn style)
> need something cylindrical to hook around — a wire lead, header pin, or
> IC leg. They cannot reliably grip a flat through-hole pad: there is
> nothing protruding for the hook to bite, and the hook is too large to
> engage inside the 0.7–1.0 mm through-hole. They will slide off with the
> lightest tug. Use one of the two options above instead.

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

**STEMMA Speaker #3885 + #4046 cable** — the #4046 cable ends in three
tinned bare wires (black / white / red). The tinned tips are stiff enough
to push directly into a breadboard, but for the most reliable contact,
either (a) solder a short pin or male header onto each wire tip, or
(b) crimp/solder each wire into a female jumper that slides onto the
Feather's header pin. Match black → GND, white → A0, red → 3V.

| #4046 cable wire | Feather pin |
|-------------------|-------------|
| Black (GND) | GND |
| White (Audio / signal) | A0 |
| Red (VIN) | 3V |

**Option S2 piezo (#2915 + #2790 + #1740/#1739)** — the piezo's bare
leads go into the #2790 plug's screw terminals (red/+ → Tip, black/− →
Sleeve). The #2790 plug then plugs into the #2915 jack. On the Feather
side, two short F-F jumper wires from the #2915 terminals to header pins:
Tip terminal → **A0**, Sleeve terminal → **GND**. No resistor, no cap.

**PAM8302 amplifier (#2130) + speaker** — same pin mapping as the STEMMA
Speaker (A0, 3V, GND), but soldered to the amp's A+ / VIN / GND pads first.
Speaker connects to the amp's two output terminals (polarity not critical).

#### If your Feather has no header pins (bare PCB pads)

The tinned ends of the #4046 cable have nothing to plug into on a header-
less Feather. You have two practical paths — pick one. Both require a
small soldering job **on the Feather**, but neither is harder than
soldering header pins.

**Path 1 — Solder the speaker wires directly to the Feather (recommended)**

Cleanest, lowest profile, and the most permanent.

1. Identify the **A0**, **3V**, and **GND** pads on the Feather (printed on
   the underside).
2. Plug the #4046 cable's JST PH socket end into the #3885 speaker. The
   other end of #4046 already has three tinned bare wires — no cutting
   needed. (For the Option S2 piezo build, strip two short wires for the
   #2915 → Feather link; the piezo itself stays attached to the #2790
   plug via screw terminals. For PAM8302, solder the wires to the amp's
   A+ / VIN / GND pads first.)
3. Trim each tinned wire to ~15 cm if longer than you need, and re-tin
   the cut ends with a touch of solder.
4. Tin each Feather pad with a touch of solder.
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
   - Option S2 piezo (#2915 + #2790 + piezo) — two F-F jumpers from the
     #2915 jack's Tip and Sleeve screw terminals to the Feather's A0
     and GND pins. The piezo itself attaches to #2790's screw terminals.
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

| Feather has headers? | #3885 + #4046 cable | Option S2 piezo (#2915 + #2790 + #1740/#1739) | PAM8302 + speaker |
|---|---|---|---|
| **Yes (breadboard or pins)** | Tin/cap 3 wire ends, push into breadboard rows for A0/3V/GND, or use F-F jumpers | 2 F-F jumpers from #2915 (Tip / Sleeve) → A0 / GND pins. Piezo wired to #2790 by screw terminals. **Zero soldering.** | Wire amp to A0/3V/GND via breadboard or F-F jumpers |
| **No (bare pads)** | Solder #4046 tinned wires directly to A0/3V/GND pads | Solder 2 wires from #2915 (Tip / Sleeve) screw terminals to Feather A0 / GND pads. Piezo side still screw-terminal. | Solder amp board to A0/3V/GND pads |

---

### Step 8E — Set up the wireless display board hardware (optional)

Skip this step if you are not using a wireless display. Software setup
for the receiver is covered separately in **§9.4.1**.

#### Option W1 — Second Reverse TFT Feather

No hardware assembly needed — the board ships ready to power on. Mount
the second Feather face-up where you can see the TFT. Once §9.4.1 is
complete it will start mirroring the main board's display within one
second of either board powering on.

Power source: any USB-C phone charger, USB power bank, or one of the
LiPoly batteries listed in §5 Option W1.

#### Option W2 — XIAO ESP32C3 + OLED

Solder four short wires between the XIAO and the OLED's 4-pin header:

| OLED pin | XIAO pin |
|----------|---------|
| VCC | 3V3 |
| GND | GND |
| SCL | D3 (SCL) |
| SDA | D2 (SDA) |

That's the only assembly. Software setup (CircuitPython firmware, the
one-line I²C edit, and copying receiver files) is in **§9.4.1 Option W2**.

Power source: any USB-C phone charger or USB power bank. The XIAO has
no battery connector — Option W1 is the only battery-capable receiver.

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

**Always copy these — REQUIRED for every build (including the built-in TFT
on #5691 / #5483 / #5300):**

```
adafruit_hid/                 ← entire folder
adafruit_bus_device/          ← entire folder
adafruit_register/            ← entire folder
adafruit_display_text/        ← entire folder  — needed for ALL builds
neopixel.mpy
```

> **Don't skip `adafruit_display_text/` if you have a built-in TFT.** Even
> though `#5691 / #5483 / #5300` don't need a separate display *driver*
> library (the display is already initialised via `board.DISPLAY`), every
> build still uses `adafruit_display_text` to render the group name, Morse
> buffer, last action, and status line. Missing this folder is the most
> common installation mistake — `code.py` fails immediately at import with
> `ImportError: no module named 'adafruit_display_text'`.

**Copy these if using the sip-and-puff sensor:**

```
adafruit_lps35hw.mpy
```

**Copy ONE of these only if you have an external display:**

| Display | Additional driver file |
|---------|------------------------|
| OLED #326 or #938 | `adafruit_displayio_ssd1306.mpy` |
| TFT #3651, #5872, #2050 | `adafruit_hx8357.mpy` |
| TFT #3315, #1770, #1743 | `adafruit_ili9341.mpy` |
| TFT #4311 | `adafruit_st7789.mpy` |
| Built-in TFT (#5691 / #5483 / #5300) | *no extra driver — uses `board.DISPLAY`* |

> You only need the items listed above — you do not need to copy the entire
> bundle, which is very large.

---

### Step 9.3 — Install Thonny and watch the serial console

Before copying the AeroMorse project files in §9.4, install **Thonny** —
a free, beginner-friendly code editor that doubles as a serial console.
The serial console is how the Feather reports errors when it tries to
load `code.py`, the libraries, or `morse_map.py`. **Without watching the
console, a problem in §9.4 looks like "nothing happens" instead of a
specific error message you can act on.**

#### Step 9.3.1 — Download and install Thonny

1. Go to **https://thonny.org** and click the download button for your
   operating system (Windows, macOS, or Linux).
2. Run the installer. No special options are needed — accept defaults.
3. Launch Thonny after installation completes.

> Mu Editor was previously recommended by Adafruit but has announced
> end-of-life in 2026. Thonny is the current recommended alternative.

#### Step 9.3.2 — Confirm the Feather is plugged in

The Feather should still be connected from §9.1 / §9.2. The **CIRCUITPY**
drive must be visible in File Explorer (Windows) or Finder (Mac). If it
isn't, unplug and replug the USB-C cable.

#### Step 9.3.3 — Point Thonny at CircuitPython

1. In Thonny, click **Run → Configure interpreter…**
   (or click the interpreter name shown at the bottom-right of the
   Thonny window).
2. In the top dropdown, select **CircuitPython (generic)**.
3. In the **Port** dropdown, select the port your Feather is on:
   - **Windows:** a COM port, e.g. `COM3` or `COM7` — try each if unsure
   - **macOS:** something like `/dev/cu.usbmodem14101`
   - **Linux:** something like `/dev/ttyACM0`
4. Click **OK**.
5. The bottom **Shell** panel should now show `>>>` — this is the REPL
   prompt, confirming Thonny is talking to the Feather.

> **Can't find the right port?**
> Windows: open Device Manager → Ports (COM & LPT) — the Feather appears
> as "USB Serial Device" or "CircuitPython CDC Control".
> Mac: open Terminal and type `ls /dev/cu.*` — look for `usbmodem`.

#### Step 9.3.4 — Leave the Shell panel visible

The Shell panel at the bottom of the Thonny window will display
everything `code.py` prints (errors, calibration messages, debug output).
Keep this panel visible while you complete §9.4. If a file copy fails,
or a library is missing, the Shell will print an exact error message
naming the file and line number — much easier to act on than guessing.

A healthy startup after §9.4 looks like this in the Shell:

```
Calibrating — do not sip or puff ...
Baseline: 1013.241  sip<1008.241  puff>1018.241
```

If you see a red `Traceback (most recent call last):` line instead, the
last line of the traceback names the problem (e.g.
`ImportError: no module named 'adafruit_lps35hw'` — means that library
file is missing from `/lib`; re-do §9.2). Note: in some Thonny versions
tracebacks render in plain text rather than red.

#### Step 9.3.5 — Capturing a fresh boot trace (Ctrl+D)

The Shell panel only shows messages that fire *while Thonny is
listening*. The first time you connect, the device has usually already
booted — the `Calibrating…` and `Baseline:` lines you want to see have
already scrolled past. You don't need to physically replug the cable or
hit a reset button to recapture them.

**Click in the Shell panel, then press Ctrl+D.** That sends a CircuitPython
"soft reset" — the device re-runs `boot.py` and `code.py` from scratch
and prints everything to the Shell as it happens. Use it any time you:

- want to see the boot output again,
- have edited `code.py` and want a clean restart (saving normally
  triggers an auto-reload, but Ctrl+D gives you a confirmed clean run),
- need to capture a traceback for diagnosing a problem.

**A healthy Ctrl+D in sensor mode looks like:**

```
soft reboot
Auto-reload is on. ...
code.py output:
Calibrating — do not sip or puff ...
Baseline: 1013.241  sip<1008.241  puff>1018.241
Input mode: 2-switch  (1-sw input = dot, 3-sw accept = long_dash)
Code repeat: off  long-press cycles group: True
ESP-NOW: disabled by USE_WIRELESS_DISPLAY = False
```

> If `ESP-NOW: init failed (ESP-NOW error 0x3065)` shows up, that's a
> known CircuitPython 9.0.3 bug — see §12 "Wireless display" for the
> workaround.

#### Useful Thonny shortcuts

| Action | Shortcut |
|--------|---------|
| Save file (and trigger Feather restart) | Ctrl+S / Cmd+S |
| Stop running program / go to REPL | Ctrl+C (in Shell) |
| Restart program from REPL | Ctrl+D (in Shell) |
| Open file from CIRCUITPY drive | File → Open → CircuitPython device |

> Further Thonny details (REPL examples, alternative editors like VS
> Code) are in `TOOLS_AND_GUIDES.md`.

---

### Step 9.4 — Copy the AeroMorse project files

> **Filenames must be exact.** CircuitPython looks for `code.py`,
> `boot.py`, and `morse_map.py` by *literal* name. If you copy a file as
> `morse_map_darci.py` (or any other variant name) it will be ignored —
> `code.py` does `from morse_map import groups`, and that import resolves
> only to a file named `morse_map.py`. **Rename the file to `morse_map.py`
> *before* or *after* copying** — see the Darci callout below.

**Which `code.py` to use depends on your Feather board:**

| Board | Copy `code.py` from |
|-------|-------------------|
| #5483 ESP32-S3 TFT Feather | `v1/` folder — uses built-in display |
| #5691 ESP32-S3 Reverse TFT Feather | `v1/` folder — uses built-in display |
| #5300 ESP32-S2 TFT Feather | `v1/` folder — uses built-in display |
| All other boards | `v2/` folder — uses external display |

Copy these three files to the **root** of the CIRCUITPY drive (not inside any
subfolder). Take `code.py` from the correct folder for your board (above), and
`boot.py` and `morse_map.py` from either folder — they are identical:

```
boot.py
code.py
morse_map.py
```

> **If you are a Darci USB user starting from `morse_map_darci.py`:**
> Copy `morse_map_darci.py` to the CIRCUITPY drive, then **rename it to
> `morse_map.py`** (right-click → Rename on Windows/Mac, or `mv` on
> Linux). Do not leave both files on the drive — CircuitPython will only
> load the one literally named `morse_map.py`, and a stale extra file
> just wastes flash.

The CIRCUITPY drive should now look like this:

```
CIRCUITPY/
├── boot.py
├── code.py
├── morse_map.py
└── lib/
    ├── adafruit_hid/                       (always — keyboard/mouse HID)
    ├── adafruit_bus_device/                (always — required by sensor + display libs)
    ├── adafruit_register/                  (always — required by sensor + display libs)
    ├── adafruit_display_text/              (always — text labels on the screen)
    ├── neopixel.mpy                        (always — onboard NeoPixel)
    ├── adafruit_lps35hw.mpy                (only if using sip-and-puff sensor)
    ├── adafruit_displayio_ssd1306.mpy      (only if using OLED #326 or #938)
    ├── adafruit_hx8357.mpy                 (only if using TFT #3651, #5872, or #2050)
    ├── adafruit_ili9341.mpy                (only if using TFT #3315, #1770, or #1743)
    └── adafruit_st7789.mpy                 (only if using TFT #4311)
```

> Built-in TFT boards (#5691 / #5483 / #5300) get nothing extra from the
> per-display list — `board.DISPLAY` is initialised by the firmware, so
> no driver `.mpy` is needed. They still need every "always" entry above.

**Safely eject the CIRCUITPY drive** before unplugging. The Feather reboots and
runs the code automatically.

> The first boot after copying `boot.py` takes a few extra seconds. This is
> normal — the board is negotiating USB HID with the host. If nothing seems to
> happen, unplug and replug the USB cable once.

---

### Step 9.4.1 — Software for the Wireless Display receiver (optional)

Skip this step if you are not using the ESP-NOW wireless display
(§5 "Wireless Display — ESP-NOW Remote Mirror"). The main board you set
up above is already fully functional.

The receiver is a **second** board that runs entirely independently of
the main board — its own CircuitPython firmware, its own `code.py`, its
own `/lib` folder. It listens for ESP-NOW broadcasts from the main board
and mirrors the four display fields on its own screen. It does **not**
act as a keyboard or mouse; you do not load `morse_map.py` or
`adafruit_hid` on it.

#### Files on the receiver

| File on your computer | Copy to the receiver as |
|----------------------|------------------------|
| `receiver.py` | `code.py` (rename when copying) |
| `receiver_boot.py` | `boot.py` (rename when copying) |

> **`receiver_boot.py` deliberately disables USB HID on the receiver.**
> Without renaming it to `boot.py` on the receiver, Windows / macOS /
> Linux will see the second board as a duplicate keyboard and try to
> type from it as well.

> **Do NOT copy `morse_map.py` to the receiver.** The receiver only
> draws what the main board sends — no Morse decoding happens on it.

#### Firmware on the receiver (Step 9.1 equivalent)

Install CircuitPython on the receiver the same way you did on the main
board in §9.1. The receiver needs **at least CircuitPython 9** so the
`espnow` module is included. The main board and the receiver do **not**
need to be on the same CircuitPython major version — see §12 "Wireless
display → CircuitPython versions on the two boards" for the details.

---

#### Option W1 — Second ESP32-S3 Reverse TFT Feather #5691 (recommended)

```
CIRCUITPY/    (on the W1 receiver)
├── boot.py                        (= renamed copy of receiver_boot.py)
├── code.py                        (= renamed copy of receiver.py)
└── lib/
    └── adafruit_display_text/     (only library needed)
```

Just **two files** at the root plus **one library folder** under `/lib`.
Nothing else. The built-in TFT is initialised via `board.DISPLAY` so no
display-driver `.mpy` is needed.

> `adafruit_hid/`, `adafruit_bus_device/`, `adafruit_register/`,
> `neopixel.mpy`, and `adafruit_lps35hw.mpy` are **not** required on the
> receiver — leaving them off saves flash and avoids confusion.

---

#### Option W2 — Seeed XIAO ESP32C3 + SSD1306 OLED

The XIAO has no STEMMA QT port. Before copying `receiver.py`, edit it
once to switch I²C from STEMMA QT to bit-banged D2/D3 pins. See
§5 "Option W2" for the exact one-line change.

```
CIRCUITPY/    (on the W2 receiver)
├── boot.py                                (= renamed copy of receiver_boot.py)
├── code.py                                (= renamed and edited copy of receiver.py)
└── lib/
    ├── adafruit_display_text/             (always)
    └── adafruit_displayio_ssd1306.mpy     (only — SSD1306 OLED driver)
```

Two files at the root plus one library folder and one driver `.mpy`
under `/lib`.

---

#### Verifying the receiver

1. Plug the receiver into a USB-C power source.
2. Within ~1 second of the **main board** booting, the receiver's
   display should mirror the four display fields (group, Morse buffer,
   last action, status).
3. If it stays blank or shows "No signal", open the receiver in Thonny
   and check the Shell — `ImportError` messages name the missing file.
   See §12 "Wireless display" for the full diagnostic table.

---

## 10. Configuration

Open `code.py` in Thonny (§9.3) or any plain-text editor (Notepad, TextEdit,
VS Code). Look for the configuration section near the top of the file.

### Key settings

| Setting | Default | What to change |
|---------|---------|----------------|
| `USE_SENSOR` | `True` | Change to `False` if using AT switches |
| `THRESH_SIP` | `5` | Raise to `8` or `10` if getting false triggers; lower to `3` if light sips are missed |
| `THRESH_PUFF` | `5` | Same as above but for puff/dash |
| `ACCEPT_DELAY` | `0.5` | Idle pause (seconds) after the last element before the pattern fires. Lower (0.3) for fast users; higher (0.7) for sip-and-puff users with slower breath rhythm. In 3-switch mode this is a safety-net timeout; the third-switch gesture commits instantly regardless. |
| `LONG_PRESS` | `1.0` | Hold time in seconds for the long-gesture (cycle / Accept). Raise if accidentally triggering |
| `SWITCH_MODE` | `2` | `1` = single-switch timed; `2` = paddle (dot + dash); `3` = paddle + explicit Accept. See "Input modes" below. |
| `ONE_SWITCH_INPUT` | `"dot"` | 1-switch mode only — `"dot"` uses the sip / D5 input; `"dash"` uses the puff / D6 input |
| `ONE_SWITCH_DOT_MS` | `200` | 1-switch mode only — press ≤ this is a dot; longer is a dash; ≥ `LONG_PRESS`×1000 cycles group |
| `THIRD_SWITCH_GESTURE` | `"long_dash"` | 3-switch mode only — `"long_dash"` makes long-puff the Accept switch; `"long_dot"` makes long-sip the Accept switch |
| `CODE_REPEAT` | `False` | `True` enables Darci-style hold-to-repeat — while DIT/DAH is held, one symbol fires per `DOT_REPEAT_MS` / `DASH_REPEAT_MS`. Release ends the stream. Only honoured when `SWITCH_MODE = 2`. |
| `DOT_REPEAT_MS` | `200` | ms between auto-repeated dots (`CODE_REPEAT` only) |
| `DASH_REPEAT_MS` | `600` | ms between auto-repeated dashes (`CODE_REPEAT` only — conventionally 3 × dot) |
| `CODE_REPEAT_MAX` | `8` | Cap on symbols per held stream — prevents buffer overflow on a forgotten hold |
| `LONG_PRESS_CYCLES_GROUP` | `True` | `False` disables the long-press group cycle gesture (DIT-side = cycle back, DAH-side = cycle forward). Switch groups via g0 Morse patterns instead. Recommended `False` alongside `CODE_REPEAT = True`. |
| `DISPLAY_ROTATION` | `0` | `0` = USB port on left; `180` = USB port on right (`90` / `270` also valid) |
| `USE_WIRELESS_DISPLAY` | `False` | `True` enables the ESP-NOW broadcast for an Option W1 / W2 receiver. Default is off because most builds don't include a second board — flip to `True` only when you actually have a receiver paired. Adds ~80–100 mA when on. |
| `BEEP_DOT_FREQ` | `1200` | Pitch in Hz for dot (sip) beeps — higher pitch |
| `BEEP_DASH_FREQ` | `800` | Pitch in Hz for dash (puff) beeps — lower pitch |

### Input modes — what `SWITCH_MODE` does

| Mode | Behaviour | Group cycling |
|---|---|---|
| **1** | Only `ONE_SWITCH_INPUT` is active. Press ≤ `ONE_SWITCH_DOT_MS` (200 ms) = dot, longer = dash. Pause `ACCEPT_DELAY` = end-of-letter. | Long-press (≥ `LONG_PRESS`) cycles forward. **No backward cycle** — use a g0 Morse pattern. |
| **2** *(default)* | Dot input = dot, dash input = dash. Pause `ACCEPT_DELAY` = end-of-letter. | Long-press dot = cycle back; long-press dash = cycle forward. |
| **3** | Dot input = dot, dash input = dash. **Explicit Accept**: long-press of `THIRD_SWITCH_GESTURE` commits immediately. | Long-press of the *other* gesture cycles forward. **No backward cycle** — use a g0 Morse pattern. |

For a side-by-side comparison of how AeroMorse, Darci USB, morAce, and
Adap2U each implement 1/2/3-switch input, see
`MORSE_DEVICES_COMPARISON.md`.

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

Grouped by hardware option, in the same order as §4 – §6 (Input → Display
→ Speaker → Wireless display → Software / general).

---

### Input — sip-and-puff sensor (#4414)

**"Calibrating" message hangs at startup**
- The LPS33HW was not found. Check the STEMMA QT cable between the Feather
  and the sensor — both connectors must click in firmly.
- Confirm `adafruit_lps35hw.mpy` is in `/lib` on the CIRCUITPY drive.

**False pressure triggers (random dots/dashes while not sipping or puffing)**
- Raise `THRESH_SIP` and `THRESH_PUFF` to 8 or 10 in `code.py`.
- Check the sip-and-puff tube is not kinked or pinched.

---

### Input — AT switches

**AT switches not registering**
- Confirm `USE_SENSOR = False` in `code.py`.
- Test the switch with a multimeter in continuity mode: pressing the
  switch should beep, confirming Tip connects to Sleeve.
- Confirm D5 (dot) and D6 (dash) wires are connected to the correct
  jack pins.

---

### Input — timing

**Pattern fires too early (cuts off long patterns)**
- Raise `ACCEPT_DELAY` from `0.2` to `0.3` or `0.4` in `code.py`.

**Groups cycle when you did not mean to**
- Raise `LONG_PRESS` from `1.0` to `1.5` or `2.0` to require a longer hold.

---

### Display

**Display is blank or white**
- Check that you are running the correct version of `code.py` for your
  display. The v2 code expects the OLED #326 by default. If you have a TFT
  FeatherWing, the display initialisation in `code.py` must be updated.
- For the OLED: check both ends of both STEMMA QT cables are fully
  clicked in.
- Try changing `device_address=0x3C` to `device_address=0x3D` if the OLED
  stays blank — some OLEDs use the alternate address.

---

### Speaker

**No sound from the STEMMA Speaker (or any speaker option)**
- Verify wiring: Audio → A0, VIN → 3V, GND → GND.
- Confirm the #4046 cable is fully seated in the #3885 speaker's JST PH
  socket — this is the most common cause of silent speakers.
- Open the serial console in Thonny (§9.3). If you see
  `WARNING: pwmio module not available`, you are running an unusual
  minimal CircuitPython build — `pwmio` is present in every standard
  build for every supported board. Re-flash with the standard `.uf2`
  from circuitpython.org/downloads.
- The audio is a square wave (not a sine), so the tone will sound
  slightly buzzy — that is expected and not a defect.

---

### Wireless display (ESP-NOW)

**Wireless display shows "No signal"**
- Confirm both boards are powered and running CircuitPython 9.x or later.
- Check the serial console on the main board. It should print
  `ESP-NOW: wireless display active (broadcast)` at startup.
  - `ESP-NOW: disabled by USE_WIRELESS_DISPLAY = False` → flip the
    `USE_WIRELESS_DISPLAY` flag back to `True` in `code.py` (§10).
  - `ESP-NOW: module not available on this board` → the board is not
    an ESP32 (e.g., RP2040, M4, nRF52840). Wireless display requires
    an ESP32-family board.
  - `ESP-NOW: init failed (...)` → see entry below.
- Range is approximately 30 m indoors. Move the boards closer to test.
- Channel mismatch: see "How the ESP-NOW channel is selected" below.

**How the ESP-NOW channel is selected**

AeroMorse does **not** set an ESP-NOW channel explicitly. Both boards
run the equivalent of:

```python
wifi.radio.enabled = True              # turn on the radio
espnow.ESPNow()                        # open ESP-NOW on it
# main board only:
peers.append(Peer(mac=b'\xff'*6))      # broadcast peer, channel default
```

ESP-NOW always operates on whatever channel the WiFi radio is currently
tuned to. When the radio is enabled but **not** joined to a network,
both ESP32 chips sit on **channel 1** — the firmware default. That is
why no configuration is needed in the typical AeroMorse build: both the
main board and the receiver come up on channel 1 and find each other
automatically.

**Things that move the channel away from 1:**
- One board joins a WiFi network (`wifi.radio.connect(...)` in your own
  code). The radio retunes to that network's channel and ESP-NOW
  follows. If the other board didn't also connect to the same network,
  they lose sync.
- A captive-portal or provisioning library that calls `connect()`
  silently.
- Manually setting `Peer(mac=..., channel=N)` on the main board while
  the receiver is still on channel 1.

**To force a specific channel** (only needed if the default isn't
working — e.g., heavy WiFi interference on channel 1):
1. On the **main board**, edit the `Peer(...)` line in `code.py`:
   ```python
   _espnow_dev.peers.append(
       _espnow_mod.Peer(mac=b'\xff\xff\xff\xff\xff\xff', channel=6)
   )
   ```
2. On the **receiver**, add this line in `receiver.py` *after*
   `wifi.radio.enabled = True`:
   ```python
   wifi.radio.start_station()           # if not already in station mode
   # the radio is now on whatever channel ESP-NOW will use; no further
   # channel command is needed because the receiver listens on the
   # radio's current channel.
   ```
   In practice the receiver picks up the sender's channel as soon as
   the first broadcast arrives, so explicit station-mode setup is
   usually unnecessary — but force it if signal is intermittent.
3. Both boards must use the **same** channel number. Valid 2.4 GHz
   channels are 1 – 13 (1, 6, 11 are the non-overlapping ones).

**Wireless display is frozen / not updating**
- The receiver updates whenever a packet arrives (10× per second). If the
  display updates briefly then freezes, the main board may have
  restarted. Check the main board's serial console for errors.

**Main board serial console shows `ESP-NOW: init failed`**
- The `wifi` module initialisation failed. Try power-cycling the main
  board. Rarely, the WiFi radio needs a cold boot (unplug power
  completely rather than pressing Reset).

**`ESP-NOW: init failed (ESP-NOW error 0x3065)` on CircuitPython 9.0.x**
- 0x3065 decodes as `ESP_ERR_ESPNOW_NOT_INIT` — the underlying ESP-NOW
  subsystem wasn't ready when `ESPNow()` was constructed. This is a
  known bug in CircuitPython 9.0.x that was fixed in 9.1+. Two fixes:
  - **Easy:** set `USE_WIRELESS_DISPLAY = False` in `code.py` (§10) to
    skip ESP-NOW entirely. Acceptable if you don't need the wireless
    display.
  - **Best:** upgrade CircuitPython on the Feather to **9.2.x or 10.x**
    from circuitpython.org/downloads. The fix is included in those
    versions; leave `USE_WIRELESS_DISPLAY = True`.

**Wireless display acts as a second keyboard on Windows**
- The `receiver_boot.py` file was not copied as `boot.py` on the second
  board, or the original `boot.py` (which enables USB HID) is still on
  the second board. Replace `boot.py` on the second board with the
  contents of `receiver_boot.py`.

**Option W2 OLED stays blank**
- Check all four wires are connected to the correct pins on both the
  XIAO and the OLED.
- Try changing the I2C address in `receiver.py`: look for
  `device_address=0x3C` and change it to `device_address=0x3D`.
- Confirm `adafruit_displayio_ssd1306.mpy` and `adafruit_display_text/`
  are in the `/lib` folder on the XIAO.

**CircuitPython versions on the two boards**
- ESP-NOW sends plain bytes with no awareness of CircuitPython versions.
  Each board runs its own CircuitPython and its own `/lib` folder. You
  can have CP9 on the main board and CP10 on the receiver, or any
  combination — no steps are needed to make them work together. The only
  requirement is that **each board runs at least CP9** (earlier versions
  did not include the `espnow` module). There is no need to match
  versions, update one when you update the other, or do anything
  differently when the versions differ.
- **However:** if you copy the `/lib` folder from the main board to the
  receiver, both boards must be on the **same major version** (both CP9
  or both CP10) — `.mpy` library files compiled for one major version
  will not load under the other. If the boards are on different major
  versions, download the matching library bundle for each board
  separately from circuitpython.org and copy the files individually. The
  receiver only needs one folder from the bundle:
  `adafruit_display_text/`.

---

### Software / general

**REPL shows `ImportError`**
- A library file is missing from `lib/`. Re-read §9.2 and copy the
  missing file from the CircuitPython bundle. The most common one to
  miss is `adafruit_display_text/` — see the callout in §9.2.

**Nothing happens on the computer at all**
- Unplug and replug the USB cable.
- Confirm the cable is a data cable (a drive should appear when plugged
  in).
- Confirm `boot.py` is on the root of the CIRCUITPY drive.
- Confirm `morse_map.py` is named **exactly** `morse_map.py` (not
  `morse_map_darci.py` or similar) — `code.py` imports it by literal
  name. See §9.4.

---

## Appendix A — Groups and Group Cycling

AeroMorse has ten groups: g0 (always-available) plus g1–g9. Group 0 is
checked in the background on every keystroke (its 8-symbol patterns work
in any group). Groups 1–9 cycle with long-press, or you can jump straight
to any group with its 8-symbol Group 0 toggle code.

| Group | Contents | 8-symbol jump code | How to reach by cycling |
|-------|---------|-------------------|------------------------|
| 0 | Group-jump patterns (8 symbols) | — | Always active |
| 1 | Letters, numbers, punctuation, function keys | `........` | Power-on default |
| 2 | Mouse movement, clicks, Windows shortcuts | `--------` | Long-puff cycling |
| 3 | Macro text strings | `....----` | Long-puff cycling |
| 4 | Function keys F1–F12 on the 12 shortest codes (Switch Control on iOS / Android) | `.......-` | Long-puff cycling |
| 5 | Placeholder (copy of g1 letters + numbers) | `......--` | Long-puff cycling |
| 6 | Placeholder | `.....---` | Long-puff cycling |
| 7 | Placeholder | `...-----` | Long-puff cycling |
| 8 | Placeholder | `..------` | Long-puff cycling |
| 9 | Placeholder | `.-------` | Long-puff cycling |

**Long sip** (hold ≥ `LONG_PRESS` seconds) → cycle backward (…3→2→1→9→8…)
**Long puff** (hold ≥ `LONG_PRESS` seconds) → cycle forward (1→2→3→4→…→9→1…)

With 10 groups, cycling all the way around takes a while — the 8-symbol
Group 0 jump codes are the fast path to any group from anywhere. The
group-toggle codes use a "count of trailing dashes" scheme: 8 dots = g1,
then add trailing dashes to reach the higher groups (see `morse_map.py`
Group 0 comments for the full list). Group 4's F-keys make AeroMorse
usable as a Switch Control input on iOS and Android, where function keys
act as switch actions.

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

Detailed step-by-step instructions for **§4 Option B1 — Solderless breadboard**.
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
