#!/usr/bin/env python3
"""Build the base cut: jump cuts + face-anchored punch-ins + grade + voice clean-up, from build/plan.json.

    python3 tools/build_base.py <reel_dir>

Writes <reel_dir>/build/base.mov (1080x1920, 30 fps, audio 48 kHz) padded with a held last frame / silence
for the end card. The raw clip is scaled to 1080x1920; zooms are anchored on the measured face centre so the
face never drifts while graphics are placed relative to plan.json -> face.
Runs ffmpeg with -nostdin and a hard timeout (ffmpeg 9.0.2 can hang on some graphs).
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    R = Path(sys.argv[1])
    plan = json.loads((R / "build" / "plan.json").read_text())
    FX = plan["face"]["cx"]
    FY = round((plan["face"]["top"] + plan["face"]["chin"]) / 2)
    segs = plan["segments"]
    vparts, aparts, order = [], [], []
    for i, s in enumerate(segs):
        a, e, d, z0, z1 = s["src_s"], s["src_e"], s["dur"], s["z0"], s["z1"]
        Z = f"({z0}+({z1}-{z0})*t/{d:.3f})"
        vparts.append(
            f"[0:v]trim=start={a}:end={e},setpts=PTS-STARTPTS,"
            f"scale=w='2*trunc(1080*{Z}/2)':h='2*trunc(1920*{Z}/2)':eval=frame:flags=lanczos,"
            f"crop=1080:1920:x='min(max(0,{FX}*(iw/1080)-{FX}),iw-1080)':y='min(max(0,{FY}*(ih/1920)-{FY}),ih-1920)',setsar=1[v{i}]")
        aparts.append(f"[0:a]atrim=start={a}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.02:.3f}:d=0.02[a{i}]")
        order.append(f"[v{i}][a{i}]")
    hold = plan["total"] - plan["speech_end"]
    fc = ";".join(vparts + aparts)
    fc += f";{''.join(order)}concat=n={len(segs)}:v=1:a=1[vc][ac]"
    fc += (f";[vc]tpad=stop_mode=clone:stop_duration={hold:.3f},fps=30,"
           "unsharp=5:5:0.7:5:5:0.0,eq=contrast=1.06:saturation=1.08:gamma=0.98,"
           "colorbalance=rs=0.02:gs=0.0:bs=-0.03:rm=0.015:bm=-0.02,"
           "vignette=angle=PI/5:mode=forward,noise=alls=3:allf=t,format=yuv420p[vout]")
    fc += (f";[ac]highpass=f=80,afftdn=nf=-28,equalizer=f=3500:t=q:w=1.2:g=2,"
           "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
           f"apad=pad_dur={hold:.3f},aresample=48000[aout]")
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(R / "raw" / "raw.mp4"), "-filter_complex", fc,
           "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
           "-c:a", "pcm_s16le", str(R / "build" / "base.mov")]
    try:
        subprocess.run(cmd, check=True, timeout=900)
    except subprocess.TimeoutExpired:
        print("FAIL: ffmpeg did not finish within 15 min (killed)")
        return 1
    print(f"ok -> {R/'build'/'base.mov'}  (anchor {FX},{FY}; hold {hold:.2f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
