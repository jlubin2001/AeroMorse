# AeroMorse vs. Darci USB — Comparison & Migration Guide

For users of the **WesTest Darci USB** considering or moving to **AeroMorse**.

This document compares the two devices feature-by-feature, calls out the
remaining gaps, and lists the AeroMorse config settings that reproduce
Darci behaviour. A companion file, `morse_map_darci.py`, provides a
Darci-style code set you can drop into AeroMorse to keep your existing
muscle memory.

For a broader comparison that also covers Adap2U and morAce, see
`MORSE_DEVICES_COMPARISON.md`.

---

## At a Glance

| | **Darci USB** | **AeroMorse** |
|---|---|---|
| Form factor | Dedicated enclosed box | Adafruit Feather board + breadboard (or off-the-shelf enclosure) |
| Output | USB HID | USB HID |
| Switch jacks | 3 × 3.5 mm mono | 2 × 3.5 mm (or sip-and-puff sensor) |
| Sip and puff | No (use external interface) | **Yes — built in** (#4414 pressure sensor) |
| Switch input modes | 1 / 2 / 3 switches (hardware) | **1 / 2 / 3 switch modes** (`SWITCH_MODE = 1/2/3`) — 3rd switch implemented as a long-press gesture on the existing 2 inputs |
| Hold-to-repeat (code repeat) | ✓ Built in | ✓ `CODE_REPEAT = True` — opt-in, independent dot / dash repeat intervals |
| Audio feedback | Headset jack, single tone | Built-in speaker, distinct dot/dash pitches (square wave via `pwmio`) |
| Visual feedback | Indicator LEDs (sticky-key status) | **OLED display** + optional wireless TFT for caregiver |
| Customization | CodeMaker program (Windows only, `.CST` files) | Plain-text `morse_map.py` — any editor on any OS |
| Host OS | Windows 98 → Windows 7 (32-bit) | **Windows / macOS / Linux / ChromeOS / iPad** — anything that takes USB HID |
| Cost | ~$1000+ commercial device | ~$50–$100 in parts |
| Source | Closed, EOL/hard to source | **Open source, ongoing** |
| Mouse control | Uses Windows' built-in Mouse Keys | Native USB HID mouse — no OS config required |

---

## 1. Switch input — now at parity with Darci

AeroMorse supports all three Darci input arrangements via the
`SWITCH_MODE` config setting in `code.py`:

| Darci mode | What it expects | AeroMorse support |
|---|---|---|
| **Single switch** | One switch; firmware times dot vs. dash | ✅ `SWITCH_MODE = 1` — press ≤ `ONE_SWITCH_DOT_MS` (default 200 ms) = dot; longer = dash; pause = end-of-character. `ONE_SWITCH_INPUT` picks which physical input (sip / D5 or puff / D6) is the sole switch. |
| **Double switch** | Switch 1 = dot, Switch 2 = dash | ✅ `SWITCH_MODE = 2` (default) — D5 = dot, D6 = dash. Pause `ACCEPT_DELAY` = end-of-character. |
| **Triple switch** | Switch 1 = dot, Switch 2 = dash, Switch 3 = end-of-character | ✅ `SWITCH_MODE = 3` — short presses still go to D5 (dot) / D6 (dash), and a **long-press gesture** on one of those inputs serves as the explicit Accept (end-of-character). `THIRD_SWITCH_GESTURE = "long_dash"` (default) makes a sustained puff the Accept; `"long_dot"` makes a sustained sip the Accept. |
| **Sip-and-puff** | Pressure sensor with external 2-switch adapter | ✅ Native (#4414 sensor, no adapter needed) |

**Note on triple-switch:** AeroMorse only has two *physical* inputs, so the
third "switch" is implemented as a gesture (a long-press on whichever input
you nominate). This preserves the *behavioural* benefit Darci's third
switch provides — explicit, timing-independent end-of-character — without
adding a third hardware jack. If a Darci user is muscle-memory-trained on
a physical third switch, the gesture is a substitute, not an exact match.

**Other input options Darci doesn't offer:** AeroMorse adds **code repeat**
(`CODE_REPEAT = True`) for Darci-style hold-to-repeat — see §8 below for
the full breakdown.

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
AeroMorse uses ten **groups** (g0 always-on plus g1–g9), each with its own
code map:

| Group | Role | Jump code (8 symbols) |
|---|---|---|
| **g0** | Always-available system codes | Detected on every keystroke (8-symbol codes — no false-trigger risk) |
| **g1** | Keyboard (letters, numbers, punctuation) | `........` |
| **g2** | Mouse / Windows shortcuts | `--------` |
| **g3** | Macros (or Number Mode in `morse_map_darci.py`) | `....----` |
| **g4** | Scanning — F1–F12 (Switch Control on iOS / Android) | `.......-` |
| **g5–g9** | Placeholders (copy of g1 letters + numbers — customise) | `......--` … `.-------` |

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

### Group-switching style — gestures vs. codes

AeroMorse's default is **gesture-based** group cycling: long-sip cycles back,
long-puff cycles forward. Darci is **code-based** — modes are entered with
explicit Morse command codes (e.g., `--.-.` enters Mouse Mode), not
gestures.

If you prefer Darci's all-codes approach, set `LONG_PRESS_CYCLES_GROUP =
False` in `code.py`. Long-press gestures then do nothing, and group
switching happens entirely through g0 Morse patterns:

| Group target | g0 pattern | Length |
|---|---|---|
| Group 1 (Keyboard) | `........` | 8 dots |
| Group 2 (Mouse) | `--------` | 8 dashes |
| Group 3 (Macros) | `....----` | 4 dots + 4 dashes |

This matches Darci's "modes are codes, not gestures" muscle memory while
keeping the 8-symbol patterns long enough that no normal letter or number
can be misread as a group change.

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
| Dot/dash tones | Same pitch | Different pitches (default 1200 Hz dot, 800 Hz dash — `BEEP_DOT_FREQ` / `BEEP_DASH_FREQ`) |
| Tone waveform | Sine (analog speaker driver) | Square wave (PWM via `pwmio` — slightly buzzy but clearly audible) |
| Command confirmation beep | Yes | Yes (`CONFIRM_FREQ`) |
| Group/Mode change tone | (per LED) | Distinct low tone (`GROUP_FREQ`) |
| Volume | Not adjustable | Not adjustable directly — set by speaker choice (#3885 has a built-in 1 W amp; piezo options are quieter) |
| On-board speaker | None — headset out only | #3885 STEMMA Speaker (Option S1), or piezo (S2), or PAM8302 amp + speaker (S3) |
| External speaker out | Headset jack | Add a 3.5 mm jack (#2915 TRRS Terminal Block) wired to A0/GND — any speaker that already terminates in a 3.5 mm mono plug plugs straight in (see Build Guide §6 Option S2) |
| Sticky-key indicator | LED on box | Text on OLED (`SHIFT`, `CTRL`, etc.) |
| Current character preview | None | OLED shows growing dot/dash sequence |
| Pressure bar | None (no sip-and-puff) | Magnitude-encoded fill bar on the TFT (green for puff, orange for sip) |
| Across-the-room display | None | Optional wireless TFT mirror via ESP-NOW (`USE_WIRELESS_DISPLAY = True`) |

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

## 8. Repeat (hold-to-repeat / code repeat)

Darci's "code repeat" behaviour — holding the switch produces a stream of
the same symbol — is now supported in AeroMorse via the `CODE_REPEAT`
config flag (default `False`). When enabled in `SWITCH_MODE = 2`:

- Tap (release within `DOT_REPEAT_MS`) → 1 symbol
- Hold ≥ 2 × `DOT_REPEAT_MS` → 2 symbols
- Hold ≥ 3 × `DOT_REPEAT_MS` → 3 symbols
- …capped at `CODE_REPEAT_MAX` (default 8) per held stream

| | Darci | AeroMorse (with `CODE_REPEAT = True`) |
|---|---|---|
| 1-switch repeat | `--` (rr) command | Inherent — `SWITCH_MODE = 1` duration already classifies dot vs. dash; longer hold yields a longer single press. (`CODE_REPEAT` is not honoured in `SWITCH_MODE = 1`.) |
| 2-switch repeat | Hold last switch after final dot/dash | `CODE_REPEAT = True` — hold DIT for a dot-stream, DAH for a dash-stream. Release ends the stream; the next press starts a new one. |
| Repeat rate — dots | One Setup value | `DOT_REPEAT_MS` (default 200 ms) |
| Repeat rate — dashes | Same Setup value | `DASH_REPEAT_MS` (default 600 ms) — **separately adjustable** from dot rate, unlike Darci |
| Repeat cap | Setup limits | `CODE_REPEAT_MAX` (default 8) — prevents buffer overflow if a hold lasts longer than intended |
| Dedicated repeat code | No | Yes: `..-..` repeats the last keystroke (independent of `CODE_REPEAT`) |
| Conflict with long-press group cycle | n/a (Darci doesn't use gesture group cycling) | Sustained dot-stream could hit `LONG_PRESS` (1 s) and cycle a group. Recommended: set `LONG_PRESS_CYCLES_GROUP = False` alongside `CODE_REPEAT = True` — use g0 Morse patterns to switch groups (matches Darci's behaviour exactly). |

**Recommended Darci-style configuration** (preserves muscle memory):

```python
CODE_REPEAT             = True   # hold-to-repeat
DOT_REPEAT_MS           = 200    # tune to user's rhythm
DASH_REPEAT_MS          = 600    # tune to user's rhythm
LONG_PRESS_CYCLES_GROUP = False  # group changes via g0 codes only
```

With this set, holding a sip emits dots at 5 per second; holding a puff
emits dashes at ~1.7 per second; group switches happen only when an
8-symbol g0 code is entered — exactly the Darci interaction model.

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
| 2 × 3.5 mm jacks (#1699 or #2915 each) | Dot switch (D5) / Dash switch (D6) |
| STEMMA QT chain | Pressure sensor (#4414), OLED (#326) |
| 3-pin speaker connector | On-board speaker out (A0 + 3V + GND) — #3885 STEMMA Speaker |
| Optional 3.5 mm audio jack (#2915) | External speaker out (A0 + GND) — accepts any 3.5 mm-plug piezo or small speaker. See Build Guide §6 Option S2. |
| USB-C | To computer |

**Darci accessories plug directly into AeroMorse with no rewiring:**

- Darci AT switches (3.5 mm mono plugs) → AeroMorse D5 / D6 jacks
- Any 3.5 mm-plug external speaker or piezo → AeroMorse #2915 audio
  jack wired to A0/GND

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

- ✅ You have a 1-, 2-, or 3-switch setup (all three are now supported)
- ✅ You want sip-and-puff input
- ✅ You use a Mac, Linux, ChromeOS, iPad, Android, or modern Windows machine
- ✅ You want active development, open source, and modern hardware
- ✅ You want a wireless remote display
- ✅ You value customizable macros beyond Darci's 4-character limit
- ✅ You want Darci-style hold-to-repeat (with separate dot / dash rates) —
  enable `CODE_REPEAT = True`
- ✅ You want Darci's code-based group switching — enable
  `LONG_PRESS_CYCLES_GROUP = False`
- ✅ Cost is a factor (~$50–100 in parts vs ~$1000+ when Darci was current)

## When Darci may still be the right choice

The functional gap has closed significantly with the addition of
`SWITCH_MODE`, `CODE_REPEAT`, and `LONG_PRESS_CYCLES_GROUP`. Reasons
Darci might still suit you:

- ⚠ You need **three separate physical jacks** for true mechanical
  3-switch input (AeroMorse's 3-switch mode uses a long-press gesture
  on the existing two inputs, not a third physical jack — see §1)
- ⚠ You are locked to an old Windows machine and existing CodeMaker
  `.CST` files
- ⚠ You need a fully enclosed, ruggedized commercial device with
  vendor warranty (AeroMorse is an open-source DIY build)
- ⚠ You require sine-wave audio output (AeroMorse uses square-wave
  PWM via `pwmio`, which sounds slightly buzzy compared to Darci's
  analog tone generator)

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

*Document version: 2.2  •  Updated for AeroMorse 1/2/3-switch modes,*
*CODE_REPEAT hold-to-repeat, LONG_PRESS_CYCLES_GROUP, pwmio audio, and*
*the restructured Option S2 (#2915 jack + #2790 plug + passive piezo —*
*solderless and removable; also accepts any 3.5 mm-plug speaker).*
*Project: https://github.com/jlubin2001/AeroMorse*
