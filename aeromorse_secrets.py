"""AeroMorse Secrets — edit your passwords and save them as a PIN-locked
macro_secrets.enc for the AeroMorse device.

    Double-click  "AeroMorse Secrets.exe"  (or run  python aeromorse_secrets.py
    [folder]). It opens the secrets in that folder (default: the folder it is
    run from), lets you edit them as  key=value  lines, and saves them
    ENCRYPTED with a PIN you choose.

On the device, macro_secrets.enc starts LOCKED at every power-up. The first
time you use a secret pattern it asks for the PIN: type it in Morse with the
Group 1 letters/digits, then ENTER. The PIN is not case-sensitive.

Format (must match code.py):
    "AMSEC1" | rounds (4, big-endian) | salt 16 | nonce 16 | check 16 | ciphertext
    k   = SHA256("AeroMorse secrets v1\\0" + salt + pin)
    repeat rounds:  k = AES256_k(00*16) || AES256_k(01*16)
    key = SHA256("enc\\0" + k);  check = SHA256("chk\\0" + k)[:16]
    ciphertext = AES-256-CTR(key, nonce) of the UTF-8  key=value  text

Needs:  pip install cryptography   (the .exe already includes it)
"""
import hashlib
import os
import re
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b"AMSEC1"
HEADER = 58
DEFAULT_ROUNDS = 5000        # ~1.5 s to unlock on an ESP32-S3 Feather
ENC_NAME = "macro_secrets.enc"
TXT_NAME = "macro_secrets.txt"
MIN_PIN = 4
GOOD_PIN = 8


# ── Crypto (mirrors code.py) ─────────────────────────────────────────────────
def normalize_pin(pin):
    return pin.strip().lower()


def _aes_ecb(key):
    return Cipher(algorithms.AES(key), modes.ECB()).encryptor()


def derive_keys(pin, salt, rounds):
    k = hashlib.sha256(b"AeroMorse secrets v1\x00" + salt + pin.encode("utf-8")).digest()
    z0, z1 = bytes(16), b"\x01" * 16
    for _ in range(rounds):
        e = _aes_ecb(k)
        k = e.update(z0) + e.update(z1)
    return (hashlib.sha256(b"enc\x00" + k).digest(),
            hashlib.sha256(b"chk\x00" + k).digest()[:16])


def encrypt(text, pin, rounds=DEFAULT_ROUNDS, salt=None, nonce=None):
    salt = salt or os.urandom(16)
    nonce = nonce or os.urandom(16)
    key, check = derive_keys(normalize_pin(pin), salt, rounds)
    ct = Cipher(algorithms.AES(key), modes.CTR(nonce)).encryptor().update(text.encode("utf-8"))
    return MAGIC + rounds.to_bytes(4, "big") + salt + nonce + check + ct


def decrypt(blob, pin):
    """Return the plain text, or None if the PIN is wrong. Raises ValueError
    if the data isn't an AeroMorse secrets file."""
    if len(blob) < HEADER or blob[:6] != MAGIC:
        raise ValueError("not an AeroMorse macro_secrets.enc file")
    rounds = int.from_bytes(blob[6:10], "big")
    salt, nonce, chk = blob[10:26], blob[26:42], blob[42:58]
    key, check = derive_keys(normalize_pin(pin), salt, rounds)
    if check != chk:
        return None
    return Cipher(algorithms.AES(key), modes.CTR(nonce)).decryptor().update(blob[HEADER:]).decode("utf-8")


def parse(text):
    """key=value lines -> (dict, list of bad line numbers). Same rules as code.py."""
    d, bad = {}, []
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip().replace("\ufeff", "")
        if not s or s[0] == "#":
            continue
        if "=" not in s:
            bad.append(i)
            continue
        k, v = s.split("=", 1)
        if k.strip():
            d[k.strip()] = v.strip()
    return d, bad


def keys_used_in_map(folder):
    p = os.path.join(folder, "morse_map.py")
    if not os.path.exists(p):
        return None
    code = "\n".join(line.split("#", 1)[0] for line in open(p, encoding="utf-8-sig"))
    return set(re.findall(r"_secret\(\s*['\"]([^'\"]+)['\"]", code))


def circuitpy_drives():
    """Drive roots whose volume label is CIRCUITPY (Windows)."""
    out = []
    if os.name != "nt":
        return out
    import ctypes
    import string
    buf = ctypes.create_unicode_buffer(261)
    for letter in string.ascii_uppercase:
        root = letter + ":\\"
        if not os.path.exists(os.path.join(root, "boot_out.txt")):
            continue
        if ctypes.windll.kernel32.GetVolumeInformationW(root, buf, 261, None, None, None, None, 0):
            if buf.value.upper() == "CIRCUITPY":
                tag = [f[:-4] for f in os.listdir(root) if f.startswith("AeroMorse-") and f.endswith(".txt")]
                out.append((root, tag[0] if tag else ""))
    return out


# ── GUI ──────────────────────────────────────────────────────────────────────
def run_gui(folder):
    import shutil
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog

    root = tk.Tk()
    root.title("AeroMorse Secrets")
    root.geometry("760x640")
    root.minsize(640, 520)
    font = ("Segoe UI", 12)
    mono = ("Consolas", 12)
    state = {"folder": folder, "pin": None}

    top = tk.Frame(root, padx=10, pady=8)
    top.pack(fill="x")
    tk.Label(top, text="Folder:", font=font).pack(side="left")
    folder_var = tk.StringVar(value=folder)
    tk.Entry(top, textvariable=folder_var, font=font, state="readonly").pack(side="left", fill="x", expand=True, padx=6)

    help_txt = ("One secret per line:   key=value      (e.g.  password1=MyP@ss)\n"
                "The key must match the name used in morse_map.py:  _secret('password1', ...)")
    tk.Label(root, text=help_txt, font=("Segoe UI", 10), justify="left", fg="#444").pack(anchor="w", padx=10)

    txt = tk.Text(root, font=mono, wrap="none", undo=True, height=14)
    txt.pack(fill="both", expand=True, padx=10, pady=6)

    pinf = tk.Frame(root, padx=10)
    pinf.pack(fill="x")
    tk.Label(pinf, text="PIN:", font=font).grid(row=0, column=0, sticky="e")
    pin1 = tk.Entry(pinf, show="*", font=font, width=24)
    pin1.grid(row=0, column=1, padx=6, pady=2, sticky="w")
    tk.Label(pinf, text="Confirm PIN:", font=font).grid(row=1, column=0, sticky="e")
    pin2 = tk.Entry(pinf, show="*", font=font, width=24)
    pin2.grid(row=1, column=1, padx=6, pady=2, sticky="w")
    show_var = tk.BooleanVar(value=False)

    def toggle_show():
        ch = "" if show_var.get() else "*"
        pin1.config(show=ch)
        pin2.config(show=ch)
    tk.Checkbutton(pinf, text="Show PIN", font=font, variable=show_var,
                   command=toggle_show).grid(row=0, column=2, padx=10, sticky="w")
    tk.Label(root, font=("Segoe UI", 10), fg="#444", justify="left",
             text="Letters and digits you can type in Group 1. Not case-sensitive. "
                  "8 or more characters recommended.\n"
                  "Leave both blank to keep the current PIN."
             ).pack(anchor="w", padx=10, pady=(2, 0))

    status = tk.StringVar()
    tk.Label(root, textvariable=status, font=font, fg="#0a5", anchor="w").pack(fill="x", padx=10, pady=(6, 0))

    def ask_pin(prompt):
        """PIN dialog with a Show PIN checkbox. Returns the text, or None if cancelled."""
        dlg = tk.Toplevel(root)
        dlg.title("AeroMorse Secrets")
        dlg.transient(root)
        dlg.resizable(False, False)
        result = {"pin": None}
        tk.Label(dlg, text=prompt, font=font).pack(anchor="w", padx=12, pady=(12, 4))
        ent = tk.Entry(dlg, show="*", font=font, width=28)
        ent.pack(padx=12, fill="x")
        sv = tk.BooleanVar(value=show_var.get())
        ent.config(show="" if sv.get() else "*")
        tk.Checkbutton(dlg, text="Show PIN", font=font, variable=sv,
                       command=lambda: ent.config(show="" if sv.get() else "*")
                       ).pack(anchor="w", padx=12, pady=4)

        def ok(_e=None):
            result["pin"] = ent.get()
            dlg.destroy()
        bf = tk.Frame(dlg)
        bf.pack(pady=(4, 12))
        tk.Button(bf, text="OK", font=font, width=8, command=ok).pack(side="left", padx=4)
        tk.Button(bf, text="Cancel", font=font, width=8, command=dlg.destroy).pack(side="left", padx=4)
        dlg.bind("<Return>", ok)
        dlg.bind("<Escape>", lambda _e: dlg.destroy())
        ent.focus_set()
        dlg.grab_set()
        root.wait_window(dlg)
        return result["pin"]

    def set_text(s):
        txt.delete("1.0", "end")
        txt.insert("1.0", s)
        txt.edit_reset()

    def load(fold):
        state["folder"] = fold
        state["pin"] = None
        folder_var.set(fold)
        enc = os.path.join(fold, ENC_NAME)
        plain = os.path.join(fold, TXT_NAME)
        if os.path.exists(enc):
            blob = open(enc, "rb").read()
            while True:
                pin = ask_pin("Enter the PIN for macro_secrets.enc:")
                if pin is None:
                    set_text("")
                    status.set("Not opened. Choose another folder, or type new secrets and save with a new PIN.")
                    return
                try:
                    text = decrypt(blob, pin)
                except ValueError as e:
                    messagebox.showerror("AeroMorse Secrets", str(e))
                    return
                if text is not None:
                    state["pin"] = normalize_pin(pin)
                    set_text(text)
                    status.set("Opened macro_secrets.enc (%d secrets)." % len(parse(text)[0]))
                    return
                messagebox.showwarning("AeroMorse Secrets", "Wrong PIN — try again.")
        elif os.path.exists(plain):
            set_text(open(plain, encoding="utf-8-sig").read())
            status.set("Imported plain macro_secrets.txt. Choose a PIN and Save to encrypt it.")
        else:
            set_text("# key=value, one per line\n")
            status.set("No secrets file here yet. Type key=value lines, choose a PIN, and Save.")

    def choose_folder():
        f = filedialog.askdirectory(initialdir=state["folder"], title="Folder with your AeroMorse files")
        if f:
            load(os.path.normpath(f))

    def save():
        text = txt.get("1.0", "end-1c")
        secrets, bad = parse(text)
        p1, p2 = pin1.get(), pin2.get()
        if p1 or p2:
            if normalize_pin(p1) != normalize_pin(p2):
                messagebox.showerror("AeroMorse Secrets", "The two PINs don't match.")
                return
            pin = normalize_pin(p1)
            if len(pin) < MIN_PIN:
                messagebox.showerror("AeroMorse Secrets", "The PIN must be at least %d characters." % MIN_PIN)
                return
            if len(pin) < GOOD_PIN and not messagebox.askyesno(
                    "AeroMorse Secrets",
                    "A PIN shorter than %d characters can be guessed by someone who copies "
                    "the file. Use it anyway?" % GOOD_PIN):
                return
        elif state["pin"]:
            pin = state["pin"]
        else:
            messagebox.showerror("AeroMorse Secrets", "Choose a PIN (type it twice).")
            return
        notes = []
        if bad:
            notes.append("Lines with no '=' will be ignored: %s" % ", ".join(map(str, bad)))
        used = keys_used_in_map(state["folder"])
        if used is not None:
            missing = sorted(used - set(secrets))
            if missing:
                notes.append("morse_map.py uses these keys that have no value here "
                             "(they'll type their placeholder): " + ", ".join(missing))
        enc_path = os.path.join(state["folder"], ENC_NAME)
        with open(enc_path, "wb") as f:
            f.write(encrypt(text, pin))
        state["pin"] = pin
        pin1.delete(0, "end")
        pin2.delete(0, "end")
        status.set("Saved %s (%d secrets, PIN-locked)." % (ENC_NAME, len(secrets)))
        msg = "Saved %d secrets to\n%s\n" % (len(secrets), enc_path)
        if notes:
            msg += "\nNote:\n- " + "\n- ".join(notes) + "\n"
        messagebox.showinfo("AeroMorse Secrets", msg)
        plain = os.path.join(state["folder"], TXT_NAME)
        if os.path.exists(plain) and messagebox.askyesno(
                "AeroMorse Secrets",
                "A plain-text macro_secrets.txt is still in this folder, readable by anyone.\n\n"
                "Delete it now? (Recommended — your secrets are now in the encrypted file.)"):
            os.remove(plain)
            status.set(status.get() + "  Plain macro_secrets.txt deleted.")

    def copy_to_device():
        enc_path = os.path.join(state["folder"], ENC_NAME)
        if not os.path.exists(enc_path):
            messagebox.showerror("AeroMorse Secrets", "Save first — there is no %s in this folder." % ENC_NAME)
            return
        drives = circuitpy_drives()
        if not drives:
            messagebox.showerror("AeroMorse Secrets", "No CIRCUITPY drive found. Plug the device in and try again.")
            return
        if len(drives) == 1:
            root_dir, tag = drives[0]
            if not messagebox.askyesno("AeroMorse Secrets",
                                       "Copy %s to %s %s?" % (ENC_NAME, root_dir, tag)):
                return
        else:
            choices = "\n".join("%d = %s %s" % (i + 1, d, t) for i, (d, t) in enumerate(drives))
            n = simpledialog.askinteger("AeroMorse Secrets", "Which device?\n" + choices,
                                        minvalue=1, maxvalue=len(drives), parent=root)
            if not n:
                return
            root_dir, tag = drives[n - 1]
        shutil.copyfile(enc_path, os.path.join(root_dir, ENC_NAME))
        msg = "Copied to %s %s. The device restarts and is LOCKED until you enter the PIN." % (root_dir, tag)
        dev_plain = os.path.join(root_dir, TXT_NAME)
        if os.path.exists(dev_plain) and messagebox.askyesno(
                "AeroMorse Secrets",
                "The device still has a plain-text macro_secrets.txt.\n\n"
                "Delete it from the device? (Recommended — the encrypted file is used instead.)"):
            os.remove(dev_plain)
            msg += "\nPlain macro_secrets.txt removed from the device."
        status.set(msg.split("\n")[0])
        messagebox.showinfo("AeroMorse Secrets", msg)

    btns = tk.Frame(root, padx=10, pady=10)
    btns.pack(fill="x")
    for label, cmd in (("Open folder...", choose_folder), ("Save (encrypt)", save),
                       ("Copy to device", copy_to_device), ("Close", root.destroy)):
        tk.Button(btns, text=label, font=font, command=cmd, padx=10).pack(side="left", padx=4)

    root.after(100, lambda: load(folder))
    root.mainloop()


def _base_folder():
    if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
        return os.path.abspath(sys.argv[1])
    here = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
    cwd = os.getcwd()
    return cwd if os.path.exists(os.path.join(cwd, "morse_map.py")) else here


def _selftest(out_path):
    """--selftest OUT: encrypt/decrypt round trip, result written to OUT
    (the windowed .exe has no console)."""
    text = "# selftest\na=1\nb=two = 2\n"
    blob = encrypt(text, " Self Test 99 ", rounds=50)
    ok = decrypt(blob, "self test 99") == text and decrypt(blob, "nope") is None
    with open(out_path, "w") as f:
        f.write("OK" if ok else "FAIL")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--selftest":
        _selftest(sys.argv[2])
    else:
        run_gui(_base_folder())
