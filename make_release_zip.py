#!/usr/bin/env python3
"""
make_release_zip.py — build the download for a GitHub release.

Makes  dist/AeroMorse-v<version>.zip  holding one plain folder with
everything a builder needs side by side, laid out like a work folder:
the device files, the Windows programs and one-click tools, the help pages
and the PDF guides. The version comes from the header of code.py.

    python make_release_zip.py

Then attach the zip to a release on GitHub (Releases → Draft a new release),
or:  gh release create v1.30 dist/AeroMorse-v1.30.zip --title "AeroMorse v1.30"

Developer tool: nothing here goes on the device.
"""
import os, re, sys, zipfile

REPO = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(REPO, "docs")

DEVICE = ["code.py", "boot.py", "config.py", "morse_map.py", "morse_map_darci.py",
          "macro_secrets.example.txt", "display_setup.example.py", "test_pressure.py",
          "receiver.py", "receiver_config.py"]
COMPUTER = ["AeroMorse Display.exe", "aeromorse_display.py",
            "AeroMorse Secrets.exe", "aeromorse_secrets.py", "Edit my AeroMorse secrets.bat",
            "aeromorse_validator.exe", "aeromorse_validator.py", "Check my AeroMorse files.bat",
            "morse_map_comments.exe", "morse_map_comments.py", "Fix my map comments.bat",
            "morse_map_analyzer.exe", "morse_map_analyzer.py", "Back up my AeroMorse.bat",
            "AeroMorse.ahk", "AeroMorse Help.html", "aeromorse_cheatsheet.htm",
            "AeroMorse Cheat Sheet.pdf", "LICENSE"]
GUIDES = ["AEROMORSE_BUILD_GUIDE.pdf", "AEROMORSE_USAGE_GUIDE.pdf", "AEROMORSE_REFERENCE.pdf",
          "CAREGIVER_SETUP_GUIDE.pdf", "AEROMORSE_SWITCH_MODE_GUIDE.pdf",
          "AeroMorse — Keycode Reference.pdf"]

START_HERE = """AeroMorse v{v} - start here
==============================

Everything in this folder belongs together. Keep it as your work folder,
for example Documents\\AeroMorse. The guides (PDFs) explain each step;
the newest versions are always at https://github.com/jlubin2001/AeroMorse

New build
  AEROMORSE_BUILD_GUIDE.pdf, section 9: put CircuitPython and its
  libraries on the board, then copy these four files to the CIRCUITPY drive:
      boot.py   code.py   config.py   morse_map.py
  Darci USB user: copy morse_map_darci.py instead of morse_map.py and
  rename it to morse_map.py on the drive.
  Wireless display (second board): copy receiver.py to it as code.py,
  plus boot.py and receiver_config.py.

Updating a device you already use
  Do not copy config.py or morse_map.py over your own - they hold your
  settings and codes. AEROMORSE_USAGE_GUIDE.pdf shows how to update safely.

On the computer (Windows)
  AeroMorse Display.exe          the device's screen in a window (PC_DISPLAY = True)
  AeroMorse Help.html            every code, one tab per group
  Check my AeroMorse files.bat   safety check before copying files to the device
  Back up my AeroMorse.bat       one-click dated backup of the device
  Edit my AeroMorse secrets.bat  PIN-locked passwords
  Fix my map comments.bat        makes the comments in morse_map.py match the codes
  morse_map_analyzer.exe         finds duplicate and free codes
  AeroMorse.ahk                  hotkeys for the window, help and the pointer (AutoHotkey)
  Mac or Linux: the .py files run the same tools with Python 3, e.g.
      python3 aeromorse_validator.py
  (Usage Guide section 2, "On a Mac or a Linux computer").

Guides
  AEROMORSE_BUILD_GUIDE.pdf       build it, install it, troubleshooting
  AEROMORSE_USAGE_GUIDE.pdf       change codes, settings and passwords safely
  AEROMORSE_REFERENCE.pdf         groups, mouse, macros, secrets
  CAREGIVER_SETUP_GUIDE.pdf       day-to-day help
  AEROMORSE_SWITCH_MODE_GUIDE.pdf switch games
  AeroMorse Cheat Sheet.pdf       every code, to print

Free and open source (MIT licence, see LICENSE).
"""

def version():
    head = open(os.path.join(REPO, "code.py"), encoding="utf-8").read(600)
    m = re.search(r"version\s+(\d+\.\d+)", head)
    if not m:
        sys.exit("ERROR: no version in the header of code.py")
    return m.group(1)

def main():
    v = version()
    top = "AeroMorse-v%s" % v
    files = [(os.path.join(REPO, f), f) for f in DEVICE + COMPUTER] + \
            [(os.path.join(DOCS, f), f) for f in GUIDES]
    missing = [src for src, _ in files if not os.path.exists(src)]
    if missing:
        sys.exit("ERROR: missing:\n  " + "\n  ".join(missing))
    os.makedirs(os.path.join(REPO, "dist"), exist_ok=True)
    out = os.path.join(REPO, "dist", top + ".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(top + "/START HERE.txt", START_HERE.format(v=v).replace("\n", "\r\n"))
        for src, name in files:
            z.write(src, top + "/" + name)
    print("%s  (%d files, %.1f MB)" % (out, len(files) + 1, os.path.getsize(out) / 1e6))

if __name__ == "__main__":
    main()
