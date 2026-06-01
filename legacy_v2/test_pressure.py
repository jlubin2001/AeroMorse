import time
import board
import adafruit_lps35hw

i2c = board.STEMMA_I2C()
lps = adafruit_lps35hw.LPS35HW(i2c)

# Calibrate baseline
print("Calibrating baseline (2 seconds, breathe normally) ...")
total = 0.0
samples = 40
for _ in range(samples):
    total += lps.pressure
    time.sleep(0.05)
baseline = total / samples
print(f"Baseline: {baseline:.3f} hPa")
print("Now sip and puff — watching for 30 seconds ...")
print("(delta > +0.3 = puff/dash,  delta < -0.3 = sip/dot)")
print()

end = time.monotonic() + 30
last_print = 0.0
while time.monotonic() < end:
    now = time.monotonic()
    delta = lps.pressure - baseline
    if now - last_print >= 0.1:   # print 10x/sec
        bar = int(abs(delta) * 20)
        direction = "PUFF +" if delta > 0 else "SIP  " if delta < 0 else "     "
        marker = "*** DETECTED ***" if abs(delta) >= 0.3 else ""
        print(f"{direction}{delta:+.3f} hPa  {'|' * bar}  {marker}")
        last_print = now
