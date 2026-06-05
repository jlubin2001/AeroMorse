# test_pressure.py — AeroMorse diagnostic
#
# HOW TO RUN
# ──────────
# CircuitPython only autoruns code.py (then main.py).  Pressing Reset or
# Ctrl-D re-runs code.py, not this file.  Instead:
#
#   1. Copy this file to the root of the CIRCUITPY drive.
#   2. Open a serial terminal:
#        Thonny  — bottom REPL pane
#        Mu      — Serial button
#        PuTTY   — connect to the Feather's COM port at 115200 baud
#        macOS/Linux shell — screen /dev/tty.usbmodem* 115200
#   3. Press Ctrl-C to interrupt code.py and reach the >>> prompt.
#      (Ctrl-D also soft-resets the Feather but it re-runs code.py —
#       stay at >>> instead.)
#   4. At >>> type:   import test_pressure
#      The script starts immediately; no reset needed.
#   5. To run it again in the same session (importlib is not available in
#      CircuitPython — use exec instead):
#        exec(open('test_pressure.py').read())
#
# WHAT IT DOES
# ────────────
# Calibrates the resting baseline for 1 s, then prints a live pressure-delta
# bar chart for 30 s.  At the end it suggests THRESH_SIP and THRESH_PUFF
# values to set in config.py.
#
# What to do during the 30 s:
#   1. Hold the tube still for the first 1 s while "Calibrating..." shows.
#   2. Sip and puff normally — as you would when typing — several times each.
#   3. Read the suggested thresholds at the end and copy them to config.py.

import time
import board
import adafruit_lps35hw

# ── Settings ───────────────────────────────────────────────────────────────
DURATION_S        = 30     # total run time in seconds
SAMPLE_INTERVAL   = 0.05   # seconds between sensor reads  (20 Hz)
PRINT_INTERVAL    = 0.20   # seconds between printed lines  (5 Hz)
POINTS_TO_AVERAGE = 8      # rolling-average depth — matches config.py default
THRESH_SIP_CFG    = 5      # config.py default — used only for trigger markers
THRESH_PUFF_CFG   = 5

# ── Init ───────────────────────────────────────────────────────────────────
print()
print("AeroMorse test_pressure.py")
print("──────────────────────────")

try:
    # board.I2C() returns the shared-bus singleton, so it works even after
    # Ctrl-C interrupts code.py — the pins are already claimed and reused
    # rather than re-initialised (which would raise "SCL in use").
    i2c    = board.I2C()
    sensor = adafruit_lps35hw.LPS35HW(i2c)
except Exception as e:
    print("ERROR: could not initialise LPS33HW sensor:", e)
    print("Check the STEMMA QT cable and that adafruit_lps35hw.mpy is in lib/.")
    raise SystemExit

# ── Calibrate baseline ─────────────────────────────────────────────────────
print("Calibrating baseline — hold tube still for 1 s ...")
cal_buf = []
cal_end = time.monotonic() + 1.0
while time.monotonic() < cal_end:
    cal_buf.append(sensor.pressure)
    time.sleep(SAMPLE_INTERVAL)
baseline = sum(cal_buf) / len(cal_buf)

print(f"Baseline: {baseline:.2f} hPa")
print()
print("Sip = negative delta (dot)   Puff = positive delta (dash)")
print(f"Trigger markers: THRESH_SIP={THRESH_SIP_CFG}  THRESH_PUFF={THRESH_PUFF_CFG}  (config.py defaults)")
print()
print(f"  {'sec':>5}   {'delta hPa':>9}   sip <──────── 0 ────────> puff   state")
print("  " + "─" * 68)

# ── Live loop ──────────────────────────────────────────────────────────────
buf          = []
min_delta    = 0.0
max_delta    = 0.0
t_start      = time.monotonic()
t_end        = t_start + DURATION_S
t_next_print = t_start

while time.monotonic() < t_end:
    now = time.monotonic()

    buf.append(sensor.pressure)
    if len(buf) > POINTS_TO_AVERAGE:
        buf.pop(0)
    delta = (sum(buf) / len(buf)) - baseline

    if delta < min_delta:
        min_delta = delta
    if delta > max_delta:
        max_delta = delta

    if now >= t_next_print:
        t_next_print += PRINT_INTERVAL
        elapsed = now - t_start

        # ASCII bar chart: 14 chars each side of centre, scale = ±15 hPa
        BAR_HALF = 14
        SCALE    = 15.0
        filled = min(BAR_HALF, int(abs(delta) / SCALE * BAR_HALF))
        if delta < 0:
            bar = " " * (BAR_HALF - filled) + "█" * filled + "│" + " " * BAR_HALF
        else:
            bar = " " * BAR_HALF + "│" + "█" * filled + " " * (BAR_HALF - filled)

        if delta <= -THRESH_SIP_CFG:
            state = "SIP  ."
        elif delta >= THRESH_PUFF_CFG:
            state = "PUFF -"
        else:
            state = "idle"

        print(f"  {elapsed:5.1f}s   {delta:+9.3f}   {bar}   {state}")

    time.sleep(SAMPLE_INTERVAL)

# ── Summary ────────────────────────────────────────────────────────────────
print()
print("── Summary " + "─" * 57)
print(f"  Baseline pressure         : {baseline:.2f} hPa")
print(f"  Peak sip  (most negative) : {min_delta:+.2f} hPa")
print(f"  Peak puff (most positive) : {max_delta:+.2f} hPa")
print()

# Suggest 60 % of peak absolute value, minimum 2, rounded to nearest integer.
# 60 % gives a comfortable margin — sensitive enough to catch normal inputs
# but well below the peak so strong sips/puffs don't false-trigger.
def _suggest(peak_abs):
    if peak_abs < 0.5:
        return "n/a (none detected — try again and sip/puff more firmly)"
    return str(max(2, round(peak_abs * 0.60)))

sip_str  = _suggest(abs(min_delta))
puff_str = _suggest(max_delta)

print(f"  Suggested THRESH_SIP   = {sip_str}")
print(f"  Suggested THRESH_PUFF  = {puff_str}")
print()
print("Open config.py in Thonny, update THRESH_SIP and THRESH_PUFF,")
print("save — the Feather will reload automatically.")
print()
print("Done.")
