# Morse HID Devices — AeroMorse vs Adap2U vs Darci USB vs morAce

A side-by-side comparison of four Morse-code keyboard-emulator devices.
The goal is to help a builder, caregiver, or AAC professional pick the
right device for a user's needs — or, for a Darci / Adap2U user
considering AeroMorse, to see exactly what carries over and what
changes.

Companion documents:
- **`AEROMORSE_VS_DARCI.md`** — deep dive on Darci-to-AeroMorse migration
  (full code-set mapping, mode-model translation, code-set file
  `morse_map_darci.py` notes).
- **`AEROMORSE_BUILD_GUIDE.md`** — how to actually build AeroMorse.

---

## At a glance

| | **Adap2U** | **Darci USB** | **morAce** | **AeroMorse** |
|---|---|---|---|---|
| Vendor | AdapTek Interface | WesTest Engineering | Ace Centre | Open-source (Jim Lubin) |
| Status | EOL (1990s era, DOS) | EOL (early 2000s) | **Active** | **Active** |
| Hardware | Dedicated rack-mount box | Dedicated enclosed box | Adafruit ItsyBitsy nRF52840 + Ace Centre x80 add-on | Adafruit Feather + sensor / jacks (off-the-shelf) |
| Connection | PC parallel + serial | USB | **USB + BLE** | **USB** (BLE possible — see boards) |
| Switch jacks | 3 × 3.5 mm mono (SW1/SW2/SW3) | 3 × 3.5 mm mono | 2 × 3.5 mm mono on x80 (plus a buzzer) | 2 × 3.5 mm mono *or* sip-and-puff sensor |
| Sip-and-puff | Via external SP interface | Via external SP interface | Not built in | **Built in** (LPS33HW #4414) |
| Speaker | Headset jack | Headset jack | On-board buzzer | Built-in speaker, distinct dot/dash pitches |
| Visual display | Indicator LEDs | Indicator LEDs | None on x80 | **OLED or built-in TFT** (full text feedback) + optional wireless TFT |
| Customization | `.CNF` files via DOS LOADER tool | `.CST` binary via CodeMaker (Windows-only) | Python text files (`user/config.py`, `morse_code.py`) | Python text files (`morse_map.py`, `code.py`) |
| Source | Closed, EOL | Closed, EOL | **Open source** (GitHub) | **Open source** (GitHub) |
| Host OS | DOS, early Windows | Windows 98 – 7 (32-bit) | **Anything that accepts USB HID or BLE HID** | **Anything that accepts USB HID** |
| Cost | Discontinued; secondary market only | Discontinued; ~$1000+ when new | x80 board + ItsyBitsy ≈ $30–40 | ~$50–100 in parts |

---

## Input modes — 1, 2, and 3 switch

All four devices support multiple input modes, but they implement them
differently and on different hardware.

| Mode | **Adap2U** | **Darci USB** | **morAce** | **AeroMorse** |
|---|---|---|---|---|
| **1-switch** (timed) | ✓ Time Code system: Short / Medium / Long / Xlong pulse lengths, settable thresholds. Loaded with `LOADER -F TCODES.CNF`. | ✓ One switch; firmware times dot vs. dash internally. | ✓ **Default mode**. Holding the switch for ≥ `dot_length` (default 200 ms) = dot; ≥ 3× = dash. | ✓ `SWITCH_MODE = 1`. `ONE_SWITCH_INPUT` picks which physical input (sip / D5 or puff / D6) is the sole switch. Press ≤ `ONE_SWITCH_DOT_MS` (default 200 ms) = dot, longer = dash. Long-press cycles group forward. |
| **2-switch** (dot + dash) | ✓ `LOADER -F MORSE2.CNF`. Switch on SW1 = dit, SW2 = dah. Pause for settable timeout = end of letter. | ✓ Switch 1 = dot, switch 2 = dash. Pause = end of letter. | ✓ Configurable in `user/config.py` (`two_button_mode = 1`). | ✓ **Default** (`SWITCH_MODE = 2`) — D5 = dot, D6 = dash, or sip = dot / puff = dash. Pause `ACCEPT_DELAY` = end of letter. |
| **3-switch** (dot + dash + accept) | ✓ `LOADER -F MORSE3.CNF`. SW1 = dit, SW2 = dah, SW3 = explicit Accept (no timing pause needed). | ✓ Three-switch mode. Switch 3 explicitly commits the letter. | ✓ `three_button_mode = 1` in `user/config.py`. | ✓ `SWITCH_MODE = 3`. Long-press of `THIRD_SWITCH_GESTURE` (default `"long_dash"` = long puff / long-D6) = explicit Accept. The other long-gesture cycles group forward. |

**Why 1-switch matters:** Users with very limited motor control may only
be able to operate one switch reliably (a single sip-and-puff straw, a
single chin switch, a single eye-blink sensor). 1-switch Morse trades
mechanical complexity for cognitive / timing demand — you have to control
*how long* you hold the switch, instead of *which* switch you press.

**Why 3-switch matters:** Users who find timing-based end-of-letter
detection unreliable (e.g., they pause naturally mid-letter to think)
benefit from an explicit "Accept" gesture. Three-switch mode eliminates
the dependency on inter-symbol timing entirely.

**What the third "switch" looks like on AeroMorse:** AeroMorse hardware
has only two physical inputs (two jacks, or one sip-and-puff sensor).
The third input is a *gesture* on the existing inputs — by default a
**long puff** (or long-D6 in jack mode) treated as an explicit Accept.
The user can flip it to long sip via `THIRD_SWITCH_GESTURE = "long_dot"`.
Forward group-cycle moves to the *other* long-gesture in 3-switch mode;
backward cycling is unavailable as a gesture and must be done via a g0
Morse pattern.

---

## Hold-to-repeat (code repeat)

A user holds the switch and the device emits a stream of identical symbols
at a fixed interval, rather than requiring one tap per symbol. Important
for users who find tap-per-symbol fatiguing.

| | **Adap2U** | **Darci USB** | **morAce** | **AeroMorse** |
|---|---|---|---|---|
| Hold-to-repeat | ✓ Settable in Time Code / Morse config | ✓ "Code repeat" — holding the switch streams the same symbol; release ends the stream or transitions to the other symbol | — *(not documented; release-and-press required)* | ✓ `CODE_REPEAT = True` — `DOT_REPEAT_MS` (default 200 ms) and `DASH_REPEAT_MS` (default 600 ms) are independent; `CODE_REPEAT_MAX` (default 8) caps a runaway hold |
| Per-symbol repeat rate | Settable | Settable | — | Two independent settings |
| Default repeat behaviour | Off | On | n/a | Off (opt-in via `CODE_REPEAT = True`) |
| Companion flag | — | — | — | `LONG_PRESS_CYCLES_GROUP = False` recommended alongside `CODE_REPEAT = True` so a sustained stream doesn't accidentally cycle groups; use a g0 Morse pattern to switch groups instead (matches the Darci muscle memory). |

---

## Mode / group model

How the device organises functions beyond plain typing.

| | **Adap2U** | **Darci USB** | **morAce** | **AeroMorse** |
|---|---|---|---|---|
| Naming | "Configurations" | "Modes" (toggled with command codes) | Single set of codes + "shortcuts" via `morse_code_shortcuts.py` | **Ten groups** (g0 always-on; g1 keyboard, g2 mouse, g3 macros, g4 scanning/Switch Control, g5–g9 customisable) |
| Mouse control | ✓ Event system | ✓ Mouse Mode (uses Windows Mouse Keys) | ✓ Switch Control mode (separate from Morse) | ✓ Group 2 — native USB HID mouse events |
| Macros / phrases | ✓ Time Code "Meanings" (up to 4 chars) | ✓ Code Set assignments (4-char limit) | ✓ Shortcut strings in `morse_code_shortcuts.py` | ✓ Group 3 — unlimited length, any keycode tuple |
| Sticky modifiers | ✓ | ✓ | ✓ | ✓ (single-tap arms, double-tap locks) |
| Multi-device pairing | — | — | ✓ **BLE switch — up to N devices** (saving parameters required) | — (USB only by default) |

---

## Wireless display / remote feedback

A relatively unique AeroMorse feature.

| | **Adap2U** | **Darci USB** | **morAce** | **AeroMorse** |
|---|---|---|---|---|
| Remote display | — | — | — | ✓ **ESP-NOW wireless mirror** — second ESP32 board shows live state up to ~30 m away |
| Audio feedback | Mono headset | Mono headset | On-board buzzer | Speaker with distinct dot / dash pitches; group-change tones |

Useful when the input device (sip-and-puff sensor) must be mounted out of
the user's line of sight — e.g., behind the headrest — but the user still
needs to see the Morse buffer and current group.

---

## Customisation workflow

| | **Adap2U** | **Darci USB** | **morAce** | **AeroMorse** |
|---|---|---|---|---|
| Edit code set | DOS `LOADER` tool with `.CNF` text files | Windows CodeMaker app → binary `.CST` upload | Edit `morse_code.py` / `morse_code_shortcuts.py` in any text editor | Edit `morse_map.py` in any text editor |
| Edit settings | Same `.CNF` files | CodeMaker → `.CST` | Edit `user/config.py` | Edit constants at top of `code.py` |
| Edit while running | Possible via LOADER | Requires CodeMaker reload | **CIRCUITPY is read-only when multi-BT or switch-control is enabled**; press switch 1 on reboot to allow edits | CIRCUITPY drive always writeable; save in Thonny → auto-reload |
| Code-set source format | Plain text in `.CNF` | Closed binary `.CST` | Plain Python | Plain Python |
| Macro length limit | 4 chars per Time Code | 4 chars per code | Strings of any length | **Unlimited** — any string, keycode, or keycode-tuple |

---

## Why pick which

### Pick **AeroMorse** if you want…

- Cross-platform USB HID (Windows / macOS / Linux / iPadOS / Android / ChromeOS)
- Built-in sip-and-puff (no external SP interface needed)
- An on-device display showing the Morse buffer live
- Optional wireless secondary display
- Open source, modern hardware, active development
- Low cost (~$50–100 in parts)

### Pick **morAce** if you want…

- BLE HID switching between multiple paired devices
- A built-in switch-control mode (separate from Morse)
- A more compact form factor (ItsyBitsy + x80 add-on board)
- A polished Ace Centre product with documentation and community support
- Single-switch Morse with a well-tuned 200 ms default

### Pick **Darci USB** if you want…

- A fully-enclosed, ruggedized commercial device (warranty, vendor support — *when it was current*)
- An exact match to an existing user's muscle memory built on Darci codes
- 3 physical hardware switches for true 3-switch Morse

### Pick **Adap2U** if you want…

- Time-code-based input (settable Short / Medium / Long / Xlong pulse lengths) — useful for users with very variable timing
- Compatibility with legacy DOS workflows
- *(Note: Adap2U is EOL and not generally available)*

---

## Open questions / known gaps

This comparison is based on:
- **Adap2U** — A2UMAN.TXT version 2.1 (1995)
- **Darci USB** — Owner's Manual P/N 3001508 (6/13/02)
- **morAce** — github.com/AceCentre/morAce, `docs/guides/configuring-morace.md`
- **AeroMorse** — current `main` branch

If something looks wrong against an actual device, please open an issue
on the AeroMorse GitHub.

---

*Document version: 1.0  •  Project: https://github.com/jlubin2001/AeroMorse*
