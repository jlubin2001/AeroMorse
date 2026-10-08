#!/usr/bin/env python3
"""
build_pdfs.py — regenerate the three AeroMorse printables from their sources.

  AEROMORSE_BUILD_GUIDE.pdf         <- AEROMORSE_BUILD_GUIDE.md
  AeroMorse Cheat Sheet.pdf         <- aeromorse_cheatsheet.htm  (+ morse_map.py)
  AeroMorse — Keycode Reference.pdf <- keycode_reference.htm

Run it after editing any of those sources (double-click Build PDFs.bat, or
`python build_pdfs.py`). Pass one of  guide | cheatsheet | keycode  to rebuild
just one. `python build_pdfs.py --folder <dir>` prints a PERSONAL cheat sheet
from the morse_map.py in <dir> (see "Build my cheat sheet.bat"). Needs Microsoft Edge (for headless PDF printing) and the `markdown`
package (auto-installed on first run if missing).

Nothing here is loaded on the device — these are PC-side documents.
"""
import os, re, sys, subprocess, time, functools, http.server, socketserver, threading

REPO = os.path.dirname(os.path.abspath(__file__))
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

def _edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    sys.exit("ERROR: Microsoft Edge (or Chrome) not found — needed to make PDFs.")

def _print_to_pdf(url, out, extra=()):
    """Drive Edge/Chrome headless to render `url` to `out` (a PDF path).

    Printed to a temporary file first and then moved over `out`, so a PDF that
    is open in a viewer (Acrobat locks it) is reported as NOT updated instead
    of silently leaving the old one in place and calling it a success."""
    tmp = out + ".building.pdf"
    if os.path.exists(tmp):
        try: os.remove(tmp)
        except OSError: pass
    cmd = [_edge(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw", *extra,
           "--print-to-pdf=%s" % tmp, url]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    for _ in range(30):
        if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            break
        time.sleep(0.5)
    else:
        return False
    try:
        os.replace(tmp, out)
    except OSError:
        print("\n  *** %s is open in another program (e.g. Acrobat), so it could NOT be\n"
              "  *** replaced. Close it and run this again. The new version was saved as:\n"
              "  ***   %s\n" % (os.path.basename(out), tmp))
        return False
    return True

def _pages(path):
    try:
        import pypdf
        return len(pypdf.PdfReader(path).pages)
    except Exception:
        return "?"

# ── 1. Build Guide: Markdown -> styled HTML -> PDF ───────────────────────────
_CSS = """
@page { size: Letter; margin: 0.75in 0.7in; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #1a1a1a; }
h1,h2,h3,h4 { color: #1f3a5f; line-height: 1.25; margin: 1.1em 0 0.4em; page-break-after: avoid; }
h1 { font-size: 22pt; border-bottom: 3px solid #1f3a5f; padding-bottom: 6px; }
h2 { font-size: 16pt; border-bottom: 1px solid #ccd6e0; padding-bottom: 4px; margin-top: 1.4em; }
h3 { font-size: 13pt; } h4 { font-size: 11.5pt; color: #33506e; }
a { color: #1462b8; text-decoration: none; word-break: break-word; }
code { font-family: Consolas,"Courier New",monospace; font-size: 0.9em; background: #eef1f4; padding: 0.08em 0.34em; border-radius: 3px; }
pre { background: #f4f6f8; border: 1px solid #d8dee4; border-radius: 5px; padding: 9px 12px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; font-size: 9pt; line-height: 1.4; }
blockquote { border-left: 4px solid #f0b429; background: #fff9e9; margin: 0.8em 0; padding: 8px 14px; border-radius: 0 5px 5px 0; page-break-inside: avoid; }
blockquote p { margin: 0.3em 0; }
table { border-collapse: collapse; width: 100%; margin: 0.8em 0; font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #cdd5dd; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #eef2f6; }
hr { border: none; border-top: 1px solid #d0d0d0; margin: 1.4em 0; }
ul, ol { padding-left: 1.5em; }
.toc-box { background: #f6f8fa; border: 1px solid #dde3e9; border-radius: 6px; padding: 10px 18px; margin: 0 0 1.6em; font-size: 9.5pt; page-break-after: always; }
.toc-box > .toctitle { font-weight: bold; font-size: 12pt; color: #1f3a5f; }
.toc-box ul { list-style: none; padding-left: 1em; margin: 4px 0; }
.toc-box > ul { padding-left: 0; }
.toc-box a { color: #33506e; }
"""

_LIST_RE = re.compile(r"(?:[-*+] |\d+\. )")

def _like_github(text):
    """Make the `markdown` library read the guides the way GitHub shows them.
    Two differences otherwise spoil the PDF:
      - a wrapped line that happens to start with a part number ("#5477). ...")
        becomes a giant heading, because the library does not need a space
        after the "#";
      - a list that follows a paragraph line with no blank line between
        ("**Before you can use BLE:**" then "- ...") is run into the paragraph;
      - a list nested inside another with 1-3 spaces of indent is run into
        its parent item, because the library wants 4.
    Code blocks are left alone."""
    out, fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence:
            m = (re.match(r"((?:> ?)*)#+[^#\s]", line)   # also inside a "> " note
                 or re.match(r"((?:> ?)* *(?:[-*+] |\d+\. ))#\d", line))  # "- #3885 ..."
            if m:
                line = m.group(1) + "\\" + line[m.end(1):]
            if re.match(r" {1,3}(?:[-*+] |\d+\. )", line):
                line = "    " + line.lstrip(" ")       # nested list: 4 spaces
            elif _LIST_RE.match(line) and out:
                prev = out[-1]
                if (prev.strip() and not prev.startswith((" ", "\t", ">", "|", "#"))
                        and not _LIST_RE.match(prev)):
                    out.append("")
        out.append(line)
    return "\n".join(out)

def build_guide(name="AEROMORSE_BUILD_GUIDE", title="AeroMorse Build Guide", toc=True):
    try:
        import markdown
    except ImportError:
        print("  installing 'markdown' (one-time)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "markdown"])
        import markdown
    md_path = os.path.join(REPO, name + ".md")
    out = os.path.join(REPO, name + ".pdf")
    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists"],
                           extension_configs={"toc": {"toc_depth": "2-6"}})   # not the title itself
    body = md.convert(_like_github(open(md_path, encoding="utf-8").read()))
    if toc:
        # The title and introduction come first; the detailed contents list then
        # takes the place of the guide's own short "Table of Contents" section.
        # (It used to be printed in front of the title page.)
        # Drop the entries for the subtitle and for that section itself.
        entries = re.sub(r'<li>(?:(?!<li>).)*?</li>\s*(?=<li><a href="#table-of-contents">)', "", md.toc, flags=re.S)
        entries = re.sub(r'<li><a href="#table-of-contents">.*?</a></li>\s*', "", entries, flags=re.S)
        box = ("<div class='toc-box' style='page-break-before: always'>"
               "<div class='toctitle'>Contents</div>%s</div>" % entries)
        own = re.search(r'<h2 id="table-of-contents">.*?(?=<hr)', body, flags=re.S)
        if own:
            body = body[:own.start()] + box + body[own.end():]
        else:
            body = box + body
    html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>%s</title>"
            "<style>%s</style></head><body>%s</body></html>"
            % (title, _CSS, body))
    tmp = os.path.join(REPO, "_%s.tmp.html" % name)
    open(tmp, "w", encoding="utf-8").write(html)
    ok = _print_to_pdf("file:///%s" % tmp.replace("\\", "/"), out)
    try: os.remove(tmp)
    except OSError: pass
    return out, ok

# ── 2. Cheat sheet: htm auto-loads morse_map.py — needs a local server ───────
def build_cheatsheet():
    out = os.path.join(REPO, "AeroMorse Cheat Sheet.pdf")
    port = 8799
    os.chdir(REPO)
    class _Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):  # don't spam the console with request logs
            pass
    httpd = socketserver.TCPServer(("127.0.0.1", port), _Quiet)
    httpd.timeout = 1
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    try:
        ok = _print_to_pdf("http://127.0.0.1:%d/aeromorse_cheatsheet.htm" % port, out,
                           extra=("--virtual-time-budget=12000",))
    finally:
        httpd.shutdown()
    return out, ok

# ── 3. Keycode reference: self-contained htm, render straight from file:// ───
def build_keycode():
    htm = os.path.join(REPO, "keycode_reference.htm")
    out = os.path.join(REPO, "AeroMorse \u2014 Keycode Reference.pdf")
    ok = _print_to_pdf("file:///%s" % htm.replace("\\", "/"), out)
    return out, ok

def build_usage():
    return build_guide("AEROMORSE_USAGE_GUIDE", "AeroMorse Usage Guide", toc=False)

def build_switchmode():
    return build_guide("AEROMORSE_SWITCH_MODE_GUIDE", "AeroMorse Switch Mode Guide", toc=False)

TARGETS = {"guide": build_guide, "usage": build_usage, "switchmode": build_switchmode,
           "cheatsheet": build_cheatsheet, "keycode": build_keycode}

def build_my_cheatsheet(folder):
    """Personal cheat sheet: print from the morse_map.py in `folder` (e.g. your
    edit folder) instead of the repo's default map. The latest cheat-sheet page
    is copied in from the repo first; the PDF is written to `folder`."""
    global REPO
    import shutil
    if not os.path.exists(os.path.join(folder, "morse_map.py")):
        sys.exit("ERROR: no morse_map.py in %s" % folder)
    shutil.copyfile(os.path.join(REPO, "aeromorse_cheatsheet.htm"),
                    os.path.join(folder, "aeromorse_cheatsheet.htm"))
    REPO = folder
    return build_cheatsheet()

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--folder":
        folder = os.path.abspath(sys.argv[2])
        print("Building your cheat sheet from %s\\morse_map.py ...\n" % folder)
        out, ok = build_my_cheatsheet(folder)
        if ok:
            print("  OK  %s  (%s pages)" % (out, _pages(out)))
        else:
            print("  FAILED - is the PDF open in another program? Close it and try again.")
        sys.exit(0 if ok else 1)
    which = sys.argv[1:] or list(TARGETS)
    bad = [w for w in which if w not in TARGETS]
    if bad:
        sys.exit("Unknown target(s): %s. Use: %s" % (", ".join(bad), " | ".join(TARGETS)))
    print("Building AeroMorse PDFs...\n")
    failed = 0
    for name in which:
        print("  %-11s ..." % name, end=" ", flush=True)
        out, ok = TARGETS[name]()
        if ok:
            print("OK  (%s, %s pages, %d KB)"
                  % (os.path.basename(out), _pages(out), os.path.getsize(out) // 1024))
        else:
            print("FAILED"); failed += 1
    print("\nDone." if not failed else "\n%d PDF(s) failed." % failed)
    if getattr(sys, "frozen", False):
        try: input("\nPress Enter to close...")
        except EOFError: pass
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
