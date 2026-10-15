# AeroMorse — Caregiver Guide

This guide is for the person who helps an AeroMorse user: plugging the
device in, connecting the tube, and getting it going again if it stops. No
technical experience is needed.

**The one thing to remember:** if the device stops responding, **unplug its
USB cable, wait five seconds, and plug it back in.** That restarts it, and
nothing is lost.

---

## What the parts are

| What it looks like | Name | What it does |
|--------------------|------|--------------|
| Small board with a little colour screen and a USB-C socket | **The AeroMorse** | Turns sips and puffs into typing and mouse movement |
| Tiny board with a short raised port on top | **Pressure sensor** | Feels the sip and the puff |
| Short thin cable with a small white plug at each end | **Sensor cable** | Joins the sensor to the AeroMorse |
| Soft clear tube | **Sip-and-puff tube** | Carries the breath to the sensor |
| USB-C cable | **Computer cable** | Powers the AeroMorse and carries the typing to the computer |

These may be inside a small case, with only the tube and the USB cable
coming out.

Some users also have:

| What it looks like | Name | What it does |
|--------------------|------|--------------|
| A second small board with a colour screen, often in its own case | **Wireless display** | Shows the same screen where the user can see it. No cable runs to the AeroMorse |
| A second complete AeroMorse | **Spare** | Takes over if the first one fails |

---

## Before first use — done once, by someone technical

- [ ] The AeroMorse software is installed on the board (Build Guide,
      section 9).
- [ ] If there is a wireless display, its software is installed too.

After that, nothing below needs a computer skill.

---

## Putting it together

1. **Sensor cable.** Push one end into the small white socket on the
   AeroMorse and the other end into either socket on the sensor. The plug
   only fits one way. If it will not go in, turn it over — do not force it.
2. **Tube.** Push one end of the tube over the raised port on the sensor.
   It should feel snug.
3. **Computer cable.** Plug the USB-C cable into the AeroMorse and into the
   computer.

If the parts are in a case, steps 1 and 2 are already done.

---

## Starting it

1. Plug the USB cable in.
2. **Keep the tube still for a few seconds** — the user should not sip or
   puff yet. The device is measuring the air pressure at rest.
3. The screen shows the device's name and a version number. It is ready.
4. The user's **first** sip or puff only clears that screen. From the
   second one on, every sip and puff counts.

The computer treats the AeroMorse as an ordinary keyboard and mouse. There
is nothing to install on the computer.

**Wireless display:** plug it into any USB power — a phone charger, a power
bank, or a spare USB socket. It shows the AeroMorse's screen within a few
seconds. If it has a battery, plugging it in also charges it.

**To switch the AeroMorse off:** unplug its USB cable.

---

## If something is not working

| What you see | What to do |
|--------------|-----------|
| **The user's sips and puffs do nothing** | Unplug the USB cable, wait five seconds, plug it back in. Keep the tube still for a few seconds while it starts |
| Still nothing after that | Check the tube is pushed onto the sensor and is not kinked or pinched. Check the sensor cable is pushed in at both ends |
| It types the wrong letters, or misses sips and puffs | Check the tube first, as above. Then restart it by unplugging and replugging |
| The screen is dark | It may be switched off on purpose — some users watch only the wireless display or a window on the computer. If the user can still type, nothing is wrong |
| The computer does not react at all | Try the USB cable in a different socket on the computer |
| Wireless display says **No signal** | The AeroMorse is not running. Plug it in or restart it |
| Wireless display is dark | It goes dark by itself after five minutes with no signal. It comes back when the AeroMorse is running. If not, unplug and replug its power |
| A small window pops up on the computer about a "USB drive" or "removable drive" when the device starts | Ignore it or close it. It is harmless |

---

## Please do not

- **Do not open, delete or rename files on the drive called `CIRCUITPY`.**
  The AeroMorse shows up on the computer as a small USB drive as well as a
  keyboard. Those files are the device's program and the user's own codes.
- **Do not agree to "format", "scan and fix" or "back up" that drive** if
  the computer offers. Close the message.
- **Do not pull on the tube.** It is held on the sensor by friction only.

---

## Changing to the spare

If the user has a second AeroMorse and the first one fails:

1. Unplug the USB cable from the first device.
2. Move the tube to the spare's sensor.
3. Plug the USB cable into the spare.
4. Keep the tube still for a few seconds while it starts.
