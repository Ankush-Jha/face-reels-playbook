#!/usr/bin/env python3
"""Collect every piece of text that is actually VISIBLE on screen across a reel's graphics timeline.

    $HOME/.venvs/media/bin/python tools/onscreen_text.py <reel_dir> [--step 0.2]

Seeks the built overlay through the whole timeline and records the visible text (innerText skips hidden elements).
Writes <reel_dir>/build/onscreen_text.txt (one distinct line per row, with first-seen time) and lists every
number it contains, so numbers/claims can be traced to the transcript or a client-supplied source.
Use it as the input of tools/compliance_check.py (it avoids false alarms from config text embedded in the page).
"""
import asyncio
import json
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright


async def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    reel = Path(sys.argv[1]).resolve()
    step = float(sys.argv[sys.argv.index("--step") + 1]) if "--step" in sys.argv else 0.2
    plan = json.loads((reel / "build" / "plan.json").read_text())
    seen = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--disable-gpu"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        name = sys.argv[sys.argv.index("--html") + 1] if "--html" in sys.argv else "overlay"
        await pg.goto("file://" + str(reel / "build" / (name + "_built.html")))
        await pg.evaluate("document.fonts.ready")
        t = 0.0
        while t <= plan["total"]:
            await pg.evaluate(f"seek({t})")
            txt = await pg.evaluate("""() => { const out=[]; const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
                while(w.nextNode()){const n=w.currentNode, s=(n.textContent||'').trim(); if(!s) continue; const el=n.parentElement; if(!el) continue;
                  let ok=true,e=el; while(e&&e!==document.body){const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.display==='none'||parseFloat(cs.opacity)<0.25){ok=false;break;} e=e.parentElement;}
                  if(ok) out.push(s);} return out; }""")
            for s in txt:
                seen.setdefault(re.sub(r"\s+", " ", s), round(t, 2))
            t += step
        await b.close()
    lines = [f"{t:6.2f}  {s}" for s, t in sorted(seen.items(), key=lambda kv: kv[1])]
    (reel / "build" / "onscreen_text.txt").write_text("\n".join(s for s in seen) + "\n")
    print("\n".join(lines))
    nums = sorted({m for s in seen for m in re.findall(r"[\d][\d,.\-#]*", s)})
    print("\nNUMBERS / IDS ON SCREEN (each must be traceable: licence, phone, address or transcript):", nums)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
