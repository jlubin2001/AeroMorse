# macro_secrets.example.py — TEMPLATE for AeroMorse secret macros
#
# AeroMorse macro_secrets (example) — version 1.0 (released 2026-09-05)
# Official source: https://github.com/jlubin2001/AeroMorse
#
# ════════════════════════════════════════════════════════════════════════════
#  HOW TO USE
#  1. Copy this file to the CIRCUITPY drive and rename it to:  macro_secrets.py
#  2. Replace the example values below with your real passwords / details.
#  3. morse_map.py imports these automatically (Group 3 macros).
#
#  ⚠  NEVER SHARE macro_secrets.py.  This is the ONLY file that holds your real
#     passwords in plain text. It is listed in .gitignore so git will not commit
#     it, and it is intentionally kept separate from morse_map.py so that when
#     you share morse_map.py (or a zip of the project) for help, your secrets do
#     NOT go with it. If you send someone your CIRCUITPY drive contents, delete
#     macro_secrets.py from the copy first.
#
#  If macro_secrets.py is absent, AeroMorse still runs fine — the secret macros
#  simply type their placeholder text instead of a real value.
# ════════════════════════════════════════════════════════════════════════════

# Each key here matches a _secret('<key>', ...) call in morse_map.py's Group 3.
# Add, remove, or rename keys freely — just keep the key names in sync with
# morse_map.py.

SECRETS = {
    # Personal details (Group 3: A / B / C / E patterns)
    "name":    "Your Name",
    "address": "123 Example St, City, ST 00000",
    "phone":   "555-555-0100",
    "email":   "you@example.com",

    # Passwords / logins (Group 3: P / W patterns in the template — change to
    # whatever patterns you assign). Replace with your real values.
    "password1": "example-password-change-me",
    "wifi":      "example-wifi-key-change-me",
}
