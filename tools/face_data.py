#!/usr/bin/env python3
"""Per-frame face box + person matte for a talking-head clip (MediaPipe).

    $HOME/.venvs/media/bin/python tools/face_data.py <video> <out_dir>

Writes:
  <out_dir>/face.json      {fps, width, height, frames:[{i,t,ok,box:[x0,y0,x1,y1],chin_y,top_y,cx}]} in pixels
  <out_dir>/matte/%05d.png 8-bit person matte (255 = person) at video resolution

Used so captions, cards and props can sit beside / behind the speaker and never on the face.
Models live in tools/models (face_landmarker.task, selfie_multiclass_256x256.tflite).
"""
import json
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

ROOT = Path(__file__).resolve().parent.parent
MODELS = ROOT / "tools" / "models"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    video, out = Path(sys.argv[1]), Path(sys.argv[2])
    (out / "matte").mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fl = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mpp.BaseOptions(model_asset_path=str(MODELS / "face_landmarker.task")),
        running_mode=vision.RunningMode.VIDEO, num_faces=1))
    seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=mpp.BaseOptions(model_asset_path=str(MODELS / "selfie_multiclass_256x256.tflite")),
        running_mode=vision.RunningMode.VIDEO, output_category_mask=False, output_confidence_masks=True))

    frames, i = [], 0
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        t_ms = int(i * 1000 / fps)
        img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        r = fl.detect_for_video(img, t_ms)
        rec = {"i": i, "t": round(i / fps, 3), "ok": False}
        if r.face_landmarks:
            pts = np.array([[p.x * W, p.y * H] for p in r.face_landmarks[0]])
            x0, y0 = pts.min(axis=0)
            x1, y1 = pts.max(axis=0)
            rec.update(ok=True, box=[round(float(x0)), round(float(y0)), round(float(x1)), round(float(y1))],
                       chin_y=round(float(y1)), top_y=round(float(y0)), cx=round(float((x0 + x1) / 2)))
        frames.append(rec)
        s = seg.segment_for_video(img, t_ms)
        # multiclass: 0 background; 1 hair 2 body-skin 3 face-skin 4 clothes 5 others => person = 1 - background
        bg = s.confidence_masks[0].numpy_view()
        person = np.clip(1.0 - bg, 0, 1)
        person = cv2.resize(person, (W, H), interpolation=cv2.INTER_LINEAR)
        person = cv2.GaussianBlur(person, (0, 0), 1.2)
        cv2.imwrite(str(out / "matte" / f"{i:05d}.png"), (np.clip((person - 0.35) / 0.4, 0, 1) * 255).astype(np.uint8))
        i += 1
    (out / "face.json").write_text(json.dumps({"fps": fps, "width": W, "height": H, "frames": frames}))
    found = sum(f["ok"] for f in frames)
    print(f"{i} frames, face found in {found} ({100*found/max(i,1):.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
