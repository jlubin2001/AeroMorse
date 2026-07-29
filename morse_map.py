from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode


class CC:
    """Wrapper marking a value as a USB HID ConsumerControl action.

    Keycode and ConsumerControlCode constants are both plain ints in
    adafruit_hid, so the firmware dispatcher can't tell them apart on
    `isinstance(x, int)`. Wrapping a ConsumerControlCode in CC() lets
    `code.py` route it to the ConsumerControl device instead of the
    Keyboard device.

    Use like:  g5[1][0b0] = CC(ConsumerControlCode.PLAY_PAUSE)
    """
    __slots__ = ('code',)
    def __init__(self, code):
        self.code = code


groups = {}

def init_group():
    """Helper to create the length-based dictionary structure"""
    return {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}}

############################################
# Begin Group 0
# ALWAYS AVAILABLE (System / Group toggles)
############################################
# Checked before the active group on every lookup.
# All patterns are 8 symbols — too long to trigger accidentally.
#
# Group toggles use a "count of trailing dashes" scheme: start from 8 dots
# (Keyboard) and add trailing dashes to reach the higher groups. The legacy
# g1 / g2 / g3 codes are unchanged; the gaps are filled by g4–g9.
#
#   ........  (0 dashes)  → g1  Keyboard
#   .......-  (1 dash)    → g4  Scanning / Switch Control (iOS / Android)
#   ......--  (2 dashes)  → g5
#   .....---  (3 dashes)  → g6
#   ....----  (4 dashes)  → g3  Macros
#   ...-----  (5 dashes)  → g7
#   ..------  (6 dashes)  → g8
#   .-------  (7 dashes)  → g9
#   --------  (8 dashes)  → g2  Mouse / Shortcuts
#   ----....  (alias)     → g2  Mouse / Shortcuts (second shortcut)

g0 = init_group()

g0[8][0b00000000] = "group 1"   # ........  → Keyboard
g0[8][0b00000001] = "group 4"   # .......-  → Scanning / Switch Control
g0[8][0b00000011] = "group 5"   # ......--  → Group 5 (placeholder)
g0[8][0b00000111] = "group 6"   # .....---  → Group 6 (placeholder)
g0[8][0b00001111] = "group 3"   # ....----  → Macros
g0[8][0b00011111] = "group 7"   # ...-----  → Group 7 (placeholder)
g0[8][0b00111111] = "group 8"   # ..------  → Group 8 (placeholder)
g0[8][0b01111111] = "group 9"   # .-------  → Group 9 (placeholder)
g0[8][0b11111111] = "group 2"   # --------  → Mouse/Shortcuts
g0[8][0b11110000] = "group 2"   # ----....  → Mouse/Shortcuts (second shortcut)

groups[0] = g0

############################################
# Begin Group 1
# KEYBOARD (Letters, Numbers, Punctuation)
############################################
# Bit encoding: 0 = dot (sip / sw-1), 1 = dash (puff / sw-2), MSB = first symbol.
#
# Two letters deliberately use non-standard patterns to free up
# high-frequency control keys on their original ITU Morse codes:
#   --   (standard M) → BACKSPACE   M relocated to ----
#   -.-. (standard C) → LEFT_CTRL   C relocated to ---.

g1 = init_group()

g1[5][0b00010]    = "group 2"   # ...-. → Switch to Mouse/Shortcuts

# ── Letters ───────────────────────────────────────────────────────────────────
g1[2][0b01]='a'             # .-
g1[4][0b1000]='b'           # -...
g1[4][0b1110]='c'           # ---.   (non-standard; -.-. freed for LEFT_CONTROL)
g1[3][0b100]='d'            # -..
g1[1][0b0]='e'              # .
g1[4][0b0010]='f'           # ..-.
g1[3][0b110]='g'            # --.
g1[4][0b0000]='h'           # ....
g1[2][0b00]='i'             # ..
g1[4][0b0111]='j'           # .---
g1[3][0b101]='k'            # -.-
g1[4][0b0100]='l'           # .-..
g1[4][0b1111]='m'           # ----   (non-standard; -- freed for BACKSPACE)
g1[2][0b10]='n'             # -.
g1[3][0b111]='o'            # ---
g1[4][0b0110]='p'           # .--.
g1[4][0b1101]='q'           # --.-
g1[3][0b010]='r'            # .-.
g1[3][0b000]='s'            # ...
g1[1][0b1]='t'              # -
g1[3][0b001]='u'            # ..-
g1[4][0b0001]='v'           # ...-
g1[3][0b011]='w'            # .--
g1[4][0b1001]='x'           # -..-
g1[4][0b1011]='y'           # -.--
g1[4][0b1100]='z'           # --..

# ── Numbers ───────────────────────────────────────────────────────────────────
# Standard ITU 5-symbol patterns. 1–5 lead with dots, 6–0 lead with dashes.
g1[5][0b01111]='1'          # .----
g1[5][0b00111]='2'          # ..---
g1[5][0b00011]='3'          # ...--
g1[5][0b00001]='4'          # ....-
g1[5][0b00000]='5'          # .....
g1[5][0b10000]='6'          # -....
g1[5][0b11000]='7'          # --...
g1[5][0b11100]='8'          # ---..
g1[5][0b11110]='9'          # ----.
g1[5][0b11111]='0'          # -----

# ── Punctuation ───────────────────────────────────────────────────────────────
g1[5][0b10001]='+'          # -...-
g1[5][0b01110]='-'          # .---.
g1[5][0b11101]='='          # ---.-
g1[5][0b10011]='*'          # -..--
g1[6][0b010000]='!'         # .-....
g1[6][0b111001]='@'         # ---..-
g1[6][0b001110]='#'         # ..---.
g1[6][0b001111]='$'         # ..----
g1[6][0b000101]='%'         # ...-.-
g1[6][0b100011]='^'         # -...--
g1[6][0b011100]='&'         # .---..
g1[6][0b011111]='.'         # .-----
g1[6][0b100000]=','         # -.....
g1[6][0b011110]=':'         # .----.
g1[6][0b100001]=';'         # -....-
g1[6][0b000111]=')'         # ...---
g1[6][0b111000]='('         # ---...
g1[6][0b100111]=']'         # -..---
g1[6][0b011000]='['         # .--...
g1[5][0b11001]='}'          # --..-
g1[5][0b00110]='{'          # ..--.
g1[6][0b110011]='<'         # --..--
g1[6][0b001100]='>'         # ..--..
g1[6][0b101111]='?'         # -.----
g1[6][0b000011]='/'         # ....--    (forward slash)
g1[6][0b111100]='\\'        # ----..    (backslash)
g1[6][0b000010]='|'         # ....-.
g1[6][0b111101]='_'         # ----.-
g1[6][0b000110]='\"'        # ...--.    (double quote)
g1[6][0b001000]='\''        # ..-...    (single quote)
g1[6][0b110111]='`'         # --.---
g1[6][0b111011]='~'         # ---.--

# ── Function Keys ─────────────────────────────────────────────────────────────
# 7-symbol patterns. Standand Numbers 1–0 lead with dashes. 1–2 trailed with dashes.
#   F1  --.----   F6  ---....
#   F2  --..---   F7  ----...
#   F3  --...--   F8  -----..
#   F4  --....-   F9  ------.
#   F5  --.....   F10 -------
#                 F11 .------
#                 F12 ..-----
g1[7][0b1101111]=Keycode.F1   # --.---- (--1)
g1[7][0b1100111]=Keycode.F2   # --..--- (--2)
g1[7][0b1100011]=Keycode.F3   # --...-- (--3)
g1[7][0b1100001]=Keycode.F4   # --....- (--4)
g1[7][0b1100000]=Keycode.F5   # --..... (--5)
g1[7][0b1110000]=Keycode.F6   # ---.... (--6)
g1[7][0b1111000]=Keycode.F7   # ----... (--7)
g1[7][0b1111100]=Keycode.F8   # -----.. (--8)
g1[7][0b1111110]=Keycode.F9   # ------. (--9)
g1[7][0b1111111]=Keycode.F10  # ------- (--0)
g1[7][0b0111111]=Keycode.F11  # .------ (1--)
g1[7][0b0011111]=Keycode.F12  # ..----- (2--)

# ── Non-printable keyboard keys ───────────────────────────────────────────────
g1[5][0b01001]=Keycode.UP_ARROW      # .-..-    (au)
g1[5][0b01100]=Keycode.DOWN_ARROW    # .--..    (ad)
g1[6][0b010100]=Keycode.LEFT_ARROW   # .-.-..   (al)
g1[5][0b01010]=Keycode.RIGHT_ARROW   # .-.-.    (ar)
g1[7][0b0000000]=Keycode.HOME        # .......  (sh) (7 dots)
g1[7][0b0001000]=Keycode.END         # ...-...  (sb)
g1[6][0b000001]=Keycode.PAGE_UP      # .....-   (su)
g1[6][0b000100]=Keycode.PAGE_DOWN    # ...-..   (sd)
g1[4][0b0101]=Keycode.ENTER          # .-.-
g1[6][0b110000]=Keycode.ESCAPE       # --....   (gs)
g1[6][0b101100]=Keycode.DELETE       # -.--..   (kd)
g1[5][0b10100]=Keycode.INSERT        # -.-..    (ku)
g1[2][0b11]=Keycode.BACKSPACE        # --     (freed from M)
g1[4][0b0011]=Keycode.SPACE          # ..--
g1[7][0b1110010]=Keycode.TAB         # ---..-.  (sf)
g1[5][0b00100] = "repeat"            # ..-..    repeat

# ── Modifier keys ─────────────────────────────────────────────────────────────
# Sticky: press once to arm, next key fires with the modifier, then it releases.
# Press again while armed to cancel.
g1[4][0b1010]=Keycode.LEFT_CONTROL   # -.-. (freed from C)
g1[6][0b110001]=Keycode.LEFT_SHIFT   # --...-
g1[5][0b11011]=Keycode.LEFT_ALT      # --.--
g1[6][0b011011]=Keycode.LEFT_GUI     # .--.--
g1[6][0b111110]=Keycode.CAPS_LOCK    # -----.
g1[6][0b110100]=Keycode.SCROLL_LOCK  # --.-..
g1[7][0b1110001]=Keycode.KEYPAD_NUMLOCK  # ---...-
g1[6][0b110110]=Keycode.PRINT_SCREEN # --.--.

groups[1] = g1

############################################
# Begin Group 2
# MOUSE MOVES & WINDOWS SHORTCUTS
############################################
# Mouse movement patterns map to the numeric keypad layout:
#
#   7  8  9         Numpad   Small (2–3 sym)   Large (5-sym, same direction)
#   4  5  6         ──────   ───────────────   ────────────────────────────
#   1  2  3         7 ↖       --...             diagonal only
#                   8 ↑       --                ---..
#                   9 ↗       ----.             diagonal only
#                   4 ←       ..                ....-
#                   5 · (repeat)   .
#                   6 →       ...               -....
#                   1 ↙       .----             diagonal only
#                   2 ↓       ---               ..---
#                   3 ↘       ...--             diagonal only
#
#   Scroll up  .....-   Scroll down  ...-..

g2 = init_group()

g2[5][0b00010]    = "group 1"   # ...-. → Switch to Keyboard

# ── Mouse movement — cardinal, small (2–3 symbols) ────────────────────────────
g2[2][0b11] = "mmove 0 -1 0"       # --      numpad 8  ↑
g2[3][0b111] = "mmove 0 1 0"       # ---     numpad 2  ↓
g2[3][0b000] = "mmove 1 0 0"       # ...     numpad 6  →
g2[2][0b00] = "mmove -1 0 0"       # ..      numpad 4  ←

# ── Mouse movement — scroll (6 symbols) ──────────────────────────────────────
g2[6][0b000001] = "mmove 0 0 1"    # .....-  scroll ↑
g2[6][0b000100] = "mmove 0 0 -1"   # ...-..  scroll ↓

# ── Mouse movement — diagonal (5 symbols) ────────────────────────────────────
g2[5][0b11000] = "mmove -1 -1 0"   # --...   numpad 7  ↖
g2[5][0b11110] = "mmove 1 -1 0"    # ----.   numpad 9  ↗
g2[5][0b01111] = "mmove -1 1 0"    # .----   numpad 1  ↙
g2[5][0b00011] = "mmove 1 1 0"     # ...--   numpad 3  ↘

# ── Mouse movement — cardinal, large (5 symbols) ─────────────────────────────
g2[5][0b11100] = "mmove 0 -1 0"    # ---..   numpad 8  ↑  large
g2[5][0b00111] = "mmove 0 1 0"     # ..---   numpad 2  ↓  large
g2[5][0b00001] = "mmove -1 0 0"    # ....-   numpad 4  ←  large
g2[5][0b10000] = "mmove 1 0 0"     # -....   numpad 6  →  large

# ── Mouse buttons and movement control ───────────────────────────────────────
g2[1][0b0] = "repeat"              # .       numpad 5  repeat last action
g2[5][0b00100] = "repeat"         # ..-..   alternate repeat
g2[4][0b1100] = "mslow"            # --..    toggle slow-step mode
g2[2][0b01] = "mclick left 1"      # .-      left click
g2[3][0b011] = "mclick right 1"    # .--     right click
g2[3][0b001] = "mclick left 2"     # ..-     double-click left
g2[4][0b0011] = "mclick right 2"   # ..--    double-click right
g2[2][0b10] = "mdrag left"         # -.      toggle left-button drag
g2[7][0b1010010] = "mreset"        # -.-..-. reset all mouse state

# ── Keypad & Arrow Keys ───────────────────────────────────────────────────────
g2[5][0b10001]=Keycode.KEYPAD_PLUS         # -...-
g2[5][0b01110]=Keycode.KEYPAD_MINUS        # .---.
g2[5][0b11101]=Keycode.KEYPAD_EQUALS       # ---.-
g2[5][0b10011]=Keycode.KEYPAD_ASTERISK     # -..--
g2[6][0b011111]=Keycode.KEYPAD_PERIOD      # .-----
g2[6][0b000011]=Keycode.KEYPAD_FORWARD_SLASH  # ....--
g2[6][0b111100]=Keycode.APPLICATION        # ----..  context-menu key
g2[7][0b1110001]=Keycode.KEYPAD_NUMLOCK    # ---...-
g2[4][0b0101]=Keycode.KEYPAD_ENTER         # .-.-
g2[5][0b01001]=Keycode.UP_ARROW            # .-..-      (au)
g2[5][0b01100]=Keycode.DOWN_ARROW          # .--..      (ad)
g2[6][0b010100]=Keycode.LEFT_ARROW         # .-.-..     (al)
g2[5][0b01010]=Keycode.RIGHT_ARROW         # .-.-.      (ar)

# ── Windows Shortcuts (tuples = all keys pressed simultaneously) ──────────────
g2[6][0b110000]=Keycode.RIGHT_CONTROL, Keycode.RIGHT_ALT, Keycode.LEFT_ARROW  # --....  free mouse from VM
g2[5][0b00000]=Keycode.ALT, Keycode.TAB    # .....   switch windows
g2[5][0b11111]=Keycode.GUI, Keycode.TAB    # -----   task view

# ── Modifier keys ─────────────────────────────────────────────────────────────
g2[4][0b1010]=Keycode.RIGHT_CONTROL        # -.-.
g2[6][0b110001]=Keycode.RIGHT_SHIFT        # --...-
g2[5][0b11011]=Keycode.RIGHT_ALT           # --.--
g2[6][0b011011]=Keycode.RIGHT_GUI          # .--.--

groups[2] = g2

############################################
# Begin Group 3
# MACRO STRINGS
############################################
# Patterns mirror the Group 1 alphabet so the same Morse muscle-memory
# produces a macro string instead of a single character.
# Single-char values are typed as individual key presses;
# longer strings are typed through the keyboard layout writer.
# Fill the empty placeholders with the user's frequently needed phrases.

g3 = init_group()

# ── Named macros (reuse A B C E patterns) ────────────────────────────────────
g3[2][0b01]='name'          # .-    A
g3[4][0b1000]='address'     # -...  B
g3[4][0b1110]='phone'       # ---.  C (non-standard pattern)
g3[1][0b0]='email'          # .     E

# ── Placeholders — fill with user phrases; pattern = Group 1 letter ───────────
g3[3][0b100]='phrase'             # -..   D
g3[4][0b0010]='phrase'            # ..-.  F
g3[3][0b110]='phrase'             # --.   G
g3[4][0b0000]='phrase'            # ....  H
g3[2][0b00]='phrase'              # ..    I
g3[4][0b0111]='phrase'            # .---  J
g3[3][0b101]='phrase'             # -.-   K
g3[4][0b0100]='phrase'            # .-..  L
g3[4][0b1111]='phrase'            # ----  M
g3[2][0b10]='phrase'              # -.    N
g3[3][0b111]='phrase'             # ---   O
g3[4][0b0110]='phrase'            # .--.  P
g3[4][0b1101]='phrase'            # --.-  Q
g3[3][0b010]='phrase'             # .-.   R
g3[3][0b000]='phrase'             # ...   S
g3[1][0b1]='phrase'               # -     T
g3[3][0b001]='phrase'             # ..-   U
g3[4][0b0001]='phrase'            # ...-  V
g3[3][0b011]='phrase'             # .--   W
g3[4][0b1001]='phrase'            # -..-  X
g3[4][0b1011]='phrase'            # -.--  Y
g3[4][0b1100]='phrase'            # --..  Z

# ── Numbers (same patterns as Group 1) ───────────────────────────────────────
g3[5][0b01111]='1'          # .----
g3[5][0b00111]='2'          # ..---
g3[5][0b00011]='3'          # ...--
g3[5][0b00001]='4'          # ....-
g3[5][0b00000]='5'          # .....
g3[5][0b10000]='6'          # -....
g3[5][0b11000]='7'          # --...
g3[5][0b11100]='8'          # ---..
g3[5][0b11110]='9'          # ----.
g3[5][0b11111]='0'          # -----

# ── Editing keys available in Macro mode ─────────────────────────────────────
g3[4][0b0101]=Keycode.ENTER      # .-.-
g3[2][0b11]=Keycode.BACKSPACE    # --

groups[3] = g3

############################################
# Placeholder group seed (g4–g9)
############################################
# Builds a fresh group pre-loaded with g1's A–Z (1–4 symbol patterns) and
# 0–9 (5-symbol patterns). Punctuation, function keys, navigation, and
# modifiers are intentionally NOT copied, so placeholder groups start
# minimal and are easy to customise. Switch between groups any time using
# the 8-symbol Group 0 toggle codes documented at the top of this file.

def _seed_letters_numbers():
    g = init_group()
    for length in (1, 2, 3, 4):
        for pattern, value in g1[length].items():
            if isinstance(value, str) and len(value) == 1 and value.isalpha():
                g[length][pattern] = value          # copy single letters a–z
    for pattern, value in g1[5].items():
        if isinstance(value, str) and len(value) == 1 and value.isdigit():
            g[5][pattern] = value                   # copy single digits 0–9
    return g

############################################
# Begin Group 4
# SCANNING (Switch Control on iOS / Android)
############################################
# iOS and Android "Switch Control" accessibility scanning can be driven by
# function keys acting as switch actions. The 12 SHORTEST Morse patterns
# are mapped to F1–F12 so the most-used scan actions take the least effort.
# The remaining letters / numbers are inherited from g1 as a placeholder
# and can be customised.
#
#   F1  .      F5  -.     F9   .-.
#   F2  -      F6  --     F10  .--
#   F3  ..     F7  ...    F11  -..
#   F4  .-     F8  ..-    F12  -.-

g4 = _seed_letters_numbers()

g4[1][0b0]   = Keycode.F1     # .
g4[1][0b1]   = Keycode.F2     # -
g4[2][0b00]  = Keycode.F3     # ..
g4[2][0b01]  = Keycode.F4     # .-
g4[2][0b10]  = Keycode.F5     # -.
g4[2][0b11]  = Keycode.F6     # --
g4[3][0b000] = Keycode.F7     # ...
g4[3][0b001] = Keycode.F8     # ..-
g4[3][0b010] = Keycode.F9     # .-.
g4[3][0b011] = Keycode.F10    # .--
g4[3][0b100] = Keycode.F11    # -..
g4[3][0b101] = Keycode.F12    # -.-

groups[4] = g4

############################################
# Begin Groups 5–9
# PLACEHOLDERS — copy of g1 letters + numbers
############################################
# Identical letter/number layout to Group 1 so existing muscle memory works
# while you decide what each group is for. Replace the entries with your own
# keycodes, macros, or command strings. Reach each group with its Group 0
# toggle code (see top of file).

for _gid in range(5, 10):
    groups[_gid] = _seed_letters_numbers()

############################################
# Group 5 — MEDIA (USB HID Consumer Controls)
############################################
# The 12 SHORTEST Morse patterns are reassigned to the most-used USB HID
# Consumer Control codes — volume, play/pause, mute, track skip, etc. This
# turns g5 into a media-remote group. The remaining letters and numbers
# stay as the placeholder seed.
#
# Wrapped in CC(...) so the dispatcher routes them through the
# ConsumerControl HID device, not the Keyboard.
#
#   .    PLAY_PAUSE         ..   VOLUME_DECREMENT    -.   PREVIOUS TRACK
#   -    MUTE               --   VOLUME_INCREMENT    .-   NEXT TRACK
#   ...  STOP               ..-  REWIND              .-.  FAST FORWARD
#   .--  BRIGHTNESS +       -..  BRIGHTNESS -        -.-  EJECT
#
# The 4-symbol patterns add application launchers and system power, keyed to
# first-letter mnemonics in STANDARD ITU Morse (note: g1's own 'c' is the
# non-standard ---. because -.-. is freed there for LEFT_CONTROL; the
# mnemonic below refers to the ITU letter, not to g1's mapping):
#
#   -.-.  C  Calculator        .-..  L  mai-L (email)
#   ..-.  F  File explorer     --..  Z  Z-z-z (sleep)
#   -...  B  Browser           .--.  P  Power

g5 = groups[5]

# ── Media — 12 shortest patterns (1–3 symbol) ─────────────────────────────
g5[1][0b0]   = CC(ConsumerControlCode.PLAY_PAUSE)            # .
g5[1][0b1]   = CC(ConsumerControlCode.MUTE)                  # -
g5[2][0b00]  = CC(ConsumerControlCode.VOLUME_DECREMENT)      # ..
g5[2][0b01]  = CC(ConsumerControlCode.SCAN_NEXT_TRACK)       # .-
g5[2][0b10]  = CC(ConsumerControlCode.SCAN_PREVIOUS_TRACK)   # -.
g5[2][0b11]  = CC(ConsumerControlCode.VOLUME_INCREMENT)      # --
g5[3][0b000] = CC(ConsumerControlCode.STOP)                  # ...
g5[3][0b001] = CC(ConsumerControlCode.REWIND)                # ..-
g5[3][0b010] = CC(ConsumerControlCode.FAST_FORWARD)          # .-.
g5[3][0b011] = CC(ConsumerControlCode.BRIGHTNESS_INCREMENT)  # .--
g5[3][0b100] = CC(ConsumerControlCode.BRIGHTNESS_DECREMENT)  # -..
g5[3][0b101] = CC(ConsumerControlCode.EJECT)                 # -.-

# ── Application launch + system — 4-symbol patterns ───────────────────────
# adafruit_hid only gained the AL_* / SLEEP / POWER names in recent bundles.
# Rather than skip these entries on an older bundle, resolve each by name and
# fall back to its raw usage ID from the USB HID Usage Tables, Consumer Page
# (0x0C). Those IDs are fixed by the spec, so the fallback is always correct
# and these codes work on every bundle version.
#
# These overwrite the placeholder letters b / f / l / z / p seeded from g1
# (-.-. was already free here, since g1 uses it for LEFT_CONTROL).
def _cc(name, usage_id):
    return CC(getattr(ConsumerControlCode, name, usage_id))

g5[4][0b1010] = _cc('AL_CALCULATOR',            0x192)   # -.-.  C  calculator
g5[4][0b0010] = _cc('AL_LOCAL_MACHINE_BROWSER', 0x194)   # ..-.  F  file explorer
g5[4][0b1000] = _cc('AL_INTERNET_BROWSER',      0x196)   # -...  B  web browser
g5[4][0b0100] = _cc('AL_EMAIL_READER',          0x18A)   # .-..  L  mai-L
g5[4][0b1100] = _cc('SLEEP',                    0x032)   # --..  Z  Z-z-z
# NOTE: POWER on a 4-symbol pattern can be triggered by accident in a group
# whose 1–3 symbol patterns are routine media keys. Comment this line out, or
# move it to a longer pattern, if an accidental shutdown would be costly.
g5[4][0b0110] = _cc('POWER',                    0x030)   # .--.  P  power
