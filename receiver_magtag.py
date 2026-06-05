# receiver_magtag.py — AeroMorse wireless e-ink remote display (Option W3)
#
# ════════════════════════════════════════════════════════════════════════════
# ⚠  WARNING — CIRCUITPYTHON VERSION REQUIREMENT  ⚠
#
#   The updated Adafruit MagTag 2025 Edition (with SSD1680 e-ink driver)
#   WILL NOT WORK with CircuitPython 9.2.x or earlier. You MUST install
#   CircuitPython 10.x.x or later on the MagTag before this file will run.
#
#   More information: https://learn.adafruit.com/adafruit-magtag
# ════════════════════════════════════════════════════════════════════════════
#
# Hardware
#   Adafruit MagTag 2025 Edition (2.9" grayscale e-ink, ESP32-S2, SSD1680)
#       https://www.adafruit.com/product/4800
#
# Libraries required in /lib on this board (download from circuitpython.org/libraries
# bundle matching CircuitPython 10.x):
#   adafruit_magtag/
#   adafruit_display_text/
#   adafruit_bitmap_font/
#   adafruit_io/                   (used internally by adafruit_magtag)
#   adafruit_portalbase/           (same)
#   adafruit_fakerequests.mpy      (same)
#   adafruit_lis3dh.mpy            (onboard accelerometer; magtag library imports it)
#   neopixel.mpy
#   simpleio.mpy
#   (displayio, terminalio, wifi, espnow are built into CircuitPython)
#
# Setup
#   1. Flash CircuitPython 10.x onto the MagTag.
#   2. Copy the libraries above to /lib on the MagTag.
#   3. Copy the SAME boot.py from the sender to the MagTag. boot.py
#      auto-detects its role from whether /morse_map.py is present, so
#      it will correctly leave USB HID off on this receiver (you won't
#      copy morse_map.py here in step 4).
#   4. Copy this file to the MagTag as code.py. Do NOT copy
#      morse_map.py — its absence is what tells boot.py this is a
#      receiver.
#   5. Power on. The e-ink display shows "[ WAITING ]" until the main
#      AeroMorse board comes up, then mirrors the group / last action /
#      modifier status.
#
# Why this option exists
#   E-ink is much more readable from a distance than the small TFT on
#   the W1 receiver. Stays on with zero power draw between refreshes.
#   Trade-off: e-ink refresh is slow (~1–2 s per full refresh), so this
#   receiver intentionally drops two of the four fields the main board
#   broadcasts:
#       SHOWN:    group name, last action, modifier/status
#       DROPPED:  live Morse pattern preview, pressure bar
#   The pattern preview at 10 Hz simply can't be rendered on e-ink. For
#   live-preview viewing use Option W1 (a second #5691 colour TFT).
#
#   The four onboard NeoPixels show the GROUP COLOUR (blue=KEYBOARD,
#   green=MOUSE, orange=MACRO, magenta=SCANNING, yellow=MEDIA, etc.),
#   matching code.py's _GROUP_COLORS palette. So even though the e-ink
#   itself is grayscale, you can tell which mode the device is in at a
#   glance from across a room.
#
# Protocol (matches receiver.py — no main-board changes needed)
#   The main AeroMorse board broadcasts a pipe-separated UTF-8 string
#   over ESP-NOW once every 100 ms:
#       "<group_str>|<buf_str>|<action_str>|<mods_str>"
#   e.g. "[ KEYBOARD ]|. - .|HELLO|LEFT SHIFT"

import time
import wifi
import espnow
import terminalio
import displayio
from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag

# ── Group palette (mirrors code.py / receiver.py) ────────────────────────────
_GROUP_NAMES  = ("BASE", "KEYBOARD", "MOUSE", "MACRO", "SCANNING",
                 "MEDIA", "GROUP 6", "GROUP 7", "GROUP 8", "GROUP 9")
_GROUP_COLORS = (0x606060, 0x0080FF, 0x00C040, 0xFF8000, 0xFF00FF,
                 0xFFFF00, 0x00FFFF, 0xFF0080, 0x8000FF, 0xFF4000)

def _group_idx(group_str):
    """Match incoming '[ NAME ]' against the names list."""
    for i, n in enumerate(_GROUP_NAMES):
        if n in group_str:
            return i
    return 0


# ── ESP-NOW ──────────────────────────────────────────────────────────────────
wifi.radio.enabled = True
e = espnow.ESPNow()


# ── MagTag display setup ─────────────────────────────────────────────────────
# 2.9" e-ink — 296 × 128 px, monochrome (black on white).
magtag = MagTag()
display = magtag.graphics.display

# Three large text labels — no pattern preview, no pressure bar.
# Layout (296 × 128 px landscape):
#   Row 1  y= 12   group name        (scale 3 — largest)
#   Row 2  y= 60   last action       (scale 2)
#   Row 3  y= 100  modifiers/status  (scale 2)
_root = displayio.Group()

# White background (e-ink "white" is the unwritten background)
_bg_bmp = displayio.Bitmap(display.width, display.height, 1)
_bg_pal = displayio.Palette(1)
_bg_pal[0] = 0xFFFFFF
_root.append(displayio.TileGrid(_bg_bmp, pixel_shader=_bg_pal))

def _mklbl(text, y, scale):
    lbl = label.Label(
        terminalio.FONT, text=text, color=0x000000, scale=scale,
        anchor_point=(0.5, 0.0),
        anchored_position=(display.width // 2, y),
    )
    _root.append(lbl)
    return lbl

_lbl_group  = _mklbl("[ WAITING ]", 12,  3)
_lbl_action = _mklbl(" ",           60,  2)
_lbl_mods   = _mklbl(" ",          100,  2)

display.root_group = _root


# ── Helpers ──────────────────────────────────────────────────────────────────
_MAX_CHARS = 20      # match the cap used on the main board

def _clip(s):
    s = s.strip()
    return s[:_MAX_CHARS] if s else " "

def _set_pixels(color):
    """Set all 4 onboard NeoPixels to the same colour (group indicator)."""
    for i in range(4):
        magtag.peripherals.neopixels[i] = color

def _force_refresh():
    """Drive a full e-ink refresh, ignoring rate-limit cooldowns."""
    while True:
        try:
            display.refresh()
            return
        except RuntimeError:
            # Display still cooling down from the previous refresh; wait.
            time.sleep(0.5)


# ── Refresh throttle ─────────────────────────────────────────────────────────
# Full e-ink refresh on the SSD1680 takes ~1–2 s and visually flashes the
# panel. Throttling to once every REFRESH_MIN_INTERVAL seconds means a fast
# stream of letters won't queue 50 refreshes — only the LAST state at the
# moment the throttle expires gets drawn.
REFRESH_MIN_INTERVAL = 2.0       # seconds — never refresh more often
NO_SIGNAL_TIMEOUT    = 10.0      # seconds before showing "[ NO SIGNAL ]"

# Show initial state on screen.
_set_pixels(0x000000)
_force_refresh()

_last_refresh    = time.monotonic()
_last_rx         = time.monotonic()
_pending_refresh = True            # ensure the first received packet draws
_last_shown      = ("", "", "")    # (group, action, mods) currently rendered
_no_signal_shown = False


# ── Main loop ────────────────────────────────────────────────────────────────
while True:
    now = time.monotonic()

    # Drain all queued ESP-NOW packets (only keep latest state).
    while True:
        pkt = e.read()
        if pkt is None:
            break
        try:
            parts = pkt.msg.decode().split("|")
        except Exception:
            continue
        if len(parts) < 4:
            continue
        _last_rx = now
        _no_signal_shown = False
        new_shown = (_clip(parts[0]), _clip(parts[2]), _clip(parts[3]))
        # parts[1] = live Morse buffer — INTENTIONALLY DROPPED (too fast for e-ink)
        if new_shown != _last_shown:
            _last_shown = new_shown
            _pending_refresh = True

    # If we have a pending change AND the throttle has elapsed, redraw.
    if _pending_refresh and (now - _last_refresh) >= REFRESH_MIN_INTERVAL:
        g, a, m = _last_shown
        _lbl_group.text  = g if g.strip() else "[ -- ]"
        _lbl_action.text = a if a.strip() else " "
        _lbl_mods.text   = m if m.strip() else " "
        _set_pixels(_GROUP_COLORS[_group_idx(g)])
        try:
            display.refresh()
            _last_refresh = now
            _pending_refresh = False
        except RuntimeError:
            # Cooldown — try again next loop. _pending_refresh stays True.
            pass

    # No-signal detection (e-ink stays at last good state; pixels go black).
    if (now - _last_rx) > NO_SIGNAL_TIMEOUT and not _no_signal_shown:
        _no_signal_shown = True
        _lbl_group.text  = "[ NO SIGNAL ]"
        _lbl_action.text = "Out of range?"
        _lbl_mods.text   = " "
        _set_pixels(0x000000)
        _force_refresh()
        _last_refresh = time.monotonic()
        _last_shown   = ("[ NO SIGNAL ]", "Out of range?", " ")

    time.sleep(0.05)
