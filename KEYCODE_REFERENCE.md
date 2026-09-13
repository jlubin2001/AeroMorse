# AeroMorse — `adafruit_hid` Keycode Reference

Every valid **`Keycode.NAME`** you can use in `morse_map.py`, taken directly from
the `adafruit_hid` library on the device (CircuitPython 9.x).

> **Names are case-sensitive and must match exactly.** `Keycode.PAGE_UP` works;
> `Keycode.Page_Up` or `Keycode.pageup` do **not**. The AeroMorse validator warns
> if you use a name that isn't on this list.

## How to use these in `morse_map.py`

```python
g1[3][0b101] = Keycode.K                              # press the K key
g2[4][0b0001] = (Keycode.LEFT_CONTROL, Keycode.C)     # a chord: Ctrl + C  (use a tuple)
g2[4][0b0010] = (Keycode.LEFT_GUI, Keycode.D)         # Win + D  (show desktop)
```

- **One key** → `Keycode.NAME`
- **A chord / combo** → a **tuple** of Keycodes, e.g. `(Keycode.LEFT_CONTROL, Keycode.LEFT_SHIFT, Keycode.ESCAPE)`
- **To type a character** instead of pressing a named key, use a **string**: `= "k"` types a lowercase *k*, `= "1"` types the digit *1*. (See the gotchas below — the number *keys* have word names.)

---

## Letters

```
A  B  C  D  E  F  G  H  I  J  K  L  M
N  O  P  Q  R  S  T  U  V  W  X  Y  Z
```

## Number keys (top row) — these are **words**, not digits

```
ONE  TWO  THREE  FOUR  FIVE  SIX  SEVEN  EIGHT  NINE  ZERO
```
> `Keycode.ONE` presses the **1** key. To *type* the character `1`, use the string `"1"` instead.

## Whitespace & editing

```
ENTER  (RETURN)    ESCAPE    BACKSPACE    TAB
SPACEBAR  (SPACE)  DELETE    INSERT       CAPS_LOCK
```

## Navigation

```
UP_ARROW   DOWN_ARROW   LEFT_ARROW   RIGHT_ARROW
HOME       END          PAGE_UP      PAGE_DOWN
```

## Punctuation / symbol keys

| Name | Key (US layout) |
|------|-----------------|
| `MINUS` | `-` |
| `EQUALS` | `=` |
| `LEFT_BRACKET` | `[` |
| `RIGHT_BRACKET` | `]` |
| `BACKSLASH` | `\` |
| `POUND` | `#` (non-US) |
| `SEMICOLON` | `;` |
| `QUOTE` | `'` |
| `GRAVE_ACCENT` | `` ` `` |
| `COMMA` | `,` |
| `PERIOD` | `.` |
| `FORWARD_SLASH` | `/` |

## Shifted symbols have **no Keycode of their own**

Characters like `:` `{` `}` `"` `?` `<` `>` `+` `_` `!` `@` `#` aren't separate keys —
they're **Shift + another key**. USB HID only has codes for the *physical* keys, so
you won't find `COLON`, `LEFT_BRACE`, etc. in the list. **Nothing is missing.**

Two ways to produce them in `morse_map.py`:

1. **Just type the character (easiest)** — use a string; `code.py` presses Shift for you:
   ```python
   g1[6][0b011110] = ':'      # types a colon
   g1[5][0b00110]  = '{'      # types a left brace
   ```
   (This is what your `morse_map.py` already does for `{ } : " ?` and the rest.)

2. **As a Shift chord** (only if you need the key-press form) — a tuple with a Shift:
   ```python
   = (Keycode.LEFT_SHIFT, Keycode.SEMICOLON)      # :
   = (Keycode.LEFT_SHIFT, Keycode.LEFT_BRACKET)   # {
   ```

| Symbol | Shift + | | Symbol | Shift + |
|--------|---------|---|--------|---------|
| `:` | `SEMICOLON` | | `_` | `MINUS` |
| `"` | `QUOTE` | | `+` | `EQUALS` |
| `{` | `LEFT_BRACKET` | | `\|` | `BACKSLASH` |
| `}` | `RIGHT_BRACKET` | | `~` | `GRAVE_ACCENT` |
| `<` | `COMMA` | | `?` | `FORWARD_SLASH` |
| `>` | `PERIOD` | | | |
| `!` | `ONE` | | `^` | `SIX` |
| `@` | `TWO` | | `&` | `SEVEN` |
| `#` | `THREE` | | `*` | `EIGHT` |
| `$` | `FOUR` | | `(` | `NINE` |
| `%` | `FIVE` | | `)` | `ZERO` |

> An **uppercase letter** is likewise Shift + the letter — but again, just use the
> string `"A"` and the layout handles it.

## Function keys

```
F1  F2  F3  F4  F5  F6  F7  F8  F9  F10  F11  F12
F13 F14 F15 F16 F17 F18 F19 F20 F21 F22  F23  F24
```
> `F13`–`F24` exist in the library but most computers ignore them. AeroMorse Group 4
> uses `F1`–`F12` for Switch Control.

## Locks & system

```
CAPS_LOCK   SCROLL_LOCK   PRINT_SCREEN   PAUSE
APPLICATION (the "menu" key)             POWER
```

## Number-pad (keypad)

```
KEYPAD_NUMLOCK
KEYPAD_ONE  KEYPAD_TWO  KEYPAD_THREE  KEYPAD_FOUR  KEYPAD_FIVE
KEYPAD_SIX  KEYPAD_SEVEN  KEYPAD_EIGHT  KEYPAD_NINE  KEYPAD_ZERO
KEYPAD_PERIOD     KEYPAD_PLUS      KEYPAD_MINUS
KEYPAD_ASTERISK   KEYPAD_FORWARD_SLASH
KEYPAD_ENTER      KEYPAD_EQUALS    KEYPAD_BACKSLASH
```

## Modifiers (for chords)

| Primary name | Also accepted (aliases) |
|--------------|--------------------------|
| `LEFT_CONTROL` | `CONTROL` |
| `RIGHT_CONTROL` | — |
| `LEFT_SHIFT` | `SHIFT` |
| `RIGHT_SHIFT` | — |
| `LEFT_ALT` | `ALT`, `OPTION` |
| `RIGHT_ALT` | — |
| `LEFT_GUI` | `GUI`, `WINDOWS`, `COMMAND` |
| `RIGHT_GUI` | — |

> The **GUI** key is the Windows key (⊞) on Windows and Command (⌘) on Mac.

---

## Gotchas that trip people up

- **The space key is `SPACEBAR`** (there's no plain `SPACE`… well, `SPACE` is an
  alias, but `SPACEBAR` is the real name — either works).
- **Number keys are words**: `Keycode.ONE` … `Keycode.ZERO`, *not* `Keycode.1`.
- **`ENTER` and `RETURN`** are the same key; so are the modifier aliases above.
- **Case-sensitive**: it's `LEFT_CONTROL`, never `Left_Control` or `left_control`.
- To *type text* (a letter, digit, word, or password), use a **string** value in
  `morse_map.py`, not a `Keycode`. Keycodes are for *pressing keys* (Enter, arrows,
  F-keys, chords like Ctrl+C).

*Source: `adafruit_hid/keycode.py` (Keycode class), CircuitPython 9.x bundle — the
version running on the AeroMorse devices. Regenerate this list if you upgrade the
`adafruit_hid` library.*
