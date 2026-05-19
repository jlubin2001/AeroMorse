from adafruit_hid.keycode import Keycode

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
#   ........ (8 dots)      → Keyboard
#   -------- (8 dashes)    → Mouse / Shortcuts
#   ....---- (dots→dashes) → Macros
#   ----.... (dashes→dots) → Mouse / Shortcuts  (second shortcut)

g0 = init_group()

g0[8][0b00000000] = "group 1"   # ........  → Keyboard
g0[8][0b11111111] = "group 2"   # --------  → Mouse/Shortcuts
g0[8][0b00001111] = "group 3"   # ....----  → Macros
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
g1[6][0b000011]='/'         # ....--
g1[6][0b111100]='\\'        # ----..
g1[6][0b000010]='|'         # ....-.
g1[6][0b111101]='_'         # ----.-
g1[6][0b000110]='\"'        # ...--.
g1[6][0b001000]='\''        # ..-...
g1[6][0b110111]='`'         # --.---
g1[6][0b111011]='~'         # ---.--

# ── Function Keys ─────────────────────────────────────────────────────────────
# 7-symbol patterns. The dot/dash boundary shifts one position per key:
#   F1  --.----   F6  ---....
#   F2  --..---   F7  ----...
#   F3  --...--   F8  -----..
#   F4  --....-   F9  ------.
#   F5  --.....   F10 -------
#                 F11 .------
#                 F12 ..-----
g1[7][0b1101111]=Keycode.F1   # --.----
g1[7][0b1100111]=Keycode.F2   # --..---
g1[7][0b1100011]=Keycode.F3   # --...--
g1[7][0b1100001]=Keycode.F4   # --....-
g1[7][0b1100000]=Keycode.F5   # --.....
g1[7][0b1110000]=Keycode.F6   # ---....
g1[7][0b1111000]=Keycode.F7   # ----...
g1[7][0b1111100]=Keycode.F8   # -----..
g1[7][0b1111110]=Keycode.F9   # ------.
g1[7][0b1111111]=Keycode.F10  # -------
g1[7][0b0111111]=Keycode.F11  # .------
g1[7][0b0011111]=Keycode.F12  # ..-----

# ── Non-printable keyboard keys ───────────────────────────────────────────────
g1[5][0b01001]=Keycode.UP_ARROW      # .-..-
g1[5][0b01100]=Keycode.DOWN_ARROW    # .--..
g1[6][0b010100]=Keycode.LEFT_ARROW   # .-.-..
g1[5][0b01010]=Keycode.RIGHT_ARROW   # .-.-.
g1[7][0b0000000]=Keycode.HOME        # .......  (7 dots)
g1[7][0b0001000]=Keycode.END         # ...-...
g1[6][0b000001]=Keycode.PAGE_UP      # .....-
g1[6][0b000100]=Keycode.PAGE_DOWN    # ...-..
g1[4][0b0101]=Keycode.ENTER          # .-.-
g1[6][0b110000]=Keycode.ESCAPE       # --....
g1[6][0b101100]=Keycode.DELETE       # -.--..
g1[5][0b10100]=Keycode.INSERT        # -.-..
g1[2][0b11]=Keycode.BACKSPACE        # --     (freed from M)
g1[4][0b0011]=Keycode.SPACE          # ..--
g1[7][0b1110010]=Keycode.TAB         # ---..-.

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
g2[5][0b01001]=Keycode.UP_ARROW            # .-..-
g2[5][0b01100]=Keycode.DOWN_ARROW          # .--..
g2[6][0b010100]=Keycode.LEFT_ARROW         # .-.-..
g2[5][0b01010]=Keycode.RIGHT_ARROW         # .-.-.

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
g3[3][0b100]=''             # -..   D
g3[4][0b0010]=''            # ..-.  F
g3[3][0b110]=''             # --.   G
g3[4][0b0000]=''            # ....  H
g3[2][0b00]=''              # ..    I
g3[4][0b0111]=''            # .---  J
g3[3][0b101]=''             # -.-   K
g3[4][0b0100]=''            # .-..  L
g3[2][0b11]=''              # --    (backspace pattern)
g3[2][0b10]=''              # -.    N
g3[3][0b111]=''             # ---   O
g3[4][0b0110]=''            # .--.  P
g3[4][0b1101]=''            # --.-  Q
g3[3][0b010]=''             # .-.   R
g3[3][0b000]=''             # ...   S
g3[1][0b1]=''               # -     T
g3[3][0b001]=''             # ..-   U
g3[4][0b0001]=''            # ...-  V
g3[3][0b011]=''             # .--   W
g3[4][0b1001]=''            # -..-  X
g3[4][0b1011]=''            # -.--  Y
g3[4][0b1100]=''            # --..  Z

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
