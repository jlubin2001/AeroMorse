# AeroMorse — Sip-and-puff / two-switch Morse HID device
#
# ════════════════════════════════════════════════════════════════════════════
#  AeroMorse code.py   —   version 1.18   (released 2026-10-02)
#
#  OFFICIAL SOURCE — always download the latest, correct files from:
#      https://github.com/jlubin2001/AeroMorse
#  code.py, boot.py, morse_map.py and config.py must all come from that repo,
#  at the same version. Copies found elsewhere on the web may be out of date.
# ════════════════════════════════════════════════════════════════════════════
#
# Hardware reference — see AEROMORSE_BUILD_GUIDE.md for all options:
#   Feather board       — Build Guide §3  (default: #5691 Reverse TFT Feather)
#   Display             — Build Guide §5  (built-in TFT on #5691, or external OLED)
#   Wireless display    — Build Guide §5 "Wireless Display — ESP-NOW Remote Mirror"
#                         (toggle with USE_WIRELESS_DISPLAY below)
#   Input method        — Build Guide §4  (Option A sensor / Option B switches)
#     Option A          — #4414 LPS33HW pressure sensor on STEMMA QT (sip-and-puff)
#     Option B1/B2/B3   — TRRS / 3.5mm jacks for AT switches (B3 = #2915 terminal block)
#   Speaker             — Build Guide §6  (S1 #3885 STEMMA / S2 piezo / S3 amp+speaker)
#   Assembly steps      — Build Guide §8  (8A display, 8B sensor, 8C switches, 8D speaker)
#
# Input modes
#   USE_SENSOR    — True = LPS33HW sip-and-puff (default), False = two AT switches
#   SWITCH_MODE   — 1 / 2 / 3 switch (default 2). See config block below and
#                   MORSE_DEVICES_COMPARISON.md for the model.
#
# Group model (see morse_map.py)
#   Group 0  always-available layer — checked before the active group
#   Group 1  keyboard  — letters, numbers, punctuation, function keys
#   Group 2  mouse + Windows shortcuts
#   Group 3  macro strings
#   Group 4  scanning — Enter, Space, F3–F12 on the 12 shortest codes (Switch Control)
#   Group 5    media keys
#   Group 6–9  placeholders (copy of g1 letters + numbers — customise)
#   Group 7    SWITCH by default (config SWITCH_GROUP): sip/puff HOLD Enter/Space
#              like two plain switches — see AEROMORSE_SWITCH_MODE_GUIDE.md
#   Reach any group directly with its 8-symbol Group 0 toggle code.
#
# Group switching
#   Primary   : long sip (> LONG_PRESS s) cycles groups backward
#               long puff                 cycles groups forward
#   Secondary : patterns within each group  (e.g. g1[5][0b00010] = "group 2")
#   Emergency : 8-symbol patterns in Group 0 (........ / -------- / etc.)

import time
import array
import board
import displayio
import terminalio
import digitalio
import usb_hid
import microcontroller      # devicereset command

from adafruit_display_text import label
try:
    import adafruit_lps35hw
    _LPS_AVAILABLE = True
except ImportError:
    _LPS_AVAILABLE = False
    print("WARNING: adafruit_lps35hw not found — falling back to switch mode")

try:
    import wifi as _wifi_mod
    import espnow as _espnow_mod
    _ESPNOW_IMPORTABLE = True
except Exception as _e:   # ImportError, or MemoryError "Failed to allocate Wifi
    _ESPNOW_IMPORTABLE = False   # memory" — never let the radio stop typing
    if not isinstance(_e, ImportError):
        print("WARNING: wifi unavailable (%s) — wireless display off" % _e)

try:
    import pwmio
    _AUDIO_AVAILABLE = True
except ImportError:
    _AUDIO_AVAILABLE = False
    print("WARNING: pwmio module not available — speaker disabled")

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

from morse_map import groups, CC
try:
    from morse_map import Secret as _Secret   # v1.5+ morse_map: secrets resolved here
except ImportError:
    _Secret = None                           # older morse_map resolves its own secrets

try:
    import aesio                             # AES for PIN-locked macro_secrets.enc
    _AES_OK = True
except ImportError:
    _AES_OK = False
import gc

# ── Configuration ─────────────────────────────────────────────────────────────
# All user-tunable settings live in config.py. Edit that file (not this one)
# to change thresholds, switch mode, code-repeat, audio pitches, etc.
from config import *  # noqa: F401,F403

# ── RollingAverage ─────────────────────────────────────────────────────────────

class RollingAverage:
    """Circular buffer for smooth pressure averaging."""
    def __init__(self, size):
        self.size   = size
        self.buffer = array.array('d')
        for _ in range(size):
            self.buffer.append(0.0)
        self.pos = 0

    def add(self, val):
        self.buffer[self.pos] = val
        self.pos = (self.pos + 1) % self.size

    def average(self):
        return sum(self.buffer) / self.size

# ── Hardware setup ─────────────────────────────────────────────────────────────

kbd    = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(kbd)
mouse  = Mouse(usb_hid.devices)
try:
    cc_device = ConsumerControl(usb_hid.devices)
    _CC_AVAILABLE = True
except Exception as _ex:
    cc_device = None
    _CC_AVAILABLE = False
    print(f"WARNING: ConsumerControl HID not available ({_ex}) — CC codes will no-op. Re-flash boot.py with usb_hid.Device.CONSUMER_CONTROL enabled.")

# Sensor bus. Boards with a STEMMA QT socket expose board.STEMMA_I2C(); boards
# without one (e.g. the nRF52840 Feather) only have board.I2C() on the SDA/SCL
# pins — wire the sensor there instead.
try:
    i2c = board.STEMMA_I2C()
except AttributeError:
    i2c = board.I2C()
    print("No STEMMA QT port on this board — using board.I2C() on SDA/SCL")

if USE_SENSOR and not _LPS_AVAILABLE:
    print("adafruit_lps35hw missing — switching to USE_SENSOR = False")
    USE_SENSOR = False

# Validate input-mode configuration
if SWITCH_MODE not in (1, 2, 3):
    print(f"SWITCH_MODE = {SWITCH_MODE} is not 1, 2, or 3 — falling back to 2")
    SWITCH_MODE = 2
# Accept any capitalisation / stray spaces (e.g. "Dot", "LONG_DASH ").
ONE_SWITCH_INPUT     = str(ONE_SWITCH_INPUT).strip().lower()
THIRD_SWITCH_GESTURE = str(THIRD_SWITCH_GESTURE).strip().lower()
if ONE_SWITCH_INPUT not in ("dot", "dash"):
    print(f"ONE_SWITCH_INPUT = {ONE_SWITCH_INPUT!r} invalid — falling back to 'dot'")
    ONE_SWITCH_INPUT = "dot"
if THIRD_SWITCH_GESTURE not in ("long_dot", "long_dash"):
    print(f"THIRD_SWITCH_GESTURE = {THIRD_SWITCH_GESTURE!r} invalid — falling back to 'long_dash'")
    THIRD_SWITCH_GESTURE = "long_dash"

# The strong-sip/puff actions are commands (e.g. "group 2") or "" to disable,
# never typed text, so make them case-insensitive too: "Group 2" -> "group 2".
STRONG_SIP_ACTION  = str(STRONG_SIP_ACTION).strip().lower()
STRONG_PUFF_ACTION = str(STRONG_PUFF_ACTION).strip().lower()

# Groups where strong sip / strong puff is switched off (config.py
# STRONG_OFF_IN_GROUPS, e.g. (4,) for Scanning): there a hard sip/puff is just
# a normal dot/dash, so it can't accidentally jump to another group. Older
# config.py without the setting: strong gestures work in every group.
try:
    _STRONG_OFF = STRONG_OFF_IN_GROUPS
    if isinstance(_STRONG_OFF, int):
        _STRONG_OFF = (_STRONG_OFF,)
    _STRONG_OFF = tuple(int(_g) for _g in _STRONG_OFF)
except NameError:
    _STRONG_OFF = ()
except Exception as _e:
    print("STRONG_OFF_IN_GROUPS not understood (%s) - strong sip/puff on in all groups" % _e)
    _STRONG_OFF = ()

# Split on a dip (config.py REPEAT_SPLIT_PCT, sensor mode): two quick sips or
# puffs in a row can run together when the pressure doesn't fall back under the
# trigger between them (p .--. comes out as r .-.). With this on, a sip/puff
# that drops below REPEAT_SPLIT_PCT % of its peak and then climbs again by
# REPEAT_SPLIT_RISE hPa counts as two. 0 or missing = off (old behaviour).
try:
    _SPLIT_FRAC = float(REPEAT_SPLIT_PCT) / 100.0
    if not 0.0 < _SPLIT_FRAC < 1.0:
        _SPLIT_FRAC = 0.0
except NameError:
    _SPLIT_FRAC = 0.0
except Exception as _e:
    print("REPEAT_SPLIT_PCT not understood (%s) - split on a dip is off" % _e)
    _SPLIT_FRAC = 0.0
try:
    _SPLIT_RISE = max(0.2, float(REPEAT_SPLIT_RISE))
except Exception:
    _SPLIT_RISE = 1.0
_SPLIT_MAX_S = 0.5      # only the first half second of a press can split, so a
                        # long hold (group cycle) is never chopped up
_sp_peak = 0.0          # highest pressure of the current press (toward its side)
_sp_low  = None         # lowest pressure since it dipped; None = not dipped yet

# Switch group (config.py SWITCH_GROUP, e.g. 7): in that group AeroMorse acts
# like two plain switches instead of Morse — a sip presses SWITCH_SIP_KEY and a
# puff presses SWITCH_PUFF_KEY the moment it starts, and HOLDS it until the
# sip/puff ends (for switch games and scanning apps that need a held key).
# Leave the group with a strong sip/puff. 0 or missing = no Switch group.
def _keycode_named(name, default):
    kc = getattr(Keycode, str(name).strip().upper(), None)
    if isinstance(kc, int):
        return kc
    print("Switch group: unknown key name %r - using %s" % (name, default))
    return getattr(Keycode, default)

try:
    _SWITCH_GROUP = int(SWITCH_GROUP)
    if not 1 <= _SWITCH_GROUP <= 9:
        _SWITCH_GROUP = 0
except NameError:
    _SWITCH_GROUP = 0
except Exception as _e:
    print("SWITCH_GROUP not understood (%s) - no Switch group" % _e)
    _SWITCH_GROUP = 0
try:
    _SW_SIP_KEY = _keycode_named(SWITCH_SIP_KEY, "ENTER")
except NameError:
    _SW_SIP_KEY = Keycode.ENTER
try:
    _SW_PUFF_KEY = _keycode_named(SWITCH_PUFF_KEY, "SPACE")
except NameError:
    _SW_PUFF_KEY = Keycode.SPACE
try:
    _SW_EXIT_S = max(2.0, float(SWITCH_EXIT_PUFF_S))
except Exception:
    _SW_EXIT_S = 5.0
try:
    _SW_IDLE_S = max(0.0, float(SWITCH_IDLE_EXIT_S))    # 0 = off
except Exception:
    _SW_IDLE_S = 20.0
try:
    _SW_EXIT_GROUP = int(SWITCH_EXIT_GROUP)
    if not 1 <= _SW_EXIT_GROUP <= 9 or _SW_EXIT_GROUP == _SWITCH_GROUP:
        _SW_EXIT_GROUP = 1
except Exception:
    _SW_EXIT_GROUP = 1
_sw_key  = None        # key currently held down by the Switch group (or None)
_sw_skip = False       # this press only dismissed the start-up screen

# Derived constants (kept once, used in the main loop hot path)
_ONE_SWITCH_DOT_S    = ONE_SWITCH_DOT_MS / 1000.0
_ONE_SWITCH_USES_DIT = (ONE_SWITCH_INPUT == "dot")     # True = DIT-side input wins
_THIRD_SWITCH_IS_DAH = (THIRD_SWITCH_GESTURE == "long_dash")
print(f"Input mode: {SWITCH_MODE}-switch  (1-sw input = {ONE_SWITCH_INPUT}, 3-sw accept = {THIRD_SWITCH_GESTURE})")

# Mouse group (Group 2) can commit patterns sooner than keyboard typing, so
# clicks feel snappier. Guarded for an older config.py that predates the
# setting — it then falls back to ACCEPT_DELAY (no behaviour change).
_MOUSE_GROUP = 2
try:
    _MOUSE_ACCEPT_DELAY = MOUSE_ACCEPT_DELAY
except NameError:
    _MOUSE_ACCEPT_DELAY = ACCEPT_DELAY

# Code-repeat derived constants and warnings
_DOT_REPEAT_S  = DOT_REPEAT_MS  / 1000.0
_DASH_REPEAT_S = DASH_REPEAT_MS / 1000.0
_CODE_REPEAT_ACTIVE = bool(CODE_REPEAT) and SWITCH_MODE == 2
if CODE_REPEAT and SWITCH_MODE != 2:
    print(f"CODE_REPEAT ignored — only applies when SWITCH_MODE = 2 (you have {SWITCH_MODE})")
if _CODE_REPEAT_ACTIVE and LONG_PRESS_CYCLES_GROUP:
    print("NOTE: CODE_REPEAT + LONG_PRESS_CYCLES_GROUP both on — a sustained symbol stream may also cycle groups on release.")
print(f"Code repeat: {'on' if _CODE_REPEAT_ACTIVE else 'off'}  long-press cycles group: {LONG_PRESS_CYCLES_GROUP}")

if USE_SENSOR:
    lps = adafruit_lps35hw.LPS35HW(i2c)
    lps.zero_pressure()
    lps.data_rate      = adafruit_lps35hw.DataRate.RATE_75_HZ
    # Hardware low-pass filter. filter_config True = ODR/20 (3.75 Hz cutoff at
    # 75 Hz — quietest but ~40-60 ms of group delay on every press AND every
    # release); False = ODR/9 (8.3 Hz, roughly half the lag). Both are on the
    # critical path for typing speed — see Build Guide Appendix E.
    lps.filter_enabled = SENSOR_FILTER_ENABLED
    lps.filter_config  = SENSOR_FILTER_HEAVY
else:
    _dot_btn  = digitalio.DigitalInOut(DOT_PIN)
    _dash_btn = digitalio.DigitalInOut(DASH_PIN)
    _dot_btn.switch_to_input(pull=digitalio.Pull.UP)
    _dash_btn.switch_to_input(pull=digitalio.Pull.UP)

# ── Sensor calibration ─────────────────────────────────────────────────────────

def _calibrate(count=10, delay=0.1):
    """Average 'count' readings to establish baseline thresholds."""
    total = 0.0
    for _ in range(count):
        total += lps.pressure
        time.sleep(delay)
    baseline = total / count
    return baseline, baseline - THRESH_SIP, baseline + THRESH_PUFF

if USE_SENSOR:
    print("Calibrating — do not sip or puff ...")
    _baseline, _sip_threshold, _puff_threshold = _calibrate()
    print(f"Baseline: {_baseline:.3f}  sip<{_sip_threshold:.3f}  puff>{_puff_threshold:.3f}")
    print("Calibration complete — ready for input.")
    _avg_pressure = RollingAverage(POINTS_TO_AVERAGE)

    # Auto-zero coefficient: each IDLE-state sample nudges _baseline this
    # fraction of the way toward the current raw reading. Sensor runs at
    # 75 Hz, so a 30 s time constant means alpha ≈ 1 / (30 × 75) ≈ 4.4e-4.
    # BASELINE_DRIFT_S = 0 disables auto-zero entirely.
    if BASELINE_DRIFT_S > 0:
        _BASELINE_ALPHA = 1.0 / (BASELINE_DRIFT_S * 75.0)
    else:
        _BASELINE_ALPHA = 0.0
    print(f"Baseline auto-zero: {BASELINE_DRIFT_S}s time constant"
          if BASELINE_DRIFT_S > 0 else "Baseline auto-zero: disabled")

# ── Audio setup ───────────────────────────────────────────────────────────────
# Square-wave tone generator on AUDIO_PIN via pwmio. This works on every
# CircuitPython chip including ESP32-S3 — synthio / audiopwmio are not
# available on ESP32-S3, so we use the simpler pwmio path uniformly.
#
# Frequency is switched per beep (dot / dash / confirm / group). 50% duty
# (0x8000) drives the STEMMA Speaker #3885 amp or a passive piezo cleanly;
# 0% duty (0) is silence.

if _AUDIO_AVAILABLE:
    _audio_out = pwmio.PWMOut(AUDIO_PIN, frequency=BEEP_DOT_FREQ,
                              duty_cycle=0, variable_frequency=True)

_beeping_morse  = False  # True while a DIT or DAH is held
_notify_end     = 0.0    # monotonic time when the timed blip should stop


def _tone_on(freq):
    """Drive the speaker at `freq` Hz with a 50% duty square wave."""
    if not _AUDIO_AVAILABLE:
        return
    _audio_out.frequency = freq
    _audio_out.duty_cycle = 0x8000        # ~50% duty — clean square wave


def _tone_off():
    """Silence the speaker."""
    if not _AUDIO_AVAILABLE:
        return
    _audio_out.duty_cycle = 0


def _beep_start(state):
    """Start sidetone on press — higher pitch for dot, lower for dash."""
    global _beeping_morse
    if not _AUDIO_AVAILABLE or _beeping_morse:
        return
    # DIT == 0, DAH == 1 — constants defined further down
    _tone_on(BEEP_DOT_FREQ if state == 0 else BEEP_DASH_FREQ)
    _beeping_morse = True


def _beep_stop():
    """Stop sidetone when press releases."""
    global _beeping_morse
    if not _AUDIO_AVAILABLE or not _beeping_morse:
        return
    _tone_off()
    _beeping_morse = False


def _beep_notify(duration=BEEP_CONFIRM_S, freq=None):
    """Short timed blip for action confirmation or group change."""
    global _notify_end
    if not _AUDIO_AVAILABLE:
        return
    _tone_on(freq if freq is not None else CONFIRM_FREQ)
    _notify_end = time.monotonic() + duration


def _audio_tick():
    """Silence the timed notification tone once its duration has elapsed."""
    global _notify_end
    if _AUDIO_AVAILABLE and _notify_end and time.monotonic() >= _notify_end:
        _tone_off()
        _notify_end = 0.0


# ── ESP-NOW wireless display ───────────────────────────────────────────────────
# Broadcasts TFT state to an Option W1 (second #5691 Reverse TFT Feather) or
# Option W2 (Adafruit MagTag #4800 e-ink) receiver. Entirely optional — if the
# espnow / wifi modules are absent nothing changes. See Build Guide §5
# "Wireless Display" for the per-option file tree and battery choices.

_ESPNOW_ENABLED = False
_broadcast_peer = None
if not USE_WIRELESS_DISPLAY:
    print("ESP-NOW: disabled by USE_WIRELESS_DISPLAY = False")
elif _ESPNOW_IMPORTABLE:
    try:
        # Channel-lock dance: start_ap then immediately stop_ap pins the radio
        # to ESPNOW_CHANNEL without leaving WiFi associated (which would enable
        # power-save and break ESP-NOW). Both boards must do this with the
        # SAME channel.
        _wifi_mod.radio.start_ap(" ", "", channel=ESPNOW_CHANNEL, max_connections=0)
        _wifi_mod.radio.stop_ap()
        _espnow_dev = _espnow_mod.ESPNow()
        # Workaround for CircuitPython issue #9380: registering ONLY a
        # broadcast peer raises ESP_ERR_ESPNOW_NOT_FOUND (0x3069) on send.
        # Register a dummy unicast peer first, then the broadcast peer.
        _espnow_dev.peers.append(_espnow_mod.Peer(
            mac=b'\x02\x00\x00\x00\x00\x01', channel=ESPNOW_CHANNEL))
        _broadcast_peer = _espnow_mod.Peer(
            mac=b'\xff\xff\xff\xff\xff\xff', channel=ESPNOW_CHANNEL)
        _espnow_dev.peers.append(_broadcast_peer)
        _ESPNOW_ENABLED = True
        print(f"ESP-NOW: wireless display active (broadcast, channel {ESPNOW_CHANNEL})")
    except Exception as _ex:
        print(f"ESP-NOW: init failed ({_ex})")
else:
    print("ESP-NOW: module not available on this board")

def _espnow_send(group_str, buf_str, action_str, mods_str):
    """Broadcast four display fields over ESP-NOW.  Fire-and-forget."""
    if not _ESPNOW_ENABLED:
        return
    msg = (group_str + "|" + buf_str + "|" + action_str + "|" + mods_str).encode()
    try:
        _espnow_dev.send(msg, _broadcast_peer)
    except Exception:
        pass

# ── Action type helpers ────────────────────────────────────────────────────────

# Modifier keycodes receive sticky treatment: press to arm, used on next key,
# then auto-release.  Press again while armed to disarm.
_STICKY_MODS = frozenset({
    Keycode.LEFT_CONTROL,  Keycode.RIGHT_CONTROL,
    Keycode.LEFT_SHIFT,    Keycode.RIGHT_SHIFT,
    Keycode.LEFT_ALT,      Keycode.RIGHT_ALT,
    Keycode.LEFT_GUI,      Keycode.RIGHT_GUI,
})

_ALPHA_KEYS = {
    'a': Keycode.A, 'b': Keycode.B, 'c': Keycode.C, 'd': Keycode.D,
    'e': Keycode.E, 'f': Keycode.F, 'g': Keycode.G, 'h': Keycode.H,
    'i': Keycode.I, 'j': Keycode.J, 'k': Keycode.K, 'l': Keycode.L,
    'm': Keycode.M, 'n': Keycode.N, 'o': Keycode.O, 'p': Keycode.P,
    'q': Keycode.Q, 'r': Keycode.R, 's': Keycode.S, 't': Keycode.T,
    'u': Keycode.U, 'v': Keycode.V, 'w': Keycode.W, 'x': Keycode.X,
    'y': Keycode.Y, 'z': Keycode.Z,
}
_DIGIT_KEYS = {
    '0': Keycode.ZERO,  '1': Keycode.ONE,   '2': Keycode.TWO,
    '3': Keycode.THREE, '4': Keycode.FOUR,  '5': Keycode.FIVE,
    '6': Keycode.SIX,   '7': Keycode.SEVEN, '8': Keycode.EIGHT,
    '9': Keycode.NINE,
}

# ── State ──────────────────────────────────────────────────────────────────────

# DIT = dot (sip / DOT_PIN), DAH = dash (puff / DASH_PIN), IDLE = neutral
DIT  = 0
DAH  = 1
IDLE = 2

active_group  = 1

# Morse accumulator — binary word and bit count (mirrors AirTalker's approach)
# Bit encoding: 0 = DIT (dot), 1 = DAH (dash), MSB = first symbol
_pending_char = 0
_num_shifts   = 0

# State-machine bookkeeping
_last_state   = IDLE
_last_trans_at = 0.0    # time of most recent state change (used for ACCEPT_DELAY)
_press_start   = 0.0    # time the current DIT/DAH press began (for LONG_PRESS)
_stream_count  = 0      # symbols emitted during the current held state
                        # (CODE_REPEAT only — counts toward CODE_REPEAT_MAX)
_peak_delta    = 0.0    # peak |pressure - baseline| during the current press
                        # (sensor mode only — used to detect strong sip/puff)
_strong_handled = False # True after STRONG_SIP/PUFF_ACTION fires for the
                        # current press, suppressing dot/dash/cycle/accept

# Debounce: only accept a sensor state change after DEBOUNCE_SAMPLES
# consecutive readings agree. Filters mid-element pressure wobble at low
# thresholds. Sensor mode only.
_candidate_state = IDLE
_candidate_count = 0

# When a new sip/puff interrupts a mouse repeat, the press itself must NOT
# also be recorded as a Morse element. _consuming_press is set on cancel and
# cleared on the release, causing the bit-shift in DIT/DAH→IDLE to be
# skipped exactly once.
_consuming_press = False

_armed_mods   = set()   # sticky modifier keycodes currently armed

# Mouse state
_mouse_speed    = MOUSE_SPEED_NORMAL
_drag_active    = False
_last_mouse_vec  = (0, 0, 0)   # last mmove already scaled (x, y, wheel)
_last_repeatable = None         # last keycode / combo / text to repeat (None = mouse-only)
_mouse_repeating = False
_mouse_moved     = [0, 0, 0]   # accumulated pixels this repeat session
_mouse_start_t   = 0.0         # when current repeat session began
_last_repeat_tick = 0.0        # when last key-repeat fired

_last_action  = " "
_repeat_label = ""    # display label of whatever `repeat` will re-fire, captured
                      # when that action runs — so the status line can show
                      # "RPT DOWN ARROW" instead of a bare "REPEAT".
_display_pressure = 0.0

# ── Morse lookup ───────────────────────────────────────────────────────────────

def lookup_action(num_shifts, pending_char):
    """Return the action mapped to the accumulated Morse pattern, or None.
    Group 0 (always-available layer) takes priority over the active group.
    """
    if num_shifts == 0 or num_shifts > 8:
        return None
    action = groups[0].get(num_shifts, {}).get(pending_char)
    if action is None and active_group != 0:
        action = groups[active_group].get(num_shifts, {}).get(pending_char)
    return action


def _pending_to_str(num_shifts, pending_char):
    """Convert the pending accumulator to a dot-dash display string."""
    if num_shifts == 0:
        return " "
    parts = []
    for i in range(num_shifts - 1, -1, -1):
        parts.append('-' if (pending_char >> i) & 1 else '.')
    return " ".join(parts)

# ── Mouse repeat ───────────────────────────────────────────────────────────────

def _start_mouse_repeat():
    global _mouse_repeating, _mouse_moved, _mouse_start_t, _last_repeat_tick
    if _last_mouse_vec == (0, 0, 0) and _last_repeatable is None:
        return                          # nothing to repeat
    _mouse_repeating  = True
    _mouse_moved      = [0, 0, 0]
    _mouse_start_t    = 0.0
    _last_repeat_tick = 0.0

def _stop_mouse_repeat():
    global _mouse_repeating, _mouse_moved, _mouse_start_t, _last_repeat_tick
    _mouse_repeating  = False
    _mouse_moved      = [0, 0, 0]
    _mouse_start_t    = 0.0
    _last_repeat_tick = 0.0

def _mouse_repeat_tick():
    """Repeat the last action:
      • mmove  — smooth, pixel-accurate movement based on elapsed time
      • keycode / combo / text — fire at fixed MOUSE_REPEAT_DELAY intervals
    Called every main-loop iteration while _mouse_repeating is True.
    """
    global _mouse_moved, _mouse_start_t, _last_repeat_tick
    now = time.monotonic()

    if _last_repeatable is not None:
        # Key / combo / text repeat — interval-based
        if now - _last_repeat_tick >= MOUSE_REPEAT_DELAY:
            if isinstance(_last_repeatable, tuple):
                _exec_combo(_last_repeatable)
            elif isinstance(_last_repeatable, int):
                _exec_keycode(_last_repeatable)
            elif isinstance(_last_repeatable, str):
                _exec_text(_last_repeatable)
            _last_repeat_tick = now
        return

    # Mouse movement repeat — smooth, time-based
    if _last_mouse_vec == (0, 0, 0):
        _stop_mouse_repeat()
        return
    if _mouse_start_t == 0.0:
        _mouse_start_t = now
        return
    elapsed = now - _mouse_start_t
    scale   = elapsed / MOUSE_REPEAT_DELAY
    target  = (
        int(round(scale * _last_mouse_vec[0])),
        int(round(scale * _last_mouse_vec[1])),
        int(round(scale * _last_mouse_vec[2])),
    )
    to_move = [
        target[0] - _mouse_moved[0],
        target[1] - _mouse_moved[1],
        target[2] - _mouse_moved[2],
    ]
    if to_move[0] or to_move[1] or to_move[2]:
        mouse.move(*to_move)
        _mouse_moved[0] += to_move[0]
        _mouse_moved[1] += to_move[1]
        _mouse_moved[2] += to_move[2]

# ── Action execution ───────────────────────────────────────────────────────────

def _exec_keycode(kc):
    """Press a single Keycode, honouring sticky modifiers."""
    global _armed_mods
    if kc in _STICKY_MODS:
        if kc in _armed_mods:
            _armed_mods.discard(kc)
        else:
            _armed_mods.add(kc)
        return
    if _armed_mods:
        kbd.press(*_armed_mods, kc)
        _armed_mods.clear()
    else:
        kbd.press(kc)
    kbd.release_all()


def _exec_combo(keycodes):
    """Press a tuple of keycodes simultaneously, plus any armed mods."""
    global _armed_mods
    if _armed_mods:
        kbd.press(*_armed_mods, *keycodes)
        _armed_mods.clear()
    else:
        kbd.press(*keycodes)
    kbd.release_all()


def _exec_text(text):
    """Type a string.  Single letter/digit uses keycode path when mods are armed
    so that e.g. armed Ctrl + 'c' sends Ctrl+C.  Multi-char macros discard mods.
    """
    global _armed_mods
    if len(text) == 1 and _armed_mods:
        kc = _ALPHA_KEYS.get(text.lower()) or _DIGIT_KEYS.get(text)
        if kc:
            kbd.press(*_armed_mods, kc)
            kbd.release_all()
            _armed_mods.clear()
            return
    _armed_mods.clear()
    # One character at a time, so a character the US layout can't type (e.g. an
    # invisible control character that slipped into a macro) is skipped instead
    # of stopping the device. layout.write() would raise part-way through.
    skipped = 0
    for ch in text:
        try:
            layout.write(ch)
        except ValueError:
            skipped += 1
    if skipped:
        print("WARNING: skipped %d character(s) the keyboard can't type" % skipped)


def _exec_command(cmd):
    """Execute a device command: group / mmove / mclick / mdrag / repeat /
    mslow / mfast / unlock / lock / version / devicereset
    """
    global active_group, _mouse_speed, _drag_active
    global _last_mouse_vec, _last_repeatable, _mouse_repeating, _armed_mods
    parts = cmd.split()
    verb  = parts[0]

    if verb == 'group':
        active_group    = int(parts[1])
        _last_repeatable = None     # reset repeat on group change — must mmove first

    elif verb == 'mmove':
        # Scale raw direction values by current speed and factor
        dx = int(parts[1]) * _mouse_speed * MOUSE_SPEED_FACTOR
        dy = int(parts[2]) * _mouse_speed * MOUSE_SPEED_FACTOR
        sc = int(parts[3]) * _mouse_speed * MOUSE_SPEED_FACTOR
        if dx or dy:
            mouse.move(dx, dy)
        if sc:
            mouse.move(wheel=sc)
        _last_mouse_vec  = (dx, dy, sc)  # store scaled values for repeat
        _last_repeatable = None           # mouse-mode repeat, not key-mode

    elif verb == 'mclick':
        side  = parts[1]
        count = int(parts[2])
        btn   = (Mouse.LEFT_BUTTON   if side == 'left'   else
                 Mouse.RIGHT_BUTTON  if side == 'right'  else
                 Mouse.MIDDLE_BUTTON)
        if _armed_mods:
            # Keyboard and mouse are separate USB HID interfaces, so the host
            # can process their reports out of order. Without a settle delay
            # the click often lands before the modifier registers and the host
            # sees a plain click — which is why Ctrl+click multi-select failed.
            kbd.press(*_armed_mods)
            time.sleep(MOUSE_CLICK_MOD_DELAY)
        # Press → hold → release, rather than mouse.click() which fires
        # press and release in the same call microseconds apart. Windows
        # scrollbar tracks and some controls ignore a zero-duration click;
        # holding for MOUSE_CLICK_HOLD makes them register. (This is why a
        # `mdrag` toggle scrolled but a click did not — the drag holds the
        # button down, a click did not.)
        for i in range(count):
            mouse.press(btn)
            time.sleep(MOUSE_CLICK_HOLD)
            mouse.release(btn)
            if i < count - 1:
                time.sleep(MOUSE_CLICK_GAP)   # separate the clicks of a dbl-click
        if _armed_mods:
            time.sleep(MOUSE_CLICK_MOD_DELAY)   # let the click land first
            kbd.release_all()
            # Modifiers normally auto-clear after one use, but Ctrl+click
            # multi-select needs the modifier to survive click after click —
            # otherwise every file costs two patterns instead of one. Keep it
            # armed and let the user toggle it off with the same pattern that
            # armed it. The status line keeps showing e.g. "RCtrl" throughout.
            if not MOUSE_CLICK_KEEPS_MODS:
                _armed_mods.clear()
        _last_mouse_vec  = (0, 0, 0)    # clicks are not repeatable
        _last_repeatable = None

    elif verb == 'mdrag':
        btn = Mouse.LEFT_BUTTON if parts[1] == 'left' else Mouse.RIGHT_BUTTON
        if _drag_active:
            mouse.release(btn)
            _drag_active = False
        else:
            mouse.press(btn)
            _drag_active = True
        _last_mouse_vec  = (0, 0, 0)    # drag toggle is not repeatable
        _last_repeatable = None

    elif verb == 'repeat':
        # Toggle repeat: second 'repeat' stops it
        if _mouse_repeating:
            _stop_mouse_repeat()
        else:
            _start_mouse_repeat()

    elif verb == 'mslow':
        _mouse_speed = (MOUSE_SPEED_NORMAL
                        if _mouse_speed == MOUSE_SPEED_SLOW
                        else MOUSE_SPEED_SLOW)

    elif verb == 'mfast':
        _mouse_speed = (MOUSE_SPEED_NORMAL
                        if _mouse_speed == MOUSE_SPEED_FAST
                        else MOUSE_SPEED_FAST)

    elif verb == 'unlock':
        if _SECRETS_ENC is None:
            _last_action_set("NO PIN FILE")
        elif not _secrets_locked:
            _last_action_set("ALREADY UNLOCKED")
        else:
            _pin_start(None)

    elif verb == 'lock':
        _secrets_lock()

    elif verb == 'version':
        _show_version()

    elif verb == 'devicereset':
        _reset_confirm_start()


def _last_action_set(text):
    global _last_action
    _last_action = text


def _show_version():
    """`version` command: show the start-up screen (device name, AeroMorse
    version, CircuitPython version) again until the next sip / puff / press."""
    global _show_splash
    _show_splash = True


# ── devicereset — restart the device, after a y/n confirmation ────────────────
# Switches to Group 1 and shows "CONFIRM RESET Y/N?". The next pattern decides:
# "y" restarts (same as unplugging and replugging); anything else — or
# _RESET_TIMEOUT seconds with no input — cancels and returns to the group you
# were in. Nothing is sent to the computer while it is asking.
_reset_confirm    = False
_reset_prev_group = 1
_reset_t          = 0.0
_RESET_TIMEOUT    = 30

def _reset_confirm_start():
    global _reset_confirm, _reset_prev_group, _reset_t, active_group, _last_action
    _reset_confirm    = True
    _reset_prev_group = active_group
    _reset_t          = time.monotonic()
    _armed_mods.clear()
    active_group = 1                     # so "y" / "n" are the Group 1 letters
    _last_action = "CONFIRM RESET Y/N?"
    print("Device reset requested - type y to restart, anything else cancels")
    _beep_notify(duration=BEEP_GROUP_S, freq=GROUP_FREQ)

def _reset_cancel(msg="RESET CANCELLED"):
    global _reset_confirm, active_group, _last_action
    _reset_confirm = False
    active_group   = _reset_prev_group
    _last_action   = msg
    print(msg)

def _reset_confirm_input(action):
    """Called instead of execute() while waiting for y/n."""
    global _last_action
    if isinstance(action, str) and action.strip().lower() == "y":
        _last_action = "RESTARTING..."
        print("Device reset confirmed - restarting")
        _update_display()
        try:
            kbd.release_all()
            mouse.release_all()
        except Exception:
            pass
        time.sleep(0.5)
        microcontroller.reset()
    _reset_cancel()


_CMD_VERBS = {'group', 'mmove', 'mclick', 'mdrag', 'repeat', 'mslow', 'mfast',
              'unlock', 'lock', 'version', 'devicereset'}

# Human-friendly display labels for mouse commands — matches the
# aeromorse_cheatsheet.htm substitutions so the OLED/TFT last-action
# line and the serial console both read clearly (e.g. "mmove up" on
# screen instead of "mmove 0 -1 0"). The raw command string is still
# what gets dispatched to _exec_command; only the display changes.
_FRIENDLY_CMD = {
    "mmove 0 -1 0":   "mmove up",
    "mmove 0 1 0":    "mmove down",
    "mmove 1 0 0":    "mmove right",
    "mmove -1 0 0":   "mmove left",
    "mmove 0 0 1":    "mwheel up",
    "mmove 0 0 -1":   "mwheel down",
    "mmove -1 -1 0":  "mmove up-left",
    "mmove 1 -1 0":   "mmove up-right",
    "mmove -1 1 0":   "mmove down-left",
    "mmove 1 1 0":    "mmove down-right",
    "mclick left 1":  "mclick left sgl",
    "mclick right 1": "mclick right sgl",
    "mclick left 2":  "mclick left dbl",
    "mclick right 2": "mclick right dbl",
    "mdrag left":     "DRAG LEFT TOGGLE",
}
# Uppercase the mouse labels too — easier to read on the small display.
_FRIENDLY_CMD = {k: v.upper() for k, v in _FRIENDLY_CMD.items()}

# Friendly names for single-character actions — punctuation gets a word,
# letters get uppercased. Multi-character macros stay as quoted strings.
_FRIENDLY_CHAR = {
    '+':  'PLUS',          '-':  'MINUS',          '=':  'EQUALS',
    '*':  'ASTERISK',      '!':  'EXCLAMATION',    '@':  'AT',
    '#':  'HASH',          '$':  'DOLLAR',         '%':  'PERCENT',
    '^':  'CARET',         '&':  'AMPERSAND',      '.':  'PERIOD',
    ',':  'COMMA',         ':':  'COLON',          ';':  'SEMICOLON',
    ')':  'RIGHT PAREN',   '(':  'LEFT PAREN',
    ']':  'RIGHT BRACKET', '[':  'LEFT BRACKET',
    '}':  'RIGHT BRACE',   '{':  'LEFT BRACE',
    '<':  'LESS THAN',     '>':  'GREATER THAN',
    '?':  'QUESTION',      '/':  'SLASH',          '\\': 'BACKSLASH',
    '|':  'PIPE',          '_':  'UNDERSCORE',
    '"':  'DOUBLE QUOTE',  "'":  'APOSTROPHE',
    '`':  'BACKTICK',      '~':  'TILDE',
    ' ':  'SPACE',         '\n': 'NEWLINE',        '\t': 'TAB',
}

# Auto-built reverse maps: integer Keycode / ConsumerControlCode → friendly
# all-caps name (UP_ARROW → "UP ARROW"). Built once at module import by
# introspecting the adafruit_hid constants.
def _build_int_name_map(cls):
    result = {}
    for name in dir(cls):
        if name.startswith('_'):
            continue
        val = getattr(cls, name)
        if isinstance(val, int):
            result[val] = name.replace('_', ' ')
    return result

_KEYCODE_NAMES = _build_int_name_map(Keycode)
_CC_NAMES      = _build_int_name_map(ConsumerControlCode)

# adafruit_hid gives several aliases to the same integer — LEFT_GUI is also
# GUI / WINDOWS / COMMAND, and LEFT_ALT is also ALT / OPTION. _build_int_name_map
# keeps whichever alias dir() happens to return last, and CircuitPython's dir()
# is not sorted, so the label picked was both arbitrary and Mac-flavoured
# ("COMMAND + TAB", "OPTION + TAB"). Pin the Windows names explicitly.
# RIGHT_* keycodes have no aliases, so they keep their auto-built names
# ("RIGHT CONTROL" etc.) and stay clearly distinguishable from these.
_KEYCODE_NAMES.update({
    Keycode.LEFT_CONTROL: "CTRL",
    Keycode.LEFT_SHIFT:   "SHIFT",
    Keycode.LEFT_ALT:     "ALT",
    Keycode.LEFT_GUI:     "WIN",
})


def _is_command(action):
    return action.split(' ')[0] in _CMD_VERBS


def _exec_consumer(cc_action):
    """Send a USB HID ConsumerControl code (media keys, volume, brightness, etc.)."""
    if _CC_AVAILABLE:
        cc_device.send(cc_action.code)


# Keycodes that must never arm the repeat (config NO_REPEAT_KEYS, by name).
# Resolved to integer keycodes once at import. Guarded so an older config.py
# without NO_REPEAT_KEYS still boots with a sane default instead of crashing.
try:
    _NO_REPEAT_NAMES = NO_REPEAT_KEYS
except NameError:
    _NO_REPEAT_NAMES = ("PAGE_UP", "PAGE_DOWN")
_NO_REPEAT_KEYCODES = set()
for _nm in _NO_REPEAT_NAMES:
    _kc = getattr(Keycode, _nm, None)
    if isinstance(_kc, int):
        _NO_REPEAT_KEYCODES.add(_kc)
    else:
        print(f"WARNING: NO_REPEAT_KEYS entry {_nm!r} is not a valid Keycode — ignored")


# ── Secret macros (passwords) — plain or PIN-locked ─────────────────────────────
#
# morse_map.py marks private values with _secret('key', 'placeholder'), which
# returns a Secret marker; the real value is looked up HERE when it is typed:
#
#   macro_secrets.enc  (made by the "AeroMorse Secrets" PC tool) — encrypted.
#       Starts LOCKED at every power-up. Pressing a secret pattern while locked
#       asks for the PIN: type it in Morse (Group 1 letters/digits), then ENTER.
#       Right PIN -> unlocks and types the secret you asked for. Wrong PIN ->
#       stays locked. ESC or BACKSPACE-on-empty cancels. Nothing typed during
#       PIN entry is sent to the computer. `lock` locks again; power-off always
#       does. Optional auto-lock: SECRETS_AUTOLOCK_MIN in config.py.
#   macro_secrets.txt  — plain key=value lines, always available (no PIN).
#
# If both exist the .enc wins. A missing/unreadable file never stops the
# device — secrets just type their placeholder. Secret VALUES are never shown
# on the screen, the wireless display or the USB serial log — only "SECRET key".

_ENC_MAGIC  = b"AMSEC1"
_ENC_HEADER = 58          # magic 6 + rounds 4 + salt 16 + nonce 16 + check 16

def _parse_secrets(text):
    d = {}
    for line in text.split("\n"):
        line = line.strip().replace("\ufeff", "")
        if not line or line[0] == "#" or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k:
            d[k] = v.strip()
    return d

_SECRETS       = {}
_SECRETS_ENC   = None     # raw bytes of macro_secrets.enc (None = no PIN lock)
_secrets_locked = False
if _Secret is not None:
    try:
        with open("/macro_secrets.enc", "rb") as _f:
            _blob = _f.read()
        if len(_blob) >= _ENC_HEADER and _blob[:6] == _ENC_MAGIC:
            _SECRETS_ENC    = _blob
            _secrets_locked = True
            print("Secrets: macro_secrets.enc found — LOCKED until PIN is entered")
        else:
            print("Secrets: macro_secrets.enc is not a valid AeroMorse secrets file — ignored")
        _blob = None
    except OSError:
        pass
    try:
        with open("/macro_secrets.txt") as _f:
            _txt = _f.read()
        if _SECRETS_ENC is None:
            _SECRETS = _parse_secrets(_txt)
        else:
            print("Secrets: WARNING plain macro_secrets.txt is ALSO on the device — delete it (the .enc is used)")
        _txt = None
    except OSError:
        pass
    except Exception as _e:
        print("Secrets: error reading macro_secrets.txt (%s)" % _e)
    if _SECRETS_ENC is not None and not _AES_OK:
        print("Secrets: this CircuitPython has no aesio — macro_secrets.enc can't be unlocked")
    gc.collect()

try:
    _AUTOLOCK_S = float(SECRETS_AUTOLOCK_MIN) * 60
except NameError:
    _AUTOLOCK_S = 0       # older config.py: never auto-lock

# SHA-256 in plain Python — CircuitPython's hashlib on the ESP32-S3 has no
# sha256. Only a few blocks are hashed per unlock, so speed doesn't matter.
_K256 = (
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2)

def _sha256(data):
    M = 0xFFFFFFFF
    h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
         0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    n = len(data)
    data = bytes(data) + b"\x80" + bytes((55 - n) % 64) + (n * 8).to_bytes(8, "big")
    for off in range(0, len(data), 64):
        w = [int.from_bytes(data[off + i * 4:off + i * 4 + 4], "big") for i in range(16)]
        for i in range(16, 64):
            x = w[i - 15]
            y = w[i - 2]
            s0 = ((x >> 7 | x << 25) ^ (x >> 18 | x << 14) ^ (x >> 3)) & M
            s1 = ((y >> 17 | y << 15) ^ (y >> 19 | y << 13) ^ (y >> 10)) & M
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & M)
        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            S1 = ((e >> 6 | e << 26) ^ (e >> 11 | e << 21) ^ (e >> 25 | e << 7)) & M
            t1 = (hh + S1 + ((e & f) ^ (~e & g)) + _K256[i] + w[i]) & M
            S0 = ((a >> 2 | a << 30) ^ (a >> 13 | a << 19) ^ (a >> 22 | a << 10)) & M
            t2 = (S0 + ((a & b) ^ (a & c) ^ (b & c))) & M
            hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & M, c, b, a, (t1 + t2) & M
        h = [(p + q) & M for p, q in zip(h, (a, b, c, d, e, f, g, hh))]
    return b"".join(x.to_bytes(4, "big") for x in h)

def _derive_keys(pin, salt, rounds):
    """PIN -> (AES-256 key, 16-byte check). Must match aeromorse_secrets.py.
    The AES chain is the deliberate slow part (~1.5 s) that makes guessing
    PINs from a copied file expensive."""
    k = bytearray(_sha256(b"AeroMorse secrets v1\x00" + salt + pin.encode("utf-8")))
    o = bytearray(16)
    z0 = bytes(16)
    z1 = b"\x01" * 16
    for _ in range(rounds):
        c = aesio.AES(bytes(k), aesio.MODE_ECB)
        c.encrypt_into(z0, o)
        k[0:16] = o
        c.encrypt_into(z1, o)
        k[16:32] = o
    k = bytes(k)
    return _sha256(b"enc\x00" + k), _sha256(b"chk\x00" + k)[:16]

def _decrypt_secrets(blob, pin):
    """Return the secrets dict, or None if the PIN is wrong."""
    rounds = int.from_bytes(blob[6:10], "big")
    salt, nonce, chk = blob[10:26], blob[26:42], blob[42:58]
    key, check = _derive_keys(pin, salt, rounds)
    if check != chk:
        return None
    ct = blob[_ENC_HEADER:]
    pt = bytearray(len(ct))
    aesio.AES(key, aesio.MODE_CTR, nonce).decrypt_into(ct, pt)
    return _parse_secrets(bytes(pt).decode("utf-8"))

# PIN entry state
_pin_active  = False
_pin_buf     = []
_pin_pending = None       # Secret to type once unlocked (None = plain `unlock`)
_pin_last_t  = 0.0
_PIN_TIMEOUT = 60         # s of no PIN input before entry is cancelled

def _pin_start(pending):
    global _pin_active, _pin_buf, _pin_pending, _pin_last_t, active_group, _last_action
    if not _AES_OK:
        _last_action = "NO AES - CANT UNLOCK"
        return
    _pin_active  = True
    _pin_buf     = []
    _pin_pending = pending
    _pin_last_t  = time.monotonic()
    _armed_mods.clear()
    active_group = 1      # PIN is typed with the Group 1 letters / digits
    _last_action = "ENTER PIN + ENTER"
    print("Secrets LOCKED — type PIN in Morse, then ENTER (ESC cancels)")
    _beep_notify(duration=BEEP_GROUP_S, freq=GROUP_FREQ)

def _pin_end(msg):
    global _pin_active, _pin_buf, _pin_pending, _last_action
    _pin_active  = False
    _pin_buf     = []
    _pin_pending = None
    _last_action = msg
    print(msg)

def _pin_finish():
    global _SECRETS, _secrets_locked, _last_action, _pin_buf
    pin = "".join(_pin_buf).strip().lower()
    _pin_buf = []
    _last_action = "UNLOCKING..."
    _update_display()
    try:
        result = _decrypt_secrets(_SECRETS_ENC, pin)
    except Exception as e:
        print("Secrets: unlock error (%s)" % e)
        result = None
    pin = None
    gc.collect()
    pending = _pin_pending
    if result is None:
        _pin_end("WRONG PIN")
        _beep_notify(duration=0.4, freq=300)
        return
    _SECRETS        = result
    _secrets_locked = False
    _pin_end("UNLOCKED")
    _beep_notify(duration=BEEP_GROUP_S, freq=CONFIRM_FREQ)
    if pending is not None:
        time.sleep(0.2)
        _exec_secret(pending, "")

def _pin_input(action):
    """Called instead of execute() while the PIN is being typed. Nothing
    reaches the computer; only letters/digits/punctuation are collected."""
    global _pin_last_t, _last_action
    _pin_last_t = time.monotonic()
    if isinstance(action, str) and _is_command(action):
        return                             # no commands - not even group changes -
                                           # until the PIN is finished or cancelled
    if action in (Keycode.ENTER, Keycode.KEYPAD_ENTER) or action == "\n":
        _pin_finish()
        return
    if action == Keycode.ESCAPE or (action == Keycode.BACKSPACE and not _pin_buf):
        _pin_end("PIN CANCELLED")
        return
    if action == Keycode.BACKSPACE:
        _pin_buf.pop()
    elif isinstance(action, str) and len(action) == 1 and action not in "\t":
        _pin_buf.append(action)
    else:
        return                             # anything else: ignored, not sent
    _beep_notify()
    _last_action = ("PIN " + "*" * len(_pin_buf))[:20]

def _secrets_lock(reason="LOCKED"):
    global _SECRETS, _secrets_locked, _last_action
    if _SECRETS_ENC is None:
        _last_action = "NO PIN FILE"
        return
    _SECRETS        = {}
    _secrets_locked = True
    gc.collect()
    _last_action = reason
    print("Secrets: " + reason)

def _exec_secret(sec, pattern):
    global _last_action, _last_repeatable, _repeat_label, _last_mouse_vec, active_group
    if _secrets_locked:
        _pin_start(sec)
        return
    value = _SECRETS.get(sec.key)
    if value is None:
        value = sec.placeholder
        label = f'"{value[:16]}"'
    else:
        label = f"SECRET {sec.key}"
    _last_action     = label[:20]
    _last_repeatable = None               # never auto-repeat a password
    _repeat_label    = ""
    _last_mouse_vec  = (0, 0, 0)
    print(f"{pattern}  {label}")
    _exec_text(value)
    _beep_notify()
    if active_group == 3:                                   # auto-return after macro
        active_group = 1
        print(f"GROUP -> 1 ({_GROUP_NAMES[1]})  [auto-return from Macro]")


def execute(action, pattern=""):
    """Run one action, never letting an error in it stop the device.

    For many users this is their only way to use the computer, so an
    unexpected problem in a single action (a bad value in morse_map.py, a
    hiccup in a USB report) must not end the program. The error is printed to
    the USB log and shown on screen, all keys and buttons are released, and
    the device carries on."""
    global _last_action, _drag_active
    try:
        _execute(action, pattern)
    except Exception as e:           # not KeyboardInterrupt: Ctrl-C still stops it
        print("ERROR in action %r: %s: %s" % (pattern, type(e).__name__, e))
        _last_action = "ERROR - SEE LOG"
        try:
            kbd.release_all()
            mouse.release_all()
            _drag_active = False
        except Exception:
            pass


def _execute(action, pattern=""):
    """Dispatch an action value from morse_map to the appropriate executor."""
    global _last_action, _last_repeatable, _last_mouse_vec, active_group
    global _repeat_label
    if _reset_confirm:
        _reset_confirm_input(action)
        return
    if _pin_active:
        _pin_input(action)
        return
    if _Secret is not None and isinstance(action, _Secret):
        _exec_secret(action, pattern)
        return
    if isinstance(action, CC):
        label = _CC_NAMES.get(action.code, f"CC {action.code}")
        _last_action     = label[:20]
        _last_repeatable = None        # CC not yet repeatable (would re-fire same code)
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  {label}")
        _exec_consumer(action)
        _beep_notify()
        if active_group == 3:                               # auto-return after macro
            active_group     = 1
            _last_repeatable = None
            print(f"GROUP -> 1 ({_GROUP_NAMES[1]})  [auto-return from Macro]")
    elif isinstance(action, tuple):
        label = " + ".join(_KEYCODE_NAMES.get(k, f"KEY {k}") for k in action)
        _last_action     = label[:20] if label else "COMBO"
        _last_repeatable = action
        _repeat_label    = _last_action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  {label}")
        _exec_combo(action)
        _beep_notify()
        if active_group == 3:                               # auto-return after macro
            active_group     = 1
            _last_repeatable = None
            print(f"GROUP -> 1 ({_GROUP_NAMES[1]})  [auto-return from Macro]")
    elif isinstance(action, int):
        label = _KEYCODE_NAMES.get(action, f"KEY {action}")
        _last_action     = label[:20]
        if action in _NO_REPEAT_KEYCODES:
            # Excluded from repeat (e.g. PAGE_UP/PAGE_DOWN): an accidental
            # repeat here scrolls far past where you were. Leave nothing armed
            # so a following `repeat` is a no-op.
            _last_repeatable = None
            _repeat_label    = ""
        else:
            _last_repeatable = action
            _repeat_label    = _last_action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  {label}")
        _exec_keycode(action)
        _beep_notify()
        if active_group == 3:                               # auto-return after macro
            active_group     = 1
            _last_repeatable = None
            print(f"GROUP -> 1 ({_GROUP_NAMES[1]})  [auto-return from Macro]")
    elif isinstance(action, str):
        if _is_command(action):
            # Friendly label for display + serial (raw `action` still dispatched).
            # Fallback uppercases anything not in _FRIENDLY_CMD so REPEAT,
            # MSLOW, MFAST, MRESET, and user-added commands also display
            # in the same all-caps style.
            display = _FRIENDLY_CMD.get(action, action.upper())
            verb    = action.split(' ')[0]
            if verb == 'repeat':
                # Toggle first, then describe the resulting state. Showing a
                # bare "REPEAT" left no way to tell WHAT was repeating, which
                # matters once the device is in daily use and the repeat may
                # have been armed several actions ago.
                was_on = _mouse_repeating
                _exec_command(action)
                if _mouse_repeating:
                    display = f"RPT {_repeat_label}" if _repeat_label else "REPEAT"
                elif was_on:
                    display = "RPT OFF"
                else:
                    display = "NOTHING TO RPT"
                _last_action = display[:20]
                print(f"{pattern}  {display}")
            else:
                _last_action = display[:20]
                print(f"{pattern}  {display}")
                _exec_command(action)
                # mmove is the only command that leaves something repeatable
                # (via _last_mouse_vec); clicks and drags explicitly clear it.
                if verb == 'mmove':
                    _repeat_label = _last_action
            # commands (including "group 3") are NOT auto-returned — intentional
        else:
            # Single char: friendly word for punctuation, uppercase for letters/digits.
            # Multi-char macros: keep as quoted text (user-supplied content).
            if len(action) == 1:
                label = _FRIENDLY_CHAR.get(action, action.upper())
            else:
                label = f'"{action[:16]}"'
            _last_action     = label[:20]
            _last_repeatable = action
            _repeat_label    = _last_action
            _last_mouse_vec  = (0, 0, 0)
            print(f"{pattern}  {label}")
            _exec_text(action)
            _beep_notify()
            if active_group == 3:                           # auto-return after macro
                active_group     = 1
                _last_repeatable = None
                print(f"GROUP -> 1 ({_GROUP_NAMES[1]})  [auto-return from Macro]")

# ── Group cycling via long-press ───────────────────────────────────────────────

def cycle_group(direction):
    """direction: +1 = forward, -1 = backward through groups 1–9 (group 0 skipped).
    The Switch group is skipped too: long presses don't cycle out of it (games
    need long holds), so landing there by cycling would strand you. Enter it
    on purpose with its Group 0 code. The 8-symbol Group 0 toggle codes are the
    direct-jump fast path to any group."""
    global active_group, _last_action, _last_repeatable
    if _pin_active or _reset_confirm:
        return                  # PIN entry / reset confirm stay in Group 1
    active_group     = (active_group - 1 + direction) % 9 + 1
    if _SWITCH_GROUP and active_group == _SWITCH_GROUP:
        active_group = (active_group - 1 + direction) % 9 + 1
    _last_repeatable = None     # reset repeat on group change — must mmove first
    _last_action     = f"-> group {active_group}"
    print(f"GROUP -> {active_group} ({_GROUP_NAMES[active_group]})")
    _beep_notify(duration=BEEP_GROUP_S, freq=GROUP_FREQ)

# ── Display ────────────────────────────────────────────────────────────────────
#
# Layout on the 240 × 135 px landscape TFT:
#   Row 1  group name               (large, group-coloured)
#   Row 2  morse buffer             (dots and dashes in progress)
#   Row 3  last executed action     (yellow)
#   Row 4  armed modifiers / speed  (orange)
#   Bottom pressure bar             (green = puff, red = sip)

_GROUP_NAMES  = ["BASE", "KEYBOARD", "MOUSE", "MACRO", "SCANNING",
                 "MEDIA", "GROUP 6", "GROUP 7", "GROUP 8", "GROUP 9"]
if _SWITCH_GROUP:
    _GROUP_NAMES[_SWITCH_GROUP] = "SWITCH"
_GROUP_COLORS = (0x606060, 0x0080FF, 0x00C040, 0xFF8000, 0xFF00FF,
                 0xFFFF00, 0x00FFFF, 0xFF0080, 0x8000FF, 0xFF4000)

# Local display (built-in TFT). A screenless board (e.g. an ESP-NOW sender with
# no screen) sets USE_DISPLAY = False in config.py: the device still types over
# USB and still broadcasts to a wireless receiver — only the local screen is off.
# Also auto-detects a missing board.DISPLAY so such a board can't crash here even
# if the flag was left on.
try:
    _USE_DISPLAY = USE_DISPLAY
except NameError:
    _USE_DISPLAY = True   # older config.py without the setting: assume a screen

display = None
if _USE_DISPLAY:
    try:
        display = board.DISPLAY
    except AttributeError:
        _USE_DISPLAY = False
        print("No board.DISPLAY on this board — running screenless. Set USE_DISPLAY = False in config.py to silence this.")

if _USE_DISPLAY:
    try:
        display.rotation = DISPLAY_ROTATION
    except AttributeError:
        print("WARNING: display rotation not settable — upgrade CircuitPython to 9.x")
    # Backlight level from config.py (0.1–1.0). Never below 0.1, so a typo
    # can't black out the screen; older config.py without it keeps full.
    try:
        display.brightness = min(1.0, max(0.1, float(DISPLAY_BRIGHTNESS)))
    except NameError:
        pass
    except Exception as _e:
        print("WARNING: display brightness not set (%s)" % _e)

def _make_label(root, text, color, scale, y):
    lbl = label.Label(
        terminalio.FONT, text=text, color=color, scale=scale,
        anchor_point=(0.5, 0.0),
        anchored_position=(display.width // 2, y),
    )
    root.append(lbl)
    return lbl

def _build_display():
    # terminalio.FONT glyphs are ~14 px tall; at scale=2 each row ≈ 28 px.
    # Four rows × 28 px = 112 px + 4 px top margin = 116 px.
    # Pressure bar (8 px tall) sits at y=126, ending at y=134 — within 135 px.
    root = displayio.Group()

    bmp = displayio.Bitmap(display.width, display.height, 1)
    pal = displayio.Palette(1)
    pal[0] = 0x000020
    root.append(displayio.TileGrid(bmp, pixel_shader=pal))

    lbl_group  = _make_label(root, f"[ {_GROUP_NAMES[1]} ]", _GROUP_COLORS[1], 2,  2)
    lbl_buf    = _make_label(root, " ",             0x00FFFF,          2, 30)
    lbl_action = _make_label(root, " ",             0xFFFF00,          2, 58)
    # Orange "RPT" tag pinned to the LEFT of the action row (row 3), shown only
    # while a repeat is active. This lets the RPT flag stand out in orange
    # against the yellow repeated-action name on the same row. Left-anchored
    # (0.0) so its x position is fixed while lbl_action stays centred.
    lbl_rpt    = label.Label(terminalio.FONT, text=" ", color=0xFF8000, scale=2,
                             anchor_point=(0.0, 0.0), anchored_position=(4, 58))
    root.append(lbl_rpt)
    lbl_mods   = _make_label(root, " ",             0xFF8000,          2, 86)

    bar_bg_bmp = displayio.Bitmap(display.width - 8, 8, 1)
    bar_bg_pal = displayio.Palette(1)
    bar_bg_pal[0] = 0x202020
    root.append(displayio.TileGrid(bar_bg_bmp, pixel_shader=bar_bg_pal, x=4, y=126))

    # Foreground bar — full-width bitmap. Palette index 0 = transparent
    # (matches background), index 1 = direction colour painted by
    # _update_display() based on sip / puff.
    bar_pal = displayio.Palette(2)
    bar_pal.make_transparent(0)
    bar_pal[1] = 0x00FF00
    bar_bmp = displayio.Bitmap(display.width - 8, 8, 2)
    root.append(displayio.TileGrid(bar_bmp, pixel_shader=bar_pal, x=4, y=126))

    display.root_group = root
    return lbl_group, lbl_buf, lbl_action, lbl_rpt, lbl_mods, bar_pal, bar_bmp

_lbl_group = _lbl_buf = _lbl_action = _lbl_rpt = _lbl_mods = None
_bar_pal = _bar_bmp = None
_BAR_WIDTH_PX = 0
_last_bar_fill = 0    # tracks last frame's fill width for incremental updates
if _USE_DISPLAY:
    _lbl_group, _lbl_buf, _lbl_action, _lbl_rpt, _lbl_mods, _bar_pal, _bar_bmp = _build_display()
    _BAR_WIDTH_PX = display.width - 8

_MOD_NAMES = {
    Keycode.LEFT_CONTROL:  "Ctrl",  Keycode.RIGHT_CONTROL: "RCtrl",
    Keycode.LEFT_SHIFT:    "Shift", Keycode.RIGHT_SHIFT:   "RShft",
    Keycode.LEFT_ALT:      "Alt",   Keycode.RIGHT_ALT:     "RAlt",
    Keycode.LEFT_GUI:      "Win",   Keycode.RIGHT_GUI:     "RWin",
}

# Start-up screen: the device name (config.py DEVICE_NAME), firmware version and
# CircuitPython version until the first sip / puff / switch press, then the
# normal group display.
# The version is read from this file's own header line, so it can't go stale.
try:
    _SPLASH_NAME = str(DEVICE_NAME).strip()[:20] or "AeroMorse"
except NameError:
    _SPLASH_NAME = "AeroMorse"   # older config.py without DEVICE_NAME
_SPLASH_VERSION = ""
try:
    with open("/code.py") as _f:
        _head = _f.read(600)
    _i = _head.find("version ")
    if _i >= 0:
        _SPLASH_VERSION = "v" + _head[_i + 8:].split()[0]
    _head = None
except Exception:
    pass
try:                                   # CircuitPython version, e.g. "CP 9.2.9"
    import os as _os
    # uname().version is e.g. "11.0.0-alpha.1 on 2026-09-24"; .release would
    # drop the "-alpha.1", which matters when a board runs a test build.
    _SPLASH_CP = ("CP " + _os.uname().version.split(" on ")[0])[:20]
except Exception:
    _SPLASH_CP = ""
_show_splash = True

def _update_display(pressure=0.0):
    # Build strings first so they can be shared with the wireless display.
    group_str  = f"[ {_GROUP_NAMES[active_group]} ]"
    buf_str    = _pending_to_str(_num_shifts, _pending_char)
    action_str = _last_action[:20] if _last_action else " "
    if _show_splash:
        group_str  = _SPLASH_NAME
        action_str = _SPLASH_VERSION or " "

    # Build the status line by concatenating whatever is active. Previously
    # this was an if/elif chain, which meant DRAG stayed invisible whenever
    # SLOW/FAST was also on — the first matching branch won.
    _pieces = []
    mods_text = " ".join(_MOD_NAMES.get(m, "?") for m in sorted(_armed_mods))
    if mods_text:
        _pieces.append(mods_text)
    if _mouse_speed == MOUSE_SPEED_SLOW:
        _pieces.append("SLOW")
    elif _mouse_speed == MOUSE_SPEED_FAST:
        _pieces.append("FAST")
    if _mouse_repeating:
        _pieces.append("RPT")
    if _drag_active:
        _pieces.append("DRAG")
    if _pin_active:
        _pieces.append("PIN")
    elif _SECRETS_ENC is not None and not _secrets_locked:
        _pieces.append("UNLOCKED")        # reminder: secrets are open
    mods_str = " ".join(_pieces) if _pieces else " "
    if _show_splash and not _pieces:
        mods_str = _SPLASH_CP or " "     # start-up screen, row 4

    if _USE_DISPLAY:
        # Update the local TFT.
        _lbl_group.text  = group_str
        _lbl_group.color = 0xFFFFFF if _show_splash else _GROUP_COLORS[active_group]
        _lbl_buf.text    = buf_str
        # Split a leading "RPT " off the action line so the RPT flag renders in
        # ORANGE (via the dedicated _lbl_rpt tag) while the repeated action name
        # stays YELLOW. action_str itself is left whole for the ESP-NOW broadcast
        # below, so the wireless display still shows "RPT <action>".
        # The tag + name are centred together as ONE unit: the combined string
        # would span len*12 px (terminalio.FONT is 12 px/char at scale 2), so both
        # labels are left-anchored from that block's centred start — the tag first,
        # the name one "RPT " width in. Reads like a normal centred row that just
        # happens to be two colours, rather than the tag pinned to the far left.
        if action_str.startswith("RPT "):
            _rpt_left = max(0, (display.width - len(action_str) * 12) // 2)
            _lbl_rpt.text                 = "RPT"
            _lbl_rpt.anchor_point         = (0.0, 0.0)
            _lbl_rpt.anchored_position    = (_rpt_left, 58)
            _lbl_action.text              = action_str[4:]
            _lbl_action.anchor_point      = (0.0, 0.0)
            _lbl_action.anchored_position = (_rpt_left + 4 * 12, 58)
        else:
            _lbl_rpt.text    = " "
            _lbl_action.text = action_str
            _lbl_action.anchor_point      = (0.5, 0.0)
            _lbl_action.anchored_position = (display.width // 2, 58)
        _lbl_mods.text   = mods_str
        if USE_SENSOR:
            # Pressure bar — direction colour + magnitude-encoded fill width.
            # pressure is delta-from-baseline (hPa): negative = sip, positive = puff.
            # Bar fills to 100% at the trigger threshold (THRESH_SIP / THRESH_PUFF)
            # and saturates beyond that.
            _bar_pal[1] = 0x00FF00 if pressure >= 0 else 0xFF4000
            if pressure >= 0:
                ratio = min(pressure / THRESH_PUFF, 1.0) if THRESH_PUFF else 0
            else:
                ratio = min(-pressure / THRESH_SIP, 1.0) if THRESH_SIP else 0
            fill_px = int(ratio * _BAR_WIDTH_PX)
            global _last_bar_fill
            if fill_px != _last_bar_fill:
                # Only repaint the columns that changed between last frame and this
                # frame. Keeps display refresh cheap (avoids painting 232x8 every
                # 100 ms).
                lo = min(fill_px, _last_bar_fill)
                hi = max(fill_px, _last_bar_fill)
                for x in range(lo, hi):
                    v = 1 if x < fill_px else 0
                    for y in range(8):
                        _bar_bmp[x, y] = v
                _last_bar_fill = fill_px

    # Mirror to wireless OLED (no-op if ESP-NOW not initialised). While a PIN is
    # being typed the dots/dashes are hidden there — the remote screen may be
    # visible to others; the local screen keeps them so you can see your input.
    if _pin_active:
        buf_str = "*" * _num_shifts if _num_shifts else " "
    _espnow_send(group_str, buf_str, action_str, mods_str)

# ── Main loop ──────────────────────────────────────────────────────────────────
#
# State machine mirrors AirTalker v2:
#   • Read sensor → DIT / DAH / IDLE
#   • On transition DIT/DAH → IDLE: shift bit into accumulator (or long-press)
#   • After ACCEPT_DELAY of idle with bits pending: commit and look up

_last_display = 0.0
_DISPLAY_RATE = 0.1     # cap display refresh at 10 Hz

while True:
    now = time.monotonic()

    # ── Timed audio release ─────────────────────────────────────────────────
    _audio_tick()

    # ── Read sensor / switches ──────────────────────────────────────────────
    if USE_SENSOR:
        raw = lps.pressure
        _avg_pressure.add(raw)
        _display_pressure = raw - _baseline

        # Auto-zero: while no input is active, slowly drift baseline toward
        # the current raw reading so weather / HVAC / temperature changes
        # in ambient atmospheric pressure don't accumulate into a phantom
        # sip. Frozen during DIT / DAH so a held sip never gets absorbed.
        if _BASELINE_ALPHA and _last_state == IDLE:
            _baseline += (raw - _baseline) * _BASELINE_ALPHA
            _sip_threshold  = _baseline - THRESH_SIP
            _puff_threshold = _baseline + THRESH_PUFF

        # Raw candidate state from pressure thresholds.
        if raw > _puff_threshold:
            candidate = DAH
        elif raw < _sip_threshold:
            candidate = DIT
        else:
            candidate = IDLE
        # Debounce: require DEBOUNCE_SAMPLES consecutive agreeing readings
        # before accepting a new state. Filters mid-element pressure wobble.
        if candidate == _candidate_state:
            if _candidate_count < DEBOUNCE_SAMPLES:
                _candidate_count += 1
        else:
            _candidate_state = candidate
            _candidate_count = 1
        new_state = _candidate_state if _candidate_count >= DEBOUNCE_SAMPLES else _last_state

        # Sip straight into puff (or puff into sip) with no rest seen in between —
        # the swing can be only a few ms, or fall inside a screen update. End
        # the first press here (one pass of IDLE) so its dot/dash is counted;
        # the next pass starts the other one. Without this it was dropped.
        if new_state != IDLE and _last_state != IDLE and new_state != _last_state:
            new_state = IDLE

        # Split on a dip: a sip/puff that falls well below its peak and then
        # climbs again is two presses that ran together. End the first one here
        # (one pass of IDLE); the next pass starts the second as a new press.
        if _SPLIT_FRAC:
            if _last_state == IDLE:
                _sp_peak = 0.0
                _sp_low  = None
            elif (new_state == _last_state and SWITCH_MODE != 1
                    and not _CODE_REPEAT_ACTIVE and not _strong_handled
                    and not _consuming_press and active_group != _SWITCH_GROUP
                    and now - _press_start < _SPLIT_MAX_S):
                _sp_a = _display_pressure if _last_state == DAH else -_display_pressure
                if _sp_low is None:
                    if _sp_a > _sp_peak:
                        _sp_peak = _sp_a
                    elif _sp_a < _sp_peak * _SPLIT_FRAC:
                        _sp_low = _sp_a
                elif _sp_a < _sp_low:
                    _sp_low = _sp_a
                elif _sp_a >= _sp_low + _SPLIT_RISE:
                    new_state = IDLE
    else:
        dot_dn  = not _dot_btn.value    # active-low with pull-up
        dash_dn = not _dash_btn.value
        new_state = DIT if dot_dn else (DAH if dash_dn else IDLE)
        _display_pressure = 0.0

    # 1-switch mode mask: ignore the input that isn't ONE_SWITCH_INPUT
    if SWITCH_MODE == 1:
        if _ONE_SWITCH_USES_DIT and new_state == DAH:
            new_state = IDLE
        elif (not _ONE_SWITCH_USES_DIT) and new_state == DIT:
            new_state = IDLE

    # ── Strong sip / strong puff detection ──────────────────────────────────
    # Track peak |pressure - baseline| during a held press. When it crosses
    # the STRONG threshold, fire the configured STRONG_*_ACTION exactly once
    # per press. The press is then "claimed" — no dot/dash is emitted, no
    # auto-repeat fires, no cycle/accept on release. Sensor mode only.
    # Off in STRONG_OFF_IN_GROUPS, in the Switch group, and while a PIN or the
    # devicereset y/n is being typed (a hard sip/puff there is a normal dot/dash).
    if (USE_SENSOR and not _strong_handled and _last_state in (DIT, DAH)
            and active_group not in _STRONG_OFF and active_group != _SWITCH_GROUP
            and not _pin_active and not _reset_confirm):
        abs_delta = abs(_display_pressure)
        if abs_delta > _peak_delta:
            _peak_delta = abs_delta
        if _last_state == DIT and _peak_delta >= THRESH_SIP_STRONG and STRONG_SIP_ACTION:
            execute(STRONG_SIP_ACTION, "STRONG SIP")
            _pending_char   = 0
            _num_shifts     = 0
            _strong_handled = True
        elif _last_state == DAH and _peak_delta >= THRESH_PUFF_STRONG and STRONG_PUFF_ACTION:
            execute(STRONG_PUFF_ACTION, "STRONG PUFF")
            _pending_char   = 0
            _num_shifts     = 0
            _strong_handled = True

    # ── Switch group: release a held key whenever we are no longer in it ────
    # (e.g. a strong sip/puff just changed group while the key was down).
    in_switch = bool(_SWITCH_GROUP) and active_group == _SWITCH_GROUP
    if _sw_key is not None and not in_switch:
        kbd.release(_sw_key)
        _sw_key = None

    # ── Code-repeat auto-emit (Darci-style hold-to-repeat) ──────────────────
    # While DIT/DAH is held in SWITCH_MODE = 2 with CODE_REPEAT on, emit one
    # symbol per repeat interval — 1 at press, +1 every DOT/DASH_REPEAT_MS.
    # Cap at CODE_REPEAT_MAX to prevent buffer overflow on a forgotten hold.
    # Skipped if a strong gesture has already fired for this press.
    if (_CODE_REPEAT_ACTIVE and _last_state in (DIT, DAH) and not _mouse_repeating
            and not _strong_handled and not in_switch):
        interval = _DOT_REPEAT_S if _last_state == DIT else _DASH_REPEAT_S
        held_duration = now - _press_start
        expected_count = 1 + int(held_duration / interval)
        while _stream_count < expected_count and _stream_count < CODE_REPEAT_MAX:
            _pending_char = (_pending_char << 1) | _last_state
            _num_shifts  += 1
            _stream_count += 1

    # ── Switch group: sip / puff hold a key, like two real switches ─────────
    # No Morse here: the key goes down the moment a sip/puff starts and comes
    # up when it ends. Short/long/hard sips and puffs do nothing else (games
    # need them). The group is left automatically after SWITCH_IDLE_EXIT_S
    # seconds with no sip/puff, or by holding one puff SWITCH_EXIT_PUFF_S s.
    if in_switch:
        if (_SW_IDLE_S and _last_state == IDLE and new_state == IDLE
                and now - _last_trans_at >= _SW_IDLE_S):
            active_group   = _SW_EXIT_GROUP
            _last_action   = "-> " + _GROUP_NAMES[_SW_EXIT_GROUP]
            _last_trans_at = now
            print("SWITCH exit (idle %.0f s) -> group %d" % (_SW_IDLE_S, _SW_EXIT_GROUP))
            _beep_notify(duration=BEEP_GROUP_S, freq=GROUP_FREQ)
        elif (_last_state == DAH and new_state == DAH and not _sw_skip
                and now - _press_start >= _SW_EXIT_S):
            # Exit gesture: very long puff. Let go of the key and switch group
            # now; the rest of this puff is swallowed (no cycle, no strong).
            if _sw_key is not None:
                kbd.release(_sw_key)
                _sw_key = None
            active_group     = _SW_EXIT_GROUP
            _consuming_press = True
            _strong_handled  = True
            _last_action     = "-> " + _GROUP_NAMES[_SW_EXIT_GROUP]
            print("SWITCH exit (%.0f s puff) -> group %d" % (_SW_EXIT_S, _SW_EXIT_GROUP))
            _beep_notify(duration=BEEP_GROUP_S, freq=GROUP_FREQ)
        elif new_state != _last_state:
            if _sw_key is not None:                 # press ended (or sip<->puff)
                kbd.release(_sw_key)
                _sw_key = None
                _last_action = " "
            if new_state == IDLE:
                _beep_stop()
                _sw_skip = False
            else:
                if _last_state == IDLE:             # a new press starts
                    _press_start    = now
                    _peak_delta     = 0.0
                    _strong_handled = False
                    _beep_start(new_state)
                    _sw_skip = _show_splash         # first press only dismisses it
                    _show_splash = False
                if not _sw_skip and not _strong_handled:
                    _armed_mods.clear()
                    _sw_key = _SW_SIP_KEY if new_state == DIT else _SW_PUFF_KEY
                    kbd.press(_sw_key)
                    _last_action = ("HOLD " + _KEYCODE_NAMES.get(_sw_key, "KEY"))[:20]
            _pending_char  = 0
            _num_shifts    = 0
            _last_trans_at = now
            _last_state    = new_state

    # ── State machine ───────────────────────────────────────────────────────
    elif new_state != _last_state:

        if _mouse_repeating:
            # New input cancels mouse repeat. Mark this press as consumed so
            # its release is not recorded as a Morse element. We deliberately
            # do NOT force new_state to IDLE — the press lands normally and
            # the release path discards it via _consuming_press.
            _stop_mouse_repeat()
            _beep_stop()
            _consuming_press = True

        elif _last_state == IDLE:
            # IDLE → DIT/DAH: record when the press started, begin sidetone,
            # reset the code-repeat stream counter and strong-press tracking
            _press_start    = now
            _stream_count   = 0
            _peak_delta     = 0.0
            _strong_handled = False
            if _show_splash:
                # The first press on the start-up screen only dismisses it:
                # swallow it entirely (no dot/dash, no strong-gesture action,
                # no group cycle) so nothing reaches the computer.
                _show_splash     = False
                _consuming_press = True
                _strong_handled  = True
            _beep_start(new_state)

        elif new_state == IDLE:
            # DIT/DAH → IDLE: stop sidetone, commit the element (or long-press)
            _beep_stop()
            duration = now - _press_start

            # If this press was the one that cancelled a mouse repeat, swallow
            # the release entirely — no bit shift, no cycle, no accept.
            if _consuming_press:
                _consuming_press = False
            # If a strong gesture already fired during the hold, the press
            # has been fully handled — skip all dot/dash/cycle/accept logic.
            elif _strong_handled:
                pass
            elif SWITCH_MODE == 1:
                # Single-switch timed: classify by duration
                if duration >= LONG_PRESS and LONG_PRESS_CYCLES_GROUP:
                    # Very long hold → forward cycle (no cycle-back in 1-switch)
                    cycle_group(+1)
                    _pending_char = 0
                    _num_shifts   = 0
                elif duration <= _ONE_SWITCH_DOT_S:
                    # Short press → dot bit (0)
                    _pending_char = (_pending_char << 1) | 0
                    _num_shifts  += 1
                else:
                    # Medium press → dash bit (1)
                    _pending_char = (_pending_char << 1) | 1
                    _num_shifts  += 1

            elif SWITCH_MODE == 3:
                # Three-switch: short presses are bits; long-press of the
                # configured gesture is Accept; long-press of the other gesture
                # is forward cycle (when LONG_PRESS_CYCLES_GROUP).
                if duration >= LONG_PRESS:
                    is_accept_gesture = (
                        (_THIRD_SWITCH_IS_DAH and _last_state == DAH) or
                        ((not _THIRD_SWITCH_IS_DAH) and _last_state == DIT)
                    )
                    if is_accept_gesture:
                        # Explicit Accept: commit pending pattern immediately
                        if _num_shifts > 0:
                            pattern = _pending_to_str(_num_shifts, _pending_char)
                            action  = lookup_action(_num_shifts, _pending_char)
                            if action is not None:
                                execute(action, pattern)
                            else:
                                _last_action = f"? {pattern}"
                                print(f"{pattern}  ?")
                            _pending_char = 0
                            _num_shifts   = 0
                    elif LONG_PRESS_CYCLES_GROUP:
                        # Long-press of the OTHER gesture → forward cycle
                        cycle_group(+1)
                        _pending_char = 0
                        _num_shifts   = 0
                    # else: long-press of non-Accept gesture is a no-op
                else:
                    # Normal short press → shift bit (DIT=0, DAH=1)
                    _pending_char = (_pending_char << 1) | _last_state
                    _num_shifts  += 1

            else:
                # SWITCH_MODE == 2 — paddle-style
                long_held = duration >= LONG_PRESS
                handled = False

                # Switch-mode "strong" equivalent: when not using the
                # pressure sensor, the strong-gesture is a long-press of
                # the corresponding switch (DIT-side or DAH-side). Takes
                # precedence over LONG_PRESS_CYCLES_GROUP. Sensor mode
                # uses the peak-pressure detector above instead, so this
                # block intentionally fires only when USE_SENSOR is False.
                if long_held and not USE_SENSOR and active_group not in _STRONG_OFF:
                    strong_action = STRONG_SIP_ACTION if _last_state == DIT else STRONG_PUFF_ACTION
                    if strong_action:
                        execute(strong_action,
                                "STRONG DOT" if _last_state == DIT else "STRONG DASH")
                        _pending_char = 0
                        _num_shifts   = 0
                        handled       = True

                if handled:
                    pass   # strong action consumed the press
                elif _CODE_REPEAT_ACTIVE:
                    # Bits already emitted during hold; release just ends the
                    # stream. Optionally cycle group on very long holds.
                    if LONG_PRESS_CYCLES_GROUP and long_held:
                        cycle_group(-1 if _last_state == DIT else +1)
                        _pending_char = 0
                        _num_shifts   = 0
                elif LONG_PRESS_CYCLES_GROUP and long_held:
                    # Original long-press cycle behaviour
                    cycle_group(-1 if _last_state == DIT else +1)
                    _pending_char = 0
                    _num_shifts   = 0
                else:
                    # Tap-per-symbol — shift current state bit into accumulator
                    _pending_char = (_pending_char << 1) | _last_state
                    _num_shifts  += 1

        _last_trans_at = now
        _last_state    = new_state

    elif _last_state == IDLE and _num_shifts > 0 and (now - _last_trans_at) >= (
            _MOUSE_ACCEPT_DELAY if active_group == _MOUSE_GROUP else ACCEPT_DELAY):
        # Been idle long enough — look up and fire the accumulated pattern.
        # Mouse group (2) uses the shorter MOUSE_ACCEPT_DELAY so clicks fire sooner.
        pattern = _pending_to_str(_num_shifts, _pending_char)
        action  = lookup_action(_num_shifts, _pending_char)
        if action is not None:
            execute(action, pattern)
        else:
            _last_action = f"? {pattern}"
            print(f"{pattern}  ?")
        _pending_char  = 0
        _num_shifts    = 0
        _last_trans_at = now

    elif _mouse_repeating:
        _mouse_repeat_tick()

    # ── Secrets: PIN-entry timeout and optional auto-lock ───────────────────
    if _reset_confirm and now - _reset_t > _RESET_TIMEOUT:
        _reset_cancel("RESET TIMED OUT")
    if _pin_active and now - _pin_last_t > _PIN_TIMEOUT:
        _pin_end("PIN TIMED OUT")
    elif (_AUTOLOCK_S and not _secrets_locked and _SECRETS_ENC is not None
          and _last_state == IDLE and now - _last_trans_at > _AUTOLOCK_S):
        _secrets_lock("AUTO-LOCKED")

    # ── Display refresh (capped at 10 Hz) ───────────────────────────────────
    if now - _last_display >= _DISPLAY_RATE:
        _update_display(_display_pressure)
        _last_display = now
