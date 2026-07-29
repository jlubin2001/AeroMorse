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
#   3. Copy the SAME boot.py from the sender to this board. boot.py
#      auto-detects its role from whether /morse_map.py is present, so
#      it will correctly leave USB HID off on this receiver (no
#      morse_map.py is copied here in step 4).
#   4. Copy this file to the board as code.py. Do NOT copy morse_map.py
#      — its absence is what tells boot.py this is a receiver.
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
import microcontroller

from adafruit_display_text import label

# ── ESP-NOW ────────────────────────────────────────────────────────────────────
# Channel-lock dance: start_ap then immediately stop_ap pins the radio to a
# known channel without leaving WiFi associated (which would enable power-save
# and break ESP-NOW). Both boards must use the SAME channel — keep this in
# sync with ESPNOW_CHANNEL in the sender's config.py.

_CHANNEL = 1

wifi.radio.start_ap(" ", "", channel=_CHANNEL, max_connections=0)
wifi.radio.stop_ap()
e = espnow.ESPNow()   # no peers needed for receive
print("ESP-NOW: listening on channel", _CHANNEL)

# ── Display ────────────────────────────────────────────────────────────────────
# Mirrors the main board TFT layout exactly: same 4 rows, same colours,
# same group indicator colours.  Pressure bar omitted (no sensor on this board).
#
# Layout on the 240 × 135 px TFT:
#   Row 1  y=  2   group name          (large, group-coloured)
#   Row 2  y= 30   morse buffer        (cyan)
#   Row 3  y= 58   last action         (yellow)
#   Row 4  y= 86   modifiers / status  (orange)

_GROUP_NAMES  = ("BASE", "KEYBOARD", "MOUSE", "MACRO", "SCANNING",
                 "MEDIA", "GROUP 6", "GROUP 7", "GROUP 8", "GROUP 9")
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
    # Orange "RPT" tag pinned to the LEFT of the action row, shown only while a
    # repeat is active. Mirrors the main board: the RPT flag stands out in
    # orange against the yellow repeated-action name on the same row.
    lbl_rpt    = label.Label(terminalio.FONT, text=" ", color=0xFF8000, scale=2,
                             anchor_point=(0.0, 0.0), anchored_position=(4, 58))
    root.append(lbl_rpt)
    lbl_mods   = _make_label(root, " ",             0xFF8000,          86)

    display.root_group = root
    return lbl_group, lbl_buf, lbl_action, lbl_rpt, lbl_mods

_lbl_group, _lbl_buf, _lbl_action, _lbl_rpt, _lbl_mods = _build_display()

def _set_action(text):
    """Set the action row, splitting a leading 'RPT ' into the orange tag so
    the RPT flag renders orange while the repeated action name stays yellow —
    matching the main board TFT.

    When the tag is shown the action name is LEFT-anchored right after it
    (x=46) instead of centred, so a long label such as 'MMOVE DOWN-RIGHT'
    can't slide left and overlap the tag. terminalio.FONT is 12 px/char at
    scale 2, so the widest 16-char remainder (after 'RPT ') spans 46..238 —
    inside the 240 px width."""
    if text.startswith("RPT "):
        _lbl_rpt.text    = "RPT"
        _lbl_action.text = text[4:]
        _lbl_action.anchor_point      = (0.0, 0.0)
        _lbl_action.anchored_position = (46, 58)
    else:
        _lbl_rpt.text    = " "
        _lbl_action.text = text
        _lbl_action.anchor_point      = (0.5, 0.0)
        _lbl_action.anchored_position = (display.width // 2, 58)

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
    _set_action("Out of range?")
    _lbl_mods.text   = " "

# ── Main loop ──────────────────────────────────────────────────────────────────

_last_rx     = time.monotonic()
_NO_SIGNAL   = 10.0    # seconds before showing "No signal"
_AUTO_RESET  = 30.0    # seconds of no signal before soft-resetting this board.
                       # The ESP32-S3 WiFi radio occasionally wedges — a soft
                       # reset re-inits it without anyone having to unplug the
                       # receiver. Only fires once signal has actually been
                       # seen this boot (see _ever_had_signal): if the sender
                       # is simply off — e.g. the host laptop is powered down
                       # overnight — the receiver stays quiet instead of
                       # rebooting every 30 s all night.
_SLEEP_AFTER = 300.0   # seconds with no packet before blanking the screen
_signal_ok   = False
_ever_had_signal = False   # True once at least one packet arrives this boot;
                           # gates the auto-reset so a never-present sender
                           # doesn't cause an endless reboot loop.
_screen_on   = True

def _set_backlight(on):
    """Turn the TFT backlight on/off. Falls back gracefully if the board
    exposes brightness instead of a backlight pin (or neither)."""
    global _screen_on
    try:
        display.brightness = 1.0 if on else 0.0
    except (AttributeError, NotImplementedError):
        pass
    _screen_on = on

while True:
    try:
        pkt = e.read()
    except ValueError:
        # ESP-NOW queue occasionally yields a malformed entry after WiFi
        # state changes (USB power swap, long idle). Drop it and continue.
        pkt = None
    if pkt is None:
        time.sleep(0.01)   # yield to WiFi/ESP-NOW callbacks
    if pkt is not None:
        if not _signal_ok:
            print("first packet received:", pkt.msg)   # remove once stable
        if not _screen_on:
            _set_backlight(True)
        _last_rx   = time.monotonic()
        _signal_ok = True
        _ever_had_signal = True
        try:
            parts = pkt.msg.decode().split("|")
            if len(parts) == 4:
                _lbl_group.text  = _clip(parts[0])
                _lbl_group.color = _group_color(parts[0])
                _lbl_buf.text    = _clip(parts[1])
                _set_action(_clip(parts[2]))
                _lbl_mods.text   = _clip(parts[3])
        except Exception:
            pass  # malformed packet — keep last good display

    else:
        idle = time.monotonic() - _last_rx
        if _ever_had_signal and idle > _AUTO_RESET:
            # We were receiving and then lost it — the WiFi radio has almost
            # certainly wedged. Reboot so nobody has to unplug the board;
            # boot.py + code.py rerun and, if the sender is up, we're
            # mirroring again within a couple of seconds. Gated on
            # _ever_had_signal so a sender that is simply OFF (host laptop
            # shut down for the night) doesn't trigger an all-night reboot
            # loop — after this one reset the fresh boot has never seen
            # signal, so it waits quietly until the sender returns.
            microcontroller.reset()
        if _screen_on and idle > _SLEEP_AFTER:
            # Long idle — blank the screen entirely (still listening).
            _set_backlight(False)
        elif _signal_ok and idle > _NO_SIGNAL:
            _signal_ok = False
            _show_no_signal()
