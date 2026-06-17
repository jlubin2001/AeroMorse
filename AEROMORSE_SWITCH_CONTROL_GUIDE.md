# AeroMorse Switch Control Guide

How to use AeroMorse as a 12-virtual-switch interface for **iOS Switch
Control**, **Android Switch Access**, and **Samsung Universal Switch**.

---

## What this is

iOS, Android, and Samsung all ship a system-wide accessibility feature
that lets the user navigate the entire OS — every app, every menu, every
control — by triggering a small set of "switches." A switch is just a
keypress: the user presses a key on a connected USB or Bluetooth
keyboard, and the OS performs the assigned action (Select, Next,
Previous, Home, Back, …).

AeroMorse already appears to the host as a standard USB HID keyboard.
**Group 4 ("Scanning") sends F1–F12 on the 12 shortest Morse patterns**,
so a sip-and-puff user can drive Switch Control as if they were pressing
twelve real switches — but in practice it's two breath movements
(sip = dot, puff = dash) producing patterns up to three symbols long.

This guide explains the recommended mapping on each platform and walks
through the OS-side setup.

---

## How AeroMorse fits in

| | Conventional 12-switch user | AeroMorse user |
|---|---|---|
| Input hardware | 12 physical jacks / pads | 1 sip-and-puff tube *(or 2 AT switches)* |
| What the OS sees | 12 keyboard keys (F1–F12) | The same 12 keyboard keys (F1–F12) |
| What the user does | Presses one of 12 switches | Sips/puffs a 1–3-symbol Morse pattern |

The OS cannot tell the difference. Anywhere this guide says "switch N"
or "press F4," an AeroMorse user simply enters the corresponding Morse
pattern in Group 4. **Switch to Group 4 first** (a long sip/puff cycles
groups; or use Group 0's 8-symbol jump pattern for a direct hop).

> **Audio feedback matters.** The built-in beeper confirms every dot
> and dash, so the user gets an immediate "did the device hear me?"
> signal — important when the host has gone full-screen Switch
> Control and the AeroMorse TFT is out of view.

---

## AeroMorse Group 4 — Morse patterns for F1–F12

The 12 shortest possible Morse patterns are assigned to F1–F12 in
priority order so the most-used switches are the fastest to enter:

| Key | Morse pattern | iOS action | Android action | Samsung action |
|----:|:--------------|:-----------|:---------------|:---------------|
| **F1**  | **·**       | Select Item     | Select           | Activate            |
| **F2**  | **−**       | Next Item       | Next             | Next Item           |
| **F3**  | **· ·**     | Previous Item   | Previous         | Previous Item       |
| **F4**  | **· −**     | Scanner Menu    | Back             | Action Menu         |
| **F5**  | **− ·**     | Home            | Home             | Back                |
| **F6**  | **− −**     | Tap             | Long Press       | Home                |
| **F7**  | **· · ·**   | Long Press      | Scroll Forward   | Touch & Hold        |
| **F8**  | **· · −**   | Scroll Down     | Scroll Backward  | Scroll Down         |
| **F9**  | **· − ·**   | Scroll Up       | Overview         | Scroll Up           |
| **F10** | **· − −**   | App Switcher    | Notifications    | Recent Apps         |
| **F11** | **− · ·**   | Notif/Control Ctr | Quick Settings  | Notifications       |
| **F12** | **− · −**   | Siri            | Auto-scan Toggle | Quick Settings      |

> A single dot or single dash is the entire input for the two
> most-used actions (Select and Next). Even the slowest F-key takes
> only three symbols.

---

## Choosing a layout

Switch Control is configurable — you only need to map as many F-keys as
you want to use. Two recommended layouts:

### Minimal — 5 actions (F1–F5)

For users new to Switch Control, or where 12 distinct OS-mapped actions
feels overwhelming. Covers the core scan-and-select loop plus one
escape route. **F1–F5 are intentionally identical between the 5-action
and 12-action layouts — muscle memory carries over.**

### Full — 12 actions (F1–F12)

Every common Switch Control action gets its own Morse pattern, with no
menu-diving for routine gestures. Recommended once the user is fluent.

---

## Minimal layout — map only F1–F5

### iOS Switch Control

| Morse | Key | iOS action | What it does |
|:------|:---:|:-----------|:-------------|
| ·     | F1  | Select Item     | Activate the highlighted item |
| −     | F2  | Move to Next Item | Highlight the next focusable item |
| · ·   | F3  | Move to Previous Item | Step back |
| · −   | F4  | Scanner Menu    | Open the contextual menu (tap, long press, scroll, drag…) |
| − ·   | F5  | Home Button     | Return to the Home Screen |

With Scanner Menu on F4 the user can reach essentially every other
gesture on demand — 5 actions covers nearly every scenario.

### Android Switch Access (stock)

| Morse | Key | Android action | What it does |
|:------|:---:|:---------------|:-------------|
| ·     | F1  | Select          | Activate the highlighted item |
| −     | F2  | Next            | Highlight the next item |
| · ·   | F3  | Previous        | Step back |
| · −   | F4  | Back            | Android's system Back |
| − ·   | F5  | Home            | Return to the Home screen |

Stock Switch Access has no contextual menu, so Back fills the gap on F4
and Home stays on F5.

### Samsung Universal Switch

| Morse | Key | Samsung action | What it does |
|:------|:---:|:---------------|:-------------|
| ·     | F1  | Activate         | Select the highlighted item |
| −     | F2  | Move to Next Item | Highlight the next item |
| · ·   | F3  | Move to Previous Item | Step back |
| · −   | F4  | Show Action Menu | Open the contextual menu (long press, scroll, notifications, drag…) |
| − ·   | F5  | Back             | Samsung/Android Back |

If both Back and Home as one-press actions matter more than the Action
Menu, swap F5 for Home and reach Back from the menu — or move to the
full 12-action layout.

---

## Full layout — map F1–F12

### iOS Switch Control

| Morse | Key | Action |
|:------|:---:|:-------|
| ·       | F1  | Select Item |
| −       | F2  | Move to Next Item |
| · ·     | F3  | Move to Previous Item |
| · −     | F4  | Scanner Menu |
| − ·     | F5  | Home |
| − −     | F6  | Tap |
| · · ·   | F7  | Long Press |
| · · −   | F8  | Scroll Down / Next Page |
| · − ·   | F9  | Scroll Up / Previous Page |
| · − −   | F10 | App Switcher |
| − · ·   | F11 | Notification / Control Center |
| − · −   | F12 | Siri |

F1–F5 cover the core scan-and-select loop, F6–F9 cover the gestures
most people otherwise dig out of the Scanner Menu, and F10–F12 reach
the system destinations directly. Siri on F12 is a catch-all for
anything not mapped.

### Android Switch Access

| Morse | Key | Action |
|:------|:---:|:-------|
| ·       | F1  | Select |
| −       | F2  | Next |
| · ·     | F3  | Previous |
| · −     | F4  | Back |
| − ·     | F5  | Home |
| − −     | F6  | Long Press |
| · · ·   | F7  | Scroll Forward |
| · · −   | F8  | Scroll Backward |
| · − ·   | F9  | Overview (Recent Apps) |
| · − −   | F10 | Notifications |
| − · ·   | F11 | Quick Settings |
| − · −   | F12 | Auto-scan Start/Stop |

Auto-scan on F12 toggles hands-free scanning so the user can rest
mid-session.

### Samsung Universal Switch

| Morse | Key | Action |
|:------|:---:|:-------|
| ·       | F1  | Activate |
| −       | F2  | Move to Next Item |
| · ·     | F3  | Move to Previous Item |
| · −     | F4  | Show Action Menu |
| − ·     | F5  | Back |
| − −     | F6  | Home |
| · · ·   | F7  | Touch & Hold (Long Press) |
| · · −   | F8  | Scroll Down |
| · − ·   | F9  | Scroll Up |
| · − −   | F10 | Recent Apps |
| − · ·   | F11 | Notifications |
| − · −   | F12 | Quick Settings / Volume |

Action Menu stays on F4 as a safety net for anything not directly
mapped.

---

## Setting up the OS to receive F1–F12

### iOS / iPadOS — Switch Control

1. Plug AeroMorse into the iPad/iPhone with USB-C (or use a
   Lightning-to-USB adapter on older devices).
2. Open **Settings › Accessibility › Switch Control**.
3. Tap **Switches › Add New Switch… › External**.
4. On AeroMorse, switch to **Group 4** (long sip/puff to cycle, or
   the Group 0 direct-jump pattern).
5. Enter **·** (a single sip) — iOS detects F1. Name it ("Select")
   and choose the action **Select Item**.
6. Tap **Add New Switch** again. Enter **−** (a single puff) for F2,
   assign **Move to Next Item**.
7. Repeat for each pattern in the table above through F5 (minimal)
   or F12 (full).
8. Set **Scanning Style** to **Manual Scanning** (recommended — you
   have dedicated Next/Previous switches and don't need auto-scan
   timing).
9. Adjust **Auto Tap**, **Hold Duration**, and **Tap Behavior** to
   taste.
10. Turn **Switch Control ON** at the top of the screen.

Set the **Accessibility Shortcut** (Settings › Accessibility →
Accessibility Shortcut → Switch Control) so triple-clicking the
side/Home button toggles Switch Control on and off — useful when an
assistant needs to interact with the screen normally.

### Android (stock) — Switch Access

1. Plug AeroMorse into the Android device (USB-C, or USB OTG cable).
2. Open **Settings › Accessibility › Switch Access**.
3. Tap **Settings** (gear) **before** turning it on, then **Assign
   switches for scanning**.
4. Choose **Number of switches** matching your chosen layout (2 for
   linear Next/Select only, up to 12 for the full layout).
5. For each action (Select, Next, Previous, Back, Home, …), tap it
   and then **enter the Morse pattern on AeroMorse** — Android
   records the resulting F-key.
6. Configure **Auto-scan timing**, **Point scan**, and **Feedback** as
   needed.
7. Go back and toggle **Use Switch Access ON**. Confirm the
   permission prompt.

### Samsung (One UI) — Universal Switch

1. Plug AeroMorse into the Samsung device with USB-C.
2. Open **Settings › Accessibility › Interaction and dexterity ›
   Universal switch**.
3. Toggle **Universal switch ON** and accept the permission prompt.
4. Tap **Add switch › Keyboard**.
5. On AeroMorse, in Group 4, enter **·** for F1. Name it ("Activate")
   and under **Action** choose **Activate**.
6. Tap **Add switch** again for each F-key in the layout.
7. Set **Scanning method** (Auto / Manual) and **Scan speed** under
   Universal switch settings.
8. Add an Accessibility shortcut (Side + Volume Up) under **Settings ›
   Accessibility › Advanced settings** to toggle Universal switch
   quickly.

---

## Cross-platform notes

- **F1–F3 are identical on every platform** (Select, Next, Previous).
  If the user only ever switches between platforms, those three
  patterns never need to be re-learned.
- **F4 diverges:** Scanner Menu (iOS), Back (Android), Action Menu
  (Samsung). On iOS and Samsung F4 is the contextual menu; on stock
  Android there is no menu so F4 is Back.
- **F5 diverges:** Home on iOS/Android, Back on Samsung. If you go
  back and forth between Samsung and iOS, consider remapping F5 on
  Samsung to Home and F6 to Back to keep the muscle memory aligned.
- AeroMorse sends *exactly* the F-key bytes a real switch interface
  would, so any third-party Switch Control configuration guide for a
  USB switch box applies verbatim.

---

## Tips

- **Print the cheat sheet.** `aeromorse_cheatsheet.htm` (Group 4 page)
  shows the Morse pattern, the F-key pill, and the iOS action label
  on the same row — exactly the information the user needs while
  configuring Switch Control. The print button produces one page per
  group.
- **Group 0 jump pattern.** Configure a memorable 8-symbol pattern in
  `morse_map.py` so the user can drop straight into Group 4 from any
  other group, instead of cycling.
- **Keep audio feedback on for setup.** Each beep confirms the
  device heard the symbol — important when the iPad screen is taken
  over by Switch Control prompts and the AeroMorse TFT is out of
  sight.
- **One device, multiple OSes.** The same AeroMorse and the same
  `morse_map.py` work on iOS, Android, Samsung, ChromeOS, Windows,
  macOS, and Linux. Only the OS-side mapping changes.

---

## Where this guide came from

The recommended action mappings (F1–F12 on each platform) are taken
from a separate cross-platform Switch Control study and are
platform-conventional, not AeroMorse-specific. AeroMorse's contribution
is delivering those 12 keypresses through Morse code instead of 12
physical switches — making whole-OS Switch Control reachable for users
who can produce only sips and puffs.
