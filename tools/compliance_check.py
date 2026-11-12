#!/usr/bin/env python3
"""Check a reel's on-screen text against its client's compliance.json.

    python3 tools/compliance_check.py <client-slug> <reel-folder-or-file> [more paths...]

It reads the reel's SOURCE text (overlay/composition HTML, reel.json, captions,
SRT, scripts) and checks:
  - every string in require_all_strings appears
  - the require_disclaimer sentence appears (whitespace-insensitive)
  - no forbid_patterns word appears
  - compliance.json has been filled in (no template placeholders left)

Exit code 0 = pass, 1 = fail. This checks the source, not the rendered pixels:
after rendering, also look at the real end-card frame (and run an OCR check if
available) because text can still be clipped, too small or off-screen.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_EXT = {".html", ".htm", ".json", ".srt", ".vtt", ".txt", ".md", ".tsx", ".ts", ".js", ".mjs", ".py"}
SKIP_DIRS = {"node_modules", ".git", "frames", "out", "raw", "broll"}
PLACEHOLDER = "exact text that MUST"


def norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)             # strip tags
    s = re.sub(r"&nbsp;|&#160;", " ", s)
    s = s.replace("&amp;", "&").replace("’", "'").replace("‑", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def gather(paths):
    chunks = []
    for p in map(Path, paths):
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file()]
        for f in files:
            if f.suffix.lower() in TEXT_EXT and not (set(f.parts) & SKIP_DIRS) and f.stat().st_size < 3_000_000:
                try:
                    chunks.append(f.read_text(encoding="utf-8", errors="ignore"))
                except OSError:
                    pass
    return norm("\n".join(chunks))


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    slug, paths = sys.argv[1], sys.argv[2:]
    cfile = ROOT / "clients" / slug / "compliance.json"
    if not cfile.exists():
        print(f"FAIL no compliance.json for client '{slug}'")
        return 1
    c = json.loads(cfile.read_text(encoding="utf-8"))
    text = gather(paths)
    fails, ok = [], []

    if any(PLACEHOLDER in s for s in c.get("require_all_strings", [])) or not c.get("require_disclaimer"):
        fails.append("compliance.json still has template placeholders / no disclaimer: fill it in with the client first")
    for s in c.get("require_all_strings", []):
        if PLACEHOLDER in s:
            continue
        (ok if norm(s) in text else fails).append(f"required text {'present' if norm(s) in text else 'MISSING'}: {s}")
    d = c.get("require_disclaimer", "")
    if d:
        (ok if norm(d) in text else fails).append(f"disclaimer {'present' if norm(d) in text else 'MISSING'}: {d[:70]}...")
    for pat in c.get("forbid_patterns", []):
        if re.search(r"\b" + re.escape(pat.lower()) + r"\b", text):
            fails.append(f"forbidden phrase found: '{pat}'")
    for line in ok:
        print("PASS", line)
    for line in fails:
        print("FAIL", line)
    print(f"\n{'COMPLIANCE SOURCE CHECK PASSED' if not fails else 'COMPLIANCE SOURCE CHECK FAILED'} (source text only; also inspect the rendered end card)")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
