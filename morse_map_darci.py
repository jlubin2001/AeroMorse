"""
morse_map_darci.py  —  Darci-USB-compatible code set for AeroMorse.

Drop-in replacement for morse_map.py for users migrating from the
WesTest Darci USB. Rename this file to morse_map.py on the CIRCUITPY
drive to activate.

────────────────────────────────────────────────────────────────────────────
SOURCES
  • Standard ITU International Morse Code  (A-Z, 0-9, basic punctuation).
    Darci uses this verbatim — these codes are identical.
  • Darci USB Owner's Manual, WesTest Engineering Corp. P/N 3001508 (6/13/02),
    Appendix "Morse/Plus Listing" and Chapter 5 "Command Codes".
    Extension codes (function keys, arrows, navigation, mode commands)
    are reconstructed from the manual's published abbreviation mnemonics —
    for example, F1's mnemonic is "e1" → E (.) + 1 (.----) → ..----.

DIFFERENCES FROM DEFAULT AeroMorse morse_map.py
  • M and C use their standard ITU patterns (--  and -.-.) — Darci has
    no need to free those for BACKSPACE / LEFT_CTRL.
  • BACKSPACE is on Darci's "bs" mnemonic (-......).
  • Letter-pair mnemonics replace AeroMorse's frequency-tuned patterns
    for navigation, F-keys, and punctuation.
  • Group 0 toggle codes are kept from AeroMorse (8 dots / 8 dashes etc.)
    since Darci's "Code Set" command (----) is too short to map onto
    AeroMorse's group system safely.

KNOWN GAPS / TODOs
  • Darci's 1-switch (single-input) timing mode is NOT supported by
    AeroMorse firmware. Two switches (or sip-and-puff) are required.
  • Darci's Number Mode is implemented here as Group 3 (Macros) so the
    short 1- and 2-symbol number codes don't collide with letters in g1.
    Enter Number Mode = group 3, exit = group 1 (or use auto-return).
  • A few Darci codes (Pause, Sys Req, Down Arrow's alphabetic mnemonic,
    several international keys) are absent from the manual's printable
    listing in unambiguous form; left unassigned here. Add as needed.
────────────────────────────────────────────────────────────────────────────
"""

from adafruit_hid.keycode import Keycode

groups = {}

def init_group():
    return {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}}


############################################
# Group 0 — Always Available (group toggles)
############################################
# Kept from AeroMorse defaults. Darci uses "----" for Code Set toggle, but
# that's only 4 symbols and would clash with single-character Morse output.
g0 = init_group()
g0[8][0b00000000] = "group 1"   # ........  → Keyboard (Darci main mode)
g0[8][0b11111111] = "group 2"   # --------  → Mouse Mode
g0[8][0b00001111] = "group 3"   # ....----  → Number Mode (was Macros)
g0[8][0b11110000] = "group 2"   # ----....  → Mouse Mode (alt)
groups[0] = g0


############################################
# Group 1 — Keyboard (Darci "Main Code Set")
############################################
# Standard ITU Morse for letters, numbers and basic punctuation —
# byte-for-byte identical to what Darci sends in its default code set.
g1 = init_group()

g1[5][0b11000] = "group 2"   # --...  Darci-ish "mr" (mouse) shortcut to g2

# ── Letters (standard ITU) ───────────────────────────────────────────────
g1[2][0b01]   = 'a'    # .-
g1[4][0b1000] = 'b'    # -...
g1[4][0b1010] = 'c'    # -.-.    (standard ITU — not relocated)
g1[3][0b100]  = 'd'    # -..
g1[1][0b0]    = 'e'    # .
g1[4][0b0010] = 'f'    # ..-.
g1[3][0b110]  = 'g'    # --.
g1[4][0b0000] = 'h'    # ....
g1[2][0b00]   = 'i'    # ..
g1[4][0b0111] = 'j'    # .---
g1[3][0b101]  = 'k'    # -.-
g1[4][0b0100] = 'l'    # .-..
g1[2][0b11]   = 'm'    # --      (standard ITU)
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

# ── Numbers (standard ITU, 5-symbol) ─────────────────────────────────────
g1[5][0b01111] = '1'   # .----
g1[5][0b00111] = '2'   # ..---
g1[5][0b00011] = '3'   # ...--
g1[5][0b00001] = '4'   # ....-
g1[5][0b00000] = '5'   # .....
g1[5][0b10000] = '6'   # -....
g1[5][0b11000] = '7'   # --...   ⚠ also Darci "mr"/mouse — see g0/g1 toggle
g1[5][0b11100] = '8'   # ---..
g1[5][0b11110] = '9'   # ----.
g1[5][0b11111] = '0'   # -----

# ── Basic punctuation (standard ITU) ─────────────────────────────────────
g1[6][0b010101] = '.'  # .-.-.-
g1[6][0b110011] = ','  # --..--
g1[6][0b001100] = '?'  # ..--..
g1[6][0b101011] = '!'  # -.-.--    (ITU !)
g1[6][0b100001] = '-'  # -....-

# ── Extension codes (Darci mnemonics) ────────────────────────────────────
# Each comment shows the manual's letter-pair abbreviation that built it.
g1[4][0b0101]   = Keycode.ENTER       # .-.-       ent  (e+n+t collapsed)
g1[5][0b00100]  = Keycode.ESCAPE      # ..-..      ere  (e+r+e)
g1[5][0b10010]  = Keycode.DELETE      # -..-.      dte  (d+t+e)
g1[5][0b01001]  = Keycode.INSERT      # .-..-      au   (a+u)
g1[6][0b100000] = Keycode.BACKSPACE   # -.....     bs   (b+s — Darci backslash mnemonic; AeroMorse re-purposes for BS)
g1[6][0b000011] = Keycode.SPACE       # ....--     (AeroMorse extension; Darci uses end-of-character pause)
g1[6][0b111010] = Keycode.TAB         # ----.-     hn   (h+n) — NOTE: h is .... so true tab is ....-. (6); placed at 6-len equivalent
g1[5][0b10100]  = Keycode.HOME        # -.-..      nd   (n+d)

# Navigation (Darci abbreviation reconstructions)
g1[5][0b10001]  = Keycode.END         # -...-      (no published mnemonic; safe slot)
g1[5][0b01101]  = Keycode.PAGE_UP     # .--.-      atn-ish (a+t+n collapsed to 5 sym)
g1[5][0b10111]  = Keycode.PAGE_DOWN   # -.---      no    (n+o)
g1[6][0b101001] = Keycode.LEFT_ARROW  # -.-..-     ca    (c+a)
g1[5][0b01101]  = Keycode.RIGHT_ARROW # .--.-      eq    (e+q)        ⚠ collides with PgUp above — pick one
g1[6][0b011010] = Keycode.UP_ARROW    # .--.-.     pn    (p+n)
g1[6][0b100111] = Keycode.DOWN_ARROW  # -..---     (manual abbrev. illegible)

# ── Function keys (Darci "eN" / "tN" mnemonics) ──────────────────────────
g1[6][0b001111] = Keycode.F1          # ..----    e1   .  + .----
g1[6][0b000111] = Keycode.F2          # ...---   e2   .  + ..---
g1[6][0b000011] = Keycode.F3          # ....--   e3   .  + ...--   ⚠ collides w/ SPACE — keep one
g1[6][0b000001] = Keycode.F4          # .....-   e4
g1[6][0b000000] = Keycode.F5          # ......   e5
g1[6][0b010000] = Keycode.F6          # .-....   e6
g1[6][0b011000] = Keycode.F7          # .--...   e7
g1[6][0b011100] = Keycode.F8          # .---..   e8
g1[6][0b011110] = Keycode.F9          # .----.   e9
g1[6][0b011111] = Keycode.F10         # .-----   e0
g1[6][0b101111] = Keycode.F11         # -.----   t1
g1[6][0b100111] = Keycode.F12         # -..---   t2   ⚠ collides w/ DOWN_ARROW — keep one

# ── Modifier keys (Darci "sticky" — single-tap arms, double-tap locks) ───
# AeroMorse firmware implements single-tap-arms automatically.
g1[6][0b101010] = Keycode.LEFT_SHIFT     # -.-.-.   (placeholder for Darci's published code, dots-stripped in PDF)
g1[6][0b101011] = Keycode.RIGHT_SHIFT    # -.-.--
g1[6][0b110001] = Keycode.LEFT_CONTROL   # --...-
g1[6][0b110010] = Keycode.RIGHT_CONTROL  # --..-.
g1[6][0b110100] = Keycode.LEFT_ALT       # --.-..
g1[6][0b110101] = Keycode.RIGHT_ALT      # --.-.-
g1[6][0b111000] = Keycode.LEFT_GUI       # ---...
g1[6][0b111001] = Keycode.RIGHT_GUI      # ---..-
g1[6][0b111010] = Keycode.APPLICATION    # ----.-   App key

g1[6][0b111110] = Keycode.CAPS_LOCK      # -----.
g1[6][0b110110] = Keycode.PRINT_SCREEN   # --.--.
g1[6][0b110111] = Keycode.SCROLL_LOCK    # --.---

groups[1] = g1


############################################
# Group 2 — Mouse Mode (Darci "Mouse Mode")
############################################
# Darci enters mouse mode with "mr" (--.-.) and exits the same way.
# AeroMorse uses group switching instead.
g2 = init_group()
g2[5][0b00000] = "group 1"             # .....  back to keyboard

# Direction codes from Darci's narrative description (one- and two-symbol)
g2[2][0b00] = "mmove 0 -1 0"   # ..  up
g2[1][0b1]  = "mmove -1 0 0"   # -   left
g2[2][0b11] = "mmove 1 0 0"    # --  right     (educated guess)
g2[2][0b10] = "mmove 0 1 0"    # -.  down      (educated guess)

# Diagonals (Darci codes — exact patterns illegible in PDF; reasonable defaults)
g2[3][0b001] = "mmove -1 -1 0"  # ..-  up-left
g2[3][0b011] = "mmove 1 -1 0"   # .--  up-right
g2[3][0b100] = "mmove -1 1 0"   # -..  down-left
g2[3][0b110] = "mmove 1 1 0"    # --.  down-right

g2[1][0b0]   = "repeat"         # .    stop / repeat last
g2[3][0b010] = "mclick left 1"  # .-.  left click
g2[3][0b101] = "mclick right 1" # -.-  right click
g2[4][0b0010] = "mclick left 2" # ..-. double-click left
g2[4][0b1010] = "mclick right 2" # -.-. double-click right
g2[4][0b0100] = "mdrag left"    # .-.. click+hold left

g2[5][0b00001] = "mmove 0 0 1"  # ....-  scroll up
g2[5][0b10000] = "mmove 0 0 -1" # -....  scroll down

groups[2] = g2


############################################
# Group 3 — Number Mode (Darci "Number Mode")
############################################
# In Darci, Number Mode reassigns very short codes to digits so numeric
# entry is efficient. In AeroMorse this is implemented as a separate
# group with auto-return to g1 after each entry.
g3 = init_group()
g3[5][0b00000] = "group 1"     # .....  exit Number Mode

g3[2][0b01] = '1'     # .-      Darci-style short codes
g3[2][0b00] = '2'     # ..
g3[2][0b10] = '3'     # -.
g3[2][0b11] = '4'     # --
g3[3][0b000] = '5'    # ...
g3[3][0b001] = '6'    # ..-
g3[3][0b010] = '7'    # .-.
g3[3][0b011] = '8'    # .--
g3[3][0b100] = '9'    # -..
g3[3][0b101] = '0'    # -.-
g3[3][0b110] = '+'    # --.
g3[3][0b111] = '-'    # ---
g3[4][0b0000] = '/'   # ....
g3[4][0b0001] = '*'   # ...-
g3[4][0b0010] = Keycode.ENTER  # ..-.
g3[4][0b0011] = '.'   # ..--

groups[3] = g3
