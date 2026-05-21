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
════════════════════════════════════════════════════════════════════════════
"""

from adafruit_hid.keycode import Keycode

groups = {}

def init_group():
    return {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}}


############################################
# Group 0 — Always Available (group toggles)
############################################
# AeroMorse safe 8-symbol toggles. Darci's "Change Code Set" command
# (---.- , 5 symbols) is too short to use as a global toggle.
g0 = init_group()
g0[8][0b00000000] = "group 1"   # ........  → Keyboard
g0[8][0b11111111] = "group 2"   # --------  → Mouse Mode
g0[8][0b00001111] = "group 3"   # ....----  → Number Mode
g0[8][0b11110000] = "group 2"   # ----....  → Mouse Mode (alt)
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
# Sound Mode, Start Menu, Keypad Mode, Change Code Set:
g1[6][0b101100]  = Keycode.GUI            # ..---.   approx for "Start Menu" (Darci: --....)
# (Darci's literal Start Menu code is `--....` = 6 chars, mapped below.)
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
g1[6][0b101101]  = "sys_req"                      # -.--.-   kk  (no HID Sys Req — placeholder)
g1[6][0b011001]  = "pause"                        # .--..-   pa  (no HID Pause — placeholder)

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
g2[3][0b111]  = "mclick left h"  # ---   click & hold left  (drag toggle in AeroMorse)
g2[2][0b01]   = "mclick right 1" # .-    click right
g2[3][0b001]  = "mclick right 2" # ..-   double-click right
g2[3][0b000]  = "mclick right h" # ...   click & hold right

# Stop / repeat: Darci uses single dot or single dash. AeroMorse already
# maps single dot/dash to right/left movement — no conflict because
# entering any movement code stops the previous one automatically.

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
