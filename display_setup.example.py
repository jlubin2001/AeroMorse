# display_setup.example.py — set-up for a display that is NOT built into the board
# For AeroMorse v1.26 or later.  https://github.com/jlubin2001/AeroMorse
#
# WHO NEEDS THIS FILE
#   Nobody with the recommended #5691 Reverse TFT Feather (or a #5483 / #5300):
#   their screen is built in and works with no extra file. Do not copy this file
#   to such a board.
#
#   You need it only for a SEPARATE display — a TFT FeatherWing, a breakout TFT
#   or an OLED — on the main AeroMorse board or on a wireless-display board.
#
# HOW TO USE IT
#   1. Copy this file to the CIRCUITPY drive and rename the copy
#          display_setup.py
#   2. Keep ONE of the blocks below (delete the others, or leave them commented
#      out) and check the pins against your own wiring.
#   3. Put the display's driver library in /lib (named in each block).
#   4. Save. The device restarts and shows a line like
#          Display: from display_setup.py (480 x 320)
#      in its start-up log. Text size and positions adjust themselves to the
#      screen — there is nothing else to edit, in code.py or anywhere.
#
#   code.py and receiver.py look for display_setup.py by themselves, so updating
#   AeroMorse to a new version never undoes your display set-up.
#
# IF IT GOES WRONG
#   AeroMorse still types. If this file has a mistake, a library is missing or
#   the display does not answer, the device falls back to the built-in screen
#   (if the board has one) or runs with no screen, and prints the reason in its
#   start-up log.
#
# TESTED?
#   Only the built-in screen is tested by the project. The blocks below are
#   written from each display's documentation and have NOT been run on real
#   hardware. Treat them as a starting point.
#
# THE RULE
#   The file must define  setup()  and setup() must return the display object.
#   Start with displayio.release_displays() — after a restart the old display
#   is still holding its pins.

import board
import displayio


# ── 3.5" TFT FeatherWing #3651 / #5872 (480 x 320, HX8357D) ───────────────────
# Library: adafruit_hx8357.mpy.  CS = D9, DC = D10 is the FeatherWing standard.
def setup():
    import busio
    import fourwire
    from adafruit_hx8357 import HX8357
    displayio.release_displays()
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9, reset=None)
    return HX8357(bus, width=480, height=320)


# ── 2.4" TFT FeatherWing #3315 (320 x 240, ILI9341) ───────────────────────────
# Library: adafruit_ili9341.mpy.  Remove the '# ' from each line to use it, and
# delete the setup() above.
# def setup():
#     import busio
#     import fourwire
#     from adafruit_ili9341 import ILI9341
#     displayio.release_displays()
#     spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
#     bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9, reset=None)
#     return ILI9341(bus, width=320, height=240)


# ── Breakout TFTs wired pin by pin (#2050 HX8357D, #1770 / #1743 ILI9341) ─────
# Same as the two blocks above, with the pins YOU wired. The Build Guide's
# wiring table uses CS = D9, DC = D10, RST = D11:
#     bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9, reset=board.D11)


# ══ EYESPI displays on the #5613 EYESPI breakout ══════════════════════════════
# Seven wires from the breakout to the Feather (Build Guide section 5):
#     Vin -> 3V    Gnd -> GND    SCK -> SCK    MOSI -> MOSI
#     TCS -> D9    DC  -> D10    RST -> D11
# AeroMorse applies DISPLAY_ROTATION from config.py AFTER setup(), so set it
# there too: the ILI9341 screens are landscape at 0 (180 turns them over); the
# ST7789 screens are portrait at 0 - use 90 or 270 for landscape.
# On a #5691 this display takes over from the built-in screen, which goes dark.

# ── 2.8" TFT with cap touch #2090, or 2.2" TFT #1480 (320 x 240, ILI9341) ─────
# Library: adafruit_ili9341.mpy.   config.py: DISPLAY_ROTATION = 0 (or 180)
# def setup():
#     import busio
#     import fourwire
#     from adafruit_ili9341 import ILI9341
#     displayio.release_displays()
#     spi = busio.SPI(board.SCK, MOSI=board.MOSI)
#     bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9, reset=board.D11)
#     return ILI9341(bus, width=320, height=240)

# ── 2.0" IPS TFT #4311 (320 x 240, ST7789) ────────────────────────────────────
# Library: adafruit_st7789.mpy.    config.py: DISPLAY_ROTATION = 90 (or 270)
# def setup():
#     import busio
#     import fourwire
#     from adafruit_st7789 import ST7789
#     displayio.release_displays()
#     spi = busio.SPI(board.SCK, MOSI=board.MOSI)
#     bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9, reset=board.D11)
#     return ST7789(bus, width=240, height=320)

# ── 1.9" IPS TFT #5394 (320 x 170, ST7789) ────────────────────────────────────
# Library: adafruit_st7789.mpy.    config.py: DISPLAY_ROTATION = 90 (or 270)
# The picture on this narrow panel starts 35 pixels in (colstart); if it sits
# off to one side, that is the number to adjust.
# def setup():
#     import busio
#     import fourwire
#     from adafruit_st7789 import ST7789
#     displayio.release_displays()
#     spi = busio.SPI(board.SCK, MOSI=board.MOSI)
#     bus = fourwire.FourWire(spi, command=board.D10, chip_select=board.D9, reset=board.D11)
#     return ST7789(bus, width=170, height=320, colstart=35)


# ── OLED #326 (0.96") / #938 (1.3")  (128 x 64, SSD1306, STEMMA QT) ───────────
# Library: adafruit_displayio_ssd1306.mpy.  If the screen stays blank, try
# device_address=0x3D. Text is small on this screen (text scale 1).
# def setup():
#     import i2cdisplaybus
#     from adafruit_displayio_ssd1306 import SSD1306
#     displayio.release_displays()
#     bus = i2cdisplaybus.I2CDisplayBus(board.STEMMA_I2C(), device_address=0x3C)
#     return SSD1306(bus, width=128, height=64)
