#!/usr/bin/env python3
"""Cut an object out of a photo (BiRefNet-lite) and save a tight-cropped RGBA PNG.

    $HOME/.venvs/ghost-matte/bin/python tools/cutout_image.py <photo> <out.png> [--crop x0,y0,x1,y1] [--model lite|portrait] [--grow 0]

--crop takes fractions of the image (0..1) so you can isolate one object before matting.
Model weights: ~/.cache/ghost-matte/hf/BiRefNet_lite (general objects) or BiRefNet-portrait (people).
Runs on Apple MPS when available. The output is trimmed to the object's bounding box with a small margin.
"""
import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForImageSegmentation

HF = Path("~/.cache/ghost-matte/hf").expanduser()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--crop", default="0,0,1,1")
    ap.add_argument("--model", default="lite", choices=["lite", "portrait"])
    ap.add_argument("--grow", type=int, default=0, help="dilate the matte by N px (negative erodes)")
    ap.add_argument("--largest", action="store_true", help="keep only the largest connected object (drops stray bits)")
    a = ap.parse_args()

    im = Image.open(a.src).convert("RGB")
    x0, y0, x1, y1 = [float(v) for v in a.crop.split(",")]
    W, H = im.size
    im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    w, h = im.size

    d = HF / ("BiRefNet_lite" if a.model == "lite" else "BiRefNet-portrait")
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model = AutoModelForImageSegmentation.from_pretrained(str(d), trust_remote_code=True).to(dev).eval()

    S = 1024
    x = np.asarray(im.resize((S, S), Image.BILINEAR), dtype=np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    t = torch.from_numpy(x.transpose(2, 0, 1)).unsqueeze(0).to(dev)
    with torch.no_grad():
        pred = model(t)[-1].sigmoid().cpu()[0, 0].numpy()
    alpha = Image.fromarray((np.clip(pred, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)
    arr = np.asarray(alpha).astype(np.float32) / 255.0
    arr = np.clip((arr - 0.12) / 0.76, 0, 1)                 # firm up the edge a little
    if a.grow:
        import cv2
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * abs(a.grow) + 1,) * 2)
        arr = (cv2.dilate if a.grow > 0 else cv2.erode)(arr, k)
    if a.largest:
        import cv2
        m8 = (arr > 0.5).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(m8)
        if n > 2:
            keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            dil = cv2.dilate((lab == keep).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
            arr = arr * dil
    rgba = np.dstack([np.asarray(im), (arr * 255).astype(np.uint8)])
    out = Image.fromarray(rgba, "RGBA")
    bbox = out.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    if bbox:
        m = 6
        out = out.crop((max(0, bbox[0] - m), max(0, bbox[1] - m), min(w, bbox[2] + m), min(h, bbox[3] + m)))
    out.save(a.out)
    cov = float((arr > 0.5).mean())
    print(f"{a.out}  {out.size[0]}x{out.size[1]}  object covers {cov*100:.0f}% of the crop  (device {dev})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
