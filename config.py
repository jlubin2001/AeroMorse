# AeroMorse — User Configuration
#
# All tunable settings live here. Edit this file, save it, and the Feather
# auto-reloads with the new values. You should not need to open code.py.
#
# Each setting has a comment block above it explaining:
#   • what it does
#   • the default value and what other values mean
#   • when to change it
#
# A short reference of every setting (one-line per row) lives in
# README.md and Build Guide §10. The companion document
# MORSE_DEVICES_COMPARISON.md compares the input-mode and code-repeat
# settings against Darci USB, Adap2U, and morAce.
#
# ─────────────────────────────────────────────────────────────────────────────
# NOTE: The v2/code.py build (external OLED display) keeps its config inline
# at the top of v2/code.py for the moment. It does not import from this file.
# Only the root code.py (built-in TFT) uses config.py.
# ─────────────────────────────────────────────────────────────────────────────

import board  # board.D5, board.D6, board.A0 are referenced below


# ═════════════════════════════════════════════════════════════════════════════
# INPUT — sensor (sip-and-puff) or AT switches
# ═════════════════════════════════════════════════════════════════════════════

# True  = Option A in the build guide — LPS33HW pressure sensor (#4414)
#         driving sip-and-puff input. Sip is a dot, puff is a dash.
# False = Option B — two AT switches plugged into the dot / dash jacks.
USE_SENSOR      = True

# Pressure thresholds (hPa delta from the zeroed baseline) — sensor mode only.
# A sip pulls pressure DOWN, a puff pushes it UP. Symbol fires once the
# delta exceeds the threshold.
#   • Getting false triggers (sipping/puffing when you don't mean to)?
#     Raise both to 8 or 10.
#   • Light sips/puffs going unrecognised? Drop both to 3.
#   • Sip and puff thresholds can be tuned independently.
THRESH_SIP      = 5     # hPa below baseline to register a sip (dot)
THRESH_PUFF     = 5     # hPa above baseline to register a puff (dash)

# Pressure smoothing — number of sensor readings averaged before threshold
# comparison. Higher = more bounce immunity, slower response. Lower = faster
# but jitterier. 8 is a sensible default for sip-and-puff.
POINTS_TO_AVERAGE = 8

# Switch GPIO pins — only used when USE_SENSOR = False.
# Wired via 3.5 mm TRRS jack #1699 (B1/B2) or terminal block #2915 (B3).
DOT_PIN         = board.D5   # → TIP of dot jack
DASH_PIN        = board.D6   # → TIP of dash jack


# ═════════════════════════════════════════════════════════════════════════════
# INPUT MODE — 1 / 2 / 3 switch
# ═════════════════════════════════════════════════════════════════════════════
# See MORSE_DEVICES_COMPARISON.md for how each mode compares to Darci,
# Adap2U, and morAce.
#
# SWITCH_MODE = 2 (default, paddle-style):
#   DIT input = dot, DAH input = dash, pause (ACCEPT_DELAY) = end of letter.
#   Long-press of either input cycles groups (DIT-side = back, DAH-side = forward).
#
# SWITCH_MODE = 1 (single-switch timed):
#   Only ONE_SWITCH_INPUT counts; the other input is ignored.
#   Short press (<= ONE_SWITCH_DOT_MS) = dot, longer press (< LONG_PRESS) = dash,
#   very long press (>= LONG_PRESS) = cycle group forward.
#   Cycle back is unavailable in 1-switch mode (use a g0 Morse pattern).
#
# SWITCH_MODE = 3 (dot + dash + explicit Accept):
#   DIT and DAH short presses behave as in mode 2 (no timing pause needed).
#   THIRD_SWITCH_GESTURE long-press = Accept (commits the pending pattern now).
#   The OTHER long-gesture cycles groups forward.
#   Cycle back must use a g0 Morse pattern in 3-switch mode.
SWITCH_MODE          = 2

# 1-switch mode only — which physical input is the sole switch.
#   "dot"  = sip (sensor)  / D5 jack (switches)
#   "dash" = puff (sensor) / D6 jack (switches)
ONE_SWITCH_INPUT     = "dot"

# 1-switch mode only — ms boundary between a dot and a dash.
# Press <= ONE_SWITCH_DOT_MS is a dot; longer is a dash. Group cycle still
# kicks in at LONG_PRESS regardless.
ONE_SWITCH_DOT_MS    = 200

# 3-switch mode only — which long-gesture is the "third switch" (Accept).
#   "long_dash" = long puff (sensor) / long-D6 (switches)
#   "long_dot"  = long sip  (sensor) / long-D5 (switches)
# The OTHER long-gesture cycles groups forward.
THIRD_SWITCH_GESTURE = "long_dash"


# ═════════════════════════════════════════════════════════════════════════════
# CODE REPEAT — Darci-style hold-to-repeat
# ═════════════════════════════════════════════════════════════════════════════
# When CODE_REPEAT is True, holding DIT or DAH emits a stream of symbols at
# the configured repeat interval — one symbol on press, then one every
# DOT_REPEAT_MS / DASH_REPEAT_MS while held. Release ends the stream; the
# next press begins a new stream. ACCEPT_DELAY of idle still commits the
# accumulated pattern. This is the Darci USB "code repeat" behaviour.
#
# Only honoured when SWITCH_MODE = 2. In mode 1 the duration already
# classifies dot vs dash; in mode 3 holding overlaps with the explicit-Accept
# gesture.
CODE_REPEAT          = False   # True = Darci-style hold-to-repeat
DOT_REPEAT_MS        = 200     # ms per auto-repeated dot
DASH_REPEAT_MS       = 600     # ms per auto-repeated dash (~3× DOT_REPEAT_MS)
CODE_REPEAT_MAX      = 8       # cap on symbols per held stream

# Long-press group cycling — independent of CODE_REPEAT.
#   True  = holding DIT or DAH for >= LONG_PRESS cycles groups (default).
#   False = long-press does nothing; switch groups via g0 Morse patterns
#           instead.
# Recommended False alongside CODE_REPEAT = True so a sustained symbol
# stream doesn't accidentally trigger a group cycle.
LONG_PRESS_CYCLES_GROUP = True


# ═════════════════════════════════════════════════════════════════════════════
# TIMING
# ═════════════════════════════════════════════════════════════════════════════

# Idle pause (seconds) after the last element before the pattern commits.
#   • Patterns committing before you finish? Raise to 0.7.
#   • Patterns feeling sluggish? Lower to 0.3.
#   • Sip-and-puff users typically need 0.5–0.7 for comfortable breath rhythm.
#   • In 3-switch mode this is a safety-net timeout; the third-switch gesture
#     commits instantly regardless of ACCEPT_DELAY.
ACCEPT_DELAY    = 0.5

# Hold time (seconds) for the long-gesture (cycle / Accept).
# Raise (e.g. 1.5) if accidentally triggering on slow dots.
LONG_PRESS      = 1.0


# ═════════════════════════════════════════════════════════════════════════════
# AUDIO — speaker pitches and timing
# ═════════════════════════════════════════════════════════════════════════════
# All speaker options (S1 STEMMA Speaker, S2 piezo via jack, S3 PAM8302 amp)
# wire to A0 / GND. The output is a 50% duty square wave at the chosen
# frequency — see Build Guide §6.
AUDIO_PIN       = board.A0

BEEP_DOT_FREQ   = 1200          # Hz — dot (sip) sidetone — higher pitch
BEEP_DASH_FREQ  =  800          # Hz — dash (puff) sidetone — lower pitch
CONFIRM_FREQ    = 1050          # Hz — short blip when an action fires
GROUP_FREQ      =  550          # Hz — short blip on group change

BEEP_CONFIRM_S  = 0.06          # seconds — duration of the confirm blip
BEEP_GROUP_S    = 0.14          # seconds — duration of the group-change blip


# ═════════════════════════════════════════════════════════════════════════════
# MOUSE — speeds and repeat
# ═════════════════════════════════════════════════════════════════════════════
# In Group 2 (mouse), movement and click patterns emit mouse-pointer events
# scaled by these multipliers. Effective pixels per step =
#   raw direction value × MOUSE_SPEED_* × MOUSE_SPEED_FACTOR
MOUSE_SPEED_NORMAL = 2          # default speed when group 2 is entered
MOUSE_SPEED_SLOW   = 1          # toggled via `mslow` command
MOUSE_SPEED_FAST   = 3          # toggled via `mfast` command (if mapped)
MOUSE_SPEED_FACTOR = 2          # overall scale (matches AirTalker feel)

# When repeat is active (mouse move repeating, key repeating), this is the
# interval between repeat ticks (40 ms = 25 ticks/sec).
MOUSE_REPEAT_DELAY = 0.040


# ═════════════════════════════════════════════════════════════════════════════
# DISPLAY — TFT orientation
# ═════════════════════════════════════════════════════════════════════════════
# Display rotation in degrees.
#   0   = USB-C port on the LEFT side of the display
#   180 = USB-C port on the RIGHT side
#   90 / 270 are also valid but place the text vertically.
# Choose whichever matches how you've mounted the Feather.
DISPLAY_ROTATION   = 0


# ═════════════════════════════════════════════════════════════════════════════
# WIRELESS DISPLAY — ESP-NOW broadcast to a remote receiver board
# ═════════════════════════════════════════════════════════════════════════════
# True  = enable the WiFi radio at boot and broadcast the display state via
#         ESP-NOW. Required for the optional second-board mirror (Build
#         Guide §5 Option W1 or W2). Adds ~80–100 mA to the current draw
#         while running.
# False = leave the WiFi radio off. No emission, lower power. Use this when
#         you have no receiver paired.
#
# Has no effect on boards without an `espnow` module (RP2040, M4, nRF52840) —
# the import fails on those and the radio stays off regardless.
USE_WIRELESS_DISPLAY = False
