#!/usr/bin/env python3
"""
build_pdfs.py — regenerate the three AeroMorse printables from their sources.

  AEROMORSE_BUILD_GUIDE.pdf         <- AEROMORSE_BUILD_GUIDE.md
  AeroMorse Cheat Sheet.pdf         <- aeromorse_cheatsheet.htm  (+ morse_map.py)
  AeroMorse — Keycode Reference.pdf <- keycode_reference.htm

Run it after editing any of those sources (double-click Build PDFs.bat, or
`python build_pdfs.py`). Pass one of  guide | cheatsheet | keycode  to rebuild
just one. Needs Microsoft Edge (for headless PDF printing) and the `markdown`
package (auto-installed on first run if missing).

Nothing here is loaded on the device — these are PC-side documents.
"""
import os, sys, subprocess, time, functools, http.server, socketserver, threading

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
    """Drive Edge/Chrome headless to render `url` to `out` (a PDF path)."""
    if os.path.exists(out):
        try: os.remove(out)
        except OSError: pass
    cmd = [_edge(), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--run-all-compositor-stages-before-draw", *extra,
           "--print-to-pdf=%s" % out, url]
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    for _ in range(30):
        if os.path.exists(out) and os.path.getsize(out) > 0:
            return True
        time.sleep(0.5)
    return False

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

def build_guide():
    try:
        import markdown
    except ImportError:
        print("  installing 'markdown' (one-time)...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "markdown"])
        import markdown
    md_path = os.path.join(REPO, "AEROMORSE_BUILD_GUIDE.md")
    out = os.path.join(REPO, "AEROMORSE_BUILD_GUIDE.pdf")
    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists"])
    body = md.convert(open(md_path, encoding="utf-8").read())
    html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>AeroMorse Build Guide</title>"
            "<style>%s</style></head><body><div class='toc-box'>"
            "<div class='toctitle'>Contents</div>%s</div>%s</body></html>"
            % (_CSS, md.toc, body))
    tmp = os.path.join(REPO, "_build_guide.tmp.html")
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

TARGETS = {"guide": build_guide, "cheatsheet": build_cheatsheet, "keycode": build_keycode}

def main():
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
