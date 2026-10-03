# AeroMorse — Wireless Display (receiver) settings
#
# AeroMorse receiver_config.py — version 1.19 (released 2026-10-03)
# Official source (always get the latest here): https://github.com/jlubin2001/AeroMorse
#
# Copy this file to the WIRELESS DISPLAY board only (next to its code.py, which
# is receiver.py or receiver_magtag.py). The main AeroMorse device uses
# config.py instead and ignores this file.
#
# Edit a value, save, and the display restarts with it. If this file is
# missing, or a value is wrong, the display simply uses the built-in default
# shown here — it never stops working because of this file.


# ── WIRELESS LINK ─────────────────────────────────────────────────────────

ESPNOW_CHANNEL = 1          # WiFi channel 1–13. MUST match ESPNOW_CHANNEL in the
                            # main device's config.py, or nothing is received.


# ── SCREEN (colour TFT display, receiver.py) ──────────────────────────────

DISPLAY_BRIGHTNESS = 1.0    # backlight 0.1 (dim) to 1.0 (full)
DISPLAY_ROTATION   = 0      # degrees: 0 = USB left, 180 = USB right (also 90, 270)
SLEEP_AFTER_S      = 300    # seconds with no signal before the screen goes dark
                            # (it wakes by itself when signal returns)


# ── NO SIGNAL / RECOVERY (both display types) ─────────────────────────────

NO_SIGNAL_S  = 10           # seconds without a message before "No signal" shows
AUTO_RESET_S = 30           # seconds of lost signal before the display restarts
                            # itself (recovers a stuck WiFi radio). Only after it
                            # has received something since starting, so a main
                            # device that is simply switched off doesn't cause a
                            # restart loop.


# ── E-INK (MagTag display, receiver_magtag.py) ────────────────────────────

REFRESH_MIN_S = 2.0         # never redraw the e-ink screen more often than this
                            # (e-ink is slow and wears with constant refreshes)
