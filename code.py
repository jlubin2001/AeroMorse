# AeroMorse — Sip-and-puff / two-switch Morse HID device
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
except ImportError:
    _ESPNOW_IMPORTABLE = False

try:
    import audiopwmio
    import synthio
    _AUDIO_AVAILABLE = True
except ImportError:
    _AUDIO_AVAILABLE = False
    print("WARNING: audio modules not available — speaker disabled")

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

from morse_map import groups

# ── Configuration ─────────────────────────────────────────────────────────────

USE_SENSOR      = True          # True  = Option A (LPS33HW #4414)  — Build Guide §4 Option A
                                # False = Option B (AT switches)      — Build Guide §4 Option B

# Pressure thresholds (hPa delta from zeroed baseline).      Build Guide §4 Option A, §10
# Raise these if you get false triggers; lower them if light sips are missed.
THRESH_SIP      = 5             # must sip this many hPa below baseline
THRESH_PUFF     = 5             # must puff this many hPa above baseline

# Timing (seconds)                                            Build Guide §10
ACCEPT_DELAY    = 0.2           # idle pause after last element before committing
LONG_PRESS      = 1.0           # hold duration that cycles the active group

# Pressure smoothing — average this many readings before thresholding.
# Increase to reduce bounce; decrease if fast elements are missed.
POINTS_TO_AVERAGE = 8

# Switch GPIO pins (used when USE_SENSOR = False)            Build Guide §4 Option B, §8C
# Wired via 3.5mm TRRS jack #1699 (B1/B2) or terminal block #2915 (B3).
DOT_PIN         = board.D5      # → TIP of dot jack / dot terminal
DASH_PIN        = board.D6      # → TIP of dash jack / dash terminal

# ── Input mode — 1 / 2 / 3 switch ──────────────────────────────────────────────
# Compare AeroMorse / Darci / Adap2U / morAce input modes in
# MORSE_DEVICES_COMPARISON.md.
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
SWITCH_MODE         = 2

# 1-switch mode only — which physical input is the sole switch
ONE_SWITCH_INPUT    = "dot"        # "dot"  = sip (sensor)  / D5 jack (switches)
                                   # "dash" = puff (sensor) / D6 jack (switches)
ONE_SWITCH_DOT_MS   = 200          # press <= this is a dot; longer is a dash
                                   # (group cycle still at LONG_PRESS)

# 3-switch mode only — which long-gesture is the "third switch" (Accept)
THIRD_SWITCH_GESTURE = "long_dash" # "long_dash" = long puff (sensor) / long-D6 (switches)
                                   # "long_dot"  = long sip  (sensor) / long-D5 (switches)
                                   # The OTHER long-gesture cycles groups forward.

# Audio                                                       Build Guide §6, §8D
# Option S1: Adafruit STEMMA Speaker #3885 wired White=A0, Red=3V, Black=GND.
# Option S2: passive piezo across A0 and GND.
# Option S3: small speaker via PAM8302 amp board on A0.
AUDIO_PIN       = board.A0
BEEP_DOT_FREQ   = 1200          # Hz — dot (sip) sidetone  — higher pitch
BEEP_DASH_FREQ  =  800          # Hz — dash (puff) sidetone — lower pitch
CONFIRM_FREQ    = 1050          # Hz — action-executed blip
GROUP_FREQ      =  550          # Hz — group-change blip
BEEP_CONFIRM_S  = 0.06          # duration of action confirm blip (seconds)
BEEP_GROUP_S    = 0.14          # duration of group-change blip (seconds)

# Mouse speeds  (raw mmove values × speed × MOUSE_SPEED_FACTOR = actual pixels)
MOUSE_SPEED_NORMAL = 2
MOUSE_SPEED_SLOW   = 1
MOUSE_SPEED_FAST   = 3
MOUSE_SPEED_FACTOR = 2          # overall scale (matches AirTalker feel)
MOUSE_REPEAT_DELAY = 0.040      # seconds between repeat ticks (40 ms)

# Display                                                    Build Guide §5, §8A
# Built-in TFT on #5691 needs no wiring. For external OLED/TFT FeatherWings or
# STEMMA QT OLEDs see Build Guide §5 tables.
DISPLAY_ROTATION   = 0          # degrees — 0 = USB on left, 180 = USB on right
                                # other valid values: 90, 270

# Wireless display (ESP-NOW)                                  Build Guide §5 "Wireless Display"
# True   = enable WiFi radio at boot and broadcast display state via ESP-NOW.
#          Required for the optional 2nd-board mirror (Option W1 / W2).
# False  = do NOT enable the radio. Saves ~80–100 mA, eliminates any RF
#          emission. Use this for battery-powered builds or whenever you have
#          no wireless display attached.
# Has no effect on boards without an `espnow` module (RP2040, M4, nRF52840) —
# the import already fails on those.
USE_WIRELESS_DISPLAY = False

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

i2c = board.STEMMA_I2C()

if USE_SENSOR and not _LPS_AVAILABLE:
    print("adafruit_lps35hw missing — switching to USE_SENSOR = False")
    USE_SENSOR = False

# Validate input-mode configuration
if SWITCH_MODE not in (1, 2, 3):
    print(f"SWITCH_MODE = {SWITCH_MODE} is not 1, 2, or 3 — falling back to 2")
    SWITCH_MODE = 2
if ONE_SWITCH_INPUT not in ("dot", "dash"):
    print(f"ONE_SWITCH_INPUT = {ONE_SWITCH_INPUT!r} invalid — falling back to 'dot'")
    ONE_SWITCH_INPUT = "dot"
if THIRD_SWITCH_GESTURE not in ("long_dot", "long_dash"):
    print(f"THIRD_SWITCH_GESTURE = {THIRD_SWITCH_GESTURE!r} invalid — falling back to 'long_dash'")
    THIRD_SWITCH_GESTURE = "long_dash"

# Derived constants (kept once, used in the main loop hot path)
_ONE_SWITCH_DOT_S    = ONE_SWITCH_DOT_MS / 1000.0
_ONE_SWITCH_USES_DIT = (ONE_SWITCH_INPUT == "dot")     # True = DIT-side input wins
_THIRD_SWITCH_IS_DAH = (THIRD_SWITCH_GESTURE == "long_dash")
print(f"Input mode: {SWITCH_MODE}-switch  (1-sw input = {ONE_SWITCH_INPUT}, 3-sw accept = {THIRD_SWITCH_GESTURE})")

if USE_SENSOR:
    lps = adafruit_lps35hw.LPS35HW(i2c)
    lps.zero_pressure()
    lps.data_rate      = adafruit_lps35hw.DataRate.RATE_75_HZ
    lps.filter_enabled = True
    lps.filter_config  = True
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
    _avg_pressure = RollingAverage(POINTS_TO_AVERAGE)

# ── Audio setup ───────────────────────────────────────────────────────────────

if _AUDIO_AVAILABLE:
    _audio_out   = audiopwmio.PWMAudioOut(AUDIO_PIN)
    _synth       = synthio.Synthesizer(sample_rate=22050)
    _audio_out.play(_synth)
    _dot_note     = synthio.Note(frequency=BEEP_DOT_FREQ)
    _dash_note    = synthio.Note(frequency=BEEP_DASH_FREQ)
    _confirm_note = synthio.Note(frequency=CONFIRM_FREQ)
    _group_note   = synthio.Note(frequency=GROUP_FREQ)

_beeping_morse     = False  # True while a DIT or DAH is held
_active_morse_note = None   # which note is currently playing
_notify_end        = 0.0    # monotonic time when the current blip should stop


def _beep_start(state):
    """Start sidetone on press — higher pitch for dot, lower for dash."""
    global _beeping_morse, _active_morse_note
    if _AUDIO_AVAILABLE and not _beeping_morse:
        # DIT == 0, DAH == 1 — constants defined further down, resolved at call time
        _active_morse_note = _dot_note if state == 0 else _dash_note
        _synth.press(_active_morse_note)
        _beeping_morse = True


def _beep_stop():
    """Stop sidetone when press releases."""
    global _beeping_morse, _active_morse_note
    if _AUDIO_AVAILABLE and _beeping_morse and _active_morse_note is not None:
        _synth.release(_active_morse_note)
        _active_morse_note = None
        _beeping_morse = False


def _beep_notify(duration=BEEP_CONFIRM_S, note=None):
    """Short timed blip for action confirmation or group change."""
    global _notify_end
    if not _AUDIO_AVAILABLE:
        return
    if note is None:
        note = _confirm_note
    _synth.press(note)
    _notify_end = time.monotonic() + duration


def _audio_tick():
    """Release the timed notification note once its duration has elapsed."""
    global _notify_end
    if _AUDIO_AVAILABLE and _notify_end and time.monotonic() >= _notify_end:
        _synth.release(_confirm_note)
        _synth.release(_group_note)
        _notify_end = 0.0


# ── ESP-NOW wireless display ───────────────────────────────────────────────────
# Broadcasts TFT state to a QT Py ESP32-C3 + SSD1306 OLED running receiver.py.
# Entirely optional — if the espnow / wifi modules are absent nothing changes.
# Wireless display hardware options — see Build Guide §5 "Wireless Display"
# (any ESP32-family Feather/QT Py as receiver; optional battery #3898/#1578/#258).

_ESPNOW_ENABLED = False
if not USE_WIRELESS_DISPLAY:
    print("ESP-NOW: disabled by USE_WIRELESS_DISPLAY = False")
elif _ESPNOW_IMPORTABLE:
    try:
        _wifi_mod.radio.enabled = True
        _espnow_dev = _espnow_mod.ESPNow()
        _espnow_dev.peers.append(_espnow_mod.Peer(mac=b'\xff\xff\xff\xff\xff\xff'))
        _ESPNOW_ENABLED = True
        print("ESP-NOW: wireless display active (broadcast)")
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
        _espnow_dev.send(msg)
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
    if text:
        layout.write(text)


def _exec_command(cmd):
    """Execute a device command: group / mmove / mclick / mdrag /
    mrepeat / mslow / mfast / mreset
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
            kbd.press(*_armed_mods)
        for _ in range(count):
            mouse.click(btn)
        if _armed_mods:
            kbd.release_all()
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

    elif verb == 'mreset':
        _mouse_speed    = MOUSE_SPEED_NORMAL
        _last_mouse_vec = (0, 0, 0)
        _stop_mouse_repeat()
        if _drag_active:
            mouse.release(Mouse.LEFT_BUTTON)
            mouse.release(Mouse.RIGHT_BUTTON)
            _drag_active = False


_CMD_VERBS = {'group', 'mmove', 'mclick', 'mdrag', 'repeat', 'mslow', 'mfast', 'mreset'}

def _is_command(action):
    return action.split(' ')[0] in _CMD_VERBS


def execute(action, pattern=""):
    """Dispatch an action value from morse_map to the appropriate executor."""
    global _last_action, _last_repeatable, _last_mouse_vec, active_group
    if isinstance(action, tuple):
        _last_action     = "COMBO"
        _last_repeatable = action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  COMBO")
        _exec_combo(action)
        _beep_notify()
        if active_group == 3:                               # auto-return after macro
            active_group     = 1
            _last_repeatable = None
            print("GROUP -> 1 (Keyboard)  [auto-return from Macro]")
    elif isinstance(action, int):
        _last_action     = f"KEY {action}"
        _last_repeatable = action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  KEY {action}")
        _exec_keycode(action)
        _beep_notify()
        if active_group == 3:                               # auto-return after macro
            active_group     = 1
            _last_repeatable = None
            print("GROUP -> 1 (Keyboard)  [auto-return from Macro]")
    elif isinstance(action, str):
        if _is_command(action):
            _last_action = action[:20]
            print(f"{pattern}  {action}")
            _exec_command(action)
            # commands (including "group 3") are NOT auto-returned — intentional
        else:
            _last_action     = f'"{action[:16]}"'
            _last_repeatable = action
            _last_mouse_vec  = (0, 0, 0)
            print(f"{pattern}  \"{action}\"")
            _exec_text(action)
            _beep_notify()
            if active_group == 3:                           # auto-return after macro
                active_group     = 1
                _last_repeatable = None
                print("GROUP -> 1 (Keyboard)  [auto-return from Macro]")

# ── Group cycling via long-press ───────────────────────────────────────────────

def cycle_group(direction):
    """direction: +1 = forward, -1 = backward through groups 1–3 (group 0 skipped)."""
    global active_group, _last_action, _last_repeatable
    active_group     = (active_group - 1 + direction) % 3 + 1
    _last_repeatable = None     # reset repeat on group change — must mmove first
    _last_action     = f"-> group {active_group}"
    print(f"GROUP -> {active_group} ({_GROUP_NAMES[active_group]})")
    _beep_notify(duration=BEEP_GROUP_S, note=_group_note if _AUDIO_AVAILABLE else None)

# ── Display ────────────────────────────────────────────────────────────────────
#
# Layout on the 240 × 135 px landscape TFT:
#   Row 1  group name               (large, group-coloured)
#   Row 2  morse buffer             (dots and dashes in progress)
#   Row 3  last executed action     (yellow)
#   Row 4  armed modifiers / speed  (orange)
#   Bottom pressure bar             (green = puff, red = sip)

_GROUP_NAMES  = ("Base", "Keyboard", "Mouse", "Macro")
_GROUP_COLORS = (0x606060, 0x0080FF, 0x00C040, 0xFF8000)

display = board.DISPLAY
try:
    display.rotation = DISPLAY_ROTATION
except AttributeError:
    print("WARNING: display rotation not settable — upgrade CircuitPython to 9.x")

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

    lbl_group  = _make_label(root, "[ Keyboard ]", _GROUP_COLORS[1], 2,  2)
    lbl_buf    = _make_label(root, " ",             0x00FFFF,          2, 30)
    lbl_action = _make_label(root, " ",             0xFFFF00,          2, 58)
    lbl_mods   = _make_label(root, " ",             0xFF8000,          2, 86)

    bar_bg_bmp = displayio.Bitmap(display.width - 8, 8, 1)
    bar_bg_pal = displayio.Palette(1)
    bar_bg_pal[0] = 0x202020
    root.append(displayio.TileGrid(bar_bg_bmp, pixel_shader=bar_bg_pal, x=4, y=126))

    bar_pal = displayio.Palette(1)
    bar_pal[0] = 0x00FFFF
    bar_bmp = displayio.Bitmap(1, 8, 1)
    root.append(displayio.TileGrid(bar_bmp, pixel_shader=bar_pal, x=4, y=126))

    display.root_group = root
    return lbl_group, lbl_buf, lbl_action, lbl_mods, bar_pal

_lbl_group, _lbl_buf, _lbl_action, _lbl_mods, _bar_pal = _build_display()

_MOD_NAMES = {
    Keycode.LEFT_CONTROL:  "Ctrl",  Keycode.RIGHT_CONTROL: "RCtrl",
    Keycode.LEFT_SHIFT:    "Shift", Keycode.RIGHT_SHIFT:   "RShft",
    Keycode.LEFT_ALT:      "Alt",   Keycode.RIGHT_ALT:     "RAlt",
    Keycode.LEFT_GUI:      "GUI",   Keycode.RIGHT_GUI:     "RGUI",
}

def _update_display(pressure=0.0):
    # Build strings first so they can be shared with the wireless display.
    group_str  = f"[ {_GROUP_NAMES[active_group]} ]"
    buf_str    = _pending_to_str(_num_shifts, _pending_char)
    action_str = _last_action[:20] if _last_action else " "

    mods_text = " ".join(_MOD_NAMES.get(m, "?") for m in sorted(_armed_mods))
    if mods_text:
        mods_str = mods_text
    elif _mouse_speed == MOUSE_SPEED_SLOW:
        mods_str = "SLOW"
    elif _mouse_speed == MOUSE_SPEED_FAST:
        mods_str = "FAST"
    elif _mouse_repeating:
        mods_str = "RPT"
    elif _drag_active:
        mods_str = "DRAG"
    else:
        mods_str = " "

    # Update the local TFT.
    _lbl_group.text  = group_str
    _lbl_group.color = _GROUP_COLORS[active_group]
    _lbl_buf.text    = buf_str
    _lbl_action.text = action_str
    _lbl_mods.text   = mods_str
    if USE_SENSOR:
        _bar_pal[0] = 0x00FF00 if pressure >= 0 else 0xFF4000

    # Mirror to wireless OLED (no-op if ESP-NOW not initialised).
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
        if raw > _puff_threshold:
            new_state = DAH
        elif raw < _sip_threshold:
            new_state = DIT
        else:
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

    # ── State machine ───────────────────────────────────────────────────────
    if new_state != _last_state:

        if _mouse_repeating:
            # Any new input cancels a mouse repeat
            _stop_mouse_repeat()
            _beep_stop()
            new_state = IDLE

        elif _last_state == IDLE:
            # IDLE → DIT/DAH: record when the press started, begin sidetone
            _press_start = now
            _beep_start(new_state)

        elif new_state == IDLE:
            # DIT/DAH → IDLE: stop sidetone, commit the element (or long-press)
            _beep_stop()
            duration = now - _press_start

            if SWITCH_MODE == 1:
                # Single-switch timed: classify by duration
                if duration >= LONG_PRESS:
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
                # is forward cycle.
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
                    else:
                        # Long-press of the OTHER gesture → forward cycle
                        cycle_group(+1)
                        _pending_char = 0
                        _num_shifts   = 0
                else:
                    # Normal short press → shift bit (DIT=0, DAH=1)
                    _pending_char = (_pending_char << 1) | _last_state
                    _num_shifts  += 1

            else:
                # SWITCH_MODE == 2 — original paddle behaviour, unchanged
                if duration >= LONG_PRESS:
                    cycle_group(-1 if _last_state == DIT else +1)
                    _pending_char = 0
                    _num_shifts   = 0
                else:
                    # Shift current state bit into accumulator (DIT=0, DAH=1)
                    _pending_char = (_pending_char << 1) | _last_state
                    _num_shifts  += 1

        _last_trans_at = now
        _last_state    = new_state

    elif _last_state == IDLE and _num_shifts > 0 and (now - _last_trans_at) >= ACCEPT_DELAY:
        # Been idle long enough — look up and fire the accumulated pattern
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

    # ── Display refresh (capped at 10 Hz) ───────────────────────────────────
    if now - _last_display >= _DISPLAY_RATE:
        _update_display(_display_pressure)
        _last_display = now
