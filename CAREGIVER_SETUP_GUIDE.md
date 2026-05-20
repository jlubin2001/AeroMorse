# AeroMorse — Caregiver Setup Guide

This guide walks you through assembling AeroMorse step by step.
No technical experience needed. Every step is described in plain language.

---

## Your Parts

| What it looks like | Name | Used for |
|--------------------|------|----------|
| Small green board, USB-C port on one short edge | **Main controller** (#5477) | Runs the AeroMorse program |
| Tiny green board with a tube port on top | **Pressure sensor** (#4414) | Detects sips and puffs |
| Small rectangular screen, 4-pin white connector | **OLED display** (#326) | Shows Morse letters and status |
| Small square speaker with short cable | **Speaker** (#3885) | Beeps for every dot and dash |
| Two small boards each with a headphone-style socket | **Switch jacks** (two #1699) | Plug in AT switches |
| White rectangular plastic board with rows of holes | **Breadboard** (#64) | Holds the switch jacks in place |
| Short wires — female socket on one end, pin on other | **Jumper wires** (#153) | Connect the controller to the jacks |
| Short cables with small white 4-pin plugs at each end | **STEMMA QT cables** | Connect sensor and display (plug-and-play) |
| Larger board, USB-C port, colour screen on front | **Wireless display** (#5691) | Shows AeroMorse status from across the room |
| USB-C cable | **Power / computer cable** | Connects controller to computer |

---

## ⚠️ Before You Start — Prerequisite Steps

**These steps require a soldering iron and are done once by a technical person.**
Once done, they never need to be repeated.

- [ ] Header pins soldered onto the main controller (#5477) so it can sit in the breadboard
- [ ] AeroMorse program loaded onto the main controller (#5477)
- [ ] Input mode set: **sensor mode** (sip-and-puff) or **switch mode** (AT switches)
- [ ] Wireless display program loaded onto the display board (#5691)

If all four boxes above are checked, continue to the next section.

---

## Putting It Together

### Step 1 — Place the breadboard

Set the breadboard flat on the desk. The short edges are at the left and right.
You will see:
- Numbers **1 to 30** along the top
- Letters **a b c d e** on the top half, and **f g h i j** on the bottom half
- A **gap** running left-to-right across the middle

```
        1   2   3   4   5   6  ...  28  29  30
        +---+---+---+---+---+---     ---+---+
   a  → | · | · | · | · | · |  · · ·  | · | · |
   b  → | · | · | · | · | · |  · · ·  | · | · |
   c  → | · | · | · | · | · |  · · ·  | · | · |
   d  → | · | · | · | · | · |  · · ·  | · | · |
   e  → | · | · | · | · | · |  · · ·  | · | · |
        ════════════ GAP ════════════════════
   f  → | · | · | · | · | · |  · · ·  | · | · |
   g  → | · | · | · | · | · |  · · ·  | · | · |
   h  → | · | · | · | · | · |  · · ·  | · | · |
   i  → | · | · | · | · | · |  · · ·  | · | · |
   j  → | · | · | · | · | · |  · · ·  | · | · |
        +---+---+---+---+---+---     ---+---+
```

> **Important:** All five holes in the same letter-row AND same number-column
> are connected to each other inside the board. That is how wires share a signal
> without touching — by sitting in the same row.

---

### Step 2 — Seat the main controller in the breadboard

The main controller (#5477) has two rows of metal pins along its long edges.
Press it firmly across the centre gap so the left-side pins go into row **e**
and the right-side pins go into row **f**, starting at column 1.

```
        1   2   3  ...  14  15  16  ...  30
   a  → | · | · |        | · |   |       | · |
   b  → | · | · |        | · |   |       | · |
   c  → | · | · |        | · |   |       | · |
   d  → | · | · |        | · |   |       | · |
   e  → [RST][3V][AREF][GND][A0]...  ← LEFT SIDE PINS
        ════════ GAP ══════════════════════════
   f  → [GND][EN][BAT][USB][D13][D12][D11][D10][D9][D6][D5][SCL][SDA]
   g  → | · | · |        | · |   |       | · |
   h  → | · | · |        | · |   |       | · |
   i  → | · | · |        | · |   |       | · |
   j  → | · | · |        | · |   |       | · |
```

> The pin labels are printed in tiny white text on the controller board itself.
> Look along both long edges — you will see **GND**, **A0**, **3V**, **D5**, **D6**
> and others. Use these labels to find the right columns in the steps below.

---

### Step 3 — Place the two switch jacks

Each switch jack (#1699) has three metal legs underneath.
Place them in the open area of the breadboard (columns 18–26), away from the controller.

- **Jack 1** (dot switch) — press into row **a–e** around columns 18–20,
  socket hole facing outward (toward the short right edge of the breadboard).
- **Jack 2** (dash switch) — press into row **a–e** around columns 22–24,
  socket hole also facing outward.

Press each jack firmly until all three legs are fully seated.

> **Which leg is which?**
> With the socket hole facing you, the three legs from left to right are:
> **TIP** (left) — **RING** (middle) — **SLEEVE** (right)
> You only use TIP and SLEEVE. RING is left with nothing connected.

---

### Step 4 — Wire the switch jacks to the controller

You will use four **female-to-male jumper wires** (#153).
The **female end** (socket) grips a pin on the controller.
The **male end** (bare pin) presses into a breadboard hole.

Pick four wires and make these four connections:

| Female end grips this controller pin | Male end goes into this breadboard hole |
|--------------------------------------|----------------------------------------|
| **D5** | Any open hole in the **TIP leg row** of Jack 1 |
| **D6** | Any open hole in the **TIP leg row** of Jack 2 |
| **GND** | Any open hole in the **SLEEVE leg row** of Jack 1 |
| **GND** | Any open hole in the **SLEEVE leg row** of Jack 2 |

> The controller has more than one GND pin — any of them work.
> You can use two wires from two different GND pins, or run one wire from
> GND to Jack 1's SLEEVE row and then a second short wire within the breadboard
> from that row to Jack 2's SLEEVE row.

---

### Step 5 — Connect the speaker

The speaker (#3885) has a short cable with **three colour-coded male pins** on the end:

| Wire colour | Label | Plug into |
|-------------|-------|-----------|
| White | Audio / Signal | Any open hole in the **A0** column of the breadboard (rows a–d) |
| Red | VIN / Power | Any open hole in the **3V** column of the breadboard (rows a–d) |
| Black | GND | Any open hole in the **GND** column of the breadboard (rows a–d) |

> The A0, 3V, and GND columns are where those controller pins are seated in
> row e. Any hole a–d in the same column connects to them automatically.

---

### Step 6 — Connect the sensor (sip-and-puff mode only)

> **Skip this step if using AT switches instead of sip-and-puff.**

Take a STEMMA QT cable — small, black, 4-pin white plugs at each end.

1. Plug one end into the **STEMMA QT port** on the controller (#5477).
   It is a small white socket on the short edge near the USB-C port.
2. Plug the other end into either STEMMA QT port on the **pressure sensor** (#4414).

The cable only fits one way. If it feels stiff, flip it 180° and try again.
Do not force it.

---

### Step 7 — Connect the OLED display

Take a second STEMMA QT cable.

1. Plug one end into the remaining open STEMMA QT port on the **sensor** (#4414).
2. Plug the other end into the STEMMA QT port on the **OLED display** (#326).

The sensor and display are now chained together on the same cable line:

```
Controller (#5477) ── cable ── Sensor (#4414) ── cable ── Display (#326)
```

---

### Step 8 — Connect to the computer

Plug a USB-C cable into the **main controller** (#5477) and into the computer.

Within a few seconds:
- The OLED display will light up and show **[Keyboard]**
- In **sip-and-puff mode**: the device calibrates for 3–5 seconds (keep the
  tube still, do not sip or puff). A short beep means it is ready.
- In **switch mode**: the device is ready immediately with a beep.

The computer will recognise it as a keyboard and mouse — no driver installation needed.

---

### Step 9 — Set up the wireless display (optional)

The wireless display board (#5691) requires no wiring to the main controller.

1. Plug a USB-C cable into the **wireless display board** (#5691).
2. Connect the other end to any USB power source — a phone charger, power bank,
   or a spare USB port on the computer.
3. The colour screen will light up within a few seconds and automatically show
   what the main controller is displaying.

The two boards communicate wirelessly. No cables run between them.

---

## Fully Assembled — What It Should Look Like

```
                        [OLED Display #326]
                              │ STEMMA QT cable
                        [Sensor #4414]
                              │ STEMMA QT cable
[Speaker #3885] ─── A0 / 3V / GND
                     │
            [Controller #5477 in breadboard]
             D5 ── TIP ──[Jack 1 #1699]◄── dot switch
             D6 ── TIP ──[Jack 2 #1699]◄── dash switch
             GND ─ SLEEVE (both jacks)
                              │ USB-C cable
                          [Computer]

     (wireless, no cable)
   [Wireless Display #5691] ◄╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌ [Controller]
          │ USB-C power
    [Phone charger or power bank]
```

---

## Daily Use

Each time AeroMorse is needed:

1. Plug the **main controller** (#5477) into the computer with the USB-C cable.
2. Wait for the OLED to show **[Keyboard]** and one short beep.
   - Sip-and-puff mode: keep tube still for 3–5 seconds during the beep.
   - Switch mode: ready immediately after the beep.
3. Open any program on the computer (text editor, browser, etc.) and start using.
4. If using the wireless display, plug it into its power source separately.

**To switch off:** simply unplug the USB-C cable from the controller.

---

## If Something Is Not Working

| What you see | What to check |
|--------------|---------------|
| OLED display stays dark | USB-C cable not fully plugged in at both ends |
| Display shows an error message | Unplug, wait 5 seconds, plug back in |
| Switches do not respond | Female socket ends not firmly gripped on D5 / D6 / GND pins — press each socket firmly onto its pin |
| Speaker makes no sound | Check the three speaker cable pins — white in A0 column, red in 3V column, black in GND column |
| Sensor not detected | Re-seat both STEMMA QT cable connectors — push each white plug firmly until it clicks |
| Wireless display shows "No signal" | Make sure the main controller is plugged in and running first; move the two boards closer together |
| Wireless display shows nothing | Unplug and re-plug its USB-C power cable |
| Computer does not see keyboard / mouse | Check that the correct program (code.py) was loaded by the technical person |

---

## Quick Reference — Pin Connections

| Signal | Controller pin | Goes to |
|--------|---------------|---------|
| Dot switch | D5 | TIP leg of Jack 1 (#1699) |
| Dash switch | D6 | TIP leg of Jack 2 (#1699) |
| Ground | GND | SLEEVE leg of both jacks |
| Speaker signal | A0 | White wire on speaker cable |
| Speaker power | 3V | Red wire on speaker cable |
| Speaker ground | GND | Black wire on speaker cable |
| Sensor + display | STEMMA QT port | STEMMA QT cable chain |
