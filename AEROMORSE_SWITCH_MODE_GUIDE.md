# AeroMorse Switch Mode Guide — Two-Button Hold Mode

**Switch mode** (Group 9; new in v1.15 as Group 7, moved to Group 9 in v1.24)
turns AeroMorse into **two plain switches**. There is no Morse code in this
group:

- a **sip** presses **Enter** the moment it starts and **holds it** until the
  sip ends;
- a **puff** presses **Space** the moment it starts and **holds it** until the
  puff ends.

That is exactly how a pair of physical accessibility switches behaves, so it
works with games and apps built for one or two switches — including ones that
need a key **held down**, which Morse groups can't do.

---

## When to use which group

| | **Group 4 — Scanning** | **Group 9 — Switch** |
|---|---|---|
| What a sip/puff does | Taps a key after the Morse pattern finishes | Presses a key **instantly** and **holds** it while you sip/puff |
| Keys | 12: Enter, Space, F3–F12 (1–3-symbol patterns) | 2: Enter (sip), Space (puff) |
| Holding a key down | No | **Yes** |
| Best for | iOS Switch Control, Android Switch Access, Samsung Universal Switch | Switch games and apps, anything that needs "hold Space" |
| Guide | [AEROMORSE_SWITCH_CONTROL_GUIDE.md](AEROMORSE_SWITCH_CONTROL_GUIDE.md) | this guide |

---

## Quick start

1. **Enter Switch mode:** type the Group 0 code **`.-------`**
   (1 sip, 7 puffs). The screen shows **[ SWITCH ]**. (Long-press group
   cycling skips Switch mode, so you never land in it by accident.)
2. **Sip** to hold **Enter**, **puff** to hold **Space**. While a key is held
   the screen shows `HOLD RETURN` or `HOLD SPACEBAR`.
3. **Leave Switch mode:** just **stop** — after **20 seconds** with no sip or
   puff it goes back to **Keyboard** by itself. (Or hold one puff for
   **5 seconds**: Space is let go at 5 s and you switch to Keyboard.)

Things that do **not** change group in Switch mode, on purpose:

- **Hard (strong) sips and puffs** — games often need them.
- **Long sips and puffs** — games often need long holds.
- **Quick repeated sips or puffs.**

The first sip or puff after AeroMorse starts only closes the start-up
(version) screen; it doesn't press a key.

---

## Benny's Hub

[**Benny's Hub**](https://narbehouse.github.io/bennyshub/index.html) (by
NARBE) is a free library of games and tools made to be used with **one or two
buttons mapped to Space and Return** — a good match for Switch mode, and it
runs in any web browser on the computer AeroMorse is plugged into.

**How the hub is driven:**

| AeroMorse (Switch mode) | Key | In Benny's Hub |
|---|---|---|
| Puff | Space | Move to the next item |
| Sip | Enter (Return) | Choose / open the highlighted item |

**Games that need a held key.** Some games use how long you hold. In
**NARBE Kart** (the racing game), for example, the on-screen help says *Hold
Space to slide left, hold Enter to slide right*, and its menus use *tap Space
= next, hold Space = back, Enter = choose*. In Switch mode that is simply:

- **hold a puff** → hold Space → slide left;
- **hold a sip** → hold Enter → slide right;
- short puff → next; long puff → back; sip → choose.

**Getting started:**

1. On the computer, open
   <https://narbehouse.github.io/bennyshub/index.html> in a browser (full
   screen helps).
2. On AeroMorse, enter Switch mode (`.-------`).
3. Puff to move, sip to choose. When you're finished, stop for 20 seconds and
   AeroMorse returns to Keyboard.

Some Benny's Hub games also have a **one-switch** option. In Switch mode you
can use just the puff (Space) for those.

---

## Settings (`config.py`)

All in the **SWITCH GROUP** section of `config.py`. Save and the device
restarts with the new values.

| Setting | Default | What it does |
|---|---|---|
| `SWITCH_GROUP` | `9` | Which group is Switch mode (it was `7` before v1.24). `0` = no Switch mode (Group 9 becomes an ordinary group again). |
| `SWITCH_SIP_KEY` | `"ENTER"` | Key held while sipping. Any Keycode name, e.g. `"LEFT_ARROW"`. |
| `SWITCH_PUFF_KEY` | `"SPACE"` | Key held while puffing, e.g. `"RIGHT_ARROW"`. |
| `SWITCH_IDLE_EXIT_S` | `20` | Seconds with no sip/puff before it returns to `SWITCH_EXIT_GROUP` by itself. `0` = never (then use the long puff). |
| `SWITCH_EXIT_PUFF_S` | `5.0` | Hold one puff this long to leave straight away. |
| `SWITCH_EXIT_GROUP` | `1` | Where you go when leaving (1 = Keyboard). |
| `SWITCH_COUNTDOWN_S` | `10` | (v1.21+) Seconds of on-screen countdown before it leaves, e.g. `MOUSE IN 5`. `0` = none. |

Key names are listed in the **Keycode Reference** (`KEYCODE_REFERENCE.md` /
the PDF). For example, a game controlled with the arrow keys could use
`SWITCH_SIP_KEY = "LEFT_ARROW"` and `SWITCH_PUFF_KEY = "RIGHT_ARROW"`.

The validator (`Check my AeroMorse files`) checks these settings before you
copy `config.py` to the device.

---

## Tips

- **Watch the top line.** It says **[ SWITCH ]** while you're in Switch mode.
  A wireless display mirrors it, so you can put it where you can see it
  while playing.
- **Resting mid-game** for less than 20 seconds keeps you in Switch mode. If
  your game has longer pauses, raise `SWITCH_IDLE_EXIT_S` (e.g. `60`).
- **Keys never get stuck.** The key is let go when your sip/puff ends, and
  also whenever AeroMorse leaves Switch mode.
- **The sensor settings still apply** — `THRESH_SIP` / `THRESH_PUFF` decide
  how hard a sip/puff must be to count, the same as for Morse.

---

## Troubleshooting

| Problem | Why | Fix |
|---|---|---|
| It leaves Switch mode while I'm playing | A pause longer than `SWITCH_IDLE_EXIT_S`, or a 5-second puff | Raise `SWITCH_IDLE_EXIT_S` / `SWITCH_EXIT_PUFF_S` |
| I need the mouse between games | Switch mode has no Morse, so there is no code to press | Set `SWITCH_EXIT_GROUP = 2` so leaving lands in Mouse, and add a short Group 2 code for `"group 9"` in `morse_map.py` to come back. The countdown (`SWITCH_COUNTDOWN_S`) shows when it is about to leave |
| It won't leave Switch mode | You keep sipping/puffing within 20 s | Stop for 20 s, or hold one puff for 5 s |
| Nothing happens in the game | The game window isn't in front, or wants other keys | Click the game once; or change `SWITCH_SIP_KEY` / `SWITCH_PUFF_KEY` |
| `.-------` doesn't go to Switch mode | `SWITCH_GROUP` isn't `9` (before v1.24 it was `7`, reached with `...-----`) | Check `config.py` (or use the Group 0 code for the group you chose) |
| Group 9's own patterns don't type | Group 9 is Switch mode | Set `SWITCH_GROUP = 0` to use Group 9 for Morse again |
