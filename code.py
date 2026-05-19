# code.py — Sip-and-puff / two-switch Morse HID device
#
# Hardware
#   Adafruit ESP32-S3 Reverse TFT Feather  https://www.adafruit.com/product/5691
#   Adafruit LPS33HW pressure sensor       https://www.adafruit.com/product/4414
#
# Input modes (select with USE_SENSOR below)
#   SENSOR  — LPS33HW via STEMMA QT: sip lowers pressure (dot), puff raises it (dash)
#   SWITCH  — two digital switches: DOT_PIN press = dot, DASH_PIN press = dash
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

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse

from morse_map import groups

# ── Configuration ─────────────────────────────────────────────────────────────

USE_SENSOR      = True          # False → use two digital switches instead

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

# Switch GPIO pins (only used when USE_SENSOR = False)
DOT_PIN         = board.D5
DASH_PIN        = board.D6

# Mouse speeds  (raw mmove values × speed × MOUSE_SPEED_FACTOR = actual pixels)
MOUSE_SPEED_NORMAL = 2
MOUSE_SPEED_SLOW   = 1
MOUSE_SPEED_FAST   = 3
MOUSE_SPEED_FACTOR = 2          # overall scale (matches AirTalker feel)
MOUSE_REPEAT_DELAY = 0.040      # seconds between repeat ticks (40 ms)

# Display
DISPLAY_ROTATION   = 0          # degrees — 0 = USB on left, 180 = USB on right
                                # other valid values: 90, 270

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

# ── ESP-NOW wireless display ───────────────────────────────────────────────────
# Broadcasts TFT state to a QT Py ESP32-C3 + SSD1306 OLED running receiver.py.
# Entirely optional — if the espnow / wifi modules are absent nothing changes.

_ESPNOW_ENABLED = False
if _ESPNOW_IMPORTABLE:
    try:
        _wifi_mod.radio.enabled = True
        _espnow_dev = _espnow_mod.ESPNow()
        _espnow_dev.peers.append(_espnow_mod.Peer(mac=b'\xff\xff\xff\xff\xff\xff'))
        _ESPNOW_ENABLED = True
        print("ESP-NOW: wireless display active (broadcast)")
    except Exception as _ex:
        print(f"ESP-NOW: init failed ({_ex})")

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
    elif isinstance(action, int):
        _last_action     = f"KEY {action}"
        _last_repeatable = action
        _last_mouse_vec  = (0, 0, 0)
        print(f"{pattern}  KEY {action}")
        _exec_keycode(action)
    elif isinstance(action, str):
        if _is_command(action):
            _last_action = action[:20]
            print(f"{pattern}  {action}")
            _exec_command(action)
            # mmove updates _last_mouse_vec and clears _last_repeatable (see below)
            # other commands leave repeat state unchanged
        else:
            _last_action     = f'"{action[:16]}"'
            _last_repeatable = action
            _last_mouse_vec  = (0, 0, 0)
            print(f"{pattern}  \"{action}\"")
            _exec_text(action)

# ── Group cycling via long-press ───────────────────────────────────────────────

def cycle_group(direction):
    """direction: +1 = forward, -1 = backward through groups 1–3 (group 0 skipped)."""
    global active_group, _last_action, _last_repeatable
    active_group     = (active_group - 1 + direction) % 3 + 1
    _last_repeatable = None     # reset repeat on group change — must mmove first
    _last_action     = f"-> group {active_group}"
    print(f"GROUP -> {active_group} ({_GROUP_NAMES[active_group]})")

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

    # ── State machine ───────────────────────────────────────────────────────
    if new_state != _last_state:

        if _mouse_repeating:
            # Any new input cancels a mouse repeat
            _stop_mouse_repeat()
            new_state = IDLE

        elif _last_state == IDLE:
            # IDLE → DIT/DAH: record when the press started
            _press_start = now

        elif new_state == IDLE:
            # DIT/DAH → IDLE: commit the element (or trigger long-press)
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
