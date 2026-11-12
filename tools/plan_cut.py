#!/usr/bin/env python3
"""Turn a raw talking-head take into a cut plan: clean word timings + silence-trimmed segments + punch-in zooms.

    python3 tools/plan_cut.py <reel_dir> [--end-card 4.0] [--max-pause 0.30] [--keep-pause 0.16]

Reads  <reel_dir>/raw/raw.mp4, <reel_dir>/build/words_dtw.json (whisper.cpp --dtw token times),
       <reel_dir>/build/face/face.json (tools/face_data.py)
Writes <reel_dir>/build/plan.json:
   segments  [{src_s, src_e, out_s, dur, z0, z1}]      kept raw ranges, mapped onto the output timeline
   words     [{i, w, s, e}]                            word times on the OUTPUT timeline
   face      {cx, top, chin} median face geometry in 1080x1920 output pixels
   speech_end, total
Why: whisper's plain word times are unreliable (it can place words inside silence). DTW token times plus the
measured audio energy fix that; pauses longer than --max-pause are shortened to --keep-pause.
"""
import argparse
import json
import math
import re
import statistics
import subprocess
import sys
import wave
import struct
from pathlib import Path

ZOOMS = [(1.00, 1.04), (1.10, 1.13), (1.00, 1.03), (1.14, 1.14), (1.05, 1.10), (1.12, 1.12)]
DTW_LAG = 0.13   # t_dtw sits ~0.13 s after the audible onset of a token


def rms_db(x, sr, a, b):
    seg = x[int(a * sr):int(b * sr)]
    if not seg:
        return -99.0
    return 20 * math.log10(max(1e-9, (sum(v * v for v in seg) / len(seg)) ** 0.5 / 32768))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("reel")
    ap.add_argument("--end-card", type=float, default=4.0)
    ap.add_argument("--max-pause", type=float, default=0.30)
    ap.add_argument("--keep-pause", type=float, default=0.16)
    ap.add_argument("--floor-db", type=float, default=-40.0)
    a = ap.parse_args()
    R = Path(a.reel)
    B = R / "build"

    # ---- words from DTW tokens ----
    d = json.loads((B / "words_dtw.json").read_text())
    toks = [(t["t_dtw"] / 100.0 if t.get("t_dtw", -1) >= 0 else None, t["text"])
            for s in d["transcription"] for t in s["tokens"] if not t["text"].startswith("[_")]
    words, last_t = [], 0.0
    for t, txt in toks:
        if t is None:
            t = last_t                           # token without alignment: reuse the previous token's time
        last_t = t
        if txt.startswith(" ") or not words:
            words.append({"w": txt.strip(), "t": t})
        else:
            words[-1]["w"] += txt                # sub-word piece or punctuation joins the previous word
            if not re.fullmatch(r"[?.,!:;]+", txt.strip()):
                words[-1]["t"] = min(words[-1]["t"], t)
    # optional human corrections: build/corrections.json = {"heard text": "right text"} applied to whole words
    cf = B / "corrections.json"
    if cf.exists():
        fixes = json.loads(cf.read_text())
        for w in words:
            if w["w"] in fixes:
                w["w"] = fixes[w["w"]]
    # a bare "?" / "." token may come BEFORE its own timing; make sure times are monotonic
    starts = []
    for i, w in enumerate(words):
        s = max(w["t"] - DTW_LAG, (starts[-1] + 0.05) if starts else 0.0)
        starts.append(s)
    for i, w in enumerate(words):
        w["s"] = starts[i]
        nxt = starts[i + 1] if i + 1 < len(words) else starts[i] + 0.5
        w["e"] = min(nxt, w["s"] + 0.9)

    # ---- audio energy: speech onset / end and silences ----
    wf = wave.open(str(B / "audio16k.wav"))
    sr, n = wf.getframerate(), wf.getnframes()
    x = struct.unpack("<%dh" % n, wf.readframes(n))
    hop = 0.02
    voiced = [rms_db(x, sr, i * hop, i * hop + 0.04) > a.floor_db for i in range(int(n / sr / hop))]
    first = next(i for i, v in enumerate(voiced) if v) * hop
    last = (len(voiced) - 1 - next(i for i, v in enumerate(reversed(voiced)) if v)) * hop + 0.04
    # silences >= max_pause inside the speech
    sil, i = [], 0
    while i < len(voiced):
        if not voiced[i]:
            j = i
            while j < len(voiced) and not voiced[j]:
                j += 1
            if i * hop > first and j * hop < last and (j - i) * hop >= a.max_pause:
                sil.append((i * hop, j * hop))
            i = j
        else:
            i += 1

    # ---- segments: keep speech, shorten long silences to keep_pause ----
    pad = a.keep_pause / 2
    t0 = max(0.0, first - 0.12)
    t1 = last + 0.30
    segs, cur = [], t0
    for s, e in sil:
        segs.append((cur, s + pad))
        cur = e - pad
    segs.append((cur, t1))
    segs = [(x0, x1) for x0, x1 in segs if x1 - x0 > 0.25]
    out, t = [], 0.0
    for k, (x0, x1) in enumerate(segs):
        z0, z1 = ZOOMS[k % len(ZOOMS)]
        out.append({"src_s": round(x0, 3), "src_e": round(x1, 3), "out_s": round(t, 3), "dur": round(x1 - x0, 3),
                    "z0": z0, "z1": z1})
        t += x1 - x0

    def to_out(tt):
        for sgm in out:
            if sgm["src_s"] - 0.001 <= tt <= sgm["src_e"] + 0.001:
                return sgm["out_s"] + (tt - sgm["src_s"])
        # inside a cut pause: snap to the start of the next kept segment
        for sgm in out:
            if tt < sgm["src_s"]:
                return sgm["out_s"]
        return out[-1]["out_s"] + out[-1]["dur"]

    ow = []
    for i, w in enumerate(words):
        s, e = to_out(w["s"]), to_out(w["e"])
        ow.append({"i": i, "w": w["w"], "s": round(s, 3), "e": round(max(e, s + 0.12), 3)})
    speech_end = round(t, 3)

    # ---- face geometry in 1080x1920 output pixels ----
    fj = json.loads((B / "face" / "face.json").read_text())
    k = 1080 / fj["width"]
    ok = [f for f in fj["frames"] if f["ok"]]
    face = {"cx": round(statistics.median(f["cx"] for f in ok) * k),
            "top": round(statistics.median(f["top_y"] for f in ok) * k),
            "chin": round(statistics.median(f["chin_y"] for f in ok) * k)}

    plan = {"segments": out, "words": ow, "face": face, "speech_end": speech_end,
            "total": round(speech_end + a.end_card, 3), "first_onset": round(first, 2), "last_voiced": round(last, 2),
            "trimmed_pauses": [(round(s, 2), round(e, 2)) for s, e in sil]}
    (B / "plan.json").write_text(json.dumps(plan, indent=1))
    print(f"speech {first:.2f}-{last:.2f}s raw -> {speech_end:.2f}s kept in {len(out)} segments; "
          f"{len(sil)} long pauses shortened; total with end card {plan['total']:.2f}s")
    print("face (1080x1920 px):", face)
    return 0


if __name__ == "__main__":
    sys.exit(main())
