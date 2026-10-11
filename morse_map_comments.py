#!/usr/bin/env python3
"""
morse_map_comments.py - make the dots and dashes in morse_map.py's comments
match the codes.

Every assignment in morse_map.py carries its Morse pattern twice: once as the
binary number the device uses, and once in the comment for people to read:

    g2[4][0b0010] = "mfast"            # ..-.    toggle fast mode
       |    |                            |
       |    +-- the code: 0 = dot, 1 = dash       +-- the same, for reading
       +------- how many dots and dashes

When you change the number, the comment is easy to forget. This tool rewrites
the pattern at the start of each comment so it says what the number says.
Nothing else on the line is touched, and the device behaves exactly the same -
comments are only for reading.

    python morse_map_comments.py                 fix morse_map.py next to this file
    python morse_map_comments.py <folder>        fix <folder>\\morse_map.py
    python morse_map_comments.py <file.py>       fix that file
    python morse_map_comments.py --check [...]   only list what would change

morse_map_comments.exe is the same program for a computer without Python: put
it next to morse_map.py and double-click it (or "Fix my map comments.bat").

Before changing anything it saves a copy next to the file, named
morse_map.py.before-comments-YYYYMMDD-HHMMSS.bak.

LOOK AT THE LIST IT PRINTS. The tool trusts the number, not the comment. If a
line's new pattern is not the one you meant, the NUMBER is what needs fixing -
the old comment was right.
"""
import io, os, re, shutil, sys, time, tokenize

_ASSIGN = re.compile(r"^\s*(g\d+)\[(\d+)\]\[0b([01]+)\]\s*=")
_PATTERN = re.compile(r"[.\-]+")


def _comment_col(line):
    """Column where the line's comment starts, or None. Uses Python's own
    tokenizer, so a # inside a quoted string is not mistaken for a comment."""
    try:
        for tok in tokenize.generate_tokens(io.StringIO(line).readline):
            if tok.type == tokenize.COMMENT:
                return tok.start[1]
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return None


def _fix_line(line):
    """Return (new_line, old_pattern, new_pattern, warning). new_line is None
    when the line is not a code assignment or is already right."""
    m = _ASSIGN.match(line)
    if not m:
        return None, None, None, None
    length, bits = int(m.group(2)), m.group(3)
    value = int(bits, 2)
    warning = None
    if value >= (1 << length):
        return None, None, None, ("%s[%d][0b%s]: the number is too big for %d symbols - "
                                  "this code can never be entered" % (m.group(1), length, bits, length))
    if len(bits) != length:
        warning = ("%s[%d][0b%s]: %d digits written for a code of %d symbols"
                   % (m.group(1), length, bits, len(bits), length))
    want = "".join("-" if b == "1" else "." for b in format(value, "0%db" % length))

    body = line.rstrip("\r\n")
    eol = line[len(body):]
    col = _comment_col(body)
    if col is None:                                   # no comment at all: add one
        return body.rstrip() + "   # " + want + eol, "", want, warning
    head, text = body[:col], body[col + 1:]           # text = everything after the #
    lead = text[:len(text) - len(text.lstrip(" "))]
    rest = text[len(lead):]
    pm = _PATTERN.match(rest)
    if not pm:                                        # a comment with no pattern: put it first
        return head + "# " + want + "   " + rest + eol, "", want, warning
    old = pm.group(0)
    if old == want:
        return None, None, None, warning
    after = rest[len(old):]
    gap = after[:len(after) - len(after.lstrip(" "))]
    tail = after[len(gap):]
    if tail and len(gap) >= 2:                        # keep the note after it in its column
        gap = " " * max(2, len(gap) + len(old) - len(want))
    return head + "#" + lead + want + gap + tail + eol, old, want, warning


def process(path, check):
    with io.open(path, encoding="utf-8-sig", newline="") as f:
        lines = f.read().splitlines(keepends=True)
    out, changes, warnings = [], [], []
    for n, line in enumerate(lines, 1):
        new, old, want, warn = _fix_line(line)
        if warn:
            warnings.append("  line %d: %s" % (n, warn))
        if new is None:
            out.append(line)
            continue
        out.append(new)
        key = _ASSIGN.match(line).group(0).rstrip("= \t")
        changes.append("  line %-4d %-22s %-10s ->  %s" % (n, key, old or "(none)", want))

    print("\n  %s" % path)
    if warnings:
        print("\n  Check these - the number itself looks wrong:")
        print("\n".join(warnings))
    if not changes:
        print("\n  Every comment already matches its code. Nothing to change.")
        return 0
    print("\n  %d comment(s) %s:\n" % (len(changes), "do not match" if check else "updated"))
    print("  %-9s %-22s %-10s     %s" % ("", "code", "comment said", "code says"))
    print("\n".join(changes))
    if check:
        print("\n  Nothing was changed (--check). Run it without --check to update them.")
        return len(changes)
    backup = "%s.before-comments-%s.bak" % (path, time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, backup)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write("".join(out))
    print("\n  Saved. The file as it was is kept as:\n    %s" % os.path.basename(backup))
    print("\n  If a NEW pattern above is not the one you meant, the number on that"
          "\n  line is wrong, not the comment - fix the number and run this again.")
    return len(changes)


def main():
    args = [a for a in sys.argv[1:] if a != "--check"]
    check = "--check" in sys.argv[1:]
    base = os.path.dirname(os.path.abspath(sys.argv[0] if getattr(sys, "frozen", False) else __file__))
    target = args[0] if args else base
    if os.path.isdir(target):
        target = os.path.join(target, "morse_map.py")
    print("=" * 68)
    print("  AeroMorse - make the comments in morse_map.py match the codes")
    print("=" * 68)
    if not os.path.isfile(target):
        print("\n  Not found: %s" % target)
        return 2
    process(target, check)
    print()
    return 0


def _pause():
    # A pause so the window doesn't vanish when double-clicked as an .exe.
    if getattr(sys, "frozen", False):
        try:
            input("  Press Enter to close...")
        except EOFError:
            pass


if __name__ == "__main__":
    _rc = main()
    _pause()
    sys.exit(_rc)
