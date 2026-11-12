#!/usr/bin/env python3
"""Build a reel's sound-effects track and music bed from the ghost-editor library.

    $HOME/.venvs/media/bin/python tools/mix_sound.py <reel_dir>

Reads  <reel_dir>/build/sound.json:
   {"music": "forest-mist-whispers", "music_start": 0, "music_gain": 1.0,
    "events": [{"t": 1.2, "sfx": "paper-flip", "gain": 0.6}, ...]}
       sfx name = a file in vendor/ghost-editor/library/sfx/<name>.wav (or cc0-<name>.wav)
Writes <reel_dir>/build/sfx.wav and music.wav (48 kHz stereo, length = plan total), levelled for the final mix
(compose.py ducks the music under the voice and normalises to -14 LUFS).
Licences: Mixkit free licence (commercial OK; not for Content ID registration) and CC0 clips.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import scipy.io.wavfile as wav
from scipy.signal import resample_poly

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "vendor" / "ghost-editor" / "library"
SR = 48000


def load(path: Path) -> np.ndarray:
    sr, x = wav.read(str(path))
    x = x.astype(np.float32)
    x = x / (32768.0 if x.dtype != np.float32 or np.abs(x).max() > 1.5 else 1.0)
    if x.ndim == 2:
        x = x.mean(axis=1)
    if sr != SR:
        g = np.gcd(sr, SR)
        x = resample_poly(x, SR // g, sr // g)
    return x


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    reel = Path(sys.argv[1])
    b = reel / "build"
    plan = json.loads((b / "plan.json").read_text())
    cfg = json.loads((b / "sound.json").read_text())
    N = int((plan["total"] + 0.5) * SR)

    sfx = np.zeros(N, np.float32)
    missing = []
    for ev in cfg["events"]:
        name = ev["sfx"]
        f = next((p for p in (LIB / "sfx" / f"{name}.wav", LIB / "sfx" / f"cc0-{name}.wav") if p.exists()), None)
        if not f:
            missing.append(name)
            continue
        x = load(f)
        mx = ev.get("max_len")
        if mx:
            x = x[: int(mx * SR)] * np.linspace(1, 0, min(len(x), int(mx * SR)), dtype=np.float32) ** 0.5
        x = x / (np.abs(x).max() + 1e-9) * ev.get("gain", 0.6)
        i = int(max(0, ev["t"]) * SR)
        j = min(N, i + len(x))
        if j > i:
            sfx[i:j] += x[: j - i]
    if missing:
        print("WARNING missing sfx:", sorted(set(missing)))

    # music bed
    mp3 = LIB / "music" / f"{cfg['music']}.mp3"
    tmp = b / "_music_raw.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(cfg.get("music_start", 0)), "-i", str(mp3),
                    "-t", str(plan["total"] + 1), "-ac", "1", "-ar", str(SR), str(tmp)], check=True, timeout=120)
    m = load(tmp)
    tmp.unlink()
    m = np.pad(m, (0, max(0, N - len(m))))[:N]
    t = np.arange(N) / SR
    m *= np.minimum(1, t / 1.2) * np.minimum(1, np.maximum(0, (plan["total"] - t) / 1.8))   # fade in / out
    m = m / (np.abs(m).max() + 1e-9) * 0.8 * cfg.get("music_gain", 1.0)

    def save(path, x):
        st = np.stack([x, x], axis=1)
        wav.write(str(path), SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))

    save(b / "sfx.wav", np.clip(sfx, -1, 1))
    save(b / "music.wav", m)
    print(f"sfx.wav ({len(cfg['events'])} events) and music.wav ({cfg['music']}) written, {N/SR:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
