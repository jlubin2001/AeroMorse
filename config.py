# AeroMorse — User Configuration
#
# AeroMorse config.py — version 1.29 (released 2026-10-10)
# Official source (always get the latest here): https://github.com/jlubin2001/AeroMorse
#
# Edit a value, save, and the Feather auto-reloads. You should not need to
# open code.py.
#
# Each setting has a one-line hint here. For the full explanation (what it
# does, what other values mean, when to change it) see the Key Settings
# table in **Build Guide §10 Configuration** — every setting in this file
# has a row in that table, with the same name.

import board   # board.D5 / D6 / A0 referenced below


# ── True/False are case-insensitive ───────────────────────────────────────
# Python normally only accepts True / False (capitalised). These aliases let
# you also write true, false, TRUE, or FALSE for any on/off setting below, so
# a value like  USE_WIRELESS_DISPLAY = false  works instead of crashing the
# board. (Do NOT put quotes around it — "false" in quotes is text, not off.)
true  = TRUE  = True
false = FALSE = False


# ── DEVICE NAME — what the computer calls this AeroMorse ─────────────────
# Shown in Windows Settings > Bluetooth & devices (and similar lists on
# other computers) instead of "Feather ESP32-S3 Reverse TFT". Handy when you
# have more than one, e.g. "AeroMorse Green" and "AeroMorse Blue".
# Letters, digits, spaces and basic punctuation, up to 40 characters, in quotes.
# Takes effect after you UNPLUG and replug the device (not on save). If
# Windows still shows the old name, remove the device in that list and replug.

DEVICE_NAME = "AeroMorse"


# ── INPUT — sensor / switches / thresholds ────────────────────────────────

USE_SENSOR        = True      # True = LPS33HW sensor; False = AT switches on D5/D6
THRESH_SIP        = 2         # hPa below baseline = dot (raise if false triggers)
THRESH_PUFF       = 2         # hPa above baseline = dash
DEBOUNCE_SAMPLES  = 3         # consecutive agreeing readings to confirm a state change (a few ms each)
BASELINE_DRIFT_S  = 30        # auto-zero: follows slow ambient pressure drift while idle; 0 disables.
                              # (Nominal seconds; in practice it settles in roughly a quarter of that.)

# Split on a dip — for two quick sips or puffs in a row that run together
# (p .--. comes out as r .-.,  space ..-- as w .--). A sip/puff that drops
# below REPEAT_SPLIT_PCT % of its peak and then climbs again by 1 hPa is
# counted as two. Try 60. 0 = off.
REPEAT_SPLIT_PCT  = 0         # 0 = off; 60 = split when it dips below 60 % of its peak

# Diagnostics — for tracking down "it types badly until I restart it". Every
# DIAG_LOG_S seconds one "DIAG ..." line of timing figures goes to the USB
# serial log (nothing is typed on the computer). The first / worst / last
# line are saved on `devicereset`, and by themselves every 5 minutes while
# you type, so they survive an unplug; the next run prints them as
# "DIAG PREV ...". Switch it off again (0) once the problem is found.
DIAG_LOG_S        = 0         # 0 = off; 10 = one line every 10 seconds

DOT_PIN           = board.D5  # switch-mode only — TIP of dot jack
DASH_PIN          = board.D6  # switch-mode only — TIP of dash jack


# ── INPUT MODE — 1 / 2 / 3 switch ─────────────────────────────────────────
# 1 = single-switch timed,  2 = paddle (default),  3 = paddle + explicit Accept

SWITCH_MODE          = 2
ONE_SWITCH_INPUT     = "dot"        # mode 1 only — "dot" or "dash" (any case)
ONE_SWITCH_DOT_MS    = 200          # mode 1 only — press ≤ this ms = dot, longer = dash
THIRD_SWITCH_GESTURE = "long_dash"  # mode 3 only — "long_dash" or "long_dot" = Accept (any case)


# ── STRONG SIP / STRONG PUFF — distinct gesture for group jumps or actions ─
# Sensor mode: peak pressure ≥ THRESH_*_STRONG fires the action.
# Switch mode: long-press of the corresponding switch fires the action,
#              and overrides LONG_PRESS_CYCLES_GROUP on that switch.
# Set ACTION = "" to disable.

STRONG_SIP_ACTION  = "group 2"        # e.g. "group 2" to jump to Mouse on strong sip (any case)
STRONG_PUFF_ACTION = "group 1"        # e.g. "group 1" to jump to Keyboard on strong puff (any case)
THRESH_SIP_STRONG  = 15        # hPa — sensor mode only
THRESH_PUFF_STRONG = 15        # hPa — sensor mode only
STRONG_OFF_IN_GROUPS = (4,)    # groups where strong sip/puff is OFF — a hard sip/puff
                               # there is just a normal dot/dash. (4,) = Scanning, so a
                               # hard sip/puff can't knock you out of Switch Control.
                               # e.g. (4, 3) for several groups, () = on everywhere.
# A strong sip/puff only counts as the FIRST breath of a code; in the middle of
# a code a hard sip/puff is just a normal dot/dash (so ---.- with a hard sip works).


# ── SWITCH GROUP — sip / puff act like two plain switches ─────────────────
# In this group there is no Morse: a sip presses SWITCH_SIP_KEY and a puff
# presses SWITCH_PUFF_KEY the moment it starts, and HOLDS the key down until
# the sip/puff ends — for switch-accessible games and scanning apps (e.g.
# Benny's Hub: Space = move, Enter = select) that need a key held.
# Get there with its Group 0 code (Group 9: .-------). It goes back to
# SWITCH_EXIT_GROUP BY ITSELF after SWITCH_IDLE_EXIT_S seconds with no sip or
# puff — just stop and wait when you're done. (Or hold one puff for
# SWITCH_EXIT_PUFF_S seconds.) Hard or long sips/puffs never leave it otherwise.

SWITCH_GROUP      = 9          # group number to use as the Switch group; 0 = none
                               # (9 = the last group since v1.24; it was 7 before)
SWITCH_SIP_KEY    = "ENTER"    # key held while sipping  (a Keycode name)
SWITCH_PUFF_KEY   = "SPACE"    # key held while puffing  (a Keycode name)
SWITCH_IDLE_EXIT_S = 20        # seconds with no sip/puff before leaving by itself (0 = never)
SWITCH_EXIT_PUFF_S = 5.0       # or hold one puff this many seconds to leave
SWITCH_EXIT_GROUP = 1          # group to go to when leaving (1 = Keyboard)
SWITCH_COUNTDOWN_S = 10       # show e.g. "KEYBOARD IN 5" for the last N seconds before leaving (0 = off)


# ── TIMING ────────────────────────────────────────────────────────────────

ACCEPT_DELAY      = 0.3        # idle seconds before pattern commits (sip-puff often 0.3–0.7; lower = faster)
MOUSE_ACCEPT_DELAY = 0.15      # like ACCEPT_DELAY but ONLY in Group 2 (mouse): shorter
                              # so clicks fire sooner, while keyboard typing keeps
                              # ACCEPT_DELAY. Must stay above your gap BETWEEN the
                              # symbols of a pattern or mouse patterns split. Lower =
                              # snappier clicks. Delete this line to disable (mouse
                              # then uses ACCEPT_DELAY like everything else).
LONG_PRESS        = 1.0        # seconds to hold for cycle / Accept gesture


# ── CODE REPEAT (Darci-style hold-to-repeat) ──────────────────────────────
# When CODE_REPEAT = True, holding DIT or DAH emits one symbol per repeat
# interval. SWITCH_MODE = 2 only.

CODE_REPEAT             = False    # True = Darci-style hold-to-repeat
DOT_REPEAT_MS           = 200      # ms per auto-repeated dot
DASH_REPEAT_MS          = 600      # ms per auto-repeated dash (~3× dot)
CODE_REPEAT_MAX         = 8        # cap on symbols per held stream
LONG_PRESS_CYCLES_GROUP = True     # False with CODE_REPEAT = True; cycle via g0 codes instead


# ── AUDIO — speaker pitches (Hz) and blip durations (s) ───────────────────

USE_SPEAKER       = True       # False = the device's own speaker / buzzer stays silent.
                               # Sound through the computer (PC_SOUND, below) is separate. (v1.29+)
AUDIO_PIN         = board.A0

BEEP_DOT_FREQ     = 1200       # dot (sip) sidetone — higher pitch
BEEP_DASH_FREQ    =  800       # dash (puff) sidetone — lower pitch
CONFIRM_FREQ      = 1050       # short blip when an action fires
GROUP_FREQ        =  550       # short blip on group change

BEEP_CONFIRM_S    = 0.06       # confirm-blip duration
BEEP_GROUP_S      = 0.14       # group-change blip duration


# ── MOUSE — group-2 movement speeds and repeat tick ───────────────────────
# Effective pixels per step = raw direction × SPEED × MOUSE_SPEED_FACTOR

MOUSE_SPEED_NORMAL = 2         # default speed in group 2
MOUSE_SPEED_SLOW   = 1         # toggled via `mslow`
MOUSE_SPEED_FAST   = 3         # toggled via `mfast`
MOUSE_SPEED_FACTOR = 2         # overall scale
MOUSE_REPEAT_DELAY = 0.040     # seconds between repeat ticks

MOUSE_CLICK_MOD_DELAY = 0.030  # s to settle a modifier before/after a click
MOUSE_CLICK_KEEPS_MODS = True  # True = armed mods survive a click (Ctrl+click
                               # multi-select); False = one-shot, cleared after
MOUSE_CLICK_HOLD = 0.060       # s to hold the button down per click. 0 = instant
                               # press/release, which Windows scrollbar tracks &
                               # some controls ignore; ~60 ms registers reliably
MOUSE_CLICK_GAP  = 0.040       # s between the two clicks of a double-click


# ── REPEAT EXCLUSIONS ─────────────────────────────────────────────────────
# Keys that must NEVER auto-repeat, listed by adafruit_hid Keycode name.
# Pressing `repeat` right after one of these does nothing (repeat needs a
# repeatable action first). Page keys are here because an accidental repeat
# scrolls far past where you were and you lose your place. Add others you
# don't want to repeat, e.g. "HOME", "END", "ESCAPE", "TAB". Arrow keys are
# intentionally NOT here — arrow + repeat is the preferred way to scroll.
# A key combination can be listed too: join the names with +, e.g. "ALT+TAB"
# or "GUI+TAB". That blocks exactly that combination (keys in any order); the
# same keys on their own still follow the single-key entries.
NO_REPEAT_KEYS = ("PAGE_UP", "PAGE_DOWN")


# ── SECRETS — PIN-locked passwords (macro_secrets.enc) ────────────────────
# Only used when macro_secrets.enc (made with the AeroMorse Secrets PC tool) is
# on the device. It is always locked at power-up; this adds an idle auto-lock.

SECRETS_AUTOLOCK_MIN = 0       # minutes with no sip/puff before secrets re-lock;
                               # 0 = stay unlocked until power-off or `lock` (Macro L)


# ── DISPLAY / WIRELESS ────────────────────────────────────────────────────

USE_DISPLAY          = True    # True = this board has a built-in screen (the default
                              # #5691 Reverse TFT). Set False for a board with NO
                              # screen (e.g. an ESP-NOW sender): the device still
                              # types and still broadcasts to a wireless receiver;
                              # only the local screen is skipped. (A missing screen
                              # is also auto-detected, so a screenless board won't
                              # crash even if this is left True.)
                              # Also set False if the board HAS a screen but you
                              # only watch the wireless display: the built-in
                              # screen is blanked and its backlight switched off,
                              # which removes screen-drawing pauses of 60-100 ms
                              # that can swallow a quick sip or puff (v1.22+).
DISPLAY_BRIGHTNESS   = 1.0      # screen backlight: 0.1 (dim) to 1.0 (full); applies on save
DISPLAY_ROTATION     = 0       # degrees: 0 = USB left, 180 = USB right (also 90, 270)
USE_WIRELESS_DISPLAY = False   # True = ESP-NOW broadcast to a wireless receiver (adds ~80–100 mA, ESP32-only). Set True only if you have a receiver.
ESPNOW_CHANNEL       = 1        # WiFi channel (1–13) — display's receiver_config.py ESPNOW_CHANNEL must match
KEYBOARD_LAYOUT      = "US"    # the keyboard layout the COMPUTER is set to. "US" needs nothing extra.
                              # If symbols come out wrong (@ and " swapped, # giving a pound sign ...)
                              # the computer uses another layout: copy that layout's file into /lib
                              # and name it here, e.g. "win_uk", "win_de", "win_fr" (v1.28+; see the
                              # Build Guide, Appendix I). Missing or faulty file = US is used.
PC_DISPLAY           = False   # True = also report the display to the "AeroMorse Display" window on the
                              # computer, over the USB cable (v1.26+). No extra hardware. Leave False
                              # unless you use that program.
PC_SOUND             = False   # True = the same program also plays the beeps (a tone for each dot and
                              # dash, a blip when an action fires) through the COMPUTER's speakers —
                              # for a device with no speaker. Needs PC_DISPLAY = True, and "Sound"
                              # switched on in the program's right-click menu.
