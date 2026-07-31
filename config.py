# AeroMorse — User Configuration
#
# Edit a value, save, and the Feather auto-reloads. You should not need to
# open code.py.
#
# Each setting has a one-line hint here. For the full explanation (what it
# does, what other values mean, when to change it) see the Key Settings
# table in **Build Guide §10 Configuration** — every setting in this file
# has a row in that table, with the same name.
#
# The deprecated legacy_v2/ build keeps its own inline config — see
# legacy_v2/DEPRECATED.md.

import board   # board.D5 / D6 / A0 referenced below


# ── INPUT — sensor / switches / thresholds ────────────────────────────────

USE_SENSOR        = True      # True = LPS33HW sensor; False = AT switches on D5/D6
THRESH_SIP        = 2         # hPa below baseline = dot (raise if false triggers)
THRESH_PUFF       = 2         # hPa above baseline = dash
DEBOUNCE_SAMPLES  = 3         # consecutive agreeing samples to confirm a state change (~13 ms each)
POINTS_TO_AVERAGE = 8         # reserved — not currently used in the threshold path

SENSOR_FILTER_ENABLED = True  # LPS33HW hardware low-pass. False = lowest latency, noisier
SENSOR_FILTER_HEAVY   = True  # True = ODR/20 (~40-60 ms lag), False = ODR/9 (~half that)
BASELINE_DRIFT_S  = 30        # auto-zero time constant; 0 disables, follows ambient pressure drift

DOT_PIN           = board.D5  # switch-mode only — TIP of dot jack
DASH_PIN          = board.D6  # switch-mode only — TIP of dash jack


# ── INPUT MODE — 1 / 2 / 3 switch ─────────────────────────────────────────
# 1 = single-switch timed,  2 = paddle (default),  3 = paddle + explicit Accept

SWITCH_MODE          = 2
ONE_SWITCH_INPUT     = "dot"        # mode 1 only — "dot" or "dash"
ONE_SWITCH_DOT_MS    = 200          # mode 1 only — press ≤ this ms = dot, longer = dash
THIRD_SWITCH_GESTURE = "long_dash"  # mode 3 only — "long_dash" or "long_dot" = Accept


# ── STRONG SIP / STRONG PUFF — distinct gesture for group jumps or actions ─
# Sensor mode: peak pressure ≥ THRESH_*_STRONG fires the action.
# Switch mode: long-press of the corresponding switch fires the action,
#              and overrides LONG_PRESS_CYCLES_GROUP on that switch.
# Set ACTION = "" to disable.

STRONG_SIP_ACTION  = "group 2"        # e.g. "group 2" to jump to Mouse on strong sip
STRONG_PUFF_ACTION = "group 1"        # e.g. "group 1" to jump to Keyboard on strong puff
THRESH_SIP_STRONG  = 15        # hPa — sensor mode only
THRESH_PUFF_STRONG = 15        # hPa — sensor mode only


# ── TIMING ────────────────────────────────────────────────────────────────

ACCEPT_DELAY      = 0.2        # idle seconds before pattern commits (sip-puff: 0.5–0.7)
LONG_PRESS        = 1.0        # seconds to hold for cycle / Accept gesture


# ── CODE REPEAT (Darci-style hold-to-repeat) ──────────────────────────────
# When CODE_REPEAT = True, holding DIT or DAH emits one symbol per repeat
# interval. SWITCH_MODE = 2 only.

CODE_REPEAT             = False    # True = Darci-style hold-to-repeat
DOT_REPEAT_MS           = 200      # ms per auto-repeated dot
DASH_REPEAT_MS          = 600      # ms per auto-repeated dash (~3× dot)
CODE_REPEAT_MAX         = 8        # cap on symbols per held stream
LONG_PRESS_CYCLES_GROUP = True     # False with CODE_REPEAT = True; cycle via g0 codes instead


# ── AUDIO — speaker pitches (Hz) and blip durations (s) ───────────────────

AUDIO_PIN         = board.A0

BEEP_DOT_FREQ     = 1200       # dot (sip) sidetone — higher pitch
BEEP_DASH_FREQ    =  800       # dash (puff) sidetone — lower pitch
CONFIRM_FREQ      = 1050       # short blip when an action fires
GROUP_FREQ        =  550       # short blip on group change

BEEP_CONFIRM_S    = 0.06       # confirm-blip duration
BEEP_GROUP_S      = 0.14       # group-change blip duration


# ── MOUSE — group-2 movement speeds and repeat tick ───────────────────────
# Effective pixels per step = raw direction × SPEED × MOUSE_SPEED_FACTOR

MOUSE_SPEED_NORMAL = 2         # default speed in group 2
MOUSE_SPEED_SLOW   = 1         # toggled via `mslow`
MOUSE_SPEED_FAST   = 3         # toggled via `mfast`
MOUSE_SPEED_FACTOR = 2         # overall scale
MOUSE_REPEAT_DELAY = 0.040     # seconds between repeat ticks

MOUSE_CLICK_MOD_DELAY = 0.030  # s to settle a modifier before/after a click
MOUSE_CLICK_KEEPS_MODS = True  # True = armed mods survive a click (Ctrl+click
                               # multi-select); False = one-shot, cleared after
MOUSE_CLICK_HOLD = 0.060       # s to hold the button down per click. 0 = instant
                               # press/release, which Windows scrollbar tracks &
                               # some controls ignore; ~60 ms registers reliably
MOUSE_CLICK_GAP  = 0.040       # s between the two clicks of a double-click


# ── DISPLAY / WIRELESS ────────────────────────────────────────────────────

DISPLAY_ROTATION     = 0        # degrees: 0 = USB left, 180 = USB right (also 90, 270)
USE_WIRELESS_DISPLAY = True    # True = ESP-NOW broadcast (adds ~80–100 mA). ESP32-only.
ESPNOW_CHANNEL       = 1        # WiFi channel (1–13) — receiver.py _CHANNEL must match
