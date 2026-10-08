# AeroMorse morse_map_darci.py — version 1.26 (released 2026-10-07)
# Official source (always get the latest here): https://github.com/jlubin2001/AeroMorse
# Darci-USB code set. To use it, copy it to the CIRCUITPY drive as morse_map.py.
"""
morse_map_darci.py  —  Darci-USB-compatible code set for AeroMorse.

Drop-in replacement for morse_map.py for users migrating from the
WesTest Darci USB. Rename this file to morse_map.py on the CIRCUITPY
drive to activate.

════════════════════════════════════════════════════════════════════════════
SOURCE
  Codes transcribed verbatim from the Darci USB Owner's Manual,
  WesTest Engineering Corp. P/N 3001508 (6/13/02), Appendix
  "Morse/Plus Listing" — Standard Characters, Sticky Keys, Command
  Codes, Mouse Control Codes, Number Mode Codes, International
  Keyboard Keys, and Keyboard Extensions tables.

DIFFERENCES FROM DEFAULT AeroMorse morse_map.py
  • M (--) and C (-.-.) keep their standard ITU patterns. Darci has
    no need to free those for BACKSPACE / LEFT_CTRL.
  • BACKSPACE is on Darci's main-set code "----" (4 dashes).
  • SPACE is on Darci's main-set code "..--" (4 symbols).
  • Mouse Mode and Number Mode are implemented as group switches
    rather than Darci's stateful modes.
  • Groups 4–9 are AeroMorse extras with no Darci equivalent: Scanning,
    Media, three groups of your own, and the Switch group (config.py
    SWITCH_GROUP = 9). They are reached only by their 8-symbol Group 0
    codes or by cycling, so they never get in the way of Darci codes.
  • All keyboard extensions, navigation, F-keys, modifiers and
    punctuation use Darci's exact published codes.

KNOWN LIMITATIONS
  • Darci's single-switch (timed) input mode is NOT supported by
    AeroMorse firmware. Two switches (or sip-and-puff) are required.
  • A few Darci codes are intentionally duplicated in the original
    listing (e.g. Down Arrow and backtick both = "------"). Resolved
    here in favor of the more useful key.
  • Darci's mouse mode codes are very short (1-4 symbols) and will
    collide with letters if used in g1. They are isolated in g2 here.
  • A mouse-move code moves ONE step. To keep moving, follow it with the
    repeat code (.-. or Darci's .-..-.); the same code stops it.
  • Darci's "click & hold" codes toggle a drag: once to press the button,
    again to let go.
════════════════════════════════════════════════════════════════════════════
"""

from adafruit_hid.keycode import Keycode
from adafruit_hid.consumer_control_code import ConsumerControlCode


class CC:
    """Marks a value as a media / app-launcher key (USB HID Consumer Control),
    so code.py sends it to the right device. Use  CC(ConsumerControlCode.MUTE)."""
    __slots__ = ('code',)
    def __init__(self, code):
        self.code = code

def _cc(name, usage_id):
    """An app-launcher / media key by NAME, for use in ANY group, e.g.
        gN[length][0b...] = _cc('AL_CALCULATOR', 0x192)
    Older key libraries lack the AL_* names, so the raw code from the USB
    standard is given as well and used when the name is missing."""
    return CC(getattr(ConsumerControlCode, name, usage_id))


groups = {}

def init_group():
    return {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}}


############################################
# Secret macros (passwords / personal details) — usable in ANY group
############################################
# Never write a password or PIN into this file. Keep the real values in
# macro_secrets.enc (PIN-locked, made with the "AeroMorse Secrets" PC tool) or
# macro_secrets.txt, and pull one in by its name:
# g6[6][0b000000]=_secret('mykey')   # ......
# Until the name is set, the code types a harmless placeholder instead. See
# README "Storing passwords and secrets safely".
class Secret:
    """Marker for a private value. code.py looks up `key` when the pattern is
    used, so the value is never stored in (or shown from) this file."""
    __slots__ = ('key', 'placeholder')
    def __init__(self, key, placeholder):
        self.key = key
        self.placeholder = placeholder

def _secret(key, placeholder=None):
    """Pattern types the secret stored under `key`, or `placeholder` if it
    isn't set. The second argument is optional."""
    if placeholder is None:
        placeholder = '(set %s in AeroMorse Secrets)' % key
    return Secret(key, placeholder)


############################################
# Group 0 — Always Available (group toggles)
############################################
# AeroMorse safe 8-symbol toggles (same codes as the standard morse_map.py).
# Darci's "Change Code Set" command (---.- , 5 symbols) is too short to use
# as a global toggle.
g0 = init_group()
g0[8][0b00000000] = "group 1"   # ........  → Keyboard
g0[8][0b00000001] = "group 4"   # .......-  → Scanning / Switch Control
g0[8][0b00000011] = "group 5"   # ......--  → Media
g0[8][0b00000111] = "group 6"   # .....---  → Group 6 (yours)
g0[8][0b00001111] = "group 3"   # ....----  → Number Mode
g0[8][0b00011111] = "group 7"   # ...-----  → Group 7 (yours)
g0[8][0b00111111] = "group 8"   # ..------  → Group 8 (yours)
g0[8][0b01111111] = "group 9"   # .-------  → Group 9 — Switch (sip/puff hold keys, no Morse)
g0[8][0b11111111] = "group 2"   # --------  → Mouse Mode
g0[8][0b11110000] = "group 4"   # ----....  → Scanning / Switch Control (second shortcut)

# Device commands — here in Group 0 so they work from every group.
g0[7][0b1010010]  = "devicereset"   # -.-..-.   restart the device (asks "CONFIRM RESET Y/N?", type y)
g0[8][0b00010010] = "version"       # ...-..-.  show start-up screen (name, version, CircuitPython)
groups[0] = g0


############################################
# Group 1 — Keyboard (Darci "Main Code Set")
############################################
g1 = init_group()

# ── Darci command-code shortcuts to other groups ─────────────────────────
# Darci uses these codes to toggle Mouse / Number modes. We re-route them
# as group switches so existing muscle memory works.
g1[5][0b11010] = "group 2"   # --.-.   Darci "Mouse Mode" (mr)
g1[5][0b10001] = "group 3"   # -...-   Darci "Number Mode"

# ── Letters (standard ITU Morse — identical to Darci) ────────────────────
g1[2][0b01]   = 'a'    # .-
g1[4][0b1000] = 'b'    # -...
g1[4][0b1010] = 'c'    # -.-.
g1[3][0b100]  = 'd'    # -..
g1[1][0b0]    = 'e'    # .
g1[4][0b0010] = 'f'    # ..-.
g1[3][0b110]  = 'g'    # --.
g1[4][0b0000] = 'h'    # ....
g1[2][0b00]   = 'i'    # ..
g1[4][0b0111] = 'j'    # .---
g1[3][0b101]  = 'k'    # -.-
g1[4][0b0100] = 'l'    # .-..
g1[2][0b11]   = 'm'    # --
g1[2][0b10]   = 'n'    # -.
g1[3][0b111]  = 'o'    # ---
g1[4][0b0110] = 'p'    # .--.
g1[4][0b1101] = 'q'    # --.-
g1[3][0b010]  = 'r'    # .-.
g1[3][0b000]  = 's'    # ...
g1[1][0b1]    = 't'    # -
g1[3][0b001]  = 'u'    # ..-
g1[4][0b0001] = 'v'    # ...-
g1[3][0b011]  = 'w'    # .--
g1[4][0b1001] = 'x'    # -..-
g1[4][0b1011] = 'y'    # -.--
g1[4][0b1100] = 'z'    # --..

# ── Numbers (standard ITU — identical to Darci) ──────────────────────────
g1[5][0b01111] = '1'   # .----
g1[5][0b00111] = '2'   # ..---
g1[5][0b00011] = '3'   # ...--
g1[5][0b00001] = '4'   # ....-
g1[5][0b00000] = '5'   # .....
g1[5][0b10000] = '6'   # -....
g1[5][0b11000] = '7'   # --...
g1[5][0b11100] = '8'   # ---..
g1[5][0b11110] = '9'   # ----.
g1[5][0b11111] = '0'   # -----

# ── Main-set special characters (Darci defaults) ─────────────────────────
g1[4][0b0011]    = Keycode.SPACE       # ..--   (Darci main-set space)
g1[4][0b1111]    = Keycode.BACKSPACE   # ----   (Darci main-set backspace)
g1[6][0b010101]  = '.'                 # .-.-.-   period
g1[6][0b110011]  = ','                 # --..--   comma
g1[6][0b001100]  = '?'                 # ..--..   question mark
g1[6][0b010011]  = '!'                 # .-..--   Darci's !  (mnemonic from "la"+t?)

# ── Sticky-key modifiers (Darci codes) ───────────────────────────────────
# Darci-style: tap once arms, tap twice locks, tap thrice releases.
# AeroMorse firmware implements single-tap-arms automatically.
g1[5][0b00101]   = Keycode.LEFT_SHIFT     # ..-.-
g1[6][0b011101]  = Keycode.RIGHT_SHIFT    # .---.-
g1[5][0b01011]   = Keycode.LEFT_ALT       # .-.--
g1[6][0b001101]  = Keycode.RIGHT_ALT      # ..--.-
g1[5][0b10101]   = Keycode.LEFT_CONTROL   # -.-.-
g1[6][0b110101]  = Keycode.RIGHT_CONTROL  # --.-.-
g1[6][0b001011]  = Keycode.LEFT_GUI       # ..-.--   Left Windows
g1[6][0b101011]  = Keycode.RIGHT_GUI      # -.-.--   Right Windows
g1[6][0b100011]  = Keycode.APPLICATION    # -...--   Application Key

# ── Darci command codes (kept for reference / system use) ────────────────
# Repeat last character: Darci ".-..-." (rr).
g1[6][0b010010]  = "repeat"               # .-..-.
# Start Menu. (Darci's Sound Mode, Keypad Mode and Change Code Set commands
# have no AeroMorse equivalent and are not mapped.)
g1[6][0b110000]  = Keycode.GUI            # --....   Darci Start Menu (taps Windows key)

# ── Keyboard extensions (Darci letter-pair mnemonics) ────────────────────
g1[4][0b0101]    = Keycode.ENTER          # .-.-     ent
g1[5][0b00100]   = Keycode.ESCAPE         # ..-..    ere
g1[5][0b10010]   = Keycode.DELETE         # -..-.    dte
g1[5][0b01001]   = Keycode.INSERT         # .-..-    au
g1[6][0b101010]  = ':'                    # -.-.-.   cn
g1[5][0b00010]   = ';'                    # ...-.    sn
g1[6][0b010001]  = '<'                    # .-...-   la
g1[6][0b110010]  = '>'                    # --..-.   zn
g1[5][0b11011]   = '"'                    # --.--    qt
g1[5][0b11001]   = '/'                    # --..-    zt
g1[6][0b100000]  = '\\'                   # -.....   bs (Darci listing)
g1[5][0b10110]   = Keycode.TAB            # -.--.    tan
g1[6][0b000010]  = Keycode.HOME           # ....-.   hn
g1[5][0b10100]   = Keycode.END            # -.-..    nd
g1[6][0b111001]  = Keycode.PAGE_UP        # ---..-
g1[6][0b111010]  = Keycode.PAGE_DOWN      # ---.-.
g1[6][0b111101]  = Keycode.LEFT_ARROW     # ----.-
g1[6][0b111110]  = Keycode.RIGHT_ARROW    # -----.
g1[6][0b111100]  = Keycode.UP_ARROW       # ----..
g1[6][0b111111]  = Keycode.DOWN_ARROW     # ------

# ── Symbols (Darci letter-pair mnemonics) ────────────────────────────────
g1[5][0b01110]   = '@'                    # .---.    atn  (a+t+n)
g1[5][0b10111]   = '#'                    # -.---    no   (n+o)
g1[6][0b101001]  = '^'                    # -.-..-   Ca   (c+a)
g1[5][0b01101]   = '='                    # .--.-    eq   (e+q)
g1[6][0b011010]  = '%'                    # .--.-.   pn   (p+n)
g1[5][0b01100]   = '+'                    # .--..    pe   (p+e)
g1[4][0b1110]    = '-'                    # ---.     mn   (m+n)
g1[5][0b01000]   = '*'                    # .-...    as   (a+s)
g1[6][0b000110]  = '('                    # ...--.   sg   (s+g)
g1[6][0b100110]  = ')'                    # -..--.   dg   (d+g)
g1[6][0b001000]  = '['                    # ..-...   us   (u+s)
g1[6][0b101000]  = ']'                    # -.-...   ks   (k+s)
g1[6][0b001110]  = '{'                    # ..---.   ug   (u+g)
g1[6][0b101110]  = '}'                    # -.---.   kg   (k+g)
g1[6][0b100010]  = '$'                    # -...-.   dr   (d+r)
g1[6][0b110001]  = '~'                    # --...-   tda  (t+d+a)
g1[5][0b00110]   = '_'                    # ..--.    un   (u+n)
g1[6][0b000100]  = '|'                    # ...-..   vi   (v+i)
g1[5][0b10011]   = '&'                    # -..--    xt   (x+t)
g1[6][0b000101]  = Keycode.SCROLL_LOCK    # ...-.-   sk
g1[6][0b100001]  = Keycode.PRINT_SCREEN   # -....-   du

# ── F-keys (Darci "eN" / "tN" mnemonics, 6–7 symbols) ────────────────────
g1[6][0b001111]  = Keycode.F1             # ..----   e1   (e + 1)
g1[6][0b000111]  = Keycode.F2             # ...---   e2
g1[6][0b000011]  = Keycode.F3             # ....--   e3
g1[6][0b000001]  = Keycode.F4             # .....-   e4
g1[6][0b000000]  = Keycode.F5             # ......   e5
g1[6][0b010000]  = Keycode.F6             # .-....   e6
g1[6][0b011000]  = Keycode.F7             # .--...   e7
g1[6][0b011100]  = Keycode.F8             # .---..   e8
g1[6][0b011110]  = Keycode.F9             # .----.   e9
g1[6][0b011111]  = Keycode.F10            # .-----   e0
g1[7][0b1011111] = Keycode.F11            # -.-----  t1 (Darci listing — 7 symbols)
g1[7][0b1001111] = Keycode.F12            # -..----  t2

# ── Lock / system keys (Darci codes) ─────────────────────────────────────
g1[6][0b001010]  = Keycode.CAPS_LOCK              # ..-.-.   ic
g1[6][0b100100]  = Keycode.KEYPAD_NUMLOCK         # -..-..   nl
g1[6][0b101101]  = Keycode.ALT, Keycode.PRINT_SCREEN  # -.--.-   kk  Sys Req (= Alt + Print Screen)
g1[6][0b011001]  = Keycode.PAUSE                  # .--..-   pa  Pause / Break

groups[1] = g1


############################################
# Group 2 — Mouse Mode (Darci "Mouse Mode")
############################################
# Darci's mouse codes are extremely short (1–4 symbols). They can only live
# in a separate group because they would collide with letters in g1.
# In Darci, entering Mouse Mode (--.-.) blocks character output until
# Mouse Mode is toggled off; in AeroMorse, switching to g2 has the same
# effect.
g2 = init_group()

# Exit back to keyboard (Darci's exit code = mr = --.-.)
g2[5][0b11010] = "group 1"     # --.-.   Darci "Exit mouse mode"

# Cardinal movement (Darci's actual codes)
g2[1][0b0]    = "mmove 1 0 0"    # .    move right
g2[1][0b1]    = "mmove -1 0 0"   # -    move left
g2[2][0b00]   = "mmove 0 -1 0"   # ..   move up
g2[2][0b11]   = "mmove 0 1 0"    # --   move down

# Diagonal movement (Darci's actual codes)
g2[4][0b0011] = "mmove -1 -1 0"  # ..--   move up & left
g2[4][0b0000] = "mmove 1 -1 0"   # ....   move up & right
g2[4][0b1111] = "mmove -1 1 0"   # ----   move down & left
g2[4][0b1100] = "mmove 1 1 0"    # --..   move down & right

# Click codes (Darci's actual codes)
g2[2][0b10]   = "mclick left 1"  # -.    click left
g2[3][0b110]  = "mclick left 2"  # --.   double-click left
g2[3][0b111]  = "mdrag left"     # ---   click & hold left  (again to let go)
g2[2][0b01]   = "mclick right 1" # .-    click right
g2[3][0b001]  = "mclick right 2" # ..-   double-click right
g2[3][0b000]  = "mdrag right"    # ...   click & hold right (again to let go)

# Keep moving / stop. A move code moves one step; the repeat code keeps the
# last move going, and the same code again (or a click) stops it.
g2[3][0b010]    = "repeat"       # .-.      keep moving / stop
g2[6][0b010010] = "repeat"       # .-..-.   same, on Darci's own Repeat code (rr)

groups[2] = g2


############################################
# Group 3 — Number Mode (Darci "Number Mode")
############################################
# Darci's Number Mode reassigns very short codes to digits 0–9 and basic
# arithmetic. Enter with -...-  (Darci toggle), exit with the same code.
g3 = init_group()

g3[5][0b10001] = "group 1"     # -...-  Darci "Exit Number Mode"

g3[1][0b0]    = '1'    # .
g3[1][0b1]    = '2'    # -
g3[2][0b01]   = '3'    # .-
g3[2][0b00]   = '4'    # ..
g3[2][0b10]   = '5'    # -.
g3[2][0b11]   = '6'    # --
g3[3][0b011]  = '7'    # .--
g3[3][0b001]  = '8'    # ..-
g3[3][0b000]  = '9'    # ...
g3[3][0b100]  = '0'    # -..
g3[3][0b110]  = '+'    # --.
g3[3][0b111]  = '-'    # ---
g3[3][0b101]  = '/'    # -.-
g3[3][0b010]  = '*'    # .-.
g3[4][0b0101] = Keycode.ENTER  # .-.-
g3[6][0b010101] = '.'  # .-.-.-

groups[3] = g3


############################################
# Group 4 — Scanning (Switch Control on iOS / Android)   [AeroMorse extra]
############################################
# Phone / tablet "Switch Control" scanning can be driven by keyboard keys.
# The 12 shortest codes are Enter, Space and F3–F12, so the two most-used
# scan actions (Select = Enter on a sip, Next = Space on a puff) take a
# single sip or puff.
g4 = init_group()

g4[1][0b0]   = Keycode.ENTER     # .
g4[1][0b1]   = Keycode.SPACE     # -
g4[2][0b00]  = Keycode.F3        # ..
g4[2][0b01]  = Keycode.F4        # .-
g4[2][0b10]  = Keycode.F5        # -.
g4[2][0b11]  = Keycode.F6        # --
g4[3][0b000] = Keycode.F7        # ...
g4[3][0b001] = Keycode.F8        # ..-
g4[3][0b010] = Keycode.F9        # .-.
g4[3][0b011] = Keycode.F10       # .--
g4[3][0b100] = Keycode.F11       # -..
g4[3][0b101] = Keycode.F12       # -.-

# ── Letters and numbers — same codes as Group 1. Change what is between the quotes. ──
g4[4][0b1000]='b'           # -...
g4[4][0b1010]='c'           # -.-.
g4[4][0b0010]='f'           # ..-.
g4[3][0b110]='g'            # --.
g4[4][0b0000]='h'           # ....
g4[4][0b0111]='j'           # .---
g4[4][0b0100]='l'           # .-..
g4[3][0b111]='o'            # ---
g4[4][0b0110]='p'           # .--.
g4[4][0b1101]='q'           # --.-
g4[4][0b0001]='v'           # ...-
g4[4][0b1001]='x'           # -..-
g4[4][0b1011]='y'           # -.--
g4[4][0b1100]='z'           # --..
g4[5][0b01111]='1'          # .----
g4[5][0b00111]='2'          # ..---
g4[5][0b00011]='3'          # ...--
g4[5][0b00001]='4'          # ....-
g4[5][0b00000]='5'          # .....
g4[5][0b10000]='6'          # -....
g4[5][0b11000]='7'          # --...
g4[5][0b11100]='8'          # ---..
g4[5][0b11110]='9'          # ----.
g4[5][0b11111]='0'          # -----

groups[4] = g4


############################################
# Group 5 — Media (USB HID Consumer Controls)   [AeroMorse extra]
############################################
#   .    PLAY_PAUSE         ..   VOLUME_DECREMENT    -.   PREVIOUS TRACK
#   -    MUTE               --   VOLUME_INCREMENT    .-   NEXT TRACK
#   ...  STOP               ..-  REWIND              .-.  FAST FORWARD
#   .--  BRIGHTNESS +       -..  BRIGHTNESS -        -.-  EJECT
# App launchers, on the first letter of each:
#   -.-.  C  Calculator        -...  B  Browser
#   ..-.  F  File explorer     .-..  L  mai-L (email)
g5 = init_group()

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

g5[4][0b1010] = _cc('AL_CALCULATOR',            0x192)   # -.-.  C  calculator
g5[4][0b0010] = _cc('AL_LOCAL_MACHINE_BROWSER', 0x194)   # ..-.  F  file explorer
g5[4][0b1000] = _cc('AL_INTERNET_BROWSER',      0x196)   # -...  B  web browser
g5[4][0b0100] = _cc('AL_EMAIL_READER',          0x18A)   # .-..  L  mai-L

# ── Letters and numbers — same codes as Group 1. Change what is between the quotes. ──
g5[3][0b110]='g'            # --.
g5[4][0b0000]='h'           # ....
g5[4][0b0111]='j'           # .---
g5[3][0b111]='o'            # ---
g5[4][0b0110]='p'           # .--.
g5[4][0b1101]='q'           # --.-
g5[4][0b0001]='v'           # ...-
g5[4][0b1001]='x'           # -..-
g5[4][0b1011]='y'           # -.--
g5[4][0b1100]='z'           # --..
g5[5][0b01111]='1'          # .----
g5[5][0b00111]='2'          # ..---
g5[5][0b00011]='3'          # ...--
g5[5][0b00001]='4'          # ....-
g5[5][0b00000]='5'          # .....
g5[5][0b10000]='6'          # -....
g5[5][0b11000]='7'          # --...
g5[5][0b11100]='8'          # ---..
g5[5][0b11110]='9'          # ----.
g5[5][0b11111]='0'          # -----

groups[5] = g5


############################################
# Groups 6, 7, 8 — YOUR groups (customise these)   [AeroMorse extra]
############################################
# Each starts with the letters and numbers on their Group 1 codes. To make a
# code do something else, change what is between the quotes on its line — or
# replace the quoted text with any of these:
#   a phrase          'My favourite string here'
#   a secret          _secret('mykey')          (then add mykey in AeroMorse Secrets)
#   a key             Keycode.ENTER             or a combination: Keycode.CONTROL, Keycode.C
#   an app launcher   _cc('AL_CALCULATOR', 0x192)
#   a command         'mclick left 1'           (see Group 2 for the commands)
# Reach a group with its Group 0 code:  g6 .....---   g7 ...-----   g8 ..------

# ── Group 6  (reach it with .....---) ─────────────────────────────────────────
g6 = init_group()
g6[2][0b01]='a'             # .-
g6[4][0b1000]='b'           # -...
g6[4][0b1010]='c'           # -.-.
g6[3][0b100]='d'            # -..
g6[1][0b0]='e'              # .
g6[4][0b0010]='f'           # ..-.
g6[3][0b110]='g'            # --.
g6[4][0b0000]='h'           # ....
g6[2][0b00]='i'             # ..
g6[4][0b0111]='j'           # .---
g6[3][0b101]='k'            # -.-
g6[4][0b0100]='l'           # .-..
g6[2][0b11]='m'             # --
g6[2][0b10]='n'             # -.
g6[3][0b111]='o'            # ---
g6[4][0b0110]='p'           # .--.
g6[4][0b1101]='q'           # --.-
g6[3][0b010]='r'            # .-.
g6[3][0b000]='s'            # ...
g6[1][0b1]='t'              # -
g6[3][0b001]='u'            # ..-
g6[4][0b0001]='v'           # ...-
g6[3][0b011]='w'            # .--
g6[4][0b1001]='x'           # -..-
g6[4][0b1011]='y'           # -.--
g6[4][0b1100]='z'           # --..
g6[5][0b01111]='1'          # .----
g6[5][0b00111]='2'          # ..---
g6[5][0b00011]='3'          # ...--
g6[5][0b00001]='4'          # ....-
g6[5][0b00000]='5'          # .....
g6[5][0b10000]='6'          # -....
g6[5][0b11000]='7'          # --...
g6[5][0b11100]='8'          # ---..
g6[5][0b11110]='9'          # ----.
g6[5][0b11111]='0'          # -----
groups[6] = g6

# ── Group 7  (reach it with ...-----) ─────────────────────────────────────────
g7 = init_group()
g7[2][0b01]='a'             # .-
g7[4][0b1000]='b'           # -...
g7[4][0b1010]='c'           # -.-.
g7[3][0b100]='d'            # -..
g7[1][0b0]='e'              # .
g7[4][0b0010]='f'           # ..-.
g7[3][0b110]='g'            # --.
g7[4][0b0000]='h'           # ....
g7[2][0b00]='i'             # ..
g7[4][0b0111]='j'           # .---
g7[3][0b101]='k'            # -.-
g7[4][0b0100]='l'           # .-..
g7[2][0b11]='m'             # --
g7[2][0b10]='n'             # -.
g7[3][0b111]='o'            # ---
g7[4][0b0110]='p'           # .--.
g7[4][0b1101]='q'           # --.-
g7[3][0b010]='r'            # .-.
g7[3][0b000]='s'            # ...
g7[1][0b1]='t'              # -
g7[3][0b001]='u'            # ..-
g7[4][0b0001]='v'           # ...-
g7[3][0b011]='w'            # .--
g7[4][0b1001]='x'           # -..-
g7[4][0b1011]='y'           # -.--
g7[4][0b1100]='z'           # --..
g7[5][0b01111]='1'          # .----
g7[5][0b00111]='2'          # ..---
g7[5][0b00011]='3'          # ...--
g7[5][0b00001]='4'          # ....-
g7[5][0b00000]='5'          # .....
g7[5][0b10000]='6'          # -....
g7[5][0b11000]='7'          # --...
g7[5][0b11100]='8'          # ---..
g7[5][0b11110]='9'          # ----.
g7[5][0b11111]='0'          # -----
groups[7] = g7

# ── Group 8  (reach it with ..------) ─────────────────────────────────────────
g8 = init_group()
g8[2][0b01]='a'             # .-
g8[4][0b1000]='b'           # -...
g8[4][0b1010]='c'           # -.-.
g8[3][0b100]='d'            # -..
g8[1][0b0]='e'              # .
g8[4][0b0010]='f'           # ..-.
g8[3][0b110]='g'            # --.
g8[4][0b0000]='h'           # ....
g8[2][0b00]='i'             # ..
g8[4][0b0111]='j'           # .---
g8[3][0b101]='k'            # -.-
g8[4][0b0100]='l'           # .-..
g8[2][0b11]='m'             # --
g8[2][0b10]='n'             # -.
g8[3][0b111]='o'            # ---
g8[4][0b0110]='p'           # .--.
g8[4][0b1101]='q'           # --.-
g8[3][0b010]='r'            # .-.
g8[3][0b000]='s'            # ...
g8[1][0b1]='t'              # -
g8[3][0b001]='u'            # ..-
g8[4][0b0001]='v'           # ...-
g8[3][0b011]='w'            # .--
g8[4][0b1001]='x'           # -..-
g8[4][0b1011]='y'           # -.--
g8[4][0b1100]='z'           # --..
g8[5][0b01111]='1'          # .----
g8[5][0b00111]='2'          # ..---
g8[5][0b00011]='3'          # ...--
g8[5][0b00001]='4'          # ....-
g8[5][0b00000]='5'          # .....
g8[5][0b10000]='6'          # -....
g8[5][0b11000]='7'          # --...
g8[5][0b11100]='8'          # ---..
g8[5][0b11110]='9'          # ----.
g8[5][0b11111]='0'          # -----
groups[8] = g8

# ── Group 9 — the SWITCH group (config.py SWITCH_GROUP = 9) ─────────────────────
# No Morse here: a sip holds SWITCH_SIP_KEY and a puff holds SWITCH_PUFF_KEY, so
# a code assigned to g9 could never be typed. None are defined. (Set
# SWITCH_GROUP = 0 in config.py to use Group 9 as an ordinary group instead.)
groups[9] = init_group()
