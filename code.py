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
#   Group 4  scanning — F1–F12 on the 12 shortest codes (Switch Control)
#   Group 5–9  placeholders (copy of g1 letters + numbers — customise)
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
            # Keyboard and mouse are separate USB HID interfaces, so the host
            # can process their reports out of order. Without a settle delay
            # the click often lands before the modifier registers and the host
            # sees a plain click — which is why Ctrl+click multi-select failed.
            kbd.press(*_armed_mods)
            time.sleep(MOUSE_CLICK_MOD_DELAY)
        for _ in range(count):
            mouse.click(btn)
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

    elif verb == 'mreset':
        _mouse_speed    = MOUSE_SPEED_NORMAL
        _last_mouse_vec = (0, 0, 0)
        _stop_mouse_repeat()
        if _drag_active:
            mouse.release(Mouse.LEFT_BUTTON)
            mouse.release(Mouse.RIGHT_BUTTON)
            _drag_active = False


_CMD_VERBS = {'group', 'mmove', 'mclick', 'mdrag', 'repeat', 'mslow', 'mfast', 'mreset'}

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


def _is_command(action):
    return action.split(' ')[0] in _CMD_VERBS


def _exec_consumer(cc_action):
    """Send a USB HID ConsumerControl code (media keys, volume, brightness, etc.)."""
    if _CC_AVAILABLE:
        cc_device.send(cc_action.code)


def execute(action, pattern=""):
    """Dispatch an action value from morse_map to the appropriate executor."""
    global _last_action, _last_repeatable, _last_mouse_vec, active_group
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
        _last_repeatable = action
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
            _last_action = display[:20]
            print(f"{pattern}  {display}")
            _exec_command(action)
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
    The 8-symbol Group 0 toggle codes are the direct-jump fast path to any group."""
    global active_group, _last_action, _last_repeatable
    active_group     = (active_group - 1 + direction) % 9 + 1
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

_GROUP_NAMES  = ("BASE", "KEYBOARD", "MOUSE", "MACRO", "SCANNING",
                 "MEDIA", "GROUP 6", "GROUP 7", "GROUP 8", "GROUP 9")
_GROUP_COLORS = (0x606060, 0x0080FF, 0x00C040, 0xFF8000, 0xFF00FF,
                 0xFFFF00, 0x00FFFF, 0xFF0080, 0x8000FF, 0xFF4000)

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

    lbl_group  = _make_label(root, f"[ {_GROUP_NAMES[1]} ]", _GROUP_COLORS[1], 2,  2)
    lbl_buf    = _make_label(root, " ",             0x00FFFF,          2, 30)
    lbl_action = _make_label(root, " ",             0xFFFF00,          2, 58)
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
    return lbl_group, lbl_buf, lbl_action, lbl_mods, bar_pal, bar_bmp

_lbl_group, _lbl_buf, _lbl_action, _lbl_mods, _bar_pal, _bar_bmp = _build_display()
_BAR_WIDTH_PX = display.width - 8
_last_bar_fill = 0    # tracks last frame's fill width for incremental updates

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
    mods_str = " ".join(_pieces) if _pieces else " "

    # Update the local TFT.
    _lbl_group.text  = group_str
    _lbl_group.color = _GROUP_COLORS[active_group]
    _lbl_buf.text    = buf_str
    _lbl_action.text = action_str
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
    if USE_SENSOR and not _strong_handled and _last_state in (DIT, DAH):
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

    # ── Code-repeat auto-emit (Darci-style hold-to-repeat) ──────────────────
    # While DIT/DAH is held in SWITCH_MODE = 2 with CODE_REPEAT on, emit one
    # symbol per repeat interval — 1 at press, +1 every DOT/DASH_REPEAT_MS.
    # Cap at CODE_REPEAT_MAX to prevent buffer overflow on a forgotten hold.
    # Skipped if a strong gesture has already fired for this press.
    if _CODE_REPEAT_ACTIVE and _last_state in (DIT, DAH) and not _mouse_repeating and not _strong_handled:
        interval = _DOT_REPEAT_S if _last_state == DIT else _DASH_REPEAT_S
        held_duration = now - _press_start
        expected_count = 1 + int(held_duration / interval)
        while _stream_count < expected_count and _stream_count < CODE_REPEAT_MAX:
            _pending_char = (_pending_char << 1) | _last_state
            _num_shifts  += 1
            _stream_count += 1

    # ── State machine ───────────────────────────────────────────────────────
    if new_state != _last_state:

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
                if long_held and not USE_SENSOR:
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
