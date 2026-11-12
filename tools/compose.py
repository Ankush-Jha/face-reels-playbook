#!/usr/bin/env python3
"""Compose the final reel: base cut + graphics frames + mixed audio -> out/<name>.mp4

    python3 tools/compose.py <reel_dir> <output_name_without_ext> [--broll] [--behind] [--frames DIR]

Video: build/base.mov + build/frames/%05d.png (+ optional B-roll via broll.json, in a SEPARATE first pass because
ffmpeg 9.0.2 can deadlock when B-roll overlays and a PNG-sequence overlay share one filter graph).
Audio: voice from base.mov, build/sfx.wav, build/music.wav; music ducked under the voice (sidechain), loudness
normalised to -14 LUFS / -1.5 dBTP. Every ffmpeg call: -nostdin and a hard timeout.
"""
import json
import subprocess
import sys
from pathlib import Path


def run(cmd, timeout):
    try:
        subprocess.run(cmd, check=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print("FAIL: ffmpeg exceeded", timeout, "s and was killed:", " ".join(cmd[:8]), "...")
        raise SystemExit(1)


def main() -> int:
    argv = sys.argv[1:]
    fdir = argv[argv.index("--frames") + 1] if "--frames" in argv else "frames"
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and not (i > 0 and argv[i - 1] == "--frames")]
    if len(args) != 2:
        print(__doc__)
        return 2
    R, name = Path(args[0]), args[1]
    B = R / "build"
    plan = json.loads((B / "plan.json").read_text())
    TOT = plan["total"]
    NF = str(round(TOT * 30))
    (R / "out").mkdir(exist_ok=True)
    base = str(B / "base.mov")

    if "--broll" in sys.argv:
        BR = json.loads((R / "broll.json").read_text())
        ins = ["-i", base]
        for b in BR:
            ins += ["-i", str(R / b["file"])]
        fc, last = [], "[0:v]"
        for k, b in enumerate(BR):
            d, s = b["dur"], b["start"]
            fc.append(f"[{k+1}:v]trim=0:{d},setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,"
                      f"format=yuva420p,fade=t=in:st=0:d=0.12:alpha=1,fade=t=out:st={d-0.12:.2f}:d=0.12:alpha=1,setpts=PTS+{s}/TB[b{k}]")
            fc.append(f"{last}[b{k}]overlay=eof_action=pass[o{k}]")
            last = f"[o{k}]"
        fc.append(f"{last}format=yuv420p[v]")
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-an", "-frames:v", NF,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", str(B / "pass1.mp4")], 900)
        under = str(B / "pass1.mp4")
    elif "--behind" in sys.argv:
        # words BEHIND the speaker: base video -> big words (frames_behind) -> person cut-out (matte webm with alpha) on top
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", base, "-framerate", "30", "-i", str(B / "frames_behind" / "%05d.png"),
             "-c:v", "libvpx-vp9", "-i", str(B / "matte_behind.webm"),
             "-filter_complex", "[0:v][1:v]overlay=format=auto:shortest=0[a];[a][2:v]overlay=format=auto:shortest=0,format=yuv420p[v]",
             "-map", "[v]", "-an", "-frames:v", NF, "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", str(B / "pass1.mp4")], 900)
        under = str(B / "pass1.mp4")
    else:
        under = base

    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", under, "-framerate", "30", "-i", str(B / fdir / "%05d.png"),
         "-filter_complex", "[0:v][1:v]overlay=format=auto:shortest=1,format=yuv420p[v]", "-map", "[v]", "-an", "-frames:v", NF, "-r", "30",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", str(B / "video_only.mp4")], 1200)

    af = ("[0:a]asplit[v1][v2];[2:a]volume=0.28[m];[m][v1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[md];"
          "[1:a]volume=0.55[sx];[v2][md][sx]amix=inputs=3:normalize=0:duration=longest,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11,apad,atrim=0:{TOT}[a]")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", base, "-i", str(B / "sfx.wav"), "-i", str(B / "music.wav"),
         "-filter_complex", af, "-map", "[a]", "-c:a", "aac", "-b:a", "192k", str(B / "mix.m4a")], 600)

    out = R / "out" / f"{name}.mp4"
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(B / "video_only.mp4"), "-i", str(B / "mix.m4a"),
         "-c", "copy", "-shortest", "-movflags", "+faststart", str(out)], 300)
    print("done ->", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
