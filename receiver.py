# receiver.py — AeroMorse wireless mirror display
#
# Hardware
#   Adafruit ESP32-S3 Reverse TFT Feather   https://www.adafruit.com/product/5691
#   (same board as the main AeroMorse unit — no extra display hardware needed)
#
# Libraries required in /lib on this board
#   adafruit_display_text/label.mpy
#   (displayio, terminalio, wifi, espnow are built into CircuitPython 9.x)
#
# Setup
#   1. Flash CircuitPython 9.x onto the second Feather.
#   2. Copy your existing /lib folder from the main board — no new files needed.
#   3. Copy receiver_boot.py to this board as boot.py
#      (skips USB HID so Windows does not see it as a second keyboard).
#   4. Copy this file to the board as code.py.
#   5. Power on — the display shows "Waiting" until the main board comes up.
#
# Protocol
#   The main AeroMorse board broadcasts a pipe-separated UTF-8 string over
#   ESP-NOW once every 100 ms (10 Hz), matching the TFT refresh rate:
#       "<group_str>|<buf_str>|<action_str>|<mods_str>"
#   e.g. "[ Keyboard ]|. - .|\"hello world\"|Shift"
#   No pairing required — any AeroMorse board on the same channel is accepted.

import time
import board
import displayio
import terminalio
import wifi
import espnow

from adafruit_display_text import label

# ── ESP-NOW ────────────────────────────────────────────────────────────────────
# WiFi radio must be enabled for ESP-NOW; no network connection is needed.

wifi.radio.enabled = True
e = espnow.ESPNow()     # receives from any sender — no peer registration needed

# ── Display ────────────────────────────────────────────────────────────────────
# Mirrors the main board TFT layout exactly: same 4 rows, same colours,
# same group indicator colours.  Pressure bar omitted (no sensor on this board).
#
# Layout on the 240 × 135 px TFT:
#   Row 1  y=  2   group name          (large, group-coloured)
#   Row 2  y= 30   morse buffer        (cyan)
#   Row 3  y= 58   last action         (yellow)
#   Row 4  y= 86   modifiers / status  (orange)

_GROUP_NAMES  = ("Base", "Keyboard", "Mouse", "Macro", "F-Keys",
                 "Group 5", "Group 6", "Group 7", "Group 8", "Group 9")
_GROUP_COLORS = (0x606060, 0x0080FF, 0x00C040, 0xFF8000, 0xFF00FF,
                 0xFFFF00, 0x00FFFF, 0xFF0080, 0x8000FF, 0xFF4000)

display = board.DISPLAY

def _make_label(root, text, color, y):
    lbl = label.Label(
        terminalio.FONT, text=text, color=color, scale=2,
        anchor_point=(0.5, 0.0),
        anchored_position=(display.width // 2, y),
    )
    root.append(lbl)
    return lbl

def _build_display():
    root = displayio.Group()

    bmp = displayio.Bitmap(display.width, display.height, 1)
    pal = displayio.Palette(1)
    pal[0] = 0x000020
    root.append(displayio.TileGrid(bmp, pixel_shader=pal))

    lbl_group  = _make_label(root, "[ AeroMorse ]", _GROUP_COLORS[1],  2)
    lbl_buf    = _make_label(root, "Waiting...",    0x00FFFF,          30)
    lbl_action = _make_label(root, " ",             0xFFFF00,          58)
    lbl_mods   = _make_label(root, " ",             0xFF8000,          86)

    display.root_group = root
    return lbl_group, lbl_buf, lbl_action, lbl_mods

_lbl_group, _lbl_buf, _lbl_action, _lbl_mods = _build_display()

# ── Helpers ────────────────────────────────────────────────────────────────────

_MAX_CHARS = 20   # matches the 20-char cap used on the main board

def _clip(s):
    """Trim to display width; return a space if empty so the label stays valid."""
    s = s.strip()
    return s[:_MAX_CHARS] if s else " "

def _group_color(group_str):
    """Return the colour for the group name label based on the received string."""
    for idx, name in enumerate(_GROUP_NAMES):
        if name in group_str:
            return _GROUP_COLORS[idx]
    return _GROUP_COLORS[0]

def _show_no_signal():
    _lbl_group.text  = "[ No signal ]"
    _lbl_group.color = 0x606060
    _lbl_buf.text    = " "
    _lbl_action.text = "Out of range?"
    _lbl_mods.text   = " "

# ── Main loop ──────────────────────────────────────────────────────────────────

_last_rx   = time.monotonic()
_NO_SIGNAL = 10.0    # seconds before showing "No signal"
_signal_ok = False

while True:
    pkt = e.read()

    if pkt is not None:
        _last_rx   = time.monotonic()
        _signal_ok = True
        try:
            parts = pkt.msg.decode().split("|")
            if len(parts) == 4:
                _lbl_group.text  = _clip(parts[0])
                _lbl_group.color = _group_color(parts[0])
                _lbl_buf.text    = _clip(parts[1])
                _lbl_action.text = _clip(parts[2])
                _lbl_mods.text   = _clip(parts[3])
        except Exception:
            pass  # malformed packet — keep last good display

    elif _signal_ok and (time.monotonic() - _last_rx) > _NO_SIGNAL:
        _signal_ok = False
        _show_no_signal()
