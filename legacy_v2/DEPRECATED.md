# `legacy_v2/` — Deprecated External-OLED Build

> **This folder is frozen and unmaintained as of 2026-06.**
> The active AeroMorse firmware lives at the **repo root** (`code.py`,
> `boot.py`, `config.py`, `morse_map.py`). New features land there only.

## What this folder used to be

`legacy_v2/code.py` was a separate firmware variant for builders whose
Feather **did not have a built-in display** and who wired up an external
**128 × 64 SSD1306 monochrome OLED** over STEMMA QT (Adafruit #326 or
#938). It had its own display setup (manual `displayio.I2CDisplay` +
`SSD1306` init, monochrome layout, no pressure bar) tuned for that
specific OLED.

The build guide used to direct builders here:

| Board | Use code.py from |
|---|---|
| #5691 / #5483 / #5300 (built-in TFT) | repo root |
| All other boards | `v2/` (this folder) |

## Why it's deprecated

`legacy_v2/code.py` has fallen behind root `code.py` on every major
feature added since early 2026:

| Feature | Root | `legacy_v2` |
|---|---|---|
| Config file (`config.py`) | ✓ | inline only |
| `SWITCH_MODE = 1 / 2 / 3` (1-switch and 3-switch modes) | ✓ | mode 2 only |
| `CODE_REPEAT` (Darci-style hold-to-repeat) | ✓ | ✗ |
| `LONG_PRESS_CYCLES_GROUP` toggle | ✓ | ✗ |
| Strong sip / strong puff (peak + long-press detection) | ✓ | ✗ |
| ConsumerControl HID + g5 Media dispatcher | ✓ | ✗ (g5 codes silently no-op) |
| `USE_WIRELESS_DISPLAY` toggle | ✓ | ✗ |
| `ACCEPT_DELAY` tuned default (0.5) | 0.5 | 0.2 (stale) |
| Calibration-complete log message | ✓ | ✗ |

The maintenance cost of bringing it to parity exceeded the (apparent)
demand. Freezing it is cleaner than continuing to half-port features.

## Migration paths

### Recommended — Use the root build with a different display

The root `code.py` was written for the 240 × 135 colour TFT on the
**#5691 Reverse TFT Feather** (and the identical-electrically `#5483`
and `#5300`). It already has the layout and pressure bar code; you just
need a Feather with a built-in TFT.

For builders who have a Feather **without** a built-in display:

- Switch to an **EYESPI TFT** (Build Guide §5 "EYESPI displays"):
  e.g. **#5800** 2.0″ 320×240 ST7789 + an **#5613** EYESPI breakout +
  any EYESPI flex cable. Pair with a Feather that has a free SPI bus.
  Display layout matches the root code with a 1-line init swap.
- Or a **FeatherWing TFT** (Build Guide §5): #3651, #5872, #3315 plug
  straight onto any Feather with header pins. Same display layout swap.

A small `display = ...` init block replaces `display = board.DISPLAY`
near the top of root `code.py`. Build Guide §5 has the snippet.

### Not recommended — Keep using `legacy_v2/`

If you must stay on the SSD1306 OLED specifically:

- The files in this folder still work as they did at the freeze date.
- You will not get any of the features listed in the table above.
- Bug fixes will not be back-ported. The recommended response to any
  bug here will be "migrate to root."

If you want to volunteer to bring `legacy_v2/code.py` to feature parity
with root, open a GitHub issue. The work is well-scoped (~150–200
lines, single commit) but needs an active OLED user to verify each
feature ports cleanly.

## What's NOT in this folder

- `legacy_v2/` does NOT have its own `config.py`. The settings were
  inline at the top of `legacy_v2/code.py` at the time of the freeze.
- The `morse_map.py` here was kept byte-identical to the root
  `morse_map.py` up to the freeze date — it has the g5 ConsumerControl
  entries, but `legacy_v2/code.py` has no dispatcher to use them, so
  g5 Media codes silently no-op on this build.

---

*Frozen 2026-06. See git history for the state at freeze:* `git log -- legacy_v2/`
