#!/usr/bin/env python3
"""
aeromorse_validator.py

A SAFETY check for the AeroMorse device files — answers one question in plain
language:

    "Will these files load on the device, or will they lock me out?"

It checks every required file the device needs to boot and run:

    boot.py       - BOM + syntax  (runs real hardware setup, so not imported)
    code.py       - BOM + syntax  (same)
    config.py     - BOM + syntax + imports cleanly + settings sanity
    morse_map.py  - BOM + syntax + imports cleanly + groups build + secrets
    macro_secrets.txt (optional) - parses, and every _secret() key resolves

For config.py and morse_map.py it reproduces exactly what the device does when
it powers up and imports them. For all files it also catches the things
CircuitPython is fussy about that desktop Python silently ignores - a UTF-8 BOM
being the big one.

PRIVACY: this program never prints the CONTENTS of any secret. It reports key
NAMES and counts only — never a password, phone number, or address.

Exit code 0 = PASS (safe to use).  Exit code 1 = FAIL (do not rely on it yet).

Drop this next to the file(s) you edited and run it. When built as
aeromorse_validator.exe, just double-click it in the same folder. An optional
folder/file argument (e.g.  aeromorse_validator.exe F:\) checks that location.
"""

import sys, os, re, types, traceback, io
from datetime import date

# Never write .pyc files. Without this, importing morse_map.py / config.py
# straight off the CIRCUITPY drive would leave a __pycache__ folder on it.
# CircuitPython ignores __pycache__, but we keep the drive clean anyway.
sys.dont_write_bytecode = True

# ── Colour output (green PASS / red FAIL / yellow WARN / grey SKIP) ──────────
# Enabled only when writing to a real terminal, so redirected or captured
# output stays plain text with no escape-code clutter.
def _enable_ansi():
    if os.name != 'nt':
        return True   # POSIX terminals understand ANSI already
    try:
        import ctypes
        k = ctypes.windll.kernel32
        h = k.GetStdHandle(-11)                       # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if not k.GetConsoleMode(h, ctypes.byref(mode)):
            return False
        # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        return bool(k.SetConsoleMode(h, mode.value | 0x0004))
    except Exception:
        return False

try:
    _USE_COLOR = sys.stdout.isatty() and _enable_ansi()
except Exception:
    _USE_COLOR = False

_ANSI = {'PASS': '\033[1;32m', 'FAIL': '\033[1;31m',
         'WARN': '\033[1;33m', 'SKIP': '\033[90m'}
_RESET = '\033[0m'

def _c(text, key):
    """Wrap text in the colour for a status keyword, if colour is on."""
    if _USE_COLOR and key in _ANSI:
        return _ANSI[key] + text + _RESET
    return text

# ── Locate the files (next to this script / .exe) ────────────────────────────
# An optional command-line argument says WHERE to look:
#   - a folder (e.g.  F:\  the CIRCUITPY drive)  -> checks  <folder>\morse_map.py
#   - a direct path to a morse_map.py file       -> checks that file
# With no argument, it checks the morse_map.py sitting next to this program
# (the .exe when frozen, or this script when run with Python).
_arg = sys.argv[1] if len(sys.argv) > 1 else None
if _arg:
    _arg = os.path.abspath(_arg)
    _BASE = _arg if os.path.isdir(_arg) else (os.path.dirname(_arg) or '.')
elif getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

# All the files the device needs in order to boot and run. macro_secrets.txt
# is optional; the rest are the "required files".
MORSE_MAP_PATH = os.path.join(_BASE, 'morse_map.py')
CONFIG_PATH    = os.path.join(_BASE, 'config.py')
BOOT_PATH      = os.path.join(_BASE, 'boot.py')
CODE_PATH      = os.path.join(_BASE, 'code.py')
SECRETS_PATH   = os.path.join(_BASE, 'macro_secrets.txt')

# Files whose presence we probe for the "nothing to check" guard.
_ALL_PATHS = (MORSE_MAP_PATH, CONFIG_PATH, BOOT_PATH, CODE_PATH)

BOM = b'\xef\xbb\xbf'

# Track any Keycode / ConsumerControlCode names the file uses that aren't in
# our known list, so we can warn (not fail) about possible typos.
_unknown_kc  = set()
_unknown_ccc = set()

# ── Result plumbing ──────────────────────────────────────────────────────────
# status is 'PASS', 'FAIL' (lockout — flips the overall result), or 'WARN'
# (device still runs; worth reviewing).
_checks   = []   # (label, status, detail)
_warnings = []

def check(label, ok, detail=''):
    _checks.append((label, 'PASS' if ok else 'FAIL', detail))
    return ok

def check_warn(label, ok, detail=''):
    """A non-fatal check: a non-PASS shows as WARN and does NOT fail the run."""
    _checks.append((label, 'PASS' if ok else 'WARN', detail))
    return True

def section(title):
    """A visual header row in the report (not a pass/fail check)."""
    _checks.append(('__section__', title, ''))

def warn(msg):
    _warnings.append(msg)

def _wrap(text, width=64, indent='      '):
    """Word-wrap a long warning so it stays readable in a console window."""
    words, lines, cur = text.split(), [], ''
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + ' ' + w).strip()
    if cur:
        lines.append(cur)
    return ('\n' + indent).join(lines)

# ── adafruit_hid stub so morse_map imports like it does on the device ────────
# Known-good Keycode names (the standard adafruit_hid set + the short aliases
# the AeroMorse code uses). An unknown name is recorded and warned about, not
# failed — the file may still be fine on your particular CircuitPython bundle.
_KC_NAMES = set((
    "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z "
    "ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE "
    "ENTER RETURN ESCAPE BACKSPACE TAB SPACE SPACEBAR "
    "MINUS EQUALS LEFT_BRACKET RIGHT_BRACKET BACKSLASH POUND SEMICOLON QUOTE "
    "GRAVE_ACCENT COMMA PERIOD FORWARD_SLASH CAPS_LOCK "
    "F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 "
    "F13 F14 F15 F16 F17 F18 F19 F20 F21 F22 F23 F24 "
    "PRINT_SCREEN SCROLL_LOCK PAUSE INSERT HOME PAGE_UP DELETE END PAGE_DOWN "
    "RIGHT_ARROW LEFT_ARROW DOWN_ARROW UP_ARROW "
    "KEYPAD_NUMLOCK KEYPAD_FORWARD_SLASH KEYPAD_ASTERISK KEYPAD_MINUS "
    "KEYPAD_PLUS KEYPAD_ENTER KEYPAD_PERIOD KEYPAD_EQUALS KEYPAD_BACKSLASH "
    "KEYPAD_ONE KEYPAD_TWO KEYPAD_THREE KEYPAD_FOUR KEYPAD_FIVE KEYPAD_SIX "
    "KEYPAD_SEVEN KEYPAD_EIGHT KEYPAD_NINE KEYPAD_ZERO "
    "APPLICATION POWER "
    "LEFT_CONTROL LEFT_SHIFT LEFT_ALT LEFT_GUI "
    "RIGHT_CONTROL RIGHT_SHIFT RIGHT_ALT RIGHT_GUI "
    "CONTROL SHIFT ALT GUI COMMAND OPTION WINDOWS"
).split())

class _KCMeta(type):
    def __getattr__(cls, name):
        if not name.startswith('__') and name not in _KC_NAMES:
            _unknown_kc.add(name)
        return 'Keycode.%s' % name

class _Keycode(metaclass=_KCMeta):
    pass

# ConsumerControlCode: permissive. The AeroMorse code reaches these through a
# guarded getattr(..., fallback) for the AL_* launchers, so a name your bundle
# lacks won't crash the device — we mirror that by never raising here.
_CCC_NAMES = set((
    "PLAY_PAUSE MUTE VOLUME_INCREMENT VOLUME_DECREMENT SCAN_NEXT_TRACK "
    "SCAN_PREVIOUS_TRACK STOP FAST_FORWARD REWIND BRIGHTNESS_INCREMENT "
    "BRIGHTNESS_DECREMENT EJECT RECORD "
    "AL_CALCULATOR AL_LOCAL_MACHINE_BROWSER AL_INTERNET_BROWSER "
    "AL_EMAIL_READER AL_CONSUMER_CONTROL_CONFIGURATION SLEEP POWER"
).split())

class _CCCMeta(type):
    def __getattr__(cls, name):
        if not name.startswith('__') and name not in _CCC_NAMES:
            _unknown_ccc.add(name)
        return 'ConsumerControlCode.%s' % name

class _ConsumerControlCode(metaclass=_CCCMeta):
    pass

def _install_hid_stub():
    hid  = types.ModuleType('adafruit_hid')
    kc   = types.ModuleType('adafruit_hid.keycode')
    ccc  = types.ModuleType('adafruit_hid.consumer_control_code')
    kc.Keycode = _Keycode
    ccc.ConsumerControlCode = _ConsumerControlCode
    hid.keycode = kc
    hid.consumer_control_code = ccc
    sys.modules['adafruit_hid'] = hid
    sys.modules['adafruit_hid.keycode'] = kc
    sys.modules['adafruit_hid.consumer_control_code'] = ccc


# ── Check 1: file present + no BOM ───────────────────────────────────────────
def check_encoding():
    if not os.path.exists(MORSE_MAP_PATH):
        return check('morse_map.py found', False,
                     "No morse_map.py in this folder:\n      %s\n"
                     "      Put this validator in the same folder as morse_map.py."
                     % _BASE)
    raw = open(MORSE_MAP_PATH, 'rb').read()
    if raw.startswith(BOM):
        return check('morse_map.py: no UTF-8 BOM', False,
                     "morse_map.py starts with a UTF-8 BOM (3 hidden bytes).\n"
                     "      Your PC ignores it, but the DEVICE will refuse to load the\n"
                     "      file - this is the classic 'lost all access' cause.\n"
                     "      FIX: in Notepad++, Encoding menu -> 'UTF-8'  (NOT 'UTF-8-BOM'),\n"
                     "           then save.")
    # A stray BOM mid-file (e.g. pasted text) trips CircuitPython too.
    if BOM in raw:
        warn("morse_map.py contains a BOM sequence partway through the file; "
             "if the device won't load, that's the likely cause.")
    return check('morse_map.py: no UTF-8 BOM', True, '')


# ── Check 2: Python syntax ───────────────────────────────────────────────────
def check_syntax():
    src = open(MORSE_MAP_PATH, 'r', encoding='utf-8-sig').read()  # tolerate BOM here; Check 1 already flagged it
    try:
        compile(src, 'morse_map.py', 'exec')
    except SyntaxError as e:
        line = e.lineno or '?'
        text = (e.text or '').rstrip()
        return check('morse_map.py: Python syntax', False,
                     "Syntax error on line %s:\n"
                     "        %s\n"
                     "      %s\n"
                     "      FIX: correct that line and save. (A stray comma, a missing\n"
                     "           quote, or a mismatched bracket is the usual cause.)"
                     % (line, text, e.msg))
    return check('morse_map.py: Python syntax', True, '')


# ── Check 3 + 4: imports and builds its groups (what the device does) ────────
def check_import():
    _install_hid_stub()
    for mod in ('morse_map',):
        sys.modules.pop(mod, None)
    sys.path.insert(0, _BASE)
    cwd = os.getcwd()
    os.chdir(_BASE)  # so morse_map's secrets loader finds macro_secrets.txt like the device (CWD = drive root)
    try:
        import morse_map as m
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        where = ''
        for fr in reversed(tb):
            if os.path.basename(fr.filename) == 'morse_map.py':
                where = " (near line %s: %s)" % (fr.lineno, (fr.line or '').strip())
                break
        os.chdir(cwd)
        check('morse_map.py: loads on the device', False,
              "morse_map.py raised %s while loading%s:\n"
              "      %s\n"
              "      The device would fail here and you'd lose access.\n"
              "      FIX: correct that line and re-run this check."
              % (type(e).__name__, where, e))
        return None
    os.chdir(cwd)
    check('morse_map.py: loads on the device', True, '')

    # Groups build + are shaped right
    try:
        groups = m.groups
        assert isinstance(groups, dict) and groups, "groups is missing or empty"
        n_pat = 0
        for gnum, g in groups.items():
            assert isinstance(g, dict), "group %r is not a dict" % gnum
            for length, d in g.items():
                assert isinstance(d, dict), "group %r length %r is not a dict" % (gnum, length)
                n_pat += len(d)
        check('morse_map.py: groups build', True, '%d groups, %d patterns total' % (len(groups), n_pat))
    except Exception as e:
        check('morse_map.py: groups build', False,
              "The groups table didn't build cleanly: %s" % e)
        return None
    return m


# ── Check 5: secrets file + _secret() resolution (names only, never values) ──
def _secret_keys_used():
    """All keys referenced by _secret('key', ...) in morse_map.py — names only."""
    src = open(MORSE_MAP_PATH, 'r', encoding='utf-8-sig').read()
    return re.findall(r"_secret\(\s*['\"]([^'\"]+)['\"]", src)

def check_secrets(m):
    used = _secret_keys_used()
    have_file = os.path.exists(SECRETS_PATH)

    # Report malformed lines in the secrets file (the loader skips them).
    bad_lines = 0
    if have_file:
        raw = open(SECRETS_PATH, 'rb').read()
        if raw.startswith(BOM):
            warn("macro_secrets.txt starts with a UTF-8 BOM. The device tolerates it, "
                 "but keep Notepad++ on 'UTF-8' to be safe.")
        for i, line in enumerate(io.StringIO(raw.decode('utf-8-sig', 'replace')), 1):
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            if '=' not in s:
                bad_lines += 1
                warn("macro_secrets.txt line %d has no '=' and will be ignored "
                     "(each entry must be  key=value)." % i)

    # What actually loaded (names only — SECRETS values are never printed).
    loaded = getattr(m, 'SECRETS', {}) or {}
    loaded_names = sorted(loaded.keys())

    if not used:
        # No _secret() patterns at all - nothing to resolve.
        detail = 'no _secret() patterns in morse_map.py'
        if have_file:
            detail += '; macro_secrets.txt has %d key(s)' % len(loaded_names)
        return check_warn('morse_map.py: secrets resolve', True, detail)

    if not have_file:
        missing = sorted(set(used))
        warn("morse_map.py uses %d _secret() pattern(s) but there is NO "
             "macro_secrets.txt in this folder, so each will type its PLACEHOLDER "
             "text, not the real value. Keys needing values: %s. "
             "(This does not crash the device.) FIX: create macro_secrets.txt with "
             "lines like  %s=your value"
             % (len(missing), ', '.join(missing), missing[0]))
        return check_warn('morse_map.py: secrets resolve', False,
                          '%d _secret() key(s) used, no macro_secrets.txt (placeholders will type)'
                          % len(missing))

    unresolved = sorted(set(k for k in used if k not in loaded))
    if unresolved:
        # Non-fatal for the device (it types the placeholder), but the user
        # almost certainly wants these filled in - surface loudly.
        warn("These _secret() keys are used in morse_map.py but are NOT in "
             "macro_secrets.txt, so they will type their placeholder text: %s. "
             "(This does not crash the device.) FIX: add each to macro_secrets.txt "
             "as  key=value, and check the spelling matches on both sides."
             % ', '.join(unresolved))
        return check_warn('morse_map.py: secrets resolve', False,
                          '%d of %d _secret() key(s) not in macro_secrets.txt'
                          % (len(unresolved), len(set(used))))

    return check_warn('morse_map.py: secrets resolve', True,
                      '%d _secret() pattern(s), all resolve; macro_secrets.txt has %d key(s)'
                      % (len(set(used)), len(loaded_names)))


# ── Non-fatal warnings: duplicates + Group-0 conflicts ───────────────────────
def collect_warnings(m):
    # Duplicate assignments (source scan)
    pat = re.compile(r'^(g\d)\[(\d+)\]\[(0b[01]+|\d+)\]')
    seen = {}
    for lineno, line in enumerate(open(MORSE_MAP_PATH, encoding='utf-8-sig'), 1):
        mm = pat.match(line.strip())
        if not mm:
            continue
        key = (mm.group(1), int(mm.group(2)), int(mm.group(3), 0))
        if key in seen:
            warn("%s[%d][%s] is assigned twice (lines %d and %d) - the second wins."
                 % (mm.group(1), key[1], mm.group(3), seen[key], lineno))
        else:
            seen[key] = lineno

    # Group-0 conflicts: a pattern in g1..g9 that also exists in g0 can never
    # be reached from that group, because g0 (always-on) intercepts it first.
    try:
        g0 = {(L, c) for L, d in m.groups[0].items() for c in d}
        for gnum, g in m.groups.items():
            if gnum == 0:
                continue
            for L, d in g.items():
                for c in d:
                    if (L, c) in g0:
                        bstr = '0b' + format(c, '0%db' % L)
                        warn("g%d pattern %s is shadowed by a Group-0 code - it will "
                             "trigger the Group-0 action, not this one." % (gnum, bstr))
    except Exception:
        pass


# ── config.py checks ─────────────────────────────────────────────────────────
# code.py does  `from config import *`, so a config.py that won't import — or
# is missing a setting code.py relies on — can stop the board at boot. These
# checks mirror that: no BOM, valid syntax, imports with `board` stubbed, and
# a light sanity pass on well-known settings.

# The settings the standard build ships with (config.py v1.0). Used only to
# WARN if one is absent — not every one is required, so this never hard-fails.
_KNOWN_CONFIG = set((
    "USE_SENSOR THRESH_SIP THRESH_PUFF DEBOUNCE_SAMPLES POINTS_TO_AVERAGE "
    "SENSOR_FILTER_ENABLED SENSOR_FILTER_HEAVY BASELINE_DRIFT_S DOT_PIN DASH_PIN "
    "SWITCH_MODE ONE_SWITCH_INPUT ONE_SWITCH_DOT_MS THIRD_SWITCH_GESTURE "
    "STRONG_SIP_ACTION STRONG_PUFF_ACTION THRESH_SIP_STRONG THRESH_PUFF_STRONG "
    "ACCEPT_DELAY LONG_PRESS CODE_REPEAT DOT_REPEAT_MS DASH_REPEAT_MS "
    "CODE_REPEAT_MAX LONG_PRESS_CYCLES_GROUP AUDIO_PIN BEEP_DOT_FREQ BEEP_DASH_FREQ "
    "CONFIRM_FREQ GROUP_FREQ BEEP_CONFIRM_S BEEP_GROUP_S MOUSE_SPEED_NORMAL "
    "MOUSE_SPEED_SLOW MOUSE_SPEED_FAST MOUSE_SPEED_FACTOR MOUSE_REPEAT_DELAY "
    "MOUSE_CLICK_MOD_DELAY MOUSE_CLICK_KEEPS_MODS MOUSE_CLICK_HOLD MOUSE_CLICK_GAP "
    "NO_REPEAT_KEYS DISPLAY_ROTATION USE_WIRELESS_DISPLAY ESPNOW_CHANNEL"
).split())

def _install_board_stub():
    board = types.ModuleType('board')
    # Predefine the pins config.py names, and answer any other board.X too.
    for _p in ('D5', 'D6', 'A0'):
        setattr(board, _p, 'board.%s' % _p)
    board.__getattr__ = lambda name: 'board.%s' % name  # PEP 562 fallback
    sys.modules['board'] = board

def check_config_encoding():
    raw = open(CONFIG_PATH, 'rb').read()
    if raw.startswith(BOM):
        return check('config.py: no UTF-8 BOM', False,
                     "config.py starts with a UTF-8 BOM (3 hidden bytes).\n"
                     "      The DEVICE will refuse to load it and stop at boot.\n"
                     "      FIX: Notepad++ -> Encoding -> 'UTF-8' (NOT 'UTF-8-BOM'), save.")
    if BOM in raw:
        warn("config.py contains a BOM sequence partway through the file; "
             "if the device won't boot, that's the likely cause.")
    return check('config.py: no UTF-8 BOM', True, '')

def check_config_syntax():
    src = open(CONFIG_PATH, 'r', encoding='utf-8-sig').read()
    try:
        compile(src, 'config.py', 'exec')
    except SyntaxError as e:
        return check('config.py: Python syntax', False,
                     "Syntax error on line %s:\n        %s\n      %s\n"
                     "      FIX: correct that line and save."
                     % (e.lineno or '?', (e.text or '').rstrip(), e.msg))
    return check('config.py: Python syntax', True, '')

def check_config_import():
    _install_board_stub()
    sys.modules.pop('config', None)
    sys.path.insert(0, _BASE)
    cwd = os.getcwd()
    os.chdir(_BASE)
    try:
        import config as c
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])
        where = ''
        for fr in reversed(tb):
            if os.path.basename(fr.filename) == 'config.py':
                where = " (near line %s: %s)" % (fr.lineno, (fr.line or '').strip())
                break
        os.chdir(cwd)
        check('config.py: loads on the device', False,
              "config.py raised %s while loading%s:\n      %s\n"
              "      The device would fail here at boot.\n"
              "      FIX: correct that line and re-run this check."
              % (type(e).__name__, where, e))
        return None
    os.chdir(cwd)
    check('config.py: loads on the device', True, '')
    return c

def check_config_settings(c):
    """Light sanity pass. Anything odd is a WARNING, never a hard fail — a bad
    value usually misbehaves rather than bricking, and we don't want to block a
    file that actually boots."""
    present = set(n for n in dir(c) if not n.startswith('_'))

    # Missing standard settings (code.py may reference them -> boot NameError).
    missing = sorted(_KNOWN_CONFIG - present)
    if missing:
        warn("config.py is missing setting(s) the standard build defines: %s. "
             "If code.py uses one, the board can fail at boot with a NameError. "
             "FIX: add them back (copy from a known-good config.py) unless you "
             "are sure your code.py doesn't need them." % ', '.join(missing))

    def val(name):
        return getattr(c, name, None)

    def want(name, ok, note):
        if name in present and not ok(val(name)):
            warn("config.py: %s = %r %s" % (name, val(name), note))

    is_num  = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
    is_bool = lambda v: isinstance(v, bool)

    for n in ("USE_SENSOR SENSOR_FILTER_ENABLED SENSOR_FILTER_HEAVY CODE_REPEAT "
              "LONG_PRESS_CYCLES_GROUP MOUSE_CLICK_KEEPS_MODS USE_WIRELESS_DISPLAY").split():
        want(n, is_bool, "should be True or False.")

    for n in ("THRESH_SIP THRESH_PUFF THRESH_SIP_STRONG THRESH_PUFF_STRONG "
              "DEBOUNCE_SAMPLES POINTS_TO_AVERAGE BASELINE_DRIFT_S ONE_SWITCH_DOT_MS "
              "DOT_REPEAT_MS DASH_REPEAT_MS CODE_REPEAT_MAX MOUSE_SPEED_NORMAL "
              "MOUSE_SPEED_SLOW MOUSE_SPEED_FAST MOUSE_SPEED_FACTOR ACCEPT_DELAY "
              "LONG_PRESS MOUSE_REPEAT_DELAY MOUSE_CLICK_MOD_DELAY MOUSE_CLICK_HOLD "
              "MOUSE_CLICK_GAP BEEP_DOT_FREQ BEEP_DASH_FREQ CONFIRM_FREQ GROUP_FREQ "
              "BEEP_CONFIRM_S BEEP_GROUP_S ESPNOW_CHANNEL DISPLAY_ROTATION").split():
        want(n, is_num, "should be a number.")

    want('SWITCH_MODE',          lambda v: v in (1, 2, 3), "should be 1, 2, or 3.")
    want('ONE_SWITCH_INPUT',     lambda v: v in ('dot', 'dash'), "should be \"dot\" or \"dash\".")
    want('THIRD_SWITCH_GESTURE', lambda v: v in ('long_dash', 'long_dot'),
         "should be \"long_dash\" or \"long_dot\".")
    want('DISPLAY_ROTATION',     lambda v: v in (0, 90, 180, 270), "should be 0, 90, 180, or 270.")
    want('ESPNOW_CHANNEL',       lambda v: is_num(v) and 1 <= v <= 13, "should be 1-13.")
    want('NO_REPEAT_KEYS',       lambda v: isinstance(v, (tuple, list)),
         "should be a tuple of key names, e.g. (\"PAGE_UP\", \"PAGE_DOWN\").")

    check_warn('config.py: settings sanity',
               not missing, 'checked %d known settings' % len(_KNOWN_CONFIG & present))

def run_config_checks():
    section('config.py')
    if not os.path.exists(CONFIG_PATH):
        _checks.append(('config.py present', 'SKIP',
                        'not in this folder - skipped (nothing to check)'))
        return
    if not check_config_encoding():
        return
    if not check_config_syntax():
        return
    c = check_config_import()
    if c is None:
        return
    check_config_settings(c)


# ── boot.py / code.py checks (BOM + syntax only) ─────────────────────────────
# These run real hardware setup (board, displayio, usb_hid, ...) that can't be
# reproduced on a PC, so we do NOT import them. But the two things that brick
# the boot - a UTF-8 BOM and a syntax error - are fully checkable here. You
# normally never edit these, but they're required files, so we check them.
def run_pyfile_checks(path, name):
    section(name)
    if not os.path.exists(path):
        _checks.append(('%s present' % name, 'SKIP',
                        'not in this folder - skipped (nothing to check)'))
        return
    raw = open(path, 'rb').read()
    if raw.startswith(BOM):
        check('%s: no UTF-8 BOM' % name, False,
              "%s starts with a UTF-8 BOM (3 hidden bytes).\n"
              "      The DEVICE will refuse to load it and stop at boot.\n"
              "      FIX: Notepad++ -> Encoding -> 'UTF-8' (NOT 'UTF-8-BOM'), save."
              % name)
        return
    if BOM in raw:
        warn("%s contains a BOM sequence partway through the file; if the device "
             "won't boot, that's the likely cause." % name)
    check('%s: no UTF-8 BOM' % name, True, '')

    src = open(path, 'r', encoding='utf-8-sig').read()
    try:
        compile(src, name, 'exec')
    except SyntaxError as e:
        check('%s: Python syntax' % name, False,
              "Syntax error on line %s:\n        %s\n      %s\n"
              "      FIX: correct that line and save."
              % (e.lineno or '?', (e.text or '').rstrip(), e.msg))
        return
    check('%s: Python syntax' % name, True, '')


# ── Single-instance guard ────────────────────────────────────────────────────
# Double-clicking the icon a few times used to open several windows at once.
# A named mutex lets only the first window run; extra clicks see it's already
# held and bow out. Windows frees the mutex automatically when the first window
# closes, so nothing to clean up.
_INSTANCE_MUTEX = None   # kept alive for the life of the process

def _already_running():
    if os.name != 'nt':
        return False
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.CreateMutexW.restype  = ctypes.c_void_p
        k.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_wchar_p]
        global _INSTANCE_MUTEX
        _INSTANCE_MUTEX = k.CreateMutexW(None, 0, "AeroMorseValidator_SingleInstance")
        ERROR_ALREADY_EXISTS = 183
        return k.GetLastError() == ERROR_ALREADY_EXISTS
    except Exception:
        return False   # if the check itself fails, don't block the user


# ── Runner ───────────────────────────────────────────────────────────────────
def run_morse_map_checks():
    section('morse_map.py')
    if not os.path.exists(MORSE_MAP_PATH):
        _checks.append(('morse_map.py present', 'SKIP',
                        'not in this folder - skipped (nothing to check)'))
        return
    # Stop this section at the first hard failure (later checks just cascade).
    if not check_encoding():
        return
    if not check_syntax():
        return
    m = check_import()
    if m is None:
        return
    check_secrets(m)
    collect_warnings(m)


def main():
    # If a window is already open, don't run a second time - just say so.
    if _already_running():
        print()
        print('  AeroMorse validator is already open in another window.')
        print('  Use that window (press Enter there to close it) before')
        print('  running it again.')
        if getattr(sys, 'frozen', False):
            try:
                input('\n  Press Enter to close this extra window...')
            except EOFError:
                pass
        sys.exit(0)

    print('=' * 68)
    print('  AeroMorse  -  Device File Safety Validator')
    print('  Checks the required files before you trust them on the device:')
    print('  boot.py, code.py, config.py, morse_map.py (+ macro_secrets.txt)')
    print('  %s' % date.today())
    print('  Folder: %s' % _BASE)
    print('=' * 68)

    # None of the required files present usually means the wrong folder.
    if not any(os.path.exists(p) for p in _ALL_PATHS):
        check('AeroMorse files found', False,
              "None of boot.py, code.py, config.py, morse_map.py are in this folder:\n"
              "      %s\n"
              "      Put this validator in the folder with the file(s) you edited."
              % _BASE)
        return finish()

    run_pyfile_checks(BOOT_PATH, 'boot.py')
    run_pyfile_checks(CODE_PATH, 'code.py')
    run_config_checks()
    run_morse_map_checks()
    return finish()


def finish():
    print()
    for label, status, detail in _checks:
        if label == '__section__':
            print('  --- %s %s' % (status, '-' * max(3, 55 - len(status))))
            continue
        dots = '.' * max(3, 37 - len(label))
        print('  %s %s %s' % (label, dots, _c(status, status)))
        if detail and status in ('PASS', 'SKIP'):
            print('        (%s)' % detail)
        elif detail:
            print('      %s' % detail)
    print()

    if _warnings:
        print('  Warnings (these will NOT stop the device, but review them):')
        for w in _warnings:
            print('    - %s' % _wrap(w))
        print()

    hard_ok = not any(status == 'FAIL' for _, status, _ in _checks)
    print('=' * 68)
    if hard_ok:
        print('  RESULT:  %s  -  safe to copy to the device.' % _c('PASS', 'PASS'))
        if _warnings:
            print('           (with the non-fatal warnings noted above)')
    else:
        print('  RESULT:  %s  -  fix the item(s) marked FAIL above before you'
              % _c('FAIL', 'FAIL'))
        print('           rely on these files. Do NOT unplug or replace your')
        print('           working files on the device until this reports PASS.')
    print('=' * 68)

    # A pause so the window doesn't vanish when double-clicked as an .exe.
    if getattr(sys, 'frozen', False):
        try:
            input('\n  Press Enter to close...')
        except EOFError:
            pass
    sys.exit(0 if hard_ok else 1)


if __name__ == '__main__':
    main()
