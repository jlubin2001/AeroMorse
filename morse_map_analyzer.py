#!/usr/bin/env python3
"""
morse_map_analyzer.py
Analyzes morse_map.py for:
  1. Duplicate morse codes within each group (detected in source)
  2. Codes in g1/g2/g3 that conflict with g0 patterns
  3. Unused morse codes for lengths 2-7 in each group
"""

import sys, os, re, types
from datetime import date

# When frozen by PyInstaller the script runs from a temp extraction folder;
# morse_map.py and the report must be found relative to the .exe itself.
if getattr(sys, 'frozen', False):
    _BASE = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    _BASE = os.path.dirname(os.path.abspath(__file__))

MORSE_MAP_PATH = os.path.join(_BASE, 'morse_map.py')
REPORT_PATH    = os.path.join(_BASE, 'morse_map_report.txt')

# ── Mock adafruit_hid so morse_map imports cleanly ───────────────────────────

# Any Keycode.NAME is accepted (SHIFT, CONTROL, keypad digits, F13+ ...): the
# analyzer only counts patterns, so it must never stop on a key name. Whether a
# name really exists on the device is the validator's job, not this tool's.
class _KeycodeMeta(type):
    def __getattr__(cls, name):
        if name.startswith('__'):
            raise AttributeError(name)
        return f'Keycode.{name}'

class _Keycode(metaclass=_KeycodeMeta):
    pass

for _n in [
    'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
    'UP_ARROW','DOWN_ARROW','LEFT_ARROW','RIGHT_ARROW',
    'HOME','END','PAGE_UP','PAGE_DOWN','ENTER','ESCAPE',
    'DELETE','INSERT','BACKSPACE','SPACE','TAB',
    'LEFT_CONTROL','LEFT_SHIFT','LEFT_ALT','LEFT_GUI',
    'RIGHT_CONTROL','RIGHT_SHIFT','RIGHT_ALT','RIGHT_GUI',
    'CAPS_LOCK','SCROLL_LOCK','KEYPAD_NUMLOCK','PRINT_SCREEN',
    'KEYPAD_PLUS','KEYPAD_MINUS','KEYPAD_EQUALS','KEYPAD_ASTERISK',
    'KEYPAD_PERIOD','KEYPAD_FORWARD_SLASH','APPLICATION',
    'KEYPAD_ENTER','GUI','ALT',
]:
    setattr(_Keycode, _n, f'Keycode.{_n}')

# ConsumerControlCode is referenced by morse_map.py for g5 media keys.
# Mock just enough that morse_map imports — the analyzer only counts the
# patterns, not the resulting code values.
class _ConsumerControlCode:
    pass

for _n in [
    'PLAY_PAUSE', 'MUTE', 'VOLUME_INCREMENT', 'VOLUME_DECREMENT',
    'SCAN_NEXT_TRACK', 'SCAN_PREVIOUS_TRACK',
    'STOP', 'FAST_FORWARD', 'REWIND',
    'BRIGHTNESS_INCREMENT', 'BRIGHTNESS_DECREMENT',
    'EJECT', 'RECORD',
    # Application Launch + system controls (may or may not be in the
    # installed adafruit_hid bundle — morse_map skips missing ones)
    'AL_CALCULATOR', 'AL_LOCAL_MACHINE_BROWSER',
    'AL_INTERNET_BROWSER', 'AL_EMAIL_READER',
    'SLEEP', 'POWER',
]:
    setattr(_ConsumerControlCode, _n, f'ConsumerControlCode.{_n}')

_hid     = types.ModuleType('adafruit_hid')
_kc      = types.ModuleType('adafruit_hid.keycode')
_ccc     = types.ModuleType('adafruit_hid.consumer_control_code')
_kc.Keycode = _Keycode
_ccc.ConsumerControlCode = _ConsumerControlCode
_hid.keycode = _kc
_hid.consumer_control_code = _ccc
sys.modules['adafruit_hid']                            = _hid
sys.modules['adafruit_hid.keycode']                    = _kc
sys.modules['adafruit_hid.consumer_control_code']      = _ccc

sys.path.insert(0, os.path.dirname(MORSE_MAP_PATH))
import morse_map

# ── Helpers ───────────────────────────────────────────────────────────────────

def to_pattern(length, code):
    """Convert (length, int code) to dot/dash string, MSB = first symbol."""
    return ''.join('-' if (code >> (length - 1 - i)) & 1 else '.' for i in range(length))

GROUP_TITLES = {
    0: 'Group 0 — Always Available (System / Group Toggles)',
    1: 'Group 1 — Keyboard',
    2: 'Group 2 — Mouse / Shortcuts',
    3: 'Group 3 — Macros',
    4: 'Group 4 — Scanning (Switch Control)',
    5: 'Group 5 — Media / USB HID Consumer Controls',
    6: 'Group 6 — Placeholder',
    7: 'Group 7 — Placeholder',
    8: 'Group 8 — Placeholder',
    9: 'Group 9 — Placeholder',
}

def read_switch_group():
    """SWITCH_GROUP from the config.py next to morse_map.py (9 = the shipped
    default when it can't be read; 0 = no Switch group)."""
    try:
        cfg = open(os.path.join(os.path.dirname(MORSE_MAP_PATH), 'config.py'),
                   encoding='utf-8-sig').read()
        m = re.search(r'(?m)^SWITCH_GROUP\s*=\s*(\d+)', cfg)
        return int(m.group(1)) if m else 9
    except OSError:
        return 9

SWITCH_GROUP = read_switch_group()
if 1 <= SWITCH_GROUP <= 9:
    GROUP_TITLES[SWITCH_GROUP] = 'Group %d — Switch (no Morse codes here)' % SWITCH_GROUP

# ── 1. Duplicate assignments (source scan) ────────────────────────────────────

def find_source_duplicates(filepath):
    """Scan source for lines where the same gN[length][code] key is assigned more than once."""
    pat = re.compile(r'^(g\d)\[(\d+)\]\[(0b[01]+|\d+)\]')
    seen = {}   # key -> first line number
    dups = []   # (first_lineno, dup_lineno, group, length, code)
    with open(filepath, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            m = pat.match(line.strip())
            if m:
                group  = m.group(1)
                length = int(m.group(2))
                code   = int(m.group(3), 0)
                key    = (group, length, code)
                if key in seen:
                    dups.append((seen[key], lineno, group, length, code))
                else:
                    seen[key] = lineno
    return dups

# ── 2. g0 conflict check ──────────────────────────────────────────────────────

def find_g0_conflicts(groups):
    """Return entries in g1/g2/g3 whose (length, code) key also exists in g0."""
    g0_keys = {
        (length, code)
        for length, d in groups[0].items()
        for code in d
    }
    conflicts = []
    for gnum in range(1, len(groups)):
        for length, d in groups[gnum].items():
            for code in d:
                if (length, code) in g0_keys:
                    conflicts.append((gnum, length, code))
    return conflicts

# ── 3. Unused codes per group ─────────────────────────────────────────────────
# g0: lengths 6–8 (its codes are all length 8; lengths 2–5 are trivially empty)
# g1/g2/g3: lengths 2–7

LENGTH_RANGE = {0: range(6, 9)}   # g0
DEFAULT_RANGE = range(2, 8)        # g1, g2, g3

def find_unused(groups):
    """Return {gnum: {length: [sorted list of unused code ints]}}.
    A code that Group 0 already uses is NOT offered for the other groups:
    Group 0 is checked first, so it could never be reached there."""
    result = {}
    g0 = groups.get(0, {})
    for gnum, g in groups.items():
        lengths = LENGTH_RANGE.get(gnum, DEFAULT_RANGE)
        result[gnum] = {}
        for length in lengths:
            used  = set(g.get(length, {}).keys())
            if gnum != 0:
                used |= set(g0.get(length, {}).keys())
            all_c = set(range(1 << length))
            result[gnum][length] = sorted(all_c - used)
    return result

# ── Report writer ─────────────────────────────────────────────────────────────

def write_report(src_dups, g0_conflicts, unused_map, groups, outpath):
    W = 78
    out = []

    def ln(s=''):
        out.append(s)

    def rule(char='='):
        ln(char * W)

    def section(title):
        ln()
        rule('=')
        ln(f'  {title}')
        rule('=')

    def sub(title):
        ln()
        ln(f'  {title}')
        ln('  ' + '-' * (len(title) + 2))

    ln('morse_map.py  —  Analysis Report')
    ln(f'Generated : {date.today()}')
    ln(f'Source    : {MORSE_MAP_PATH}')

    # ── Section 1: Duplicates ─────────────────────────────────────────────────
    section('1.  DUPLICATE MORSE CODES WITHIN EACH GROUP')
    ln()
    if not src_dups:
        ln('  No duplicates found.')
    else:
        ln(f'  {"Group":<8}{"Len":<6}{"Binary":<14}{"Pattern":<12}'
           f'{"First at line":<16}{"Duplicate at line"}')
        ln('  ' + '-' * (W - 2))
        for first, dup, grp, length, code in src_dups:
            pat = to_pattern(length, code)
            ln(f'  {grp:<8}{length:<6}{bin(code):<14}{pat:<12}{first:<16}{dup}')

    # ── Section 2: g0 conflicts ───────────────────────────────────────────────
    section('2.  CODES CONFLICTING WITH GROUP 0  (g0)')
    ln()
    if not g0_conflicts:
        ln('  No conflicts with g0 found.')
    else:
        ln(f'  {"Group":<8}{"Len":<6}{"Binary":<14}{"Pattern":<12}'
           f'{"g0 value":<24}{"Group value"}')
        ln('  ' + '-' * (W - 2))
        for gnum, length, code in g0_conflicts:
            pat    = to_pattern(length, code)
            g0_val = repr(groups[0][length][code])
            gx_val = repr(groups[gnum][length][code])
            ln(f'  g{gnum:<7}{length:<6}{bin(code):<14}{pat:<12}{g0_val:<24}{gx_val}')

    # ── Section 3: Unused codes — paste-ready ─────────────────────────────────
    # Every line from here on is either a comment (starts with #) or a complete,
    # left-justified morse_map.py line in the map's own spacing, so any block can
    # be copied straight into morse_map.py without fixing indents or spaces.
    ln()
    ln('# ' + '=' * (W - 2))
    ln('# 3.  UNUSED MORSE CODES PER GROUP  —  ready to copy and paste')
    ln('#')
    ln('#   Every line below is either a comment (starts with #) or a complete')
    ln('#   morse_map.py line. To add a code: copy its line, paste it into that')
    ln("#   group's section of morse_map.py, and put what it should do between")
    ln("#   the quotes — e.g. 'my phrase' — or replace the quotes with a key")
    ln("#   (Keycode.ENTER), a secret (_secret('mykey')), an app launcher")
    ln("#   (_cc('AL_CALCULATOR', 0x192)) or a command ('mclick left 1').")
    ln('#')
    ln('#   Listed: Group 0 lengths 6-8, all other groups lengths 2-7. Codes that')
    ln('#   Group 0 already uses are left out of the other groups (Group 0 is')
    ln('#   checked first, so they could never be reached there).')
    ln('# ' + '=' * (W - 2))

    for gnum in sorted(unused_map):
        title = GROUP_TITLES.get(gnum, f'Group {gnum}')
        ln()
        ln()
        ln('# ' + '-' * (W - 2))
        ln(f'# {title}')
        ln('# ' + '-' * (W - 2))
        if gnum == SWITCH_GROUP:
            ln('# Nothing to add here: in the Switch group a sip and a puff hold a key each,')
            ln('# so no Morse code can be typed.')
            continue
        lengths = LENGTH_RANGE.get(gnum, DEFAULT_RANGE)
        for length in lengths:
            unused = unused_map[gnum][length]
            total  = 1 << length
            used_n = total - len(unused)
            ln()
            ln(f'# Group {gnum}, {length} symbols: {used_n} of {total} used, {len(unused)} free')
            if not unused:
                ln('# (none free)')
            else:
                for code in unused:
                    pat   = to_pattern(length, code)
                    entry = f"g{gnum}[{length}][0b{code:0{length}b}]=''"
                    ln(f'{entry:<28}# {pat}')

    ln()
    ln('# ' + '=' * (W - 2))
    ln('# END OF REPORT')
    ln('# ' + '=' * (W - 2))
    ln()

    with open(outpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
    print(f'Report written to: {outpath}')

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('Scanning source for duplicate assignments ...')
    src_dups = find_source_duplicates(MORSE_MAP_PATH)
    print(f'  Found {len(src_dups)} duplicate(s).')

    print('Checking for g0 conflicts ...')
    g0_conflicts = find_g0_conflicts(morse_map.groups)
    print(f'  Found {len(g0_conflicts)} conflict(s).')

    print('Computing unused codes for lengths 2–7 ...')
    unused = find_unused(morse_map.groups)

    write_report(src_dups, g0_conflicts, unused, morse_map.groups, REPORT_PATH)
