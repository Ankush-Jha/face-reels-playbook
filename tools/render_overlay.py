#!/usr/bin/env python3
"""Render a reel's transparent graphics layer frame by frame (Playwright + Chromium, several pages in parallel).

    $HOME/.venvs/media/bin/python tools/render_overlay.py <reel_dir> stills 1.0,5.5,12 [--out qa]
    $HOME/.venvs/media/bin/python tools/render_overlay.py <reel_dir> all [--workers 4]

Reads  <reel_dir>/build/overlay.html (or --html NAME)  (a template using __PLAN__ __CLIENT__ __BRAND__ __COMPLIANCE__)
Writes <reel_dir>/build/overlay_built.html, then PNGs: build/qa/ov_*.png (stills) or build/frames/%05d.png (all; --frames DIR to change).
The template exposes window.seek(t); every frame is a pure function of t, so frames are deterministic.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
FPS = 30


def build_html(reel: Path, name: str = "overlay.html") -> Path:
    b = reel / "build"
    client_dir = reel.parent.parent
    html = (b / name).read_text()
    for key, data in {
        "__PLAN__": json.loads((b / "plan.json").read_text()),
        "__CLIENT__": json.loads((client_dir / "client.json").read_text()),
        "__BRAND__": json.loads((client_dir / "brand" / "brand.json").read_text()),
        "__COMPLIANCE__": json.loads((client_dir / "compliance.json").read_text()),
    }.items():
        html = html.replace(key, json.dumps(data))
    out = b / (name.replace(".html", "") + "_built.html")
    out.write_text(html)
    return out


async def worker(browser, url, jobs, outdir, name):
    pg = await browser.new_page(viewport={"width": 1080, "height": 1920})
    await pg.goto(url)
    await pg.evaluate("document.fonts.ready")
    await pg.wait_for_timeout(600)
    for t, fn in jobs:
        await pg.evaluate(f"seek({t})")
        await pg.screenshot(path=str(outdir / fn), omit_background=True)
    await pg.close()


async def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    reel, mode = Path(sys.argv[1]).resolve(), sys.argv[2]
    name = sys.argv[sys.argv.index("--html") + 1] if "--html" in sys.argv else "overlay.html"
    fdir = sys.argv[sys.argv.index("--frames") + 1] if "--frames" in sys.argv else "frames"
    built = build_html(reel, name)
    plan = json.loads((reel / "build" / "plan.json").read_text())
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 4
    if mode == "stills":
        ts = [float(x) for x in sys.argv[3].split(",")]
        outdir = reel / "build" / (sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "qa")
        jobs = [(t, f"ov_{t:06.2f}.png") for t in ts]
        workers = 1
    else:
        outdir = reel / "build" / fdir
        n = int(round(plan["total"] * FPS))
        jobs = [(i / FPS, f"{i:05d}.png") for i in range(n)]
    outdir.mkdir(parents=True, exist_ok=True)
    chunks = [jobs[k::workers] for k in range(workers)]
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--disable-gpu", "--force-device-scale-factor=1"])
        await asyncio.gather(*[worker(browser, "file://" + str(built), c, outdir, k) for k, c in enumerate(chunks) if c])
        await browser.close()
    print(f"rendered {len(jobs)} frame(s) -> {outdir}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
