# AeroMorse vs. Darci USB — Comparison & Migration Guide

For users of the **WesTest Darci USB** considering or moving to **AeroMorse**.

This document compares the two devices feature-by-feature, calls out the
real gaps (where AeroMorse cannot match Darci), and lists practical
workarounds. A companion file, `morse_map_darci.py`, provides a Darci-style
code set you can drop into AeroMorse to keep your existing muscle memory.

---

## At a Glance

| | **Darci USB** | **AeroMorse** |
|---|---|---|
| Form factor | Dedicated enclosed box | Adafruit Feather board + breadboard (or off-the-shelf enclosure) |
| Output | USB HID | USB HID |
| Switch jacks | 3 × 3.5 mm mono | 2 × 3.5 mm (or sip-and-puff sensor) |
| Sip and puff | No (use external interface) | **Yes — built in** (#4414 pressure sensor) |
| Switch inputs supported | 1 / 2 / 3 switches | 2 switches only |
| Audio feedback | Headset jack, single tone | Built-in speaker, distinct dot/dash pitches |
| Visual feedback | Indicator LEDs (sticky-key status) | **OLED display** + optional wireless TFT for caregiver |
| Customization | CodeMaker program (Windows only, `.CST` files) | Plain-text `morse_map.py` — any editor on any OS |
| Host OS | Windows 98 → Windows 7 (32-bit) | **Windows / macOS / Linux / ChromeOS / iPad** — anything that takes USB HID |
| Cost | ~$1000+ commercial device | ~$50–$100 in parts |
| Source | Closed, EOL/hard to source | **Open source, ongoing** |
| Mouse control | Uses Windows' built-in Mouse Keys | Native USB HID mouse — no OS config required |

---

## 1. Switch input — the one place AeroMorse cannot match Darci

Darci supports three input arrangements:

| Darci mode | What it expects | AeroMorse support |
|---|---|---|
| **Single switch** | One switch; firmware times dot vs. dash | ❌ Not supported |
| **Double switch** | Switch 1 = dot, Switch 2 = dash | ✅ Native (D5/D6 jacks) |
| **Triple switch** | Switch 1 = dot, Switch 2 = dash, Switch 3 = end-of-character | ❌ Not supported |
| **Sip-and-puff** | Pressure sensor with external 2-switch adapter | ✅ Native (#4414 sensor, no adapter needed) |

**Workaround for single-switch Darci users:**
Single-switch operation requires an external timing module that converts long
press → dash, short press → dot, pause → end-of-character. Off-the-shelf
options exist (e.g. Tecla, AbleNet timing relays), but the user experience
is not identical. If single-switch is essential, Darci or a software
solution like Morse-Code-Keyboard for iOS may be a better fit.

**Workaround for triple-switch Darci users:**
The third (end-of-character) switch is unnecessary in AeroMorse because
firmware always uses inter-symbol timing for character segmentation.
The two existing dot/dash switches map directly.

---

## 2. The mode model — Darci's "Modes" vs. AeroMorse's "Groups"

### Darci's model
Darci has one main code set plus several **modes** entered/exited with
**command codes**:

| Darci mode | Command code | What it does |
|---|---|---|
| Mouse Mode | `--.-.` (mr) | Mouse pointer & click codes active |
| Number Mode | (short toggle) | Single-symbol digits 0–9 |
| Keypad Mode | (short toggle) | Numeric keypad characters |
| Code Set | `----` | Switch between Main and Alternate code sets |

Modifiers (Shift, Ctrl, Alt, GUI) work as **sticky keys** — single tap
arms, double tap locks, third tap releases.

### AeroMorse's model
AeroMorse uses four **groups**, each with its own code map:

| Group | Role | Default activation |
|---|---|---|
| **g0** | Always-available system codes | Detected on every keystroke (very long 8-symbol codes — no false-trigger risk) |
| **g1** | Keyboard (letters, numbers, punctuation) | Default after boot |
| **g2** | Mouse / Windows shortcuts | `........` (8 dots) → g1, `--------` (8 dashes) → g2 |
| **g3** | Macros (or Number Mode in `morse_map_darci.py`) | `....----` |

Modifiers are sticky in the same single-tap-arms way Darci uses.

### Mental-model mapping

| Darci | AeroMorse |
|---|---|
| Main Code Set | Group 1 |
| Mouse Mode | Group 2 |
| Number Mode | Group 3 (in `morse_map_darci.py`) |
| Alternate Code Set | Swap `morse_map.py` files |
| `mr` command | g0 toggle code |
| Sticky shift | Same — single-tap modifier in g1 |

---

## 3. Code Set differences

### Letters and numbers — **identical**
A–Z and 0–9 in `morse_map_darci.py` use the same standard ITU Morse
patterns Darci does. Existing muscle memory transfers 100%.

### Default AeroMorse `morse_map.py` differs
The default AeroMorse map relocates two letters to free their codes for
high-frequency keys:
- `--` (standard M) → repurposed as **BACKSPACE**, M moved to `----`
- `-.-.` (standard C) → repurposed as **LEFT_CTRL**, C moved to `---.`

If you do not want this, use `morse_map_darci.py` instead — it keeps
M and C on their ITU codes and routes BACKSPACE/CTRL via Darci's
abbreviation-based extensions.

### Extension codes (F-keys, arrows, nav)
Darci uses **letter-pair mnemonics**: F1 = `e1` = `.` + `.----`, Tab =
`hn` = `....` + `-.`, Home = `nd` = `-.` + `-..`. These are preserved
in `morse_map_darci.py` so the mnemonics still work.

The default AeroMorse map uses different patterns chosen for ergonomic
length distribution (e.g. F-keys are 7-symbol patterns built around
`--` plus the digit). New users may find these easier; Darci veterans
will prefer `morse_map_darci.py`.

---

## 4. Mouse control

### Darci
- Enters Mouse Mode with `mr` (`--.-.`)
- Movement codes drive **Windows' Mouse Keys** — requires:
  - Accessibility Options → Mouse → enable Mouse Keys
  - NumLock On, Automatic Reset off
- Codes for: 8 directions, single/double/click-and-hold for left & right
- Works only on Windows (because it relies on the Windows Mouse Keys feature)

### AeroMorse
- Mouse Mode is **Group 2**
- Movement codes send **real USB HID mouse events** — works on any OS
- No OS configuration required
- Codes for: 8 directions in two speeds (small/large step), scroll up/down,
  single/double click L+R, click-and-hold (drag), drag toggle, mouse-state reset
- Repeatable: holding the same code repeats the action

### Migration note
A Darci user accustomed to single-step Mouse Keys behavior may find
AeroMorse's mouse smoother because:
- AeroMorse uses real mouse-pointer events (sub-pixel accuracy, full speed)
- No reliance on Windows' Mouse Keys acceleration curves
- Wraps to all OSes — same behavior on Mac, Linux, ChromeOS

---

## 5. Number Mode

### Darci
Number Mode provides short 1-and-2-symbol codes for digits and arithmetic
operators. Entered with the Number Mode command, exited automatically or
with the same command.

### AeroMorse default
No special number mode — numbers use standard 5-symbol Morse in g1.

### `morse_map_darci.py` provides Number Mode as g3
- Enter with `....----` (g0 toggle to g3)
- Exit with `.....` (5 dots) in g3 → back to g1
- Digits 1–4 on 2-symbol codes; 5–0 on 3-symbol; operators on 3- and 4-symbol

---

## 6. Audio and visual feedback

| | Darci | AeroMorse |
|---|---|---|
| Dot/dash tones | Same pitch | Different pitches (1200 Hz dot, 800 Hz dash) |
| Command confirmation beep | Yes | Yes |
| Group/Mode change tone | (per LED) | Distinct low tone |
| Volume | Not adjustable | Adjustable in firmware constants |
| Output | Headset jack | Built-in speaker (#3885) |
| Sticky-key indicator | LED on box | Text on OLED (`SHIFT`, `CTRL`, etc.) |
| Current character preview | None | OLED shows growing dot/dash sequence |
| Across-the-room display | None | Optional wireless TFT (#5691) |

---

## 7. Customization

### Darci — CodeMaker
- Closed Windows program
- `.CST` binary files
- Up to 126 redefinable codes; some codes (Mouse Mode, Code Set, Repeat,
  Sound Mode, Number Mode, Keypad) cannot be reassigned
- Macros: up to 4 characters per code

### AeroMorse — `morse_map.py`
- Plain Python text file
- Edit with any editor (Notepad, VS Code, even a phone)
- Unlimited codes (limited only by available patterns up to 8 symbols)
- Macros: any string, any keycode, or any keycode-tuple combination —
  no 4-character limit
- Companion tools:
  - **`aeromorse_visualizer.htm`** — generates printable cheat sheets
  - **`morse_map_analyzer.exe`** — audits for duplicates, conflicts, unused codes

---

## 8. Repeat

| | Darci | AeroMorse |
|---|---|---|
| 1-switch repeat | `--` (rr) command | N/A (no 1-switch mode) |
| 2-switch repeat | Hold last switch after final dot/dash | Hold last switch (dash-stream / dot-stream) |
| Dedicated repeat code | No | Yes: `..-..` repeats the last keystroke |
| Repeat delay/rate | Adjustable in Setup | Adjustable in firmware constants |

---

## 9. Hardware connections

### Darci
| Port | Use |
|---|---|
| 3 × 3.5 mm jacks | Dot / Dash / End-of-character switches |
| Audio out | Headset for feedback |
| USB-B | To computer |

### AeroMorse
| Port | Use |
|---|---|
| 2 × 3.5 mm jacks (#1699 each) | Dot switch (D5) / Dash switch (D6) |
| STEMMA QT chain | Pressure sensor (#4414), OLED (#326) |
| 3-pin speaker connector | Audio out (A0 + 3V + GND) |
| USB-C | To computer |

Existing Darci AT switches with 3.5 mm plugs work directly in AeroMorse's
#1699 jacks — no rewiring needed.

---

## 10. Migration checklist

For a Darci user moving to AeroMorse, in order:

1. **Build or obtain the hardware** — see `AEROMORSE_BUILD_GUIDE.md` or have a
   technical person follow `CAREGIVER_SETUP_GUIDE.md`.
2. **Decide on input style** — keep existing 2-switch setup, or try sip-and-puff.
3. **Decide on code set:**
   - To keep Darci muscle memory → install `morse_map_darci.py` (rename to `morse_map.py` on the CIRCUITPY drive).
   - To use AeroMorse's optimized defaults → keep the shipped `morse_map.py`.
4. **Print a cheat sheet** — open `aeromorse_visualizer.htm` in a browser,
   load your chosen `morse_map.py`, click Print.
5. **Practice** for a week with familiar codes (A–Z, 0–9) before learning
   any AeroMorse-specific extensions or group changes.
6. **Customize** — edit `morse_map.py` to bind your most-used macros to
   short patterns in g3.

---

## 11. When AeroMorse is the right choice

- ✅ You have a 2-switch setup or want sip-and-puff
- ✅ You use a Mac, Linux, ChromeOS, iPad, or modern Windows machine
- ✅ You want active development, open source, and modern hardware
- ✅ You want a wireless caregiver display
- ✅ You value customizable macros beyond Darci's 4-character limit
- ✅ Cost is a factor

## When Darci may still be the right choice

- ⚠ You need **single-switch timed input** (most important Darci-only feature)
- ⚠ You need **3-switch input** with a hardware end-of-character switch
- ⚠ You are locked to an old Windows machine and existing CodeMaker `.CST` files
- ⚠ You need a fully enclosed, ruggedized commercial device

---

## 12. Code accuracy

All codes in `morse_map_darci.py` are transcribed directly from the
Darci USB Owner's Manual (P/N 3001508, 6/13/02) — the Appendix
"Morse/Plus Listing" tables for Standard Characters, Sticky Keys,
Command Codes, Mouse Control Codes, Number Mode Codes, International
Keyboard Keys, and Keyboard Extensions.

The file has been verified by `morse_map_analyzer.py` to contain
zero duplicate codes and zero conflicts with Group 0.

If you spot a discrepancy against an actual Darci unit, please open
an issue on GitHub.

---

*Document version: 1.0  •  Project: https://github.com/jlubin2001/AeroMorse*
