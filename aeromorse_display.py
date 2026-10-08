# AeroMorse Display — the AeroMorse screen in a window on the computer
# For AeroMorse v1.26 or later.  https://github.com/jlubin2001/AeroMorse
#
# Shows what the device's own screen shows — group, the dots and dashes as they
# build, the last action and the status line — in a window you can make any
# size and put anywhere. No extra hardware: it reads the device over the USB
# cable it is already plugged in with.
#
# On the device: set  PC_DISPLAY = True  in config.py.
#
# This program ONLY LISTENS. It never sends a single byte to the device, so it
# cannot stop or disturb it. While it is running, no other program (Thonny, a
# serial terminal) can open the same device's port — close this window first.
#
# Run:   AeroMorse Display.exe            (finds the device by itself)
#        aeromorse_display.py --port COM8 (use one port only)
#        aeromorse_display.py --demo      (made-up data, no device needed)
#
# Right-click the window for the menu (always on top, see-through, title bar,
# switch device, close). Needs Python 3 with pyserial when run from source.

import json
import os
import queue
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont

try:
    import serial
    import serial.tools.list_ports as list_ports
except ImportError:                       # only matters when run from source
    serial = None
    list_ports = None

APP = "AeroMorse Display"
MARK = "~AM\t"                            # start of a status line from code.py
ADAFRUIT_VID = 0x239A
BG = "#000020"
GROUP_COLORS = {"BASE": "#606060", "KEYBOARD": "#0080FF", "MOUSE": "#00C040", "MACRO": "#FF8000",
                "SCANNING": "#FF00FF", "MEDIA": "#FFFF00", "GROUP 6": "#00FFFF", "GROUP 7": "#FF0080",
                "GROUP 8": "#8000FF", "GROUP 9": "#FF4000", "SWITCH": "#FF4000"}
QUIET_S = 5.0                             # no line for this long = "waiting"
PROBE_S = 3.5                             # how long to listen to one port when searching


def _settings_path():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, "AeroMorse", "display.json")

def load_settings():
    try:
        with open(_settings_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except Exception:
        return {}

def save_settings(d):
    try:
        os.makedirs(os.path.dirname(_settings_path()), exist_ok=True)
        with open(_settings_path(), "w", encoding="utf-8") as f:
            json.dump(d, f, indent=1)
    except Exception:
        pass


def parse(line):
    """'~AM<tab>group<tab>buffer<tab>action<tab>status' -> 4 strings, else None."""
    i = line.find(MARK)
    if i < 0:
        return None
    parts = line[i + len(MARK):].rstrip("\r\n").split("\t")
    if len(parts) != 4:
        return None
    return tuple(p.strip() for p in parts)

def group_color(text):
    for name, col in GROUP_COLORS.items():
        if name in text:
            return col
    return "#FFFFFF"                      # e.g. the device name on the start-up screen


class Reader(threading.Thread):
    """Listens to the device. Opens the port, reads lines, never writes."""

    def __init__(self, out, port=None, serial_number=None):
        super().__init__(daemon=True)
        self.out = out                    # queue of ("data", fields) / ("state", text)
        self.fixed_port = port
        self.want_serial = serial_number  # remembered device, or None = any
        self.stop = False
        self.rescan = False               # set by the menu to choose again
        self.avoid_serial = None          # the device to try LAST when switching

    def _candidates(self):
        ports = [p for p in list_ports.comports() if p.vid == ADAFRUIT_VID]
        if self.fixed_port:
            return [(self.fixed_port, None)]
        if self.want_serial:
            # The device chosen before, and ONLY that one. While it is away (a
            # restart takes a few seconds) wait for it rather than showing
            # another AeroMorse that happens to be plugged in.
            return [(p.device, p.serial_number) for p in ports if p.serial_number == self.want_serial]
        ports.sort(key=lambda p: p.serial_number == self.avoid_serial)   # "switch": others first
        return [(p.device, p.serial_number) for p in ports]

    def _listen(self, device, sn, probe):
        """Read one port. With probe=True give up after PROBE_S without a status line."""
        try:
            s = serial.Serial(device, 115200, timeout=0.2)
        except Exception:
            return False
        got = False
        t0 = time.time()
        buf = b""
        try:
            while not self.stop and not self.rescan:
                chunk = s.read(4096)      # read only - nothing is ever written
                if chunk:
                    buf += chunk
                    while b"\n" in buf:
                        raw, buf = buf.split(b"\n", 1)
                        f = parse(raw.decode("utf-8", "replace"))
                        if f:
                            if not got:
                                got = True
                                self.out.put(("found", (device, sn)))
                            self.out.put(("data", f))
                    if len(buf) > 20000:
                        buf = b""
                if probe and not got and time.time() - t0 > PROBE_S:
                    break
        except Exception:
            pass                          # unplugged / restarted: go and look again
        finally:
            try:
                s.close()
            except Exception:
                pass
        return got

    def run(self):
        if serial is None:
            self.out.put(("state", "pyserial is not installed"))
            return
        while not self.stop:
            self.rescan = False
            cands = self._candidates()
            if not cands:
                self.out.put(("state", "Waiting for your AeroMorse to come back ..." if self.want_serial
                              else "No AeroMorse plugged in"))
                time.sleep(1.5)
                continue
            found = False
            for device, sn in cands:
                if self.stop or self.rescan:
                    break
                self.out.put(("state", "Listening on %s ..." % device))
                if self._listen(device, sn, probe=True):
                    found = True
                    break
            if not found and not self.stop and not self.rescan:
                self.out.put(("state", "Set PC_DISPLAY = True in config.py"))
                time.sleep(1.0)


class Demo(threading.Thread):
    def __init__(self, out):
        super().__init__(daemon=True)
        self.out = out
        self.stop = False
    def run(self):
        frames = [("AeroMorse Green", " ", "v1.26", "CP 9.2.9"),
                  ("[ KEYBOARD ]", ".", " ", " "), ("[ KEYBOARD ]", ". -", " ", " "),
                  ("[ KEYBOARD ]", ". - .", " ", " "), ("[ KEYBOARD ]", " ", '"r"', " "),
                  ("[ KEYBOARD ]", " ", "Ctrl", "Ctrl"), ("[ KEYBOARD ]", " ", '"c"', " "),
                  ("[ MOUSE ]", " ", "-> group 2", " "), ("[ MOUSE ]", ". . .", " ", " "),
                  ("[ MOUSE ]", " ", "MMOVE RIGHT", " "), ("[ MOUSE ]", " ", "RPT MMOVE RIGHT", "RPT"),
                  ("[ MOUSE ]", " ", "mclick left sgl", "SLOW DRAG"), ("[ MACRO ]", " ", "-> group 3", "UNLOCKED"),
                  ("[ SWITCH ]", " ", "KEYBOARD IN 5", " ")]
        self.out.put(("found", ("demo", None)))
        i = 0
        while not self.stop:
            self.out.put(("data", frames[i % len(frames)]))
            i += 1
            time.sleep(1.0)


class Window:
    def __init__(self, args):
        self.cfg = load_settings()
        self.q = queue.Queue()
        self.last_data = 0.0
        self.state = "Looking for the AeroMorse ..."
        self.device = None

        r = self.root = tk.Tk()
        r.title(APP)
        r.configure(bg=BG)
        r.geometry(self.cfg.get("geometry") or "520x300")
        r.minsize(160, 90)
        self.font = tkfont.Font(family="Consolas", size=20, weight="bold")
        self.small = tkfont.Font(family="Segoe UI", size=9)

        self.rows = tk.Frame(r, bg=BG)
        self.rows.place(relx=0.5, rely=0.5, anchor="center")
        self.l_group = tk.Label(self.rows, text="AeroMorse", bg=BG, fg="#FFFFFF", font=self.font)
        self.l_buf = tk.Label(self.rows, text=" ", bg=BG, fg="#00FFFF", font=self.font)
        self.act = tk.Frame(self.rows, bg=BG)
        self.l_rpt = tk.Label(self.act, text="", bg=BG, fg="#FF8000", font=self.font)
        self.l_action = tk.Label(self.act, text=" ", bg=BG, fg="#FFFF00", font=self.font)
        self.l_mods = tk.Label(self.rows, text=" ", bg=BG, fg="#FF8000", font=self.font)
        self.l_group.pack()
        self.l_buf.pack()
        self.act.pack()
        self.l_rpt.pack(side="left")
        self.l_action.pack(side="left")
        self.l_mods.pack()
        self.l_state = tk.Label(r, text="", bg=BG, fg="#8090A0", font=self.small)
        self.l_state.place(relx=0.5, rely=1.0, anchor="s")

        self.v_top = tk.BooleanVar(value=self.cfg.get("on_top", True))
        self.v_bar = tk.BooleanVar(value=self.cfg.get("title_bar", True))
        self.v_alpha = tk.IntVar(value=int(self.cfg.get("opacity", 100)))
        m = self.menu = tk.Menu(r, tearoff=0)
        m.add_checkbutton(label="Always on top", variable=self.v_top, command=self.apply_look)
        m.add_checkbutton(label="Title bar (untick for a plain panel)", variable=self.v_bar, command=self.apply_look)
        sub = tk.Menu(m, tearoff=0)
        for pct in (100, 85, 70, 50, 35):
            sub.add_radiobutton(label="%d %%" % pct, value=pct, variable=self.v_alpha, command=self.apply_look)
        m.add_cascade(label="See-through", menu=sub)
        m.add_separator()
        m.add_command(label="Switch to another AeroMorse", command=self.choose_again)
        m.add_separator()
        m.add_command(label="Close", command=self.close)

        for w in (r, self.rows, self.act, self.l_group, self.l_buf, self.l_rpt, self.l_action, self.l_mods, self.l_state):
            w.bind("<Button-3>", self.popup)
            w.bind("<ButtonPress-1>", self.drag_start)
            w.bind("<B1-Motion>", self.drag_move)
        r.bind("<Configure>", self.on_resize)
        r.protocol("WM_DELETE_WINDOW", self.close)

        if args.get("demo"):
            self.reader = Demo(self.q)
        else:
            self.reader = Reader(self.q, port=args.get("port"),
                                 serial_number=None if args.get("port") else self.cfg.get("serial"))
        self.reader.start()
        self.apply_look()
        self.fit()
        self.tick()

    # ── look ──────────────────────────────────────────────────────────────────
    def apply_look(self):
        r = self.root
        r.attributes("-topmost", bool(self.v_top.get()))
        r.attributes("-alpha", max(0.2, min(1.0, self.v_alpha.get() / 100.0)))
        want_plain = not self.v_bar.get()
        if bool(r.overrideredirect()) != want_plain:
            r.overrideredirect(want_plain)
        self.remember()

    def remember(self):
        self.cfg.update(on_top=bool(self.v_top.get()), title_bar=bool(self.v_bar.get()),
                        opacity=int(self.v_alpha.get()), geometry=self.root.geometry())
        save_settings(self.cfg)

    def fit(self):
        """Text as large as fits: 20 characters across, 4 rows down."""
        w, h = self.root.winfo_width(), self.root.winfo_height()
        if w < 10 or h < 10:
            return
        px = int(min((w - 12) / 20.0 / 0.56, (h - 22) / 4.0 / 1.22))
        px = max(8, px)
        if self.font.cget("size") != -px:
            self.font.configure(size=-px)          # negative = pixels

    def on_resize(self, ev):
        if ev.widget is self.root:
            self.fit()

    def popup(self, ev):
        self.menu.tk_popup(ev.x_root, ev.y_root)

    def drag_start(self, ev):
        self._drag = (ev.x_root - self.root.winfo_x(), ev.y_root - self.root.winfo_y())

    def drag_move(self, ev):
        if not self.v_bar.get():                   # the plain panel has no title bar to drag
            dx, dy = self._drag
            self.root.geometry("+%d+%d" % (ev.x_root - dx, ev.y_root - dy))

    # ── data ──────────────────────────────────────────────────────────────────
    def choose_again(self):
        old = self.cfg.pop("serial", None)
        save_settings(self.cfg)
        if isinstance(self.reader, Reader):
            self.reader.avoid_serial = old       # try the other device(s) first
            self.reader.want_serial = None
            self.reader.rescan = True
        self.last_data = 0.0

    def show(self, group, buf, action, mods):
        self.l_group.configure(text=group or " ", fg=group_color(group))
        self.l_buf.configure(text=buf or " ")
        if action.startswith("RPT "):
            self.l_rpt.configure(text="RPT ")
            self.l_action.configure(text=action[4:] or " ")
        else:
            self.l_rpt.configure(text="")
            self.l_action.configure(text=action or " ")
        self.l_mods.configure(text=mods or " ")

    def tick(self):
        try:
            while True:
                kind, val = self.q.get_nowait()
                if kind == "data":
                    self.last_data = time.time()
                    self.show(*val)
                elif kind == "found":
                    self.device = val[0]
                    if val[1] and not self.cfg.get("serial"):
                        # Remember this device and stay with it from now on;
                        # only the menu's "Switch" changes it.
                        self.cfg["serial"] = val[1]
                        save_settings(self.cfg)
                        if isinstance(self.reader, Reader):
                            self.reader.want_serial = val[1]
                elif kind == "state":
                    self.state = val
        except queue.Empty:
            pass
        if time.time() - self.last_data > QUIET_S:
            self.l_group.configure(text="AeroMorse", fg="#606060")
            self.l_buf.configure(text=" ")
            self.l_rpt.configure(text="")
            self.l_action.configure(text="waiting ...")
            self.l_mods.configure(text=" ")
            self.l_state.configure(text=self.state)
        else:
            self.l_state.configure(text="")
        self.root.after(40, self.tick)

    def close(self):
        self.remember()
        self.reader.stop = True
        self.root.destroy()


def dump(port, seconds, serial_number=None):
    """No window: print the status lines received, for checking a set-up."""
    q = queue.Queue()
    rd = Reader(q, port=port, serial_number=serial_number)
    rd.start()
    t0 = time.time()
    n = 0
    while time.time() - t0 < seconds:
        try:
            kind, val = q.get(timeout=0.2)
        except queue.Empty:
            continue
        if kind == "data":
            n += 1
        print(kind, val)
    rd.stop = True
    print("status lines:", n)


def main():
    a = sys.argv[1:]
    args = {"demo": "--demo" in a}
    if "--port" in a:
        args["port"] = a[a.index("--port") + 1]
    if "--dump" in a:
        dump(args.get("port"), float(a[a.index("--dump") + 1]),
             a[a.index("--serial") + 1] if "--serial" in a else None)
        return
    w = Window(args)
    if "--shot" in a:                              # for testing: save a picture of the window, then close
        path = a[a.index("--shot") + 1]
        def _shot():
            from PIL import ImageGrab
            r = w.root
            r.update()
            x, y = r.winfo_rootx(), r.winfo_rooty()
            ImageGrab.grab((x, y, x + r.winfo_width(), y + r.winfo_height())).save(path)
            w.close()
        w.root.after(int(float(a[a.index("--shot") + 2]) * 1000), _shot)
    w.root.mainloop()


if __name__ == "__main__":
    main()
