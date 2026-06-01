# code.py — AeroMorse v2  (STEMMA QT OLED · TRRS AT-switch · STEMMA Speaker)
#
# Hardware
#   Adafruit ESP32-S3 Feather 4MB/2MB PSRAM    https://www.adafruit.com/product/5477
#   Adafruit LPS33HW pressure sensor            https://www.adafruit.com/product/4414
#   Monochrome 0.96" 128x64 OLED - STEMMA QT   https://www.adafruit.com/product/326
#   Adafruit STEMMA Speaker                     https://www.adafruit.com/product/3885
#   Adafruit TRRS Jack Breakout                 https://www.adafruit.com/product/5764
#     (breadboard alt: 3.5mm stereo jack        https://www.adafruit.com/product/1699)
#
# Input modes (select with USE_SENSOR below)
#   SENSOR  — LPS33HW via STEMMA QT: sip lowers pressure (dot), puff raises it (dash)
#   SWITCH  — AT switches via TRRS jack (or breadboard stereo jack):
#               Tip → D5 (dot), Ring1 → D6 (dash), Sleeve → GND
#
# Wiring
#   STEMMA QT chain : Feather --[100mm]--> LPS33HW --[400mm]--> OLED
#   STEMMA Speaker  : Feather A0 → Audio in,  3V → VIN,  GND → GND
#   TRRS Breakout   : T → D5,  R1 → D6,  S → GND  (R2 unused)
#   Breadboard alt  : stereo jack TIP → D5,  RING → D6,  SLEEVE → GND
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
    import adafruit_displayio_ssd1306
    _OLED_AVAILABLE = True
except ImportError:
    _OLED_AVAILABLE = False
    print("WARNING: adafruit_displayio_ssd1306 not found — display disabled")

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

from morse_map import groups

# ── Configuration ─────────────────────────────────────────────────────────────

USE_SENSOR      = True          # False → use AT switches via TRRS / stereo jack

# Pressure thresholds (hPa delta from zeroed baseline).
# Raise these if you get false triggers; lower them if light sips are missed.
THRESH_SIP      = 5             # must sip this many hPa below baseline
THRESH_PUFF     = 5             # must puff this many hPa above baseline

# Timing (seconds)
ACCEPT_DELAY    = 0.2           # idle pause after last element before committing
LONG_PRESS      = 1.0           # hold duration that cycles the active group

# Pressure smoothing — average this many readings before thresholding.
# Increase to reduce bounce; decrease if fast elements are missed.
POINTS_TO_AVERAGE = 8

# Switch GPIO pins — TRRS Tip=dot, Ring1=dash; breadboard: jack Tip=dot, Ring=dash
DOT_PIN         = board.D5
DASH_PIN        = board.D6

# Audio
AUDIO_PIN       = board.A0      # connects to STEMMA Speaker audio input
BEEP_DOT_FREQ   = 1200          # Hz — dot (sip) sidetone  — higher pitch
BEEP_DASH_FREQ  =  800          # Hz — dash (puff) sidetone — lower pitch
CONFIRM_FREQ    = 1050          # Hz — action-executed blip
GROUP_FREQ      = 550           # Hz — group-change blip
BEEP_CONFIRM_S  = 0.06          # duration of action confirm blip (seconds)
BEEP_GROUP_S    = 0.14          # duration of group-change blip (seconds)

# Mouse speeds  (raw mmove values × speed × MOUSE_SPEED_FACTOR = actual pixels)
MOUSE_SPEED_NORMAL = 2
MOUSE_SPEED_SLOW   = 1
MOUSE_SPEED_FAST   = 3
MOUSE_SPEED_FACTOR = 2          # overall scale
MOUSE_REPEAT_DELAY = 0.040      # seconds between repeat ticks (40 ms)

# Display
DISPLAY_W           = 128
DISPLAY_H           = 64
DISPLAY_ROTATION    = 180   # degrees — 0 = USB on left, 180 = USB on right
                            # other valid values: 90, 270
                            # default 180: USB on right (matches STEMMA QT cable exit)

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

# Shared STEMMA QT I2C bus — LPS33HW (0x5C) and SSD1306 OLED (0x3C) share it.
i2c = board.STEMMA_I2C()

if USE_SENSOR and not _LPS_AVAILABLE:
    print("adafruit_lps35hw missing — switching to USE_SENSOR = False")
    USE_SENSOR = False

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

# ── OLED display setup ─────────────────────────────────────────────────────────

if _OLED_AVAILABLE:
    displayio.release_displays()
    _display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
    display = adafruit_displayio_ssd1306.SSD1306(_display_bus, width=DISPLAY_W, height=DISPLAY_H, rotation=DISPLAY_ROTATION)
else:
    display = None

# ── Audio setup ─────────────────────────────────────────────────────────────────

# Square-wave tone generator on AUDIO_PIN via pwmio. synthio / audiopwmio
# are not available on ESP32-S3, so use the simpler pwmio path uniformly.
# Frequency is switched per beep; 50% duty (0x8000) plays, 0 is silence.

if _AUDIO_AVAILABLE:
    _audio_out = pwmio.PWMOut(AUDIO_PIN, frequency=BEEP_DOT_FREQ,
                              duty_cycle=0, variable_frequency=True)

_beeping_morse  = False   # True while a DIT or DAH is held
_notify_end     = 0.0     # monotonic time when the timed blip should stop


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
    """Start sidetone when a press begins — higher pitch for dot, lower for dash."""
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

# Morse accumulator — binary word and bit count
# Bit encoding: 0 = DIT (dot), 1 = DAH (dash), MSB = first symbol
_pending_char = 0
_num_shifts   = 0

# State-machine bookkeeping
_last_state    = IDLE
_last_trans_at = 0.0    # time of most recent state change (used for ACCEPT_DELAY)
_press_start   = 0.0    # time the current DIT/DAH press began (for LONG_PRESS)

_armed_mods    = set()  # sticky modifier keycodes currently armed

# Mouse state
_mouse_speed     = MOUSE_SPEED_NORMAL
_drag_active     = False
_last_mouse_vec  = (0, 0, 0)   # last mmove already scaled (x, y, wheel)
_last_repeatable = None         # last keycode / combo / text to repeat
_mouse_repeating = False
_mouse_moved     = [0, 0, 0]   # accumulated pixels this repeat session
_mouse_start_t   = 0.0         # when current repeat session began
_last_repeat_tick = 0.0        # when last key-repeat fired

_last_action      = " "
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
    repeat / mslow / mfast / mreset
    """
    global active_group, _mouse_speed, _drag_active
    global _last_mouse_vec, _last_repeatable, _mouse_repeating, _armed_mods
    parts = cmd.split()
    verb  = parts[0]

    if verb == 'group':
        active_group     = int(parts[1])
        _last_repeatable = None     # reset repeat on group change

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

    elif verb == 'mdrag':
        btn = Mouse.LEFT_BUTTON if parts[1] == 'left' else Mouse.RIGHT_BUTTON
        if _drag_active:
            mouse.release(btn)
            _drag_active = False
        else:
            mouse.press(btn)
            _drag_active = True

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
    global _last_action, _last_repeatable, _last_mouse_vec
    if isinstance(action, tuple):
        _last_action     = "COMBO"
        _last_repeatable = action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  COMBO")
        _exec_combo(action)
        _beep_notify()
    elif isinstance(action, int):
        _last_action     = f"KEY {action}"
        _last_repeatable = action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  KEY {action}")
        _exec_keycode(action)
        _beep_notify()
    elif isinstance(action, str):
        if _is_command(action):
            _last_action = action[:20]
            print(f"{pattern}  {action}")
            _exec_command(action)
        else:
            _last_action     = f'"{action[:16]}"'
            _last_repeatable = action
            _last_mouse_vec  = (0, 0, 0)
            print(f"{pattern}  \"{action}\"")
            _exec_text(action)
            _beep_notify()

# ── Group cycling via long-press ───────────────────────────────────────────────

_GROUP_NAMES  = ("Base", "Keyboard", "Mouse", "Macro", "Scanning",
                 "Media", "Group 6", "Group 7", "Group 8", "Group 9")

def cycle_group(direction):
    """direction: +1 = forward, -1 = backward through groups 1–9 (group 0 skipped).
    The 8-symbol Group 0 toggle codes are the direct-jump fast path to any group."""
    global active_group, _last_action, _last_repeatable
    active_group     = (active_group - 1 + direction) % 9 + 1
    _last_repeatable = None
    _last_action     = f"-> {_GROUP_NAMES[active_group]}"
    print(f"GROUP -> {active_group} ({_GROUP_NAMES[active_group]})")
    _beep_notify(duration=BEEP_GROUP_S, freq=GROUP_FREQ)

# ── Display ────────────────────────────────────────────────────────────────────
#
# Layout on the 128 × 64 px OLED  (terminalio.FONT scale=1, ~14 px per row):
#   y= 1   [ group name ]
#   y=15   morse buffer          (dots and dashes in progress)
#   y=29   last executed action
#   y=43   armed modifiers / speed / drag / repeat
#   y=57   pressure bar          (6 px bitmap, sensor mode only)

def _make_label(root, text, y):
    lbl = label.Label(
        terminalio.FONT, text=text, color=0xFFFFFF, scale=1,
        anchor_point=(0.0, 0.0),
        anchored_position=(1, y),
    )
    root.append(lbl)
    return lbl


def _build_display():
    if display is None:
        return None, None, None, None, None, None

    root = displayio.Group()

    bg_bmp = displayio.Bitmap(DISPLAY_W, DISPLAY_H, 1)
    bg_pal = displayio.Palette(1)
    bg_pal[0] = 0x000000
    root.append(displayio.TileGrid(bg_bmp, pixel_shader=bg_pal))

    lbl_group  = _make_label(root, "[Keyboard]",  1)
    lbl_buf    = _make_label(root, " ",           15)
    lbl_action = _make_label(root, " ",           29)
    lbl_mods   = _make_label(root, " ",           43)

    # Pressure bar: 128 wide × 6 tall, 2-colour (index 0 = off, index 1 = on)
    bar_bmp = displayio.Bitmap(DISPLAY_W, 6, 2)
    bar_pal = displayio.Palette(2)
    bar_pal[0] = 0x000000
    bar_pal[1] = 0xFFFFFF
    root.append(displayio.TileGrid(bar_bmp, pixel_shader=bar_pal, x=0, y=57))

    display.root_group = root
    return lbl_group, lbl_buf, lbl_action, lbl_mods, bar_bmp, bar_pal


_lbl_group, _lbl_buf, _lbl_action, _lbl_mods, _bar_bmp, _bar_pal = _build_display()

_MOD_NAMES = {
    Keycode.LEFT_CONTROL:  "Ctrl",  Keycode.RIGHT_CONTROL: "RCtrl",
    Keycode.LEFT_SHIFT:    "Shift", Keycode.RIGHT_SHIFT:   "RShft",
    Keycode.LEFT_ALT:      "Alt",   Keycode.RIGHT_ALT:     "RAlt",
    Keycode.LEFT_GUI:      "GUI",   Keycode.RIGHT_GUI:     "RGUI",
}

_BAR_MAX_PRESSURE = THRESH_SIP * 3   # pressure that fills the bar completely
_prev_bar_w = 0


def _update_bar(pressure):
    """Redraw only the changed columns of the pressure bar bitmap."""
    global _prev_bar_w
    if _bar_bmp is None or not USE_SENSOR:
        return
    new_w = int(min(abs(pressure) / _BAR_MAX_PRESSURE, 1.0) * DISPLAY_W)
    if new_w == _prev_bar_w:
        return
    lo = min(new_w, _prev_bar_w)
    hi = max(new_w, _prev_bar_w)
    fill_val = 1 if new_w > _prev_bar_w else 0
    for x in range(lo, hi):
        for row in range(6):
            _bar_bmp[x, row] = fill_val
    _prev_bar_w = new_w


def _update_display(pressure=0.0):
    if display is None:
        return
    _lbl_group.text  = f"[{_GROUP_NAMES[active_group]}]"
    _lbl_buf.text    = _pending_to_str(_num_shifts, _pending_char)
    _lbl_action.text = _last_action[:21] if _last_action else " "
    mods_text = " ".join(_MOD_NAMES.get(m, "?") for m in sorted(_armed_mods))
    if mods_text:
        _lbl_mods.text = mods_text[:21]
    elif _mouse_speed == MOUSE_SPEED_SLOW:
        _lbl_mods.text = "SLOW"
    elif _mouse_speed == MOUSE_SPEED_FAST:
        _lbl_mods.text = "FAST"
    elif _mouse_repeating:
        _lbl_mods.text = "RPT"
    elif _drag_active:
        _lbl_mods.text = "DRAG"
    else:
        _lbl_mods.text = " "
    _update_bar(pressure)

# ── Main loop ──────────────────────────────────────────────────────────────────
#
# State machine mirrors v1:
#   • Read sensor → DIT / DAH / IDLE
#   • On transition DIT/DAH → IDLE: shift bit into accumulator (or long-press)
#   • After ACCEPT_DELAY of idle with bits pending: commit and look up

_last_display = 0.0
_DISPLAY_RATE = 0.1     # cap display refresh at 10 Hz

while True:
    now = time.monotonic()

    # ── Timed audio release ──────────────────────────────────────────────────
    _audio_tick()

    # ── Read sensor / switches ───────────────────────────────────────────────
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

    # ── State machine ────────────────────────────────────────────────────────
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
